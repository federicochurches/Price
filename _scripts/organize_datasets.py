#!/usr/bin/env python3
"""
organize_datasets.py · Organiza los datasets semanales en el repo PRICE

USO:
    python organize_datasets.py <SEMANA> <PATH_ND> <PATH_CK>

EJEMPLO:
    python organize_datasets.py 17 ~/Downloads/Rates_NoDispo_W17.xlsx ~/Downloads/CheckRates_W17.xlsx

QUÉ HACE:
    1. Crea carpetas datasets/rates-nodispo/week-NN/ y datasets/checkrates/week-NN/
    2. Copia los datasets con nombres estandarizados
    3. Muestra un resumen de lo que quedó guardado
"""

import sys
import os
import shutil

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    week_num  = int(sys.argv[1])
    path_nd   = sys.argv[2]
    path_ck   = sys.argv[3]
    week_str  = f"week-{week_num:02d}"

    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Carpetas destino
    dir_nd = os.path.join(REPO_ROOT, 'datasets', 'rates-nodispo', week_str)
    dir_ck = os.path.join(REPO_ROOT, 'datasets', 'checkrates', week_str)

    os.makedirs(dir_nd, exist_ok=True)
    os.makedirs(dir_ck, exist_ok=True)

    # Nombres estandarizados
    dest_nd = os.path.join(dir_nd, f'Rates_NoDispo_W{week_num:02d}.xlsx')
    dest_ck = os.path.join(dir_ck, f'CheckRates_W{week_num:02d}.xlsx')

    shutil.copy2(path_nd, dest_nd)
    shutil.copy2(path_ck, dest_ck)

    print(f"\n✓ Datasets Week {week_num} organizados:")
    print(f"  RatesNoDispo → {dest_nd}")
    print(f"               {os.path.getsize(dest_nd)/1_000_000:.1f} MB")
    print(f"  CheckRates   → {dest_ck}")
    print(f"               {os.path.getsize(dest_ck)/1_000_000:.1f} MB")
    print(f"\nEstructura del repo:")
    print(f"  datasets/")
    print(f"    rates-nodispo/{week_str}/Rates_NoDispo_W{week_num:02d}.xlsx")
    print(f"    checkrates/{week_str}/CheckRates_W{week_num:02d}.xlsx")
    print(f"\nCommit sugerido:")
    print(f"  datasets: Week {week_num} · RatesNoDispo + CheckRates")

if __name__ == '__main__':
    main()
