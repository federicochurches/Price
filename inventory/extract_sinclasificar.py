"""
extract_sinclasificar.py
========================
Dos modos de uso:

MODO 1 — Extraer hoteles sin destino a Excel:
    python extract_sinclasificar.py extract

MODO 2 — Convertir Excel completado a dest_mapping.py:
    python extract_sinclasificar.py build

El Excel de salida (hoteles_sinclasificar.xlsx) tiene columnas:
    Hotel | Corporativo | Region | Tipo | Destino_sugerido (vacío — completar)

Una vez completado el Excel, correr MODO 2 para generar dest_mapping.py.
"""

import sys
import pandas as pd
from pathlib import Path

INPUT_FILE  = "dataHoteles_contratos.xlsx"
EXCEL_OUT   = "hoteles_sinclasificar.xlsx"
MAPPING_OUT = "dest_mapping.py"

TIPO_NORM = {
    'solo tercero':  'sólo terceros',
    'solo propio':   'sólo propio',
}
TIPO_MAP = {
    'sólo propio':          'Solo Propio',
    'Propio_con_tercero':   'Hybrid',
    'sólo terceros':        'Third Party',
}

def load_dataset():
    print(f"Cargando {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE, header=1)
    df.columns = df.columns.str.strip()
    # Excluir sin contrato
    if 'TipoHotel' in df.columns:
        df['TipoHotel'] = df['TipoHotel'].str.strip().str.lower().replace(TIPO_NORM)
        df = df[df['TipoHotel'] != 'sincontrato']
        df['TipoHotel'] = df['TipoHotel'].map(TIPO_MAP).fillna(df['TipoHotel'])
    return df

def extract():
    df = load_dataset()

    # Detectar hoteles sin destino clasificado
    dest_col = next((c for c in df.columns if 'destino' in c.lower()), None)
    hotel_col = next((c for c in df.columns if 'hotel' == c.lower()), 'Hotel')
    corp_col  = next((c for c in df.columns if 'corporativo' in c.lower() or 'corporate' in c.lower()), None)
    region_col = next((c for c in df.columns if 'region' in c.lower()), None)
    tipo_col  = 'TipoHotel'

    if not dest_col:
        print("ERROR: No se encontró columna Destino")
        return

    sin_dest = df[
        df[dest_col].isna() |
        df[dest_col].astype(str).str.strip().isin(['', 'nan', 'SinClasificar', 'sinclasificar', 'Sin Clasificar'])
    ].copy()

    cols = [hotel_col]
    if corp_col:  cols.append(corp_col)
    if region_col: cols.append(region_col)
    if tipo_col in df.columns: cols.append(tipo_col)

    result = sin_dest[cols].drop_duplicates(subset=[hotel_col]).copy()
    result['Destino_sugerido'] = ''  # Columna a completar

    result.to_excel(EXCEL_OUT, index=False)
    print(f"\n✅ {len(result)} hoteles sin clasificar exportados a {EXCEL_OUT}")
    print(f"   Completá la columna 'Destino_sugerido' y corré: python extract_sinclasificar.py build")

def build():
    if not Path(EXCEL_OUT).exists():
        print(f"ERROR: No se encontró {EXCEL_OUT}. Corré primero: python extract_sinclasificar.py extract")
        return

    df = pd.read_excel(EXCEL_OUT)
    hotel_col = df.columns[0]  # Primera columna = Hotel

    # Filtrar solo filas con destino completado
    df = df[df['Destino_sugerido'].notna() & (df['Destino_sugerido'].astype(str).str.strip() != '')]
    
    if len(df) == 0:
        print("No hay destinos completados en el Excel.")
        return

    mapping = {}
    for _, row in df.iterrows():
        hotel = str(row[hotel_col]).strip()
        dest  = str(row['Destino_sugerido']).strip()
        if hotel and dest:
            mapping[hotel] = dest

    lines = ['# dest_mapping.py — generado por extract_sinclasificar.py', 
             '# Editar manualmente o regenerar con: python extract_sinclasificar.py build',
             '',
             'DEST_MAPPING = {']
    for hotel, dest in sorted(mapping.items()):
        hotel_esc = hotel.replace("'", "\\'")
        dest_esc  = dest.replace("'", "\\'")
        lines.append(f"    '{hotel_esc}': '{dest_esc}',")
    lines.append('}')
    lines.append('')

    with open(MAPPING_OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✅ {len(mapping)} hoteles mapeados → {MAPPING_OUT}")
    print(f"   Ahora poné dest_mapping.py en inventory/ y corré calc_inv.py")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'extract'
    if mode == 'extract':
        extract()
    elif mode == 'build':
        build()
    else:
        print(__doc__)
