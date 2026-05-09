"""
calc_rnd v2 · lee directamente de Excel W18 + W17 · calcula WoW reales
"""
import pandas as pd, numpy as np, pickle, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from engine import banda_nodispo, banda_rpm

# ── Cargar datasets ───────────────────────────────────────────────
def load_rnd(path, week):
    df = pd.read_excel(path)
    if df.columns[0] != 'CorpName':
        df = df.rename(columns={df.columns[0]: 'CorpName'})
    df = df[df['DistributionCategory'].isin(['B2C','B2B (OP)','CUG (UOP)'])].copy()
    df['Hotel']   = df['Hotel'].astype(str).str.strip()
    df['CorpName']= df['CorpName'].astype(str).str.strip()
    df['Destino'] = df['Destino'].astype(str).str.strip()
    df['TraficoNoDispo'] = df['Trafico'] * df['%NoDispo']
    df['IPM'] = (df['gb_usd'] / df['Trafico'].replace(0,np.nan) * 1_000_000).fillna(0)
    df['ConvRate'] = (df['Bookings'] / df['Trafico'].replace(0,np.nan)).fillna(0)
    df['DemandaNoConvertida'] = df['TraficoNoDispo']
    print(f'  W{week}: {len(df):,} filas · {df["DistributionCategory"].value_counts().to_dict()}')
    return df

print('Cargando datasets...')
df18 = load_rnd('Dataset_RatesNoDispo_W18.xlsx', 18)
df17 = load_rnd('Dataset_RatesNoDispo_W17.xlsx', 17)

# ── Funciones de agregación ───────────────────────────────────────
def agg_hotel(df):
    g = df.groupby(['Hotel','CorpName','PaisDestino','Destino']).agg(
        Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
    ).reset_index()
    g['%NoDispo']            = (g['TraficoNoDispo']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['IPM']                 = (g['gb_usd']/g['Trafico'].replace(0,np.nan)*1_000_000).fillna(0)
    g['RPM']                 = g['IPM']
    g['ConvRate']            = (g['Bookings']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['DemandaNoConvertida'] = g['TraficoNoDispo']
    g['BandaNoDispo']        = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM']            = g['IPM'].apply(banda_rpm)
    return g

def agg_dim(df, col):
    g = df.groupby(col).agg(
        Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
    ).reset_index()
    g['%NoDispo'] = (g['TraficoNoDispo']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['IPM']      = (g['gb_usd']/g['Trafico'].replace(0,np.nan)*1_000_000).fillna(0)
    g['RPM']      = g['IPM']
    g['ConvRate'] = (g['Bookings']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['BandaNoDispo'] = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM']     = g['IPM'].apply(banda_rpm)
    return g

def metrics_global(df):
    t = df['Trafico'].sum(); nd = df['TraficoNoDispo'].sum()
    bk = df['Bookings'].sum(); gb = df['gb_usd'].sum()
    ipm = gb/t*1_000_000 if t else 0
    return {
        'trafico':t,'bookings':bk,'gb_usd':gb,
        'nodispo':nd/t if t else 0,'pct_nodispo':nd/t if t else 0,
        'ipm':ipm,'rpm':ipm,'conv_rate':bk/t if t else 0,'conversion':bk/t if t else 0,
        'banda_rpm':banda_rpm(ipm),'banda_nd':banda_nodispo(nd/t if t else 0),
        'banda_nodispo':banda_nodispo(nd/t if t else 0),
    }

# ── P80 global ────────────────────────────────────────────────────
print('Calculando P80...')
g_hotel_all = agg_hotel(df18).sort_values('Trafico', ascending=False)
cumsum = g_hotel_all['Trafico'].cumsum(); total = g_hotel_all['Trafico'].sum()
p80_hotel = g_hotel_all[cumsum <= total*0.80].copy()

# ── Agregados globales W17 para WoW ───────────────────────────────
g_hotel_w17 = agg_hotel(df17).rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17','RPM':'RPM_W17'})\
    [['Hotel','%NoDispo_W17','IPM_W17','RPM_W17']]
g_corp_w17  = agg_dim(df17,'CorpName').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})\
    [['CorpName','%NoDispo_W17','IPM_W17']]
g_dest_w17  = agg_dim(df17,'Destino').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})\
    [['Destino','%NoDispo_W17','IPM_W17']]
