"""
reinyectar_editorial_w25.py
Corre DESPUÉS de assemble_unified.py para restaurar el editorial W25.
Uso: py reinyectar_editorial_w25.py
"""
import json, re, sys, os

# Ajustar paths según entorno local
HTML_PATH     = r'SUPPLY_W25.html'          # archivo generado por assemble_unified.py
EDITORIAL_JSON = r'editorial_w25.json'       # este mismo archivo de editorial

if not os.path.exists(HTML_PATH):
    print(f"ERROR: no se encuentra {HTML_PATH}")
    print("Asegurate de correr desde la carpeta donde assemble_unified.py generó el HTML")
    sys.exit(1)

if not os.path.exists(EDITORIAL_JSON):
    print(f"ERROR: no se encuentra {EDITORIAL_JSON}")
    sys.exit(1)

with open(EDITORIAL_JSON, 'r', encoding='utf-8') as f:
    editorial = json.load(f)

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

def escape_js(s):
    """Escapar </ para que no corte el <script>"""
    return s.replace('</', '<\\/')

def patch_var(html, var_name, editorial_data):
    """Reinyecta re/plan/co en un JSON variable (CR_D o RND_D) del HTML."""
    # Encontrar la variable en el HTML
    idx = html.find(f'{var_name}={{')
    if idx < 0:
        idx = html.find(f'{var_name} = {{')
    if idx < 0:
        print(f"  WARN: {var_name} no encontrado en HTML")
        return html

    # Extraer el objeto JSON completo
    start = html.index('{', idx)
    depth = 0; end = start
    for i, ch in enumerate(html[start:], start):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: end = i + 1; break

    raw = html[start:end]
    try:
        d = json.loads(raw.replace('<\\/', '</'))
    except Exception as e:
        print(f"  ERROR parseando {var_name}: {e}")
        return html

    # Aplicar el editorial por canasta
    changed = 0
    for canasta, ed in editorial_data.items():
        if canasta in d:
            d[canasta]['re']   = ed.get('re', [])
            d[canasta]['plan'] = ed.get('plan', [])
            d[canasta]['co']   = ed.get('co', [])
            changed += 1

    # Serializar y escapar
    new_json = escape_js(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    html = html[:start] + new_json + html[end:]
    print(f"  {var_name}: {changed} canastas reinyectadas")
    return html

print(f"Reinyectando editorial en {HTML_PATH}...")
html = patch_var(html, 'CR_D', editorial['CR_D'])
html = patch_var(html, 'RND_D', editorial['RND_D'])

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nListo. Verificar en el browser antes de commitear.")
