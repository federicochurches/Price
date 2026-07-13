"""_copy_to_archive.py · Copia los outputs generados en la raíz a sus carpetas
de archivo (reports/week-NN/, checkrates/week-NN/, rates-nodispo/week-NN/)
ANTES de que corra build_package.py (que limpia la raíz).

Este paso existía solo en calc_supply.py (fix documentado en W24-rnd-ar-card:
"copia SUPPLY_WNN.html a reports/week-NN/ ANTES de build_package") pero
run_pipeline.py nunca lo heredó — por eso la raíz se actualizaba bien pero
las carpetas de archivo quedaban con la versión de la semana anterior.
"""
import os, shutil
from pathlib import Path
from regional_config import REGIONES
from accounts_config import ACCOUNT_GROUPS

WEEK = os.getenv('WEEK', 'W00')
VOL_NUM = os.getenv('VOL_NUM', '0')
WEEK_NUM = int(VOL_NUM)
week_dir = f'week-{WEEK_NUM:02d}'
root = Path('.')

pairs = [
    (root / f'SUPPLY_{WEEK}.html',
     root / 'reports' / week_dir / f'SUPPLY_{WEEK}.html'),
    (root / f'Analisis_CheckRates_{WEEK}.xlsx',
     root / 'checkrates' / week_dir / f'Analisis_CheckRates_{WEEK}.xlsx'),
    (root / f'Analisis_RatesNoDispo_{WEEK}.xlsx',
     root / 'rates-nodispo' / week_dir / f'Analisis_RatesNoDispo_{WEEK}.xlsx'),
]

# Excels regionales (México/US/CALA) y por cuenta (Global Accounts/Estratégicas) —
# excel_*_regional.py y excel_*_accounts.py escriben siempre a regional/ y accounts/
# en la raíz (todas las semanas mezcladas); acá se archivan igual que el resto.
for region in REGIONES.values():
    pairs.append((root / 'regional' / f'Analisis_CR_{region["file"]}_{WEEK}.xlsx',
                  root / 'checkrates' / week_dir / 'regional' / f'Analisis_CR_{region["file"]}_{WEEK}.xlsx'))
    pairs.append((root / 'regional' / f'Analisis_RND_{region["file"]}_{WEEK}.xlsx',
                  root / 'rates-nodispo' / week_dir / 'regional' / f'Analisis_RND_{region["file"]}_{WEEK}.xlsx'))
for account in ACCOUNT_GROUPS:
    pairs.append((root / 'accounts' / f'Analisis_CR_{account["file"]}_{WEEK}.xlsx',
                  root / 'checkrates' / week_dir / 'accounts' / f'Analisis_CR_{account["file"]}_{WEEK}.xlsx'))
    pairs.append((root / 'accounts' / f'Analisis_RND_{account["file"]}_{WEEK}.xlsx',
                  root / 'rates-nodispo' / week_dir / 'accounts' / f'Analisis_RND_{account["file"]}_{WEEK}.xlsx'))

for src, dst in pairs:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f'  copiado: {src.name} -> {dst}')
    else:
        print(f'  (omitido, no se encontro en la raiz): {src.name}')

print('Copia a carpetas de archivo completada.')