g_pais_w17  = agg_dim(df17,'PaisDestino').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})\
    [['PaisDestino','%NoDispo_W17','IPM_W17']]

# Enriquecer p80 con WoW
p80_hotel = p80_hotel.merge(g_hotel_w17, on='Hotel', how='left')
p80_hotel['NoDispo_WoW_pp'] = (p80_hotel['%NoDispo'] - p80_hotel['%NoDispo_W17']) * 100
p80_hotel['IPM_WoW_pp']     = p80_hotel['IPM'] - p80_hotel['IPM_W17']

# ── Métricas globales ─────────────────────────────────────────────
M = {'global_w18': metrics_global(df18), 'global_w17': metrics_global(df17)}
for cat in ['B2C','B2B (OP)','CUG (UOP)']:
    key = cat.replace(' (OP)','').replace(' (UOP)','').replace('(','').replace(')','').replace(' ','')
    m18 = metrics_global(df18[df18['DistributionCategory']==cat])
    m17 = metrics_global(df17[df17['DistributionCategory']==cat])
    m18['n_hoteles'] = len(p80_hotel)
    m17['n_hoteles'] = len(p80_hotel)
    M[f'B2C_w18']         = m18 if cat=='B2C' else M.get('B2C_w18', m18)
    M[f'B2C_w17']         = m17 if cat=='B2C' else M.get('B2C_w17', m17)
    M[f'B2B (OP)_w18']    = m18 if cat=='B2B (OP)' else M.get('B2B (OP)_w18', m18)
    M[f'B2B (OP)_w17']    = m17 if cat=='B2B (OP)' else M.get('B2B (OP)_w17', m17)
    M[f'CUG (UOP)_w18']   = m18 if cat=='CUG (UOP)' else M.get('CUG (UOP)_w18', m18)
    M[f'CUG (UOP)_w17']   = m17 if cat=='CUG (UOP)' else M.get('CUG (UOP)_w17', m17)
    M[f'B2B-OP_w18']      = M['B2B (OP)_w18']
    M[f'B2B-OP_w17']      = M['B2B (OP)_w17']
    M[f'CUG_w18']         = M['CUG (UOP)_w18']
    M[f'CUG_w17']         = M['CUG (UOP)_w17']

for k in M: M[k]['n_hoteles'] = len(p80_hotel)

# ── Severity ─────────────────────────────────────────────────────
BANDAS = ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica','Sin Conversión']
sev_nd  = {b: int((p80_hotel['BandaNoDispo']==b).sum()) for b in BANDAS}
sev_rpm = {b: int((p80_hotel['BandaRPM']==b).sum()) for b in BANDAS}

# ── Agregados dimensión global ────────────────────────────────────
g_hotel = agg_hotel(df18)
g_corp  = agg_dim(df18,'CorpName').merge(g_corp_w17, on='CorpName', how='left')
g_dest  = agg_dim(df18,'Destino').merge(g_dest_w17, on='Destino', how='left')
g_pais  = agg_dim(df18,'PaisDestino').merge(g_pais_w17, on='PaisDestino', how='left')
for g in [g_corp, g_dest, g_pais]:
    g['NoDispo_WoW_pp'] = (g['%NoDispo'] - g.get('%NoDispo_W17', g['%NoDispo'])) * 100

# ── TABs para KPI hero ────────────────────────────────────────────
def make_tab(df, col, sort_col, asc=False):
    return df.sort_values(sort_col, ascending=asc).head(10).reset_index(drop=True)

TAB_NoDispo = {
    'pais':    make_tab(g_pais,'PaisDestino','%NoDispo',False),
    'destino': make_tab(g_dest,'Destino','%NoDispo',False),
    'corp':    make_tab(g_corp,'CorpName','%NoDispo',False),
    'hotel':   make_tab(p80_hotel,'Hotel','%NoDispo',False),
    'canasta': pd.DataFrame([
        {'Canasta':'B2C',      **{k:v for k,v in M['B2C_w18'].items()}},
        {'Canasta':'B2B (OP)', **{k:v for k,v in M['B2B (OP)_w18'].items()}},
        {'Canasta':'CUG (UOP)',**{k:v for k,v in M['CUG (UOP)_w18'].items()}},
    ]).sort_values('pct_nodispo', ascending=False).reset_index(drop=True),
}


