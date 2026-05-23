"""
calc_cr.py · Cálculo métricas CheckRates W18
Genera pickle cr_w18_data.pkl con todos los agregados necesarios.
"""
import pickle
import pandas as pd
import numpy as np
import os

from engine import banda_eficacia, banda_convrate

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK = os.getenv('WEEK', 'W20')
PERIODO = os.getenv('PERIODO', '12–18 may 2026')
MES_AÑO = os.getenv('MES_AÑO', 'Mayo 2026')
VOL_NUM = os.getenv('VOL_NUM', '20')
FECHA_PUB = os.getenv('FECHA_PUB', 'LUNES 18 de Mayo de 2026')  # Día de publicación del reporte

# Derivar números de semana
WEEK_NUM = int(WEEK.replace('W', ''))
VOL_NUM_PREV = int(VOL_NUM) - 1

PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']

CANAL_VALIDO = ['B2C', 'B2B (OP)', 'CUG (UOP)']

# ── CARGA ─────────────────────────────────────────────────────────────────────
def load_and_clean(path):
    df = pd.read_excel(path)
    df.rename(columns={'Corporate':'CorpName', 'CheckRates Únicos':'CR_Unicos'}, inplace=True)
    df = df[df['DistributionCategory'].isin(CANAL_VALIDO)].copy()
    df['Eficacia']  = df['Successful UniqueChkRts'] / df['CR_Unicos']
    df['ConvRate']  = df['Bookings'] / df['CR_Unicos']
    df['Eficacia']  = df['Eficacia'].clip(0, 1)
    df['ConvRate']  = df['ConvRate'].clip(0)
    return df

