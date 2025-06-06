# **Real-Time Performer Tracking with LIDAR**

## **Descripción**

Este proyecto implementa un sistema de seguimiento en tiempo real para un único intérprete en un escenario de artes escénicas. Utiliza un sensor **RPLIDAR A1** conectado a una **Raspberry Pi** para detectar la posición de la persona, la procesa para filtrar ruido y, finalmente, envía las coordenadas normalizadas (x, y) a través de UDP a un software de control como **Max/MSP**.

El sistema está diseñado para ser **robusto, modular y fácilmente configurable** para diferentes tamaños de escenario y condiciones de iluminación, lo que lo hace ideal para su uso en espectáculos en directo.

### **Características Principales**

* **Detección Precisa:** Utiliza el algoritmo de clustering **DBSCAN** para aislar a la persona de objetos pequeños y ruido ambiental.  
* **Filtrado Inteligente:** Ignora los datos del LIDAR que están fuera del área del escenario definida o demasiado cerca del sensor.  
* **Seguimiento de Movimiento Suave:** Si el intérprete se detiene, el sistema sigue enviando la última posición activa, evitando saltos o la pérdida de la señal.  
* **Coordenadas Normalizadas:** Convierte la posición cartesiana del escenario a un rango \[0.0, 1.0\], perfecto para mapear en otros programas.  
* **Comunicación en Tiempo Real:** Envía datos a través de **UDP**, un protocolo de baja latencia ideal para aplicaciones en directo.  
* **Configuración Centralizada:** Todos los parámetros clave (tamaño del escenario, puertos, sensibilidad) se ajustan en un único fichero config.py.

## **Requisitos**

### **Hardware**

* **Raspberry Pi** (Modelo 3, 4 o 5 recomendado para un rendimiento óptimo).  
* Sensor **RPLIDAR A1** con su adaptador USB.  
* Tarjeta microSD de buena calidad (mínimo 16 GB).  
* Fuente de alimentación adecuada para la Raspberry Pi.

### **Software y Dependencias**

* **Python 3.7+**  
* Las siguientes librerías de Python (incluidas en requirements.txt):  
  * rplidar-roboticia  
  * numpy  
  * scikit-learn

## **Estructura del Proyecto**

/  
├── main.py             \# Script principal que ejecuta toda la lógica de tracking.  
├── config.py           \# Fichero para configurar todos los parámetros del sistema.  
└── requirements.txt    \# Lista de dependencias de Python.

## **Instalación y Configuración**

### **1\. Preparar la Raspberry Pi**

Para obtener el mejor rendimiento, se recomienda instalar **Raspberry Pi OS Lite (64-bit)**. Sigue la [**Guía de Instalación y Configuración**](http://docs.google.com/URL_A_TU_GUIA.md) para preparar el sistema operativo de forma "headless" (sin monitor) y conectarte por SSH.

*(Nota: Puedes enlazar aquí a la guía que te proporcioné anteriormente si la subes también al repositorio).*

### **2\. Clonar el Repositorio**

Conéctate a tu Raspberry Pi por SSH y clona este repositorio:

git clone https://github.com/tu-usuario/tu-repositorio.git  
cd tu-repositorio

### **3\. Instalar las Dependencias**

Primero, instala las dependencias del sistema necesarias para scikit-learn en la Raspberry Pi:

sudo apt update  
sudo apt install python3-dev libatlas-base-dev \-y

Luego, instala las librerías de Python usando pip:

pip install \-r requirements.txt

### **4\. Configurar el Sistema**

Abre el fichero config.py para ajustar los parámetros a tu montaje:

* **STAGE\_WIDTH\_M y STAGE\_HEIGHT\_M**: Define las dimensiones de tu escenario en metros.  
* **LIDAR\_PORT\_RASPBERRY\_PI**: Asegúrate de que el puerto (/dev/ttyUSB0 por defecto) es correcto. Puedes verificarlo con el comando ls /dev/ttyUSB\*.  
* **Parámetros de DBSCAN**: Si la detección no es precisa, ajusta DBSCAN\_EPS y MIN\_CLUSTER\_SIZE\_FOR\_PERSON para cambiar la sensibilidad.  
* **UDP\_IP\_TARGET y UDP\_PORT\_TARGET**: Introduce la dirección IP de la máquina que ejecuta Max/MSP y el puerto que escuchará.

## **Uso**

1. **Conecta el RPLIDAR A1** a un puerto USB de la Raspberry Pi.  
2. **Inicia el script de tracking** desde la terminal de la Raspberry Pi:  
   python3 main.py

   El programa empezará a escanear, procesar y enviar datos por UDP. Verás mensajes de estado en la consola. Para detenerlo, pulsa Ctrl+C.  
3. **Recibir en Max/MSP**:  
   * Abre un patch en Max.  
   * Crea un objeto udpreceive con el puerto configurado (ej: udpreceive 8888).  
   * Conecta su salida a route symbol \-\> fromsymbol \-\> unpack f f para obtener las coordenadas X e Y como números flotantes.

## **Licencia**

Este proyecto está bajo la Licencia MIT. Consulta el fichero LICENSE para más detalles.