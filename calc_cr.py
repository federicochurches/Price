"""
calc_cr.py · Cálculo métricas CheckRates W18
Genera pickle cr_w18_data.pkl con todos los agregados necesarios.
"""
import pickle
import pandas as pd
import numpy as np
import os

from engine import banda_eficacia, banda_convrate, banda_eficacia_tiered, get_dest_tier

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK = os.getenv('WEEK', 'W20')
PERIODO = os.getenv('PERIODO', '11–17 may 2026')
MES_AÑO = os.getenv('MES_AÑO', 'Mayo 2026')
WEEK = os.getenv('WEEK', 'W21')
VOL_NUM = os.getenv('VOL_NUM', None)
if VOL_NUM is None:
    # Si no viene VOL_NUM, extraerlo de WEEK
    try:
        WEEK_NUM = int(WEEK.replace('W', ''))
        VOL_NUM = str(WEEK_NUM)  # Usar WEEK_NUM directamente, no restar 1
    except:
        VOL_NUM = '21'
else:
    VOL_NUM = str(VOL_NUM)
FECHA_PUB = os.getenv('FECHA_PUB', 'LUNES 18 de Mayo de 2026')  # Día de publicación del reporte

# Derivar números de semana
WEEK_NUM = int(WEEK.replace('W', ''))
VOL_NUM_PREV = int(VOL_NUM) - 1

PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
THIRD_PARTY     = ['Expedia','HotelBeds','Hotel Unico','Travelgate']

CANAL_VALIDO = ['B2C', 'B2B (OP)', 'CUG (UOP)']

# ── CARGA ─────────────────────────────────────────────────────────────────────
import datetime as _dt

def _reshape_daily_pivot(path):
    """Formato real recibido desde ~W27: 1 fila por entidad×canasta×métrica,
    con el valor de cada día en su propia columna de fecha (col 'Unnamed: N'
    = nombre de la métrica: 'CheckRates Únicos'/'Successful UniqueChkRts'/
    '#Errors'/'Bookings'/'CheckRates Absolutos'/etc.). 'Semana'/'Fecha' son
    metadata constante/vacía, se ignoran. Se reconstruye a formato largo
    sumando los conteos diarios — Eficacia/ConvRate las recalcula
    load_and_clean() después desde los conteos ya sumados, no desde acá
    (sumar % diarios sería incorrecto, hay que ponderar por volumen)."""
    head = pd.read_excel(path, nrows=1)
    date_cols = [c for c in head.columns if isinstance(c, (_dt.datetime, pd.Timestamp))]
    unnamed_cols = [c for c in head.columns if str(c).startswith('Unnamed')]
    if not (date_cols and unnamed_cols):
        return None

    probe = pd.read_excel(path, usecols=[unnamed_cols[0]], nrows=200)
    metric_vals = set(probe[unnamed_cols[0]].dropna().astype(str))
    count_metrics = {'CheckRates Absolutos', 'CheckRates Únicos',
                      'Successful UniqueChkRts', '#Errors', 'Bookings'}
    if not (metric_vals & count_metrics):
        return None

    df_raw = pd.read_excel(path).rename(columns={unnamed_cols[0]: 'Metric'})
    id_cols = [c for c in ['ExternalProviderName', 'Corporate', 'País destino',
                            'Destino', 'Hotel', 'DistributionCategory'] if c in df_raw.columns]
    for c in date_cols:
        df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

    pieces = {}
    base_index = None
    for metric in count_metrics:
        sub = df_raw[df_raw['Metric'] == metric]
        if not len(sub):
            continue
        s = sub.set_index(id_cols)[date_cols].sum(axis=1)
        pieces[metric] = s
        base_index = s.index if base_index is None else base_index

    if base_index is None:
        return None

    out = pd.DataFrame(index=base_index)
    for metric in count_metrics:
        out[metric] = pieces.get(metric, pd.Series(0, index=base_index)).reindex(base_index).fillna(0)
    out = out.reset_index()
    # Limpiar fila de placeholder (todo cero + Corporate/Hotel='-')
    _corp_col = 'Corporate' if 'Corporate' in out.columns else None
    if _corp_col:
        out = out[~((out['CheckRates Únicos'] == 0) & (out['Bookings'] == 0) &
                    (out[_corp_col].astype(str).str.strip() == '-'))].copy()
    print(f'  (pivot diario→largo CR): {len(out):,} filas')
    return out


def load_and_clean(path):
    df = _reshape_daily_pivot(path)
    if df is None:
        df = pd.read_excel(path)
    df.rename(columns={'Corporate':'CorpName', 'CheckRates Únicos':'CR_Unicos'}, inplace=True)
    df = df[df['DistributionCategory'].isin(CANAL_VALIDO)].copy()
    # Limpieza de destinos: quitar sufijo " Area" y eliminar "SinClasificar"
    if 'Destino' in df.columns:
        df['Destino'] = df['Destino'].astype(str).str.strip().str.replace(r'\s+Area\b', '', regex=True).str.strip()
        df = df[df['Destino'].str.lower().str.replace(' ', '') != 'sinclasificar'].copy()
    # Compatibilidad W22+: dataset puede no tener 'Successful UniqueChkRts'
    # En ese caso, derivar de 'Efectividad en CheckRates' * CR_Unicos
    if 'Successful UniqueChkRts' not in df.columns:
        if 'Efectividad en CheckRates' in df.columns:
            ef_col = pd.to_numeric(df['Efectividad en CheckRates'], errors='coerce').fillna(0).clip(0, 1)
            df['Successful UniqueChkRts'] = (ef_col * df['CR_Unicos']).round().astype(int)
        else:
            df['Successful UniqueChkRts'] = 0
    df['Eficacia']  = pd.to_numeric(df['Successful UniqueChkRts'], errors='coerce').fillna(0) / df['CR_Unicos'].replace(0, np.nan)
    df['Eficacia']  = df['Eficacia'].fillna(0).clip(0, 1)
    # ConvRate: puede venir como columna o calcular desde Bookings / CR_Unicos
    df['ConvRate']  = pd.to_numeric(df['Bookings'], errors='coerce').fillna(0) / df['CR_Unicos'].replace(0, np.nan)
    df['ConvRate']  = df['ConvRate'].fillna(0).clip(0)
    return df

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def _find(name):
    for d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
        p = os.path.join(d, name)
        if os.path.exists(p): return p
    raise FileNotFoundError(f'{name} no encontrado')
