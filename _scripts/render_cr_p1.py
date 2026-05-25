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
with open(os.getenv('PICKLE_CR', 'cr_w20_data.pkl'),'rb') as f:
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
def render_masthead():
    LOGO = "data:image/png;base64,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"

    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div style="display:table;width:100%;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div style="display:table-cell;vertical-align:middle;">
<div style="display:inline-block;vertical-align:top;">
<span class="report-tag" style="display:block;text-align:left;margin-bottom:6px;">CheckRates</span>
<div style="font-size:26px;font-weight:800;letter-spacing:-.02em;color:var(--ink);line-height:1;">Week {WEEK_NUM}</div>
<div style="font-size:12px;font-weight:400;color:var(--ink-muted);margin-top:3px;">{PERIODO}</div>
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
    
    subhead = (f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(cr18)}</strong> CR únicos · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(n_hot)}</strong> hoteles · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(bk18)}</strong> Bookings · '
               f'<strong style="color:#5C469C;font-weight:700;">{fmt_int_es(n_p80)}</strong> hoteles P80.')
    
    return h1, subhead, ef, cv, ef17, cv17, ef_wow, cv_wow

# Color de acento CR (cyan/teal)
CR_ACCENT = '#5C469C'

from historico_module_v2 import render_historico_cr

def _mini_badge(bnd):
    if not bnd or not isinstance(bnd, str): return ''
    bc = BANDA_COLORS.get(bnd, {})
    bg = bc.get('bg', '#F2EEE6'); fg = bc.get('fg', '#5F5E5A')
    return f'<span style="flex-shrink:0;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;">{bnd}</span>'


