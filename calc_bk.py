"""
calc_bk.py · Cálculo métricas Bookability WNN
Genera pickle bk_wNN_data.pkl con todos los agregados necesarios.

Dataset: Dataset_Bookability_WNN.xlsx
Columnas: Provider, LOB, SourceMarket, Destination, Corporate, Hotel, Semana, Bookability, Books

Diferencias clave vs CR/RND:
- No tiene canastas (cross-canasta, es la salud de cada interface)
- Dimensión principal: Provider (+ Destino, Corp, Hotel)
- Bookability ponderada = sum(Bookability * Books) / sum(Books)
- Bandas: mismas que Eficacia CR (>= 97% Exitosa, 93-97% Aceptable, etc.)
- Para W24+: el dataset solo trae la semana actual; W_PREV se usa como WoW
"""
import pickle
import pandas as pd
import numpy as np
import os

from engine import banda_eficacia  # reutilizamos la misma función de bandas

# ── CONFIG ────────────────────────────────────────────────────────────────────
WEEK    = os.getenv('WEEK', 'W23')
VOL_NUM = os.getenv('VOL_NUM', None)
if VOL_NUM is None:
    try:
        WEEK_NUM = int(WEEK.replace('W', ''))
        VOL_NUM = str(WEEK_NUM)
    except:
        VOL_NUM = '23'
else:
    VOL_NUM = str(VOL_NUM)

WEEK_NUM     = int(WEEK.replace('W', ''))
VOL_NUM_PREV = int(VOL_NUM) - 1

PERIODO  = os.getenv('PERIODO',  '2 – 8 jun 2026')
MES_AÑO  = os.getenv('MES_AÑO', 'Junio 2026')
FECHA_PUB = os.getenv('FECHA_PUB', 'LUNES 09 de Junio de 2026')

# Clasificación de providers
PRODUCTO_PROPIO = ['DerbySoft', 'Internal', 'HBSI', 'SynXis', 'Siteminder', 'Travelclick', 'Omnibees']
THIRD_PARTY     = ['Expedia', 'HotelBeds', 'Hotel Unico', 'Travelgate', 'RateFox']
# Rename para mostrar nombres canónicos (igual que CR)
_CHANNEL_RENAME = {'HotelBeds Apitude': 'HotelBeds', 'Hotel Unico V2': 'Hotel Unico'}

MIN_BOOKS = 5  # mínimo de books para incluir en rankings

# ── HELPERS ───────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _find(name):
    import glob as _glob
    for d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
        # Buscar variantes de nombre (mayúsculas/minúsculas, sin semana)
        base = os.path.splitext(name)[0]  # ej: Dataset_Bookability_W23
        # Intentar nombre genérico: Dataset_bookability.xlsx
        generic = os.path.join(d, 'Dataset_bookability.xlsx')
        if os.path.exists(generic):
            return generic
        # Buscar con glob insensible a mayúsculas
        pattern = os.path.join(d, '[Dd]ataset_[Bb]ookability*.xlsx')
        matches = _glob.glob(pattern)
        if matches:
            return matches[0]
    raise FileNotFoundError(f'{name} no encontrado')

def bk_weighted(df):
    """Bookability ponderada por Books."""
    total_books = df['Books'].sum()
    if total_books == 0:
        return 0.0
    return (df['Bookability'] * df['Books']).sum() / total_books

def banda_bk(val):
    """Mismas bandas que Eficacia CR."""
    return banda_eficacia(val)

def grupo_provider(provider):
    if provider in PRODUCTO_PROPIO:
        return 'Producto Propio'
    if provider in THIRD_PARTY:
        return 'Third Party'
    return 'Otro'

def fmt_pct(v):
    return f'{v*100:.2f}%'

# ── CARGA ─────────────────────────────────────────────────────────────────────
def load_bk(path, week_num=None):
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    df['Bookability'] = pd.to_numeric(df['Bookability'], errors='coerce').fillna(0).clip(0, 1)
    df['Books']       = pd.to_numeric(df['Books'],       errors='coerce').fillna(0).astype(int)
    # Normalizar nombre de columnas
    if 'Destination' in df.columns:
        df.rename(columns={'Destination': 'Destino'}, inplace=True)
    if 'Corporate' in df.columns:
        df.rename(columns={'Corporate': 'CorpName'}, inplace=True)
    # Agregar tipo de provider
    df['TipoProvider'] = df['Provider'].apply(grupo_provider)
    # Filtrar por semana si se especifica
    if week_num is not None and 'Semana' in df.columns:
        df = df[df['Semana'] == week_num].copy()
    return df


