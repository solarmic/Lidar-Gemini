# config.py
"""
Fichero de configuración para todos los parámetros del sistema de tracking.
Modifica estos valores para adaptar el software a tu escenario y hardware.
"""

# --- Configuración del Escenario ---
# Dimensiones del escenario en metros. El LIDAR se asume en el centro.
STAGE_WIDTH_M = 6.0
STAGE_HEIGHT_M = 6.0

# --- Configuración del LIDAR ---
# Puertos serie. Descomenta o modifica según tu sistema operativo.
# Para encontrar el puerto correcto, revisa la guía de implementación.
LIDAR_PORT_MAC = '/dev/tty.SLAB_USBtoUART'  # Ejemplo para un driver común en Mac
LIDAR_PORT_RASPBERRY_PI = '/dev/ttyUSB0'   # Puerto estándar en Raspberry Pi

# Rango de distancia para filtrar puntos (en milímetros).
# Ayuda a ignorar el ruido cerca del sensor y los objetos muy lejanos.
MIN_DISTANCE_MM = 200  # 20 cm
MAX_DISTANCE_MM = 4500 # 4.5 metros (un poco más que la diagonal de un escenario 6x6)

# --- Configuración de Detección (Algoritmo DBSCAN) ---
# eps: Distancia máxima entre dos puntos para considerarlos vecinos (en metros).
#      Un valor más alto agrupa puntos más lejanos. Ajusta según la "densidad"
#      de los puntos que rebotan en el actor. Un buen punto de partida es 0.25 (25 cm).
DBSCAN_EPS = 0.25

# min_samples: Número mínimo de puntos para formar un cluster.
#              Un valor más alto ayuda a filtrar objetos pequeños y ruido.
DBSCAN_MIN_SAMPLES = 5

# Tamaño mínimo de un cluster para ser considerado una persona.
# Filtro adicional para asegurar que no detectamos un objeto pequeño como una persona.
MIN_CLUSTER_SIZE_FOR_PERSON = 8

# --- Configuración de Movimiento ---
# Umbral de movimiento (en coordenadas normalizadas).
# La posición "activa" solo se actualiza si el actor se mueve más de esta distancia.
# Esto evita que pequeños temblores o errores de medición se consideren movimiento.
MOVEMENT_THRESHOLD = 0.02 # 2% de la dimensión del escenario

# --- Configuración de Red (UDP para Max/MSP) ---
# IP de la máquina que ejecuta Max/MSP. "127.0.0.1" si es la misma máquina.
UDP_IP_TARGET = "127.0.0.1"
# Puerto en el que Max/MSP estará escuchando.
UDP_PORT_TARGET = 8888
