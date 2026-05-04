"""
Motor de cálculo W18 · Proyecto PRICE
Sistema bandas D · post W17
"""
import pandas as pd
import numpy as np

# ============ BANDAS DE SEVERITY (sistema D) ============
def banda_nodispo(pct):
    """% NoDispo · 5 niveles"""
    if pd.isna(pct): return 'Sin Datos'
    if pct < 0.03:   return 'Exitosa'
    if pct < 0.05:   return 'Aceptable'
    if pct < 0.20:   return 'Revisar'
    if pct < 0.60:   return 'Crítica'
    return 'Súper Crítica'

def banda_eficacia(pct):
    """% Eficacia CR · 5 niveles"""
    if pd.isna(pct): return 'Sin Datos'
    if pct >= 0.97:  return 'Exitosa'
    if pct >= 0.93:  return 'Aceptable'
    if pct >= 0.85:  return 'Revisar'
    if pct >= 0.60:  return 'Crítica'
    return 'Súper Crítica'

def banda_rpm(rpm, bkgs):
    """RPM como GBM USD/M (Gross Booking USD por millón de búsquedas) · sistema D
    Thresholds: <$200 Crítica · $200-$650 Revisar · $650-$1500 Aceptable · ≥$1500 Exitosa
    Target ≥ $650 (banda Aceptable o mejor)"""
    if pd.isna(bkgs) or bkgs == 0: return 'Sin Conversión'
    if pd.isna(rpm): return 'Sin Datos'
    if rpm < 200:    return 'Crítica'
    if rpm < 650:    return 'Revisar'
    if rpm < 1500:   return 'Aceptable'
    return 'Exitosa'

def banda_convrate(cr, bkgs):
    """Conv Rate (CR) · sistema D"""
    if pd.isna(bkgs) or bkgs == 0: return 'Sin Conversión'
    if pd.isna(cr): return 'Sin Datos'
    if cr < 0.008:   return 'Crítica'
    if cr < 0.015:   return 'Revisar'
    if cr < 0.025:   return 'Aceptable'
    return 'Exitosa'

# ============ CHANNEL AGRUPADO (CR) ============
PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']

def grupo_channel(provider):
    if pd.isna(provider): return 'Otros'
    p = str(provider).strip()
    for pp in PRODUCTO_PROPIO:
        if pp.lower() == p.lower(): return 'Producto Propio'
    for tp in THIRD_PARTY:
        if tp.lower() == p.lower(): return 'Third Party'
    return 'Otros'

# ============ LIMPIEZA ============
def clean_rnd(df):
    """Limpia dataset RND"""
    df = df.copy()
    # filas basura
    df = df[df['CorpName'].astype(str).str.strip() != '-']
    df = df[df['Hotel'].astype(str).str.strip() != '-']
    df = df[df['DistributionCategory'].isin(['B2C','B2B (OP)','CUG (UOP)'])]
    # tipos
    for c in ['Trafico','Bookings','gb_usd','%NoDispo']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df.reset_index(drop=True)

def clean_cr(df):
    """Limpia dataset CR"""
    df = df.copy()
    df = df[df['DistributionCategory'].isin(['B2C','B2B (OP)','CUG (UOP)'])]
    df = df[df['CorpName'].astype(str).str.strip() != '-']
    df = df[df['Hotel'].astype(str).str.strip() != '-']
    for c in ['Bookings','#Errors','Successful UniqueChkRts','CheckRates Únicos']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['Conversion Rate'] = pd.to_numeric(df['Conversion Rate'], errors='coerce').fillna(0)
    df['Efectividad en CheckRates'] = pd.to_numeric(df['Efectividad en CheckRates'], errors='coerce').fillna(0)
    return df.reset_index(drop=True)

# ============ MÉTRICAS RND ============
def metrics_rnd_global(df):
    """Métricas globales RND"""
    trafico = df['Trafico'].sum()
    bkgs    = df['Bookings'].sum()
    gb      = df['gb_usd'].sum()
    nodispo = df['Trafico'].mul(df['%NoDispo']).sum() / trafico if trafico > 0 else 0
    rpm     = (gb / trafico * 1_000_000) if trafico > 0 else 0
    conv    = bkgs / trafico if trafico > 0 else 0
    return {
        'trafico': trafico,
        'bookings': bkgs,
        'gb_usd': gb,
        'pct_nodispo': nodispo,
        'rpm': rpm,
        'conv_rate': conv,
        'banda_nodispo': banda_nodispo(nodispo),
        'banda_rpm': banda_rpm(rpm, bkgs),
        'n_hoteles': df['Hotel'].nunique(),
        'n_corp': df['CorpName'].nunique(),
        'n_destinos': df['Destino'].nunique(),
        'n_paises': df['PaisDestino'].nunique(),
    }