# Estrategia de carga W24+:
#   - df_cur:  Dataset_bookability_W{NN}.xlsx filtrado a Semana==NN  (datos completos de la semana)
#   - df_prev: Dataset_bookability.xlsx filtrado a Semana==NN-1      (acumulado histórico, prev)
# Fallback: si no existe el semanal específico, usar acumulado para ambos.
import glob as _glob_mod

def _find_semanal(week_n):
    """Busca Dataset_bookability_W{N}.xlsx en los dirs de búsqueda."""
    name = f'Dataset_bookability_W{week_n}.xlsx'
    for d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    # También buscar con mayúscula
    name_cap = f'Dataset_Bookability_W{week_n}.xlsx'
    for d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
        p = os.path.join(d, name_cap)
        if os.path.exists(p):
            return p
    return None

_semanal_path = _find_semanal(WEEK_NUM)
_acumulado_path = None
for _d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
    _p = os.path.join(_d, 'Dataset_bookability.xlsx')
    if os.path.exists(_p):
        _acumulado_path = _p
        break

if _semanal_path and _acumulado_path:
    # Caso W24+: semanal para cur, acumulado para prev
    df_cur  = load_bk(_semanal_path, week_num=WEEK_NUM)
    df_prev = load_bk(_acumulado_path, week_num=WEEK_NUM - 1)
    print(f"✅ W{WEEK_NUM}: semanal ({os.path.basename(_semanal_path)}) filtrado → Semana {WEEK_NUM}")
    print(f"   W{WEEK_NUM-1}: acumulado ({os.path.basename(_acumulado_path)}) filtrado → Semana {WEEK_NUM-1}")
elif _acumulado_path:
    # Fallback: solo acumulado disponible — filtrar por semana
    df_cur  = load_bk(_acumulado_path, week_num=WEEK_NUM)
    df_prev = load_bk(_acumulado_path, week_num=WEEK_NUM - 1)
    print(f"✅ Dataset acumulado ({os.path.basename(_acumulado_path)}), filtrando semanas {WEEK_NUM} y {WEEK_NUM-1}")
else:
    raise FileNotFoundError(f'No se encontró ningún dataset de bookability para W{WEEK_NUM}')

print(f"   W{WEEK_NUM}: {len(df_cur):,} filas · {df_cur['Books'].sum():,} books")
print(f"   W{VOL_NUM_PREV}: {len(df_prev):,} filas · {df_prev['Books'].sum():,} books")

# Normalizar nombre de canales para display (igual que CR)
df_cur['Provider']  = df_cur['Provider'].replace(_CHANNEL_RENAME)
df_prev['Provider'] = df_prev['Provider'].replace(_CHANNEL_RENAME)
# Re-clasificar TipoProvider después del rename
df_cur['TipoProvider']  = df_cur['Provider'].apply(grupo_provider)
df_prev['TipoProvider'] = df_prev['Provider'].apply(grupo_provider)

# ── MÉTRICAS GLOBALES ─────────────────────────────────────────────────────────
bk_global     = bk_weighted(df_cur)
bk_global_prev = bk_weighted(df_prev)
bk_global_wow  = bk_global - bk_global_prev
books_global   = int(df_cur['Books'].sum())
books_global_prev = int(df_prev['Books'].sum())
hoteles_global = df_cur['Hotel'].nunique()

banda_global = banda_bk(bk_global)

print(f"\n📊 Bookability Global W{WEEK_NUM}: {bk_global*100:.2f}% ({banda_global})")
print(f"   WoW: {bk_global_wow*100:+.2f}pp")

# ── AGREGADOS POR DIMENSIÓN ───────────────────────────────────────────────────

