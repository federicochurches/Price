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

from historico_module_rnd import render_historico_rnd

def _mini_badge(bnd):
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span style="flex-shrink:1;min-width:0;font-size:7px;font-weight:700;padding:1px 3px;border-radius:2px;background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.03em;overflow:hidden;text-overflow:clip;white-space:nowrap;">{bnd}</span>'


# Cargar datos
with open(os.getenv('PICKLE_RND', 'rnd_w20_data.pkl'),'rb') as f:
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

    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div style="display:table;width:100%;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div style="display:table-cell;vertical-align:middle;">
<div style="display:inline-block;vertical-align:top;">
<span class="report-tag" style="display:block;text-align:left;margin-bottom:6px;">RatesNoDispo</span>
<div style="font-size:26px;font-weight:800;letter-spacing:-.02em;color:var(--ink);line-height:1;">{WEEK_DISPLAY}</div>
<div style="font-size:12px;font-weight:400;color:var(--ink-muted);margin-top:3px;">{PERIODO_LABEL}</div>
</div>
</div>
<div style="display:table-cell;vertical-align:middle;text-align:right;white-space:nowrap;">
<img alt="PriceTravel" src="{LOGO}" style="height:50px;width:auto;vertical-align:middle;"/>
<span style="display:inline-block;width:1px;height:38px;background:var(--rule);margin:0 12px;vertical-align:middle;"></span>
<span style="display:inline-block;vertical-align:middle;text-align:left;line-height:1.15;">
<span style="display:block;font-size:20px;font-weight:400;letter-spacing:-.01em;color:var(--accent);">Supply Optimization</span>
</span>
</div>
</div>
<div class="masthead-sub">
<span>{FECHA_PUB}</span>
<span>Vol. {VOL_NUM}</span>
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
    
    subhead = (f'<strong style="color:#EA0074;font-weight:700;">{fmt_big(tr18)}</span> Tráfico · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_hot)}</span> hoteles · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(bk18)}</span> Bookings · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_usd(gb18)}</span> GB · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_p80)}</span> hoteles P80.')
    
    return h1, subhead, pct, rpm, pct17, rpm17, pct_wow, rpm_wow

