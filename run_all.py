import subprocess
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time

current_dir = os.path.dirname(os.path.abspath(__file__))

def ejecutar_scripts():
    print(f"Ejecutando scripts a las {datetime.now()}")
    subprocess.run(["python", os.path.join(current_dir, "Stocks2.py")])
    subprocess.run(["python", os.path.join(current_dir, "StocksAnalysis.py")])
    subprocess.run(["streamlit", "run", os.path.join(current_dir, "app.py")])

def verificar_y_ejecutar():
    ahora = datetime.now()
    if ahora.hour >= 17 or ahora.hour < 12:
        ejecutar_scripts()
    elif ahora.hour >= 12:
        ejecutar_scripts()

verificar_y_ejecutar()

scheduler = BackgroundScheduler()
scheduler.add_job(ejecutar_scripts, 'cron', hour=12, minute=0)
scheduler.add_job(ejecutar_scripts, 'cron', hour=17, minute=0)
scheduler.start()

print("Scheduler iniciado. Esperando próximas ejecuciones...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Script detenido manualmente.")
    scheduler.shutdown()