def agg_dim(df, col, min_books=MIN_BOOKS):
    """Agrega Bookability ponderada por una dimensión."""
    g = df.groupby(col, as_index=False).apply(
        lambda x: pd.Series({
            'Bookability': bk_weighted(x),
            'Books':       int(x['Books'].sum()),
            'Hoteles':     x['Hotel'].nunique() if 'Hotel' in x.columns else 0,
        })
    ).reset_index(drop=True)
    g = g[g['Books'] >= min_books].copy()
    g['BandaBK'] = g['Bookability'].apply(banda_bk)
    return g.sort_values('Bookability')

def agg_dim_wow(df_cur, df_prev, col, min_books=MIN_BOOKS):
    """Agrega con WoW vs semana anterior."""
    g_cur  = agg_dim(df_cur,  col, min_books=0)
    g_prev = agg_dim(df_prev, col, min_books=0)
    g = g_cur.merge(
        g_prev[[col, 'Bookability', 'Books']].rename(columns={
            'Bookability': 'Bookability_prev',
            'Books':       'Books_prev',
        }),
        on=col, how='left'
    )
    g['BK_WoW_pp'] = g['Bookability'] - g['Bookability_prev'].fillna(g['Bookability'])
    # Books WoW absoluto y porcentual
    g['Books_WoW_abs'] = g['Books'] - g['Books_prev'].fillna(g['Books'])
    g['Books_WoW_pct'] = ((g['Books'] - g['Books_prev']) / g['Books_prev'].replace(0, pd.NA) * 100).fillna(0)
    g = g[g['Books'] >= min_books].copy()
    g['BandaBK'] = g['Bookability'].apply(banda_bk)
    return g.sort_values('Bookability')

# Por Provider
g_provider = agg_dim_wow(df_cur, df_prev, 'Provider')
g_provider['TipoProvider'] = g_provider['Provider'].apply(grupo_provider)

# Por Destino
g_dest = agg_dim_wow(df_cur, df_prev, 'Destino')

# Por Corporativo
g_corp = agg_dim_wow(df_cur, df_prev, 'CorpName')

# Por Hotel
g_hotel = agg_dim_wow(df_cur, df_prev, 'Hotel', min_books=MIN_BOOKS)
# Arrastrar CorpName principal por hotel (el corp con más books en la semana actual)
_hotel_corp = (df_cur.groupby('Hotel', as_index=False)
                     .apply(lambda x: x.loc[x['Books'].idxmax(), 'CorpName'] if 'CorpName' in x.columns and len(x) > 0 else '')
                     .reset_index())
_hotel_corp.columns = ['idx_drop', 'Hotel', 'CorpName'] if len(_hotel_corp.columns) == 3 else _hotel_corp.columns
# Forma alternativa más robusta
if 'CorpName' in df_cur.columns:
    _hc = df_cur.groupby('Hotel').apply(lambda x: x.loc[x['Books'].idxmax(), 'CorpName']).reset_index()
    _hc.columns = ['Hotel', 'CorpName']
    g_hotel = g_hotel.merge(_hc, on='Hotel', how='left')
    g_hotel['CorpName'] = g_hotel['CorpName'].fillna('')

print(f"\n   Providers: {len(g_provider)}")
print(f"   Destinos:  {len(g_dest)}")
print(f"   Corps:     {len(g_corp)}")
print(f"   Hoteles:   {len(g_hotel)}")

# ── TOP RANKINGS ──────────────────────────────────────────────────────────────

TOP_N = 100  # Para tablas del reporte

def make_top(df, col, sort_asc=True, n=TOP_N, min_books=None):
    """Top N filas ordenadas por Bookability, con umbral de volumen opcional."""
    df2 = df.copy()
    if min_books is not None:
        df2 = df2[df2['Books'] >= min_books]
    df2 = df2.sort_values('Bookability', ascending=sort_asc).head(n)
    return df2

# Umbrales de volumen por dimensión: evitar destinos/corps con 5-10 trx que dominan el top
TOP_PROVIDER = make_top(g_provider, 'Provider',   min_books=50)
TOP_DEST     = make_top(g_dest,     'Destino',     min_books=50)
TOP_CORP     = make_top(g_corp,     'CorpName',    min_books=20)
TOP_HOTEL    = make_top(g_hotel,    'Hotel',       min_books=20)

