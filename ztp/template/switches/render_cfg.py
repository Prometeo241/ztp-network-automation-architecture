# render_cfg.py
# Renderiza plantilla Jinja2 con usuario/contraseña SSH locales

import csv
from jinja2 import Environment, FileSystemLoader

# Configuración básica
TEMPLATES_DIR = "templates" #Ruta de archivo jinja
TEMPLATE_FILE = "switches_acceso.j2"
INPUT_CSV = "switch.csv"

# Inicializar entorno Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
template = env.get_template(TEMPLATE_FILE)

# Leer CSV e iterar por cada fila
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cfg = template.render(
            LOCAL_USER=row["LOCAL_USER"],
            LOCAL_PASS=row["LOCAL_PASS"]
        )

        output_file = f"{row['LOCAL_USER']}.cfg"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(cfg)
        print(f"[OK] Generado: {output_file}")

print("\nListo. Archivos .cfg creados.")