df18 = load_and_clean(_find(f'Dataset_CheckRates_W{WEEK_NUM}.xlsx'))  # semana actual
df17 = load_and_clean(_find(f'Dataset_CheckRates_W{VOL_NUM_PREV}.xlsx'))  # semana anterior para WoW

# ── Agregados W17 para merge WoW en tabs del hero ─────────────────────────
def _agg_dim_w17(df, col):
    g = df.groupby(col, as_index=False).agg(
        CR_Unicos_W17=('CR_Unicos','sum'),
        Bookings_W17=('Bookings','sum'),
        Successful_W17=('Successful UniqueChkRts','sum')
    )
    g['Eficacia_W17']  = g['Successful_W17']/g['CR_Unicos_W17']
    g['ConvRate_W17']  = g['Bookings_W17']/g['CR_Unicos_W17']
    return g

g_dest_w17    = _agg_dim_w17(df17, 'Destino')
g_corp_w17    = _agg_dim_w17(df17, 'CorpName')
g_hotel_w17   = _agg_dim_w17(df17, 'Hotel')
g_channel_w17 = _agg_dim_w17(df17, 'ExternalProviderName')

# ── FILTRO DE RELEVANCIA OPERACIONAL: MIN_CR = 100 ───────────────────────────
# Hoteles con >= 100 CR/semana = universo operacionalmente relevante
MIN_CR = 100

def calc_p80(df):
    """Hoteles que acumulan 90% del volumen CR (antes era 80%)."""
    g = df.groupby('Hotel').agg(CR_Unicos=('CR_Unicos','sum')).reset_index()
    g = g.sort_values('CR_Unicos', ascending=False)
    g['cum'] = g['CR_Unicos'].cumsum() / g['CR_Unicos'].sum()
    return g[g['cum'].shift(1, fill_value=0) < 0.90]['Hotel'].tolist()

# Aplicar filtro MIN_CR primero
df18 = df18[df18['CR_Unicos'] >= MIN_CR].copy()
df17 = df17[df17['CR_Unicos'] >= MIN_CR].copy() if len(df17) > 0 else df17

# Normalizar nombre de canales para display
_CHANNEL_RENAME = {'HotelBeds Apitude': 'HotelBeds', 'Hotel Unico V2': 'Hotel Unico'}
df18['ExternalProviderName'] = df18['ExternalProviderName'].replace(_CHANNEL_RENAME)
if len(df17) > 0:
    df17['ExternalProviderName'] = df17['ExternalProviderName'].replace(_CHANNEL_RENAME)


p80_hotels = calc_p80(df18)

# ── AGREGADOS POR HOTEL (P80) ─────────────────────────────────────────────────
def agg_hotel(df, hotels=None):
    sub = df[df['Hotel'].isin(hotels)] if hotels else df
    g = sub.groupby(['Hotel','CorpName','Destino'], as_index=False).agg(
        CR_Unicos=('CR_Unicos','sum'),
        Bookings=('Bookings','sum'),
        Successful=('Successful UniqueChkRts','sum'),
    )
    g['Eficacia']  = g['Successful'] / g['CR_Unicos']
    g['ConvRate']  = g['Bookings']   / g['CR_Unicos']
    g['BandaEficacia'] = g.apply(lambda r: banda_eficacia_tiered(r['Eficacia'], r['Destino']), axis=1)
    g['BandaConvRate'] = g.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
    return g

g_hotel_all = agg_hotel(df18)
p80_hotel   = agg_hotel(df18, p80_hotels)

# ── AGREGADOS POR DIMENSIÓN ────────────────────────────────────────────────────
def agg_dim(df, col):
    g = df.groupby(col, as_index=False).agg(
        CR_Unicos=('CR_Unicos','sum'),
        Bookings=('Bookings','sum'),
        Successful=('Successful UniqueChkRts','sum'),
    )
    g['Eficacia']  = g['Successful'] / g['CR_Unicos']
    g['ConvRate']  = g['Bookings']   / g['CR_Unicos']
    g['BandaEficacia'] = (
        g.apply(lambda r: banda_eficacia_tiered(r['Eficacia'], r[col]), axis=1)
        if col == 'Destino'
        else g.apply(lambda r: banda_eficacia(r['Eficacia']), axis=1)
    )
    g['BandaConvRate'] = g.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
    return g

# Dimensiones globales sobre P80 (metodología consistente con RND)
df18_p80 = df18[df18['Hotel'].isin(p80_hotels)].copy()
df17_p80 = df17[df17['Hotel'].isin(p80_hotels)].copy()
g_corp    = agg_dim(df18_p80, 'CorpName').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
g_destino = agg_dim(df18_p80, 'Destino').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
g_channel = agg_dim(df18_p80, 'ExternalProviderName').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