TAB_RPM = {
    'pais':    make_tab(g_pais,'PaisDestino','IPM',True),
    'destino': make_tab(g_dest,'Destino','IPM',True),
    'corp':    make_tab(g_corp,'CorpName','IPM',True),
    'hotel':   make_tab(p80_hotel,'Hotel','IPM',True),
    'canasta': TAB_NoDispo['canasta'],
}
# Alias RPM en TABs
for tab in [TAB_NoDispo, TAB_RPM]:
    for k in tab:
        t = tab[k]
        if 'IPM' in t.columns and 'RPM' not in t.columns:
            t['RPM'] = t['IPM']

# ── TOP global ────────────────────────────────────────────────────
proc = p80_hotel[p80_hotel['Bookings'] > 0]
no_conv = p80_hotel[p80_hotel['Bookings'] == 0]
top50_dnc  = proc.sort_values('TraficoNoDispo', ascending=False).head(50).reset_index(drop=True)
top50_br   = proc[proc['BandaRPM'].isin(['Crítica','Revisar'])].sort_values('Trafico', ascending=False).head(50).reset_index(drop=True)
top50_sc   = no_conv.sort_values('Trafico', ascending=False).head(50).reset_index(drop=True)

TOP = {
    'demanda_nc':       top50_dnc.head(10).reset_index(drop=True),
    'demanda_nc_extra': top50_dnc.iloc[10:].reset_index(drop=True),
    'bajo_rend':        top50_br.head(10).reset_index(drop=True),
    'bajo_rend_extra':  top50_br.iloc[10:].reset_index(drop=True),
    'sin_conv':         top50_sc.head(10).reset_index(drop=True),
    'sin_conv_extra':   top50_sc.iloc[10:].reset_index(drop=True),
    'corps':   g_corp.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'destinos':g_dest.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'paises':  g_pais.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'corps_10':g_corp.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'destinos_10':g_dest.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'paises_10':g_pais.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
}

