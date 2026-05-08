"""
Cálculo final · todas las métricas, rankings, deltas RND W18
"""
import pandas as pd, numpy as np
import pickle
from engine import *

rnd_w18 = clean_rnd(pd.read_pickle('rnd_w18.pkl'))
rnd_w17 = clean_rnd(pd.read_pickle('rnd_w17.pkl'))

# --------- métricas globales y por canasta ----------
M = {}
M['global_w18'] = metrics_rnd_global(rnd_w18)
M['global_w17'] = metrics_rnd_global(rnd_w17)
for c in ['B2C','B2B (OP)','CUG (UOP)']:
    M[f'{c}_w18'] = metrics_rnd_global(rnd_w18[rnd_w18['DistributionCategory']==c])
    M[f'{c}_w17'] = metrics_rnd_global(rnd_w17[rnd_w17['DistributionCategory']==c])

# --------- aggregados por nivel (TODOS) ----------
def make_hotel_agg(df):
    g = df.groupby(['Hotel','CorpName','PaisDestino','Destino']).agg(
        Trafico=('Trafico','sum'),
        Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'),
        TraficoNoDispo=('Trafico', lambda x: (x * df.loc[x.index, '%NoDispo']).sum()),
    ).reset_index()
    g['%NoDispo'] = (g['TraficoNoDispo'] / g['Trafico'].replace(0, np.nan)).fillna(0)
    g['RPM'] = (g['gb_usd'] / g['Trafico'].replace(0, np.nan) * 1_000_000).fillna(0)
    g['ConvRate'] = (g['Bookings'] / g['Trafico'].replace(0, np.nan)).fillna(0)
    g['BandaNoDispo'] = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM'] = g.apply(lambda r: banda_rpm(r['RPM'], r['Bookings']), axis=1)
    g['DemandaNoConvertida'] = g['Trafico'] * g['%NoDispo']
    return g

g_hotel_w18 = make_hotel_agg(rnd_w18)
g_hotel_w17 = make_hotel_agg(rnd_w17)
g_destino_w18 = aggregate_rnd(rnd_w18, 'Destino')
g_destino_w17 = aggregate_rnd(rnd_w17, 'Destino')
g_corp_w18 = aggregate_rnd(rnd_w18, 'CorpName')
g_corp_w17 = aggregate_rnd(rnd_w17, 'CorpName')
g_pais_w18 = aggregate_rnd(rnd_w18, 'PaisDestino')
g_pais_w17 = aggregate_rnd(rnd_w17, 'PaisDestino')

# --------- P80 ----------
p80_hotel_w18 = pareto_p80(g_hotel_w18, 'Trafico')