# Grupo Producto Propio / Third Party
df18['Grupo'] = df18['ExternalProviderName'].apply(
    lambda x: 'Producto Propio' if x in PRODUCTO_PROPIO else ('Third Party' if x in THIRD_PARTY else 'Otro')
)
df18_p80['Grupo'] = df18_p80['ExternalProviderName'].apply(lambda x: 'Producto Propio' if x in PRODUCTO_PROPIO else ('Third Party' if x in THIRD_PARTY else 'Otro'))
g_grupo = df18_p80[df18_p80['Grupo'].isin(['Producto Propio','Third Party'])].groupby('Grupo', as_index=False).agg(
    CR_Unicos=('CR_Unicos','sum'),
    Bookings=('Bookings','sum'),
    Successful=('Successful UniqueChkRts','sum'),
)
g_grupo['Eficacia']  = g_grupo['Successful'] / g_grupo['CR_Unicos']
g_grupo['ConvRate']  = g_grupo['Bookings']   / g_grupo['CR_Unicos']
g_grupo['BandaEficacia'] = g_grupo['Eficacia'].apply(banda_eficacia)
g_grupo['BandaConvRate'] = g_grupo.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)

# ── MÉTRICAS GLOBALES ─────────────────────────────────────────────────────────
def global_metrics(df):
    cr   = df['CR_Unicos'].sum()
    bkgs = df['Bookings'].sum()
    succ = df['Successful UniqueChkRts'].sum()
    return {
        'cr_unicos': int(cr),
        'bookings':  int(bkgs),
        'eficacia':  succ/cr if cr else 0,
        'conv_rate': bkgs/cr if cr else 0,
        'n_hoteles': df['Hotel'].nunique(),
    }

def canasta_metrics(df, cat):
    sub = df[df['DistributionCategory']==cat]
    return global_metrics(sub)

M = {
    f'global_w{WEEK_NUM}': global_metrics(df18_p80),
    f'global_w{VOL_NUM_PREV}': global_metrics(df17_p80),
    f'B2C_w{WEEK_NUM}':    canasta_metrics(df18_p80, 'B2C'),
    f'B2B (OP)_w{WEEK_NUM}': canasta_metrics(df18_p80, 'B2B (OP)'),
    f'CUG (UOP)_w{WEEK_NUM}': canasta_metrics(df18_p80, 'CUG (UOP)'),
    f'B2C_w{VOL_NUM_PREV}':    canasta_metrics(df17_p80, 'B2C'),
    f'B2B (OP)_w{VOL_NUM_PREV}': canasta_metrics(df17_p80, 'B2B (OP)'),
    f'CUG (UOP)_w{VOL_NUM_PREV}': canasta_metrics(df17_p80, 'CUG (UOP)'),
}

# ── SEVERITY (P80) ─────────────────────────────────────────────────────────────
sev_ef_p80 = p80_hotel['BandaEficacia'].value_counts()
sev_cv_p80 = p80_hotel['BandaConvRate'].value_counts()

# ── TOP TABLES ────────────────────────────────────────────────────────────────
# Críticos: peor Eficacia · P80 · solo BKGS>0 (los BKGS=0 están en tab "Sin Conversión")
df_crit_pool = p80_hotel[p80_hotel['Bookings']>0].copy()
# Priorizar por Eficacia ascendente, luego por volumen CR
df_crit_pool = df_crit_pool.sort_values(['Eficacia', 'CR_Unicos'], ascending=[True, False]).reset_index(drop=True)
# Bajo rendimiento: ConvRate Crítica/Revisar · BKGS>0 · alto CR
df_br_pool = p80_hotel[(p80_hotel['Bookings']>0) & 
                        (p80_hotel['BandaConvRate'].isin(['Crítica','Revisar']))].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
# Sin conversión: BKGS=0 · alto CR
df_sc_pool = p80_hotel[p80_hotel['Bookings']==0].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
# Menor ConvRate: BKGS>0 · menor CR
df_mcv_pool = p80_hotel[p80_hotel['Bookings']>0].sort_values('ConvRate').reset_index(drop=True)

TOP = {
    'criticos':       df_crit_pool.head(100).reset_index(drop=True),
    'criticos_extra': df_crit_pool.iloc[10:].reset_index(drop=True),
    'bajo_rend':      df_br_pool.head(100).reset_index(drop=True),
    'bajo_rend_extra':df_br_pool.iloc[10:].reset_index(drop=True),
    'sin_conv':       df_sc_pool.head(100).reset_index(drop=True),
    'sin_conv_extra': df_sc_pool.iloc[10:].reset_index(drop=True),
    'menor_cv':       df_mcv_pool.head(100).reset_index(drop=True),
    'corps_10':       g_corp.head(100).reset_index(drop=True),
    'destinos':       g_destino.head(100).reset_index(drop=True),
    'channels':       g_channel.sort_values('CR_Unicos', ascending=False).reset_index(drop=True),
}

# ── TABS HERO (Eficacia + ConvRate) ────────────────────────────────────────────

def _add_wow_channel(g_ch, metric_col):
    """Merge WoW W17 a g_channel por ExternalProviderName."""
    ref_col = metric_col + '_W17'
    merged = g_ch.merge(
        g_channel_w17[['ExternalProviderName', ref_col]],
        on='ExternalProviderName', how='left'
    )
    merged[metric_col + '_WoW_pp'] = (merged[metric_col] - merged[ref_col]) * 100
    return merged.sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

