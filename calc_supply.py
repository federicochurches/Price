"""
calc_supply.py — Supply Weekly KPIs · Standalone Pipeline
Genera SUPPLY_WNN.html + Analisis_CheckRates_WNN.xlsx + Analisis_RatesNoDispo_WNN.xlsx
en una sola corrida, sin dependencias de run_pipeline.py.

Uso:
    python calc_supply.py

Coloca los 4 datasets en la misma carpeta y configurá el bloque CONFIG.
Los scripts del pipeline (calc_rnd.py, calc_cr.py, etc.) deben estar en la misma carpeta
o en /mnt/project.

Outputs en OUTPUT_DIR (por defecto: misma carpeta que este script):
    SUPPLY_WNN.html
    Analisis_CheckRates_WNN.xlsx
    Analisis_RatesNoDispo_WNN.xlsx
"""

import os
import sys
import shutil
import runpy
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG — editar cada semana
# ─────────────────────────────────────────────
WEEK        = 'W23'
VOL_NUM     = '23'
PERIODO     = '2 – 8 jun 2026'
MES_ANO     = 'Junio 2026'
FECHA_PUB   = 'LUNES 09 de Junio de 2026'

# Outputs — por defecto misma carpeta del script
OUTPUT_DIR  = str(Path(__file__).parent)
# ─────────────────────────────────────────────

WEEK_NUM    = int(WEEK.replace('W', ''))
VOL_NUM_INT = int(VOL_NUM)

# Rutas de búsqueda para scripts del pipeline
SCRIPT_DIR  = Path(__file__).parent
PROJECT_DIR = Path('/mnt/project')

def find_script(name):
    """Busca un script en SCRIPT_DIR o PROJECT_DIR."""
    for d in [SCRIPT_DIR, PROJECT_DIR]:
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(f'Script no encontrado: {name}')

def validate_datasets():
    """Verifica que los 4 datasets existan antes de arrancar."""
    required = [
        f'Dataset_RatesNoDispo_W{WEEK_NUM}.xlsx',
        f'Dataset_RatesNoDispo_W{WEEK_NUM - 1}.xlsx',
        f'Dataset_CheckRates_W{WEEK_NUM}.xlsx',
        f'Dataset_CheckRates_W{WEEK_NUM - 1}.xlsx',
    ]
    search_dirs = [SCRIPT_DIR, PROJECT_DIR, Path('/mnt/user-data/uploads')]
    missing = []
    for name in required:
        found = any((d / name).exists() for d in search_dirs)
        if not found:
            missing.append(name)
    if missing:
        print('\n❌ Datasets faltantes:')
        for m in missing:
            print(f'   · {m}')
        print(f'\nColocalos en: {SCRIPT_DIR}')
        sys.exit(1)
    print('✅ Datasets validados')

def run_step(label, script_name, extra_env=None):
    """Ejecuta un script del pipeline via runpy con las env vars correctas."""
    script_path = find_script(script_name)
    env = {
        'WEEK':       WEEK,
        'VOL_NUM':    VOL_NUM,
        'PERIODO':    PERIODO,
        'MES_ANO':    MES_ANO,
        'FECHA_PUB':  FECHA_PUB,
        'OUTPUTS_DIR': OUTPUT_DIR,
        'PICKLE_RND': str(Path(__file__).parent / f'rnd_w{VOL_NUM}_data.pkl'),
        'PICKLE_CR':  str(Path(__file__).parent / f'cr_w{VOL_NUM}_data.pkl'),
    }
    if extra_env:
        env.update(extra_env)
    os.environ.update(env)

    print(f'\n[{label}] {script_name}...')
    try:
        # Run script in its own directory so relative imports and file lookups work
        original_dir = os.getcwd()
        os.chdir(script_path.parent)
        runpy.run_path(str(script_path), run_name='__main__')
        os.chdir(original_dir)
        print(f'  ✓ {script_name} completado')
    except SystemExit:
        pass  # runpy puede lanzar SystemExit(0) al terminar — es normal
    except Exception as e:
        os.chdir(original_dir)
        print(f'  ❌ Error en {script_name}: {e}')
        raise

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 60)
    print(f'  calc_supply.py · {WEEK} · {PERIODO}')
    print('=' * 60)

    # 0. Validar datasets
    validate_datasets()

    # Asegurar que el output dir existe
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 1. Calcular RND → pickle
    run_step('1/6', 'calc_rnd.py')

    # 2. Calcular CR → pickle
    run_step('2/6', 'calc_cr.py')

    # 3. Render RND parciales
    for i, script in enumerate(['render_rnd_p1.py', 'render_rnd_p2.py', 'render_rnd_p3.py'], 1):
        run_step(f'3.{i}/6', script)

    # 4. Render CR parciales
    for i, script in enumerate(['render_cr_p1.py', 'render_cr_p2.py', 'render_cr_p3.py'], 1):
        run_step(f'4.{i}/6', script)

    # 5. Ensamblar HTML unificado
    run_step('5/6', 'assemble_unified.py')

    # 6. Generar Excels
    run_step('6a/7', 'excel_rnd.py')
    run_step('6b/7', 'excel_cr.py')

    # 7. Generar Mail
    run_step('7/7', 'render_mail_v3.py')

    # 8. Build package (index.html)
    run_step('8/7', 'build_package.py')

    # ── Resumen ──
    print('\n' + '=' * 60)
    output_path = Path(OUTPUT_DIR)
    outputs = [
        output_path / f'SUPPLY_W{VOL_NUM}.html',
        output_path / f'Analisis_RatesNoDispo_W{VOL_NUM}.xlsx',
        output_path / f'Analisis_CheckRates_W{VOL_NUM}.xlsx',
        output_path / f'Mail_W{VOL_NUM}.html',
        Path(__file__).parent / 'index.html',
    ]
    print(f'\n✅ Pipeline completado · {WEEK} · {PERIODO}')
    print(f'\nOutputs en: {OUTPUT_DIR}')
    for f in outputs:
        if f.exists():
            size_kb = f.stat().st_size / 1024
            print(f'  ✓ {f.name} · {size_kb:.0f} KB')
        else:
            print(f'  ✗ {f.name} · NO GENERADO')
    print()
