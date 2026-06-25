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
WEEK        = 'W25'
VOL_NUM     = '25'
PERIODO     = '15 – 21 jun 2026'
MES_ANO     = 'Junio 2026'
FECHA_PUB   = 'LUNES 22 de Junio de 2026'

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
        # Bookability es opcional si el pickle ya existe (re-pipeline sin nuevo dataset BK)
        # f'Dataset_Bookability_W{WEEK_NUM}.xlsx',
    ]
    # Aliases aceptados para Bookability (el archivo puede llamarse Dataset_bookability.xlsx)
    bk_aliases = ['Dataset_bookability.xlsx', f'Dataset_Bookability_W{WEEK_NUM}.xlsx']
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
        'OUTPUTS_DIR': str(Path(__file__).parent),
        'OUTPUT_DIR':  str(Path(__file__).parent),
        'UPLOADS_DIR': str(Path(__file__).parent),
        'PROJECT_DIR': str(Path(__file__).parent),
        'PICKLE_RND': str(Path(__file__).parent / f'rnd_w{VOL_NUM}_data.pkl'),
        'PICKLE_CR':  str(Path(__file__).parent / f'cr_w{VOL_NUM}_data.pkl'),
        'PICKLE_BK':  str(Path(__file__).parent / f'bk_w{VOL_NUM}_data.pkl'),
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
    run_step('1/7', 'calc_rnd.py')

    # 2. Calcular CR → pickle
    run_step('2/7', 'calc_cr.py')

    # 3. Calcular Bookability → pickle (opcional si no hay dataset nuevo)
    _bk_dataset_found = any(
        (d / alias).exists()
        for d in [SCRIPT_DIR, PROJECT_DIR, Path('/mnt/user-data/uploads')]
        for alias in ['Dataset_bookability.xlsx', f'Dataset_Bookability_W{WEEK_NUM}.xlsx']
    )
    _bk_pickle = Path(__file__).parent / f'bk_w{VOL_NUM}_data.pkl'
    if _bk_dataset_found:
        run_step('3/7', 'calc_bk.py')
    elif _bk_pickle.exists():
        print(f'\n[3/7] calc_bk.py omitido — usando pickle existente {_bk_pickle.name}')
    else:
        print(f'\n[3/7] ⚠️  calc_bk.py omitido — sin dataset ni pickle BK (BK quedará vacío en el HTML)')

    # 4. Render RND parciales
    for i, script in enumerate(['render_rnd_p1.py', 'render_rnd_p2.py', 'render_rnd_p3.py'], 1):
        run_step(f'4.{i}/7', script)

    # 5. Render CR parciales
    for i, script in enumerate(['render_cr_p1.py', 'render_cr_p2.py', 'render_cr_p3.py'], 1):
        run_step(f'5.{i}/7', script)

    # 6. Ensamblar HTML unificado
    run_step('6/7', 'assemble_unified.py')

    # 7. Generar Excels
    run_step('7a/8', 'excel_rnd.py')
    run_step('7b/8', 'excel_cr.py')

    # 8. Generar Mail
    run_step('8/8', 'render_mail_v3.py')

    # 9. Build package (index.html)
    run_step('9/8', 'build_package.py')

    # ── 10. Copiar HTML a reports/week-NN/ en disco ─────────────────────────
    # assemble_unified.py escribe SUPPLY_WNN.html en OUTPUTS_DIR (la raíz),
    # pero el HTML "oficial" del repo vive en reports/week-NN/. Sin esta copia,
    # reports/week-NN/SUPPLY_WNN.html queda con la versión vieja y genera
    # confusión (el usuario abre el viejo mientras el nuevo está solo en el ZIP).
    script_dir = Path(__file__).parent
    wn = VOL_NUM.zfill(2)
    # assemble escribe SUPPLY_WNN.html en OUTPUTS_DIR. Buscar en las ubicaciones
    # posibles (raíz del repo en local; /mnt/user-data/outputs en Claude).
    _candidates = [
        # El staging Price_W{NN}/ es la fuente autoritativa (es la que se empaca en el ZIP).
        script_dir.parent / f'Price_W{VOL_NUM}' / 'reports' / f'week-{wn}' / f'SUPPLY_W{VOL_NUM}.html',
        Path(os.getenv('OUTPUTS_DIR', str(script_dir))) / f'SUPPLY_W{VOL_NUM}.html',
        script_dir / f'SUPPLY_W{VOL_NUM}.html',
        Path('/mnt/user-data/outputs') / f'SUPPLY_W{VOL_NUM}.html',
    ]
    _src_html = next((c for c in _candidates if c.exists()), None)
    _dst_html = script_dir / f'reports/week-{wn}/SUPPLY_W{VOL_NUM}.html'
    if _src_html:
        _dst_html.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_src_html, _dst_html)
        print(f'\n[10/10] HTML copiado a reports/week-{wn}/ ({_dst_html.stat().st_size//1024} KB)')
    else:
        print(f'\n[10/10] ⚠️  No se encontró SUPPLY_W{VOL_NUM}.html — reports/week-{wn}/ no actualizado')

    # ── Resumen ──
    print('\n' + '=' * 60)
    outputs = [
        (script_dir / f'reports/week-{wn}/SUPPLY_W{VOL_NUM}.html',                    'SUPPLY_W{}.html'.format(VOL_NUM)),
        (script_dir / f'checkrates/week-{wn}/Analisis_CheckRates_W{VOL_NUM}.xlsx',     'Analisis_CheckRates_W{}.xlsx'.format(VOL_NUM)),
        (script_dir / f'rates-nodispo/week-{wn}/Analisis_RatesNoDispo_W{VOL_NUM}.xlsx','Analisis_RatesNoDispo_W{}.xlsx'.format(VOL_NUM)),
        (script_dir / f'_email' / f'week-{wn}' / f'Mail_W{VOL_NUM}.html',              'Mail_W{}.html'.format(VOL_NUM)),
        (script_dir / 'index.html',                                                     'index.html'),
        (script_dir / f'Price_W{VOL_NUM}.zip',                                         'Price_W{}.zip'.format(VOL_NUM)),
    ]
    print(f'\n✅ Pipeline completado · {WEEK} · {PERIODO}')
    print(f'\nOutputs en: {script_dir}')
    for path, name in outputs:
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f'  ✓ {name} · {size_kb:.0f} KB')
        else:
            print(f'  ✗ {name} · NO GENERADO')
    print()