def tab_eficacia():
    """Aggregados para tabs del KPI Eficacia — Destino/Corp sobre P80."""
    g_d = df18_p80.groupby('Destino', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_d['Eficacia'] = g_d['Successful']/g_d['CR_Unicos']
    g_c = df18_p80.groupby('CorpName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_c['Eficacia'] = g_c['Successful']/g_c['CR_Unicos']
    g_c.rename(columns={'CorpName':'CorpName'}, inplace=True)
    # Hotel — usar todos los hoteles (g_hotel_all) para no excluir hoteles con volumen bajo
    g_h = g_hotel_all[g_hotel_all['Bookings'] > 0].copy()  # excluir Sin Conversión del card Conv Rate
    # Channel — sobre dataset completo (channel no se filtra por hotel)
    g_ch = df18.groupby('ExternalProviderName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_ch['Eficacia'] = g_ch['Successful']/g_ch['CR_Unicos']
    # Canasta
    g_can = df18_p80.groupby('DistributionCategory', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_can['Eficacia'] = g_can['Successful']/g_can['CR_Unicos']
    g_can.rename(columns={'DistributionCategory':'Canasta'}, inplace=True)
    # Asegurar ambas métricas
    for g in [g_d,g_c,g_ch,g_can]:
        if 'ConvRate' not in g.columns: g['ConvRate']=g['Bookings']/g['CR_Unicos']
    # Sin filtro P50 para corp: mismo universo que pestaña "Por Corporativo" del Excel
    p50_d = g_d['CR_Unicos'].quantile(0.50)
    p50_h = g_h['CR_Unicos'].quantile(0.50)
    df_d = g_d[g_d['CR_Unicos']>=p50_d].sort_values('Eficacia').head(500).reset_index(drop=True)
    df_c = g_c.sort_values('Eficacia').head(100).reset_index(drop=True)
    # P15: pool COMPLETO de hoteles (todas las bandas, sin cap) para que cross-filter
    # y searchbox de CR KPI alcancen cualquier corp/hotel. Filas 11+ van como sb-hidden.
    # Los pills de banda filtran en JS por data-banda; el orden band-grouped se preserva.
    _df_crit = g_h[g_h['BandaEficacia'].isin(['Crítica','Súper Crítica'])].sort_values('Eficacia', ascending=True)
    _df_br   = g_h[g_h['BandaEficacia'].isin(['Revisar','Aceptable'])].sort_values('Eficacia', ascending=True)
    _df_exit = g_h[g_h['BandaEficacia']=='Exitosa'].sort_values('CR_Unicos', ascending=False)
    _df_sc   = g_hotel_all[g_hotel_all['Bookings']==0].sort_values('CR_Unicos', ascending=False)
    df_h = pd.concat([_df_crit, _df_br, _df_exit, _df_sc], ignore_index=True).drop_duplicates('Hotel').reset_index(drop=True)
    # Merge WoW — Eficacia + ConvRate + CR_Unicos (tráfico)
    df_d = df_d.merge(g_dest_w17[['Destino','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='Destino', how='left')
    df_d['Eficacia_WoW_pp']  = (df_d['Eficacia']  - df_d['Eficacia_W17'])  * 100
    df_d['ConvRate_WoW_pp']  = (df_d['ConvRate']  - df_d['ConvRate_W17'])  * 100
    df_d['CR_Unicos_WoW_pp'] = (df_d['CR_Unicos'] - df_d['CR_Unicos_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='CorpName', how='left')
    df_c['Eficacia_WoW_pp']  = (df_c['Eficacia']  - df_c['Eficacia_W17'])  * 100
    df_c['ConvRate_WoW_pp']  = (df_c['ConvRate']  - df_c['ConvRate_W17'])  * 100
    df_c['CR_Unicos_WoW_pp'] = (df_c['CR_Unicos'] - df_c['CR_Unicos_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='Hotel', how='left')
    df_h['Eficacia_WoW_pp']  = (df_h['Eficacia']  - df_h['Eficacia_W17'])  * 100
    df_h['ConvRate_WoW_pp']  = (df_h['ConvRate']  - df_h['ConvRate_W17'])  * 100
    df_h['CR_Unicos_WoW_pp'] = (df_h['CR_Unicos'] - df_h['CR_Unicos_W17']) * 100
    return {
        'destino': df_d,
        'corp':    df_c,
        'hotel':   df_h,
        'channel': _add_wow_channel(g_ch, 'Eficacia'),
        'canasta': g_can.sort_values('Eficacia').reset_index(drop=True),
    }

def tab_convrate():
    """Aggregados para tabs del KPI ConvRate — Destino/Corp sobre P80."""
    g_d = df18_p80.groupby('Destino', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_d['ConvRate'] = g_d['Bookings']/g_d['CR_Unicos']
    g_d['Eficacia'] = g_d['Successful']/g_d['CR_Unicos']
    g_c = df18_p80.groupby('CorpName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_c['ConvRate'] = g_c['Bookings']/g_c['CR_Unicos']
    g_c['Eficacia'] = g_c['Successful']/g_c['CR_Unicos']
    g_h = g_hotel_all[g_hotel_all['Bookings'] > 0].copy()  # excluir Sin Conversión del card Conv Rate
    g_ch = df18.groupby('ExternalProviderName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_ch['ConvRate'] = g_ch['Bookings']/g_ch['CR_Unicos']
    g_ch['Eficacia'] = g_ch['Successful']/g_ch['CR_Unicos']
    g_can = df18_p80.groupby('DistributionCategory', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_can['ConvRate'] = g_can['Bookings']/g_can['CR_Unicos']
    g_can['Eficacia'] = g_can['Successful']/g_can['CR_Unicos']
    g_can.rename(columns={'DistributionCategory':'Canasta'}, inplace=True)
    # Sin filtro P50 para corp: mismo universo que Excel
    p50_d = g_d['CR_Unicos'].quantile(0.50)
    p50_h = g_h['CR_Unicos'].quantile(0.50)
    df_d = g_d[(g_d['CR_Unicos']>=p50_d) & (g_d['Bookings']>0)].sort_values('ConvRate').head(500).reset_index(drop=True)
    df_c = g_c.sort_values('ConvRate').head(100).reset_index(drop=True)
    # P15: pool COMPLETO de hoteles (todas las bandas, sin cap) — cobertura total de corps.
    _df_crit_cv = g_h[g_h['BandaConvRate'].isin(['Crítica','Súper Crítica'])].sort_values('ConvRate', ascending=True)
    _df_br_cv   = g_h[g_h['BandaConvRate'].isin(['Revisar','Aceptable'])].sort_values('ConvRate', ascending=True)
    _df_exit_cv = g_h[g_h['BandaConvRate']=='Exitosa'].sort_values('CR_Unicos', ascending=False)
    _df_sc_cv   = g_hotel_all[g_hotel_all['Bookings']==0].sort_values('CR_Unicos', ascending=False)
    df_h = pd.concat([_df_crit_cv, _df_br_cv, _df_exit_cv, _df_sc_cv], ignore_index=True).drop_duplicates('Hotel').reset_index(drop=True)
    # Merge WoW — ConvRate + CR_Unicos (tráfico)
    df_d = df_d.merge(g_dest_w17[['Destino','ConvRate_W17','CR_Unicos_W17']], on='Destino', how='left')
    df_d['ConvRate_WoW_pp'] = (df_d['ConvRate'] - df_d['ConvRate_W17']) * 100
    df_d['CR_Unicos_WoW_pp'] = (df_d['CR_Unicos'] - df_d['CR_Unicos_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','ConvRate_W17','CR_Unicos_W17']], on='CorpName', how='left')
    df_c['ConvRate_WoW_pp'] = (df_c['ConvRate'] - df_c['ConvRate_W17']) * 100
    df_c['CR_Unicos_WoW_pp'] = (df_c['CR_Unicos'] - df_c['CR_Unicos_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','ConvRate_W17','CR_Unicos_W17']], on='Hotel', how='left')
    df_h['ConvRate_WoW_pp'] = (df_h['ConvRate'] - df_h['ConvRate_W17']) * 100
    df_h['CR_Unicos_WoW_pp'] = (df_h['CR_Unicos'] - df_h['CR_Unicos_W17']) * 100
    return {
        'destino': df_d,
        'corp':    df_c,
        'hotel':   df_h,
        'channel': _add_wow_channel(g_ch, 'ConvRate'),
        'canasta': g_can.sort_values('ConvRate').reset_index(drop=True),
    }

TAB_EF = tab_eficacia()
TAB_CV = tab_convrate()

# ── TABS POR CANASTA (para cards KPI reactivas) ────────────────────────────────
DIST_MAP = {'b2c': 'B2C', 'op': 'B2B (OP)', 'cug': 'CUG (UOP)'}

def tab_eficacia_for(dist_cat):
    """Igual que tab_eficacia() pero filtrando por DistributionCategory."""
    sub = df18_p80[df18_p80['DistributionCategory'] == dist_cat].copy()
    if len(sub) == 0:
        return {k: pd.DataFrame() for k in ['destino','corp','hotel','channel','canasta']}
    g_d = sub.groupby('Destino', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_d['Eficacia'] = g_d['Successful'] / g_d['CR_Unicos']
    g_c = sub.groupby('CorpName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_c['Eficacia'] = g_c['Successful'] / g_c['CR_Unicos']
    g_h = sub.groupby('Hotel', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_h['Eficacia'] = g_h['Successful'] / g_h['CR_Unicos']
    sub_full = df18[df18['DistributionCategory'] == dist_cat]
    g_ch = sub_full.groupby('ExternalProviderName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_ch['Eficacia'] = g_ch['Successful'] / g_ch['CR_Unicos']
    for g in [g_d, g_c, g_h, g_ch]:
        if 'ConvRate' not in g.columns: g['ConvRate'] = g['Bookings'] / g['CR_Unicos']
    p50_d = g_d['CR_Unicos'].quantile(0.50) if len(g_d) else 0
    p50_h = g_h['CR_Unicos'].quantile(0.50) if len(g_h) else 0
    df_d = g_d[g_d['CR_Unicos'] >= p50_d].sort_values('Eficacia').head(500).reset_index(drop=True)
    df_c = g_c.sort_values('Eficacia').head(100).reset_index(drop=True)
    df_h = g_h[g_h['CR_Unicos'] >= p50_h].sort_values('Eficacia').head(100).reset_index(drop=True)
    df_d = df_d.merge(g_dest_w17[['Destino','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='Destino', how='left')
    df_d['Eficacia_WoW_pp']  = (df_d['Eficacia']  - df_d['Eficacia_W17'])  * 100
    df_d['ConvRate_WoW_pp']  = (df_d['ConvRate']  - df_d['ConvRate_W17'])  * 100
    df_d['CR_Unicos_WoW_pp'] = (df_d['CR_Unicos'] - df_d['CR_Unicos_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='CorpName', how='left')
    df_c['Eficacia_WoW_pp']  = (df_c['Eficacia']  - df_c['Eficacia_W17'])  * 100
    df_c['ConvRate_WoW_pp']  = (df_c['ConvRate']  - df_c['ConvRate_W17'])  * 100
    df_c['CR_Unicos_WoW_pp'] = (df_c['CR_Unicos'] - df_c['CR_Unicos_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','Eficacia_W17','ConvRate_W17','CR_Unicos_W17']], on='Hotel', how='left')
    df_h['Eficacia_WoW_pp']  = (df_h['Eficacia']  - df_h['Eficacia_W17'])  * 100
    df_h['ConvRate_WoW_pp']  = (df_h['ConvRate']  - df_h['ConvRate_W17'])  * 100
    df_h['CR_Unicos_WoW_pp'] = (df_h['CR_Unicos'] - df_h['CR_Unicos_W17']) * 100
    return {'destino': df_d, 'corp': df_c, 'hotel': df_h,
            'channel': _add_wow_channel(g_ch, 'Eficacia'), 'canasta': pd.DataFrame()}

def tab_convrate_for(dist_cat):
    """Igual que tab_convrate() pero filtrando por DistributionCategory."""
    sub = df18_p80[df18_p80['DistributionCategory'] == dist_cat].copy()
    if len(sub) == 0:
        return {k: pd.DataFrame() for k in ['destino','corp','hotel','channel','canasta']}
    g_d = sub.groupby('Destino', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_d['ConvRate'] = g_d['Bookings'] / g_d['CR_Unicos']
    g_d['Eficacia'] = g_d['Successful'] / g_d['CR_Unicos']
    g_c = sub.groupby('CorpName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_c['ConvRate'] = g_c['Bookings'] / g_c['CR_Unicos']
    g_c['Eficacia'] = g_c['Successful'] / g_c['CR_Unicos']
    g_h = sub.groupby('Hotel', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_h['ConvRate'] = g_h['Bookings'] / g_h['CR_Unicos']
    g_h['Eficacia'] = g_h['Successful'] / g_h['CR_Unicos']
    sub_full = df18[df18['DistributionCategory'] == dist_cat]
    g_ch = sub_full.groupby('ExternalProviderName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_ch['ConvRate'] = g_ch['Bookings'] / g_ch['CR_Unicos']
    g_ch['Eficacia'] = g_ch['Successful'] / g_ch['CR_Unicos']
    p50_d = g_d['CR_Unicos'].quantile(0.50) if len(g_d) else 0
    p50_h = g_h['CR_Unicos'].quantile(0.50) if len(g_h) else 0
    df_d = g_d[(g_d['CR_Unicos'] >= p50_d) & (g_d['Bookings'] > 0)].sort_values('ConvRate').head(100).reset_index(drop=True)
    df_c = g_c.sort_values('ConvRate').head(100).reset_index(drop=True)
    df_h = g_h[g_h['CR_Unicos'] >= p50_h].sort_values('ConvRate').head(100).reset_index(drop=True)
    df_d = df_d.merge(g_dest_w17[['Destino','ConvRate_W17','CR_Unicos_W17']], on='Destino', how='left')
    df_d['ConvRate_WoW_pp'] = (df_d['ConvRate'] - df_d['ConvRate_W17']) * 100
    df_d['CR_Unicos_WoW_pp'] = (df_d['CR_Unicos'] - df_d['CR_Unicos_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','ConvRate_W17','CR_Unicos_W17']], on='CorpName', how='left')
    df_c['ConvRate_WoW_pp'] = (df_c['ConvRate'] - df_c['ConvRate_W17']) * 100
    df_c['CR_Unicos_WoW_pp'] = (df_c['CR_Unicos'] - df_c['CR_Unicos_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','ConvRate_W17','CR_Unicos_W17']], on='Hotel', how='left')
    df_h['ConvRate_WoW_pp'] = (df_h['ConvRate'] - df_h['ConvRate_W17']) * 100
    df_h['CR_Unicos_WoW_pp'] = (df_h['CR_Unicos'] - df_h['CR_Unicos_W17']) * 100
    return {'destino': df_d, 'corp': df_c, 'hotel': df_h,
            'channel': _add_wow_channel(g_ch, 'ConvRate'), 'canasta': pd.DataFrame()}

# Calcular para las 3 sub-canastas + global (ya en TAB_EF/TAB_CV)
TAB_EF_BY_CANASTA = {'global': TAB_EF}
TAB_CV_BY_CANASTA = {'global': TAB_CV}
for _key, _dist in DIST_MAP.items():
    TAB_EF_BY_CANASTA[_key] = tab_eficacia_for(_dist)
    TAB_CV_BY_CANASTA[_key] = tab_convrate_for(_dist)

# ── Enriquecer TOP[] con WoW desde TAB_EF/TAB_CV (evita NaN por orden de construcción) ──
_wow_ef = TAB_EF['hotel'][['Hotel','Eficacia_WoW_pp']].drop_duplicates('Hotel')
_wow_cv = TAB_CV['hotel'][['Hotel','ConvRate_WoW_pp']].drop_duplicates('Hotel')
_wow_hotel_lkp = _wow_ef.merge(_wow_cv, on='Hotel', how='outer')
for _k in ['criticos','criticos_extra','bajo_rend','bajo_rend_extra','sin_conv','sin_conv_extra','menor_cv']:
    if _k in TOP:
        _df = TOP[_k]
        if 'Hotel' in _df.columns:
            _drop = [c for c in ['Eficacia_WoW_pp','ConvRate_WoW_pp'] if c in _df.columns]
            _df = _df.drop(columns=_drop).merge(_wow_hotel_lkp, on='Hotel', how='left')
            TOP[_k] = _df

# ── CANASTAS ─────────────────────────────────────────────────────────────────
def canasta_data(cat, short, df18=df18, df17=df17):
    sub18 = df18[df18['DistributionCategory']==cat].copy()
    sub17 = df17[df17['DistributionCategory']==cat].copy()
    
    # P80 canasta
    g_h = sub18.groupby('Hotel').agg(CR_Unicos=('CR_Unicos','sum')).reset_index()
    g_h = g_h.sort_values('CR_Unicos', ascending=False)
    g_h['cum'] = g_h['CR_Unicos'].cumsum()/g_h['CR_Unicos'].sum()
    p80_list = g_h[g_h['cum'].shift(1, fill_value=0) < 0.80]['Hotel'].tolist()
    
    p80_can = agg_hotel(sub18, p80_list)

    sev_ef = p80_can['BandaEficacia'].value_counts()
    sev_cv = p80_can['BandaConvRate'].value_counts()

    # Tops sobre P80
    df_crit = p80_can[(p80_can['Bookings']>0) & (p80_can['Eficacia']>0)].sort_values('Eficacia').reset_index(drop=True)
    df_br   = p80_can[(p80_can['Bookings']>0) & (p80_can['BandaConvRate'].isin(['Crítica','Revisar']))].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_sc   = p80_can[p80_can['Bookings']==0].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_mcv  = p80_can[p80_can['Bookings']>0].sort_values('ConvRate').reset_index(drop=True)

    # Dimensiones sobre P80 de la canasta
    p80_set = set(p80_list)
    sub18_p80 = sub18[sub18['Hotel'].isin(p80_set)].copy()
    sub17_p80 = sub17[sub17['Hotel'].isin(p80_set)].copy()

    g_corp_can = agg_dim(sub18_p80, 'CorpName').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    g_dest_can = agg_dim(sub18_p80, 'Destino').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    g_chan_can = agg_dim(sub18_p80, 'ExternalProviderName').sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

    # Métricas de canasta sobre P80
    cr18 = sub18_p80['CR_Unicos'].sum(); bk18 = sub18_p80['Bookings'].sum(); su18 = sub18_p80['Successful UniqueChkRts'].sum()
    cr17 = sub17_p80['CR_Unicos'].sum(); bk17 = sub17_p80['Bookings'].sum(); su17 = sub17_p80['Successful UniqueChkRts'].sum()

    ef_val = su18/cr18 if cr18 else 0
    cv_val = bk18/cr18 if cr18 else 0
    m18 = {'cr_unicos':int(cr18),'bookings':int(bk18),'eficacia':ef_val,'conv_rate':cv_val,
            'banda_eficacia':banda_eficacia(ef_val),
            'banda_convrate':banda_convrate(cv_val, int(bk18))}
    m17 = {'cr_unicos':int(cr17),'bookings':int(bk17),'eficacia':su17/cr17 if cr17 else 0,'conv_rate':bk17/cr17 if cr17 else 0}

    n_critica = int((p80_can['BandaEficacia'].isin(['Crítica','Súper Crítica'])).sum())
    cat_labels = {'B2C':'B2C','B2B (OP)':'B2B Opaco','CUG (UOP)':'CUG'}
    return {
        'cat': cat, 'short': short, 'name': cat_labels.get(cat, cat),
        'n_critica': n_critica,
        'agg_hotel': p80_can,
        'm18': m18, 'm17': m17,
        'p80': p80_can,
        'sev_ef': sev_ef, 'sev_cv': sev_cv,
        'top_crit': df_crit.head(100).reset_index(drop=True),
        'top_crit_extra': df_crit.iloc[10:].reset_index(drop=True),
        'top_br':   df_br.head(100).reset_index(drop=True),
        'top_br_extra':  df_br.iloc[10:].reset_index(drop=True),
        'top_sc':   df_sc.head(100).reset_index(drop=True),
        'top_sc_extra':  df_sc.iloc[10:].reset_index(drop=True),
        'top_mcv':  df_mcv.head(100).reset_index(drop=True),
        'g_corp':   g_corp_can.head(100),
        'g_dest':   g_dest_can.head(100),
        'g_chan':   g_chan_can,
        'agg_destino': g_dest_can,
        'agg_corp': g_corp_can,
        'agg_channel': g_chan_can,
        'bajo':     df_br.head(10).reset_index(drop=True),
        'sin_conv': df_sc.head(10).reset_index(drop=True),
        'critic':   df_crit.head(10).reset_index(drop=True),
        'menor_cv': df_mcv.head(10).reset_index(drop=True),
        'top_dest': g_dest_can.head(10),
        'top_corp': g_corp_can.head(10),
        'top_hot':  p80_can.sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True),
        'top_chan':  g_chan_can,
    }

CANASTA = {
    'B2C':    canasta_data('B2C',    'B2C'),
    'B2B-OP': canasta_data('B2B (OP)', 'OP'),
    'CUG':    canasta_data('CUG (UOP)', 'CUG'),
}

# ── SEVERITY P80 POR CANASTA (para tabs hero) ─────────────────────────────────
sev_ef_p80_b2c  = CANASTA['B2C']['sev_ef']
sev_cv_p80_b2c  = CANASTA['B2C']['sev_cv']

# ── ENRIQUECER p80_hotel CON COLUMNAS WoW ────────────────────────────────────
# Agregar WoW de Eficacia y tráfico (CR_Unicos) a p80_hotel para render_cr_p2
p80_hotel = p80_hotel.merge(
    g_hotel_w17[['Hotel', 'Eficacia_W17', 'ConvRate_W17', 'CR_Unicos_W17']], 
    on='Hotel', 
    how='left'
)
p80_hotel['Eficacia_WoW_pp']   = (p80_hotel['Eficacia']   - p80_hotel.get('Eficacia_W17',   0)) * 100
p80_hotel['ConvRate_WoW_pp']   = (p80_hotel['ConvRate']   - p80_hotel.get('ConvRate_W17',   0)) * 100
p80_hotel['CR_Unicos_WoW_pp']  = (p80_hotel['CR_Unicos']  - p80_hotel.get('CR_Unicos_W17',  0)) * 100

# ── GUARDAR PICKLE ────────────────────────────────────────────────────────────
D = {
    'WEEK': WEEK,
    'VOL_NUM': VOL_NUM,
    'PERIODO': PERIODO,
    'MES_AÑO': MES_AÑO,
    'FECHA_PUB': FECHA_PUB,
    'M': M,
    'TOP': TOP,
    'TAB_EF': TAB_EF,
    'TAB_CV': TAB_CV,
    'TAB_EF_BY_CANASTA': TAB_EF_BY_CANASTA,
    'TAB_CV_BY_CANASTA': TAB_CV_BY_CANASTA,
    'CANASTA': CANASTA,
    'sev_ef': sev_ef_p80,
    'sev_cv': sev_cv_p80,
    'sev_ef_p80': sev_ef_p80,
    'sev_cv_p80': sev_cv_p80,
    'g_hotel': g_hotel_all,
    'p80_hotel': p80_hotel,
    'g_corp': g_corp,
    'g_channel': g_channel,
    'g_grupo': g_grupo,
    'df18': df18,
    'df17': df17,
    'p80_hotels': p80_hotels,
    'g_corp_w17': g_corp_w17,
    'g_dest_w17': g_dest_w17,
    'g_channel_w17': g_channel_w17,
    'hotel_channel_map': (
        df18.groupby(['Hotel','ExternalProviderName'])['CR_Unicos'].sum()
            .reset_index().sort_values('CR_Unicos', ascending=False)
            .drop_duplicates('Hotel').set_index('Hotel')['ExternalProviderName'].to_dict()
    ),
    'g_hotel_w17': g_hotel_w17,
}

# ── Enriquecer CANASTA[] con WoW desde TAB_EF/TAB_CV ──────────────────────
_wow_ef_c = TAB_EF['hotel'][['Hotel','Eficacia_WoW_pp']].drop_duplicates('Hotel')
_wow_cv_c = TAB_CV['hotel'][['Hotel','ConvRate_WoW_pp']].drop_duplicates('Hotel')
_wow_lkp_c = _wow_ef_c.merge(_wow_cv_c, on='Hotel', how='outer')
for _ck, _cd in CANASTA.items():
    if not isinstance(_cd, dict): continue
    for _sk, _df in _cd.items():
        if not isinstance(_df, pd.DataFrame) or 'Hotel' not in _df.columns: continue
        _nn = sum(_df[_wc].notna().sum() for _wc in ['Eficacia_WoW_pp','ConvRate_WoW_pp'] if _wc in _df.columns)
        if _nn > 0: continue
        _drop = [_c for _c in ['Eficacia_WoW_pp','ConvRate_WoW_pp'] if _c in _df.columns]
        _df2 = _df.drop(columns=_drop).merge(_wow_lkp_c, on='Hotel', how='left')
        _cd[_sk] = _df2

# ── Histórico real por corp/dest (W18 … VOL_NUM-1) ───────────────────────────
try:
    from build_hist_entity import build_cr_hist
    _base = os.path.dirname(os.path.abspath(__file__))
    D['CR_HIST'] = build_cr_hist(range(18, int(VOL_NUM)), base_dir=_base)
    print(f"   CR_HIST corps: {len(D['CR_HIST']['corp'])}  dests: {len(D['CR_HIST']['dest'])}")
except Exception as _e:
    print(f"   [warn] CR_HIST no generado: {_e}")
    D['CR_HIST'] = {'corp': {}, 'dest': {}}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'cr_w{VOL_NUM}_data.pkl'),'wb') as f:
    pickle.dump(D, f)

print(f"✅ Pickle guardado: cr_w{VOL_NUM}_data.pkl")
print(f"   Eficacia global W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['eficacia']:.4f} ({M[f'global_w{WEEK_NUM}']['eficacia']*100:.2f}%)")
print(f"   ConvRate global W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['conv_rate']:.4f} ({M[f'global_w{WEEK_NUM}']['conv_rate']*100:.2f}%)")
print(f"   CR únicos W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['cr_unicos']:,}")
print(f"   Bookings W{WEEK_NUM}:  {M[f'global_w{WEEK_NUM}']['bookings']:,}")
print(f"   Hoteles P80:   {len(p80_hotel)}")
print(f"   Severity Ef P80: {dict(sev_ef_p80)}")
print(f"   Severity CV P80: {dict(sev_cv_p80)}")
print(f"   Canastas: B2C={M[f'B2C_w{WEEK_NUM}']['cr_unicos']:,} | OP={M[f'B2B (OP)_w{WEEK_NUM}']['cr_unicos']:,} | CUG={M[f'CUG (UOP)_w{WEEK_NUM}']['cr_unicos']:,}")
