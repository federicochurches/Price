"""
session_init.py · Inicialización de sesión PRICE
=================================================
Ejecutar al inicio de cada sesión para clonar el repo y tener
todos los scripts actualizados sin necesidad de subir archivos al proyecto Claude.

Uso:
    python3 session_init.py --token ghp_XXXX
    python3 session_init.py --token-file /mnt/user-data/uploads/text2.txt

El script:
    1. Lee el token de GitHub
    2. Clona federicochurches/Price → /home/claude/pipeline/
    3. Copia los scripts al directorio de trabajo /home/claude/ (raíz + inventory/)
    4. Verifica que todos los archivos clave estén presentes (incluyendo calc_inv.py, run_inv.py)
    5. Imprime resumen listo para el pipeline
"""

import argparse, os, subprocess, shutil, sys
from pathlib import Path

REPO     = 'federicochurches/Price'
BRANCH   = 'main'
WORK_DIR = Path('/home/claude')
CLONE_DIR = WORK_DIR / 'pipeline_repo'

# Archivos clave que deben existir tras la clonación
KEY_FILES = [
    'calc_cr.py', 'calc_rnd.py', 'calc_supply.py',
    'render_cr_p1.py', 'render_cr_p2.py', 'render_cr_p3.py',
    'render_rnd_p1.py', 'render_rnd_p2.py', 'render_rnd_p3.py',
    'assemble_unified.py', 'render_helpers.py',
    'excel_cr.py', 'excel_rnd.py', 'render_mail_v3.py',
    'build_package.py', 'github_commit.py',
    'historico_data.py', 'historico_module.py',
    'js_override.js', 'demo_js_main.js',
    # Inventory (subcarpeta)
    'calc_inv.py', 'run_inv.py',
]

def read_token(args):
    if args.token:
        return args.token.strip()
    if args.token_file:
        return Path(args.token_file).read_text().strip()
    # Buscar text2.txt en uploads
    for p in Path('/mnt/user-data/uploads').glob('text*.txt'):
        token = p.read_text().strip()
        if token.startswith('ghp_'):
            print(f"  Token encontrado en {p.name}")
            return token
    print("❌ Token no encontrado. Usar --token o --token-file")
    sys.exit(1)

def clone_repo(token):
    url = f'https://{token}@github.com/{REPO}.git'

    # Limpiar clon previo si existe
    if CLONE_DIR.exists():
        shutil.rmtree(CLONE_DIR)

    print(f"  Clonando {REPO} (branch {BRANCH})...")
    result = subprocess.run(
        ['git', 'clone', '--depth=1', '--branch', BRANCH, url, str(CLONE_DIR)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Error clonando repo:\n{result.stderr}")
        sys.exit(1)
    print(f"  ✅ Clonado en {CLONE_DIR}")

def copy_scripts():
    """Copia scripts del repo al /home/claude/ para que el pipeline los encuentre."""
    copied = 0
    skipped = []

    for f in CLONE_DIR.rglob('*'):
        # Solo archivos en la raíz del repo (no subcarpetas de datos)
        if f.parent != CLONE_DIR:
            continue
        if f.suffix not in {'.py', '.md', '.html', '.js', '.css', '.txt'}:
            continue
        dest = WORK_DIR / f.name
        shutil.copy2(f, dest)
        copied += 1

    # Copiar scripts de inventory/ directamente al directorio de trabajo
    # (calc_inv.py y run_inv.py viven en subcarpeta pero Claude los necesita en raíz)
    inv_dir = CLONE_DIR / 'inventory'
    inv_scripts = ['calc_inv.py', 'run_inv.py']
    inv_copied = 0
    if inv_dir.exists():
        for fname in inv_scripts:
            src = inv_dir / fname
            if src.exists():
                shutil.copy2(src, WORK_DIR / fname)
                inv_copied += 1
        if inv_copied:
            print(f"  ✅ {inv_copied} script(s) de inventory/ copiados a /home/claude/")

    print(f"  ✅ {copied + inv_copied} archivos copiados en total a /home/claude/")
    return copied + inv_copied

def verify():
    missing = [f for f in KEY_FILES if not (WORK_DIR / f).exists()]
    if missing:
        print(f"⚠️  Archivos faltantes: {missing}")
    else:
        print(f"  ✅ Todos los archivos clave presentes ({len(KEY_FILES)})")
    return not missing

def main():
    parser = argparse.ArgumentParser(description='Inicializar sesión PRICE desde GitHub')
    parser.add_argument('--token',      help='GitHub PAT directamente')
    parser.add_argument('--token-file', help='Archivo con el token')
    args = parser.parse_args()

    print("\n" + "="*55)
    print("  🚀 SESSION INIT · Proyecto PRICE")
    print("="*55)

    token = read_token(args)
    clone_repo(token)
    copy_scripts()
    ok = verify()

    # Leer última semana del repo para orientar
    hist = WORK_DIR / 'historico_data.py'
    if hist.exists():
        content = hist.read_text()
        import re
        m = re.search(r"SEMANAS\s*=\s*\[([^\]]+)\]", content)
        if m:
            semanas = m.group(1).replace("'","").split(',')
            ultima = semanas[-1].strip()
            print(f"\n  📅 Última semana en repo: {ultima}")
            print(f"  📅 Próxima semana: W{int(ultima.replace('W',''))+1}")

    print("\n" + "="*55)
    print(f"  {'✅ Listo para el pipeline' if ok else '⚠️  Verificar archivos faltantes'}")
    print("="*55 + "\n")

if __name__ == '__main__':
    main()
