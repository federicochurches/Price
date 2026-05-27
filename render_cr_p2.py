"""
render_cr_p2.py · W21+ · Modelo demo data-driven
Genera: part2_cr.html
Estructura: filter-bar + secciones HTML vacías + <script> con JSON real W21
Sin: Análisis por hotel estático, Análisis por dimensión, Análisis por canasta
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, pandas as pd, numpy as np
from engine import banda_eficacia, banda_convrate
from render_helpers import clean_hotel_name, BANDA_COLORS, fmt_pct2, fmt_int_es, fmt_big

# ── Config ────────────────────────────────────────────────────────────────────
with open(os.getenv('PICKLE_CR', 'cr_w21_data.pkl'), 'rb') as f:
    D = pickle.load(f)

VOL_NUM   = D.get('VOL_NUM', '21')
WEEK_NUM  = int(VOL_NUM)
WEEK_PREV = WEEK_NUM - 1
PERIODO   = D.get('PERIODO', '18-24 may 2026')

M        = D['M']
CANASTA  = D['CANASTA']
p80      = D['p80_hotel'].copy()
g_corp   = D['g_corp']
g_channel= D['g_channel']
g_hotel  = D['g_hotel']
sev_ef   = dict(D['sev_ef_p80'])
sev_cv   = dict(D['sev_cv_p80'])

# WoW lookups
g_hotel_w17 = D.get('g_hotel_w17')
g_corp_w17  = D.get('g_corp_w17')
g_dest_w17  = D.get('g_dest_w17')
g_channel_w17 = D.get('g_channel_w17')

hotel_channel_map = D.get('hotel_channel_map', {})
_hcm_clean = {clean_hotel_name(k): v for k, v in hotel_channel_map.items()} if hotel_channel_map else {}

p80['Hotel'] = p80['Hotel'].apply(clean_hotel_name)
if _hcm_clean and 'Channel' not in p80.columns:
    p80['Channel'] = p80['Hotel'].map(_hcm_clean).fillna('—')

# Enriquecer p80 con WoW de Eficacia y ConvRate desde TAB_EF/TAB_CV
_tab_ef_h = D.get('TAB_EF', {}).get('hotel')
_tab_cv_h = D.get('TAB_CV', {}).get('hotel')
if _tab_ef_h is not None and 'Eficacia_WoW_pp' in _tab_ef_h.columns:
    _ef_wow = _tab_ef_h[['Hotel','Eficacia_WoW_pp']].copy()
    _ef_wow['Hotel'] = _ef_wow['Hotel'].apply(clean_hotel_name)
    _ef_wow = _ef_wow.drop_duplicates('Hotel')
    p80 = p80.merge(_ef_wow, on='Hotel', how='left')
if _tab_cv_h is not None and 'ConvRate_WoW_pp' in _tab_cv_h.columns:
    _cv_wow = _tab_cv_h[['Hotel','ConvRate_WoW_pp']].copy()
    _cv_wow['Hotel'] = _cv_wow['Hotel'].apply(clean_hotel_name)
    _cv_wow = _cv_wow.drop_duplicates('Hotel')
    p80 = p80.merge(_cv_wow, on='Hotel', how='left')

# Agregar CR_Unicos_WoW_pp si no existe (desde p80_hotel enriquecido)
if 'CR_Unicos_WoW_pp' not in p80.columns and 'CR_Unicos_WoW_pp' in D['p80_hotel'].columns:
    _cr_wow = D['p80_hotel'][['Hotel','CR_Unicos_WoW_pp']].copy()
    _cr_wow['Hotel'] = _cr_wow['Hotel'].apply(clean_hotel_name)
    _cr_wow = _cr_wow.drop_duplicates('Hotel')
    p80 = p80.merge(_cr_wow, on='Hotel', how='left')

# ── Helpers ───────────────────────────────────────────────────────────────────
def es_pct(v): return f'{v*100:.2f}%'.replace('.', ',')
def es_int(v): return f'{int(v):,}'.replace(',', '.')
def es_pct2(v): return f'{v:.2f}%'.replace('.', ',') if isinstance(v, float) else str(v)

def banda_colors(banda):
    bc = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
    return bc['bg'], bc['fg']

def wow_arrow(pp):
    if pp is None or (isinstance(pp, float) and np.isnan(pp)):
        return '—'
    if pp > 0: return f'▲{abs(pp):.1f}'.replace('.', ',')
    if pp < 0: return f'▼{abs(pp):.1f}'.replace('.', ',')
    return '—'

def wow_arrow_abs(delta):
    """WoW para tráfico (número absoluto, sin unidad pp). delta = diferencia real."""
    if delta is None or (isinstance(delta, float) and np.isnan(delta)):
        return '—'
    val = abs(delta)
    # Formatear como entero con puntos de miles
    formatted = f'{int(val):,}'.replace(',', '.')
    if delta > 0: return f'▲{formatted}'
    if delta < 0: return f'▼{formatted}'
    return '—'

def build_hotel_row(row, ef_col='Eficacia', cv_col='ConvRate',
                    cr_col='CR_Unicos', band_col='BandaEficacia', wow_col='Eficacia_WoW_pp',
                    wow_cv_col='ConvRate_WoW_pp', wow_cr_col='CR_Unicos_WoW_pp'):
    """Construye fila: [nombre, bbg, bfg, banda, CR, ef, cv, wow_up, wow_ef_str, wow_cv_str, wow_cr_str]"""
    name  = clean_hotel_name(str(row.get('Hotel', row.get('CorpName', '?'))))[:60]
    banda = row.get(band_col, 'Sin Conversión')
    bbg, bfg = banda_colors(banda)
    cr_val = row.get(cr_col, 0)
    cr    = fmt_big(float(cr_val)) if cr_val and not (isinstance(cr_val, float) and np.isnan(cr_val)) else '0'
    ef    = es_pct(row.get(ef_col, 0))
    cv    = es_pct(row.get(cv_col, 0))
    # WoW Eficacia
    wow_pp = row.get(wow_col)
    if wow_pp is None or (isinstance(wow_pp, float) and np.isnan(wow_pp)):
        wow_up = None; wow_ef_str = '—'
    else:
        wow_up = bool(wow_pp >= 0); wow_ef_str = wow_arrow(wow_pp)
    # WoW ConvRate
    wow_cv_pp = row.get(wow_cv_col)
    if wow_cv_pp is None or (isinstance(wow_cv_pp, float) and np.isnan(wow_cv_pp)):
        wow_cv_str = '—'
    else:
        wow_cv_str = wow_arrow(wow_cv_pp)
    # WoW CR_Unicos (tráfico)
    wow_cr_pp = row.get(wow_cr_col)
    if wow_cr_pp is None or (isinstance(wow_cr_pp, float) and np.isnan(wow_cr_pp)):
        wow_cr_str = '—'
    else:
        # CR_Unicos_WoW_pp = (cr - cr_w17)*100 → dividir por 100 = delta real
        wow_cr_str = wow_arrow_abs(wow_cr_pp / 100)
    return [name, bbg, bfg, banda, cr, ef, cv, wow_up, wow_ef_str, wow_cv_str, wow_cr_str]

def sev_badge_html(banda):
    bbg, bfg = banda_colors(banda)
    return (f'<b class="sev-badge" style="background:{bbg};color:{bfg};'
            f'font-size:8px;padding:2px 6px;text-transform:uppercase;'
            f'outline:1px solid rgba(0,0,0,.12);">{banda}</b>')

# ── Construir CR_CV[canasta] ──────────────────────────────────────────────────
def build_cr_cv():
    """Retorna KPIs + datos de hoteles para CR_CV."""
    result = {}
    canasta_map = {'global': ('global', WEEK_NUM),
                   'b2c':    ('B2C', WEEK_NUM),
                   'op':     ('B2B (OP)', WEEK_NUM),
                   'cug':    ('CUG (UOP)', WEEK_NUM)}
    # Colores por canasta
    canasta_col = {'global': '#333132', 'b2c': '#EA0074', 'op': '#FCB000', 'cug': '#4FC3F4'}

    for key, (m_key, wn) in canasta_map.items():
        if key == 'global':
            m = M.get(f'global_w{wn}', {})
        else:
            m = M.get(f'{m_key}_w{wn}', {})
        ef    = m.get('eficacia', 0)
        cv    = m.get('conv_rate', 0)
        banda = banda_eficacia(ef)
        bbg, bfg = banda_colors(banda)
        
        cr_unicos  = m.get('cr_unicos', 0)
        cr_prev    = M.get(f'{m_key}_w{int(wn)-1}', {}).get('cr_unicos', 0) if key != 'global' else M.get(f'global_w{int(wn)-1}', {}).get('cr_unicos', 0)
        traf_wow   = round(((cr_unicos - cr_prev) / cr_prev * 100), 1) if cr_prev else None
        banda_cv_v = banda_convrate(cv, int(m.get('bookings', 1)))
        bbg_cv, bfg_cv = banda_colors(banda_cv_v)

        # Valores semana anterior para WoW en cards AR
        wn_prev = int(wn) - 1
        m_prev = M.get(f'global_w{wn_prev}', {}) if key == 'global' else M.get(f'{m_key}_w{wn_prev}', {})
        ef_prev = m_prev.get('eficacia', None)
        cv_prev = m_prev.get('conv_rate', None)

        result[key] = {
            'ef':      es_pct(ef),
            'cv':      es_pct(cv),
            'ef_prev': es_pct(ef_prev) if ef_prev is not None else None,
            'cv_prev': es_pct(cv_prev) if cv_prev is not None else None,
            'ef_wow':  round((ef - ef_prev) * 100, 2) if ef_prev is not None else None,
            'cv_wow':  round((cv - cv_prev) * 100, 2) if cv_prev is not None else None,
            'band':    banda,
            'bbg':     bbg,
            'bfg':     bfg,
            'band_cv': banda_cv_v,
            'bbg_cv':  bbg_cv,
            'bfg_cv':  bfg_cv,
            'col':     canasta_col[key],
            'vol':     f'{int(cr_unicos/1000)}K' if cr_unicos >= 1000 else str(cr_unicos),
            'trafico': fmt_int_es(int(cr_unicos)),
            'traf_wow': traf_wow,
            'kv_id':   f'w{wn}-kv-ef',
            'kv2_id':  f'w{wn}-kv-cv',
            'hist_id': f'w{wn}-hist-ef',
            'hist2_id':f'w{wn}-hist-cv',
        }
    
    return result

# ── Construir CR_D[canasta] ───────────────────────────────────────────────────
def build_canasta_data(key, df_hotel, m18, m17, sev_ef_c, sev_cv_c,
                       g_corp_c, g_dest_c, n_p80, g_channel_c=None, g_dest_local=None):
    """Construye {re, hotels, dims, plan, co} para una canasta CR."""

    ef   = m18.get('eficacia', 0)
    cv   = m18.get('conv_rate', 0)
    ef17 = m17.get('eficacia', 0)
    cv17 = m17.get('conv_rate', 0)
    ef_wow = (ef - ef17) * 100
    cv_wow = (cv - cv17) * 100
    banda_ef = banda_eficacia(ef)
    banda_cv = banda_convrate(cv, m18.get('bookings', 1))

    n_crit = int(sev_ef_c.get('Crítica', 0) + sev_ef_c.get('Súper Crítica', 0))
    n_sc   = int(sev_cv_c.get('Sin Conversión', 0))
    n_cv_crit = int(sev_cv_c.get('Crítica', 0))
    cr_tot = int(m18.get('cr_unicos', 0))

    # Peor hotel Eficacia
    df_w  = df_hotel[df_hotel['Bookings'] > 0].copy() if 'Bookings' in df_hotel.columns else df_hotel.copy()
    df_ef = df_w.sort_values('Eficacia', ascending=True)
    df_cv = df_w.sort_values('ConvRate', ascending=True)

    worst_ef_name = clean_hotel_name(str(df_ef.iloc[0]['Hotel'])) if len(df_ef) else '—'
    worst_ef_val  = es_pct(df_ef.iloc[0]['Eficacia']) if len(df_ef) else '—'
    worst_ef_cr   = es_int(df_ef.iloc[0]['CR_Unicos']) if len(df_ef) else '—'

    worst_cv_name = clean_hotel_name(str(df_cv.iloc[0]['Hotel'])) if len(df_cv) else '—'
    worst_cv_val  = es_pct(df_cv.iloc[0]['ConvRate']) if len(df_cv) else '—'
    worst_cv_cr   = es_int(df_cv.iloc[0]['CR_Unicos']) if len(df_cv) else '—'

    # Top corp por CR
    top_corp = g_corp_c.sort_values('CR_Unicos', ascending=False).iloc[0] if len(g_corp_c) else None
    top_corp_name = str(top_corp['CorpName']) if top_corp is not None else '—'
    top_corp_ef   = es_pct(top_corp['Eficacia']) if top_corp is not None else '—'
    top_corp_cr   = es_int(top_corp['CR_Unicos']) if top_corp is not None else '—'

    # Resumen ejecutivo (10 bullets)
    label = key.upper().replace('OP', 'Opaco').replace('CUG', 'Ultra Opaco').replace('B2C', 'B2C')
    sfx   = f' {label}' if key != 'global' else ' global'
    re_items = [
        {'n': es_pct(ef),
         't': f'Eficacia{sfx} · {sev_badge_html(banda_ef)}',
         'd': f'Target ≥ 97% · {"mejora" if ef_wow>=0 else "cae"} {wow_arrow(ef_wow)} WoW.'},
        {'n': es_pct(cv),
         't': f'Conv Rate{sfx} · {sev_badge_html(banda_cv)}',
         'd': f'{"Mejora" if cv_wow>=0 else "Cae"} {wow_arrow(cv_wow)} vs sem. ant.'},
        {'n': str(n_crit),
         't': f'Hoteles{sfx} {sev_badge_html("Crítica")}+',
         'd': f'{round(n_crit/n_p80*100,1):.0f}% del P80.'.replace('.', ',')},
        {'n': str(n_sc),
         't': f'Hoteles{sfx} {sev_badge_html("Sin Conversión")}',
         'd': f'{round(n_sc/n_p80*100,1):.0f}% sin convertir.'.replace('.', ',')},
        {'n': str(n_cv_crit),
         't': f'ConvRate {sev_badge_html("Crítica")}{sfx}',
         'd': 'ConvRate < 0,8%.'},
        {'n': worst_ef_val,
         't': f'{worst_ef_name} · peor Eficacia',
         'd': f'{worst_ef_cr} CR.'},
        {'n': top_corp_cr,
         't': f'{top_corp_name} · líder volumen',
         'd': f'{top_corp_ef}.'},
        {'n': worst_cv_val,
         't': f'{worst_cv_name} · peor ConvRate',
         'd': f'{worst_cv_cr} CR.'},
        {'n': str(int(sev_ef_c.get('Sin Conversión', n_sc))),
         't': f'Sin Conversión #1 · {df_hotel.sort_values("CR_Unicos",ascending=False).iloc[0]["Hotel"][:30] if len(df_hotel) else "—"}' if 'Sin Conversión' in sev_ef_c else f'Hoteles Sin Conversión{sfx}',
         'd': f'Cohorte estructural.'},
        {'n': str(n_p80),
         't': f'Hoteles P80 analizados',
         'd': f'W{VOL_NUM}.'},
    ]

    # Hotels rows — 4 tabs separados
    def hotel_rows_from(df):
        return [build_hotel_row(r, wow_col='Eficacia_WoW_pp') for _, r in df.iterrows()]

    # Críticos: Eficacia < 93% (Crítica + Súper Crítica), con bookings, top 10 Eficacia ASC
    df_crit = df_w[df_w['BandaEficacia'].isin(['Crítica','Súper Crítica'])].sort_values('Eficacia', ascending=True).head(100)
    # Bajo Rendimiento: Eficacia Revisar o Aceptable, con bookings
    df_br   = df_w[df_w['BandaEficacia'].isin(['Revisar','Aceptable'])].sort_values('Eficacia', ascending=True).head(100)
    # Sin Conversión: bookings = 0
    df_sc   = df_hotel[df_hotel['Bookings']==0].sort_values('CR_Unicos', ascending=False).head(100)
    # Menor ConvRate: con bookings, orden ConvRate ASC
    df_cv   = df_w.sort_values('ConvRate', ascending=True).head(100)

    hotel_rows      = hotel_rows_from(df_crit)  # default = Críticos
    hotels_crit_rows = hotel_rows_from(df_crit)
    hotels_br_rows   = hotel_rows_from(df_br)
    hotels_sc_rows   = hotel_rows_from(df_sc)
    hotels_cv_rows   = hotel_rows_from(df_cv)

    df_crit_top = df_crit  # para el plan de acción

    # Dims rows (por Corp, top 10 Eficacia ASC)
    dim_rows = []
    g_sort = g_corp_c.sort_values('Eficacia', ascending=True).head(100)
    for _, row in g_sort.iterrows():
        name  = str(row['CorpName'])[:60]
        banda = row.get('BandaEficacia', banda_eficacia(row['Eficacia']))
        bbg, bfg = banda_colors(banda)
        cr    = es_int(row['CR_Unicos'])
        ef    = es_pct(row['Eficacia'])
        cv    = es_pct(row['ConvRate'])
        wow_pp = None
        if g_corp_w17 is not None and 'CorpName' in g_corp_w17.columns:
            match = g_corp_w17[g_corp_w17['CorpName'] == row['CorpName']]
            if len(match):
                wow_pp = (row['Eficacia'] - match.iloc[0]['Eficacia_W17']) * 100
        wow_up  = None if wow_pp is None else bool(wow_pp >= 0)
        wow_str = wow_arrow(wow_pp)
        dim_rows.append([name, bbg, bfg, banda, cr, ef, cv, wow_up, wow_str, '—', '—'])

    # Dims rows por Destino (top 10 Eficacia ASC) — con WoW de tráfico
    dest_rows = []
    g_dest = None
    # Usar destinos por canasta si disponible, sino calcular desde df_hotel
    if g_dest_local is not None and len(g_dest_local) > 0:
        g_dest = g_dest_local.copy()
        if 'Eficacia' not in g_dest.columns and 'Successful' in g_dest.columns:
            g_dest['Eficacia'] = g_dest['Successful'] / g_dest['CR_Unicos'].replace(0,1)
        if 'ConvRate' not in g_dest.columns and 'Bookings' in g_dest.columns:
            g_dest['ConvRate'] = g_dest['Bookings'] / g_dest['CR_Unicos'].replace(0,1)
    elif 'Destino' in df_hotel.columns:
        g_dest = df_hotel.groupby('Destino').agg(
            CR_Unicos=('CR_Unicos','sum'), Successful=('Successful','sum'),
            Bookings=('Bookings','sum')).reset_index()
        g_dest['Eficacia'] = g_dest['Successful'] / g_dest['CR_Unicos'].replace(0,1)
        g_dest['ConvRate'] = g_dest['Bookings'] / g_dest['CR_Unicos'].replace(0,1)
        if g_dest_w17 is not None:
            g_dest = g_dest.merge(g_dest_w17[['Destino','CR_Unicos_W17']], on='Destino', how='left')
            g_dest['CR_Unicos_WoW_pp'] = (g_dest['CR_Unicos'] - g_dest['CR_Unicos_W17']) * 100
    if g_dest is not None and len(g_dest) > 0:
        for _, row in g_dest.sort_values('Eficacia', ascending=True).head(100).iterrows():
            banda = banda_eficacia(row['Eficacia'])
            bbg, bfg = banda_colors(banda)
            wow_cr = row.get('CR_Unicos_WoW_pp')
            wow_cr_str = wow_arrow_abs(wow_cr / 100) if wow_cr is not None and not (isinstance(wow_cr, float) and np.isnan(wow_cr)) else '—'
            dest_rows.append([str(row['Destino']).replace(' Area','').replace(' area','')[:55], bbg, bfg, banda,
                              es_int(row['CR_Unicos']), es_pct(row['Eficacia']),
                              es_pct(row['ConvRate']), None, '—', '—', wow_cr_str])

    # Dims rows por Canal — split Producto Propio / Third Party — con WoW de tráfico
    PROPIO_SET = {'DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees'}
    THIRD_SET  = {'Expedia','HotelBeds','Hotel Unico','Travelgate','Hotel Unico V2'}
    chan_rows = []
    chans_pp  = []
    chans_tp  = []
    
    # Usar canal por canasta si disponible, sino el global
    g_chan_local = (g_channel_c.copy() if g_channel_c is not None and len(g_channel_c) > 0
                   else (g_channel.copy() if g_channel is not None and len(g_channel) else None))
    
    if g_chan_local is not None and len(g_chan_local):
        # Merge WoW si disponible
        if g_channel_w17 is not None:
            g_chan_local = g_chan_local.merge(g_channel_w17[['ExternalProviderName','CR_Unicos_W17']], on='ExternalProviderName', how='left')
            g_chan_local['CR_Unicos_WoW_pp'] = (g_chan_local['CR_Unicos'] - g_chan_local['CR_Unicos_W17']) * 100
        for _, row in g_chan_local.sort_values('Eficacia', ascending=True).iterrows():
            banda = row.get('BandaEficacia', banda_eficacia(row['Eficacia']))
            bbg, bfg = banda_colors(banda)
            wow_cr = row.get('CR_Unicos_WoW_pp')
            # CR_Unicos_WoW_pp = (cr - cr_w17)*100 → dividir por 100 = delta real
            wow_cr_str = wow_arrow_abs(wow_cr / 100) if wow_cr is not None and not (isinstance(wow_cr, float) and np.isnan(wow_cr)) else '—'
            r = [str(row['ExternalProviderName'])[:45], bbg, bfg, banda,
                 es_int(row['CR_Unicos']), es_pct(row['Eficacia']),
                 es_pct(row['ConvRate']), None, '—', '—', wow_cr_str]
            chan_rows.append(r)
            if row['ExternalProviderName'] in THIRD_SET:
                chans_tp.append(r)
            else:
                chans_pp.append(r)

    # Catálogo canónico — channels que siempre deben aparecer
    CATALOG_PP = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    CATALOG_TP = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    
    # Row vacío para channels sin actividad esta semana
    def _inactive_row(name):
        return [name, '#F2EEE6', '#8A8377', 'Sin Actividad',
                '—', '—', '—', None, '—', '—', '—']
    
    # Detectar nombres presentes (normalizado)
    pp_names = set(r[0] for r in chans_pp)
    tp_names = set(r[0] for r in chans_tp)
    
    # Ordenar activos: peor eficacia primero (r[5]=metrica str, parsear)
    def _sort_val(r):
        try: return float(str(r[5]).replace('%','').replace(',','.'))
        except: return 999
    chans_pp.sort(key=_sort_val)
    chans_tp.sort(key=_sort_val)

    # Completar PP con faltantes
    for name in CATALOG_PP:
        if not any(name.lower() in n.lower() for n in pp_names):
            chans_pp.append(_inactive_row(name))
    
    # Completar TP con faltantes
    for name in CATALOG_TP:
        if not any(name.lower() in n.lower() for n in tp_names):
            chans_tp.append(_inactive_row(name))
    owners = ['Supply Optimization', 'Supply Opt. / TPS', 'Supply Comercial / SO', 'Supply Comercial']
    plan = []
    if len(df_crit_top):
        h0 = df_crit_top.iloc[0]
        plan.append({'c': '', 'o': owners[0],
                     'a': f'Escalar {clean_hotel_name(str(h0["Hotel"]))[:55]} — Ef {es_pct(h0["Eficacia"])}.',
                     't': 'Conectividad', 'p': f'W{WEEK_NUM}'})
    if len(df_crit_top) > 1:
        h1 = df_crit_top.iloc[1]
        plan.append({'c': 'qw', 'o': owners[1],
                     'a': f'Revisar {clean_hotel_name(str(h1["Hotel"]))[:55]} — {es_pct(h1["Eficacia"])}.',
                     't': 'Eficacia', 'p': f'W{WEEK_NUM}'})
    plan.append({'c': 'mp', 'o': owners[2],
                 'a': f'Saneamiento {n_crit} hoteles Crítica+.',
                 't': 'Saneamiento', 'p': f'W{WEEK_NUM+1}'})
    if n_sc > 0:
        plan.append({'c': '', 'o': owners[3],
                     'a': f'Diagnóstico {n_sc} Sin Conversión — revisar mapping.',
                     't': 'Mapping', 'p': f'W{WEEK_NUM+1}'})

    # Carryover (vacío por defecto)
    co = []

    return {'re': re_items, 'hotels': hotel_rows, 'hotels_crit': hotels_crit_rows, 'hotels_br': hotels_br_rows, 'hotels_sc': hotels_sc_rows, 'hotels_cv': hotels_cv_rows, 'dims': dim_rows, 'corps': dim_rows, 'dests': dest_rows, 'chans': chan_rows, 'chans_pp': chans_pp, 'chans_tp': chans_tp, 'plan': plan, 'co': co}


def build_cr_d():
    result = {}

    # GLOBAL
    m_g  = M.get(f'global_w{WEEK_NUM}', {})
    m_g17= M.get(f'global_w{WEEK_PREV}', {})
    result['global'] = build_canasta_data(
        'global', p80, m_g, m_g17,
        dict(sev_ef), dict(sev_cv), g_corp,
        g_corp, len(p80))

    # CANASTAS
    canasta_map = {
        'b2c': ('B2C',    'B2C',       'B2B (OP)', False),
        'op':  ('B2B-OP', 'B2B (OP)',  'B2B (OP)', False),
        'cug': ('CUG',    'CUG (UOP)', 'CUG (UOP)', False),
    }
    for key, (c_key, m_key, _dist, _) in canasta_map.items():
        c = CANASTA.get(c_key)
        if c is None:
            result[key] = {'re': [], 'hotels': [], 'dims': [], 'plan': [], 'co': []}
            continue
        m18 = c.get('m18', {})
        m17 = c.get('m17', {})
        df_h = c.get('agg_hotel', pd.DataFrame()).copy()
        if 'Hotel' in df_h.columns:
            df_h['Hotel'] = df_h['Hotel'].apply(clean_hotel_name)
        # Agregar WoW si disponible
        if g_hotel_w17 is not None and 'Hotel' in df_h.columns and 'Eficacia_WoW_pp' not in df_h.columns:
            df_h = df_h.merge(
                g_hotel_w17[['Hotel','Eficacia_W17']].assign(Hotel=lambda x: x['Hotel'].apply(clean_hotel_name)),
                on='Hotel', how='left')
            df_h['Eficacia_WoW_pp'] = (df_h['Eficacia'] - df_h['Eficacia_W17']) * 100
        g_corp_c = c.get('agg_corp', pd.DataFrame())
        n_p80_c  = len(c.get('p80', pd.DataFrame()))
        if n_p80_c == 0: n_p80_c = len(df_h)
        sev_ef_c = dict(c.get('sev_ef', {}))
        sev_cv_c = dict(c.get('sev_cv', {}))
        result[key] = build_canasta_data(
            key, df_h, m18, m17, sev_ef_c, sev_cv_c,
            g_corp_c, g_corp_c, n_p80_c,
            g_channel_c=c.get('agg_channel'),
            g_dest_local=c.get('agg_destino'))
    return result


# ── Construir CR_AL[canasta] ──────────────────────────────────────────────────
def build_cr_al():
    result = {}

    def al_for(df_h, g_corp_c, label_ef='Peor Eficacia', label_cv='Peor ConvRate'):
        rows = []
        # Hoteles
        df_w = df_h[df_h.get('Bookings', pd.Series([1]*len(df_h))) > 0] if 'Bookings' in df_h.columns else df_h
        if len(df_w):
            h_ef = df_w.sort_values('Eficacia', ascending=True).iloc[0]
            h_cv = df_w.sort_values('ConvRate',  ascending=True).iloc[0]
            rows.append(['🏨', 'Hoteles',
                         clean_hotel_name(str(h_ef['Hotel']))[:35], es_pct(h_ef['Eficacia']),
                         clean_hotel_name(str(h_cv['Hotel']))[:35], es_pct(h_cv['ConvRate'])])
        # Destinos (desde agg por destino)
        g_dest_h = df_h.groupby('Destino').agg(
            CR_Unicos=('CR_Unicos','sum'), Bookings=('Bookings','sum'),
            Successful=('Successful','sum')).reset_index() if 'Destino' in df_h.columns else pd.DataFrame()
        if len(g_dest_h):
            g_dest_h['Eficacia'] = g_dest_h['Successful']/g_dest_h['CR_Unicos'].replace(0,1)
            g_dest_h['ConvRate'] = g_dest_h['Bookings']/g_dest_h['CR_Unicos'].replace(0,1)
            d_ef = g_dest_h.sort_values('Eficacia', ascending=True).iloc[0]
            d_cv = g_dest_h.sort_values('ConvRate',  ascending=True).iloc[0]
            rows.append(['📍', 'Destinos',
                         str(d_ef['Destino'])[:35], es_pct(d_ef['Eficacia']),
                         str(d_cv['Destino'])[:35], es_pct(d_cv['ConvRate'])])
        # Corporativo
        if len(g_corp_c):
            c_ef = g_corp_c.sort_values('Eficacia', ascending=True).iloc[0]
            c_cv = g_corp_c.sort_values('ConvRate',  ascending=True).iloc[0]
            rows.append(['🏢', 'Corporativo',
                         str(c_ef['CorpName'])[:35], es_pct(c_ef['Eficacia']),
                         str(c_cv['CorpName'])[:35], es_pct(c_cv['ConvRate'])])
        return rows

    result['global'] = al_for(p80, g_corp)

    for key, c_key in [('b2c','B2C'), ('op','Opaco'), ('cug','Ultra Opaco')]:
        c = CANASTA.get(c_key)
        if c is None:
            result[key] = []
            continue
        df_h = c.get('agg_hotel', pd.DataFrame()).copy()
        if 'Hotel' in df_h.columns:
            df_h['Hotel'] = df_h['Hotel'].apply(clean_hotel_name)
        g_corp_c = c.get('agg_corp', pd.DataFrame())
        result[key] = al_for(df_h, g_corp_c)

    return result


# ── Severity HTML (secciones estáticas que no cambian con canasta) ────────────
def render_severity():
    def sev_row(banda, rango, count, total):
        bbg, bfg = banda_colors(banda)
        pct = count/total if total else 0
        bc = BANDA_COLORS.get(banda, {})
        bar_color = bc.get('bar', bbg)
        bar_w = min(int(pct*100), 100)
        return (f'<div style="display:grid;grid-template-columns:120px 80px 1fr 60px 45px;'
                f'gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
                f'<span style="display:inline-block;padding:3px 8px;background:{bbg};color:{bfg};'
                f'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;'
                f'text-align:center;">{banda}</span>'
                f'<span style="font-size:11px;color:var(--ink-muted);text-align:right;">{rango}</span>'
                f'<div style="background:var(--rule-soft);height:6px;border-radius:0;">'
                f'<div style="width:{bar_w}%;height:100%;background:{bar_color};"></div></div>'
                f'<span style="font-size:12px;font-weight:700;color:var(--ink);text-align:right;">{count:,}</span>'
                f'<span style="font-size:11px;color:var(--ink-muted);text-align:right;">{pct:.1%}</span>'
                f'</div>').replace(',', '.')

    total_ef = sum(sev_ef.values())
    total_cv = sum(sev_cv.values())

    rows_ef = ''
    for banda, rng in [('Súper Crítica','<60%'),('Crítica','60–85%'),
                        ('Revisar','85–93%'),('Aceptable','93–97%'),('Exitosa','≥97%')]:
        rows_ef += sev_row(banda, rng, int(sev_ef.get(banda,0)), total_ef)

    rows_cv = ''
    for banda, rng in [('Sin Conversión','BKGS=0'),('Crítica','<0,8%'),
                        ('Revisar','0,8–1,5%'),('Aceptable','1,5–2,5%'),('Exitosa','≥2,5%')]:
        rows_cv += sev_row(banda, rng, int(sev_cv.get(banda,0)), total_cv)

    return f'''<section id="severity-combinada" style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Severity</h2>
<span class="section-subtitle" style="color:#5C469C">P80 · {len(p80)} hoteles</span>
<p class="section-kicker">Distribución del Top volumen CR (P80) por banda de Eficacia (target ≥ 97%) y Conv Rate (target ≥ 2,5%). Sin Conversión es cohorte estructural separada.</p>
</div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">Eficacia</h3>
{rows_ef}
</div>
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#5C469C;margin:0 0 12px;">Conv Rate</h3>
{rows_cv}
</div>
</div>
</section>'''


# ── HTML tabla de análisis de rendimiento ─────────────────────────────────────
def render_analisis_rendimiento():
    th_labels_hotel = ['Hotel', 'Severity', 'Tráfico', 'WoW↕', 'Eficacia', 'WoW↕', 'Conv Rate', 'WoW↕']
    th_labels_corp  = ['Corporativo', 'Severity', 'Tráfico', 'WoW↕', 'Eficacia', 'WoW↕', 'Conv Rate', 'WoW↕']

    def table_html(tbody_id, btn_id, th_labels, dim_header_id=None):
        # Colgroup: nombre amplio, resto fijos para evitar wrap
        colwidths = ['', '100px', '64px', '44px', '68px', '44px', '84px', '44px']
        colgroup = ''.join(
            f'<col style="width:{colwidths[i]}">' if colwidths[i] else '<col>'
            for i in range(len(th_labels))
        )
        cols = ''.join(
            f'<th style="padding:8px {"6px" if i>0 else "12px"} 8px {"6px" if i>0 else "12px"};'
            f'border-bottom:2px solid #5C469C;font-size:10px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);'
            f'text-align:{"left" if i==0 else "center" if i==1 else "right"};white-space:nowrap;">'
            f'{"<span id=\""+dim_header_id+"\">Corporativo</span>" if dim_header_id and i==0 else lbl}</th>'
            for i, lbl in enumerate(th_labels))
        return (f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;">'
                f'<colgroup>{colgroup}</colgroup>'
                f'<thead><tr>{cols}</tr></thead>'
                f'<tbody id="{tbody_id}"></tbody></table>'
                f'<div style="text-align:center;margin-top:10px;">'
                f'<button id="{btn_id}" style="display:none;font-family:\'Geist\',sans-serif;'
                f'font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'
                f'background:none;border:1px solid var(--rule);color:var(--ink-muted);'
                f'padding:7px 20px;cursor:pointer;border-radius:3px;"></button></div>')

    return f'''<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Análisis de Rendimiento</h2>
<span class="section-subtitle" style="color:var(--accent)">Top hoteles y dimensiones · canasta activa</span>
</div></div>
<div id="w22-ph" style="border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  <div class="tabs-row" style="margin-top:0;">
    <label class="active" style="padding:8px 14px;font-size:10px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;border-radius:6px 6px 0 0;border:1px solid var(--rule);border-bottom:1px solid var(--paper);background:var(--paper);margin-bottom:-1px;" onclick="w22_iTab(this)">Críticos</label>
    <label class="tab-label" onclick="w22_iTab(this)">Bajo Rendimiento</label>
    <label class="tab-label" onclick="w22_iTab(this)">Sin Conversión</label>
    <label class="tab-label" onclick="w22_iTab(this)">Menor ConvRate</label>
  </div>
  <div style="padding-top:14px;">
    {table_html('w22-th', 'w22-th-more', th_labels_hotel)}
  </div>
</div>
<div id="w22-pd" style="display:none;border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  <div class="tabs-row" style="margin-top:0;">
    <label style="padding:8px 14px;font-size:10px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;border-radius:6px 6px 0 0;border:1px solid var(--rule);border-bottom:1px solid var(--paper);background:var(--paper);margin-bottom:-1px;" onclick="w22_iTab(this);w22_setDim('corp')">Por Corporativo</label>
    <label class="tab-label" onclick="w22_iTab(this);w22_setDim('dest')">Por Destino</label>
    <label class="tab-label" onclick="w22_iTab(this);w22_setDim('chan')">Por Channel</label>
  </div>
  <div style="padding-top:14px;">
    {table_html('w22-td', 'w22-td-more', th_labels_corp, dim_header_id='w22-th-dim')}
  </div>
</div>
</section>'''


# ── HTML Alertas (contenedor vacío) ──────────────────────────────────────────
def render_alertas():
    return f'''<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Alertas Críticas</h2>
<span class="section-subtitle" id="w22-alertas-sub" style="color:var(--accent)">Peor Eficacia + Peor ConvRate · canasta activa</span>
</div></div>
<div id="w22-alertas" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;"></div>
</section>'''


# ── HTML Resumen Ejecutivo ────────────────────────────────────────────────────
def render_resumen():
    return f'''<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Resumen Ejecutivo</h2>
<span class="section-subtitle" style="color:var(--accent)">Canasta activa · 10 findings</span>
</div></div>
<ol class="exec-bullets" id="w22-re-list"></ol>
<div class="re-wrap"><button class="re-btn" id="w22-re-btn" onclick="w22_toggleRE()">Ver 5 más ↓</button></div>
</section>'''


# ── HTML Plan de Acción ───────────────────────────────────────────────────────
def render_plan():
    return f'''<section style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Plan de Acción</h2>
<span class="section-subtitle" style="color:var(--accent)">Canasta activa · W{WEEK_NUM}</span>
</div></div>
<div class="p-grid" id="w22-pg" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px;"></div>
<div style="margin-top:14px;padding:14px 18px;background:var(--paper-soft);border:1px solid var(--rule);border-left:3px solid var(--ink-muted);">
  <div style="font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-muted);margin-bottom:10px;">Carryover W{WEEK_PREV}</div>
  <div id="w22-co"></div>
</div>
</section>'''


# ── MAIN: calcular todo y escribir part2_cr.html ──────────────────────────────
print('Calculando CR_CV...')
CR_CV = build_cr_cv()

print('Calculando CR_D...')
CR_D  = build_cr_d()

print('Calculando CR_AL...')
CR_AL = build_cr_al()

# Extraer datos de hoteles desde CR_D para inyectarlos en CR_CV
CR_HOTELS = {}
for canasta in ['global', 'b2c', 'op', 'cug']:
    if canasta in CR_D and 'hotels_crit' in CR_D[canasta]:
        CR_HOTELS[canasta] = {
            'hotels': CR_D[canasta].get('hotels', []),
            'hotels_crit': CR_D[canasta].get('hotels_crit', []),
            'hotels_br': CR_D[canasta].get('hotels_br', []),
            'hotels_sc': CR_D[canasta].get('hotels_sc', []),
            'hotels_cv': CR_D[canasta].get('hotels_cv', []),
        }

# Serializar JSON
def safe_json(obj):
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    raise TypeError(f'Not serializable: {type(obj)}')

CR_CV_JSON = json.dumps(CR_CV, ensure_ascii=False, default=safe_json)
CR_D_JSON  = json.dumps(CR_D,  ensure_ascii=False, default=safe_json)
CR_AL_JSON = json.dumps(CR_AL, ensure_ascii=False, default=safe_json)
CR_HOTELS_JSON = json.dumps(CR_HOTELS, ensure_ascii=False, default=safe_json)

PART2 = (
    '<div id="w22-sev-cr">\n' + render_severity() + '\n</div>\n' +
    f'\n<script>\nvar CR_CV={CR_CV_JSON};\nvar CR_D={CR_D_JSON};\nvar CR_AL={CR_AL_JSON};\nvar CR_HOTELS={CR_HOTELS_JSON};\n</script>\n'
)

with open('part2_cr.html', 'w', encoding='utf-8') as f:
    f.write(PART2)
print(f'Part 2 CR escrito: {len(PART2):,} chars')
