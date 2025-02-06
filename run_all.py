import subprocess
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Obtener la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

def ejecutar_scripts():
    print(f"Ejecutando scripts a las {datetime.now()}")
    subprocess.run(["python", os.path.join(current_dir, "Stocks2.py")])
    subprocess.run(["python", os.path.join(current_dir, "StocksAnalysis.py")])
    subprocess.run(["python", os.path.join(current_dir, "Main.py")])
    subprocess.run(["streamlit", "run", os.path.join(current_dir, "app.py")])

def verificar_y_ejecutar():
    ahora = datetime.now()
    if ahora.hour >= 17 or ahora.hour < 12:
        ejecutar_scripts()
    elif ahora.hour >= 12:
        ejecutar_scripts()

# Verificar si ya pasó alguna de las horas programadas y ejecutar inmediatamente si es necesario
verificar_y_ejecutar()

# Programar la ejecución de los scripts a las 12:00 y 17:00
scheduler = BackgroundScheduler()
scheduler.add_job(ejecutar_scripts, 'cron', hour=12, minute=0)
scheduler.add_job(ejecutar_scripts, 'cron', hour=17, minute=0)
scheduler.start()

print("Scheduler iniciado. Esperando próximas ejecuciones...")

# Mantener el script en ejecución
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Script detenido manualmente.")
    scheduler.shutdown()
