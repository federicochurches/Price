"""
render_rnd_p2.py · W21+ · Modelo demo data-driven
Genera: part2_rnd.html
Estructura: secciones HTML vacías + <script> con JSON real W21 RND
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, pandas as pd, numpy as np
from engine import banda_nodispo, banda_rpm
from render_helpers import BANDA_COLORS, fmt_int_es, fmt_big

with open(os.getenv('PICKLE_RND', 'rnd_w21_data.pkl'), 'rb') as f:
    D = pickle.load(f)

VOL_NUM   = D.get('VOL_NUM', '21')
WEEK_NUM  = int(VOL_NUM)
WEEK_PREV = WEEK_NUM - 1

M        = D['M']
CANASTA  = D['CANASTA']
p80      = D['p80_hotel'].copy()
g_corp   = D['g_corp']
g_dest   = D['g_dest']
sev_nd   = D['sev_nd']
sev_rpm  = D['sev_rpm']
TOP      = D['TOP']
g_corp_w17 = D.get('g_corp_w17')
g_dest_w17 = D.get('g_dest_w17')

# ── Helpers ───────────────────────────────────────────────────────────────────
def es_pct(v):  return f'{v*100:.2f}%'.replace('.', ',')
def es_int(v):  return f'{int(v):,}'.replace(',', '.')
def es_ipm(v):  return f'${int(v):,}'.replace(',', '.')

def banda_colors(banda):
    bc = BANDA_COLORS.get(banda, BANDA_COLORS['Sin Conversión'])
    return bc['bg'], bc['fg']

def wow_arrow(pp):
    if pp is None or (isinstance(pp, float) and np.isnan(pp)): return '—'
    if pp > 0: return f'▲{abs(pp):.1f}'.replace('.', ',')
    if pp < 0: return f'▼{abs(pp):.1f}'.replace('.', ',')
    return '—'

def sev_badge_html(banda):
    bbg, bfg = banda_colors(banda)
    return (f'<b class="sev-badge" style="background:{bbg};color:{bfg};'
            f'font-size:8px;padding:2px 6px;text-transform:uppercase;'
            f'outline:1px solid rgba(0,0,0,.12);">{banda}</b>')

def build_hotel_row_rnd(row):
    """r: [nombre, bbg, bfg, banda, trafico, %NoDispo, IPM, wow_up, wow_nd_str, wow_ipm_str, wow_traf_str]"""
    name   = str(row.get('Hotel', '?'))[:60]
    banda  = row.get('BandaNoDispo', 'Sin Conversión')
    bbg, bfg = banda_colors(banda)
    traf_v = row.get('Trafico', 0)
    traf   = fmt_big(float(traf_v)) if traf_v and not np.isnan(float(traf_v)) else '0'
    nd     = es_pct(row.get('%NoDispo', 0))
    ipm    = es_ipm(row.get('IPM', row.get('RPM', 0)))
    # WoW NoDispo
    wow_pp = row.get('NoDispo_WoW_pp')
    if wow_pp is None or (isinstance(wow_pp, float) and np.isnan(wow_pp)):
        wow_up = None; wow_nd_str = '—'
    else:
        wow_up = bool(wow_pp <= 0)   # NoDispo: baja = mejor
        wow_nd_str = wow_arrow(wow_pp)
    # WoW IPM
    wow_ipm_pp = row.get('IPM_WoW_pp')
    if wow_ipm_pp is None or (isinstance(wow_ipm_pp, float) and np.isnan(wow_ipm_pp)):
        wow_ipm_str = '—'
    else:
        wow_ipm_str = wow_arrow(wow_ipm_pp)
    # WoW Tráfico
    wow_traf = row.get('Trafico_WoW_pct')
    if wow_traf is None or (isinstance(wow_traf, float) and np.isnan(wow_traf)):
        wow_traf_str = '—'
    else:
        sign = '▲' if wow_traf >= 0 else '▼'
        wow_traf_str = f'{sign}{abs(round(wow_traf,1))}'.replace('.', ',') + '%'
    return [name, bbg, bfg, banda, traf, nd, ipm, wow_up, wow_nd_str, wow_ipm_str, wow_traf_str]

# ── RND_CV ────────────────────────────────────────────────────────────────────
def build_rnd_cv():
    result = {}
    canasta_col = {'global': '#333132', 'b2c': '#EA0074', 'op': '#FCB000', 'cug': '#4FC3F4'}
    canasta_m = {'global': f'global_w{WEEK_NUM}',
                 'b2c':    f'B2C_w{WEEK_NUM}',
                 'op':     f'B2B (OP)_w{WEEK_NUM}',
                 'cug':    f'CUG (UOP)_w{WEEK_NUM}'}
    for key, m_key in canasta_m.items():
        m = M.get(m_key, {})
        nd    = m.get('pct_nodispo', m.get('nodispo', 0))
        ipm   = m.get('ipm', m.get('rpm', 0))
        banda = banda_nodispo(nd)
        bbg, bfg = banda_colors(banda)
        banda_ipm_v = banda_rpm(ipm, m.get('bookings', 1))
        bbg_cv, bfg_cv = banda_colors(banda_ipm_v)
        trafico_v = m.get('trafico', 0)
        # WoW tráfico
        m_prev_key = m_key.replace(f'_w{WEEK_NUM}', f'_w{WEEK_NUM-1}')
        m_prev = M.get(m_prev_key, {})
        traf_prev = m_prev.get('trafico', 0)
        traf_wow = round((trafico_v - traf_prev) / traf_prev * 100, 1) if traf_prev else None
        # Formatear tráfico
        def _fmt_big(v):
            v = float(v) if v else 0
            if v >= 1e9: return f'{v/1e9:.1f}B'.replace('.',',')
            if v >= 1e6: return f'{v/1e6:.1f}M'.replace('.',',')
            if v >= 1e3: return f'{v/1e3:.0f}K'
            return str(int(v))
        trafico_str = _fmt_big(trafico_v)
        vol_str = _fmt_big(trafico_v)
        # Valores semana anterior para WoW en cards AR
        nd_prev  = m_prev.get('pct_nodispo', m_prev.get('nodispo', None))
        ipm_prev = m_prev.get('ipm', m_prev.get('rpm', None))
        nd_wow   = round((nd  - nd_prev)  * 100, 2) if nd_prev  is not None else None
        ipm_wow  = round((ipm - ipm_prev), 2)        if ipm_prev is not None else None
        result[key] = {
            'ef':      es_pct(nd),
            'cv':      es_ipm(ipm),
            'ef_prev': es_pct(nd_prev)   if nd_prev  is not None else None,
            'cv_prev': es_ipm(ipm_prev)  if ipm_prev is not None else None,
            'ef_wow':  nd_wow,
            'cv_wow':  ipm_wow,
            'band':    banda,
            'bbg':     bbg,
            'bfg':     bfg,
            'band_cv': banda_ipm_v,
            'bbg_cv':  bbg_cv,
            'bfg_cv':  bfg_cv,
            'col':     canasta_col[key],
            'vol':     vol_str,
            'trafico': trafico_str,
            'traf_wow': traf_wow,
        }
    return result

# ── RND_D ─────────────────────────────────────────────────────────────────────
def build_canasta_data_rnd(key, df_hotel, m18, m17, sev_nd_c, sev_rpm_c, g_corp_c, n_p80):
    nd    = m18.get('pct_nodispo', m18.get('nodispo', 0))
    ipm   = m18.get('ipm', m18.get('rpm', 0))
    nd17  = m17.get('pct_nodispo', m17.get('nodispo', 0))
    ipm17 = m17.get('ipm', m17.get('rpm', 0))
    nd_wow  = (nd - nd17) * 100
    ipm_wow = ipm - ipm17
    banda_nd  = banda_nodispo(nd)
    banda_ipm = banda_rpm(ipm, m18.get('bookings', 1))

    n_crit = int(sev_nd_c.get('Crítica', 0) + sev_nd_c.get('Súper Crítica', 0))
    n_sc   = int(sev_rpm_c.get('Sin Conversión', 0))

    # Peores
    df_sorted = df_hotel.sort_values('%NoDispo', ascending=False)
    worst_nd  = df_sorted.iloc[0] if len(df_sorted) else None
    df_ipm    = df_hotel[df_hotel.get('Bookings', pd.Series([1]*len(df_hotel))) > 0].sort_values(
        'IPM', ascending=True) if 'Bookings' in df_hotel.columns else df_hotel.sort_values('IPM', ascending=True)
    worst_ipm = df_ipm.iloc[0] if len(df_ipm) else None

    # Top destino
    g_dest_h = df_hotel.groupby('Destino').agg(
        Trafico=('Trafico','sum'), Bookings=('Bookings','sum'), gb_usd=('gb_usd','sum'),
        TraficoNoDispo=('TraficoNoDispo','sum')).reset_index() if 'Destino' in df_hotel.columns else pd.DataFrame()
    if len(g_dest_h):
        g_dest_h['%NoDispo'] = g_dest_h['TraficoNoDispo'] / g_dest_h['Trafico'].replace(0,1)
        worst_dest = g_dest_h.sort_values('%NoDispo', ascending=False).iloc[0]
        worst_dest_name = str(worst_dest['Destino'])
        worst_dest_nd   = es_pct(worst_dest['%NoDispo'])
    else:
        worst_dest_name = '—'; worst_dest_nd = '—'

    sfx = f' {key.upper().replace("OP","Opaco")}' if key != 'global' else ' global'

    re_items = [
        {'n': es_pct(nd),
         't': f'NoDispo{sfx} · {sev_badge_html(banda_nd)}',
         'd': f'{"Por debajo" if nd < 0.05 else "Por encima"} del target 5% · {"mejora" if nd_wow<=0 else "empeora"} {wow_arrow(nd_wow)} WoW.'},
        {'n': es_ipm(ipm),
         't': f'IPM{sfx} · {sev_badge_html(banda_ipm)}',
         'd': f'Target ≥ $650 · {"récord" if ipm > ipm17 else "cae"} WoW.'},
        {'n': str(n_crit),
         't': f'Hoteles P80 {sev_badge_html("Crítica")}+ NoDispo',
         'd': f'NoDispo > 20%.'},
        {'n': str(n_sc),
         't': f'Hoteles P80 {sev_badge_html("Sin Conversión")}',
         'd': 'Sin booking · BKGS=0.'},
        {'n': es_pct(nd),
         't': f'Canal{sfx} NoDispo más alto',
         'd': 'Mayor demanda perdida del canal.'},
        {'n': es_pct(df_hotel.sort_values("%NoDispo",ascending=False).iloc[0]["%NoDispo"]) if len(df_hotel) else "—",
         't': f'{worst_nd["Hotel"][:35] if worst_nd is not None else "—"} · peor NoDispo',
         'd': f'{es_int(worst_nd["Trafico"]) if worst_nd is not None else "—"} tráfico.'},
        {'n': es_ipm(worst_ipm["IPM"]) if worst_ipm is not None else "—",
         't': f'{worst_ipm["Hotel"][:35] if worst_ipm is not None else "—"} · peor IPM',
         'd': 'Revenue bajo en canal.'},
        {'n': worst_dest_nd,
         't': f'{worst_dest_name} · mayor NoDispo',
         'd': 'Primera prioridad de apertura de cupos.'},
        {'n': str(n_sc),
         't': f'Sin Conversión · cohorte estructural{sfx}',
         'd': 'Diagnóstico técnico/contractual urgente.'},
        {'n': str(n_p80),
         't': 'Hoteles P80 analizados',
         'd': f'W{VOL_NUM}.'},
    ]

    # Hotel rows — 3 tabs separados
    def rnd_hotel_rows_from(df):
        return [build_hotel_row_rnd(r) for _, r in df.iterrows()]

    # Demanda NC: mayor NoDispo (con o sin bookings)
    df_dnc  = df_hotel.sort_values('%NoDispo', ascending=False).head(100)
    # Bajo Rendimiento: Bookings > 0, NoDispo Revisar o Crítica/SC
    df_bkgs = df_hotel[df_hotel.get('Bookings', pd.Series([0]*len(df_hotel))) > 0] if 'Bookings' in df_hotel.columns else df_hotel
    df_br   = df_bkgs[df_bkgs['BandaNoDispo'].isin(['Revisar','Crítica','Súper Crítica'])].sort_values('%NoDispo', ascending=False).head(100)
    # Sin Conversión: Bookings = 0
    df_sc   = df_hotel[df_hotel.get('Bookings', pd.Series([1]*len(df_hotel))) == 0].sort_values('Trafico', ascending=False).head(100) if 'Bookings' in df_hotel.columns else pd.DataFrame()

    hotel_rows       = rnd_hotel_rows_from(df_dnc)
    hotels_dnc_rows  = rnd_hotel_rows_from(df_dnc)
    hotels_br_rows   = rnd_hotel_rows_from(df_br)
    hotels_sc_rows   = rnd_hotel_rows_from(df_sc)

    # Dim rows (por corp, peor NoDispo)
    dim_rows = []
    g_c_sort = g_corp_c.sort_values('%NoDispo', ascending=False).head(100) if '%NoDispo' in g_corp_c.columns else g_corp_c.head(100)
    for _, row in g_c_sort.iterrows():
        name   = str(row.get('CorpName', '?'))[:45]
        nd_r   = row.get('%NoDispo', 0)
        ipm_r  = row.get('IPM', row.get('RPM', 0))
        banda  = banda_nodispo(nd_r)
        bbg, bfg = banda_colors(banda)
        traf   = es_int(row.get('Trafico', 0))
        wow_pp = row.get('NoDispo_WoW_pp')
        if wow_pp is None or (isinstance(wow_pp, float) and np.isnan(wow_pp)):
            wow_up = None; wow_str = '—'
        else:
            wow_up = bool(wow_pp <= 0); wow_str = wow_arrow(wow_pp)
        dim_rows.append([name, bbg, bfg, banda, traf, es_pct(nd_r), es_ipm(ipm_r), wow_up, wow_str, '—', '—'])

    # Corp rows = dim_rows (alias)
    corps_rows = dim_rows

    # Dest rows (por Destino, peor NoDispo)
    dest_rows = []
    # Agrupar por destino desde df_hotel
    g_d_avail = None
    if 'Destino' in df_hotel.columns and len(df_hotel):
        g_d_avail = df_hotel.groupby('Destino').agg(
            Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
            gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum')
        ).reset_index()
        g_d_avail['%NoDispo'] = g_d_avail['TraficoNoDispo'] / g_d_avail['Trafico'].replace(0,1)
        g_d_avail['IPM'] = g_d_avail['gb_usd'] / g_d_avail['Trafico'].replace(0,1) * 1_000_000
    if g_d_avail is not None and '%NoDispo' in g_d_avail.columns:
        for _, row in g_d_avail.sort_values('%NoDispo', ascending=False).head(100).iterrows():
            dest_name = str(row.get('Destino','?')).replace(' Area','').replace(' area','')[:55]
            nd_r  = row.get('%NoDispo', 0)
            ipm_r = row.get('IPM', row.get('RPM', 0))
            banda = banda_nodispo(nd_r)
            bbg, bfg = banda_colors(banda)
            traf  = es_int(row.get('Trafico', 0))
            wow_pp = row.get('NoDispo_WoW_pp')
            wow_up = None; wow_nd = '—'
            if wow_pp is not None and not (isinstance(wow_pp, float) and np.isnan(wow_pp)):
                wow_up = bool(wow_pp <= 0); wow_nd = wow_arrow(wow_pp)
            wow_ipm_pp = row.get('IPM_WoW_pp')
            wow_ipm = '—'
            if wow_ipm_pp is not None and not (isinstance(wow_ipm_pp, float) and np.isnan(wow_ipm_pp)):
                wow_ipm = wow_arrow(wow_ipm_pp)
            dest_rows.append([dest_name, bbg, bfg, banda, traf, es_pct(nd_r), es_ipm(ipm_r), wow_up, wow_nd, wow_ipm, '—'])

    # Pais rows
    pais_rows = []
    if 'PaisDestino' in df_hotel.columns and len(df_hotel):
        g_pais = df_hotel.groupby('PaisDestino').agg(
            Trafico=('Trafico','sum'), Bookings=('Bookings','sum'),
            gb_usd=('gb_usd','sum'), TraficoNoDispo=('TraficoNoDispo','sum')
        ).reset_index()
        g_pais['%NoDispo'] = g_pais['TraficoNoDispo'] / g_pais['Trafico'].replace(0,1)
        g_pais['IPM'] = g_pais['gb_usd'] / g_pais['Trafico'].replace(0,1) * 1_000_000
        for _, row in g_pais.sort_values('%NoDispo', ascending=False).head(100).iterrows():
            pais_name = str(row.get('PaisDestino','?'))[:55]
            nd_r  = row.get('%NoDispo', 0)
            ipm_r = row.get('IPM', 0)
            banda = banda_nodispo(nd_r)
            bbg, bfg = banda_colors(banda)
            traf  = es_int(row.get('Trafico', 0))
            pais_rows.append([pais_name, bbg, bfg, banda, traf,
                              es_pct(nd_r), es_ipm(ipm_r), None, '—', '—', '—'])

    # Plan
    owners = ['Supply Optimization', 'Supply Opt. / TPS', 'Supply Comercial / SO', 'Supply Comercial']
    plan = []
    if worst_nd is not None:
        plan.append({'c': '', 'o': owners[0],
                     'a': f'Apertura cupos {str(worst_nd["Hotel"])[:40]} — NoDispo {es_pct(worst_nd["%NoDispo"])}.',
                     't': 'NoDispo', 'p': f'W{WEEK_NUM}'})
    if len(g_c_sort):
        c0 = g_c_sort.iloc[0]
        plan.append({'c': 'qw', 'o': owners[1],
                     'a': f'Revisar paridad {str(c0["CorpName"])[:35]} — NoDispo {es_pct(c0["%NoDispo"])}.',
                     't': 'Paridad', 'p': f'W{WEEK_NUM}'})
    plan.append({'c': 'mp', 'o': owners[2],
                 'a': f'Saneamiento {n_crit} hoteles Crítica+ NoDispo.',
                 't': 'Saneamiento', 'p': f'W{WEEK_NUM+1}'})

    return {'re': re_items, 'hotels': hotel_rows, 'hotels_dnc': hotels_dnc_rows, 'hotels_br': hotels_br_rows, 'hotels_sc': hotels_sc_rows, 'dims': dim_rows, 'corps': corps_rows, 'dests': dest_rows, 'chans': pais_rows, 'plan': plan, 'co': []}


def build_rnd_d():
    result = {}
    # GLOBAL
    m_g   = M.get(f'global_w{WEEK_NUM}', {})
    m_g17 = M.get(f'global_w{WEEK_PREV}', {})
    # Agregar WoW a p80
    p80_w = p80.copy()
    if 'NoDispo_WoW_pp' not in p80_w.columns:
        p80_w['NoDispo_WoW_pp'] = None

    # g_corp con NoDispo
    g_corp_nd = g_corp.copy()
    if '%NoDispo' not in g_corp_nd.columns:
        # Calcular desde p80
        g_corp_nd = p80_w.groupby('CorpName').agg(
            Trafico=('Trafico','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
            Bookings=('Bookings','sum'), gb_usd=('gb_usd','sum')).reset_index()
        g_corp_nd['%NoDispo'] = g_corp_nd['TraficoNoDispo'] / g_corp_nd['Trafico'].replace(0,1)
        g_corp_nd['IPM'] = g_corp_nd['gb_usd'] / g_corp_nd['Trafico'].replace(0,1) * 1_000_000

    result['global'] = build_canasta_data_rnd(
        'global', p80_w, m_g, m_g17,
        dict(sev_nd), dict(sev_rpm), g_corp_nd, len(p80_w))

    # CANASTAS
    for key, c_key in [('b2c','B2C'),('op','B2B-OP'),('cug','CUG')]:
        c = CANASTA.get(c_key) or CANASTA.get(c_key.lower())
        if c is None:
            result[key] = {'re': [], 'hotels': [], 'dims': [], 'plan': [], 'co': []}
            continue
        m18 = c.get('m18', {})
        m17 = c.get('m17', {})
        df_h = c.get('agg_hotel', pd.DataFrame()).copy()
        if 'NoDispo_WoW_pp' not in df_h.columns:
            df_h['NoDispo_WoW_pp'] = None
        g_corp_c = c.get('agg_corp', pd.DataFrame())
        if '%NoDispo' not in g_corp_c.columns and 'TraficoNoDispo' in g_corp_c.columns:
            g_corp_c['%NoDispo'] = g_corp_c['TraficoNoDispo'] / g_corp_c['Trafico'].replace(0,1)
        n_p80_c = len(c.get('p80_hotel', df_h))
        sev_nd_c  = dict(c.get('sev_nd', {}))
        sev_rpm_c = dict(c.get('sev_rpm', {}))
        result[key] = build_canasta_data_rnd(
            key, df_h, m18, m17, sev_nd_c, sev_rpm_c, g_corp_c, n_p80_c)
    return result


# ── RND_AL ────────────────────────────────────────────────────────────────────
def build_rnd_al():
    result = {}
    def al_for(df_h, g_corp_c):
        rows = []
        if len(df_h):
            h_nd  = df_h.sort_values('%NoDispo', ascending=False).iloc[0]
            df_ipm = df_h[df_h['Bookings']>0].sort_values('IPM', ascending=True) if 'Bookings' in df_h.columns else df_h.sort_values('IPM', ascending=True)
            h_ipm = df_ipm.iloc[0] if len(df_ipm) else h_nd
            rows.append(['🏨', 'Hoteles',
                         str(h_nd['Hotel'])[:35], es_pct(h_nd['%NoDispo']),
                         str(h_ipm['Hotel'])[:35], es_ipm(h_ipm.get('IPM', 0))])
        if len(df_h) and 'Destino' in df_h.columns:
            g_d = df_h.groupby('Destino').agg(
                Trafico=('Trafico','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
                Bookings=('Bookings','sum'), gb_usd=('gb_usd','sum')).reset_index()
            g_d['%NoDispo'] = g_d['TraficoNoDispo']/g_d['Trafico'].replace(0,1)
            g_d['IPM'] = g_d['gb_usd']/g_d['Trafico'].replace(0,1)*1_000_000
            d_nd  = g_d.sort_values('%NoDispo', ascending=False).iloc[0]
            d_ipm = g_d[g_d['Bookings']>0].sort_values('IPM', ascending=True).iloc[0] if len(g_d[g_d['Bookings']>0]) else d_nd
            rows.append(['📍', 'Destinos',
                         str(d_nd['Destino']).replace(' Area','')[:35], es_pct(d_nd['%NoDispo']),
                         str(d_ipm['Destino']).replace(' Area','')[:35], es_ipm(d_ipm['IPM'])])
        if len(g_corp_c) and '%NoDispo' in g_corp_c.columns:
            c_nd  = g_corp_c.sort_values('%NoDispo', ascending=False).iloc[0]
            c_ipm = g_corp_c[g_corp_c.get('Bookings',pd.Series([1]*len(g_corp_c)))>0].sort_values(
                'IPM', ascending=True).iloc[0] if 'IPM' in g_corp_c.columns and len(g_corp_c) else c_nd
            rows.append(['🏢', 'Corporativo',
                         str(c_nd['CorpName'])[:35], es_pct(c_nd['%NoDispo']),
                         str(c_ipm.get('CorpName', c_nd['CorpName']))[:35], es_ipm(c_ipm.get('IPM', 0))])
        return rows

    g_corp_nd = g_corp.copy()
    if '%NoDispo' not in g_corp_nd.columns:
        g_corp_nd = p80.groupby('CorpName').agg(
            Trafico=('Trafico','sum'), TraficoNoDispo=('TraficoNoDispo','sum'),
            Bookings=('Bookings','sum'), gb_usd=('gb_usd','sum')).reset_index()
        g_corp_nd['%NoDispo'] = g_corp_nd['TraficoNoDispo'] / g_corp_nd['Trafico'].replace(0,1)
        g_corp_nd['IPM'] = g_corp_nd['gb_usd'] / g_corp_nd['Trafico'].replace(0,1) * 1_000_000

    result['global'] = al_for(p80, g_corp_nd)
    for key, c_key in [('b2c','B2C'),('op','B2B-OP'),('cug','CUG')]:
        c = CANASTA.get(c_key) or CANASTA.get(c_key.lower())
        if c is None: result[key] = []; continue
        df_h     = c.get('agg_hotel', pd.DataFrame()).copy()
        g_corp_c = c.get('agg_corp', pd.DataFrame())
        if '%NoDispo' not in g_corp_c.columns and 'TraficoNoDispo' in g_corp_c.columns:
            g_corp_c['%NoDispo'] = g_corp_c['TraficoNoDispo']/g_corp_c['Trafico'].replace(0,1)
        if 'IPM' not in g_corp_c.columns and 'RPM' in g_corp_c.columns:
            g_corp_c['IPM'] = g_corp_c['RPM']
        result[key] = al_for(df_h, g_corp_c)
    return result


# ── Severity HTML ─────────────────────────────────────────────────────────────
def render_severity():
    def sev_row(banda, rango, count, total):
        bbg, bfg = banda_colors(banda)
        pct = count/total if total else 0
        bc  = BANDA_COLORS.get(banda, {})
        bar_color = bc.get('bar', bbg)
        bar_w = min(int(pct*100), 100)
        return (f'<div style="display:grid;grid-template-columns:120px 80px 1fr 60px 45px;'
                f'gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
                f'<span style="display:inline-block;padding:3px 8px;background:{bbg};color:{bfg};'
                f'font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{banda}</span>'
                f'<span style="font-size:11px;color:var(--ink-muted);text-align:right;">{rango}</span>'
                f'<div style="background:var(--rule-soft);height:6px;">'
                f'<div style="width:{bar_w}%;height:100%;background:{bar_color};"></div></div>'
                f'<span style="font-size:12px;font-weight:700;color:var(--ink);text-align:right;">{count:,}</span>'
                f'<span style="font-size:11px;color:var(--ink-muted);text-align:right;">{pct:.1%}</span>'
                f'</div>').replace(',', '.')

    total_nd  = sum(sev_nd.values())
    total_rpm = sum(sev_rpm.values())

    rows_nd = ''
    for banda, rng in [('Súper Crítica','>60%'),('Crítica','20–60%'),
                        ('Revisar','5–20%'),('Aceptable','3–5%'),('Exitosa','<3%')]:
        rows_nd += sev_row(banda, rng, int(sev_nd.get(banda,0)), total_nd)

    rows_rpm = ''
    for banda, rng in [('Sin Conversión','BKGS=0'),('Crítica','<$200'),
                        ('Revisar','$200–$650'),('Aceptable','$650–$1.500'),('Exitosa','≥$1.500')]:
        rows_rpm += sev_row(banda, rng, int(sev_rpm.get(banda,0)), total_rpm)

    return f'''<section id="severity-combinada" style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Severity</h2>
<span class="section-subtitle" style="color:#EA0074">P80 · {len(p80)} hoteles · {len(p80.get("DistributionCategory", p80).drop_duplicates() if "DistributionCategory" in p80.columns else p80)} registros</span>
<p class="section-kicker">Distribución global del P80 por banda de %NoDispo (target < 3%) e IPM (target ≥ $650). Sin Conversión = BKGS=0, cohorte estructural separada.</p>
</div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">%NoDispo</h3>
{rows_nd}
</div>
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#A86A1D;margin:0 0 12px;">IPM (Income Per Million USD)</h3>
{rows_rpm}
</div>
</div>
</section>'''


# ── Análisis de Rendimiento ───────────────────────────────────────────────────
def render_analisis():
    def table_html(tbody_id, btn_id, th_labels, dim_id=None):
        colwidths = ['', '100px', '64px', '44px', '68px', '44px', '84px', '44px']
        colgroup = ''.join(
            f'<col style="width:{colwidths[i]}">' if i < len(colwidths) and colwidths[i] else '<col>'
            for i in range(len(th_labels))
        )
        cols = ''.join(
            f'<th style="padding:8px {"6px" if i>0 else "12px"} 8px {"6px" if i>0 else "12px"};'
            f'border-bottom:2px solid #EA0074;font-size:10px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);'
            f'text-align:{"left" if i==0 else "center" if i==1 else "right"};white-space:nowrap;">'
            f'{"<span id=\""+dim_id+"\">Corporativo</span>" if dim_id and i==0 else lbl}</th>'
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

    th_h = ['Hotel', 'Severity', 'Tráfico', 'WoW↕', '%NoDispo', 'WoW↕', 'IPM', 'WoW↕']
    th_d = ['Dimensión', 'Severity', 'Tráfico', 'WoW↕', '%NoDispo', 'WoW↕', 'IPM', 'WoW↕']

    return f'''<section style="margin-bottom:48px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head"><div>
<h2 class="section-title">Análisis de Rendimiento</h2>
<span class="section-subtitle" style="color:var(--accent)">Top hoteles y dimensiones · canasta activa</span>
</div></div>
<div id="w22-ph" style="border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  <div class="tabs-row" style="margin-top:0;">
    <label style="padding:8px 14px;font-size:10px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;border-radius:6px 6px 0 0;border:1px solid var(--rule);border-bottom:1px solid var(--paper);background:var(--paper);margin-bottom:-1px;" onclick="w22_iTab(this)">Demanda NC</label>
    <label class="tab-label" onclick="w22_iTab(this)">Bajo Rendimiento</label>
    <label class="tab-label" onclick="w22_iTab(this)">Sin Conversión</label>
  </div>
  <div style="padding-top:14px;">
    {table_html('w22-th', 'w22-th-more', th_h)}
  </div>
</div>
<div id="w22-pd" style="display:none;border:1px solid var(--rule);border-top:none;padding:20px;background:var(--paper);">
  {table_html('w22-td', 'w22-td-more', th_d, dim_id='w22-th-dim')}
</div>
</section>'''


# ── MAIN ──────────────────────────────────────────────────────────────────────
print('Calculando RND_CV...')
RND_CV = build_rnd_cv()
print('Calculando RND_D...')
RND_D  = build_rnd_d()
print('Calculando RND_AL...')
RND_AL = build_rnd_al()

def safe_json(obj):
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    raise TypeError(f'Not serializable: {type(obj)}')

RND_CV_JSON = json.dumps(RND_CV, ensure_ascii=False, default=safe_json)
RND_D_JSON  = json.dumps(RND_D,  ensure_ascii=False, default=safe_json)
RND_AL_JSON = json.dumps(RND_AL, ensure_ascii=False, default=safe_json)

# Alertas subtitle dinámico para RND
PART2 = (
    '<div id="w22-sev-rnd" style="display:none;">\n' + render_severity() + '\n</div>\n' +
    f'\n<script>\nvar RND_CV={RND_CV_JSON};\nvar RND_D={RND_D_JSON};\nvar RND_AL={RND_AL_JSON};\n</script>\n'
)
with open('part2_rnd.html', 'w', encoding='utf-8') as f:
    f.write(PART2)
print(f'Part 2 RND escrito: {len(PART2):,} chars')
