"""
Renderer · Reporte Editorial RND W18
Genera HTML completo · sistema bandas D · post W17
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np
from engine import *
from render_helpers import *
from render_helpers import _kpi_pill

from historico_module import render_historico
from render_historico_svg import render_historico_svg as _rhs

def _mini_badge(bnd):
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span class="sev-badge" style="background:{bg};color:{fg};">{bnd}</span>'


# Cargar datos
with open(os.getenv('PICKLE_RND', 'rnd_w21_data.pkl'),'rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']; TAB_NoDispo = D['TAB_NoDispo']; TAB_RPM = D['TAB_RPM']

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

CANASTA = D['CANASTA']; sev_nd = D['sev_nd']; sev_rpm = D['sev_rpm']


# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
# Los pickles usan global_w18/w17 pero W18 es realmente W_current y W17 es W_prev
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1

# Crear alias dinámicos que apunten a los datos correctos
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))

# Para compatibilidad backwards, también mantener los viejos keys
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

# Alias para funciones no definidas en esta versión
def fmt_usd(v):
    """Alias de fmt_num2 para compatibilidad."""
    return fmt_num2(v)
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']

# ── CONFIG SEMANAL ────────────────────────────────────────────────────────────
WEEK_NUM      = D.get('VOL_NUM', '19')
WEEK_DISPLAY  = f'Week {WEEK_NUM}'
PERIODO_LABEL = D.get('PERIODO', '5–11 may 2026')
VOL_NUM       = D.get('VOL_NUM', WEEK_NUM)
MES_AÑO       = D.get('MES_AÑO', 'Mayo 2026')
FECHA_PUB     = D.get('FECHA_PUB', 'LUNES 18 de Mayo de 2026')
# ─────────────────────────────────────────────────────────────────────────────

# Cargar head y footer
with open('asset_rnd_head.html') as f: HEAD = f.read()
with open('asset_rnd_footer.html') as f: FOOTER = f.read()

# ============ MASTHEAD ============
def render_masthead():
    LOGO = "data:image/png;base64,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"

    g22 = M.get(f'global_w{WEEK_NUM_INT}', {})
    TRAFICO_FMT   = fmt_big(g22.get('trafico', 0))
    N_HOTELES_FMT = fmt_int_es(g22.get('n_hoteles', 0))
    BOOKINGS_FMT  = fmt_int_es(g22.get('bookings', 0))
    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div class="masthead-inner" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div class="masthead-left">
<div style="display:inline-block;background:#EA0074;color:#fff;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 9px;border-radius:3px;margin-bottom:6px;">{WEEK_DISPLAY}</div>
<h1 style="margin:6px 0 4px;font-size:clamp(20px,2.0vw,30px);font-weight:800;letter-spacing:-.03em;line-height:1.05;"><span style="color:#EA0074;">Connectivities </span><span style="color:var(--ink);">&amp; Hotel </span><span style="color:#EA0074;">Availability</span></h1>
<div style="font-size:10px;font-weight:500;color:var(--ink-muted);margin-top:6px;letter-spacing:.06em;text-transform:uppercase;"><strong style="color:#EA0074;font-weight:700;">{TRAFICO_FMT}</strong> Tráfico · <strong style="color:#EA0074;font-weight:700;">{N_HOTELES_FMT}</strong> hoteles P80 · Target: <strong style="color:#EA0074;font-weight:700;">{BOOKINGS_FMT}</strong> Bookings</div>
<div style="font-size:11px;font-weight:400;color:var(--ink-muted);margin-top:6px;">{FECHA_PUB}<span style="margin:0 16px;color:var(--rule);">|</span>Vol. {VOL_NUM}</div>
</div>
<div class="masthead-right" style="display:flex;align-items:center;gap:0;flex-shrink:0;">
<img alt="PriceTravel" src="{LOGO}" style="height:40px;width:auto;" class="masthead-logo"/>

</div>
</div>

</header>
'''

# ============ HERO H1 + KPI HERO + ALERTS ============
def calc_h1_data():
    """Construye H1 narrativo de 2 líneas."""
    pct = M['global_current']['pct_nodispo']
    rpm = M['global_current']['rpm']
    # Top 3 destinos por demanda no convertida
    g_d = TAB_NoDispo['destino']
    top_dest = []
    # mejor: top 3 destinos con más demanda no convertida
    g_h = g_hotel.copy()
    by_dest = g_h.groupby('Destino').agg(
        Trafico=('Trafico','sum'),
        DNC=('DemandaNoConvertida','sum'),
    ).reset_index().sort_values('DNC', ascending=False).head(3)
    top_dest = by_dest['Destino'].tolist()
    # Top 3 corp con más volumen + %NoDispo Crítico/Revisar
    by_corp = g_hotel.groupby('CorpName').agg(
        Trafico=('Trafico','sum'),
        Bookings=('Bookings','sum'),
        DNC=('DemandaNoConvertida','sum'),
    ).reset_index().sort_values('DNC', ascending=False).head(3)
    top_corp = by_corp['CorpName'].tolist()
    return pct, rpm, top_dest, top_corp

def render_hero():
    pct, rpm, top_dest, top_corp = calc_h1_data()
    pct17 = M['global_w17']['pct_nodispo']
    rpm17 = M['global_w17']['rpm']
    bk18 = M['global_current']['bookings']; bk17 = M['global_w17']['bookings']
    gb18 = M['global_current']['gb_usd']; gb17 = M['global_w17']['gb_usd']
    tr18 = M['global_current']['trafico']
    n_hot = M['global_current']['n_hoteles']
    n_p80 = len(p80_hotel)
    
    pct_wow = (pct - pct17) * 100
    rpm_wow = (rpm/rpm17 - 1) * 100 if rpm17 else 0
    
    h1 = (f'<span style="display:block;">{fmt_pct2(pct)} de búsquedas sin disponibilidad y IPM de {fmt_num2(rpm)} · '
          f'concentración crítica en <span class="accent">{top_dest[0]}</span>, '
          f'<span class="accent">{top_dest[1]}</span> y <span class="accent">{top_dest[2]}</span>.</span>'
          f'<span style="display:block;margin-top:.3em;">'
          f'<span class="accent">{top_corp[0]}</span>, '
          f'<span class="accent">{top_corp[1]}</span> y '
          f'<span class="accent">{top_corp[2]}</span> son los corporativos con mayor demanda no convertida.</span>')
    
    subhead = (f'<strong style="font-weight:700;color:var(--ink);">Tráfico:</strong> <strong style="color:#EA0074;font-weight:700;">{fmt_big(tr18)}</strong> · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_hot)}</strong> hoteles · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(bk18)}</strong> Bookings · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_usd(gb18)}</strong> GB · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_p80)}</strong> hoteles P80.')
    
    return h1, subhead, pct, rpm, pct17, rpm17, pct_wow, rpm_wow

def render_kpi_card_nodispo(pct_w18, pct_w17, pct_wow):
    banda = banda_nodispo(pct_w18)
    target = "&lt; 3%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'nodispo')
    
    wow_color = '#2F6C34' if pct_wow < 0 else '#C0392B'  # mejor si baja
    wow_arrow = '↓' if pct_wow < 0 else ('↑' if pct_wow > 0 else '=')
    wow_str = f'{wow_arrow} {abs(pct_wow):+.2f}'.replace('+', '').replace('.', ',')
    if pct_wow < 0: wow_str = f'{wow_arrow} -{abs(pct_wow):.2f}'.replace('.', ',')
    elif pct_wow > 0: wow_str = f'{wow_arrow} +{pct_wow:.2f}'.replace('.', ',')
    else: wow_str = '= 0,00'
    
    wow_block = wow_box(fmt_pct2(pct_w17), fmt_pct2(pct_w18), wow_str, wow_color, ACCENT)
    # Prop V1: NoDispo baja = buena → invertir signo para que verde = mejora
    _wow_pill_nd = wow_pill_html(-pct_wow, unit='', prefix_pos='↓', prefix_neg='↑')
    
    # Línea de tráfico — helper centralizado
    _tr18 = M['global_current'].get('trafico', 0)
    _tr17 = M.get('global_w17', {}).get('trafico', 0)
    _traf_line = render_traf_line_rnd(_tr18, _tr17)
    
    # Tabs panels — pills onclick verdes (migrado del sistema CR · W24)
    _PILL_ACTIVE = 'border:1px solid #EA0074;background:#FCE4F1;color:#EA0074;text-transform:uppercase;'
    _PILL_INACT  = 'border:1px solid #EA0074;background:transparent;color:#EA0074;text-transform:uppercase;'
    _PILL_STYLE  = 'font-size:9px;font-weight:700;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;'
    tabs = ''
    for i, (t_key, t_label) in enumerate([('pais','País'),('destino','Destino'),('corp','Corp'),('hotel','Hotel')]):
        tabs += _kpi_pill('nd', t_key, t_label, _PILL_STYLE, _PILL_ACTIVE if i==0 else _PILL_INACT)

    # ── Config centralizada NoDispo ─────────────────────────────────────────────
    _ND_CFG = {
        'val_col':       '%NoDispo',
        'val_fmt':       fmt_pct2,
        'hist_scale':    lambda v: round(float(v) * 100, 4),
        'hist_prev_col': '%NoDispo_W17',   # fallback: NoDispo_W17 / %NoDispo_W18
        'banda_fn':      banda_nodispo,
        'banda_col':     'BandaNoDispo',
        'traf_col':      'Trafico',
        'traf_fmt':      fmt_int_es,
        'traf_wow_col':  'Trafico_WoW_pct',
        'traf_wow_type': 'pct',
        'wow_col':       'NoDispo_WoW_pp',
        'wow_is_pos':    False,            # NoDispo: bajar = mejorar
        'grid_cols':     'minmax(0,1fr) 72px 52px 74px 46px',
        'show_severity': False,
    }
    _ND_HDR = {'headers': ['Tráfico','WoW','%NoDispo','WoW'],
               'widths':  'minmax(0,1fr) 72px 52px 74px 46px'}
    # ────────────────────────────────────────────────────────────────────────────

    panels = ''
    for t_key, t_label, df_t in [
        ('pais','País', TAB_NoDispo['pais']),
        ('destino','Destino', TAB_NoDispo['destino']),
        ('corp','Corp', TAB_NoDispo['corp']),
        ('hotel','Hotel', TAB_NoDispo['hotel']),
    ]:
        # ── Helper centralizado — val_col buscado con fallbacks de NoDispo ─────
        # Para NoDispo la columna puede llamarse %NoDispo, pct_nodispo, nodispo
        # Normalizar df_t para que siempre tenga '%NoDispo'
        _df = df_t.copy()
        if '%NoDispo' not in _df.columns:
            for _alt in ('pct_nodispo','nodispo'):
                if _alt in _df.columns:
                    _df = _df.rename(columns={_alt: '%NoDispo'})
                    break
        # Fallback hist_prev: puede ser %NoDispo_W17, NoDispo_W17 o %NoDispo_W18
        for _hcol in ('%NoDispo_W17','NoDispo_W17','%NoDispo_W18'):
            if _hcol in _df.columns:
                _ND_CFG['hist_prev_col'] = _hcol
                break
        panels += build_kpi_tab_panel(_df, t_key, _ND_CFG, _ND_HDR, default_tab='pais')
    
    return f'''<div class="kpi-card" id="kpicard-nd" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">% de No Dispo</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div id="w21-kv-nd" style="font-size:40px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(pct_w18)}</div>
<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pill_nd}</div>
{_traf_line}
</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:14px;margin-bottom:2px;">{tabs}</div>
<div id="kpi-nd-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>
<div style="display:flex;justify-content:flex-start;margin-top:8px;margin-bottom:4px;">{searchbox_pill_html('sb-kpi-nd', accent_color='#EA0074', placeholder='Buscar…', count_id='cnt-kpi-nd')}</div>
<div id="kpi-nd-panels" class="tab-panels">{panels}</div>
<div style='margin-top:12px;border-top:1px solid var(--rule);padding-top:10px;'><span id='hist-hrnd-panel-nd-label' style='font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#EA0074;display:block;margin-bottom:6px;'>Global</span>{_rhs('rnd','nodispo',banda,pct_w18,'hrnd-panel-nd')}</div>
</div>'''


def render_alerts_block():
    """Banner alertas hero · 3 columnas: Hoteles, Destinos, Corp"""
    # Hotel con peor %NoDispo + Hotel con peor RPM (BKGS>0, RPM>0, alto tráfico)
    g_p80 = p80_hotel
    h_nd = g_p80[g_p80['Trafico']>g_p80['Trafico'].quantile(0.50)].sort_values('%NoDispo', ascending=False).iloc[0]
    h_rpm_pool = g_p80[(g_p80['Bookings']>0) & (g_p80['RPM']>0) & (g_p80['Trafico']>g_p80['Trafico'].quantile(0.50))]
    h_rpm = h_rpm_pool.sort_values('RPM').iloc[0]
    
    # Destinos · filtrar RPM>0 para evitar negativos (refunds)
    d_nd = TAB_NoDispo['destino'].iloc[0]
    d_rpm_pool = TAB_RPM['destino'][TAB_RPM['destino']['RPM']>0]
    d_rpm = d_rpm_pool.iloc[0] if len(d_rpm_pool)>0 else TAB_RPM['destino'].iloc[0]
    
    # Corp · filtrar RPM>0
    c_nd = TAB_NoDispo['corp'].iloc[0]
    c_rpm_pool = TAB_RPM['corp'][TAB_RPM['corp']['RPM']>0]
    c_rpm = c_rpm_pool.iloc[0] if len(c_rpm_pool)>0 else TAB_RPM['corp'].iloc[0]
    
    def alert_card(title, icon, color_b, items):
        cells = ''
        for it in items:
            cells += (f'<div style="background:#FAF7F2;padding:8px 10px;border-radius:3px;border:1px solid var(--rule-soft);">'
                      f'<div style="font-size:9px;font-weight:700;color:{it["pill_color"]};background:{it["pill_bg"]};padding:2px 5px;border-radius:2px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;">{it["pill"]}</div>'
                      f'<div style="font-size:10px;font-weight:700;color:var(--ink);line-height:1.2;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["name"]}</div>'
                      f'<div style="font-size:7px;color:var(--ink-muted);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["sub"]}</div>'
                      f'<div style="font-size:18px;font-weight:600;color:{it["pill_color"]};margin-top:6px;letter-spacing:-.02em;line-height:1;">{it["value"]}</div>'
                      f'<div style="font-size:8px;color:var(--ink-muted);margin-top:3px;line-height:1.4;">{it["foot"]}</div>'
                      f'</div>')
        return (f'<div style="background:#F2EDE0;border-radius:4px;padding:10px;border-top:3px solid {color_b};">'
                f'<div style="font-size:10px;font-weight:700;color:{color_b};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px;">'
                f'<span>{icon}</span><span>{title}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{cells}</div></div>')
    
    h_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(clean_hotel_name(h_nd['Hotel']),38),'sub':f'{h_nd["CorpName"]} · {h_nd["Destino"]}',
         'value':fmt_pct2(h_nd['%NoDispo']),'foot':f'{fmt_big(h_nd["Trafico"])} · {int(h_nd["Bookings"])} BKGS'},
        {'pill':'IPM','pill_color':'#5C469C','pill_bg':'#EDE9F8',
         'name':truncate(clean_hotel_name(h_rpm['Hotel']),38),'sub':f'{h_rpm["CorpName"]} · {h_rpm["Destino"]}',
         'value':fmt_num2(h_rpm['RPM']),'foot':f'{fmt_big(h_rpm["Trafico"])} · {int(h_rpm["Bookings"])} BKGS'},
    ]
    d_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(d_nd['Destino'],38),'sub':f'{fmt_big(d_nd["Trafico"])} · {int(d_nd["Bookings"])} BKGS',
         'value':fmt_pct2(d_nd['%NoDispo']),'foot':f'IPM {fmt_num2(d_nd["RPM"])}'},
        {'pill':'IPM','pill_color':'#5C469C','pill_bg':'#EDE9F8',
         'name':truncate(d_rpm['Destino'],38),'sub':f'{fmt_big(d_rpm["Trafico"])} · {int(d_rpm["Bookings"])} BKGS',
         'value':fmt_num2(d_rpm['RPM']),'foot':f'%ND {fmt_pct2(d_rpm["%NoDispo"])}'},
    ]
    c_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(c_nd['CorpName'],38),'sub':f'{fmt_big(c_nd["Trafico"])} · {int(c_nd["Bookings"])} BKGS',
         'value':fmt_pct2(c_nd['%NoDispo']),'foot':f'IPM {fmt_num2(c_nd["RPM"])}'},
        {'pill':'IPM','pill_color':'#5C469C','pill_bg':'#EDE9F8',
         'name':truncate(c_rpm['CorpName'],38),'sub':f'{fmt_big(c_rpm["Trafico"])} · {int(c_rpm["Bookings"])} BKGS',
         'value':fmt_num2(c_rpm['RPM']),'foot':f'%ND {fmt_pct2(c_rpm["%NoDispo"])}'},
    ]
    
    cards = (alert_card('Hoteles','🏨','#EA0074',h_items) +
             alert_card('Destinos','📍','#EA0074',d_items) +
             alert_card('Corp','🏛','#EA0074',c_items))
    return f'''<div class="alerts-block" style="margin:0 0 24px;">
<div style="font-size:11px;color:#EA0074;font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
<span>📍</span><span>Alertas · Casos Críticos de la Semana</span>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr));gap:14px;">{cards}</div>
</div>'''

# Build hero
h1, subhead, pct18, _rpm18, pct17, _rpm17, pct_wow, _rpm_wow = render_hero()
HERO = f'''<section class="hero" id="kpis-hero-section">
<div class="kpis-hero" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:14px;margin:6px 0 12px;">
{render_kpi_card_nodispo(pct18, pct17, pct_wow)}
</div>
<p class="hero-subhead" style="font-size:13px;color:var(--ink-muted);margin:0 0 24px;line-height:1.5;">{subhead}</p>
</section>
'''

import json as _json_rnd
import math as _math_rnd

def _build_rnd_card_tabs_json():
    """Genera JSON RND_CARD_TABS con datos para sort en cards KPI NoDispo e IPM."""
    CANASTA_BY = D.get('CANASTA', {})
    result = {}
    _AGG_BY_TKEY = {'pais':'agg_pais', 'destino':'agg_dest', 'corp':'agg_corp', 'hotel':'agg_hotel'}
    _GLOBAL_SRC = {
        'pais':    (TAB_NoDispo['pais'],    TAB_RPM['pais']),
        'destino': (TAB_NoDispo['destino'], TAB_RPM['destino']),
        'corp':    (TAB_NoDispo['corp'],    TAB_RPM['corp']),
        'hotel':   (TAB_NoDispo['hotel'],   TAB_RPM['hotel']),
    }
    for canasta_key, tab_key in [('global','global'),('b2c','B2C'),('op','B2B-OP'),('cug','CUG')]:
        # Desglose per-canasta: cada canasta es un subset del Global (por DistributionCategory).
        # Global usa TAB_NoDispo/TAB_RPM; las canastas usan sus propios agg_* del pickle
        # (CANASTA[c]). El row-builder re-ordena cada df (nd por %NoDispo desc · ipm por IPM asc).
        _c = CANASTA_BY.get(canasta_key) if canasta_key != 'global' else None
        nd_rows, ipm_rows = [], []
        for t_key in ['pais', 'destino', 'corp', 'hotel']:
            _agg = _c.get(_AGG_BY_TKEY[t_key]) if _c is not None else None
            if _agg is not None and len(_agg):
                df_nd = df_ipm = _agg
            else:
                df_nd, df_ipm = _GLOBAL_SRC[t_key]
            _name_col = {'pais':'PaisDestino','destino':'Destino','corp':'CorpName','hotel':'Hotel'}.get(t_key,'Destino')
            # NoDispo rows: ordenar peor primero (mayor %NoDispo)
            df_nd_s = df_nd.sort_values('%NoDispo', ascending=False).head(500)
            nd_tab = []
            for _, r in df_nd_s.iterrows():
                lab      = str(r.get(_name_col, '?'))[:60]
                nd       = r.get('%NoDispo', 0)
                traf     = r.get('Trafico', 0)
                traf_wow = r.get('Trafico_WoW_pct', None)
                wow      = r.get('NoDispo_WoW_pp', None)
                w21      = round(nd * 100, 4)
                bnd      = banda_nodispo(nd)
                bc       = BANDA_COLORS.get(bnd, {})
                traf_str = fmt_big(traf) if traf else '0'
                _cfc = str(r.get('CorpName', '') or '')
                _cfd = str(r.get('Destino', '') or '')
                _cfp = str(r.get('PaisDestino', '') or '')
                nd_tab.append([
                    lab,
                    '',              # r[1] sub
                    bc.get('bg','#F2EEE6'), bc.get('fg','#5F5E5A'), bnd,
                    traf_str,        # r[5] tráfico abreviado (6,9M)
                    round(float(traf_wow), 2) if traf_wow is not None and not _math_rnd.isnan(float(traf_wow)) else None,  # r[6] wow tráfico %
                    round(nd * 100, 2),   # r[7] val_pct
                    round(float(wow), 2) if wow is not None and not _math_rnd.isnan(float(wow)) else None,  # r[8] wow val
                    w21,                                                # r[9]  hist_w21
                    round((nd - r.get('%NoDispo_W18', nd)) * 100, 4),   # r[10] hist_w20
                    _cfc, _cfd, _cfp,                                   # r[11] corp, r[12] dest, r[13] pais
                ])
            # IPM rows: ordenar peor primero (menor IPM)
            df_ipm_s = df_ipm[df_ipm['Bookings'] > 0].sort_values('IPM', ascending=True).head(500)
            ipm_tab = []
            for _, r in df_ipm_s.iterrows():
                lab      = str(r.get(_name_col, '?'))[:60]
                ipm      = r.get('IPM', r.get('RPM', 0))
                traf     = r.get('Trafico', 0)
                traf_wow = r.get('Trafico_WoW_pct', None)
                wow      = r.get('IPM_WoW_pp', None)
                bnd      = banda_rpm(ipm, int(r.get('Bookings', 1)))
                bc       = BANDA_COLORS.get(bnd, {})
                traf_str = fmt_big(traf) if traf else '0'
                ipm_tab.append([
                    lab,
                    '',              # r[1] sub
                    bc.get('bg','#F2EEE6'), bc.get('fg','#5F5E5A'), bnd,
                    traf_str,        # r[5] tráfico abreviado
                    round(float(traf_wow), 2) if traf_wow is not None and not _math_rnd.isnan(float(traf_wow)) else None,  # r[6] wow tráfico %
                    round(ipm, 2),   # r[7] val_pct
                    round(float(wow), 2) if wow is not None and not _math_rnd.isnan(float(wow)) else None,  # r[8] wow val
                    round(ipm, 4),   # r[9]  hist_w21
                    0,               # r[10] hist_w20
                    str(r.get('CorpName','') or ''), str(r.get('Destino','') or ''), str(r.get('PaisDestino','') or ''),  # r[11,12,13]
                ])
            nd_rows_map  = nd_rows if t_key == 'hotel' else None
            ipm_rows_map = ipm_rows if t_key == 'hotel' else None
            result.setdefault(canasta_key, {}).setdefault('nd', {})[t_key]  = nd_tab
            result.setdefault(canasta_key, {}).setdefault('ipm', {})[t_key] = ipm_tab
    return f'\n<script>\nvar RND_CARD_TABS={_json_rnd.dumps(result, ensure_ascii=False, default=lambda x: None)};\n</script>\n'

def _build_rnd_membership_json():
    """Mapa de membresía corp→destinos y corp→países (relación muchos-a-muchos).
    Permite el cross-filter Corp→Destino / Corp→País / Destino→Corp / País→Corp
    en las cards KPI (un destino tiene muchos corps, así que el data-cf-corp por fila
    no alcanza). Se construye desde g_hotel (TODOS los hoteles, no solo top-500)."""
    corp_dest, corp_pais = {}, {}
    dest_pais = {}
    try:
        gh = g_hotel[['CorpName', 'Destino', 'PaisDestino']].copy()
        for _, r in gh.iterrows():
            c = str(r.get('CorpName', '') or '').strip()
            d = str(r.get('Destino', '') or '').strip()
            p = str(r.get('PaisDestino', '') or '').strip()
            if d and p:
                dest_pais[d] = p          # cada destino tiene 1 país
            if not c:
                continue
            if d:
                corp_dest.setdefault(c, set()).add(d)
            if p:
                corp_pais.setdefault(c, set()).add(p)
    except Exception:
        pass
    corp_dest = {k: sorted(v) for k, v in corp_dest.items()}
    corp_pais = {k: sorted(v) for k, v in corp_pais.items()}
    payload = {'corpDest': corp_dest, 'corpPais': corp_pais, 'destPais': dest_pais}
    return ('\n<script>\nvar RND_MEMBERSHIP='
            + _json_rnd.dumps(payload, ensure_ascii=False)
            + ';\n</script>\n')


def _build_rnd_hotel_pool_json():
    """Pool COMPLETO de hoteles (~21K) para el cross-filter →hotel en las KPI cards RND.
    Compacto y NO en el DOM: el JS arma las filas del subconjunto cruzado on-demand
    (B · W24). Resuelve C/D — corp/dest/país →hotel alcanzaban solo el top-500/100.
    Formato fila (12 campos):
      [label, corp, dest, pais, traf_str, traf_wow,
       nd_pct, nd_bidx, nd_wow, ipm_val, ipm_bidx, ipm_wow]
    Banda como índice 0-5 → _RND_BAND_NAMES → _AR_BANDA_C (colores) en JS."""
    _BIDX = {'Exitosa': 0, 'Aceptable': 1, 'Revisar': 2, 'Crítica': 3,
             'Súper Crítica': 4, 'Sin Conversión': 5}

    def _num(v, ndig=2):
        try:
            f = float(v)
            if _math_rnd.isnan(f) or _math_rnd.isinf(f):
                return None
            return round(f, ndig)
        except (TypeError, ValueError):
            return None

    pool = []
    for _, r in p80_hotel.iterrows():
        lab = truncate(clean_hotel_name(str(r.get('Hotel', ''))), 38)
        corp = str(r.get('CorpName', '') or '')
        dest = str(r.get('Destino', '') or '')
        pais = str(r.get('PaisDestino', '') or '')
        traf = r.get('Trafico', 0)
        traf_str = fmt_big(traf) if traf else '0'
        traf_wow = _num(r.get('Trafico_WoW_pct'))
        nd = r.get('%NoDispo')
        nd_pct = _num(nd * 100) if nd is not None else None
        nd_band = _BIDX.get(r.get('BandaNoDispo') or (banda_nodispo(nd) if nd is not None else 'Sin Conversión'), 5)
        nd_wow = _num(r.get('NoDispo_WoW_pp'))
        bk = r.get('Bookings', 0) or 0
        ipm = r.get('IPM')
        if bk > 0 and ipm is not None and float(ipm) > 0:
            ipm_val = _num(ipm)
            ipm_band = _BIDX.get(r.get('BandaRPM') or banda_rpm(ipm, int(bk)), 5)
            ipm_wow = _num(r.get('IPM_WoW_pp'))
        else:
            ipm_val = ipm_band = ipm_wow = None
        pool.append([lab, corp, dest, pais, traf_str, traf_wow,
                     nd_pct, nd_band, nd_wow, ipm_val, ipm_band, ipm_wow])
    return ('\n<script>\nvar RND_HOTEL_POOL='
            + _json_rnd.dumps(pool, ensure_ascii=False, default=lambda x: None)
            + ';\nvar _RND_BAND_NAMES=["Exitosa","Aceptable","Revisar","Cr\\u00edtica",'
              '"S\\u00faper Cr\\u00edtica","Sin Conversi\\u00f3n"];\n</script>\n')


def _build_rnd_hist_json():
    """Emite RND_CORP_HIST y RND_DEST_HIST con datos reales W18-W(N-1) por corp/dest."""
    hist = D.get('RND_HIST', {})
    semanas_prev = [f'W{n:02d}' for n in range(18, WEEK_NUM_INT)]

    def _entity_dict(bucket):
        out = {}
        for name, wdict in hist.get(bucket, {}).items():
            nd_vals  = [wdict.get(w, {}).get('nd')  for w in semanas_prev]
            ipm_vals = [wdict.get(w, {}).get('ipm') for w in semanas_prev]
            if any(v is not None for v in nd_vals):
                out[name] = {
                    'nd':  [round(v * 100, 2) if v is not None else None for v in nd_vals],
                    'ipm': [round(v, 0)        if v is not None else None for v in ipm_vals],
                }
        return out

    import json
    corp_js  = json.dumps(_entity_dict('corp'),  ensure_ascii=False, separators=(',', ':'))
    dest_js  = json.dumps(_entity_dict('dest'),  ensure_ascii=False, separators=(',', ':'))
    hotel_js = json.dumps(_entity_dict('hotel'), ensure_ascii=False, separators=(',', ':'))
    return (
        f'\n<script>\nvar RND_CORP_HIST={corp_js};\n'
        f'var RND_DEST_HIST={dest_js};\n'
        f'var RND_HOTEL_HIST={hotel_js};\n</script>\n'
    )


    """Pool COMPLETO de hoteles (~21K) para el cross-filter →hotel en las KPI cards RND.
    Compacto y NO en el DOM: el JS arma las filas del subconjunto cruzado on-demand
    (B · W24). Resuelve C/D — corp/dest/país →hotel alcanzaban solo el top-500/100.
    Formato fila (12 campos):
      [label, corp, dest, pais, traf_str, traf_wow,
       nd_pct, nd_bidx, nd_wow, ipm_val, ipm_bidx, ipm_wow]
    Banda como índice 0-5 → _RND_BAND_NAMES → _AR_BANDA_C (colores) en JS."""
    _BIDX = {'Exitosa': 0, 'Aceptable': 1, 'Revisar': 2, 'Crítica': 3,
             'Súper Crítica': 4, 'Sin Conversión': 5}

    def _num(v, ndig=2):
        try:
            f = float(v)
            if _math_rnd.isnan(f) or _math_rnd.isinf(f):
                return None
            return round(f, ndig)
        except (TypeError, ValueError):
            return None

    pool = []
    for _, r in p80_hotel.iterrows():
        lab = truncate(clean_hotel_name(str(r.get('Hotel', ''))), 38)
        corp = str(r.get('CorpName', '') or '')
        dest = str(r.get('Destino', '') or '')
        pais = str(r.get('PaisDestino', '') or '')
        traf = r.get('Trafico', 0)
        traf_str = fmt_big(traf) if traf else '0'
        traf_wow = _num(r.get('Trafico_WoW_pct'))
        nd = r.get('%NoDispo')
        nd_pct = _num(nd * 100) if nd is not None else None
        nd_band = _BIDX.get(r.get('BandaNoDispo') or (banda_nodispo(nd) if nd is not None else 'Sin Conversión'), 5)
        nd_wow = _num(r.get('NoDispo_WoW_pp'))
        bk = r.get('Bookings', 0) or 0
        ipm = r.get('IPM')
        if bk > 0 and ipm is not None and float(ipm) > 0:
            ipm_val = _num(ipm)
            ipm_band = _BIDX.get(r.get('BandaRPM') or banda_rpm(ipm, int(bk)), 5)
            ipm_wow = _num(r.get('IPM_WoW_pp'))
        else:
            ipm_val = ipm_band = ipm_wow = None
        pool.append([lab, corp, dest, pais, traf_str, traf_wow,
                     nd_pct, nd_band, nd_wow, ipm_val, ipm_band, ipm_wow])
    return ('\n<script>\nvar RND_HOTEL_POOL='
            + _json_rnd.dumps(pool, ensure_ascii=False, default=lambda x: None)
            + ';\nvar _RND_BAND_NAMES=["Exitosa","Aceptable","Revisar","Cr\\u00edtica",'
              '"S\\u00faper Cr\\u00edtica","Sin Conversi\\u00f3n"];\n</script>\n')


PART1 = (
    '\n<!-- ═══════════════ SECCIÓN RND ═══════════════ -->\n'
    '<section id="section-rnd" class="section-rnd">\n'
    + render_masthead()
    + HERO
    + _build_rnd_card_tabs_json()
    + _build_rnd_membership_json()
    + _build_rnd_hotel_pool_json()
    + _build_rnd_hist_json()
    + '''
<script>
// HIST_DATA: datos históricos RND W17-W21
if (!window.HIST_DATA) {
    window.HIST_DATA = {};
}
window.HIST_DATA['rnd'] = {
    'nodispo': {
        'global': [3.63, 2.84, 2.31, 2.59, 2.59],
        'op':     [3.18, 2.62, 1.93, 2.24, 2.19],
        'cug':    [4.34, 3.07, 2.73, 2.82, 2.78],
        'b2c':    [4.48, 3.68, 3.36, 3.31, 3.29],
    },
    'ipm': {
        'global': [574.0, 524.0, 499.0, 677.0, 834.0],
        'op':     [523.0, 534.0, 479.0, 688.0, 845.0],
        'cug':    [866.0, 659.0, 656.0, 787.0, 944.0],
        'b2c':    [183.0, 206.0, 188.0, 248.0, 304.0],
    },
};
</script>
'''
)

with open('part1_rnd.html', 'w', encoding='utf-8') as f:
    f.write(PART1)
print(f"Part 1 RND escrito: {len(PART1):,} chars")