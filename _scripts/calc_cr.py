"""
Cálculo final · todas las métricas CR W18
"""
import pandas as pd, numpy as np
import pickle
from engine import *

cr_w18 = clean_cr(pd.read_pickle('cr_w18.pkl'))
cr_w17 = clean_cr(pd.read_pickle('cr_w17.pkl'))

# Agregar columna Grupo (Channel agrupado)
cr_w18['Grupo'] = cr_w18['ExternalProviderName'].apply(grupo_channel)
cr_w17['Grupo'] = cr_w17['ExternalProviderName'].apply(grupo_channel)

M = {}
M['global_w18'] = metrics_cr_global(cr_w18)
M['global_w17'] = metrics_cr_global(cr_w17)
for c in ['B2C','B2B (OP)','CUG (UOP)']:
    M[f'{c}_w18'] = metrics_cr_global(cr_w18[cr_w18['DistributionCategory']==c])
    M[f'{c}_w17'] = metrics_cr_global(cr_w17[cr_w17['DistributionCategory']==c])

# Aggregados por nivel
def make_hotel_agg_cr(df):
    g = df.groupby(['Hotel','CorpName','Destino']).agg(
        CR_Unicos=('CheckRates Únicos','sum'),
        Success=('Successful UniqueChkRts','sum'),
        Bookings=('Bookings','sum'),
        Errors=('#Errors','sum'),
    ).reset_index()
    g['Eficacia'] = (g['Success']  / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['ConvRate'] = (g['Bookings'] / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['PctErr'] = (g['Errors'] / g['CR_Unicos'].replace(0, np.nan)).fillna(0)
    g['BandaEficacia'] = g['Eficacia'].apply(banda_eficacia)
    g['BandaConvRate'] = g.apply(lambda r: banda_convrate(r['ConvRate'], r['Bookings']), axis=1)
    return g

g_hotel_w18 = make_hotel_agg_cr(cr_w18)
g_hotel_w17 = make_hotel_agg_cr(cr_w17)
g_destino_w18 = aggregate_cr(cr_w18, 'Destino')
g_corp_w18 = aggregate_cr(cr_w18, 'CorpName')
g_corp_w17 = aggregate_cr(cr_w17, 'CorpName')
g_channel_w18 = aggregate_cr(cr_w18, 'ExternalProviderName')
g_grupo_w18 = aggregate_cr(cr_w18, 'Grupo')

p80_hotel_w18 = pareto_p80(g_hotel_w18, 'CR_Unicos')

# Severity counts
sev_ef  = g_hotel_w18['BandaEficacia'].value_counts().reindex(
    ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
sev_cv  = g_hotel_w18['BandaConvRate'].value_counts().reindex(
    ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
sev_ef_p80 = p80_hotel_w18['BandaEficacia'].value_counts().reindex(
    ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
sev_cv_p80 = p80_hotel_w18['BandaConvRate'].value_counts().reindex(
    ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)

# TOP listas
TOP = {}

# Hoteles Críticos (P80, eficacia Crítica/Súper Crítica · BKGS>0 y Eficacia>0 para excluir Sin Conversión)
crit = p80_hotel_w18[(p80_hotel_w18['BandaEficacia'].isin(['Crítica','Súper Crítica'])) & (p80_hotel_w18['Bookings']>0) & (p80_hotel_w18['Eficacia']>0)].sort_values('CR_Unicos', ascending=False)
TOP['criticos'] = crit.head(5).reset_index(drop=True)
TOP['criticos_extra'] = crit.iloc[5:10].reset_index(drop=True)

# Bajo Rendimiento (P80, ConvRate Crítica/Revisar y BKGS>0)
br = p80_hotel_w18[(p80_hotel_w18['BandaConvRate'].isin(['Crítica','Revisar'])) & (p80_hotel_w18['Bookings']>0)]
TOP['bajo_rend'] = br.sort_values('CR_Unicos', ascending=False).head(5).reset_index(drop=True)
TOP['bajo_rend_extra'] = br.sort_values('CR_Unicos', ascending=False).iloc[5:10].reset_index(drop=True)

# Sin Conversión
sc = p80_hotel_w18[p80_hotel_w18['Bookings']==0]
TOP['sin_conv'] = sc.sort_values('CR_Unicos', ascending=False).head(5).reset_index(drop=True)
TOP['sin_conv_extra'] = sc.sort_values('CR_Unicos', ascending=False).iloc[5:10].reset_index(drop=True)

# Por corp y por destino
TOP['corps'] = g_corp_w18.sort_values('CR_Unicos', ascending=False).head(5).reset_index(drop=True)
TOP['corps_10'] = g_corp_w18.sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)
TOP['destinos'] = g_destino_w18.sort_values('CR_Unicos', ascending=False).head(10).reset_index(drop=True)

# Severity por corporativo
TOP['sev_corp'] = g_corp_w18.sort_values('CR_Unicos', ascending=False).head(15).reset_index(drop=True)

# Menor Conv Rate (P80, BKGS>0)
men = p80_hotel_w18[p80_hotel_w18['Bookings']>0].sort_values('ConvRate').head(5)
TOP['menor_cv'] = men.reset_index(drop=True)

# Channels
TOP['channels'] = g_channel_w18.sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
TOP['grupos'] = g_grupo_w18.sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

# Tabs Eficacia (peores)
TAB_EF = {}
TAB_EF['destino']  = g_destino_w18[g_destino_w18['CR_Unicos']>500].sort_values('Eficacia').head(10).reset_index(drop=True)
TAB_EF['corp']     = g_corp_w18[g_corp_w18['CR_Unicos']>1000].sort_values('Eficacia').head(10).reset_index(drop=True)
TAB_EF['hotel']    = g_hotel_w18[g_hotel_w18['CR_Unicos']>200].sort_values('Eficacia').head(10).reset_index(drop=True)
TAB_EF['channel']  = g_channel_w18.sort_values('Eficacia').reset_index(drop=True)
TAB_EF['canasta']  = pd.DataFrame([
    {'Canasta':'B2C',      'Eficacia':M['B2C_w18']['eficacia']},
    {'Canasta':'B2B (OP)', 'Eficacia':M['B2B (OP)_w18']['eficacia']},
    {'Canasta':'CUG (UOP)','Eficacia':M['CUG (UOP)_w18']['eficacia']},
]).sort_values('Eficacia').reset_index(drop=True)

# Tabs ConvRate (peores)
TAB_CV = {}
TAB_CV['destino']  = g_destino_w18[(g_destino_w18['Bookings']>5) & (g_destino_w18['CR_Unicos']>500)].sort_values('ConvRate').head(10).reset_index(drop=True)
TAB_CV['corp']     = g_corp_w18[(g_corp_w18['Bookings']>5) & (g_corp_w18['CR_Unicos']>1000)].sort_values('ConvRate').head(10).reset_index(drop=True)
TAB_CV['hotel']    = g_hotel_w18[(g_hotel_w18['Bookings']>0) & (g_hotel_w18['CR_Unicos']>200)].sort_values('ConvRate').head(10).reset_index(drop=True)
TAB_CV['channel']  = g_channel_w18.sort_values('ConvRate').reset_index(drop=True)
TAB_CV['canasta']  = pd.DataFrame([
    {'Canasta':'B2C',      'ConvRate':M['B2C_w18']['conv_rate']},
    {'Canasta':'B2B (OP)', 'ConvRate':M['B2B (OP)_w18']['conv_rate']},
    {'Canasta':'CUG (UOP)','ConvRate':M['CUG (UOP)_w18']['conv_rate']},
]).sort_values('ConvRate').reset_index(drop=True)

# Datos por canasta
CANASTA = {}
for c, key in [('B2C','b2c'), ('B2B (OP)','op'), ('CUG (UOP)','cug')]:
    sub18 = cr_w18[cr_w18['DistributionCategory']==c]
    sub17 = cr_w17[cr_w17['DistributionCategory']==c]
    g_h = make_hotel_agg_cr(sub18)
    g_d = aggregate_cr(sub18, 'Destino')
    g_co = aggregate_cr(sub18, 'CorpName')
    g_ch = aggregate_cr(sub18, 'ExternalProviderName')
    g_grp = aggregate_cr(sub18, 'Grupo')
    p80 = pareto_p80(g_h, 'CR_Unicos')
    
    m18 = metrics_cr_global(sub18)
    m17 = metrics_cr_global(sub17)
    
    # Críticos: Eficacia en Crítica/Súper Crítica · pero solo casos con BKGS>0 (los BKGS=0 van a sin_conv)
    crit = p80[(p80['BandaEficacia'].isin(['Crítica','Súper Crítica'])) & (p80['Bookings']>0) & (p80['Eficacia']>0)].sort_values('CR_Unicos', ascending=False).head(10)
    bajo = p80[(p80['BandaConvRate'].isin(['Crítica','Revisar'])) & (p80['Bookings']>0)].sort_values('CR_Unicos', ascending=False).head(10)
    sin_c = p80[p80['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(10)
    
    # Tabs por canasta (los peores en eficacia, BKGS>0 para excluir Sin Conversión) · 10 items
    tt_dest = g_d[(g_d['CR_Unicos']>200) & (g_d['Bookings']>0) & (g_d['Eficacia']>0)].sort_values('Eficacia').head(10).reset_index(drop=True)
    tt_corp = g_co[(g_co['CR_Unicos']>500) & (g_co['Bookings']>0) & (g_co['Eficacia']>0)].sort_values('Eficacia').head(10).reset_index(drop=True)
    tt_hot = g_h[(g_h['CR_Unicos']>100) & (g_h['Bookings']>0) & (g_h['Eficacia']>0)].sort_values('Eficacia').head(10).reset_index(drop=True)
    tt_chan = g_ch[(g_ch['Bookings']>0) & (g_ch['Eficacia']>0)].sort_values('Eficacia').reset_index(drop=True)
    
    n_critica = (g_h['BandaEficacia'].isin(['Crítica','Súper Crítica'])).sum()
    
    # Severity por canasta (sobre P80 procesable)
    sev_ef_canasta = p80['BandaEficacia'].value_counts().reindex(
        ['Súper Crítica','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
    sev_cv_canasta = p80['BandaConvRate'].value_counts().reindex(
        ['Sin Conversión','Crítica','Revisar','Aceptable','Exitosa']).fillna(0).astype(int)
    
    # Alertas por canasta · peor hotel por Eficacia y peor por ConvRate
    alert_h_ef_pool = p80[(p80['Bookings']>0) & (p80['Eficacia']>0)]
    alert_h_ef = alert_h_ef_pool.sort_values('Eficacia').iloc[0] if len(alert_h_ef_pool)>0 else None
    alert_h_cv_pool = p80[(p80['Bookings']>0) & (p80['Eficacia']>0)]
    alert_h_cv = alert_h_cv_pool.sort_values('ConvRate').iloc[0] if len(alert_h_cv_pool)>0 else None
    
    # Worst destino · peor Eficacia y peor ConvRate
    alert_d_ef_pool = g_d[(g_d['CR_Unicos']>500) & (g_d['Bookings']>0) & (g_d['Eficacia']>0)]
    alert_d_ef = alert_d_ef_pool.sort_values('Eficacia').iloc[0] if len(alert_d_ef_pool)>0 else None
    alert_d_cv = alert_d_ef_pool.sort_values('ConvRate').iloc[0] if len(alert_d_ef_pool)>0 else None
    
    # Worst channel · peor Eficacia y peor ConvRate
    alert_c_ef_pool = g_ch[(g_ch['Bookings']>0) & (g_ch['Eficacia']>0)]
    alert_c_ef = alert_c_ef_pool.sort_values('Eficacia').iloc[0] if len(alert_c_ef_pool)>0 else None
    alert_c_cv = alert_c_ef_pool.sort_values('ConvRate').iloc[0] if len(alert_c_ef_pool)>0 else None
    
    CANASTA[key] = {
        'name': c, 'short': {'B2C':'B2C','B2B (OP)':'B2B Opaco','CUG (UOP)':'CUG'}[c],
        'm18': m18, 'm17': m17,
        'agg_hotel': g_h, 'agg_destino': g_d, 'agg_corp': g_co, 'agg_channel': g_ch, 'agg_grupo': g_grp,
        'p80': p80,
        'critic': crit.reset_index(drop=True),
        'bajo': bajo.reset_index(drop=True),
        'sin_conv': sin_c.reset_index(drop=True),
        'top_dest': tt_dest, 'top_corp': tt_corp, 'top_hot': tt_hot, 'top_chan': tt_chan,
        'n_critica': int(n_critica),
        'sev_ef': sev_ef_canasta.to_dict(),
        'sev_cv': sev_cv_canasta.to_dict(),
        'alert_h_ef': alert_h_ef, 'alert_h_cv': alert_h_cv,
        'alert_d_ef': alert_d_ef, 'alert_d_cv': alert_d_cv,
        'alert_c_ef': alert_c_ef, 'alert_c_cv': alert_c_cv,
    }

with open('cr_w18_data.pkl','wb') as f:
    pickle.dump({'M':M,'TOP':TOP,'TAB_EF':TAB_EF,'TAB_CV':TAB_CV,
                 'CANASTA':CANASTA,'sev_ef':sev_ef,'sev_cv':sev_cv,
                 'sev_ef_p80':sev_ef_p80,'sev_cv_p80':sev_cv_p80,
                 'g_hotel':g_hotel_w18,'p80_hotel':p80_hotel_w18,
                 'g_corp':g_corp_w18, 'g_channel':g_channel_w18, 'g_grupo':g_grupo_w18}, f)

print(f"=== CR W18 · Resumen Globales ===")
print(f"CR Únicos: {fmt_int(M['global_w18']['cr_unicos'])} (W17 {fmt_int(M['global_w17']['cr_unicos'])})")
print(f"Bookings: {fmt_int(M['global_w18']['bookings'])} (W17 {fmt_int(M['global_w17']['bookings'])})")
print(f"Eficacia: {fmt_pct(M['global_w18']['eficacia'],2)} (W17 {fmt_pct(M['global_w17']['eficacia'],2)})")
print(f"ConvRate: {fmt_pct(M['global_w18']['conv_rate'],3)} (W17 {fmt_pct(M['global_w17']['conv_rate'],3)})")
print(f"Hoteles P80: {len(p80_hotel_w18):,}")
print(f"Severity Eficacia (P80): {sev_ef_p80.to_dict()}")
print(f"Severity ConvRate (P80): {sev_cv_p80.to_dict()}")
