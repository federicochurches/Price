"""
Renderer · Reporte Editorial CR W20
Genera HTML completo · sistema bandas D · post W17
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np
from engine import *
from render_helpers import *

# Cargar datos
with open(os.getenv('PICKLE_CR', 'cr_w21_data.pkl'),'rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']

# ── Cargar configuración semanal ──────────────────────────────────────────────────
VOL_NUM   = D.get('VOL_NUM', '20')
PERIODO   = D.get('PERIODO', '12–18 may 2026')
MES_AÑO   = D.get('MES_AÑO', 'Mayo 2026')
FECHA_PUB = D.get('FECHA_PUB', 'LUNES 18 de Mayo de 2026')
# ─────────────────────────────────────────────────────────────────────────────────

# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', {})
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', {})
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

TAB_EF = D['TAB_EF']; TAB_CV = D['TAB_CV']
CANASTA = D['CANASTA']
sev_ef = D['sev_ef']; sev_cv = D['sev_cv']
sev_ef_p80 = D['sev_ef_p80']; sev_cv_p80 = D['sev_cv_p80']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']
g_corp = D['g_corp']; g_channel = D['g_channel']; g_grupo = D['g_grupo']

# Cargar head
with open('asset_cr_head.html') as f: HEAD = f.read()

# ============ MASTHEAD ============
def _kpi_pill(card, key, label, base_style, active_style):
    """Genera un span pill de vista para cards KPI con onclick correcto."""
    onclick = "kpi_setView('" + card + "','" + key + "',this)"
    return ('<span id="kpi-' + card + '-v-' + key + '" class="kpi-' + card + '-vpill"'
            ' onclick="' + onclick + '"'
            ' style="' + base_style + active_style + '">' + label + '</span>')


def _kpi_view_pill_bk(key, label, active):
    """Pills de vista para card Bookability."""
    _PA = 'border:1px solid #5C469C;background:#EDE8F7;color:#5C469C;text-transform:uppercase;'
    _PI = 'border:1px solid #5C469C;background:transparent;color:#5C469C;text-transform:uppercase;'
    _PS = 'font-size:9px;font-weight:700;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;'
    st = _PA if active else _PI
    return _kpi_pill('bk', key, label, _PS, st)


def render_masthead():
    LOGO = "data:image/png;base64,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"

    g22 = M.get(f'global_w{WEEK_NUM_INT}', {})
    CR_UNICOS_FMT = fmt_int_es(g22.get('cr_unicos', 0))
    N_HOTELES_FMT = fmt_int_es(g22.get('n_hoteles', 0))
    BOOKINGS_FMT  = fmt_int_es(g22.get('bookings', 0))
    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div class="masthead-inner" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div class="masthead-left">
<div style="display:inline-block;background:#EA0074;color:#fff;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 9px;border-radius:3px;margin-bottom:6px;">Week {WEEK_NUM_INT}</div>
<h1 style="margin:6px 0 4px;font-size:clamp(20px,2.0vw,30px);font-weight:800;letter-spacing:-.03em;line-height:1.05;"><span style="color:#EA0074;">Connectivities </span><span style="color:var(--ink);">&amp; Hotel </span><span style="color:#EA0074;">Availability</span></h1>
<div style="font-size:10px;font-weight:500;color:var(--ink-muted);margin-top:6px;letter-spacing:.06em;text-transform:uppercase;"><strong style="color:#EA0074;font-weight:700;">{CR_UNICOS_FMT}</strong> CheckRates · <strong style="color:#EA0074;font-weight:700;">{N_HOTELES_FMT}</strong> hoteles P80 · Target: <strong style="color:#EA0074;font-weight:700;">{BOOKINGS_FMT}</strong> Bookings</div>
<div style="font-size:11px;font-weight:400;color:var(--ink-muted);margin-top:6px;">{FECHA_PUB}<span style="margin:0 16px;color:var(--rule);">|</span>Vol. {VOL_NUM}</div>
</div>
<div class="masthead-right" style="display:flex;align-items:center;gap:0;flex-shrink:0;">
<img alt="PriceTravel" src="{LOGO}" style="height:40px;width:auto;" class="masthead-logo"/>

</div>
</div>

</header>
'''

# ============ HERO H1 + KPIs + ALERTS ============
def calc_h1_data():
    """H1 narrativo CR: 2 líneas alineadas."""
    ef = M['global_current']['eficacia']
    cv = M['global_current']['conv_rate']
    # Top 3 destinos por volumen CR (sobre P80)
    g_d_p80 = p80_hotel.groupby('Destino').agg(
        CR=('CR_Unicos','sum'),
        Bookings=('Bookings','sum')
    ).reset_index().sort_values('CR', ascending=False).head(3)
    top_dest = g_d_p80['Destino'].tolist()
    # Top 3 corp por volumen CR
    g_c_p80 = p80_hotel.groupby('CorpName').agg(
        CR=('CR_Unicos','sum'),
        Bookings=('Bookings','sum')
    ).reset_index().sort_values('CR', ascending=False).head(3)
    top_corp = g_c_p80['CorpName'].tolist()
    return ef, cv, top_dest, top_corp

def render_hero():
    ef, cv, top_dest, top_corp = calc_h1_data()
    ef17 = M['global_w17']['eficacia']
    cv17 = M['global_w17']['conv_rate']
    bk18 = M['global_current']['bookings']; bk17 = M['global_w17']['bookings']
    cr18 = M['global_current']['cr_unicos']
    n_hot = M['global_current']['n_hoteles']
    n_p80 = len(p80_hotel)
    
    ef_wow = (ef - ef17) * 100  # pp
    cv_wow = (cv - cv17) * 100  # pp
    
    h1 = (f'<span style="display:block;">Eficacia de {fmt_pct2(ef)} y Conversion Rate de {fmt_pct2(cv)} · '
          f'volumen concentrado en <span class="accent">{top_dest[0]}</span>, '
          f'<span class="accent">{top_dest[1]}</span> y <span class="accent">{top_dest[2]}</span>.</span>'
          f'<span style="display:block;margin-top:.3em;">'
          f'<span class="accent">{top_corp[0]}</span>, '
          f'<span class="accent">{top_corp[1]}</span> y '
          f'<span class="accent">{top_corp[2]}</span> son los corporativos con más check-rates de la semana.</span>')
    
    subhead = (f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(cr18)}</strong> Tráfico · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(n_hot)}</strong> hoteles · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(bk18)}</strong> Bookings · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(n_p80)}</strong> hoteles P80.')
    
    return h1, subhead, ef, cv, ef17, cv17, ef_wow, cv_wow

# Color de acento CR (cyan/teal)
CR_ACCENT = '#5C469C'

from historico_module import render_historico
from render_historico_svg import render_historico_svg as _rhs

def _cr_trafico_line():
    """Mini-fila con CR Únicos globales y WoW — delegada al helper centralizado."""
    cr_w21 = M['global_current'].get('cr_unicos', 0)
    cr_w17_val = M.get('global_w17', {}).get('cr_unicos')
    return render_traf_line_cr(cr_w21, cr_w17_val)

def _mini_badge(bnd):
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span class="sev-badge" style="background:{bg};color:{fg};">{bnd}</span>'


def render_kpi_card_eficacia(ef_w18, ef_w17, ef_wow, week_num=f'W{WEEK_NUM_INT}', week_prev=f'W{WEEK_PREV_INT}'):
    banda = banda_eficacia(ef_w18)
    target = "≥ 97%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'eficacia')
    
    wow_color = '#2F6C34' if ef_wow > 0 else '#C0392B'
    wow_arrow = '↑' if ef_wow > 0 else ('↓' if ef_wow < 0 else '=')
    if ef_wow > 0: wow_str = f'{wow_arrow} +{ef_wow:.2f}'.replace('.', ',')
    elif ef_wow < 0: wow_str = f'{wow_arrow} {ef_wow:.2f}'.replace('.', ',')
    else: wow_str = '= 0,00'
    
    wow_block = wow_box(fmt_pct2(ef_w17), fmt_pct2(ef_w18), wow_str, wow_color, CR_ACCENT, week_num, week_prev)
    # Prop V1: pill WoW redondeada (+ = verde, - = rojo)
    _wow_pill_ef = wow_pill_html(ef_wow, unit='')
    cr_trafico_line = _cr_trafico_line()
    
    # Pills de vista — mismo patrón que AR (onclick, no CSS radio)
    _PILL_ACTIVE = 'border:1px solid #5C469C;background:#EDE8F7;color:#5C469C;text-transform:uppercase;'
    _PILL_INACT  = 'border:1px solid #5C469C;background:transparent;color:#5C469C;text-transform:uppercase;'
    _PILL_STYLE  = 'font-size:9px;font-weight:700;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;'
    tabs = ''
    for i, (t_key, t_label) in enumerate([('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel')]):
        _active_style = _PILL_ACTIVE if i == 0 else _PILL_INACT
        tabs += _kpi_pill('ef', t_key, t_label, _PILL_STYLE, _PILL_ACTIVE if i==0 else _PILL_INACT)
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds','Hotel Unico','Travelgate']

    # ── Config centralizada — 1 sola línea controla grid, top_n, etc. ──────────
    _EF_CFG = {
        'val_col':       'Eficacia',
        'val_fmt':       fmt_pct2,
        'hist_scale':    lambda v: round(float(v) * 100, 4),
        'hist_prev_col': 'Eficacia_W17',
        'banda_fn':      banda_eficacia,
        'banda_col':     'BandaEficacia',
        'traf_col':      'CR_Unicos',
        'traf_fmt':      fmt_int_es,
        'traf_wow_col':  'CR_Unicos_WoW_pp',
        'traf_wow_type': 'abs',     # viene escalado ×100, reescalamos /100 → abs delta
        'wow_col':       'Eficacia_WoW_pp',
        'wow_is_pos':    True,
        'grid_cols':     'minmax(0,1fr) 80px 56px 54px 48px',
        'show_severity': False,
    }
    _EF_HDR = {'headers': ['Tráfico','WoW','Eficacia','WoW'],
               'widths':  'minmax(0,1fr) 80px 56px 54px 48px'}
    # ────────────────────────────────────────────────────────────────────────────

    panels = ''
    for t_key, df_t in [
        ('destino', TAB_EF['destino']),
        ('corp', TAB_EF['corp']),
        ('hotel', TAB_EF['hotel'].head(5)),  # static: solo estructura+fallback; _kpiSortAttach(crit) + motor lazy (pool) re-renderizan
        ('channel', TAB_EF['channel']),
        ('canasta', TAB_EF['canasta']),
    ]:
        if t_key == 'channel':
            # Split en Producto Propio + Third Party — catálogo canónico fijo
            def _lookup_chan(nombre, df_src):
                mask = df_src['ExternalProviderName'].str.startswith(nombre) if nombre == 'HotelBeds' else df_src['ExternalProviderName'] == nombre
                hits = df_src[mask]
                return hits.iloc[0] if len(hits) > 0 else None

            def _sorted_canonical(lista, df_src, val_col):
                with_data = []
                for nombre in lista:
                    r = _lookup_chan(nombre, df_src)
                    if r is not None:
                        with_data.append((nombre, r))
                with_data.sort(key=lambda x: x[1][val_col] if not (x[1][val_col] != x[1][val_col]) else 999)
                return with_data

            _pp_sorted = _sorted_canonical(PRODUCTO_PROPIO, df_t, 'Eficacia')
            _tp_sorted = _sorted_canonical(THIRD_PARTY, df_t, 'Eficacia')

            def chan_row(i, nombre, r, val_col):
                import math
                if r is None: return ''
                raw_val = r[val_col] if val_col in r.index else float('nan')
                if raw_val != raw_val or (isinstance(raw_val, float) and math.isinf(raw_val)):
                    val_str = '—'
                else:
                    val_str = fmt_pct2(raw_val)
                # TRX (CR_Unicos)
                cr_u = r.get('CR_Unicos', 0)
                trx_str = fmt_int_es(int(cr_u)) if cr_u and cr_u == cr_u else '—'
                wow_col_k = val_col + '_WoW_pp'
                try:
                    wow_v = r[wow_col_k]
                    if wow_v != wow_v: raise ValueError
                    if abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'; wb = '#EAF3DE' if mejora else '#FCE8E6'
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};white-space:nowrap;">{"+" if wow_v>0 else ""}{wow_v:.2f}'.replace('.', ',') + '</em>'
                    else:
                        wow_pill = '<span style="color:var(--ink-muted);font-size:10px;">—</span>'
                except:
                    wow_pill = '<span style="color:var(--ink-muted);font-size:10px;">—</span>'
                _w21 = round(float(raw_val)*100, 4) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isnan(raw_val)) else 0
                _lbl = str(r.get('ExternalProviderName', nombre))
                # data-* para sort (reusa la maquinaria de bkSort: data-lbl/trx/trx-wow/bk/bk-wow)
                _trx_int = int(cr_u) if cr_u and cr_u == cr_u else 0
                _bk_val  = float(raw_val) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isinf(raw_val)) else 0
                try:
                    _wv = r[wow_col_k]; _bk_wow_v = _wv if _wv == _wv else 0
                except Exception:
                    _bk_wow_v = 0
                # Grid de 4 cols (BK style): nombre · TRX · valor · WoW — clase bk-row para sort+selección
                return (f'<div class="bk-row" data-lbl="{_lbl}" data-trx="{_trx_int}" data-trx-wow="0" '
                        f'data-bk="{_bk_val:.6f}" data-bk-wow="{_bk_wow_v:.6f}" '
                        f'data-hist-w21="{_w21}" '
                        f'data-hist-w20="{round(_w21 - _bk_wow_v * 100, 4)}"'
                        f' data-hist-label="{_lbl}"'
                        f' style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;width:100%;">'
                        f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;font-size:11px;color:var(--ink);">{_lbl}</span>'
                        f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">{trx_str}</span>'
                        f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">{val_str}</span>'
                        f'<div style="text-align:right;">{wow_pill}</div>'
                        f'</div>')

            rows_pp = ''.join(chan_row(i, nombre, r, 'Eficacia') for i, (nombre, r) in enumerate(_pp_sorted))
            rows_tp = ''.join(chan_row(i, nombre, r, 'Eficacia') for i, (nombre, r) in enumerate(_tp_sorted))
            _metric_lbl = 'Eficacia'
            _hdr_chan = lambda lbl, acc: (
                f'<div class="bk-sort-hdr" style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;width:100%;'
                f'align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid {acc};margin-bottom:2px;">'
                f'<span data-sort-key="lbl" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);cursor:pointer;user-select:none;">Channel <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="trx" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">Trx <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{acc};text-align:right;cursor:pointer;user-select:none;">{lbl} <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk-wow" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">WoW <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'</div>'
            )
            chan_html = (
                f'<div class="chan-wrap" style="display:flex;flex-direction:column;gap:14px;width:100%;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{_hdr_chan(_metric_lbl, "#5C469C")}{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{_hdr_chan(_metric_lbl, "#5C469C")}{rows_tp}</div>'
                f'</div>'
            )
            _h = ' style="display:none;"' if t_key != 'destino' else ''
            panels += f'<div class="tab-panel" data-tab="{t_key}"{_h}>{chan_html}</div>'
            continue

        # ── Filas generadas por helper centralizado ───────────────────────────
        panels += build_kpi_tab_panel(df_t, t_key, _EF_CFG, _EF_HDR)
    
    return f'''<div class="kpi-card" id="kpicard-ef" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);display:flex;flex-direction:column;">

<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Eficacia</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div id="w21-kv-ef" style="font-size:40px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(ef_w18)}</div>

</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:14px;margin-bottom:2px;">{tabs}</div>
<div id="kpi-ef-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>
<div id="kpi-ef-hfilt" style="display:none;"></div>
<div style="display:flex;justify-content:flex-start;margin-top:8px;margin-bottom:4px;">{searchbox_pill_html('sb-kpi-ef', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-kpi-ef')}</div>
<div id="kpi-ef-panels" class="tab-panels">{panels}</div>
<div style='margin-top:12px;border-top:1px solid var(--rule);padding-top:10px;'><span id='hist-hcr-panel-ef-label' style='font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#5C469C;display:block;margin-bottom:6px;'>Global</span>{_rhs('cr','eficacia',banda,ef_w18,'hcr-panel-ef')}</div>
</div>'''

def render_kpi_card_convrate(cv_w18, cv_w17, cv_wow, week_num=f'W{WEEK_NUM_INT}', week_prev=f'W{WEEK_PREV_INT}'):
    banda = banda_convrate(cv_w18, M['global_current']['bookings'])
    target = "≥ 2,5%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'convrate')
    
    wow_color = '#2F6C34' if cv_wow > 0 else '#C0392B'
    wow_arrow = '↑' if cv_wow > 0 else ('↓' if cv_wow < 0 else '=')
    if cv_wow > 0: wow_str = f'{wow_arrow} +{cv_wow:.2f}'.replace('.', ',')
    elif cv_wow < 0: wow_str = f'{wow_arrow} {cv_wow:.2f}'.replace('.', ',')
    else: wow_str = '= 0,00'
    
    wow_block = wow_box(fmt_pct2(cv_w17), fmt_pct2(cv_w18), wow_str, wow_color, CR_ACCENT, week_num, week_prev)
    # Prop V1: pill WoW redondeada
    _wow_pill_cv = wow_pill_html(cv_wow, unit='')
    cr_trafico_line = _cr_trafico_line()
    
    # Pills de vista — mismo patrón que AR (onclick, no CSS radio)
    _PILL_ACTIVE = 'border:1px solid #5C469C;background:#EDE8F7;color:#5C469C;text-transform:uppercase;'
    _PILL_INACT  = 'border:1px solid #5C469C;background:transparent;color:#5C469C;text-transform:uppercase;'
    _PILL_STYLE  = 'font-size:9px;font-weight:700;letter-spacing:.07em;padding:4px 12px;border-radius:20px;cursor:pointer;white-space:nowrap;'
    tabs = ''
    for i, (t_key, t_label) in enumerate([('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel')]):
        _active_style = _PILL_ACTIVE if i == 0 else _PILL_INACT
        tabs += _kpi_pill('cv', t_key, t_label, _PILL_STYLE, _PILL_ACTIVE if i==0 else _PILL_INACT)
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds','Hotel Unico','Travelgate']

    # ── Config centralizada ConvRate ────────────────────────────────────────────
    _CV_CFG = {
        'val_col':       'ConvRate',
        'val_fmt':       fmt_pct2,
        'hist_scale':    lambda v: round(float(v) * 100, 4),
        'hist_prev_col': 'ConvRate_W17',
        'banda_fn':      lambda v: banda_convrate(v, 1),  # banda sin bkgs en tab (bkgs en card hero)
        'banda_col':     'BandaConvRate',
        'traf_col':      'CR_Unicos',
        'traf_fmt':      fmt_int_es,
        'traf_wow_col':  'CR_Unicos_WoW_pp',
        'traf_wow_type': 'abs',
        'wow_col':       'ConvRate_WoW_pp',
        'wow_is_pos':    True,
        'grid_cols':     'minmax(0,1fr) 80px 56px 68px 40px',
        'show_severity': False,
    }
    _CV_HDR = {'headers': ['Tráfico','WoW','Conv Rate','WoW'],
               'widths':  'minmax(0,1fr) 80px 56px 68px 40px'}
    # ────────────────────────────────────────────────────────────────────────────

    panels = ''
    for t_key, df_t in [
        ('destino', TAB_CV['destino']),
        ('corp', TAB_CV['corp']),
        ('hotel', TAB_CV['hotel'][TAB_CV['hotel']['Bookings'] > 0].sort_values('ConvRate').reset_index(drop=True).head(5)),  # static: solo estructura+fallback; _kpiSortAttach(crit) + motor lazy (pool) re-renderizan
        ('channel', TAB_CV['channel']),
        ('canasta', TAB_CV['canasta']),
    ]:
        if t_key == 'channel':
            def _lookup_chan_cv(nombre, df_src):
                mask = df_src['ExternalProviderName'].str.startswith(nombre) if nombre == 'HotelBeds' else df_src['ExternalProviderName'] == nombre
                hits = df_src[mask]
                return hits.iloc[0] if len(hits) > 0 else None

            def _sorted_canonical_cv(lista, df_src, val_col):
                with_data = []
                for nombre in lista:
                    r = _lookup_chan_cv(nombre, df_src)
                    if r is not None:
                        with_data.append((nombre, r))
                with_data.sort(key=lambda x: x[1][val_col] if not (x[1][val_col] != x[1][val_col]) else 999)
                return with_data

            _pp_sorted_cv = _sorted_canonical_cv(PRODUCTO_PROPIO, df_t, 'ConvRate')
            _tp_sorted_cv = _sorted_canonical_cv(THIRD_PARTY, df_t, 'ConvRate')

            def chan_row_cv(i, nombre, r, val_col):
                import math
                if r is None: return ''
                raw_val = r[val_col] if val_col in r.index else float('nan')
                val_str = fmt_pct2(raw_val) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isinf(raw_val)) else '—'
                # TRX
                cr_u = r.get('CR_Unicos', 0)
                trx_str = fmt_int_es(int(cr_u)) if cr_u and cr_u == cr_u else '—'
                wow_col_k = val_col + '_WoW_pp'
                try:
                    wow_v = r[wow_col_k]
                    if wow_v != wow_v: raise ValueError
                    if abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'; wb = '#EAF3DE' if mejora else '#FCE8E6'
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;background:{wb};color:{wc};white-space:nowrap;">{"+" if wow_v>0 else ""}{wow_v:.2f}'.replace('.', ',') + '</em>'
                    else:
                        wow_pill = '<span style="color:var(--ink-muted);font-size:10px;">—</span>'
                except:
                    wow_pill = '<span style="color:var(--ink-muted);font-size:10px;">—</span>'
                _w21 = round(float(raw_val)*100, 4) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isnan(raw_val)) else 0
                _lbl = str(r.get('ExternalProviderName', nombre))
                _trx_int = int(cr_u) if cr_u and cr_u == cr_u else 0
                _bk_val  = float(raw_val) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isinf(raw_val)) else 0
                try:
                    _wv = r[wow_col_k]; _bk_wow_v = _wv if _wv == _wv else 0
                except Exception:
                    _bk_wow_v = 0
                return (f'<div class="bk-row" data-lbl="{_lbl}" data-trx="{_trx_int}" data-trx-wow="0" '
                        f'data-bk="{_bk_val:.6f}" data-bk-wow="{_bk_wow_v:.6f}" '
                        f'data-hist-w21="{_w21}" '
                        f'data-hist-w20="{round(_w21 - _bk_wow_v * 100, 4)}"'
                        f' data-hist-label="{_lbl}"'
                        f' style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;width:100%;">'
                        f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;font-size:11px;color:var(--ink);">{_lbl}</span>'
                        f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">{trx_str}</span>'
                        f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;">{val_str}</span>'
                        f'<div style="text-align:right;">{wow_pill}</div>'
                        f'</div>')

            rows_pp = ''.join(chan_row_cv(i, nombre, r, 'ConvRate') for i, (nombre, r) in enumerate(_pp_sorted_cv))
            rows_tp = ''.join(chan_row_cv(i, nombre, r, 'ConvRate') for i, (nombre, r) in enumerate(_tp_sorted_cv))
            _metric_lbl = 'ConvRate'
            _hdr_chan = lambda lbl, acc: (
                f'<div class="bk-sort-hdr" style="display:grid;grid-template-columns:minmax(0,1fr) 52px 72px 48px;width:100%;'
                f'align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid {acc};margin-bottom:2px;">'
                f'<span data-sort-key="lbl" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);cursor:pointer;user-select:none;">Channel <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="trx" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">Trx <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{acc};text-align:right;cursor:pointer;user-select:none;">{lbl} <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk-wow" style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">WoW <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'</div>'
            )
            chan_html = (
                f'<div class="chan-wrap" style="display:flex;flex-direction:column;gap:14px;width:100%;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{_hdr_chan(_metric_lbl, "#5C469C")}{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{_hdr_chan(_metric_lbl, "#5C469C")}{rows_tp}</div>'
                f'</div>'
            )
            _h = ' style="display:none;"' if t_key != 'destino' else ''
            panels += f'<div class="tab-panel" data-tab="{t_key}"{_h}>{chan_html}</div>'
            continue

        # ── Filas generadas por helper centralizado ───────────────────────────
        panels += build_kpi_tab_panel(df_t, t_key, _CV_CFG, _CV_HDR)
    
    return f'''<div class="kpi-card" id="kpicard-cv" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);display:flex;flex-direction:column;">

<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Conversion Rate</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div id="w21-kv-cv" style="font-size:40px;font-weight:700;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(cv_w18)}</div>

</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:14px;margin-bottom:2px;">{tabs}</div>
<div id="kpi-cv-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>
<div id="kpi-cv-hfilt" style="display:none;"></div>
<div style="display:flex;justify-content:flex-start;margin-top:8px;margin-bottom:4px;">{searchbox_pill_html('sb-kpi-cv', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-kpi-cv')}</div>
<div id="kpi-cv-panels" class="tab-panels">{panels}</div>
<div style='margin-top:12px;border-top:1px solid var(--rule);padding-top:10px;'><span id='hist-hcr-panel-cv-label' style='font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#5C469C;display:block;margin-bottom:6px;'>Global</span>{_rhs('cr','convrate',banda,cv_w18,'hcr-panel-cv')}</div>
</div>'''

def render_alerts_block():
    """Banner alertas hero CR · 3 columnas: Hoteles, Destinos, Channel.
    Reglas: excluir BKGS=0 (cohorte Sin Conv aparte) y excluir Eficacia/ConvRate=0
    (casos sin actividad real). Esos casos ya están cubiertos en sección Sin Conversión."""
    g_p80 = p80_hotel.copy()
    
    # Hoteles · peor Eficacia (P80, alto volumen, BKGS>0, Eficacia>0)
    h_ef_pool = g_p80[(g_p80['Bookings']>0) & (g_p80['Eficacia']>0) & (g_p80['CR_Unicos']>g_p80['CR_Unicos'].quantile(0.50))]
    h_ef = h_ef_pool.sort_values('Eficacia').iloc[0]
    # Hoteles · peor ConvRate (P80, alto volumen, BKGS>0)
    h_cv_pool = g_p80[(g_p80['Bookings']>0) & (g_p80['CR_Unicos']>g_p80['CR_Unicos'].quantile(0.50))]
    h_cv = h_cv_pool.sort_values('ConvRate').iloc[0]
    
    # Destinos · BKGS>0, Eficacia>0
    d_ef_pool = TAB_EF['destino'][(TAB_EF['destino']['Bookings']>0) & (TAB_EF['destino']['Eficacia']>0)]
    d_ef = d_ef_pool.iloc[0] if len(d_ef_pool)>0 else TAB_EF['destino'].iloc[0]
    d_cv_pool = TAB_CV['destino'][TAB_CV['destino']['Bookings']>0]
    d_cv = d_cv_pool.iloc[0] if len(d_cv_pool)>0 else TAB_CV['destino'].iloc[0]
    
    # Channels · BKGS>0, Eficacia>0
    ch_ef_pool = TAB_EF['channel'][(TAB_EF['channel']['Bookings']>0) & (TAB_EF['channel']['Eficacia']>0)]
    ch_ef = ch_ef_pool.iloc[0] if len(ch_ef_pool)>0 else TAB_EF['channel'].iloc[0]
    ch_cv_pool = TAB_CV['channel'][TAB_CV['channel']['Bookings']>0]
    ch_cv = ch_cv_pool.iloc[0] if len(ch_cv_pool)>0 else TAB_CV['channel'].iloc[0]
    
    def alert_card(title, icon, color_b, items):
        cells = ''
        for it in items:
            cells += (f'<div style="background:#FAF7F2;padding:8px 10px;border-radius:3px;border:1px solid var(--rule-soft);">'
                      f'<div style="font-size:8px;font-weight:700;color:{it["pill_color"]};background:{it["pill_bg"]};padding:2px 5px;border-radius:2px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;">{it["pill"]}</div>'
                      f'<div style="font-size:11px;font-weight:700;color:var(--ink);line-height:1.2;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["name"]}</div>'
                      f'<div style="font-size:7px;color:var(--ink-muted);margin-top:1px;">{it["sub"]}</div>'
                      f'<div style="font-size:18px;font-weight:600;color:{it["pill_color"]};margin-top:6px;letter-spacing:-.02em;line-height:1;">{it["value"]}</div>'
                      f'<div style="font-size:8px;color:var(--ink-muted);margin-top:3px;line-height:1.4;">{it["foot"]}</div>'
                      f'</div>')
        return (f'<div style="background:#F2EDE0;border-radius:4px;padding:10px;border-top:3px solid {color_b};">'
                f'<div style="font-size:10px;font-weight:700;color:{color_b};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px;">'
                f'<span>{icon}</span><span>{title}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{cells}</div></div>')
    
    h_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(clean_hotel_name(h_ef['Hotel']),38),'sub':f'{h_ef["CorpName"]} · {h_ef["Destino"]}',
         'value':fmt_pct2(h_ef['Eficacia']),'foot':f'{fmt_int_es(h_ef["CR_Unicos"])} CR · {int(h_ef["Bookings"])} BKGS'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EEE9F7',
         'name':truncate(clean_hotel_name(h_cv['Hotel']),38),'sub':f'{h_cv["CorpName"]} · {h_cv["Destino"]}',
         'value':fmt_pct2(h_cv['ConvRate']),'foot':f'{fmt_int_es(h_cv["CR_Unicos"])} CR · {int(h_cv["Bookings"])} BKGS'},
    ]
    d_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':clean_destino_name(d_ef['Destino'],38),'sub':f'{fmt_int_es(d_ef["CR_Unicos"])} CR · {int(d_ef["Bookings"])} BKGS',
         'value':fmt_pct2(d_ef['Eficacia']),'foot':f'CR {fmt_pct2(d_ef["ConvRate"])}'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EEE9F7',
         'name':clean_destino_name(d_cv['Destino'],38),'sub':f'{fmt_int_es(d_cv["CR_Unicos"])} CR · {int(d_cv["Bookings"])} BKGS',
         'value':fmt_pct2(d_cv['ConvRate']),'foot':f'Ef {fmt_pct2(d_cv["Eficacia"])}'},
    ]
    ch_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(ch_ef['ExternalProviderName'],38),'sub':f'{fmt_int_es(ch_ef["CR_Unicos"])} CR · {int(ch_ef["Bookings"])} BKGS',
         'value':fmt_pct2(ch_ef['Eficacia']),'foot':f'CR {fmt_pct2(ch_ef["ConvRate"])}'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EEE9F7',
         'name':truncate(ch_cv['ExternalProviderName'],38),'sub':f'{fmt_int_es(ch_cv["CR_Unicos"])} CR · {int(ch_cv["Bookings"])} BKGS',
         'value':fmt_pct2(ch_cv['ConvRate']),'foot':f'Ef {fmt_pct2(ch_cv["Eficacia"])}'},
    ]
    
    cards = (alert_card('Hoteles','🏨','#5C469C',h_items) +
             alert_card('Destinos','📍','#5C469C',d_items) +
             alert_card('Channels','🔌','#5C469C',ch_items))
    return f'''<div class="alerts-block" style="margin:0 0 24px;">
<div style="font-size:11px;color:#5C469C;font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
<span>📍</span><span>Alertas · Casos Críticos de la Semana</span>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr));gap:14px;">{cards}</div>
</div>'''

# ── Card 3: Bookability ────────────────────────────────────────────────────────
def render_kpi_card_bookability():
    import pickle as _pk, os as _os, pandas as _pd
    BK_COLOR = '#333132'
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path):
        return ''
    with open(bk_path, 'rb') as _f:
        DB = _pk.load(_f)

    bk_val    = DB.get('bk_global', 0)
    bk_prev   = DB.get('bk_prev',   0)
    bk_wow    = DB.get('bk_wow',    0)
    books     = DB.get('books_global', 0)
    banda_key = DB.get('banda_global', 'exitosa')

    from render_helpers import (wow_box, fmt_pct2, fmt_int_es, BANDA_COLORS,
                                banda_pill, target_caption, gauge_5levels,
                                wow_pill_html, searchbox_pill_html, _kpi_ver_mas_btn)
    def _fmt_compact(n):
        n = int(n)
        if n >= 1_000_000: return f'{n/1_000_000:.1f}M'.replace('.',',')
        if n >= 1_000:     return f'{n/1_000:.1f}K'.replace('.',',')
        return str(n)
    from engine import banda_eficacia as _bef
    from historico_module import render_historico as _rh

    _lbl = {'exitosa':'Exitosa','aceptable':'Aceptable','revisar':'Revisar',
            'critica':'Crítica','sc':'Súper Crítica','sinconv':'Sin Conversión'}
    banda = _lbl.get(banda_key, 'Exitosa')

    bk_fmt  = fmt_pct2(bk_val)
    bp_fmt  = fmt_pct2(bk_prev)
    wow_c   = '#2F6C34' if bk_wow > 0 else '#C0392B'
    wow_arr = '↑' if bk_wow > 0 else ('↓' if bk_wow < 0 else '=')
    if bk_wow > 0:   wow_s = f'{wow_arr} +{bk_wow*100:.2f}'.replace('.', ',')
    elif bk_wow < 0: wow_s = f'{wow_arr} {bk_wow*100:.2f}'.replace('.', ',')
    else:            wow_s = '= 0,00'

    pill          = banda_pill(banda, target='≥ 97%')
    pill_tgt      = pill
    gauge         = gauge_5levels(banda, 'eficacia')
    _bk_wow_pp  = bk_wow * 100
    if abs(_bk_wow_pp) < 0.005:
        wow_pill_bk = ('<span style="display:inline-flex;align-items:center;gap:2px;'
                       'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
                       'background:#F2EEE6;color:#8A8377;">— 0,00</span>')
    elif _bk_wow_pp > 0:
        wow_pill_bk = (f'<span style="display:inline-flex;align-items:center;gap:2px;'
                       f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
                       f'background:#EAF3DE;color:#2F6C34;">↑ +{_bk_wow_pp:.2f}</span>'.replace('.',','))
    else:
        wow_pill_bk = (f'<span style="display:inline-flex;align-items:center;gap:2px;'
                       f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
                       f'background:#FCE8E6;color:#C0392B;">↓ {_bk_wow_pp:.2f}</span>'.replace('.',','))

    # WoW de Books (Trx total) — comparar books_global vs books_global_prev
    books_prev = DB.get('books_global_prev', books)
    if books_prev and books_prev > 0:
        books_wow_pct = (books - books_prev) / books_prev * 100
    else:
        books_wow_pct = 0
    # Badge TRX: MISMO estilo que el badge de Tráfico de las cards EF/CV
    # (em, font-size:8px, padding:1px 4px, border-radius:3px, flecha ▲/▼, solo valor%)
    if abs(books_wow_pct) < 0.05:
        wow_books_pill = ('<em style="font-style:normal;font-size:8px;font-weight:700;'
                          'padding:1px 4px;border-radius:3px;background:#F2EEE6;color:#8A8377;'
                          'white-space:nowrap;">— 0,0%</em>')
    else:
        _arrow = '▲' if books_wow_pct > 0 else '▼'
        _bg = '#EAF3DE' if books_wow_pct > 0 else '#FCE8E6'
        _fg = '#2F6C34' if books_wow_pct > 0 else '#C0392B'
        wow_books_pill = (f'<em style="font-style:normal;font-size:8px;font-weight:700;'
                          f'padding:1px 4px;border-radius:3px;background:{_bg};color:{_fg};'
                          f'white-space:nowrap;">{_arrow}{abs(books_wow_pct):.1f}%</em>'.replace('.', ','))
    wow_block     = wow_box(bp_fmt, bk_fmt, wow_s, wow_c, BK_COLOR,
                            week_num=f'W{WEEK_NUM_INT}', week_prev=f'W{WEEK_PREV_INT}')
    # trx_line se ensambla más abajo con wow_books_pill ya calculado

    # ── Tabs labels ───────────────────────────────────────────────────────────
    tabs_lbl = ''.join(_kpi_view_pill_bk(k, l, i==0)
                        for i,(k,l) in enumerate([('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel')]))

    # ── Helpers de fila ───────────────────────────────────────────────────────
    def _hdr(col):
        # Headers clickeables con data-sort-key
        return (f'<div class="bk-sort-hdr" '
                f'style="display:grid;grid-template-columns:minmax(0,1fr) 52px 44px 72px 48px;'
                f'align-items:center;gap:6px;padding:4px 0;border-bottom:2px solid {BK_COLOR};">'
                f'<span data-sort-key="lbl" '
                f'style="font-size:9px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.08em;color:var(--ink-muted);cursor:pointer;user-select:none;">{col} <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="trx" '
                f'style="font-size:9px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">Trx <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="trx-wow" '
                f'style="font-size:9px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">WoW <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk" '
                f'style="font-size:9px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.08em;color:{BK_COLOR};text-align:right;cursor:pointer;user-select:none;">BK% <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'<span data-sort-key="bk-wow" '
                f'style="font-size:9px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.08em;color:var(--ink-muted);text-align:right;cursor:pointer;user-select:none;">WoW <em class="bk-arrow" style="font-style:normal;opacity:.4;">↕</em></span>'
                f'</div>')

    def _row(r, dim_col, sub_col=None, extra_cls='', extra_style='', idx=None):
        bkr  = float(r['Bookability'])
        trx  = fmt_int_es(int(r.get('Books', 0)))
        wpp  = r.get('BK_WoW_pp', None)
        wf   = f'{wpp*100:+.2f}'.replace('.',',') if (wpp is not None and not _pd.isna(wpp)) else '—'
        wc   = '#1A6B4A' if (wpp or 0) >= 0 else '#C0392B'
        lbl  = str(r.get(dim_col, '—'))
        # Limpieza de sufijos comunes en Destino
        if dim_col == 'Destino':
            lbl = lbl.replace(' Area', '').replace(' area', '')
        sub  = str(r.get(sub_col, '')) if sub_col and r.get(sub_col) else ''
        sub_html = (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;'
                    f'overflow:hidden;text-overflow:ellipsis;display:block;">{sub}</span>'
                    if sub else '')
        # WoW de Trx (Books_WoW_pct)
        bwp = r.get('Books_WoW_pct', None)
        if bwp is not None and not _pd.isna(bwp):
            twf = f'{bwp:+.1f}%'.replace('.', ',')
            twc = '#1A6B4A' if bwp >= 0 else '#C0392B'
        else:
            twf, twc = '—', 'var(--ink-muted)'
        # data attrs para sort
        _trx_int = int(r.get('Books', 0))
        _trx_wow_v = bwp if (bwp is not None and not _pd.isna(bwp)) else 0
        _bk_wow_v  = wpp if (wpp is not None and not _pd.isna(wpp)) else 0
        _ridx = f' data-row-idx="{idx-1}"' if idx is not None else ''
        return (f'<div class="bk-row{extra_cls}"{_ridx} '
                f'data-lbl="{lbl}" data-hist-label="{lbl}" data-hist-w21="{round(bkr*100,2)}" data-hist-w20="{round((bkr - (wpp/100 if (wpp is not None and not _pd.isna(wpp)) else 0))*100,2)}" data-trx="{_trx_int}" '
                f'data-trx-wow="{_trx_wow_v:.4f}" '
                f'data-bk="{bkr:.6f}" data-bk-wow="{_bk_wow_v:.6f}" '
                f'style="{"" if "display:none" in extra_style else "display:grid;"}grid-template-columns:minmax(0,1fr) 52px 44px 72px 48px;'
                f'align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;{extra_style}">'
                f'<div style="min-width:0;overflow:hidden;">'
                f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                f'font-weight:600;font-size:11px;color:var(--ink);display:block;">{(str(idx)+". ") if idx is not None else ""}{lbl}</span>'
                f'{sub_html}</div>'
                f'<span style="text-align:right;font-size:11px;font-weight:700;color:var(--ink);">{trx}</span>'
                f'<span style="text-align:right;font-size:9px;font-weight:700;color:{twc};">{twf}</span>'
                f'<span style="text-align:right;font-size:11px;font-weight:700;color:{BK_COLOR};">{fmt_pct2(bkr)}</span>'
                f'<span style="text-align:right;font-size:9px;font-weight:700;color:{wc};">{wf}</span>'
                f'</div>')

    def _ver_mas_btn():
        return _kpi_ver_mas_btn(target_class='rows-more')

    def _panel(t_key, df, dim_col, col_lbl):
        if df is None or len(df) == 0:
            return f'<div class="tab-panel" data-tab="{t_key}"><p style="font-size:11px;color:var(--ink-muted);">Sin datos</p></div>'
        _sub = 'CorpName' if dim_col == 'Hotel' else None
        # 5 visibles
        rows5 = ''.join(_row(r, dim_col, sub_col=_sub, idx=i+1) for i, (_, r) in enumerate(df.head(5).iterrows()))
        # 6-10: clase rows-more (mismo sistema que EF/CV)
        rows_m = ''.join(
            _row(r, dim_col, sub_col=_sub, extra_cls=' rows-more', extra_style='display:none;', idx=i+6)
            for i, (_, r) in enumerate(df.iloc[5:10].iterrows()))
        # 11+: clase sb-hidden (buscables)
        rows_sb = ''.join(
            _row(r, dim_col, sub_col=_sub, extra_cls=' sb-hidden', extra_style='display:none;')
            for _, r in df.iloc[10:].iterrows())
        show_btn = _ver_mas_btn() if len(df) > 5 else ''
        # Mismo wrapper .kpi-tab-rows que EF/CV para compatibilidad con SB y Ver más
        return (f'<div class="tab-panel" data-tab="{t_key}">'
                f'<div class="kpi-tab-rows">{_hdr(col_lbl)}{rows5}{rows_m}{rows_sb}{show_btn}</div></div>')

    # ── Paneles ───────────────────────────────────────────────────────────────
    panels = ''

    # Channel — split Producto Propio / Third Party
    top_prov = DB.get('TOP_PROVIDER', DB.get('g_provider', None))
    if top_prov is not None:
        # Catálogo canónico unificado (mismo que EF/CV) — rellenar faltantes con "Sin Actividad"
        _CAT_PP = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
        _CAT_TP = ['Expedia','HotelBeds','Hotel Unico','Travelgate','RateFox']
        # Clasificación dinámica desde TipoProvider del pickle (providers nuevos como RateFox incluidos)
        _PROPIO  = set(top_prov[top_prov['TipoProvider'] == 'Producto Propio']['Provider'].tolist())
        _TERCERO = set(top_prov[top_prov['TipoProvider'] == 'Third Party']['Provider'].tolist())
        _present = set(str(p) for p in top_prov['Provider'].tolist())
        def _inactive_row_bk(name):
            return ('<div style="display:grid;grid-template-columns:minmax(0,1fr) 56px 72px 48px;'
                    'align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid var(--rule-soft);opacity:.45;">'
                    f'<span style="font-size:11px;font-weight:600;color:var(--ink-muted);">{name}</span>'
                    '<span style="text-align:right;font-size:11px;color:var(--ink-muted);">—</span>'
                    '<span style="text-align:right;font-size:9px;font-weight:700;text-transform:uppercase;color:var(--ink-muted);">Sin Actividad</span>'
                    '<span style="text-align:right;font-size:11px;color:var(--ink-muted);">—</span>'
                    '</div>')
        pp_rows  = ''.join(_row(r,'Provider') for _,r in top_prov.iterrows() if r['Provider'] in _PROPIO)
        tp_rows  = ''.join(_row(r,'Provider') for _,r in top_prov.iterrows() if r['Provider'] in _TERCERO)
        # Rellenar faltantes del catálogo con Sin Actividad
        pp_rows += ''.join(_inactive_row_bk(n) for n in _CAT_PP if n not in _present)
        tp_rows += ''.join(_inactive_row_bk(n) for n in _CAT_TP if n not in _present)
        _no_data = '<p style="font-size:11px;color:var(--ink-muted)">Sin datos</p>'
        _pp_body = pp_rows if pp_rows else _no_data
        _tp_body = tp_rows if tp_rows else _no_data
        chan_html = (
            f'<div class="chan-wrap" style="display:flex;flex-direction:column;gap:14px;width:100%;">'
            f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;'
            f'letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>'
            f'{_hdr("Channel")}{_pp_body}</div>'
            f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;'
            f'letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>'
            f'{_hdr("Channel")}{_tp_body}</div>'
            f'</div>'
        )
        panels += f'<div class="tab-panel" data-tab="channel">{chan_html}</div>'
    else:
        panels += '<div class="tab-panel" data-tab="channel"><p>Sin datos</p></div>'

    panels += _panel('destino', DB.get('TOP_DEST',  DB.get('g_dest',  None)), 'Destino',  'Destino')
    panels += _panel('corp',    DB.get('TOP_CORP',  DB.get('g_corp',  None)), 'CorpName', 'Corporativo')
    panels += _panel('hotel',   DB.get('TOP_HOTEL', DB.get('g_hotel', None)), 'Hotel',    'Hotel')

    # ── Histórico ─────────────────────────────────────────────────────────────
    hist_bk = _rhs('bk', 'bookability', banda, bk_val, 'h-bk-panel')

    # ── HTML final ────────────────────────────────────────────────────────────
    _sb = searchbox_pill_html('sb-kpi-bk', accent_color='#5C469C',
                              placeholder='Buscar…', count_id='cnt-kpi-bk')
    return (
        f'<div class="kpi-card" id="kpicard-bk" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);display:flex;flex-direction:column;">'
        f'<div>'
        f'<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Bookability</div>'
        f'<div style="margin-top:4px;display:flex;align-items:flex-start;gap:10px;">'
        f'<div>'
        f'<div style="font-size:40px;font-weight:700;letter-spacing:-.02em;color:{BK_COLOR};line-height:1;">{bk_fmt}</div>'
        f'<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);flex-wrap:wrap;">'
        f''
        f'</div>'
        f'</div>'
        f'<div style="padding-top:4px;flex-shrink:0;align-self:flex-start;">{pill_tgt}</div>'
        f'</div>'
        f'</div>'
        f'{gauge}'
        f'{wow_block}'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:14px;margin-bottom:2px;">{tabs_lbl}</div>'
        f'<div id="kpi-bk-cross-pills" style="display:none;flex-wrap:wrap;gap:6px;margin-top:6px;margin-bottom:2px;"></div>'
        f'<div style="display:flex;justify-content:flex-start;margin-top:8px;margin-bottom:4px;">{_sb}</div>'
        f'<div style="margin-top:12px;border-top:1px solid var(--rule);padding-top:10px;"><span id="hist-h-bk-panel-label" style="font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#333132;display:block;margin-bottom:6px;">Global</span>{hist_bk}</div>'
        f'<div id="kpi-bk-panels" class="tab-panels">{panels}</div>'
        f'</div>'
    )


# Build hero
h1, subhead, ef18, cv18, ef17, cv17, ef_wow, cv_wow = render_hero()
HERO = f'''<section class="hero" id="kpis-hero-section">
<div class="kpis-hero" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:14px;margin:6px 0 12px;">
{render_kpi_card_eficacia(ef18, ef17, ef_wow, f'W{WEEK_NUM_INT}', f'W{WEEK_PREV_INT}')}
{render_kpi_card_convrate(cv18, cv17, cv_wow, f'W{WEEK_NUM_INT}', f'W{WEEK_PREV_INT}')}
{render_kpi_card_bookability()}
</div>
<p class="hero-subhead" style="font-size:13px;color:var(--ink-muted);margin:0 0 24px;line-height:1.5;">{subhead}</p>
</section>
'''

import json as _json
import math as _math_glob

def _build_card_rows_ef(tab_ef, t_key):
    """Convierte tab de eficacia en array de filas para JS — via build_card_rows."""
    df = tab_ef.get(t_key, pd.DataFrame())
    return build_card_rows(df, t_key, {
        'val_col':       'Eficacia',
        'val_scale':     lambda v: round(float(v)*100, 2),
        'banda_fn':      banda_eficacia,
        'banda_col':     'BandaEficacia',
        'traf_col':      'CR_Unicos',
        'traf_wow_col':  'CR_Unicos_WoW_pp',
        'traf_wow_scale': lambda v: round(float(v)/100, 0),
        'wow_col':       'Eficacia_WoW_pp',
        'hist_prev_col': 'Eficacia_W17',
    })

def _build_card_rows_cv(tab_cv, t_key):
    """Convierte tab de convrate en array de filas para JS — via build_card_rows."""
    df = tab_cv.get(t_key, pd.DataFrame())
    return build_card_rows(df, t_key, {
        'val_col':       'ConvRate',
        'val_scale':     lambda v: round(float(v)*100, 2),
        'banda_fn':      lambda v: banda_convrate(v, 0),
        'banda_col':     'BandaConvRate',
        'traf_col':      'CR_Unicos',
        'traf_wow_col':  'CR_Unicos_WoW_pp',
        'traf_wow_scale': lambda v: round(float(v)/100, 0),
        'wow_col':       'ConvRate_WoW_pp',
        'hist_prev_col': 'ConvRate_W17',
    })

def _build_card_rows_chan(tab, metric_col, wow_col):
    """Convierte tab channel en array de filas para JS."""
    PRODUCTO_PROPIO = {'DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees'}
    df = tab.get('channel', pd.DataFrame())
    pp_rows, tp_rows = [], []
    for _, r in df.iterrows():
        nombre = str(r.get('ExternalProviderName','?'))
        val = r.get(metric_col, None)
        val_pct = round(float(val)*100, 2) if val and not _math_glob.isnan(float(val)) else None
        bnd = banda_eficacia(val) if metric_col=='Eficacia' and val is not None else (banda_convrate(val, int(r.get('Bookings',0))) if val is not None else '')
        bc = BANDA_COLORS.get(bnd, {})
        cr_u = r.get('CR_Unicos', None)
        wow = r.get(wow_col, None)
        entry = [nombre, bc.get('bg','#F2EEE6'), bc.get('fg','#5F5E5A'), bnd,
                 int(cr_u) if cr_u and not _math_glob.isnan(float(cr_u)) else None,
                 val_pct,
                 round(float(wow), 2) if wow and not _math_glob.isnan(float(wow)) else None]
        if nombre in PRODUCTO_PROPIO:
            pp_rows.append(entry)
        else:
            tp_rows.append(entry)
    return {'pp': pp_rows, 'tp': tp_rows}

def _build_cr_card_tabs_json():
    """Genera JSON con los datos de las cards KPI por canasta."""
    TAB_EF_BY = D.get('TAB_EF_BY_CANASTA', {'global': TAB_EF})
    TAB_CV_BY = D.get('TAB_CV_BY_CANASTA', {'global': TAB_CV})
    _CRIT = {'Crítica', 'Súper Crítica'}
    tabs = {}
    for canasta in ['global', 'b2c', 'op', 'cug']:
        tab_ef = TAB_EF_BY.get(canasta, TAB_EF)
        tab_cv = TAB_CV_BY.get(canasta, TAB_CV)
        ef_tabs = {t: _build_card_rows_ef(tab_ef, t) for t in ['destino','corp','hotel']}
        cv_tabs = {t: _build_card_rows_cv(tab_cv, t) for t in ['destino','corp','hotel']}
        if canasta == 'global':
            # W24: el hotel GLOBAL se sirve del motor lazy (CR_HOTEL_POOL, ~3.582). En
            # CR_CARD_TABS dejamos solo la banda crit (el default que _kpiSortAttach renderiza
            # en carga y al cambiar de canasta); el lazy cubre cross-filter + searchbox (pool).
            # Las per-canasta (b2c/op/cug, ~100 c/u) siguen completas por el camino DOM.
            ef_tabs['hotel'] = [r for r in ef_tabs['hotel'] if (r[4] if len(r) > 4 else '') in _CRIT]
            cv_tabs['hotel'] = [r for r in cv_tabs['hotel'] if (r[4] if len(r) > 4 else '') in _CRIT]
        tabs[canasta] = {
            'ef': ef_tabs,
            'cv': cv_tabs,
            'ef_chan': _build_card_rows_chan(tab_ef, 'Eficacia', 'Eficacia_WoW_pp'),
            'cv_chan': _build_card_rows_chan(tab_cv, 'ConvRate', 'ConvRate_WoW_pp'),
        }
    return f'\n<script>\nvar CR_CARD_TABS={_json.dumps(tabs, ensure_ascii=False, default=lambda x: None)};\n</script>\n'

def _build_bk_card_rows(df, t_key):
    """Convierte df de BK en array de filas para JS — misma estructura que EF/CV.
    Array: [lab, sub, bbg, bfg, banda, traf(Books), traf_wow, val(Bookability), val_wow, hist_w21, hist_w20]
    """
    if df is None or len(df) == 0:
        return []
    return build_card_rows(df, t_key, {
        'val_col':        'Bookability',
        'val_scale':      lambda v: round(float(v)*100, 2),
        'banda_col':      'BandaBK',
        'traf_col':       'Books',
        'traf_wow_col':   'Books_WoW_abs',
        'traf_wow_scale': lambda v: round(float(v), 0),
        'wow_col':        'BK_WoW_pp',
        'hist_prev_col':  'Bookability_prev',
    })

def _build_bk_card_tabs_json():
    """Genera JSON con los datos de la card BK por canasta — estructura igual a CR_CARD_TABS."""
    import pickle as _pk, os as _os
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path):
        return '\n<script>\nvar BK_CARD_TABS={};\n</script>\n'
    with open(bk_path, 'rb') as _f:
        _BKD = _pk.load(_f)
    _BK_BY = _BKD.get('BK_BY_CANASTA', None)
    tabs = {}
    for canasta in ['global', 'b2c', 'op', 'cug']:
        src = (_BK_BY.get(canasta) if _BK_BY else None) or _BKD
        tabs[canasta] = {
            'bk': {
                'destino': _build_bk_card_rows(src.get('TOP_DEST',  src.get('g_dest',  None)), 'destino'),
                'corp':    _build_bk_card_rows(src.get('TOP_CORP',  src.get('g_corp',  None)), 'corp'),
                'hotel':   _build_bk_card_rows(src.get('TOP_HOTEL', src.get('g_hotel', None)), 'hotel'),
            },
        }
    return f'\n<script>\nvar BK_CARD_TABS={_json.dumps(tabs, ensure_ascii=False, default=lambda x: None)};\n</script>\n'


def _build_cr_hotel_pool_json():
    """Pool COMPLETO de hoteles CR (~3.582) para el cross-filter →hotel y searchbox en
    las KPI cards CR (ef/cv). Unifica CR sobre el motor lazy de RND (W24): el pool vive
    compacto en CR_HOTEL_POOL (NO se vuelca al DOM) y el JS arma el subconjunto cruzado
    on-demand. Reemplaza las ~2.6K filas estáticas + el hotel de CR_CARD_TABS (~4MB).
    Formato fila (11 campos):
      [label, corp, dest, cru, cru_wow, ef_pct, ef_bidx, ef_wow, cv_pct, cv_bidx, cv_wow]
    Banda como índice 0-5 → _CR_BAND_NAMES → _AR_BANDA_C (colores) en JS."""
    _BIDX = {'Exitosa': 0, 'Aceptable': 1, 'Revisar': 2, 'Crítica': 3,
             'Súper Crítica': 4, 'Sin Conversión': 5}

    def _num(v, ndig=2):
        try:
            f = float(v)
            if _math_glob.isnan(f) or _math_glob.isinf(f):
                return None
            return round(f, ndig)
        except (TypeError, ValueError):
            return None

    pool = []
    for _, r in TAB_EF['hotel'].iterrows():
        lab = truncate(clean_hotel_name(str(r.get('Hotel', ''))), 38)
        corp = str(r.get('CorpName', '') or '')
        dest = str(r.get('Destino', '') or '')
        cru = int(r.get('CR_Unicos', 0) or 0)
        _cw = r.get('CR_Unicos_WoW_pp')
        cru_wow = _num(float(_cw) / 100, 0) if _cw is not None and not pd.isna(_cw) else None
        ef = r.get('Eficacia')
        ef_pct = _num(ef * 100) if ef is not None else None
        ef_band = _BIDX.get(r.get('BandaEficacia') or (banda_eficacia(ef) if ef is not None else 'Sin Conversión'), 5)
        ef_wow = _num(r.get('Eficacia_WoW_pp'))
        cv = r.get('ConvRate')
        bk = int(r.get('Bookings', 0) or 0)
        cv_pct = _num(cv * 100) if cv is not None else None
        cv_band = _BIDX.get(r.get('BandaConvRate') or (banda_convrate(cv, bk) if cv is not None else 'Sin Conversión'), 5)
        cv_wow = _num(r.get('ConvRate_WoW_pp'))
        pool.append([lab, corp, dest, cru, cru_wow,
                     ef_pct, ef_band, ef_wow, cv_pct, cv_band, cv_wow])
    return ('\n<script>\nvar CR_HOTEL_POOL='
            + _json.dumps(pool, ensure_ascii=False, default=lambda x: None)
            + ';\nvar _CR_BAND_NAMES=["Exitosa","Aceptable","Revisar","Cr\\u00edtica",'
              '"S\\u00faper Cr\\u00edtica","Sin Conversi\\u00f3n"];\n</script>\n')


def _build_cr_hist_json():
    """Emite CR_CORP_HIST y CR_DEST_HIST con datos reales W18-W(N-1) por corp/dest."""
    hist = D.get('CR_HIST', {})
    semanas_prev = [f'W{n:02d}' for n in range(18, WEEK_NUM_INT)]  # W18…W(N-1)

    def _entity_dict(bucket):
        out = {}
        for name, wdict in hist.get(bucket, {}).items():
            ef_vals = [wdict.get(w, {}).get('ef') for w in semanas_prev]
            cv_vals = [wdict.get(w, {}).get('cv') for w in semanas_prev]
            # Solo incluir si hay al menos 1 dato real
            if any(v is not None for v in ef_vals):
                out[name] = {
                    'ef': [round(v * 100, 2) if v is not None else None for v in ef_vals],
                    'cv': [round(v * 100, 4) if v is not None else None for v in cv_vals],
                }
        return out

    import json
    corp_js     = json.dumps(_entity_dict('corp'),     ensure_ascii=False, separators=(',', ':'))
    dest_js     = json.dumps(_entity_dict('dest'),     ensure_ascii=False, separators=(',', ':'))
    hotel_js    = json.dumps(_entity_dict('hotel'),    ensure_ascii=False, separators=(',', ':'))
    provider_js = json.dumps(_entity_dict('provider'), ensure_ascii=False, separators=(',', ':'))
    sem_js      = json.dumps(semanas_prev, ensure_ascii=False)
    return (
        f'\n<script>\nvar CR_CORP_HIST={corp_js};\n'
        f'var CR_DEST_HIST={dest_js};\n'
        f'var CR_HOTEL_HIST={hotel_js};\n'
        f'var CR_PROVIDER_HIST={provider_js};\n'
        f'var _HIST_SEMANAS_PREV={sem_js};\n</script>\n'
    )


def _build_bk_hist_json():
    """Emite BK_CORP_HIST con bookability histórica W18-W(N-1) por corp.
    Requiere corp_hist_bk en el pickle BK."""
    import json as _json, pickle as _pk, os as _os
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path):
        return ''
    with open(bk_path, 'rb') as _f:
        _BKD = _pk.load(_f)
    corp_hist = _BKD.get('corp_hist_bk', {})
    if not corp_hist:
        return ''  # Sin datos históricos por corp
    corp_js = _json.dumps(corp_hist, ensure_ascii=False, separators=(',', ':'))
    return f'\n<script>\nvar BK_CORP_HIST={corp_js};\n</script>\n'


def _build_bk_hotel_hist_json():
    """Emite BK_HOTEL_HIST con bookability histórica W18-W(N-1) por hotel.
    Requiere hotel_hist_bk en el pickle BK. Usado por AR3 al clickear un hotel."""
    import json as _json, pickle as _pk, os as _os
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path):
        return ''
    with open(bk_path, 'rb') as _f:
        _BKD = _pk.load(_f)
    hotel_hist = _BKD.get('hotel_hist_bk', {})
    if not hotel_hist:
        return ''
    hotel_js = _json.dumps(hotel_hist, ensure_ascii=False, separators=(',', ':'))
    return f'\n<script>\nvar BK_HOTEL_HIST={hotel_js};\n</script>\n'


def _build_bk_dest_hist_json():
    """Emite BK_DEST_HIST con bookability histórica W18-W(N-1) por destino."""
    import json as _json, pickle as _pk, os as _os
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path): return ''
    with open(bk_path,'rb') as _f: _BKD = _pk.load(_f)
    dest_hist = _BKD.get('dest_hist_bk', {})
    if not dest_hist: return ''
    js = _json.dumps(dest_hist, ensure_ascii=False, separators=(',',':'))
    return f'\n<script>\nvar BK_DEST_HIST={js};\n</script>\n'


def _build_bk_provider_hist_json():
    """Emite BK_PROVIDER_HIST con bookability histórica W18-W(N-1) por provider/channel.
    Requiere provider_hist_bk en el pickle BK. Usado por el sparkline en channel view."""
    import json as _json, pickle as _pk, os as _os
    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')
    if not _os.path.exists(bk_path): return ''
    with open(bk_path, 'rb') as _f: _BKD = _pk.load(_f)
    prov_hist = _BKD.get('provider_hist_bk', {})
    if not prov_hist: return ''
    js = _json.dumps(prov_hist, ensure_ascii=False, separators=(',', ':'))
    return f'\n<script>\nvar BK_PROVIDER_HIST={js};\n</script>\n'


    """Pool COMPLETO de hoteles CR (~3.582) para el cross-filter →hotel y searchbox en
    las KPI cards CR (ef/cv). Unifica CR sobre el motor lazy de RND (W24): el pool vive
    compacto en CR_HOTEL_POOL (NO se vuelca al DOM) y el JS arma el subconjunto cruzado
    on-demand. Reemplaza las ~2.6K filas estáticas + el hotel de CR_CARD_TABS (~4MB).
    Formato fila (11 campos):
      [label, corp, dest, cru, cru_wow, ef_pct, ef_bidx, ef_wow, cv_pct, cv_bidx, cv_wow]
    Banda como índice 0-5 → _CR_BAND_NAMES → _AR_BANDA_C (colores) en JS."""
    _BIDX = {'Exitosa': 0, 'Aceptable': 1, 'Revisar': 2, 'Crítica': 3,
             'Súper Crítica': 4, 'Sin Conversión': 5}

    def _num(v, ndig=2):
        try:
            f = float(v)
            if _math_glob.isnan(f) or _math_glob.isinf(f):
                return None
            return round(f, ndig)
        except (TypeError, ValueError):
            return None

    pool = []
    for _, r in TAB_EF['hotel'].iterrows():
        lab = truncate(clean_hotel_name(str(r.get('Hotel', ''))), 38)
        corp = str(r.get('CorpName', '') or '')
        dest = str(r.get('Destino', '') or '')
        cru = int(r.get('CR_Unicos', 0) or 0)
        _cw = r.get('CR_Unicos_WoW_pp')
        cru_wow = _num(float(_cw) / 100, 0) if _cw is not None and not pd.isna(_cw) else None
        ef = r.get('Eficacia')
        ef_pct = _num(ef * 100) if ef is not None else None
        ef_band = _BIDX.get(r.get('BandaEficacia') or (banda_eficacia(ef) if ef is not None else 'Sin Conversión'), 5)
        ef_wow = _num(r.get('Eficacia_WoW_pp'))
        cv = r.get('ConvRate')
        bk = int(r.get('Bookings', 0) or 0)
        cv_pct = _num(cv * 100) if cv is not None else None
        cv_band = _BIDX.get(r.get('BandaConvRate') or (banda_convrate(cv, bk) if cv is not None else 'Sin Conversión'), 5)
        cv_wow = _num(r.get('ConvRate_WoW_pp'))
        pool.append([lab, corp, dest, cru, cru_wow,
                     ef_pct, ef_band, ef_wow, cv_pct, cv_band, cv_wow])
    return ('\n<script>\nvar CR_HOTEL_POOL='
            + _json.dumps(pool, ensure_ascii=False, default=lambda x: None)
            + ';\nvar _CR_BAND_NAMES=["Exitosa","Aceptable","Revisar","Cr\\u00edtica",'
              '"S\\u00faper Cr\\u00edtica","Sin Conversi\\u00f3n"];\n</script>\n')


PART1 = (
    '\n<!-- ═══════════════ SECCIÓN CR ═══════════════ -->\n'
    '<section id="section-cr" class="section-cr">\n'
    + render_masthead()
    + HERO
    + '''
<script>
// HIST_DATA: datos históricos CR W16-W23 (8 puntos) — sincronizado con historico_data.py
// El último valor (W23) se agrega dinámicamente; estos son W16-W22 base.
const HIST_DATA = {
    'cr': {
        'eficacia': {
            'global': [93.27, 93.58, 93.71, 93.30, 93.34, 93.15, 94.21],
            'op':     [93.72, 94.03, 94.25, 93.87, 93.96, 93.81, 94.68],
            'cug':    [92.38, 92.69, 92.65, 92.54, 92.28, 92.11, 92.74],
            'b2c':    [91.82, 92.12, 92.18, 91.49, 92.01, 91.88, 92.41],
        },
        'convrate': {
            'global': [1.29, 1.15, 1.02, 1.14, 1.63, 1.57, 1.00],
            'op':     [1.12, 1.00, 0.94, 1.06, 1.59, 1.52, 0.92],
            'cug':    [2.65, 2.38, 1.82, 2.07, 2.90, 2.74, 2.12],
            'b2c':    [0.33, 0.30, 0.27, 0.25, 0.39, 0.36, 0.28],
        },
    },
};
window.HIST_DATA = HIST_DATA;
</script>
'''
    + _build_cr_card_tabs_json()
    + _build_cr_hotel_pool_json()
    + _build_bk_card_tabs_json()
    + _build_cr_hist_json()
    + _build_bk_hist_json()
    + _build_bk_hotel_hist_json()
    + _build_bk_dest_hist_json()
    + _build_bk_provider_hist_json()
)

with open('part1_cr.html', 'w', encoding='utf-8') as f:
    f.write(PART1)
print(f"Part 1 CR escrito: {len(PART1):,} chars")
