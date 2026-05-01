#!/usr/bin/env python3
"""
PRICE · Release semanal automatizado.

Uso:
    python _scripts/release_week.py --week 18 --periodo "27 Abr - 3 May 2026"

Asume que en _scripts/inputs/ están los 2 datasets crudos:
    - data_set_checkrates_W{NN}.xlsx
    - Week{NN}RatesNoDispo.xlsx (o cualquier xlsx que tenga 'NoDispo' en el nombre)

Outputs · pone los archivos en sus rutas correctas del repo:
    checkrates/week-NN/Analisis_Checkrates_7d_W{NN}.xlsx
    checkrates/week-NN/data_set_checkrates_W{NN}.xlsx (copia del input)
    rates-nodispo/week-NN/Analisis_Rates_NoDispo_7d_W{NN}.xlsx
    rates-nodispo/week-NN/Week{NN}RatesNoDispo.xlsx (copia del input)
    _email/week-NN/Mail_W{NN}.html
    index.html (actualizado)

Después corré commit_release.py para commit + push.
"""
import argparse
import shutil
import sys
from pathlib import Path

# Asumir estructura: <repo>/_scripts/release_week.py
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INPUT_DIR = SCRIPT_DIR / 'inputs'

# Agregar lib al path
sys.path.insert(0, str(SCRIPT_DIR / 'lib'))

from calculate_kpis import calculate_cr_kpis, calculate_rnd_kpis
from generate_xlsx import generate_cr_xlsx, generate_rnd_xlsx
from generate_mail import generate_mail
from update_index import update_index


