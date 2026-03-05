Ejemplo de lógica del servicio de ping a montarse en otra instancia EC2.
Este codigo no escala dado que esta hardcodeado con IP's, pero puede reemplazarse con un barrido de una lista de IP's.
Es importante aclarar que, llevado al "mundo AWS", hay que actualizar el código para que apunte a los ARN (Amazon resource name) correctos.

Ejemplo de código a ejecutar en red On-Prem:

import subprocess
import time
import platform

# Lista de IPs o hosts a comprobar
ips = ["192.168.0.1", "192.168.0.10", "192.168.0.50"] #Se limita a recorrer las IP's de la lista

def ping(ip):
    """Hace ping 1 vez y devuelve True si responde."""
    if platform.system() == "Windows":
        cmd = ["ping", "-n", "1", "-w", "1000", ip]  # 1 intento, timeout 1s
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

print("Iniciando monitoreo de red...\n")
for ip in ips:
    if ping(ip):
        print(f"{ip}: ✅ OK")
    else:
        print(f"{ip}: ❌ DOWN")
    time.sleep(2)  # Espera 10 s antes del siguiente ciclo


*********************************************************************

El siguiente código evoluciona en tomar las IP's desde un CSV, y generar otro archivo .CSV como resultado agregando si dicha IP respondía o no.

import csv
import subprocess
import platform
from datetime import datetime, UTC

INPUT_CSV = "ips.csv"
OUTPUT_CSV = "resultados.csv"

def ping_once(host: str, timeout_ms: int = 1000) -> bool:
    """Devuelve True si el host responde a 1 ping. Soporta Windows/Linux/macOS."""
    if platform.system() == "Windows":
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
    else:
        # -c 1: un paquete; -W 1: timeout 1s
        cmd = ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), host]
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except Exception:
        return False

# Leer IPs
with open(INPUT_CSV, newline="") as f:
    ips = [row["ip"].strip() for row in csv.DictReader(f) if row.get("ip")]

# Hacer una única pasada y guardar resultados
now = datetime.now(UTC).isoformat(timespec="seconds")
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp_utc", "ip", "status"])
    for ip in ips:
        status = "OK" if ping_once(ip) else "DOWN"
        writer.writerow([now, ip, status])

print(f"Listo. Resultados guardados en {OUTPUT_CSV}")
