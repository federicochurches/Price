#!/usr/bin/env python3
"""
github_commit.py · Paso 8 del pipeline PRICE
Commit de todos los archivos a GitHub vía API + ZIP del proyecto Claude.

Uso standalone:
    python3 github_commit.py --week 21 --periodo "18–24 may 2026" --token ghp_xxx
    python3 github_commit.py --week 21 --periodo "18–24 may 2026" --token-file .github_token

    # Fix puntual (no pipeline):
    python3 github_commit.py --week 21 --tipo fix --mensaje "Fix searchbox canastas" --token ghp_xxx

Desde run_pipeline.py:
    Se llama automáticamente con los datos del config YAML.
    El token se lee de la variable de entorno GITHUB_TOKEN.

Qué commitea:
    - ZIP del repo (Price_WNN.zip): todos los archivos generados por build_package.py
    - Scripts actualizados en _scripts/ (render_*.py, asset_*.html, render_helpers.py, etc.)
    - Documentación actualizada en _docs/ (CHANGELOG.md, README.md, PROMPT_CORE.md)

Qué genera localmente:
    - ProyectoClaude_PRICE_WNN.zip: ZIP del proyecto para claude.ai
"""

import argparse
import base64
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ pip install requests")
    sys.exit(1)

REPO = 'federicochurches/Price'
BASE = f'https://api.github.com/repos/{REPO}'

SCRIPT_DIR = Path(__file__).resolve().parent

# ── Archivos de scripts que siempre se incluyen si existen ──────────────────
SCRIPT_FILES = [
    'render_helpers.py',
    'render_cr_p1.py', 'render_cr_p2.py', 'render_cr_p3.py',
    'render_rnd_p1.py', 'render_rnd_p2.py', 'render_rnd_p3.py',
    'asset_supply_head.html', 'asset_shared_head.html',
    'asset_cr_head.html', 'asset_rnd_head.html',
    'asset_cr_masthead.html', 'asset_rnd_masthead.html',
    'asset_cr_footer.html', 'asset_rnd_footer.html',
    'calc_cr.py', 'calc_rnd.py',
    'assemble_unified.py',          # W21+ reemplaza assemble_cr + assemble_rnd
    'excel_cr.py', 'excel_rnd.py',  # W21+ consolidados (4 hojas c/u)
    'render_mail_v3.py', 'build_package.py', 'run_pipeline.py',
    'update_docs.py', 'github_commit.py',
    'historico_data.py', 'historico_module.py',
    'template_resumen.py', 'template_alertas.py', 'template_severity.py', 'template_seguimiento.py',
    'engine.py', 'areas_catalogo.py',
    # JS/CSS críticos del frontend (W21+)
    'demo_js_main.js', 'js_override.js', 'demo_css_w22.css',
]

DOC_FILES = ['CHANGELOG.md', 'README_QUICK.md', 'PROMPT_CORE.md',
             'HISTORIAL_SESIONES.md', 'BANDAS.md', 'COMMIT_GUIDE.md']

def get_token(args):
    """Obtiene el token GitHub: argumento > env var > archivo."""
    if args.token:
        return args.token
    env = os.environ.get('GITHUB_TOKEN', '')
    if env:
        return env
    if args.token_file and Path(args.token_file).exists():
        return Path(args.token_file).read_text().strip()
    print("❌ Token GitHub no encontrado. Usar --token, --token-file o variable GITHUB_TOKEN")
    sys.exit(1)