# --------- Severity counts (en P80) ----------
sev_nd = p80_hotel_w18['BandaNoDispo'].value_counts().reindex(
    ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
sev_rpm = p80_hotel_w18['BandaRPM'].value_counts().reindex(
    ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)

# --------- TOP 5 listas ----------
TOP = {}
# Demanda no convertida
TOP['demanda_nc'] = g_hotel_w18.sort_values('DemandaNoConvertida', ascending=False).head(5).reset_index(drop=True)
TOP['demanda_nc_extra'] = g_hotel_w18.sort_values('DemandaNoConvertida', ascending=False).iloc[5:10].reset_index(drop=True)

# Bajo Rendimiento (P80, BKGS>0, RPM>0, RPM por debajo del P50 procesable)
proc_p80 = p80_hotel_w18[(p80_hotel_w18['Bookings']>0) & (p80_hotel_w18['RPM']>0)]
rpm_p50_proc = proc_p80['RPM'].quantile(0.50)
mask_br = (p80_hotel_w18['Bookings'] > 0) & (p80_hotel_w18['RPM'] > 0) & (p80_hotel_w18['RPM'] < rpm_p50_proc)
TOP['bajo_rend'] = p80_hotel_w18[mask_br].sort_values('Trafico', ascending=False).head(5).reset_index(drop=True)
TOP['bajo_rend_extra'] = p80_hotel_w18[mask_br].sort_values('Trafico', ascending=False).iloc[5:10].reset_index(drop=True)

# Sin Conversión (P80, BKGS=0)
TOP['sin_conv'] = p80_hotel_w18[p80_hotel_w18['Bookings']==0].sort_values('Trafico', ascending=False).head(5).reset_index(drop=True)
TOP['sin_conv_extra'] = p80_hotel_w18[p80_hotel_w18['Bookings']==0].sort_values('Trafico', ascending=False).iloc[5:10].reset_index(drop=True)

# Por destino (Top 5 por tráfico)
TOP['destinos'] = g_destino_w18.sort_values('Trafico', ascending=False).head(5).reset_index(drop=True)
TOP['destinos_10'] = g_destino_w18.sort_values('Trafico', ascending=False).head(10).reset_index(drop=True)

# Por corp (Top 5)
TOP['corps'] = g_corp_w18.sort_values('Trafico', ascending=False).head(5).reset_index(drop=True)
TOP['corps_10'] = g_corp_w18.sort_values('Trafico', ascending=False).head(10).reset_index(drop=True)

# Por país (Top 5)
TOP['paises'] = g_pais_w18.sort_values('Trafico', ascending=False).head(5).reset_index(drop=True)
TOP['paises_10'] = g_pais_w18.sort_values('Trafico', ascending=False).head(10).reset_index(drop=True)

# Top hoteles
TOP['hoteles'] = g_hotel_w18.sort_values('Trafico', ascending=False).head(10).reset_index(drop=True)

# --------- Para tabs KPI Hero %NoDispo: top 5 con peor %NoDispo (filtro de tráfico mínimo) ----------
# Tráfico mínimo para entrar en ranking de "peor": top 20% por tráfico
min_traf = g_hotel_w18['Trafico'].quantile(0.80)
TAB_NoDispo = {}
TAB_NoDispo['pais']    = g_pais_w18[g_pais_w18['Trafico']>50_000_000].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True)
TAB_NoDispo['destino'] = g_destino_w18[g_destino_w18['Trafico']>20_000_000].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True)
TAB_NoDispo['corp']    = g_corp_w18[g_corp_w18['Trafico']>50_000_000].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True)
TAB_NoDispo['hotel']   = g_hotel_w18[g_hotel_w18['Trafico']>min_traf].sort_values('%NoDispo', ascending=False).head(10).reset_index(drop=True)
TAB_NoDispo['canasta'] = pd.DataFrame([
    {'Canasta':'B2C',      '%NoDispo':M['B2C_w18']['pct_nodispo']},
    {'Canasta':'B2B (OP)', '%NoDispo':M['B2B (OP)_w18']['pct_nodispo']},
    {'Canasta':'CUG (UOP)','%NoDispo':M['CUG (UOP)_w18']['pct_nodispo']},
]).sort_values('%NoDispo', ascending=False).reset_index(drop=True)

# ── WoW por dimensión para TAB_NoDispo ──────────────────────────────────────
def _merge_wow_nd(tab, df17, key_col):
    """Agrega columna NoDispo_W17 y NoDispo_WoW_pp al TAB."""
    ref = df17[[key_col, '%NoDispo']].rename(columns={'%NoDispo': 'NoDispo_W17'})
    merged = tab.merge(ref, on=key_col, how='left')
    merged['NoDispo_WoW_pp'] = (merged['%NoDispo'] - merged['NoDispo_W17']) * 100
    return merged

TAB_NoDispo['pais']    = _merge_wow_nd(TAB_NoDispo['pais'],    g_pais_w17,    'PaisDestino')
TAB_NoDispo['destino'] = _merge_wow_nd(TAB_NoDispo['destino'], g_destino_w17, 'Destino')
TAB_NoDispo['corp']    = _merge_wow_nd(TAB_NoDispo['corp'],    g_corp_w17,    'CorpName')
TAB_NoDispo['hotel']   = _merge_wow_nd(TAB_NoDispo['hotel'],   g_hotel_w17,   'Hotel')
# Canasta WoW
TAB_NoDispo['canasta']['NoDispo_WoW_pp'] = [
    (M['B2C_w18']['pct_nodispo']      - M['B2C_w17']['pct_nodispo'])      * 100,
    (M['B2B (OP)_w18']['pct_nodispo'] - M['B2B (OP)_w17']['pct_nodispo']) * 100,
    (M['CUG (UOP)_w18']['pct_nodispo']- M['CUG (UOP)_w17']['pct_nodispo'])* 100,
]

# --------- Para tabs KPI Hero RPM: top 10 con menor RPM positivo (BKGS>0, RPM>0) ----------
TAB_RPM = {}
TAB_RPM['pais']    = g_pais_w18[(g_pais_w18['Bookings']>10) & (g_pais_w18['RPM']>0) & (g_pais_w18['Trafico']>50_000_000)].sort_values('RPM').head(10).reset_index(drop=True)
TAB_RPM['destino'] = g_destino_w18[(g_destino_w18['Bookings']>10) & (g_destino_w18['RPM']>0) & (g_destino_w18['Trafico']>20_000_000)].sort_values('RPM').head(10).reset_index(drop=True)
TAB_RPM['corp']    = g_corp_w18[(g_corp_w18['Bookings']>10) & (g_corp_w18['RPM']>0) & (g_corp_w18['Trafico']>50_000_000)].sort_values('RPM').head(10).reset_index(drop=True)
TAB_RPM['hotel']   = g_hotel_w18[(g_hotel_w18['Bookings']>0) & (g_hotel_w18['RPM']>0) & (g_hotel_w18['Trafico']>min_traf)].sort_values('RPM').head(10).reset_index(drop=True)
TAB_RPM['canasta'] = pd.DataFrame([
    {'Canasta':'B2C',      'RPM':M['B2C_w18']['rpm']},
    {'Canasta':'B2B (OP)', 'RPM':M['B2B (OP)_w18']['rpm']},
    {'Canasta':'CUG (UOP)','RPM':M['CUG (UOP)_w18']['rpm']},
]).sort_values('RPM').reset_index(drop=True)