# ── Canastas ─────────────────────────────────────────────────────
print('Calculando canastas...')
CANASTA_DATA = {}
for c_key, c_filter, c_name, c_short, c_weight in [
    ('B2C','B2C','B2C','B2C',0.1),
    ('B2B-OP','B2B (OP)','B2B Opaco','OP',0.6),
    ('CUG','CUG (UOP)','CUG','CUG',0.6),
]:
    sub18 = df18[df18['DistributionCategory']==c_filter].copy()
    sub17 = df17[df17['DistributionCategory']==c_filter].copy()
    gh = agg_hotel(sub18).sort_values('Trafico',ascending=False)
    cs = gh['Trafico'].cumsum(); tot = gh['Trafico'].sum()
    p80c = gh[cs<=tot*0.80].copy()
    # WoW por hotel en canasta
    gh17 = agg_hotel(sub17).rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})[['Hotel','%NoDispo_W17','IPM_W17']]
    p80c = p80c.merge(gh17, on='Hotel', how='left')
    p80c['NoDispo_WoW_pp'] = (p80c['%NoDispo'] - p80c['%NoDispo_W17']) * 100
    p80c['IPM_WoW_pp']     = p80c['IPM'] - p80c['IPM_W17']
    p80c['RPM'] = p80c['IPM']
    proc_c = p80c[p80c['Bookings']>0]
    nc_c   = p80c[p80c['Bookings']==0]
    sev_nd_c  = {b:int((p80c['BandaNoDispo']==b).sum()) for b in BANDAS}
    sev_rpm_c = {b:int((p80c['BandaRPM']==b).sum()) for b in BANDAS}
    ac = agg_dim(sub18,'CorpName').merge(
        agg_dim(sub17,'CorpName').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})[['CorpName','%NoDispo_W17','IPM_W17']],
        on='CorpName', how='left')
    ad = agg_dim(sub18,'Destino').merge(
        agg_dim(sub17,'Destino').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})[['Destino','%NoDispo_W17','IPM_W17']],
        on='Destino', how='left')
    ap = agg_dim(sub18,'PaisDestino').merge(
        agg_dim(sub17,'PaisDestino').rename(columns={'%NoDispo':'%NoDispo_W17','IPM':'IPM_W17'})[['PaisDestino','%NoDispo_W17','IPM_W17']],
        on='PaisDestino', how='left')
    top_dnc = proc_c.sort_values('TraficoNoDispo',ascending=False).head(50).reset_index(drop=True)
    top_br  = proc_c[proc_c['BandaRPM'].isin(['Crítica','Revisar'])].sort_values('Trafico',ascending=False).head(50).reset_index(drop=True)
    top_sc  = nc_c.sort_values('Trafico',ascending=False).head(50).reset_index(drop=True)
    m18c = metrics_global(sub18); m17c = metrics_global(sub17)
    m18c['n_hoteles'] = len(p80c); m17c['n_hoteles'] = len(p80c)
    c_data = {
        'name':c_name,'short':c_short,'filter':c_filter,'weight':c_weight,
        'agg_hotel':gh,'p80_hotel':p80c,'p80':p80c,
        'agg_corp':ac,'agg_dest':ad,'agg_pais':ap,
        'top_hot':    p80c.sort_values('%NoDispo',ascending=False).head(10).reset_index(drop=True),
        'top_hot_rpm':p80c[(p80c['Bookings']>0)&(p80c['RPM']>0)].sort_values('RPM').head(10).reset_index(drop=True),
        'top_dnc':top_dnc.head(10).reset_index(drop=True),'top_dnc_extra':top_dnc.iloc[10:].reset_index(drop=True),
        'top_br': top_br.head(10).reset_index(drop=True), 'top_br_extra': top_br.iloc[10:].reset_index(drop=True),
        'top_sc': top_sc.head(10).reset_index(drop=True), 'top_sc_extra': top_sc.iloc[10:].reset_index(drop=True),
        'demanda_nc':top_dnc.head(10),'demanda_nc_extra':top_dnc.iloc[10:].reset_index(drop=True),
        'bajo_rend':top_br.head(10), 'bajo_rend_extra': top_br.iloc[10:].reset_index(drop=True),
        'sin_conv':top_sc.head(10),  'sin_conv_extra':  top_sc.iloc[10:].reset_index(drop=True),
        'sev_nd':sev_nd_c,'sev_rpm':sev_rpm_c,
        'corps_10':ac.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
        'destinos_10':ad.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
        'paises_10':ap.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
        'm18':m18c,'m17':m17c,'tab_nd':{},
    }
    CANASTA_DATA[c_key] = c_data
    CANASTA_DATA[c_key.lower()] = c_data
    if c_key == 'B2B-OP': CANASTA_DATA['op'] = c_data
    if c_key == 'CUG': CANASTA_DATA['cug'] = c_data
    if c_key == 'B2C': CANASTA_DATA['b2c'] = c_data

# ── Guardar pickle ────────────────────────────────────────────────
D = {
    'df18':df18,'df17':df17,
    'M':M,'TOP':TOP,'CANASTA':CANASTA_DATA,
    'p80_hotel':p80_hotel,'g_hotel':g_hotel,
    'g_corp':g_corp,'g_dest':g_dest,'g_pais':g_pais,
    'sev_nd':sev_nd,'sev_rpm':sev_rpm,
    'sev_nd_p80':sev_nd,'sev_rpm_p80':sev_rpm,
    'g_hotel_w17':g_hotel_w17,'g_corp_w17':g_corp_w17,
    'g_dest_w17':g_dest_w17,'g_pais_w17':g_pais_w17,
    'TAB_NoDispo':TAB_NoDispo,'TAB_RPM':TAB_RPM,
}
with open('rnd_w18_data.pkl','wb') as f: pickle.dump(D, f)

t18=df18['Trafico'].sum(); nd18=df18['TraficoNoDispo'].sum()
t17=df17['Trafico'].sum(); nd17=df17['TraficoNoDispo'].sum()
pct18=nd18/t18*100; pct17=nd17/t17*100
print(f'✅ RND W18 calculado con deltas WoW')
print(f'   %NoDispo W18: {pct18:.2f}% | W17: {pct17:.2f}% | WoW: {pct18-pct17:+.2f}pp')
print(f'   Hoteles P80: {len(p80_hotel):,}')
