"""
Renderer · Reporte Editorial RND W18
Genera HTML completo · sistema bandas D · post W17
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

# Cargar datos
with open('rnd_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']; TAB_NoDispo = D['TAB_NoDispo']; TAB_RPM = D['TAB_RPM']
CANASTA = D['CANASTA']; sev_nd = D['sev_nd']; sev_rpm = D['sev_rpm']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']

# Cargar head y footer
with open('asset_rnd_head.html') as f: HEAD = f.read()
with open('asset_rnd_footer.html') as f: FOOTER = f.read()

# ============ MASTHEAD ============
def render_masthead():
    LOGO_DATA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQMAAAA/CAYAAADkHq2pAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAACWAAAAAQAAAJYAAAAB"
    # uso el logo del template original; lo extraigo
    import re
    with open('/mnt/project/_TEMPLATE_RatesNoDispo_Reporte.html') as f:
        tmpl = f.read()
    m = re.search(r'src="(data:image/png;base64,[^"]+)"', tmpl)
    LOGO = m.group(1) if m else LOGO_DATA
    return f'''<header class="masthead">
<div class="masthead-top-rule"></div>
<div style="display:table;width:100%;padding:10px 0 9px;border-bottom:1px solid var(--rule);">
<div style="display:table-cell;vertical-align:middle;">
<div style="display:inline-block;vertical-align:top;">
<span class="report-tag" style="display:block;text-align:left;margin-bottom:6px;">RatesNoDispo</span>
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

# ============ HERO H1 + KPI HERO + ALERTS ============
def calc_h1_data():
    """Construye H1 narrativo de 2 líneas."""
    pct = M['global_w18']['pct_nodispo']
    rpm = M['global_w18']['rpm']
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
    bk18 = M['global_w18']['bookings']; bk17 = M['global_w17']['bookings']
    gb18 = M['global_w18']['gb_usd']; gb17 = M['global_w17']['gb_usd']
    tr18 = M['global_w18']['trafico']
    n_hot = M['global_w18']['n_hoteles']
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
    
    subhead = (f'<strong style="color:#EA0074;font-weight:700;">{fmt_big(tr18)}</strong> Tráfico · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_hot)}</strong> hoteles · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(bk18)}</strong> Bookings · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_usd(gb18)}</strong> GB · '
               f'<strong style="color:#EA0074;font-weight:700;">{fmt_int_es(n_p80)}</strong> hoteles P80.')
    
    return h1, subhead, pct, rpm, pct17, rpm17, pct_wow, rpm_wow

def render_kpi_card_nodispo(pct_w18, pct_w17, pct_wow):
    banda = banda_nodispo(pct_w18)
    target = "&lt; 3%"
    pill = banda_pill(banda, target=target)
    gauge = gauge_5levels(banda, 'nodispo')
    
    wow_color = '#2F6C34' if pct_wow < 0 else '#C0392B'  # mejor si baja
    wow_arrow = '↓' if pct_wow < 0 else ('↑' if pct_wow > 0 else '=')
    wow_str = f'{wow_arrow} {abs(pct_wow):+.2f}pp'.replace('+', '').replace('.', ',')
    if pct_wow < 0: wow_str = f'{wow_arrow} -{abs(pct_wow):.2f}pp'.replace('.', ',')
    elif pct_wow > 0: wow_str = f'{wow_arrow} +{pct_wow:.2f}pp'.replace('.', ',')
    else: wow_str = '= 0,00pp'
    
    wow_block = wow_box(fmt_pct2(pct_w17), fmt_pct2(pct_w18), wow_str, wow_color, ACCENT)
    
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
        # 2 columnas · 1-5 izquierda, 6-10 derecha · peor→mejor (ya viene ordenado descendente)
        rows_left, rows_right = '', ''
        for i, r in df_t.iterrows():
            if t_key=='canasta':
                lab = r['Canasta']; val = r['%NoDispo']
            elif t_key=='hotel':
                lab = truncate(clean_hotel_name(r['Hotel']), 30); val = r['%NoDispo']
            else:
                col = {'pais':'PaisDestino','destino':'Destino','corp':'CorpName'}[t_key]
                lab = truncate(r[col], 30); val = r['%NoDispo']
            cell = f'<div><strong>{i+1}. {lab}</strong> <span>{fmt_pct2(val)}</span></div>'
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
<input checked="" id="tab-nd-pais" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-destino" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-corp" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-hotel" name="tabs-nd" style="display:none;" type="radio"/>
<input id="tab-nd-canasta" name="tabs-nd" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">% de No Dispo</div>
<div style="margin-top:4px;">
<div style="font-size:48px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">{fmt_pct2(pct_w18)}</div>
<div style="margin-top:10px;">{pill}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;flex-wrap:wrap;border-bottom:1px solid var(--rule);padding:0 0 0 4px;">{tabs}</div>
<div class="tab-panels">{panels}</div>
</div>'''

def render_kpi_card_rpm(rpm_w18, rpm_w17, rpm_wow):
    banda = banda_rpm(rpm_w18, M['global_w18']['bookings'])
    target = "≥ $650"
    pill = banda_pill(banda, target=target)
    gauge = gauge_5levels(banda, 'rpm')
    
    wow_color = '#2F6C34' if rpm_wow > 0 else '#C0392B'
    wow_arrow = '↑' if rpm_wow > 0 else ('↓' if rpm_wow < 0 else '=')
    wow_str = f'{wow_arrow} {rpm_wow:+.1f}%'.replace('.', ',')
    
    wow_block = wow_box(fmt_num2(rpm_w17), fmt_num2(rpm_w18), wow_str, wow_color, ACCENT)
    
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
        # 2 columnas peor→mejor (TAB_RPM ya viene ordenado ascendente: peor RPM primero)
        rows_left, rows_right = '', ''
        for i, r in df_t.iterrows():
            if t_key=='canasta':
                lab = r['Canasta']; val = r['RPM']
            elif t_key=='hotel':
                lab = truncate(clean_hotel_name(r['Hotel']), 30); val = r['RPM']
            else:
                col = {'pais':'PaisDestino','destino':'Destino','corp':'CorpName'}[t_key]
                lab = truncate(r[col], 30); val = r['RPM']
            cell = f'<div><strong>{i+1}. {lab}</strong> <span>${fmt_num2(val)}</span></div>'
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
<input checked="" id="tab-rpm-pais" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-destino" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-corp" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-hotel" name="tabs-rpm" style="display:none;" type="radio"/>
<input id="tab-rpm-canasta" name="tabs-rpm" style="display:none;" type="radio"/>
<div>
<div style="font-size:10px;color:var(--ink-muted);font-weight:700;letter-spacing:.12em;text-transform:uppercase;">IPM <span style="font-weight:500;text-transform:none;letter-spacing:0;color:var(--ink-soft);">· Income Per Million · GB USD por millón</span></div>
<div style="margin-top:4px;">
<div style="font-size:48px;font-weight:600;letter-spacing:-.02em;color:var(--accent);line-height:1;">${fmt_num2(rpm_w18)}</div>
<div style="margin-top:10px;">{pill}</div>
</div>
</div>
{gauge}
{wow_block}
<div class="tabs-row" style="display:flex;gap:2px;margin-top:14px;flex-wrap:wrap;border-bottom:1px solid var(--rule);padding:0 0 0 4px;">{tabs}</div>
<div class="tab-panels">{panels}</div>
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
            cells += (f'<div style="background:var(--paper);padding:8px 10px;border-radius:3px;">'
                      f'<div style="font-size:8px;font-weight:700;color:{it["pill_color"]};background:{it["pill_bg"]};padding:2px 5px;border-radius:2px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;">{it["pill"]}</div>'
                      f'<div style="font-size:11px;font-weight:700;color:var(--ink);line-height:1.2;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["name"]}</div>'
                      f'<div style="font-size:7px;color:var(--ink-muted);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{it["sub"]}</div>'
                      f'<div style="font-size:18px;font-weight:600;color:{it["pill_color"]};margin-top:6px;letter-spacing:-.02em;line-height:1;">{it["value"]}</div>'
                      f'<div style="font-size:8px;color:var(--ink-muted);margin-top:3px;line-height:1.4;">{it["foot"]}</div>'
                      f'</div>')
        return (f'<div style="background:var(--paper-soft);border-radius:4px;padding:10px;border-top:3px solid {color_b};">'
                f'<div style="font-size:10px;font-weight:700;color:{color_b};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px;">'
                f'<span>{icon}</span><span>{title}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{cells}</div></div>')
    
    h_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(clean_hotel_name(h_nd['Hotel']),38),'sub':f'{h_nd["CorpName"]} · {h_nd["Destino"]}',
         'value':fmt_pct2(h_nd['%NoDispo']),'foot':f'{fmt_big(h_nd["Trafico"])} · {int(h_nd["Bookings"])} BKGS'},
        {'pill':'IPM','pill_color':'#A86A1D','pill_bg':'#FEF3E2',
         'name':truncate(clean_hotel_name(h_rpm['Hotel']),38),'sub':f'{h_rpm["CorpName"]} · {h_rpm["Destino"]}',
         'value':fmt_num2(h_rpm['RPM']),'foot':f'{fmt_big(h_rpm["Trafico"])} · {int(h_rpm["Bookings"])} BKGS'},
    ]
    d_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(d_nd['Destino'],38),'sub':f'{fmt_big(d_nd["Trafico"])} · {int(d_nd["Bookings"])} BKGS',
         'value':fmt_pct2(d_nd['%NoDispo']),'foot':f'IPM {fmt_num2(d_nd["RPM"])}'},
        {'pill':'IPM','pill_color':'#A86A1D','pill_bg':'#FEF3E2',
         'name':truncate(d_rpm['Destino'],38),'sub':f'{fmt_big(d_rpm["Trafico"])} · {int(d_rpm["Bookings"])} BKGS',
         'value':fmt_num2(d_rpm['RPM']),'foot':f'%ND {fmt_pct2(d_rpm["%NoDispo"])}'},
    ]
    c_items = [
        {'pill':'% NoDispo','pill_color':'#EA0074','pill_bg':'#FCE4F1',
         'name':truncate(c_nd['CorpName'],38),'sub':f'{fmt_big(c_nd["Trafico"])} · {int(c_nd["Bookings"])} BKGS',
         'value':fmt_pct2(c_nd['%NoDispo']),'foot':f'IPM {fmt_num2(c_nd["RPM"])}'},
        {'pill':'IPM','pill_color':'#A86A1D','pill_bg':'#FEF3E2',
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
HERO = f'''<section class="hero">
<p class="hero-subhead" style="font-size:14px;color:var(--ink-soft);margin:24px 0;line-height:1.5;">{subhead}</p>
<div class="kpis-hero" style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:0 0 24px;">
{render_kpi_card_nodispo(pct18, pct17, pct_wow)}
{render_kpi_card_rpm(rpm18, rpm17, rpm_wow)}
</div>
{render_alerts_block()}
</section>
'''

with open('part1_rnd.html','w') as f:
    f.write(HEAD + '\n<body>\n<div class="shell">\n' + render_masthead() + HERO)
print(f"Part 1 RND escrito: {len(HEAD + HERO):,} chars")