# ── Severity counts (sobre todos los hoteles con MIN_BOOKS) ──────────────────
# Igual lógica que CR: contar hoteles por banda
sev_bk_p80 = g_hotel['BandaBK'].value_counts().to_dict()
# Asegurar todas las bandas
for _b in ['Súper Crítica', 'Crítica', 'Revisar', 'Aceptable', 'Exitosa']:
    sev_bk_p80.setdefault(_b, 0)
p80_hoteles_bk = int(g_hotel['Hotel'].nunique())
print(f'\n   Severity BK (P80): {sev_bk_p80}')

# ── MÉTRICAS PARA CFB (strip de métricas en la barra de canasta) ──────────────
# Bookability no tiene canastas, pero sí se muestra en el CFB con valor fijo
M = {
    f'global_w{WEEK_NUM}': {
        'bk':          bk_global,
        'bk_fmt':      fmt_pct(bk_global),
        'bk_prev':     bk_global_prev,
        'bk_prev_fmt': fmt_pct(bk_global_prev),
        'bk_wow':      bk_global_wow,
        'bk_wow_fmt':  f'{bk_global_wow*100:+.2f}pp',
        'books':       books_global,
        'hoteles':     hoteles_global,
        'banda':       banda_global,
    }
}

# ── HISTÓRICO (para canvas del reporte) ───────────────────────────────────────
# Calculamos por semana desde el dataset acumulado
# Cuando sea W24+, el histórico vendrá del HIST_DATA de historico_data.py
hist_by_week = {}
# Para el histórico usamos el acumulado (W16-W{NN-1}) + la semana actual del semanal
if _acumulado_path:
    df_all = pd.read_excel(_acumulado_path)
    df_all['Bookability'] = pd.to_numeric(df_all['Bookability'], errors='coerce').fillna(0).clip(0, 1)
    df_all['Books']       = pd.to_numeric(df_all['Books'],       errors='coerce').fillna(0).astype(int)
    for sem in sorted(df_all['Semana'].unique()):
        if int(sem) >= WEEK_NUM:
            continue  # la semana actual la ponemos desde df_cur (semanal completo)
        df_s = df_all[df_all['Semana'] == sem]
        hist_by_week[f'W{int(sem)}'] = {
            'bk':    bk_weighted(df_s),
            'books': int(df_s['Books'].sum()),
        }
# Agregar semana actual desde df_cur (fuente correcta)
hist_by_week[f'W{WEEK_NUM}'] = {
    'bk':    bk_global,
    'books': books_global,
}
print(f"\n   Histórico por semana: {list(hist_by_week.keys())}")

# ── PICKLE ────────────────────────────────────────────────────────────────────
D = {
    'WEEK':        WEEK,
    'VOL_NUM':     VOL_NUM,
    'PERIODO':     PERIODO,
    'MES_AÑO':     MES_AÑO,
    'FECHA_PUB':   FECHA_PUB,
    # Métricas globales
    'M':           M,
    'bk_global':   bk_global,
    'bk_prev':     bk_global_prev,
    'bk_wow':      bk_global_wow,
    'books_global': books_global,
    'books_global_prev': books_global_prev,
    'hoteles_global': hoteles_global,
    'banda_global': banda_global,
    # Agregados por dimensión (con WoW)
    'g_provider':  g_provider,
    'g_dest':      g_dest,
    'g_corp':      g_corp,
    'g_hotel':     g_hotel,
    # Top rankings
    'TOP_PROVIDER': TOP_PROVIDER,
    'TOP_DEST':    TOP_DEST,
    'TOP_CORP':    TOP_CORP,
    'TOP_HOTEL':   TOP_HOTEL,
    'sev_bk_p80':  sev_bk_p80,
    'p80_hoteles_bk': p80_hoteles_bk,
    # DataFrames originales
    'df_cur':      df_cur,
    'df_prev':     df_prev,
    # Histórico por semana
    'hist_by_week': hist_by_week,
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'bk_w{VOL_NUM}_data.pkl')
with open(out_path, 'wb') as f:
    pickle.dump(D, f)

print(f"\n✅ Pickle guardado: bk_w{VOL_NUM}_data.pkl")
print(f"   Bookability global: {bk_global*100:.2f}% ({banda_global}) · WoW {bk_global_wow*100:+.2f}pp")