def render_kpi_card_nodispo(pct_w18, pct_w17, pct_wow):
    banda = banda_nodispo(pct_w18)
    target = "&lt; 3%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'nodispo')
    
    wow_color = '#2F6C34' if pct_wow < 0 else '#C0392B'  # mejor si baja
    wow_arrow = '↓' if pct_wow < 0 else ('↑' if pct_wow > 0 else '=')
    wow_str = f'{wow_arrow} {abs(pct_wow):+.2f}pp'.replace('+', '').replace('.', ',')
    if pct_wow < 0: wow_str = f'{wow_arrow} -{abs(pct_wow):.2f}pp'.replace('.', ',')
    elif pct_wow > 0: wow_str = f'{wow_arrow} +{pct_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(pct_w17), fmt_pct2(pct_w18), wow_str, wow_color, ACCENT)
    # Prop V1: NoDispo baja = buena → invertir signo para que verde = mejora
    _wow_pill_nd = wow_pill_html(-pct_wow, unit='pp', prefix_pos='↓', prefix_neg='↑')
    
    # Tabs panels
    tabs = ''
    for t_key, t_label in [('pais','País'),('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-nd-{t_key}">{t_label}</label>'
    
    panels = ''
    for t_key, t_label, df_t in [
        ('pais','País', TAB_NoDispo['pais']),
        ('destino','Destino', TAB_NoDispo['destino']),
        ('corp','Corp', TAB_NoDispo['corp']),
        ('hotel','Hotel', TAB_NoDispo['hotel']),
        ('canasta','Canasta', TAB_NoDispo['canasta']),
    ]:
        # Layout: 1 columna de 5 visible + botón "Ver 5 más" (excepto canasta)
        rows_html = top5 = next5 = rest = ''
        for i, r in df_t.iterrows():
            nd_val = r.get('%NoDispo', r.get('pct_nodispo', r.get('nodispo', 0)))
            _corp_sub = ''
            if t_key=='canasta':
                raw_lab = r['Canasta']; lab = raw_lab; val = nd_val
            elif t_key=='hotel':
                raw_lab = str(r['Hotel']); lab = truncate(clean_hotel_name(raw_lab), 38); val = nd_val
                _corp_sub = truncate(str(r.get('CorpName', '')), 20) if 'CorpName' in r.index else ''
            elif t_key=='pais':
                raw_lab = str(r['PaisDestino']); lab = clean_pais_name(raw_lab, max_len=30); val = nd_val
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                raw_lab = str(r[col]); lab = truncate(r[col], 36) if t_key=='corp' else clean_destino_name(r[col], 36); val = r['%NoDispo']
            show_wow = t_key in ('pais', 'destino', 'corp', 'hotel')
            wow_pill = ''
            if show_wow:
                wow_pp = r.get('NoDispo_WoW_pp', None)
                if wow_pp is not None and not (wow_pp != wow_pp) and abs(wow_pp) >= 0.05:
                    mejora = wow_pp < 0
                    wow_color = '#2F6C34' if mejora else '#C0392B'
                    wow_bg    = '#EAF3DE' if mejora else '#FCE8E6'
                    arrow = '↓' if wow_pp < 0 else '↑'
                    wow_txt = f'{arrow}{abs(wow_pp):.2f}'.replace('.', ',')
                    css_cls = "wow-pill dn" if mejora else "wow-pill up"
                    wow_pill = f'<em class="{css_cls}">{wow_txt}</em>'
                else:
                    wow_pill = '<em class="wow-pill nd">—</em>'
            grid = 'minmax(0,1fr) 76px 54px 36px' if show_wow else 'minmax(0,1fr) 76px 54px'
            import math as _mnd
            _nd_w21 = round(float(val)*100, 4) if val and not _mnd.isnan(float(val)) else 0
            _nd_w20_raw = r.get('%NoDispo_W18', r.get('NoDispo_W17', r.get('%NoDispo_W17', None)))
            try: _nd_w20 = round(float(_nd_w20_raw)*100,4) if _nd_w20_raw is not None and not _mnd.isnan(float(_nd_w20_raw)) else _nd_w21
            except: _nd_w20 = _nd_w21
            _bnd_nd = r.get('BandaNoDispo','') if 'BandaNoDispo' in r.index else ''
            if not _bnd_nd and val is not None:
                from engine import banda_nodispo as _bn; _bnd_nd = _bn(val)
            _badge_nd = _mini_badge(_bnd_nd)
            if i < 5: _cls = ''
            elif i < 10: _cls = 'rows-more'
            else: _cls = 'sb-hidden'
            _row = (f'<div class="{_cls}" data-row-idx="{i}"'
                    f' data-hist-w21="{_nd_w21}" data-hist-w20="{_nd_w20}" data-hist-label="{raw_lab}"'
                    f' style="display:grid;grid-template-columns:{grid};align-items:center;gap:10px;'
                    f'width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                    f'<div style="min-width:0;overflow:hidden;">'
                    f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
                    + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{_corp_sub}</span>' if _corp_sub else '')
                    + f'</div>'
                    f'<div style="display:flex;align-items:center;min-width:0;overflow:hidden;">{_badge_nd}</div>'
                    f'<span style="text-align:right;font-size:11px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(val)}</span>'
                    + (f'{wow_pill}</div>' if show_wow else '</div>'))
            if i < 5: top5 += _row
            elif i < 10: next5 += _row
            else: rest += _row
        if t_key not in ('canasta',):
            has_more = len(df_t) > 5
            ver_mas_btn = ''
            if has_more:
                ver_mas_btn = (f'<button class="rows-toggle" data-panel="{t_key}" '
                               f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                               f'font-size:10px;font-weight:600;color:var(--accent);letter-spacing:.04em;'
                               f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                               f'<span class="toggle-label">Ver 5 más</span> '
                               f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
            _tab_hdr = tab_column_header(['Severity','%NoDispo','WoW'], 'minmax(0,1fr) 76px 54px 36px')
            panel_html = f'<div class="kpi-tab-rows">{_tab_hdr}{top5}{next5}{ver_mas_btn}</div>{rest}'
        else:
            panel_html = top5 + next5 + rest
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-nd-pais" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-destino" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-corp" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-hotel" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-canasta" name="tabs-nd" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">% de No Dispo</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div style="font-size:40px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(pct_w18)}</div>
<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pill_nd}</div>
</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;">{tabs}{searchbox_pill_html('sb-kpi-nd', accent_color='#EA0074', placeholder='Buscar…', count_id='cnt-kpi-nd')}</div>
<div id="kpi-nd-panels" class="tab-panels">{panels}</div>
{render_historico_rnd('nodispo', banda, pct_w18, 'hrnd-global-nd')}
</div>'''

def render_kpi_card_rpm(rpm_w18, rpm_w17, rpm_wow):
    banda = banda_rpm(rpm_w18, M['global_current']['bookings'])
    target = "≥ $650"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'rpm')
    
    wow_color = '#2F6C34' if rpm_wow > 0 else '#C0392B'
    wow_arrow = '↑' if rpm_wow > 0 else ('↓' if rpm_wow < 0 else '=')
    wow_str = f'{wow_arrow} {rpm_wow:+.1f}%'.replace('.', ',')
    
    wow_block = wow_box(fmt_num2(rpm_w17), fmt_num2(rpm_w18), wow_str, wow_color, ACCENT)
    # Prop V1: IPM sube = buena → pasar directo, unidad %
    _wow_pill_ipm = wow_pill_html(rpm_wow, unit='%')
    
    tabs = ''
    for t_key, t_label in [('pais','País'),('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-rpm-{t_key}">{t_label}</label>'
    
    panels = ''
    for t_key, t_label, df_t in [
        ('pais','País', TAB_RPM['pais']),
        ('destino','Destino', TAB_RPM['destino']),
        ('corp','Corp', TAB_RPM['corp']),
        ('hotel','Hotel', TAB_RPM['hotel']),
        ('canasta','Canasta', TAB_RPM['canasta']),
    ]:
        # Layout: 1 columna de 5 visible + botón "Ver 5 más" (excepto canasta)
        rows_html = top5 = next5 = rest = ''
        for i, r in df_t.iterrows():
            rpm_val = r.get('RPM', r.get('rpm', r.get('IPM', r.get('ipm', 0))))
            _corp_sub = ''
            if t_key=='canasta':
                raw_lab = r['Canasta']; lab = raw_lab; val = rpm_val
            elif t_key=='hotel':
                raw_lab = str(r['Hotel']); lab = truncate(clean_hotel_name(raw_lab), 38); val = rpm_val
                _corp_sub = truncate(str(r.get('CorpName', '')), 20) if 'CorpName' in r.index else ''
            elif t_key=='pais':
                raw_lab = str(r['PaisDestino']); lab = clean_pais_name(raw_lab, max_len=30); val = rpm_val
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                raw_lab = str(r[col]); lab = truncate(r[col], 36) if t_key=='corp' else clean_destino_name(r[col], 36); val = rpm_val
            show_wow = t_key in ('pais', 'destino', 'corp', 'hotel')
            wow_pill = ''
            if show_wow:
                wow_v = r.get('IPM_WoW_pp', r.get('RPM_WoW_pct', None))
                ipm_prev = r.get('IPM_W18', r.get('IPM_W17', 0))
                if wow_v is not None and not (wow_v != wow_v) and abs(wow_v) > 0.1 and ipm_prev > 0:
                    wow_pct = (wow_v / ipm_prev) * 100
                    mejora = wow_pct > 0
                    arrow = '↑' if wow_pct > 0 else '↓'
                    wow_txt = f'{arrow}{abs(wow_pct):.1f}%'.replace('.', ',')
                    css_cls = "wow-pill dn" if mejora else "wow-pill up"
                    wow_pill = f'<em class="{css_cls}">{wow_txt}</em>'
                else:
                    wow_pill = '<em class="wow-pill nd">—</em>'
            grid = 'minmax(0,1fr) 76px 54px 36px' if show_wow else 'minmax(0,1fr) 76px 54px'
            import math as _mipm
            _ipm_w21 = round(float(val), 2) if val and not _mipm.isnan(float(val)) else 0
            _ipm_w20_raw = r.get('IPM_W18', r.get('IPM_W17', None))
            try: _ipm_w20 = round(float(_ipm_w20_raw), 2) if _ipm_w20_raw is not None and not _mipm.isnan(float(_ipm_w20_raw)) else _ipm_w21
            except: _ipm_w20 = _ipm_w21
            _bnd_ipm = r.get('BandaRPM', r.get('BandaIPM','')) if ('BandaRPM' in r.index or 'BandaIPM' in r.index) else ''
            if not _bnd_ipm and val is not None:
                from engine import banda_rpm as _brpm; _bnd_ipm = _brpm(val, 1)
            _badge_ipm = _mini_badge(_bnd_ipm)
            if i < 5: _cls2 = ''
            elif i < 10: _cls2 = 'rows-more'
            else: _cls2 = 'sb-hidden'
            _row2 = (f'<div class="{_cls2}" data-row-idx="{i}"'
                    f' data-hist-w21="{_ipm_w21}" data-hist-w20="{_ipm_w20}" data-hist-label="{raw_lab}"'
                    f' style="display:grid;grid-template-columns:{grid};align-items:center;gap:10px;'
                    f'width:100%;padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                    f'<div style="min-width:0;overflow:hidden;">'
                    f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
                    + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{_corp_sub}</span>' if _corp_sub else '')
                    + f'</div>'
                    f'<div style="display:flex;align-items:center;min-width:0;overflow:hidden;">{_badge_ipm}</div>'
                    f'<span style="text-align:right;font-size:11px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums;">${fmt_num2(val)}</span>'
                    + (f'{wow_pill}</div>' if show_wow else '</div>'))
            if i < 5: top5 += _row2
            elif i < 10: next5 += _row2
            else: rest += _row2
        if t_key not in ('canasta',):
            has_more = len(df_t) > 5
            ver_mas_btn = ''
            if has_more:
                ver_mas_btn = (f'<button class="rows-toggle" data-panel="{t_key}" '
                               f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                               f'font-size:10px;font-weight:600;color:var(--accent);letter-spacing:.04em;'
                               f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                               f'<span class="toggle-label">Ver 5 más</span> '
                               f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
            _tab_hdr = tab_column_header(['Severity','IPM','WoW'], 'minmax(0,1fr) 76px 54px 36px')
            panel_html = f'<div class="kpi-tab-rows">{_tab_hdr}{top5}{next5}{ver_mas_btn}</div>{rest}'
        else:
            panel_html = top5 + next5 + rest
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-rpm-pais" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-destino" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-corp" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-hotel" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-canasta" name="tabs-rpm" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">IPM <span style="font-weight:500;text-transform:none;letter-spacing:0;color:var(--ink-soft);">· Income Per Million · GB USD por millón</span></div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div style="font-size:40px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">${fmt_num2(rpm_w18)}</div>
<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pill_ipm}</div>
</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;">{tabs}{searchbox_pill_html('sb-kpi-ipm', accent_color='#EA0074', placeholder='Buscar…', count_id='cnt-kpi-ipm')}</div>
<div id="kpi-ipm-panels" class="tab-panels">{panels}</div>
{render_historico_rnd('ipm', banda, rpm_w18, 'hrnd-global-ipm')}
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
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">{cards}</div>
</div>'''

# Build hero
h1, subhead, pct18, rpm18, pct17, rpm17, pct_wow, rpm_wow = render_hero()
HERO = f'''<section class="hero" id="kpis-hero-section">
<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:12px 0 16px;">
{render_kpi_card_nodispo(pct18, pct17, pct_wow)}
{render_kpi_card_rpm(rpm18, rpm17, rpm_wow)}
</div>
<p class="hero-subhead" style="font-size:13px;color:var(--ink-muted);margin:0 0 24px;line-height:1.5;">{subhead}</p>
{render_alerts_block()}
</section>
'''

with open('part1_rnd.html','w') as f:
    f.write(HEAD + '\n<body>\n<div class="shell">\n' + render_masthead() + HERO)
print(f"Part 1 RND escrito: {len(HEAD + HERO):,} chars")