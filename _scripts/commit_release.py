#!/usr/bin/env python3
"""
PRICE · Commit + Push de release.

Uso:
    python _scripts/commit_release.py --week 18 --periodo "27 Abr - 3 May 2026"

Verifica que TODOS los archivos esperados estén en sus rutas, hace git add selectivo,
commit con mensaje template, y push a main.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

EXPECTED_FILES = [
    'checkrates/week-{week}/CheckRates_Reporte_Editorial.html',
    'checkrates/week-{week}/Analisis_Checkrates_7d_W{week}.xlsx',
    'checkrates/week-{week}/data_set_checkrates_W{week}.xlsx',
    'rates-nodispo/week-{week}/RatesNoDispo_Reporte_Editorial.html',
    'rates-nodispo/week-{week}/Analisis_Rates_NoDispo_7d_W{week}.xlsx',
    'rates-nodispo/week-{week}/Week{week}RatesNoDispo.xlsx',
    '_email/week-{week}/Mail_W{week}.html',
    'index.html',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, required=True)
    parser.add_argument('--periodo', type=str, required=True)
    parser.add_argument('--no-push', action='store_true', help='Hacer commit pero no push')
    parser.add_argument('--message', type=str, default=None, help='Mensaje custom')
    args = parser.parse_args()
    
    week = args.week
    
    print(f"\n{'#'*60}")
    print(f"# PRICE · Commit Week {week}")
    print(f"{'#'*60}\n")
    
    # Verificar archivos esperados
    missing = []
    for tmpl in EXPECTED_FILES:
        path = REPO_ROOT / tmpl.format(week=week)
        if not path.exists():
            missing.append(str(path.relative_to(REPO_ROOT)))
    
    if missing:
        print("✗ Archivos faltantes:")
        for m in missing:
            print(f"  · {m}")
        print("\nGenerá primero con: python _scripts/release_week.py --week {week} --periodo \"...\"")
        print("Y agregá los reportes editoriales HTML manualmente.")
        sys.exit(1)
    
    print("✓ Todos los archivos esperados están presentes")
    print()
    for tmpl in EXPECTED_FILES:
        path = tmpl.format(week=week)
        print(f"  ✓ {path}")
    
    # Confirmar
    print()
    resp = input("¿Hacer git add + commit + push? [y/N] ").strip().lower()
    if resp != 'y':
        print("Cancelado.")
        sys.exit(0)
    
    # git add
    os.chdir(REPO_ROOT)
    print("\n▶ git add .")
    subprocess.run(['git', 'add', '.'], check=True)
    
    # Mensaje
    if args.message:
        msg = args.message
    else:
        msg = f"feat: release W{week} · {args.periodo}"
    
    print(f"\n▶ git commit -m \"{msg}\"")
    try:
        subprocess.run(['git', 'commit', '-m', msg], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error en commit: {e}")
        sys.exit(1)
    
    # push
    if args.no_push:
        print("\n⏭ --no-push · saltando push")
    else:
        print("\n▶ git push origin main")
        try:
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error en push: {e}")
            sys.exit(1)
    
    print(f"\n{'#'*60}")
    print(f"# ✓ Commit Week {week} completado")
    print(f"{'#'*60}\n")
    print("URLs públicas (deploy en 1-2 min):")
    print(f"  Hub:     https://federicochurches.github.io/Price/")
    print(f"  CR:      https://federicochurches.github.io/Price/checkrates/week-{week}/CheckRates_Reporte_Editorial.html")
    print(f"  RND:     https://federicochurches.github.io/Price/rates-nodispo/week-{week}/RatesNoDispo_Reporte_Editorial.html")
    print()


if __name__ == "__main__":
    main()