# ── WoW por dimensión para TAB_RPM ──────────────────────────────────────────
def _merge_wow_rpm(tab, df17, key_col):
    """Agrega columna RPM_W17 y RPM_WoW_pct al TAB."""
    ref = df17[[key_col, 'RPM']].rename(columns={'RPM': 'RPM_W17'})
    merged = tab.merge(ref, on=key_col, how='left')
    merged['RPM_WoW_pct'] = (merged['RPM'] / merged['RPM_W17'] - 1) * 100
    return merged

TAB_RPM['pais']    = _merge_wow_rpm(TAB_RPM['pais'],    g_pais_w17,    'PaisDestino')
TAB_RPM['destino'] = _merge_wow_rpm(TAB_RPM['destino'], g_destino_w17, 'Destino')
TAB_RPM['corp']    = _merge_wow_rpm(TAB_RPM['corp'],    g_corp_w17,    'CorpName')
TAB_RPM['hotel']   = _merge_wow_rpm(TAB_RPM['hotel'],   g_hotel_w17,   'Hotel')
# Canasta WoW
TAB_RPM['canasta']['RPM_WoW_pct'] = [
    (M['B2C_w18']['rpm']      / M['B2C_w17']['rpm']      - 1) * 100,
    (M['B2B (OP)_w18']['rpm'] / M['B2B (OP)_w17']['rpm'] - 1) * 100,
    (M['CUG (UOP)_w18']['rpm']/ M['CUG (UOP)_w17']['rpm']- 1) * 100,
]