def aggregate_rnd(df, by):
    """Agrega RND por nivel (Hotel, Corp, Destino, etc.)"""
    g = df.groupby(by).agg(
        Trafico=('Trafico','sum'),
        Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'),
        TraficoNoDispo=('Trafico', lambda x: (x * df.loc[x.index, '%NoDispo']).sum()),
    ).reset_index()
    g['%NoDispo'] = g['TraficoNoDispo'] / g['Trafico'].replace(0, np.nan)
    g['%NoDispo'] = g['%NoDispo'].fillna(0)
    g['RPM']      = (g['gb_usd'] / g['Trafico'].replace(0, np.nan) * 1_000_000).fillna(0)
    g['ConvRate'] = (g['Bookings'] / g['Trafico'].replace(0, np.nan)).fillna(0)
    g['BandaNoDispo'] = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM']     = g.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
    return g

def pareto_p80(g, col='Trafico'):
    """Top hoteles que acumulan 80% del tráfico/checkrates"""
    g = g.sort_values(col, ascending=False).reset_index(drop=True)
    g['cum'] = g[col].cumsum()
    total = g[col].sum()
    if total == 0: return g.iloc[0:0]
    g['cum_pct'] = g['cum'] / total
    return g[g['cum_pct'] <= 0.80].drop(columns=['cum','cum_pct'])

# ============ MÉTRICAS CR ============
def metrics_cr_global(df):
    cr_unicos = df['CheckRates Únicos'].sum()
    success   = df['Successful UniqueChkRts'].sum()
    bkgs      = df['Bookings'].sum()
    errs      = df['#Errors'].sum()
    eficacia  = success / cr_unicos if cr_unicos > 0 else 0
    convrate  = bkgs / cr_unicos if cr_unicos > 0 else 0
    pct_err   = errs / cr_unicos if cr_unicos > 0 else 0
    return {
        'cr_unicos': cr_unicos,
        'success': success,
        'bookings': bkgs,
        'errors': errs,
        'eficacia': eficacia,
        'conv_rate': convrate,
        'pct_errors': pct_err,
        'banda_eficacia': banda_eficacia(eficacia),
        'banda_convrate': banda_convrate(convrate, bkgs),
        'n_hoteles': df['Hotel'].nunique(),
        'n_corp': df['CorpName'].nunique(),
        'n_destinos': df['Destino'].nunique(),
        'n_channels': df['ExternalProviderName'].nunique(),
    }

def aggregate_cr(df, by):
    g = df.groupby(by).agg(
        CR_Unicos=('CheckRates Únicos','sum'),
        Success=('Successful UniqueChkRts','sum'),
        Bookings=('Bookings','sum'),
        Errors=('#Errors','sum'),
    ).reset_index()
    g['Eficacia'] = (g['Success']  / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['ConvRate'] = (g['Bookings'] / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['PctErr']   = (g['Errors']   / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['BandaEficacia'] = g['Eficacia'].apply(banda_eficacia)
    g['BandaConvRate'] = g.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
    return g

# ============ FORMATEO ============
def fmt_int(x):
    if pd.isna(x): return '-'
    return f'{int(round(x)):,}'.replace(',', '.')

def fmt_usd(x):
    if pd.isna(x): return '$0'
    if abs(x) >= 1_000_000: return f'${x/1_000_000:,.2f}M'.replace(',', '.')
    if abs(x) >= 1_000:     return f'${x/1_000:,.1f}K'.replace(',', '.')
    return f'${x:,.0f}'.replace(',', '.')

def fmt_pct(x, dec=1):
    if pd.isna(x): return '-'
    return f'{x*100:.{dec}f}%'.replace('.', ',')

def fmt_num(x, dec=2):
    if pd.isna(x): return '-'
    return f'{x:,.{dec}f}'.replace(',', '|').replace('.', ',').replace('|', '.')

def fmt_wow(curr, prev, kind='abs', dec=1):
    """Calcula delta WoW · kind: abs, pct, pp"""
    if pd.isna(prev) or prev == 0:
        if curr == 0: return ('=', 0)
        return ('▲', None)
    if kind == 'pp':  # percentage points
        d = (curr - prev) * 100
        sign = '▲' if d > 0 else ('▼' if d < 0 else '=')
        return (sign, d)
    if kind == 'pct':  # relative %
        d = (curr - prev) / prev * 100
        sign = '▲' if d > 0 else ('▼' if d < 0 else '=')
        return (sign, d)
    d = curr - prev
    sign = '▲' if d > 0 else ('▼' if d < 0 else '=')
    return (sign, d)