def render_kpi_card_eficacia(ef_w18, ef_w17, ef_wow, week_num='W20', week_prev='W19'):
    banda = banda_eficacia(ef_w18)
    target = "≥ 97%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'eficacia')
    
    wow_color = '#2F6C34' if ef_wow > 0 else '#C0392B'
    wow_arrow = '↑' if ef_wow > 0 else ('↓' if ef_wow < 0 else '=')
    if ef_wow > 0: wow_str = f'{wow_arrow} +{ef_wow:.2f}pp'.replace('.', ',')
    elif ef_wow < 0: wow_str = f'{wow_arrow} {ef_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(ef_w17), fmt_pct2(ef_w18), wow_str, wow_color, CR_ACCENT, week_num, week_prev)
    # Prop V1: pill WoW redondeada (+ = verde, - = rojo)
    _wow_pill_ef = wow_pill_html(ef_wow, unit='pp')
    
    tabs = ''
    for t_key, t_label in [('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-ef-{t_key}">{t_label}</label>'
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds','Hotel Unico','Travelgate']
    
    panels = ''
    for t_key, df_t in [
        ('destino', TAB_EF['destino']),
        ('corp', TAB_EF['corp']),
        ('hotel', TAB_EF['hotel']),
        ('channel', TAB_EF['channel']),
        ('canasta', TAB_EF['canasta']),
    ]:
        if t_key == 'channel':
            # Split en Producto Propio + Third Party — catálogo canónico fijo
            # Para canales sin datos esa semana se renderiza '—'
            def _lookup_chan(nombre, df_src):
                """Busca nombre en df_src; si no existe devuelve row dummy con NaN."""
                import math
                # Normalizar: HotelBeds* → 'HotelBeds'
                _name_norm = nombre
                mask = df_src['ExternalProviderName'].str.startswith(nombre) if nombre == 'HotelBeds' else df_src['ExternalProviderName'] == nombre
                hits = df_src[mask]
                if len(hits) == 0:
                    return None
                return hits.iloc[0]

            # Ordenar los que tienen datos por Eficacia (peor primero), luego los sin datos al final
            def _sorted_canonical(lista, df_src, val_col):
                with_data = []
                without_data = []
                for nombre in lista:
                    r = _lookup_chan(nombre, df_src)
                    if r is not None:
                        with_data.append((nombre, r))
                    else:
                        without_data.append((nombre, None))
                with_data.sort(key=lambda x: x[1][val_col] if not (x[1][val_col] != x[1][val_col]) else 999)
                return with_data + without_data

            _pp_sorted = _sorted_canonical(PRODUCTO_PROPIO, df_t, 'Eficacia')
            _tp_sorted = _sorted_canonical(THIRD_PARTY, df_t, 'Eficacia')

            _WOW_MUTED_EF = '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F2EEE6;color:#8A8377;margin-left:4px;white-space:nowrap;">—</em>'

            def chan_row(i, nombre, r, val_col):
                import math
                # r=None → canal sin datos esta semana: fila atenuada con guiones
                if r is None:
                    return (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 52px 32px;align-items:center;gap:4px;padding:4px 0;opacity:.45;">'
                            f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;color:var(--ink-muted);">{i+1}. {nombre}</span>'
                            f'<span style="text-align:right;color:var(--ink-muted);">—</span>'
                            f'{_WOW_MUTED_EF}</div>')
                raw_val = r[val_col] if val_col in r.index else float('nan')
                if raw_val != raw_val or (isinstance(raw_val, float) and math.isinf(raw_val)):
                    val_str = '—'
                else:
                    val_str = fmt_pct2(raw_val)
                wow_col = val_col + '_WoW_pp'
                try:
                    wow_v = r[wow_col]
                    if wow_v != wow_v: raise ValueError
                    if raw_val is not None and not math.isnan(float(raw_val)) and abs(raw_val - 1.0) < 0.0001:
                        wow_pill = '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#EAF3DE;color:#2F6C34;margin-left:4px;white-space:nowrap;">= 0,0</em>'
                    elif abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb = '#EAF3DE' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        wow_txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};margin-left:4px;white-space:nowrap;">{wow_txt}</em>'
                    else:
                        wow_pill = _WOW_MUTED_EF
                except:
                    wow_pill = _WOW_MUTED_EF
                _w21 = round(float(raw_val)*100, 4) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isnan(raw_val)) else 0
                _lbl = str(r.get('ExternalProviderName', nombre))
                return (f'<div data-hist-w21="{_w21}" data-hist-w20="{_w21}" data-hist-label="{_lbl}"'
                        f' style="display:grid;grid-template-columns:minmax(0,1fr) 52px 32px;align-items:center;gap:4px;padding:4px 0;cursor:pointer;transition:background .12s;">'
                        f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;">{i+1}. {_lbl}</span>'
                        f'<span style="text-align:right;font-variant-numeric:tabular-nums;">{val_str}</span>'
                        f'{wow_pill}</div>')

            rows_pp = ''.join(chan_row(i, nombre, r, 'Eficacia') for i, (nombre, r) in enumerate(_pp_sorted))
            rows_tp = ''.join(chan_row(i, nombre, r, 'Eficacia') for i, (nombre, r) in enumerate(_tp_sorted))
            chan_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{rows_tp}</div>'
                f'</div>'
            )
            panels += f'<div class="tab-panel" data-tab="{t_key}">{chan_html}</div>'
            continue
        # Layout: 1 columna de 5 visible + botón "Ver 5 más" (excepto channel/canasta)
        rows_html = top5 = next5 = rest = ''
        for i, r in df_t.iterrows():
            _corp_sub = ''
            if t_key=='canasta':
                raw_lab = r['Canasta']; lab = raw_lab; val = r['Eficacia']
            elif t_key=='hotel':
                raw_lab = str(r['Hotel']); lab = truncate(clean_hotel_name(raw_lab), 38); val = r['Eficacia']
                _corp_sub = truncate(str(r.get('CorpName', '')), 20) if 'CorpName' in r.index else ''
            elif t_key=='corp':
                raw_lab = str(r['CorpName']); lab = truncate(clean_corp_name(raw_lab), 36); val = r['Eficacia']
            elif t_key=='destino':
                raw_lab = str(r['Destino']); lab = clean_destino_name(raw_lab, 36); val = r['Eficacia']
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                raw_lab = str(r[col]); lab = truncate(r[col], 32); val = r['Eficacia']
            wow_pill = ''
            if t_key in ('destino', 'corp', 'hotel'):
                wow_pill = make_wow_pill_row(r.get('Eficacia_WoW_pp', None))
            import math as _math
            _w21 = round(val * 100, 4) if val and not _math.isnan(float(val)) else 0
            _w20_raw = r.get('Eficacia_W17', None)
            _w20 = round(float(_w20_raw) * 100, 4) if _w20_raw and not _math.isnan(float(_w20_raw)) else _w21
            _bnd = r.get('BandaEficacia','') if 'BandaEficacia' in r.index else (banda_eficacia(val) if val is not None else '')
            _badge = _mini_badge(_bnd)
            # Clases de visibilidad: top5 visible, next5 oculta (rows-more), rest sb-hidden
            if i < 5:
                _cls = ''
            elif i < 10:
                _cls = 'rows-more'  # oculto por CSS, mostrado con botón
            else:
                _cls = 'sb-hidden'
            _row = (f'<div class="{_cls}" data-row-idx="{i}"'
                    f' data-hist-w21="{_w21}" data-hist-w20="{_w20}" data-hist-label="{raw_lab}"'
                    f' style="display:grid;grid-template-columns:minmax(0,1fr) 80px 54px 40px;align-items:center;gap:10px;'
                    f'padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                    f'<div style="min-width:0;overflow:hidden;">'
                    f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
                    + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{_corp_sub}</span>' if _corp_sub else '')
                    + f'</div>'
                    f'<div style="display:flex;align-items:center;">{_badge}</div>'
                    f'<span style="text-align:right;font-size:11px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(val)}</span>'
                    f'{wow_pill}</div>')
            if i < 5: top5 += _row
            elif i < 10: next5 += _row
            else: rest += _row
        if t_key not in ('channel', 'canasta'):
            total_rows = len(df_t)
            has_more = total_rows > 5
            ver_mas_btn = ''
            if has_more:
                ver_mas_btn = (f'<button class="rows-toggle" data-panel="{t_key}" '
                               f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                               f'font-size:10px;font-weight:600;color:var(--accent);letter-spacing:.04em;'
                               f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                               f'<span class="toggle-label">Ver 5 más</span> '
                               f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
            _tab_hdr = tab_column_header(['Severity','Eficacia','WoW'], 'minmax(0,1fr) 80px 54px 40px')
            panel_html = f'<div class="kpi-tab-rows">{_tab_hdr}{top5}{next5}</div>{rest}{ver_mas_btn}'
        else:
            panel_html = top5 + next5 + rest
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-ef-destino" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-corp" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-hotel" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-channel" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-canasta" name="tabs-ef" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Eficacia</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div style="font-size:40px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(ef_w18)}</div>
<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pill_ef}</div>
</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;">{tabs}{searchbox_pill_html('sb-kpi-ef', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-kpi-ef')}</div>
<div id="kpi-ef-panels" class="tab-panels">{panels}</div>
{render_historico_cr('eficacia', banda, ef_w18, 'hcr-global-ef')}
</div>'''

def render_kpi_card_convrate(cv_w18, cv_w17, cv_wow, week_num='W20', week_prev='W19'):
    banda = banda_convrate(cv_w18, M['global_current']['bookings'])
    target = "≥ 2,5%"
    pill = banda_pill(banda, target=target)
    pill_with_target = pill + target_caption(target)
    gauge = gauge_5levels(banda, 'convrate')
    
    wow_color = '#2F6C34' if cv_wow > 0 else '#C0392B'
    wow_arrow = '↑' if cv_wow > 0 else ('↓' if cv_wow < 0 else '=')
    if cv_wow > 0: wow_str = f'{wow_arrow} +{cv_wow:.2f}pp'.replace('.', ',')
    elif cv_wow < 0: wow_str = f'{wow_arrow} {cv_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(cv_w17), fmt_pct2(cv_w18), wow_str, wow_color, CR_ACCENT, week_num, week_prev)
    # Prop V1: pill WoW redondeada
    _wow_pill_cv = wow_pill_html(cv_wow, unit='pp')
    
    tabs = ''
    for t_key, t_label in [('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-cv-{t_key}">{t_label}</label>'
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds','Hotel Unico','Travelgate']
    
    panels = ''
    for t_key, df_t in [
        ('destino', TAB_CV['destino']),
        ('corp', TAB_CV['corp']),
        ('hotel', TAB_CV['hotel'][TAB_CV['hotel']['Bookings'] > 0].sort_values('ConvRate').reset_index(drop=True)),
        ('channel', TAB_CV['channel']),
        ('canasta', TAB_CV['canasta']),
    ]:
        if t_key == 'channel':
            # Split en Producto Propio + Third Party — catálogo canónico fijo
            def _lookup_chan_cv(nombre, df_src):
                mask = df_src['ExternalProviderName'].str.startswith(nombre) if nombre == 'HotelBeds' else df_src['ExternalProviderName'] == nombre
                hits = df_src[mask]
                return hits.iloc[0] if len(hits) > 0 else None

            def _sorted_canonical_cv(lista, df_src, val_col):
                with_data = []
                without_data = []
                for nombre in lista:
                    r = _lookup_chan_cv(nombre, df_src)
                    if r is not None:
                        with_data.append((nombre, r))
                    else:
                        without_data.append((nombre, None))
                with_data.sort(key=lambda x: x[1][val_col] if not (x[1][val_col] != x[1][val_col]) else 999)
                return with_data + without_data

            _pp_sorted_cv = _sorted_canonical_cv(PRODUCTO_PROPIO, df_t, 'ConvRate')
            _tp_sorted_cv = _sorted_canonical_cv(THIRD_PARTY, df_t, 'ConvRate')

            _WOW_MUTED_CV = '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F2EEE6;color:#8A8377;margin-left:4px;white-space:nowrap;">—</em>'

            def chan_row_cv(i, nombre, r, val_col):
                import math
                if r is None:
                    return (f'<div style="display:grid;grid-template-columns:minmax(0,1fr) 52px 32px;align-items:center;gap:4px;padding:4px 0;opacity:.45;">'
                            f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;color:var(--ink-muted);">{i+1}. {nombre}</span>'
                            f'<span style="text-align:right;color:var(--ink-muted);">—</span>'
                            f'{_WOW_MUTED_CV}</div>')
                raw_val = r[val_col] if val_col in r.index else float('nan')
                if raw_val != raw_val or (isinstance(raw_val, float) and math.isinf(raw_val)):
                    val_str = '—'
                else:
                    val_str = fmt_pct2(raw_val)
                wow_col = val_col + '_WoW_pp'
                try:
                    wow_v = r[wow_col]
                    if wow_v != wow_v: raise ValueError
                    if abs(wow_v) >= 0.005:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb = '#EAF3DE' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        wow_txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};margin-left:4px;white-space:nowrap;">{wow_txt}</em>'
                    else:
                        wow_pill = _WOW_MUTED_CV
                except:
                    wow_pill = _WOW_MUTED_CV
                _w21 = round(float(raw_val)*100, 4) if raw_val == raw_val and not (isinstance(raw_val, float) and math.isnan(raw_val)) else 0
                _lbl = str(r.get('ExternalProviderName', nombre))
                return (f'<div data-hist-w21="{_w21}" data-hist-w20="{_w21}" data-hist-label="{_lbl}"'
                        f' style="display:grid;grid-template-columns:minmax(0,1fr) 52px 32px;align-items:center;gap:4px;padding:4px 0;cursor:pointer;transition:background .12s;">'
                        f'<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;min-width:0;">{i+1}. {_lbl}</span>'
                        f'<span style="text-align:right;font-variant-numeric:tabular-nums;">{val_str}</span>'
                        f'{wow_pill}</div>')

            rows_pp = ''.join(chan_row_cv(i, nombre, r, 'ConvRate') for i, (nombre, r) in enumerate(_pp_sorted_cv))
            rows_tp = ''.join(chan_row_cv(i, nombre, r, 'ConvRate') for i, (nombre, r) in enumerate(_tp_sorted_cv))
            chan_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{rows_tp}</div>'
                f'</div>'
            )
            panels += f'<div class="tab-panel" data-tab="{t_key}">{chan_html}</div>'
            continue
        # Layout: 1 columna de 5 visible + botón "Ver 5 más" (excepto channel/canasta)
        rows_html = top5 = next5 = rest = ''
        for i, r in df_t.iterrows():
            _corp_sub = ''
            if t_key=='canasta':
                raw_lab = r['Canasta']; lab = raw_lab; val = r['ConvRate']
            elif t_key=='hotel':
                raw_lab = str(r['Hotel']); lab = truncate(clean_hotel_name(raw_lab), 38); val = r['ConvRate']
                _corp_sub = truncate(str(r.get('CorpName', '')), 20) if 'CorpName' in r.index else ''
            elif t_key=='corp':
                raw_lab = str(r['CorpName']); lab = truncate(clean_corp_name(raw_lab), 36); val = r['ConvRate']
            elif t_key=='destino':
                raw_lab = str(r['Destino']); lab = clean_destino_name(raw_lab, 36); val = r['ConvRate']
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                raw_lab = str(r[col]); lab = truncate(r[col], 32); val = r['ConvRate']
            wow_pill = ''
            if t_key in ('destino', 'corp', 'hotel'):
                wow_pill = make_wow_pill_row(r.get('ConvRate_WoW_pp', None))
            import math as _math
            _w21 = round(val * 100, 4) if val and not _math.isnan(float(val)) else 0
            _w20_raw = r.get('ConvRate_W17', None)
            _w20 = round(float(_w20_raw) * 100, 4) if _w20_raw and not _math.isnan(float(_w20_raw)) else _w21
            _bnd_cv = (
                r.get('BandaConvRate','') if 'BandaConvRate' in r.index else (banda_convrate(val, int(r.get('Bookings',0))) if val is not None else ''))
            _badge_cv = _mini_badge(_bnd_cv)
            if i < 5: _cls = ''
            elif i < 10: _cls = 'rows-more'
            else: _cls = 'sb-hidden'
            _row = (f'<div class="{_cls}" data-row-idx="{i}"'
                    f' data-hist-w21="{_w21}" data-hist-w20="{_w20}" data-hist-label="{raw_lab}"'
                    f' style="display:grid;grid-template-columns:minmax(0,1fr) 80px 68px 40px;align-items:center;gap:10px;'
                    f'padding:6px 0;border-bottom:1px solid var(--rule-soft);cursor:pointer;transition:background .12s;">'
                    f'<div style="min-width:0;overflow:hidden;">'
                    f'<span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{i+1}. {lab}</span>'
                    + (f'<span style="font-size:9px;color:var(--ink-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{_corp_sub}</span>' if _corp_sub else '')
                    + f'</div>'
                    f'<div style="display:flex;align-items:center;">{_badge_cv}</div>'
                    f'<span style="text-align:right;font-size:11px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums;">{fmt_pct2(val)}</span>'
                    f'{wow_pill}</div>')
            if i < 5: top5 += _row
            elif i < 10: next5 += _row
            else: rest += _row
        if t_key not in ('channel', 'canasta'):
            total_rows = len(df_t)
            has_more = total_rows > 5
            ver_mas_btn = ''
            if has_more:
                ver_mas_btn = (f'<button class="rows-toggle" data-panel="{t_key}" '
                               f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                               f'font-size:10px;font-weight:600;color:var(--accent);letter-spacing:.04em;'
                               f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                               f'<span class="toggle-label">Ver 5 más</span> '
                               f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
            _tab_hdr = tab_column_header(['Severity','Conv Rate','WoW'], 'minmax(0,1fr) 80px 68px 40px')
            panel_html = f'<div class="kpi-tab-rows">{_tab_hdr}{top5}{next5}</div>{rest}{ver_mas_btn}'
        else:
            panel_html = top5 + next5 + rest
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:12px 16px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-cv-destino" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-corp" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-hotel" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-channel" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-canasta" name="tabs-cv" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Conversion Rate</div>
<div style="margin-top:4px;display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;">
<div>
<div style="font-size:40px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(cv_w18)}</div>
<div style="margin-top:5px;display:flex;align-items:center;gap:6px;font-size:10px;color:var(--ink-muted);">vs sem. ant. {_wow_pill_cv}</div>
</div>
<div style="padding-top:4px;">{pill_with_target}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;border-bottom:1px solid var(--rule);padding:0 0 0 4px;align-items:flex-end;">{tabs}{searchbox_pill_html('sb-kpi-cv', accent_color='#5C469C', placeholder='Buscar…', count_id='cnt-kpi-cv')}</div>
<div id="kpi-cv-panels" class="tab-panels">{panels}</div>
{render_historico_cr('convrate', banda, cv_w18, 'hcr-global-cv')}
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
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">{cards}</div>
</div>'''

# Build hero
h1, subhead, ef18, cv18, ef17, cv17, ef_wow, cv_wow = render_hero()
HERO = f'''<section class="hero" id="kpis-hero-section">
<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:12px 0 16px;">
{render_kpi_card_eficacia(ef18, ef17, ef_wow, 'W20', 'W19')}
{render_kpi_card_convrate(cv18, cv17, cv_wow, 'W20', 'W19')}
</div>
<p class="hero-subhead" style="font-size:13px;color:var(--ink-muted);margin:0 0 24px;line-height:1.5;">{subhead}</p>
</section>
'''

with open('part1_cr.html','w') as f:
    f.write(HEAD + '\n<body>\n<div class="shell">\n' + render_masthead() + HERO)
print(f"Part 1 CR escrito: {len(HEAD + HERO):,} chars")