# --------- Datos por canasta para sección "Análisis por Canasta" ----------
CANASTA = {}
for c, key in [('B2C','b2c'), ('B2B (OP)','op'), ('CUG (UOP)','cug')]:
    sub18 = rnd_w18[rnd_w18['DistributionCategory']==c]
    sub17 = rnd_w17[rnd_w17['DistributionCategory']==c]
    g_h = make_hotel_agg(sub18)
    g_d = aggregate_rnd(sub18, 'Destino')
    g_co = aggregate_rnd(sub18, 'CorpName')
    g_p = aggregate_rnd(sub18, 'PaisDestino')
    p80 = pareto_p80(g_h, 'Trafico')
    
    # KPIs
    m18 = metrics_rnd_global(sub18)
    m17 = metrics_rnd_global(sub17)
    
    # Tabs Top 5 por nivel (% NoDispo) — los peores
    tt_dest = g_d[(g_d['Trafico']>5_000_000) & (g_d['BandaNoDispo'].isin(['Crítica','Súper Crítica','Revisar']))].sort_values('%NoDispo', ascending=False).head(10)
    if len(tt_dest) < 10:
        tt_dest = g_d[g_d['Trafico']>5_000_000].sort_values('%NoDispo', ascending=False).head(10)
    tt_corp = g_co[g_co['Trafico']>10_000_000].sort_values('%NoDispo', ascending=False).head(10)
    tt_hot  = g_h[g_h['Trafico']>g_h['Trafico'].quantile(0.95)].sort_values('%NoDispo', ascending=False).head(10)
    tt_pais = g_p[g_p['Trafico']>30_000_000].sort_values('%NoDispo', ascending=False).head(10)
    
    # Bajo rendimiento canasta · BKGS>0, RPM>0 (excluir refunds), por debajo del P50 procesable de la canasta
    proc_canasta = p80[(p80['Bookings']>0) & (p80['RPM']>0)]
    rpm_p50 = proc_canasta['RPM'].quantile(0.50) if len(proc_canasta)>0 else 0
    bajo = p80[(p80['Bookings']>0) & (p80['RPM']>0) & (p80['RPM'] < rpm_p50)].sort_values('Trafico', ascending=False).head(10)
    sin_conv = p80[p80['Bookings']==0].sort_values('Trafico', ascending=False).head(10)
    
    # Sev count
    n_critica = (g_h['BandaNoDispo']=='Crítica').sum() + (g_h['BandaNoDispo']=='Súper Crítica').sum()
    
    # Severity por canasta (sobre P80)
    sev_nd_canasta = p80['BandaNoDispo'].value_counts().reindex(
        ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
    sev_rpm_canasta = p80['BandaRPM'].value_counts().reindex(
        ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
    
    # Alertas por canasta · peor hotel/destino/corp por %NoDispo y por RPM
    alert_h_nd_pool = p80[p80['Trafico']>p80['Trafico'].quantile(0.50)]
    alert_h_nd = alert_h_nd_pool.sort_values('%NoDispo', ascending=False).iloc[0] if len(alert_h_nd_pool)>0 else None
    alert_h_rpm_pool = p80[(p80['Bookings']>0) & (p80['RPM']>0) & (p80['Trafico']>p80['Trafico'].quantile(0.50))]
    alert_h_rpm = alert_h_rpm_pool.sort_values('RPM').iloc[0] if len(alert_h_rpm_pool)>0 else None
    
    alert_d_nd_pool = g_d[g_d['Trafico']>5_000_000]
    alert_d_nd = alert_d_nd_pool.sort_values('%NoDispo', ascending=False).iloc[0] if len(alert_d_nd_pool)>0 else None
    alert_d_rpm_pool = g_d[(g_d['Bookings']>0) & (g_d['RPM']>0) & (g_d['Trafico']>5_000_000)]
    alert_d_rpm = alert_d_rpm_pool.sort_values('RPM').iloc[0] if len(alert_d_rpm_pool)>0 else None
    
    alert_co_nd_pool = g_co[g_co['Trafico']>10_000_000]
    alert_co_nd = alert_co_nd_pool.sort_values('%NoDispo', ascending=False).iloc[0] if len(alert_co_nd_pool)>0 else None
    alert_co_rpm_pool = g_co[(g_co['Bookings']>0) & (g_co['RPM']>0) & (g_co['Trafico']>10_000_000)]
    alert_co_rpm = alert_co_rpm_pool.sort_values('RPM').iloc[0] if len(alert_co_rpm_pool)>0 else None
    
    CANASTA[key] = {
        'name': c, 'short': {'B2C':'B2C','B2B (OP)':'B2B Opaco','CUG (UOP)':'CUG'}[c],
        'm18': m18, 'm17': m17,
        'agg_hotel': g_h, 'agg_destino': g_d, 'agg_corp': g_co, 'agg_pais': g_p,
        'p80': p80,
        'top_dest': tt_dest.reset_index(drop=True), 'top_corp': tt_corp.reset_index(drop=True),
        'top_hot': tt_hot.reset_index(drop=True), 'top_pais': tt_pais.reset_index(drop=True),
        'bajo_rend': bajo.reset_index(drop=True), 'sin_conv': sin_conv.reset_index(drop=True),
        'n_critica': int(n_critica),
        'sev_nd': sev_nd_canasta.to_dict(),
        'sev_rpm': sev_rpm_canasta.to_dict(),
        'alert_h_nd': alert_h_nd, 'alert_h_rpm': alert_h_rpm,
        'alert_d_nd': alert_d_nd, 'alert_d_rpm': alert_d_rpm,
        'alert_co_nd': alert_co_nd, 'alert_co_rpm': alert_co_rpm,
    }

# Guardar
with open('rnd_w18_data.pkl','wb') as f:
    pickle.dump({'M':M,'TOP':TOP,'TAB_NoDispo':TAB_NoDispo,'TAB_RPM':TAB_RPM,
                 'CANASTA':CANASTA,'sev_nd':sev_nd,'sev_rpm':sev_rpm,
                 'g_hotel':g_hotel_w18,'p80_hotel':p80_hotel_w18}, f)

# Resumen para validar
print(f"\n=== RND W18 · Resumen Globales ===")
print(f"Tráfico: {fmt_int(M['global_w18']['trafico'])}")
print(f"Bookings: {fmt_int(M['global_w18']['bookings'])} (W17 {fmt_int(M['global_w17']['bookings'])})")
print(f"GB: {fmt_usd(M['global_w18']['gb_usd'])} (W17 {fmt_usd(M['global_w17']['gb_usd'])})")
print(f"%NoDispo: {fmt_pct(M['global_w18']['pct_nodispo'],2)} (W17 {fmt_pct(M['global_w17']['pct_nodispo'],2)})")
print(f"RPM: {fmt_num(M['global_w18']['rpm'],2)} (W17 {fmt_num(M['global_w17']['rpm'],2)})")
print(f"Hoteles P80: {len(p80_hotel_w18):,}")
print(f"\nSeverity %NoDispo (P80): {sev_nd.to_dict()}")
print(f"Severity RPM (P80): {sev_rpm.to_dict()}")
