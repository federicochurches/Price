"""
Renderer · Reporte Editorial CR W18
Genera HTML completo · sistema bandas D · post W17
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

# Cargar datos
with open('cr_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']
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
    import re
    import os
    tmpl_cr = '/mnt/project/_TEMPLATE_CheckRates_Reporte.html'
    tmpl_rnd = '/mnt/project/_TEMPLATE_RatesNoDispo_Reporte.html'
    tmpl_path = tmpl_cr if os.path.exists(tmpl_cr) else tmpl_rnd
    with open(tmpl_path) as f:
        tmpl = f.read()
    m = re.search(r'src="(data:image/png;base64,[^"]+)"', tmpl)
    LOGO = m.group(1) if m else ''
    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div style="display:table;width:100%;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div style="display:table-cell;vertical-align:middle;">
<div style="display:inline-block;vertical-align:top;">
<span class="report-tag" style="display:block;text-align:left;margin-bottom:6px;">CheckRates</span>
<div style="font-size:26px;font-weight:800;letter-spacing:-.02em;color:var(--ink);line-height:1;">Week 18</div>
<div style="font-size:12px;font-weight:400;color:var(--ink-muted);margin-top:3px;">27 abr – 3 may {MES_AÑO}</div>
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
<span>{PERIODO_LABEL}</span>
<span>Vol. {VOL_NUM}</span>
</div>
</header>
'''

# ============ HERO H1 + KPIs + ALERTS ============
def calc_h1_data():
    """H1 narrativo CR: 2 líneas alineadas."""
    ef = M['global_w18']['eficacia']
    cv = M['global_w18']['conv_rate']
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
    bk18 = M['global_w18']['bookings']; bk17 = M['global_w17']['bookings']
    cr18 = M['global_w18']['cr_unicos']
    n_hot = M['global_w18']['n_hoteles']
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

def render_kpi_card_eficacia(ef_w18, ef_w17, ef_wow):
    banda = banda_eficacia(ef_w18)
    target = "≥ 97%"
    pill = banda_pill(banda, target=target)
    gauge = gauge_5levels(banda, 'eficacia')
    
    wow_color = '#2F6C34' if ef_wow > 0 else '#C0392B'
    wow_arrow = '↑' if ef_wow > 0 else ('↓' if ef_wow < 0 else '=')
    if ef_wow > 0: wow_str = f'{wow_arrow} +{ef_wow:.2f}pp'.replace('.', ',')
    elif ef_wow < 0: wow_str = f'{wow_arrow} {ef_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(ef_w17), fmt_pct2(ef_w18), wow_str, wow_color, CR_ACCENT)
    
    tabs = ''
    for t_key, t_label in [('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-ef-{t_key}">{t_label}</label>'
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    
    panels = ''
    for t_key, df_t in [
        ('destino', TAB_EF['destino']),
        ('corp', TAB_EF['corp']),
        ('hotel', TAB_EF['hotel']),
        ('channel', TAB_EF['channel']),
        ('canasta', TAB_EF['canasta']),
    ]:
        if t_key == 'channel':
            # Split en Producto Propio + Third Party (ordenado peor→mejor por Eficacia)
            df_pp = df_t[df_t['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('Eficacia').reset_index(drop=True)
            df_tp = df_t[df_t['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('Eficacia').reset_index(drop=True)

            def chan_row(i, r, val_col):
                import math
                raw_val = r[val_col] if val_col in r.index else float('nan')
                if raw_val != raw_val or (isinstance(raw_val, float) and math.isinf(raw_val)):
                    val_str = '—'
                else:
                    val_str = fmt_pct2(raw_val)
                wow_col = val_col + '_WoW_pp'
                wow_pill = '<em style="font-style:normal;color:var(--ink-muted);font-size:9px;margin-left:4px;">—</em>'
                try:
                    wow_v = r[wow_col]
                    if wow_v == wow_v and abs(wow_v) >= 0.05:  # ignorar ±0,0
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb = '#EAF3DE' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        wow_txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};margin-left:4px;">{wow_txt}</em>'
                except: pass
                return (f'<div style="display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:4px;">'
                        f'<strong style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{i+1}. {r["ExternalProviderName"]}</strong>'
                        f'<span style="text-align:right;">{val_str}</span>'
                        f'{wow_pill}</div>')

            rows_pp = ''.join(chan_row(i, r, 'Eficacia') for i, r in df_pp.iterrows())
            rows_tp = ''.join(chan_row(i, r, 'Eficacia') for i, r in df_tp.iterrows())
            chan_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{rows_tp}</div>'
                f'</div>'
            )
            panels += f'<div class="tab-panel" data-tab="{t_key}">{chan_html}</div>'
            continue
        # Tabs en 2 columnas · 1-5 izquierda, 6-10 derecha · ya vienen ordenadas peor→mejor (sort_values('Eficacia'))
        rows_left, rows_right = '', ''
        for i, r in df_t.iterrows():
            if t_key=='canasta':
                lab = r['Canasta']; val = r['Eficacia']
            elif t_key=='hotel':
                lab = truncate(clean_hotel_name(r['Hotel']), 26); val = r['Eficacia']
            elif t_key=='corp':
                lab = truncate(clean_corp_name(r['CorpName']), 26); val = r['Eficacia']
            elif t_key=='destino':
                lab = clean_destino_name(r['Destino'], 26); val = r['Eficacia']
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                lab = truncate(r[col], 26); val = r['Eficacia']
            # Pill WoW · solo en destino y corp (tienen merge W17)
            wow_pill = ''
            if t_key in ('destino', 'corp', 'hotel'):
                wow_pp = r.get('Eficacia_WoW_pp', None)
                if wow_pp is not None and wow_pp == wow_pp:  # not NaN
                    mejora = wow_pp > 0  # Eficacia: mejora si sube
                    color = '#2F6C34' if mejora else '#C0392B'
                    bg    = '#EAF3DE' if mejora else '#FCE8E6'
                    arrow = '↑' if wow_pp > 0 else '↓'
                    txt   = f'{arrow}{abs(wow_pp):.1f}'.replace('.', ',')
                    wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{bg};color:{color};margin-left:4px;vertical-align:middle;">{txt}</em>'
            cell = (f'<div style="display:grid;grid-template-columns:1fr 52px 44px;align-items:baseline;">'
                    f'<strong style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{i+1}. {lab}</strong>'
                    f'<span style="text-align:right;">{fmt_pct2(val)}</span>'
                    f'{wow_pill}</div>')
            if i < 5:
                rows_left += cell
            else:
                rows_right += cell
        if rows_right:
            panel_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div>{rows_left}</div><div>{rows_right}</div>'
                f'</div>'
            )
        else:
            panel_html = rows_left
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:18px 20px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-ef-destino" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-corp" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-hotel" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-channel" name="tabs-ef" style="display:none;" type="radio"/>
<input id="tab-ef-canasta" name="tabs-ef" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Eficacia</div>
<div style="margin-top:4px;">
<div style="font-size:48px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(ef_w18)}</div>
<div style="margin-top:10px;">{pill}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;flex-wrap:wrap;border-bottom:1px solid var(--rule);padding:0 0 0 4px;">{tabs}</div>
<div class="tab-panels">{panels}</div>
</div>'''

def render_kpi_card_convrate(cv_w18, cv_w17, cv_wow):
    banda = banda_convrate(cv_w18, M['global_w18']['bookings'])
    target = "≥ 2,5%"
    pill = banda_pill(banda, target=target)
    gauge = gauge_5levels(banda, 'convrate')
    
    wow_color = '#2F6C34' if cv_wow > 0 else '#C0392B'
    wow_arrow = '↑' if cv_wow > 0 else ('↓' if cv_wow < 0 else '=')
    if cv_wow > 0: wow_str = f'{wow_arrow} +{cv_wow:.2f}pp'.replace('.', ',')
    elif cv_wow < 0: wow_str = f'{wow_arrow} {cv_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(cv_w17), fmt_pct2(cv_w18), wow_str, wow_color, CR_ACCENT)
    
    tabs = ''
    for t_key, t_label in [('destino','Destino'),('corp','Corp'),('hotel','Hotel'),('channel','Channel'),('canasta','Canasta')]:
        tabs += f'<label class="tab-label" for="tab-cv-{t_key}">{t_label}</label>'
    
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    
    panels = ''
    for t_key, df_t in [
        ('destino', TAB_CV['destino']),
        ('corp', TAB_CV['corp']),
        ('hotel', TAB_CV['hotel']),
        ('channel', TAB_CV['channel']),
        ('canasta', TAB_CV['canasta']),
    ]:
        if t_key == 'channel':
            # Split en Producto Propio + Third Party (peor→mejor por ConvRate)
            df_pp = df_t[df_t['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('ConvRate').reset_index(drop=True)
            df_tp = df_t[df_t['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('ConvRate').reset_index(drop=True)

            def chan_row_cv(i, r, val_col):
                import math
                raw_val = r[val_col] if val_col in r.index else float('nan')
                if raw_val != raw_val or (isinstance(raw_val, float) and math.isinf(raw_val)):
                    val_str = '—'
                else:
                    val_str = fmt_pct2(raw_val)
                wow_col = val_col + '_WoW_pp'
                wow_pill = '<em style="font-style:normal;color:var(--ink-muted);font-size:9px;margin-left:4px;">—</em>'
                try:
                    wow_v = r[wow_col]
                    if wow_v == wow_v and abs(wow_v) >= 0.05:
                        mejora = wow_v > 0
                        wc = '#2F6C34' if mejora else '#C0392B'
                        wb = '#EAF3EA' if mejora else '#FCE8E6'
                        arrow = '↑' if wow_v > 0 else '↓'
                        wow_txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                        wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};margin-left:4px;">{wow_txt}</em>'
                except: pass
                return (f'<div style="display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:4px;">'
                        f'<strong style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{i+1}. {r["ExternalProviderName"]}</strong>'
                        f'<span style="text-align:right;">{val_str}</span>'
                        f'{wow_pill}</div>')

            rows_pp = ''.join(chan_row_cv(i, r, 'ConvRate') for i, r in df_pp.iterrows())
            rows_tp = ''.join(chan_row_cv(i, r, 'ConvRate') for i, r in df_tp.iterrows())
            chan_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div><div style="font-size:9px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🏠 Producto Propio</div>{rows_pp}</div>'
                f'<div><div style="font-size:9px;font-weight:700;color:#4FC3F4;letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">🔌 Third Party</div>{rows_tp}</div>'
                f'</div>'
            )
            panels += f'<div class="tab-panel" data-tab="{t_key}">{chan_html}</div>'
            continue
        # 2 columnas · 1-5 izquierda, 6-10 derecha · peor→mejor
        rows_left, rows_right = '', ''
        for i, r in df_t.iterrows():
            if t_key=='canasta':
                lab = r['Canasta']; val = r['ConvRate']
            elif t_key=='hotel':
                lab = truncate(clean_hotel_name(r['Hotel']), 26); val = r['ConvRate']
            elif t_key=='corp':
                lab = truncate(clean_corp_name(r['CorpName']), 26); val = r['ConvRate']
            elif t_key=='destino':
                lab = clean_destino_name(r['Destino'], 26); val = r['ConvRate']
            else:
                col = {'destino':'Destino','corp':'CorpName'}[t_key]
                lab = truncate(r[col], 26); val = r['ConvRate']
            # Pill WoW · solo en destino, corp y hotel (tienen merge W17)
            wow_pill = ''
            if t_key in ('destino', 'corp', 'hotel'):
                wow_pp = r.get('ConvRate_WoW_pp', None)
                if wow_pp is not None and wow_pp == wow_pp:  # not NaN
                    mejora = wow_pp > 0  # ConvRate: mejora si sube
                    color = '#2F6C34' if mejora else '#C0392B'
                    bg    = '#EAF3DE' if mejora else '#FCE8E6'
                    arrow = '↑' if wow_pp > 0 else '↓'
                    txt   = f'{arrow}{abs(wow_pp):.1f}'.replace('.', ',')
                    wow_pill = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{bg};color:{color};margin-left:4px;vertical-align:middle;">{txt}</em>'
            cell = (f'<div style="display:grid;grid-template-columns:1fr 52px 44px;align-items:baseline;">'
                    f'<strong style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{i+1}. {lab}</strong>'
                    f'<span style="text-align:right;">{fmt_pct2(val)}</span>'
                    f'{wow_pill}</div>')
            if i < 5:
                rows_left += cell
            else:
                rows_right += cell
        if rows_right:
            panel_html = (
                f'<div style="grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px;">'
                f'<div>{rows_left}</div><div>{rows_right}</div>'
                f'</div>'
            )
        else:
            panel_html = rows_left
        panels += f'<div class="tab-panel" data-tab="{t_key}">{panel_html}</div>'
    
    return f'''<div class="kpi-card" style="border:1px solid var(--rule);padding:18px 20px;border-radius:3px;background:var(--paper);">
<input checked="" id="tab-cv-destino" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-corp" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-hotel" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-channel" name="tabs-cv" style="display:none;" type="radio"/>
<input id="tab-cv-canasta" name="tabs-cv" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Conversion Rate</div>
<div style="margin-top:4px;">
<div style="font-size:48px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(cv_w18)}</div>
<div style="margin-top:10px;">{pill}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;flex-wrap:wrap;border-bottom:1px solid var(--rule);padding:0 0 0 4px;">{tabs}</div>
<div class="tab-panels">{panels}</div>
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
            cells += (f'<div style="background:var(--paper);padding:8px 10px;border-radius:3px;">'
                      f'<div style="font-size:8px;font-weight:700;color:{it["pill_color"]};background:{it["pill_bg"]};padding:2px 5px;border-radius:2px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;">{it["pill"]}</div>'
                      f'<div style="font-size:11px;font-weight:700;color:var(--ink);line-height:1.2;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["name"]}</div>'
                      f'<div style="font-size:7px;color:var(--ink-muted);margin-top:1px;">{it["sub"]}</div>'
                      f'<div style="font-size:18px;font-weight:600;color:{it["pill_color"]};margin-top:6px;letter-spacing:-.02em;line-height:1;">{it["value"]}</div>'
                      f'<div style="font-size:8px;color:var(--ink-muted);margin-top:3px;line-height:1.4;">{it["foot"]}</div>'
                      f'</div>')
        return (f'<div style="background:var(--paper-soft);border-radius:4px;padding:10px;border-top:3px solid {color_b};">'
                f'<div style="font-size:10px;font-weight:700;color:{color_b};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px;">'
                f'<span>{icon}</span><span>{title}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{cells}</div></div>')
    
    h_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(clean_hotel_name(h_ef['Hotel']),38),'sub':f'{h_ef["CorpName"]} · {h_ef["Destino"]}',
         'value':fmt_pct2(h_ef['Eficacia']),'foot':f'{fmt_int_es(h_ef["CR_Unicos"])} CR · {int(h_ef["Bookings"])} BKGS'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EDE8F7',
         'name':truncate(clean_hotel_name(h_cv['Hotel']),38),'sub':f'{h_cv["CorpName"]} · {h_cv["Destino"]}',
         'value':fmt_pct2(h_cv['ConvRate']),'foot':f'{fmt_int_es(h_cv["CR_Unicos"])} CR · {int(h_cv["Bookings"])} BKGS'},
    ]
    d_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':clean_destino_name(d_ef['Destino'],38),'sub':f'{fmt_int_es(d_ef["CR_Unicos"])} CR · {int(d_ef["Bookings"])} BKGS',
         'value':fmt_pct2(d_ef['Eficacia']),'foot':f'CR {fmt_pct2(d_ef["ConvRate"])}'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EDE8F7',
         'name':clean_destino_name(d_cv['Destino'],38),'sub':f'{fmt_int_es(d_cv["CR_Unicos"])} CR · {int(d_cv["Bookings"])} BKGS',
         'value':fmt_pct2(d_cv['ConvRate']),'foot':f'Ef {fmt_pct2(d_cv["Eficacia"])}'},
    ]
    ch_items = [
        {'pill':'Eficacia','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(ch_ef['ExternalProviderName'],38),'sub':f'{fmt_int_es(ch_ef["CR_Unicos"])} CR · {int(ch_ef["Bookings"])} BKGS',
         'value':fmt_pct2(ch_ef['Eficacia']),'foot':f'CR {fmt_pct2(ch_ef["ConvRate"])}'},
        {'pill':'ConvRate','pill_color':'#5C469C','pill_bg':'#EDE8F7',
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
HERO = f'''<section class="hero">
<p class="hero-subhead" style="font-size:14px;color:var(--ink-soft);margin:24px 0;line-height:1.5;">{subhead}</p>
<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">
{render_kpi_card_eficacia(ef18, ef17, ef_wow)}
{render_kpi_card_convrate(cv18, cv17, cv_wow)}
</div>
{render_alerts_block()}
</section>
'''

with open('part1_cr.html','w') as f:
    f.write(HEAD + '\n<body>\n<div class="shell">\n' + render_masthead() + HERO)
print(f"Part 1 CR escrito: {len(HEAD + HERO):,} chars")
