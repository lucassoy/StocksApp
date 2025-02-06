import subprocess
import os
import time
from datetime import datetime, timedelta

# Obtener la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

def ejecutar_scripts():
    # Ejecutar Stocks2.py
    subprocess.run(["python", os.path.join(current_dir, "Stocks2.py")])
    # Ejecutar StocksAnalysis.py
    subprocess.run(["python", os.path.join(current_dir, "StocksAnalysis.py")])
    # Ejecutar Main.py con streamlit
    subprocess.run(["streamlit", "run", os.path.join(current_dir, "Main.py")])

def calcular_tiempo_espera():
    ahora = datetime.now()
    hoy_12 = ahora.replace(hour=12, minute=0, second=0, microsecond=0)
    hoy_17 = ahora.replace(hour=17, minute=0, second=0, microsecond=0)

    if ahora < hoy_12:
        return (hoy_12 - ahora).total_seconds()
    elif ahora < hoy_17:
        return (hoy_17 - ahora).total_seconds()
    else:
        return ((hoy_12 + timedelta(days=1)) - ahora).total_seconds()

# Verificar si ya pasó alguna de las horas programadas y ejecutar inmediatamente si es necesario
ahora = datetime.now()
if ahora.hour >= 17:
    ejecutar_scripts()

# Bucle principal para ejecutar los scripts a las horas programadas
while True:
    tiempo_espera = calcular_tiempo_espera()
    time.sleep(tiempo_espera)
    ejecutar_scripts()
