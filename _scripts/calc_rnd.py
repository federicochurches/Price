"""
calc_rnd v2 · lee directamente de Excel W19 + W18 · calcula WoW reales
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
    df['Hotel']   = df['Hotel'].astype(str).str.strip().str.replace(r'	','',regex=True).str.strip()
    df['CorpName']= df['CorpName'].astype(str).str.strip()
    df['Destino'] = df['Destino'].astype(str).str.strip()
    df['TraficoNoDispo'] = df['Trafico'] * df['%NoDispo']
    df['IPM'] = (df['gb_usd'] / df['Trafico'].replace(0,np.nan) * 1_000_000).fillna(0)
    df['ConvRate'] = (df['Bookings'] / df['Trafico'].replace(0,np.nan)).fillna(0)
    df['DemandaNoConvertida'] = df['TraficoNoDispo']
    print(f'  W{week}: {len(df):,} filas · {df["DistributionCategory"].value_counts().to_dict()}')
    return df

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
# Lee desde env vars (run_pipeline.py) o fallback a hardcodeado
WEEK     = os.getenv('WEEK', 'W20')
VOL_NUM  = os.getenv('VOL_NUM', '20')
PERIODO  = os.getenv('PERIODO', '11–17 may 2026')
MES_AÑO  = os.getenv('MES_AÑO', 'Mayo 2026')
FECHA_PUB = os.getenv('FECHA_PUB', 'LUNES 18 de Mayo de 2026')  # Día de publicación del reporte

# Derivar números de semana desde strings
WEEK_NUM = int(WEEK.replace('W', ''))
VOL_NUM_PREV = int(VOL_NUM) - 1
# ─────────────────────────────────────────────────────────────────────────────

print('Cargando datasets...')
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def _find_rnd(name):
    for d in [_SCRIPT_DIR, '/mnt/project', '/mnt/user-data/uploads']:
        p = os.path.join(d, name)
        if os.path.exists(p): return p
    raise FileNotFoundError(f'{name} no encontrado')
df18 = load_rnd(_find_rnd(f'Dataset_RatesNoDispo_W{WEEK_NUM}.xlsx'), WEEK_NUM)
df17 = load_rnd(_find_rnd(f'Dataset_RatesNoDispo_W{VOL_NUM_PREV}.xlsx'), VOL_NUM_PREV)

# ── Funciones de agregación ───────────────────────────────────────
def agg_hotel(df):
    g = df.groupby(['Hotel','CorpName','PaisDestino','Destino']).agg(
        Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
    ).reset_index()
    g['%NoDispo']            = (g['TraficoNoDispo']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['gb_usd_pos']          = g['gb_usd'].clip(lower=0)  # ignorar cancelaciones negativas
    g['IPM']                 = (g['gb_usd_pos']/g['Trafico'].replace(0,np.nan)*1_000_000).fillna(0)
    g['RPM']                 = g['IPM']
    g['ConvRate']            = (g['Bookings']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['DemandaNoConvertida'] = g['TraficoNoDispo']
    g['BandaNoDispo']        = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM']            = g.apply(lambda r: banda_rpm(r['IPM'], r['Bookings']), axis=1)
    return g

def agg_dim(df, col):
    g = df.groupby(col).agg(
        Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
        gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
    ).reset_index()
    g['%NoDispo'] = (g['TraficoNoDispo']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['IPM']      = (g['gb_usd'].clip(lower=0)/g['Trafico'].replace(0,np.nan)*1_000_000).fillna(0)
    g['RPM']      = g['IPM']
    g['ConvRate'] = (g['Bookings']/g['Trafico'].replace(0,np.nan)).fillna(0)
    g['BandaNoDispo'] = g['%NoDispo'].apply(banda_nodispo)
    g['BandaRPM']     = g.apply(lambda r: banda_rpm(r['IPM'], r['Bookings']), axis=1)
    return g

def metrics_global(df):
    t = df['Trafico'].sum(); nd = df['TraficoNoDispo'].sum()
    bk = df['Bookings'].sum()
    gb_pos = df['gb_usd'].clip(lower=0).sum()  # clip por fila, no por suma
    ipm = gb_pos/t*1_000_000 if t else 0
    gb = df['gb_usd'].sum()  # para compatibilidad
    return {
        'trafico':t,'bookings':bk,'gb_usd':gb,
        'nodispo':nd/t if t else 0,'pct_nodispo':nd/t if t else 0,
        'ipm':ipm,'rpm':ipm,'conv_rate':bk/t if t else 0,'conversion':bk/t if t else 0,
        'banda_rpm':banda_rpm(ipm),'banda_nd':banda_nodispo(nd/t if t else 0),
        'banda_nodispo':banda_nodispo(nd/t if t else 0),
    }

# ── P80 global ────────────────────────────────────────────────────
# ── FILTRO DE RELEVANCIA OPERACIONAL: MIN_TRAFICO = 50K (checkrates equivalente) ────
# Hoteles con tráfico mínimo = universo operacionalmente relevante
MIN_TRAFICO = 50000

df18 = df18[df18['Trafico'] >= MIN_TRAFICO].copy()
df17 = df17[df17['Trafico'] >= MIN_TRAFICO].copy() if len(df17) > 0 else df17

print('Calculando P90 (hoteles con Trafico >= 50K)...')
g_hotel_all = agg_hotel(df18).sort_values('Trafico', ascending=False)
cumsum = g_hotel_all['Trafico'].cumsum(); total = g_hotel_all['Trafico'].sum()
p80_hotel = g_hotel_all[cumsum <= total*0.90].copy()

# ── Agregados globales W18 para WoW ───────────────────────────────
g_hotel_w17 = agg_hotel(df17).rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18','RPM':'RPM_W18'})\
    [['Hotel','%NoDispo_W18','IPM_W18','RPM_W18']]
g_corp_w17  = agg_dim(df17,'CorpName').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})\
    [['CorpName','%NoDispo_W18','IPM_W18']]
g_dest_w17  = agg_dim(df17,'Destino').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})\
    [['Destino','%NoDispo_W18','IPM_W18']]
g_pais_w17  = agg_dim(df17,'PaisDestino').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})\
    [['PaisDestino','%NoDispo_W18','IPM_W18']]

# Enriquecer p80 con WoW
p80_hotel = p80_hotel.merge(g_hotel_w17, on='Hotel', how='left')
p80_hotel['NoDispo_WoW_pp'] = (p80_hotel['%NoDispo'] - p80_hotel['%NoDispo_W18']) * 100
p80_hotel['IPM_WoW_pp']     = p80_hotel['IPM'] - p80_hotel['IPM_W18']

# ── Métricas globales · basadas en P80 (metodología) ─────────────
# Las cards globales muestran métricas del P80, no del dataset completo
# Para W18: reconstruimos p80 equivalente por hoteles que también están en el p80 W19
hotel_p80_names = set(p80_hotel['Hotel'].unique())
df17_p80 = df17[df17['Hotel'].isin(hotel_p80_names)].copy()

M = {
    f'global_w{WEEK_NUM}': metrics_global(p80_hotel),  # P80 semana actual
    f'global_w{VOL_NUM_PREV}': metrics_global(df17_p80),   # P80 semana anterior
}
for cat in ['B2C','B2B (OP)','CUG (UOP)']:
    p80_cat_18 = p80_hotel[p80_hotel['DistributionCategory']==cat] if 'DistributionCategory' in p80_hotel.columns else df18[df18['DistributionCategory']==cat]
    # p80 no tiene DistributionCategory porque viene del agg_hotel — usar df18 filtrado al P80
    df18_p80_cat = df18[(df18['Hotel'].isin(hotel_p80_names)) & (df18['DistributionCategory']==cat)]
    df17_p80_cat = df17[(df17['Hotel'].isin(hotel_p80_names)) & (df17['DistributionCategory']==cat)]
    m18 = metrics_global(df18_p80_cat)
    m17 = metrics_global(df17_p80_cat)
    m18['n_hoteles'] = len(p80_hotel)
    m17['n_hoteles'] = len(p80_hotel)
    M[f'B2C_w{WEEK_NUM}']        = m18 if cat=='B2C'       else M.get(f'B2C_w{WEEK_NUM}', m18)
    M[f'B2C_w{VOL_NUM_PREV}']        = m17 if cat=='B2C'       else M.get(f'B2C_w{VOL_NUM_PREV}', m17)
    M[f'B2B (OP)_w{WEEK_NUM}']   = m18 if cat=='B2B (OP)'  else M.get(f'B2B (OP)_w{WEEK_NUM}', m18)
    M[f'B2B (OP)_w{VOL_NUM_PREV}']   = m17 if cat=='B2B (OP)'  else M.get(f'B2B (OP)_w{VOL_NUM_PREV}', m17)
    M[f'CUG (UOP)_w{WEEK_NUM}']  = m18 if cat=='CUG (UOP)' else M.get(f'CUG (UOP)_w{WEEK_NUM}', m18)
    M[f'CUG (UOP)_w{VOL_NUM_PREV}']  = m17 if cat=='CUG (UOP)' else M.get(f'CUG (UOP)_w{VOL_NUM_PREV}', m17)
    M[f'B2B-OP_w{WEEK_NUM}']     = M[f'B2B (OP)_w{WEEK_NUM}']
    M[f'B2B-OP_w{VOL_NUM_PREV}']     = M[f'B2B (OP)_w{VOL_NUM_PREV}']
    M[f'CUG_w{WEEK_NUM}']        = M[f'CUG (UOP)_w{WEEK_NUM}']
    M[f'CUG_w{VOL_NUM_PREV}']        = M[f'CUG (UOP)_w{VOL_NUM_PREV}']

for k in M: M[k]['n_hoteles'] = len(p80_hotel)

# ── Severity ─────────────────────────────────────────────────────
BANDAS = ['Exitosa','Aceptable','Revisar','Crítica','Súper Crítica','Sin Conversión']
sev_nd  = {b: int((p80_hotel['BandaNoDispo']==b).sum()) for b in BANDAS}
sev_rpm = {b: int((p80_hotel['BandaRPM']==b).sum()) for b in BANDAS}

# ── Agregados dimensión global ────────────────────────────────────
g_hotel = agg_hotel(df18)
# Agregados dimensión globales sobre P80 (hoteles que acumulan 80% tráfico)
df18_p80 = df18[df18['Hotel'].isin(hotel_p80_names)].copy()
df17_p80 = df17[df17['Hotel'].isin(hotel_p80_names)].copy()

g_corp  = agg_dim(df18_p80,'CorpName').merge(g_corp_w17, on='CorpName', how='left')
g_dest  = agg_dim(df18_p80,'Destino').merge(g_dest_w17, on='Destino', how='left')
g_pais  = agg_dim(df18_p80,'PaisDestino').merge(g_pais_w17, on='PaisDestino', how='left')
# Drop duplicados post-merge
for g in [g_corp, g_dest, g_pais]:
    g.drop_duplicates(subset=[g.columns[0]], keep='first', inplace=True)
    g.reset_index(drop=True, inplace=True)
    g['NoDispo_WoW_pp'] = (g['%NoDispo'] - g.get('%NoDispo_W18', g['%NoDispo'])) * 100
    if 'IPM_W18' in g.columns and 'IPM_WoW_pp' not in g.columns:
        g['IPM_WoW_pp'] = g['IPM'] - g['IPM_W18']

# ── TABs para KPI hero ────────────────────────────────────────────
def make_tab(df, col, sort_col, asc=False, min_ipm=False, min_trafico=None):
    sub = df.copy()
    if min_ipm:
        sub = sub[sub['IPM'] > 0]
    if min_trafico:
        sub = sub[sub['Trafico'] >= min_trafico]
    return sub.sort_values(sort_col, ascending=asc).head(100).reset_index(drop=True)

# Umbral mínimo de tráfico para destino y país (evita outliers de bajo volumen)
# Corp: sin filtro de tráfico — mismo universo que pestaña "Por Corporativo" del Excel
MIN_TRAFICO_DIM = 500_000

TAB_NoDispo = {
    'pais':    make_tab(g_pais,'PaisDestino','%NoDispo',False, min_trafico=MIN_TRAFICO_DIM),
    'destino': make_tab(g_dest,'Destino','%NoDispo',False, min_trafico=MIN_TRAFICO_DIM),
    'corp':    make_tab(g_corp,'CorpName','%NoDispo',False),
    'hotel':   make_tab(p80_hotel,'Hotel','%NoDispo',False),
    'canasta': pd.DataFrame([
        {'Canasta':'B2C',      **{k:v for k,v in M[f'B2C_w{WEEK_NUM}'].items()}},
        {'Canasta':'B2B (OP)', **{k:v for k,v in M[f'B2B (OP)_w{WEEK_NUM}'].items()}},
        {'Canasta':'CUG (UOP)',**{k:v for k,v in M[f'CUG (UOP)_w{WEEK_NUM}'].items()}},
    ]).sort_values('pct_nodispo', ascending=False).reset_index(drop=True),
}

TAB_RPM = {
    'pais':    make_tab(g_pais,'PaisDestino','IPM',True, min_ipm=True, min_trafico=MIN_TRAFICO_DIM),
    'destino': make_tab(g_dest,'Destino','IPM',True, min_ipm=True, min_trafico=MIN_TRAFICO_DIM),
    'corp':    make_tab(g_corp,'CorpName','IPM',True, min_ipm=True),
    'hotel':   make_tab(p80_hotel,'Hotel','IPM',True, min_ipm=True),
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
    'demanda_nc':       top50_dnc.head(100).reset_index(drop=True),
    'demanda_nc_extra': top50_dnc.iloc[10:].reset_index(drop=True),
    'bajo_rend':        top50_br.head(100).reset_index(drop=True),
    'bajo_rend_extra':  top50_br.iloc[10:].reset_index(drop=True),
    'sin_conv':         top50_sc.head(100).reset_index(drop=True),
    'sin_conv_extra':   top50_sc.iloc[10:].reset_index(drop=True),
    'corps':   g_corp.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'destinos':g_dest.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'paises':  g_pais.sort_values('Trafico',ascending=False).head(10).reset_index(drop=True),
    'corps_10':g_corp.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
    'destinos_10':g_dest.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
    'paises_10':g_pais.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
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
    p80c = gh[cs<=tot*0.90].copy()
    # WoW por hotel en canasta
    gh17 = agg_hotel(sub17).rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})[['Hotel','%NoDispo_W18','IPM_W18']]
    p80c = p80c.merge(gh17, on='Hotel', how='left')
    p80c['NoDispo_WoW_pp'] = (p80c['%NoDispo'] - p80c['%NoDispo_W18']) * 100
    p80c['IPM_WoW_pp']     = p80c['IPM'] - p80c['IPM_W18']
    p80c['RPM'] = p80c['IPM']
    proc_c = p80c[p80c['Bookings']>0]
    nc_c   = p80c[p80c['Bookings']==0]
    sev_nd_c  = {b:int((p80c['BandaNoDispo']==b).sum()) for b in BANDAS}
    sev_rpm_c = {b:int((p80c['BandaRPM']==b).sum()) for b in BANDAS}
    # Dimensiones calculadas sobre el P80 de la canasta
    p80c_hotels = set(p80c['Hotel'].unique())
    sub18_p80 = sub18[sub18['Hotel'].isin(p80c_hotels)].copy()
    sub17_p80 = sub17[sub17['Hotel'].isin(p80c_hotels)].copy()
    ac = agg_dim(sub18_p80,'CorpName').merge(
        agg_dim(sub17_p80,'CorpName').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})[['CorpName','%NoDispo_W18','IPM_W18']],
        on='CorpName', how='left')
    ad = agg_dim(sub18_p80,'Destino').merge(
        agg_dim(sub17_p80,'Destino').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})[['Destino','%NoDispo_W18','IPM_W18']],
        on='Destino', how='left')
    ap = agg_dim(sub18_p80,'PaisDestino').merge(
        agg_dim(sub17_p80,'PaisDestino').rename(columns={'%NoDispo':'%NoDispo_W18','IPM':'IPM_W18'})[['PaisDestino','%NoDispo_W18','IPM_W18']],
        on='PaisDestino', how='left')
    # Drop duplicados post-merge
    for g in [ac, ad, ap]:
        g.drop_duplicates(subset=[g.columns[0]], keep='first', inplace=True)
        g.reset_index(drop=True, inplace=True)
        g['NoDispo_WoW_pp'] = (g['%NoDispo'] - g.get('%NoDispo_W18', g['%NoDispo'])) * 100
        if 'IPM_W18' in g.columns:
            g['IPM_WoW_pp'] = g['IPM'] - g['IPM_W18']
    top_dnc = proc_c.sort_values('TraficoNoDispo',ascending=False).head(50).reset_index(drop=True)
    top_br  = proc_c[proc_c['BandaRPM'].isin(['Crítica','Revisar'])].sort_values('Trafico',ascending=False).head(50).reset_index(drop=True)
    top_sc  = nc_c.sort_values('Trafico',ascending=False).head(50).reset_index(drop=True)
    m18c = metrics_global(sub18_p80); m17c = metrics_global(sub17_p80)
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
        'demanda_nc':top_dnc.head(100),'demanda_nc_extra':top_dnc.iloc[10:].reset_index(drop=True),
        'bajo_rend':top_br.head(100), 'bajo_rend_extra': top_br.iloc[10:].reset_index(drop=True),
        'sin_conv':top_sc.head(100),  'sin_conv_extra':  top_sc.iloc[10:].reset_index(drop=True),
        'sev_nd':sev_nd_c,'sev_rpm':sev_rpm_c,
        'corps_10':ac.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
        'destinos_10':ad.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
        'paises_10':ap.sort_values('Trafico',ascending=False).head(100).reset_index(drop=True),
        'm18':m18c,'m17':m17c,'tab_nd':{},
    }
    CANASTA_DATA[c_key] = c_data
    CANASTA_DATA[c_key.lower()] = c_data
    if c_key == 'B2B-OP': CANASTA_DATA['op'] = c_data
    if c_key == 'CUG': CANASTA_DATA['cug'] = c_data
    if c_key == 'B2C': CANASTA_DATA['b2c'] = c_data

# ── Guardar pickle ────────────────────────────────────────────────
D = {
    'WEEK': WEEK,
    'VOL_NUM': VOL_NUM,
    'PERIODO': PERIODO,
    'MES_AÑO': MES_AÑO,
    'FECHA_PUB': FECHA_PUB,
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
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'rnd_w{VOL_NUM}_data.pkl'),'wb') as f: pickle.dump(D, f)

t18=df18['Trafico'].sum(); nd18=df18['TraficoNoDispo'].sum()
t17=df17['Trafico'].sum(); nd17=df17['TraficoNoDispo'].sum()
pct18=nd18/t18*100 if t18>0 else 0
pct17=nd17/t17*100 if t17>0 else 0
print(f'✅ RND W{VOL_NUM} calculado con deltas WoW')
print(f'   %NoDispo W19: {pct18:.2f}% | W18: {pct17:.2f}% | WoW: {pct18-pct17:+.2f}pp')
print(f'   Hoteles P80: {len(p80_hotel):,}')
