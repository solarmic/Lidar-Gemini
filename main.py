# main.py
import sys
import time
import socket
import platform
import numpy as np
from sklearn.cluster import DBSCAN
from rplidar import RPLidar

# Importar la configuración local
try:
    import config
except ImportError:
    print("Error: El fichero 'config.py' no se ha encontrado.")
    print("Por favor, asegúrate de que el fichero de configuración está en la misma carpeta.")
    sys.exit(1)

class PersonTracker:
    """
    Gestiona la conexión con el LIDAR, el procesamiento de datos, la detección
    de una persona y el envío de su posición normalizada vía UDP.
    """
    def __init__(self):
        # Cargar configuración
        self.stage_width = config.STAGE_WIDTH_M
        self.stage_height = config.STAGE_HEIGHT_M
        self.movement_threshold = config.MOVEMENT_THRESHOLD

        # Inicializar estado
        self.lidar = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_active_position = None  # Última posición donde se detectó movimiento real
        self.last_sent_position = None    # Última posición enviada (puede ser la activa o la anterior)

        # Inicializar el algoritmo de clustering DBSCAN con los parámetros de config
        self.dbscan = DBSCAN(eps=config.DBSCAN_EPS, min_samples=config.DBSCAN_MIN_SAMPLES)

    def _get_lidar_port(self):
        """Devuelve el puerto serie correcto según el sistema operativo."""
        os_name = platform.system()
        if os_name == "Darwin":  # macOS
            print("Sistema operativo detectado: macOS")
            return config.LIDAR_PORT_MAC
        elif os_name == "Linux": # Asumimos Raspberry Pi (Linux)
            print("Sistema operativo detectado: Linux (probablemente Raspberry Pi)")
            return config.LIDAR_PORT_RASPBERRY_PI
        else:
            print(f"Sistema operativo '{os_name}' no soportado automáticamente. Revisa 'config.py'.")
            return None

    def connect_lidar(self):
        """Establece la conexión con el sensor RPLIDAR."""
        port = self._get_lidar_port()
        if not port:
            return False
        
        try:
            print(f"Intentando conectar con el LIDAR en el puerto: {port}...")
            self.lidar = RPLidar(port)
            self.lidar.start_motor()
            time.sleep(1) # Dar tiempo al motor para que se estabilice
            health = self.lidar.get_health()
            info = self.lidar.get_info()
            print(f"-> Salud del LIDAR: {health}")
            print(f"-> Info del LIDAR: {info}")
            if health[0] != 'Good':
                print("Advertencia: El estado de salud del LIDAR no es 'Good'.")
            return True
        except Exception as e:
            print(f"Error crítico al conectar con el LIDAR: {e}")
            self.stop()
            return False

    def _process_scan(self, scan_data):
        """
        Procesa un escaneo completo: filtra, agrupa, y encuentra el centroide de la persona.
        Devuelve la posición normalizada (x, y) o None si no se detecta a nadie.
        """
        # 1. Filtrar puntos por distancia y convertir a coordenadas cartesianas (en metros)
        points_xy = []
        for _, angle, distance in scan_data:
            if config.MIN_DISTANCE_MM < distance < config.MAX_DISTANCE_MM:
                # Convertir de coordenadas polares (ángulo, distancia) a cartesianas (x, y)
                rad = np.deg2rad(angle)
                x = (distance / 1000.0) * np.cos(rad)
                y = (distance / 1000.0) * np.sin(rad)
                
                # Filtrar puntos que están fuera de los límites del escenario
                if abs(x) < self.stage_width / 2 and abs(y) < self.stage_height / 2:
                    points_xy.append((x, y))

        if not points_xy:
            return None

        points_array = np.array(points_xy)

        # 2. Clustering con DBSCAN para agrupar los puntos
        self.dbscan.fit(points_array)
        labels = self.dbscan.labels_
        
        unique_labels = set(labels)
        if not unique_labels or (len(unique_labels) == 1 and -1 in unique_labels):
            return None # No se encontraron clusters, solo ruido

        # 3. Encontrar el cluster más grande (que probablemente sea la persona)
        largest_cluster_label = -1
        max_points_in_cluster = 0
        
        for label in unique_labels:
            if label == -1:  # -1 es la etiqueta para el ruido según DBSCAN
                continue
            
            cluster_size = np.sum(labels == label)
            if cluster_size > max_points_in_cluster and cluster_size >= config.MIN_CLUSTER_SIZE_FOR_PERSON:
                max_points_in_cluster = cluster_size
                largest_cluster_label = label
        
        if largest_cluster_label == -1:
            return None # Ningún cluster es suficientemente grande para ser una persona

        # 4. Calcular el centroide (posición media) del cluster de la persona
        person_cluster_points = points_array[labels == largest_cluster_label]
        centroid = np.mean(person_cluster_points, axis=0)

        # 5. Normalizar las coordenadas al rango [0, 1]
        norm_x = (centroid[0] + self.stage_width / 2) / self.stage_width
        norm_y = (centroid[1] + self.stage_height / 2) / self.stage_height
        
        # Asegurar que los valores están estrictamente dentro del rango [0, 1]
        return (np.clip(norm_x, 0.0, 1.0), np.clip(norm_y, 0.0, 1.0))

    def _send_udp_data(self, position):
        """Envía la posición (x, y) a la IP y puerto configurados."""
        # Formato de mensaje: "x y", por ejemplo "0.5312 0.7845"
        message = f"{position[0]:.6f} {position[1]:.6f}"
        self.udp_socket.sendto(message.encode('utf-8'), (config.UDP_IP_TARGET, config.UDP_PORT_TARGET))
        # Descomenta la siguiente línea para depuración (ver qué se envía)
        # print(f"Enviado a Max: {message}")

    def run(self):
        """Bucle principal de ejecución: captura, procesa y envía."""
        if not self.connect_lidar():
            return

        print("\n🚀 Tracking iniciado. Pulsa Ctrl+C para detener.")
        try:
            for scan in self.lidar.iter_scans(scan_type='express', max_buf_meas=3500):
                current_position = self._process_scan(scan)
                
                if current_position:
                    # Si es la primera detección, la guardamos como la posición inicial
                    if self.last_active_position is None:
                        self.last_active_position = current_position
                    
                    # Calcular si el movimiento supera el umbral
                    dist_moved = np.sqrt(
                        (current_position[0] - self.last_active_position[0])**2 +
                        (current_position[1] - self.last_active_position[1])**2
                    )

                    # Lógica de movimiento
                    if dist_moved > self.movement_threshold:
                        # Si hay movimiento, actualizamos la posición activa
                        self.last_active_position = current_position
                    
                    # La posición a enviar es siempre la última posición activa
                    self.last_sent_position = self.last_active_position
                
                # Si tenemos una posición válida (actual o anterior), la enviamos
                if self.last_sent_position:
                    self._send_udp_data(self.last_sent_position)

        except KeyboardInterrupt:
            print("\nDeteniendo el programa por solicitud del usuario.")
        except Exception as e:
            print(f"\nHa ocurrido un error inesperado: {e}")
        finally:
            self.stop()

    def stop(self):
        """Detiene el LIDAR y cierra las conexiones de forma segura."""
        print("Cerrando conexiones...")
        if self.lidar:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
        self.udp_socket.close()
        print("Recursos liberados. ¡Adiós!")

if __name__ == "__main__":
    tracker = PersonTracker()
    tracker.run()