def make_headers(token):
    return {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

def create_blob(base_url, headers, content_bytes):
    """Sube un blob a GitHub. Retorna SHA o None."""
    try:
        txt = content_bytes.decode('utf-8')
        enc = 'utf-8'
    except UnicodeDecodeError:
        txt = base64.b64encode(content_bytes).decode('ascii')
        enc = 'base64'
    r = requests.post(f'{base_url}/git/blobs', headers=headers,
                      json={'content': txt, 'encoding': enc})
    if r.status_code == 201:
        return r.json()['sha']
    print(f"  ⚠️  Blob failed: {r.status_code} {r.text[:100]}")
    return None

def commit_to_github(token, week_num, periodo, tipo, mensaje_extra, blobs_map):
    """
    Crea tree + commit + actualiza ref.
    blobs_map: {repo_path: local_path_or_bytes}
    Retorna commit SHA o None.
    """
    headers = make_headers(token)

    # HEAD actual
    r = requests.get(f'{BASE}/git/refs/heads/main', headers=headers)
    if r.status_code != 200:
        print(f"❌ No se pudo leer HEAD: {r.text[:100]}"); return None
    head_sha = r.json()['object']['sha']

    r = requests.get(f'{BASE}/git/commits/{head_sha}', headers=headers)
    base_tree_sha = r.json()['tree']['sha']

    # Crear blobs
    print(f"\n  📦 Subiendo {len(blobs_map)} archivos a GitHub...")
    tree_items = []
    for repo_path, local in blobs_map.items():
        data = local if isinstance(local, bytes) else Path(local).read_bytes()
        sha = create_blob(BASE, headers, data)
        if sha:
            tree_items.append({'path': repo_path, 'mode': '100644', 'type': 'blob', 'sha': sha})
            print(f"    ✅ {repo_path}")
        else:
            print(f"    ❌ {repo_path}")

    if not tree_items:
        print("❌ Ningún blob subido."); return None

    # Tree
    r = requests.post(f'{BASE}/git/trees', headers=headers,
                      json={'base_tree': base_tree_sha, 'tree': tree_items})
    if r.status_code != 201:
        print(f"❌ Tree failed: {r.text[:200]}"); return None
    tree_sha = r.json()['sha']

    # Mensaje commit
    if tipo == 'pipeline':
        msg = (f"feat: Week {week_num} · Supply unificado + Excels consolidados · {periodo}\n\n"
               f"Pipeline completo W{week_num}: calc → render → assemble_unified → excel (4 hojas) → mail → hub → docs → commit")
    else:
        msg = mensaje_extra or f"fix: W{week_num} · {periodo}"

    # Commit
    r = requests.post(f'{BASE}/git/commits', headers=headers, json={
        'message': msg,
        'tree': tree_sha,
        'parents': [head_sha],
        'author': {'name': 'Federico Iglesias', 'email': 'federico.iglesias@pricetravel.com'}
    })
    if r.status_code != 201:
        print(f"❌ Commit failed: {r.text[:200]}"); return None
    commit_sha = r.json()['sha']

    # Update ref
    r = requests.patch(f'{BASE}/git/refs/heads/main', headers=headers,
                       json={'sha': commit_sha, 'force': False})
    if r.status_code != 200:
        print(f"❌ Ref update failed: {r.text[:200]}"); return None

    return commit_sha

def build_blobs_map(week_num, outputs_dir, scripts_dir):
    """
    Construye el mapa de archivos a commitear.
    Combina: contenido del ZIP del repo + scripts actualizados + docs.
    """
    blobs = {}
    outputs = Path(outputs_dir)
    scripts = Path(scripts_dir)

    # 1. Archivos del ZIP del repo (build_package.py ya los preparó)
    zip_path = outputs / f'Price_W{week_num}.zip'
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if not name.endswith('/'):
                    blobs[name] = zf.read(name)
        print(f"  📦 ZIP del repo: {len(blobs)} archivos de {zip_path.name}")
    else:
        print(f"  ⚠️  No se encontró {zip_path.name} — commitando solo scripts y docs")

    # 2. Scripts actualizados en _scripts/
    for fname in SCRIPT_FILES:
        local = scripts / fname
        if local.exists():
            blobs[f'_scripts/{fname}'] = local.read_bytes()

    # 3. Documentación en _docs/
    for fname in DOC_FILES:
        local = scripts / fname
        if local.exists():
            blobs[f'_docs/{fname}'] = local.read_bytes()

    return blobs

def build_project_zip(week_num, scripts_dir, outputs_dir, docs_dir=None):
    """
    Genera el ZIP del proyecto Claude con todos los archivos de _scripts/.
    42-44 archivos: scripts + docs + Mail.
    docs_dir: si se especifica, los .md del proyecto se toman de ahí (tienen prioridad sobre scripts_dir).
    """
    scripts = Path(scripts_dir)
    outputs = Path(outputs_dir)
    out = outputs / f'ProyectoClaude_PRICE_W{week_num}.zip'

    # Si hay docs_dir, copiar los docs actualizados al scripts_dir antes de empaquetar
    if docs_dir:
        docs_path = Path(docs_dir)
        for doc in ['CHANGELOG.md', 'README_QUICK.md', 'PROMPT_CORE.md', 'HISTORIAL_SESIONES.md', 'BANDAS.md']:
            src = docs_path / doc
            if src.exists():
                import shutil
                shutil.copy2(str(src), str(scripts / doc))

    all_script_files = list(scripts.glob('*.py')) + list(scripts.glob('*.html')) + list(scripts.glob('*.md')) + list(scripts.glob('*.js')) + list(scripts.glob('*.css'))
    
    # Patrones a excluir del proyecto Claude
    EXCLUDE = {
        'part1_cr.html', 'part2_cr.html', 'part3_cr.html',
        'part1_rnd.html', 'part2_rnd.html', 'part3_rnd.html',
        # Deprecated W21 — reemplazados por assemble_unified + excel_*.py consolidados
        'assemble_cr.py', 'assemble_rnd.py',
        'excel_cr_canastas.py', 'excel_rnd_canastas.py',
        # Módulos obsoletos reemplazados por historico_module.py
        'historico_module_rnd.py', 'historico_module_v2.py',
        # Archivos one-shot / temporales
        '__init__.py', 'test_table.html',
        'run_cr_w21_patch.py', 'run_rnd_w21.py',
        'PROMPT_CORE_updated.md',
    }

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        seen = set()
        for f in sorted(all_script_files):
            if f.name.startswith('__') or f.name in seen or f.name in EXCLUDE:
                continue
            zf.write(str(f), f.name)
            seen.add(f.name)
        
        # Mail de la semana actual
        mail_candidates = [
            outputs / f'Mail_W{week_num}.html',
            scripts / f'Mail_W{week_num}.html',
        ]
        if 'Mail_W' + str(week_num) + '.html' not in seen:
            for mc in mail_candidates:
                if mc.exists():
                    zf.write(str(mc), f'Mail_W{week_num}.html')
                    break

    n = len(zipfile.ZipFile(out).namelist())
    size_kb = out.stat().st_size / 1024
    print(f"  ✅ ProyectoClaude_PRICE_W{week_num}.zip: {n} archivos · {size_kb:.0f} KB")
    return str(out)

def main():
    parser = argparse.ArgumentParser(description='Commit PRICE a GitHub vía API')
    parser.add_argument('--week',        type=int,  required=True)
    parser.add_argument('--periodo',     type=str,  default='')
    parser.add_argument('--tipo',        type=str,  default='pipeline', choices=['pipeline','fix'])
    parser.add_argument('--mensaje',     type=str,  default='')
    parser.add_argument('--token',       type=str,  default=None)
    parser.add_argument('--token-file',  type=str,  default=None)
    parser.add_argument('--outputs-dir', type=str,  default=None,
                        help='Directorio de outputs (default: /mnt/user-data/outputs)')
    parser.add_argument('--scripts-dir', type=str,  default=None,
                        help='Directorio de scripts (default: directorio del script)')
    parser.add_argument('--skip-zip',    action='store_true', help='No generar ZIP del proyecto Claude')
    args = parser.parse_args()

    week_num    = args.week
    periodo     = args.periodo or f'W{week_num}'
    outputs_dir = Path(args.outputs_dir) if args.outputs_dir else Path('/mnt/user-data/outputs')
    scripts_dir = Path(args.scripts_dir) if args.scripts_dir else SCRIPT_DIR

    token = get_token(args)

    print(f"\n{'='*60}")
    print(f"  🚀 GITHUB COMMIT · W{week_num} · {periodo}")
    print(f"{'='*60}\n")

    # ── Auto-actualizar docs antes del commit ────────────────────────────
    import subprocess
    _doc_cmd = [
        'python3', str(scripts_dir / 'update_docs.py'),
        '--week', str(week_num),
        '--periodo', periodo,
        '--tipo', args.tipo,
        '--mensaje', args.mensaje,
        '--scripts-dir', str(scripts_dir),
    ]
    if args.tipo == 'fix':
        _doc_cmd.append('--skip-historico')
    try:
        subprocess.run(_doc_cmd, check=True)
    except Exception as e:
        print(f"  ⚠️  update_docs: {e} (continuando)")

    # Construir mapa de blobs (DESPUÉS de actualizar docs)
    blobs = build_blobs_map(week_num, outputs_dir, scripts_dir)
    print(f"  Total archivos a commitear: {len(blobs)}")

    # Commit
    commit_sha = commit_to_github(token, week_num, periodo, args.tipo, args.mensaje, blobs)

    if commit_sha:
        print(f"\n  ✅ Commit: {commit_sha[:12]}")
        print(f"  🔗 https://github.com/{REPO}/commit/{commit_sha}")
        print(f"  🌐 Hub: https://analytics-desk.netlify.app")

        # ZIP del proyecto Claude
        if not args.skip_zip:
            print(f"\n  📦 Generando ZIP del proyecto Claude...")
            zip_path = build_project_zip(week_num, scripts_dir, outputs_dir)
            print(f"  ✅ {zip_path}")

        print(f"\n{'='*60}")
        print(f"  ✅ ENTREGA W{week_num} COMPLETA")
        print(f"{'='*60}\n")
        return commit_sha
    else:
        print(f"\n❌ Commit fallido")
        return None

if __name__ == '__main__':
    main()