def find_dataset(week, pattern_words):
    """Busca un dataset en INPUT_DIR que contenga las palabras del pattern."""
    week_str_options = [f'W{week}', f'W{week:02d}', f'Week{week}', f'Week-{week}', f'Week {week}']
    
    for f in INPUT_DIR.glob('*.xlsx'):
        name_lower = f.name.lower()
        # Match por palabras del pattern
        if all(w.lower() in name_lower for w in pattern_words):
            # Match por número de semana
            if any(ws.lower() in f.name.lower().replace('-', '').replace(' ', '').replace('_', '') 
                   for ws in [f'w{week}', f'w{week:02d}', f'week{week}']):
                return f
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, required=True, help='Número de semana (ej: 18)')
    parser.add_argument('--periodo', type=str, required=True, help='Periodo (ej: "27 Abr - 3 May 2026")')
    parser.add_argument('--cr-input', type=str, default=None)
    parser.add_argument('--rnd-input', type=str, default=None)
    args = parser.parse_args()
    
    week = args.week
    periodo = args.periodo
    
    print(f"\n{'#'*60}")
    print(f"# PRICE · Release Week {week} · {periodo}")
    print(f"{'#'*60}\n")
    
    # Validar carpeta inputs
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir(parents=True)
    
    # Encontrar datasets
    cr_dataset = Path(args.cr_input) if args.cr_input else find_dataset(week, ['checkrates'])
    rnd_dataset = Path(args.rnd_input) if args.rnd_input else find_dataset(week, ['nodispo'])
    
    if not cr_dataset or not cr_dataset.exists():
        print(f"✗ Dataset CR no encontrado · esperado en _scripts/inputs/data_set_checkrates_W{week}.xlsx")
        print(f"  Archivos disponibles en inputs/:")
        for f in INPUT_DIR.glob('*.xlsx'):
            print(f"    · {f.name}")
        sys.exit(1)
    if not rnd_dataset or not rnd_dataset.exists():
        print(f"✗ Dataset RND no encontrado · esperado en _scripts/inputs/Week{week}RatesNoDispo.xlsx")
        sys.exit(1)
    
    print(f"✓ CR dataset:  {cr_dataset.name}")
    print(f"✓ RND dataset: {rnd_dataset.name}")
    print(f"✓ Repo root:   {REPO_ROOT}")
    print()
    
    # Confirmar
    resp = input("¿Continuar con la generación? [y/N] ").strip().lower()
    if resp != 'y':
        print("Cancelado.")
        sys.exit(0)
    
    # ========================================================
    # PASO 1 · Calcular KPIs CR
    # ========================================================
    print(f"\n{'='*60}\nPASO 1 · Procesando CheckRates W{week}\n{'='*60}")
    cr_data = calculate_cr_kpis(cr_dataset)
    print(f"  Hoteles:    {cr_data['kpis']['total_hot']:,}")
    print(f"  P80:        {cr_data['kpis']['p80_count']:,}")
    print(f"  Eficacia:   {cr_data['kpis']['eficacia']:.2f}%")
    print(f"  CR:         {cr_data['kpis']['cr']:.2f}%")
    print(f"  Bookings:   {cr_data['kpis']['total_bkgs']:,}")
    
    # ========================================================
    # PASO 2 · Calcular KPIs RND
    # ========================================================
    print(f"\n{'='*60}\nPASO 2 · Procesando RatesNoDispo W{week}\n{'='*60}")
    rnd_data = calculate_rnd_kpis(rnd_dataset)
    print(f"  Hoteles:    {rnd_data['kpis']['total_hot']:,}")
    print(f"  P80:        {rnd_data['kpis']['p80_count']:,}")
    print(f"  %NoDispo:   {rnd_data['kpis']['nodispo_pond']:.2f}%")
    print(f"  Tráfico:    {rnd_data['kpis']['total_traf']/1e6:.1f}M")
    print(f"  GB:         ${rnd_data['kpis']['total_gb']/1e6:.2f}M")
    print(f"  CorpName:   {'SÍ' if rnd_data['kpis']['has_corp'] else 'NO ⚠'}")
    
    # ========================================================
    # PASO 3 · Generar Excels
    # ========================================================
    print(f"\n{'='*60}\nPASO 3 · Generando Excels Top 50\n{'='*60}")
    cr_xlsx = REPO_ROOT / 'checkrates' / f'week-{week}' / f'Analisis_Checkrates_7d_W{week}.xlsx'
    rnd_xlsx = REPO_ROOT / 'rates-nodispo' / f'week-{week}' / f'Analisis_Rates_NoDispo_7d_W{week}.xlsx'
    
    generate_cr_xlsx(cr_data, week, periodo, cr_xlsx)
    print(f"  ✓ {cr_xlsx.relative_to(REPO_ROOT)}")
    generate_rnd_xlsx(rnd_data, week, periodo, rnd_xlsx)
    print(f"  ✓ {rnd_xlsx.relative_to(REPO_ROOT)}")
    
    # ========================================================
    # PASO 4 · Copiar datasets crudos
    # ========================================================
    print(f"\n{'='*60}\nPASO 4 · Copiando datasets crudos\n{'='*60}")
    cr_dest = REPO_ROOT / 'checkrates' / f'week-{week}' / f'data_set_checkrates_W{week}.xlsx'
    rnd_dest = REPO_ROOT / 'rates-nodispo' / f'week-{week}' / f'Week{week}RatesNoDispo.xlsx'
    cr_dest.parent.mkdir(parents=True, exist_ok=True)
    rnd_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cr_dataset, cr_dest)
    print(f"  ✓ {cr_dest.relative_to(REPO_ROOT)}")
    shutil.copy2(rnd_dataset, rnd_dest)
    print(f"  ✓ {rnd_dest.relative_to(REPO_ROOT)}")
    
    # ========================================================
    # PASO 5 · Generar mail
    # ========================================================
    print(f"\n{'='*60}\nPASO 5 · Generando mail unificado\n{'='*60}")
    mail_path = REPO_ROOT / '_email' / f'week-{week}' / f'Mail_W{week}.html'
    generate_mail(week, periodo, cr_data, rnd_data, mail_path)
    print(f"  ✓ {mail_path.relative_to(REPO_ROOT)}")
    
    # ========================================================
    # PASO 6 · Actualizar index.html
    # ========================================================
    print(f"\n{'='*60}\nPASO 6 · Actualizando index.html\n{'='*60}")
    index_path = REPO_ROOT / 'index.html'
    if index_path.exists():
        update_index(index_path, week, periodo, cr_data, rnd_data)
        print(f"  ✓ {index_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  ⚠ index.html no existe · saltando")
    
    # ========================================================
    # AVISO · falta lo manual
    # ========================================================
    print(f"\n{'='*60}\n⚠ FALTA HACER MANUALMENTE\n{'='*60}")
    print(f"""
Los reportes editoriales HTML los generás en una sesión con Claude:
  · {REPO_ROOT}/checkrates/week-{week}/CheckRates_Reporte_Editorial.html
  · {REPO_ROOT}/rates-nodispo/week-{week}/RatesNoDispo_Reporte_Editorial.html

Cuando los tengas, corré:
  python _scripts/commit_release.py --week {week} --periodo "{periodo}"
""")
    print("✓ Generación completada\n")


if __name__ == "__main__":
    main()