df18 = load_and_clean(f'/mnt/project/Dataset_CheckRates_W{WEEK_NUM}.xlsx' if os.path.exists(f'/mnt/project/Dataset_CheckRates_W{WEEK_NUM}.xlsx') else f'/mnt/user-data/uploads/Dataset_CheckRates_W{WEEK_NUM}.xlsx')  # semana actual
df17 = load_and_clean(f'/mnt/user-data/uploads/Dataset_CheckRates_W{VOL_NUM_PREV}.xlsx')  # semana anterior para WoW

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
    g['BandaEficacia'] = g.apply(lambda r: banda_eficacia(r['Eficacia']), axis=1)
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
    g['BandaEficacia'] = g.apply(lambda r: banda_eficacia(r['Eficacia']), axis=1)
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
    'criticos':       df_crit_pool.head(5).reset_index(drop=True),
    'criticos_extra': df_crit_pool.iloc[5:10].reset_index(drop=True),
    'bajo_rend':      df_br_pool.head(5).reset_index(drop=True),
    'bajo_rend_extra':df_br_pool.iloc[5:10].reset_index(drop=True),
    'sin_conv':       df_sc_pool.head(5).reset_index(drop=True),
    'sin_conv_extra': df_sc_pool.iloc[5:10].reset_index(drop=True),
    'menor_cv':       df_mcv_pool.head(10).reset_index(drop=True),
    'corps_10':       g_corp.head(10).reset_index(drop=True),
    'destinos':       g_destino.head(10).reset_index(drop=True),
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
    # Hotel (P80)
    g_h = p80_hotel[p80_hotel['Bookings'] > 0].copy()  # excluir Sin Conversión del card Conv Rate
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
    # Filtro P50 para excluir destinos/corps de volumen insignificante
    p50_d = g_d['CR_Unicos'].quantile(0.50)
    p50_c = g_c['CR_Unicos'].quantile(0.50)
    p50_h = g_h['CR_Unicos'].quantile(0.50)
    df_d = g_d[g_d['CR_Unicos']>=p50_d].sort_values('Eficacia').head(10).reset_index(drop=True)
    df_c = g_c[g_c['CR_Unicos']>=p50_c].sort_values('Eficacia').head(10).reset_index(drop=True)
    df_h = g_h[g_h['CR_Unicos']>=p50_h].sort_values('Eficacia').head(10).reset_index(drop=True)
    # Merge WoW
    df_d = df_d.merge(g_dest_w17[['Destino','Eficacia_W17']], on='Destino', how='left')
    df_d['Eficacia_WoW_pp'] = (df_d['Eficacia'] - df_d['Eficacia_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','Eficacia_W17']], on='CorpName', how='left')
    df_c['Eficacia_WoW_pp'] = (df_c['Eficacia'] - df_c['Eficacia_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','Eficacia_W17']], on='Hotel', how='left')
    df_h['Eficacia_WoW_pp'] = (df_h['Eficacia'] - df_h['Eficacia_W17']) * 100
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
    g_h = p80_hotel[p80_hotel['Bookings'] > 0].copy()  # excluir Sin Conversión del card Conv Rate
    g_ch = df18.groupby('ExternalProviderName', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_ch['ConvRate'] = g_ch['Bookings']/g_ch['CR_Unicos']
    g_ch['Eficacia'] = g_ch['Successful']/g_ch['CR_Unicos']
    g_can = df18_p80.groupby('DistributionCategory', as_index=False).agg(CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'), Successful=('Successful UniqueChkRts','sum'))
    g_can['ConvRate'] = g_can['Bookings']/g_can['CR_Unicos']
    g_can['Eficacia'] = g_can['Successful']/g_can['CR_Unicos']
    g_can.rename(columns={'DistributionCategory':'Canasta'}, inplace=True)
    # Filtro P50 para excluir destinos/corps de volumen insignificante
    p50_d = g_d['CR_Unicos'].quantile(0.50)
    p50_c = g_c['CR_Unicos'].quantile(0.50)
    p50_h = g_h['CR_Unicos'].quantile(0.50)
    df_d = g_d[(g_d['CR_Unicos']>=p50_d) & (g_d['Bookings']>0)].sort_values('ConvRate').head(10).reset_index(drop=True)
    df_c = g_c[g_c['CR_Unicos']>=p50_c].sort_values('ConvRate').head(10).reset_index(drop=True)
    df_h = g_h[g_h['CR_Unicos']>=p50_h].sort_values('ConvRate').head(10).reset_index(drop=True)
    # Merge WoW
    df_d = df_d.merge(g_dest_w17[['Destino','ConvRate_W17']], on='Destino', how='left')
    df_d['ConvRate_WoW_pp'] = (df_d['ConvRate'] - df_d['ConvRate_W17']) * 100
    df_c = df_c.merge(g_corp_w17[['CorpName','ConvRate_W17']], on='CorpName', how='left')
    df_c['ConvRate_WoW_pp'] = (df_c['ConvRate'] - df_c['ConvRate_W17']) * 100
    df_h = df_h.merge(g_hotel_w17[['Hotel','ConvRate_W17']], on='Hotel', how='left')
    df_h['ConvRate_WoW_pp'] = (df_h['ConvRate'] - df_h['ConvRate_W17']) * 100
    return {
        'destino': df_d,
        'corp':    df_c,
        'hotel':   df_h,
        'channel': _add_wow_channel(g_ch, 'ConvRate'),
        'canasta': g_can.sort_values('ConvRate').reset_index(drop=True),
    }

TAB_EF = tab_eficacia()
TAB_CV = tab_convrate()

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
        'top_crit': df_crit.head(5).reset_index(drop=True),
        'top_crit_extra': df_crit.iloc[5:10].reset_index(drop=True),
        'top_br':   df_br.head(5).reset_index(drop=True),
        'top_br_extra':  df_br.iloc[5:10].reset_index(drop=True),
        'top_sc':   df_sc.head(5).reset_index(drop=True),
        'top_sc_extra':  df_sc.iloc[5:10].reset_index(drop=True),
        'top_mcv':  df_mcv.head(10).reset_index(drop=True),
        'g_corp':   g_corp_can.head(10),
        'g_dest':   g_dest_can.head(10),
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

with open(f'/mnt/project/_scripts/cr_w{VOL_NUM}_data.pkl','wb') as f:
    pickle.dump(D, f)

print(f"✅ Pickle guardado: cr_w20_data.pkl")
print(f"   Eficacia global W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['eficacia']:.4f} ({M[f'global_w{WEEK_NUM}']['eficacia']*100:.2f}%)")
print(f"   ConvRate global W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['conv_rate']:.4f} ({M[f'global_w{WEEK_NUM}']['conv_rate']*100:.2f}%)")
print(f"   CR únicos W{WEEK_NUM}: {M[f'global_w{WEEK_NUM}']['cr_unicos']:,}")
print(f"   Bookings W{WEEK_NUM}:  {M[f'global_w{WEEK_NUM}']['bookings']:,}")
print(f"   Hoteles P80:   {len(p80_hotel)}")
print(f"   Severity Ef P80: {dict(sev_ef_p80)}")
print(f"   Severity CV P80: {dict(sev_cv_p80)}")
print(f"   Canastas: B2C={M[f'B2C_w{WEEK_NUM}']['cr_unicos']:,} | OP={M[f'B2B (OP)_w{WEEK_NUM}']['cr_unicos']:,} | CUG={M[f'CUG (UOP)_w{WEEK_NUM}']['cr_unicos']:,}")
