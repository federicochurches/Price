"""
Renderer RND parte 2: Resumen Ejecutivo, Severity, Top 5
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

with open('rnd_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']; TAB_NoDispo = D['TAB_NoDispo']; TAB_RPM = D['TAB_RPM']
CANASTA = D['CANASTA']; sev_nd = D['sev_nd']; sev_rpm = D['sev_rpm']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']

# ============ RESUMEN EJECUTIVO · 10 findings ============
def build_findings():
    """Genera 10 findings con estructura template: numero + titulo + desc."""
    pct = M['global_w18']['pct_nodispo']; pct17 = M['global_w17']['pct_nodispo']
    rpm = M['global_w18']['rpm']; rpm17 = M['global_w17']['rpm']
    bk = M['global_w18']['bookings']; bk17 = M['global_w17']['bookings']
    gb = M['global_w18']['gb_usd']; gb17 = M['global_w17']['gb_usd']
    
    pct_wow = (pct - pct17) * 100
    rpm_wow = (rpm/rpm17 - 1) * 100
    bk_wow = (bk/bk17 - 1) * 100
    
    n_p80 = len(p80_hotel)
    n_supcrit = sev_nd['Súper Crítica']
    n_critmas = sev_nd['Crítica'] + sev_nd['Súper Crítica']
    n_sin_conv = sev_rpm['Sin Conversión']
    n_critica_rpm = sev_rpm['Crítica']
    pct_sin_conv = n_sin_conv/n_p80*100
    
    dnc_p80_total = p80_hotel['DemandaNoConvertida'].sum()
    dnc_global = (g_hotel['Trafico']*g_hotel['%NoDispo']).sum()
    pct_dnc_p80 = dnc_p80_total/dnc_global*100
    
    by_corp = g_hotel.groupby('CorpName').agg(DNC=('DemandaNoConvertida','sum'), TR=('Trafico','sum'), BK=('Bookings','sum')).reset_index()
    by_corp = by_corp.sort_values('DNC', ascending=False)
    top1_corp = by_corp.iloc[0]
    
    by_dest = g_hotel.groupby('Destino').agg(DNC=('DemandaNoConvertida','sum'), TR=('Trafico','sum')).reset_index()
    by_dest['pctND'] = by_dest['DNC']/by_dest['TR']
    by_dest = by_dest.sort_values('DNC', ascending=False).head(3)
    
    cb = M['B2C_w18']; co = M['B2B (OP)_w18']; cu = M['CUG (UOP)_w18']
    cug_rpm_wow = (cu['rpm']/M['CUG (UOP)_w17']['rpm']-1)*100
    
    h0 = TOP['sin_conv'].iloc[0]
    
    def es_pct(v, dec=2):
        return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}pp'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    def es_num2(v):
        return f'{v:,.2f}'.replace(',','|').replace('.',',').replace('|','.')
    
    findings = [
        {'numero': es_pct(pct*100,2),
         'titulo': '% NoDispo global · banda Aceptable',
         'desc': f'WoW {es_pp(pct_wow)} · primera vez que se acerca a la zona Exitosa (target &lt;3%) tras semanas en Revisar.'},
        {'numero': '$' + es_num2(rpm),
         'titulo': f'IPM (Income Per Million USD) · banda {M["global_w18"]["banda_rpm"]}',
         'desc': f'WoW {es_pct1(rpm_wow)} · sigue por debajo del target ≥ $650 con deterioro en tráfico (-1,7%) y bookings ({es_pct1(bk_wow)}) anticipa presión.'},
        {'numero': fmt_big(dnc_p80_total),
         'titulo': 'Demanda no convertida en P80',
         'desc': f'{f"{pct_dnc_p80:.0f}".replace(".",",")}% del total ({fmt_big(dnc_global)}) provienen de los {fmt_int_es(n_p80)} hoteles del P80 · concentración estructural.'},
        {'numero': fmt_int_es(n_critmas),
         'titulo': 'Hoteles P80 Severity Crítica+',
         'desc': f'{es_pct(n_critmas/n_p80*100,1)} del P80 · de ellos {n_supcrit} Súper Críticos son los más urgentes para escalar a Supply.'},
        {'numero': fmt_int_es(n_sin_conv),
         'titulo': 'Hoteles P80 Sin Conversión (BKGS=0)',
         'desc': f'{es_pct(pct_sin_conv,1)} del P80 · cohorte estructural · diagnóstico técnico/contractual, no de eficacia. {fmt_int_es(n_critica_rpm)} adicionales en Crítica.'},
        {'numero': fmt_big(top1_corp["DNC"]),
         'titulo': f'{top1_corp["CorpName"]} · líder demanda perdida',
         'desc': f'búsquedas no convertidas en P80 · escalamiento KAM directo, mayor palanca disponible esta semana.'},
        {'numero': es_pct(by_dest.iloc[0]["pctND"]*100,2),
         'titulo': f'{by_dest.iloc[0]["Destino"]} · destino crítico',
         'desc': f'{fmt_big(by_dest.iloc[0]["DNC"])} búsquedas no convertidas · concentra fugas de high-traffic markets.'},
        {'numero': '$' + es_num2(cu['rpm']),
         'titulo': 'CUG · mayor deterioro de IPM',
         'desc': f'WoW {es_pct1(cug_rpm_wow)} · canasta con weight 0,6 que requiere atención prioritaria pese a mejorar %NoDispo a {es_pct(cu["pct_nodispo"]*100,2)}.'},
        {'numero': es_pct(co['pct_nodispo']*100,2),
         'titulo': 'B2B-OP · canasta más sólida en %NoDispo',
         'desc': f'banda {co["banda_nodispo"]} en %NoDispo y IPM ${es_num2(co["rpm"])} (banda {co["banda_rpm"]}) · refleja la calidad del producto opaco premium frente a B2C.'},
        {'numero': fmt_big(h0["Trafico"]),
         'titulo': f'{truncate(clean_hotel_name(h0["Hotel"]),32)} · #1 Sin Conv',
         'desc': f'tráfico sin convertir · {h0["CorpName"]} · primera fila para revisión técnica esta semana.'},
    ]
    return findings

def render_resumen_ej():
    """Resumen Ejecutivo · estructura template literal."""
    from template_resumen import render_resumen_ejecutivo
    findings = build_findings()
    return render_resumen_ejecutivo(findings, accent_color='#EA0074', scope='global')

# ============ SECCIÓN SEVERITY %NoDispo ============
def render_severity_nodispo():
    levels = [
        ('Súper Crítica','&gt; 60%','#161616'),
        ('Crítica','20–60%','#C0392B'),
        ('Revisar','5–20%','#D4A878'),
        ('Aceptable','3–5%','#5C469C'),
        ('Exitosa','&lt; 3%','#4FC3F4'),
    ]
    total = int(sev_nd.sum())
    rows = ''
    for name, rng, color in levels:
        n = int(sev_nd[name])
        pct = n/total*100 if total else 0
        bar_w = max(min(pct, 100), 0.5)
        rows += (f'<div style="display:grid;grid-template-columns:110px 70px 1fr 65px 50px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule-soft);">'
                 f'<span style="display:inline-block;padding:3px 8px;background:{("rgba(22,22,22,.80)" if name=="Súper Crítica" else BANDA_COLORS[name]["bg"])};color:{("#FFFFFF" if name=="Súper Crítica" else BANDA_COLORS[name]["fg"])};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                 f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                 f'<div style="height:12px;background:var(--paper-soft);position:relative;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{color};"></div></div>'
                 f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                 f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                 f'</div>')
    
    n_critmas = int(sev_nd['Crítica'] + sev_nd['Súper Crítica'])
    n_supc = int(sev_nd['Súper Crítica'])
    n_exito = int(sev_nd['Exitosa'])
    
    return f'''<section id="severity-nodispo">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">Severity · % NoDispo</h2>
<span class="section-subtitle" style="color:#EA0074">P80 · {fmt_int_es(total)} hoteles</span>
<p class="section-kicker">Distribución de hoteles del Top tráfico (P80) por nivel de %NoDispo. El target es &lt;3% (banda Exitosa).</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>{rows}</div>
<div class="pull-note" style="margin-top:0;"><strong>Interpretación.</strong> {fmt_int_es(n_exito)} hoteles ({n_exito/total*100:.1f}%) están en zona Exitosa. <strong>{fmt_int_es(n_critmas)} hoteles ({n_critmas/total*100:.2f}%)</strong> en Severity Crítica+ requieren escalamiento: {n_supc} Súper Críticos son los más urgentes.</div>
</div>
</section>
'''.replace('.','.',2)

# ============ SECCIÓN SEVERITY · NoDispo + IPM combinada en 2 cols ============
def render_severities_combinadas():
    """Severity %NoDispo + IPM lado a lado · una sola sección."""
    
    def render_table(sev_dict, levels_data, accent='#EA0074', fmt_label='pct'):
        total = int(sev_dict.sum()) if hasattr(sev_dict, "sum") else int(sum(sev_dict.values()))
        rows = ''
        for name, rng, color in levels_data:
            n = int(sev_dict.get(name, 0))
            pct = n/total*100 if total else 0
            bar_w = max(min(pct, 100), 0.5)
            rows += (f'<div style="display:grid;grid-template-columns:120px 80px 1fr 60px 45px;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
                     f'<span style="display:inline-block;padding:3px 8px;background:{BANDA_COLORS[name]["bg"]};color:{BANDA_COLORS[name]["fg"]};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                     f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                     f'<div style="height:11px;background:var(--paper-soft);position:relative;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{color};"></div></div>'
                     f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                     f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                     f'</div>')
        return rows, total
    
    levels_nd = [
        ('Súper Crítica','&gt; 60%','#161616'),
        ('Crítica','20–60%','#C0392B'),
        ('Revisar','5–20%','#D4A878'),
        ('Aceptable','3–5%','#5C469C'),
        ('Exitosa','&lt; 3%','#4FC3F4'),
    ]
    levels_ipm = [
        ('Sin Conversión','BKGS=0','#8A8377'),
        ('Crítica','&lt; $200','#C0392B'),
        ('Revisar','$200–$650','#D4A878'),
        ('Aceptable','$650–$1500','#5C469C'),
        ('Exitosa','≥ $1500','#4FC3F4'),
    ]
    
    rows_nd, total_nd = render_table(sev_nd, levels_nd)
    rows_ipm, total_ipm = render_table(sev_rpm, levels_ipm)
    
    n_critmas = int(sev_nd['Crítica'] + sev_nd['Súper Crítica'])
    n_sc = int(sev_rpm['Sin Conversión'])
    n_crit_ipm = int(sev_rpm['Crítica'])
    n_proc = total_ipm - n_sc
    
    return f'''<section id="severity-combinada">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">Severidad · % NoDispo y IPM</h2>
<span class="section-subtitle" style="color:#EA0074">P80 · {fmt_int_es(total_nd)} hoteles</span>
<p class="section-kicker">Distribución de hoteles del Top tráfico (P80) por nivel de %NoDispo (target &lt;3%) e IPM (Income Per Million USD · target ≥ $650). Sin Conversión es cohorte aparte (BKGS=0); Severity IPM se aplica solo a procesables.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">% No Disponibilidad</h3>
{rows_nd}
</div>
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">IPM (USD)</h3>
{rows_ipm}
</div>
</div>
<div class="pull-note" style="margin-top:18px;"><strong>Interpretación.</strong> En %NoDispo, {fmt_int_es(n_critmas)} hoteles ({n_critmas/total_nd*100:.2f}%) en Severity Crítica+ requieren escalamiento. En IPM, <strong>{fmt_int_es(n_sc)} hoteles ({n_sc/total_ipm*100:.1f}%) sin conversión</strong> son cohorte estructural; de los {fmt_int_es(n_proc)} procesables, {fmt_int_es(n_crit_ipm)} están en Crítica (&lt; $200) — primera fila de escalamiento.</div>
</section>
'''

# ============ SECCIÓN TOP 5 (Demanda No Convertida, Bajo Rendimiento, Sin Conversión, Por Corp/Dest/Pais) ============
def render_top_table(title, num, df, cols_def, accent_color='#EA0074', subtitle='', kicker=''):
    """
    cols_def: list of dicts {key, label, fmt, width, align}
    """
    # Header
    header = '<div style="display:grid;grid-template-columns:'
    grid = ''
    for c in cols_def:
        grid += c['width'] + ' '
    grid = grid.strip()
    header = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {accent_color};margin-bottom:4px;">'
    for c in cols_def:
        h_align = c.get('align','right')
        color = accent_color if c.get('key')=='hotel' or c.get('key')=='label' else 'var(--ink-muted)'
        header += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{h_align};">{c["label"]}</span>'
    header += '</div>'
    
    rows = header
    for i, r in df.iterrows():
        row_cells = ''
        for c in cols_def:
            align = c.get('align','right')
            val = c['fmt'](r) if callable(c['fmt']) else c['fmt']
            color = accent_color if c.get('key') in ('hotel','label') else 'var(--ink)'
            if c.get('key') == 'hotel':
                # 1. Hotel name + corp
                hotel_name = truncate(r.get('Hotel') or r.get('Destino') or r.get('CorpName') or r.get('PaisDestino') or '-', 36)
                sub = r.get('CorpName','')
                row_cells += (f'<div><div style="font-weight:600;color:{accent_color};line-height:1.3;" title="{r.get("Hotel","")}">{i+1}. {hotel_name}</div>'
                              f'<div style="font-size:10px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.06em;margin-top:1px;">{sub}</div></div>')
            else:
                row_cells += f'<span style="text-align:{align};color:{color};font-weight:600;font-variant-numeric:tabular-nums;">{val}</span>'
        rows += f'<div style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;">{row_cells}</div>'
    return rows

def render_demanda_nc():
    df1 = TOP['demanda_nc']
    df2 = TOP['demanda_nc_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dnc','label':'Pérdidas','width':'80px','fmt':lambda r:fmt_big(r['DemandaNoConvertida'])},
    ]
    col1 = render_top_table('','',df1,cols)
    # ajustar índices del df2
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table('','',df2_renum,cols)
    
    return f'''<section id="demanda-nc" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">Demanda no convertida</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · ordenado por búsquedas perdidas ↓</span>
<p class="section-kicker">Hoteles con mayor volumen absoluto de búsquedas que se perdieron por NoDispo. Combina tráfico × %NoDispo. Top 1: <strong>{truncate(df1.iloc[0]["Hotel"],38)}</strong> ({fmt_big(df1.iloc[0]["DemandaNoConvertida"])} búsquedas perdidas).</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Demanda No Convertida</strong> está en la pestaña <em>«Demanda No Convertida»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bajo_rend():
    df1 = TOP['bajo_rend']
    df2 = TOP['bajo_rend_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'bk','label':'BKGS','width':'55px','fmt':lambda r:fmt_int_es(r['Bookings'])},
        {'key':'rpm','label':'IPM','width':'70px','fmt':lambda r:fmt_num2(r['RPM'])},
    ]
    col1 = render_top_table('','',df1,cols)
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table('','',df2_renum,cols)
    
    return f'''<section id="bajo-rendimiento" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 05</div>
<h2 class="section-title">Bajo rendimiento</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · alto tráfico · IPM Crítica/Revisar · ordenado por tráfico ↓</span>
<p class="section-kicker">Hoteles del P80 con bookings &gt; 0 pero IPM en banda Crítica/Revisar — están convirtiendo, pero el income por millón de búsquedas no llega al target ≥ $650.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Bajo Rendimiento</strong> está en la pestaña <em>«Bajo Rendimiento»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_no_convierten():
    df1 = TOP['sin_conv']
    df2 = TOP['sin_conv_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dest','label':'Destino','width':'120px','fmt':lambda r:truncate(r['Destino'],18)},
    ]
    col1 = render_top_table('','',df1,cols)
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table('','',df2_renum,cols) if len(df2)>0 else ''
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    
    body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
            if col2 else f'<div>{col1}</div>')
    
    return f'''<section id="sin-conversion" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 06</div>
<h2 class="section-title">Sin conversión</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · alto tráfico · 0 BKGS · ordenado por tráfico ↓</span>
<p class="section-kicker">{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings. Cohorte estructural: requiere diagnóstico técnico (errores de carga, mapping) o contractual (paridad, tarifas). No incluye en Severity de Conv Rate.</p>
</div>
</div>
{body}
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Sin Conversión</strong> está en la pestaña <em>«Sin Conversión»</em> del Excel adjunto · separada de Bajo Rendimiento.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def _render_dim_table_rnd(df, dim_col, dim_label, start_idx=0):
    """Tabla de una columna con N filas para Top dimensión RND."""
    grid = '1fr 90px 70px 75px 70px'
    rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid #EA0074;margin-bottom:4px;">'
    for label in [dim_label,'Tráfico','BKGS','%NoDispo','IPM']:
        align = 'left' if label==dim_label else 'right'
        color = '#EA0074' if label==dim_label else 'var(--ink-muted)'
        rows += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{align};">{label}</span>'
    rows += '</div>'
    
    for i, r in df.iterrows():
        bnd = r.get('BandaNoDispo','')
        bnd_color = BANDA_COLORS.get(bnd,{}).get('fg','#EA0074')
        bnd_bg = BANDA_COLORS.get(bnd,{}).get('bg','#FCE4F1') if bnd!='Súper Crítica' else 'rgba(22,22,22,.80)'
        bnd_fg = '#FFFFFF' if bnd=='Súper Crítica' else bnd_color
        pill = (f'<span style="display:inline-block;font-size:8px;font-weight:700;padding:2px 6px;border-radius:2px;'
                f'background:{bnd_bg};color:{bnd_fg};text-transform:uppercase;letter-spacing:.05em;margin-left:6px;">{bnd}</span>')
        n = start_idx + i + 1
        cells = (f'<div><div style="font-weight:600;color:#EA0074;line-height:1.3;">{n}. {truncate(r[dim_col],28)}{pill}</div></div>'
                 f'<span style="text-align:right;color:#EA0074;font-weight:600;font-variant-numeric:tabular-nums;">{fmt_big(r["Trafico"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                 f'<span style="text-align:right;color:#EA0074;font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["%NoDispo"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_num2(r["RPM"])}</span>')
        rows += f'<div style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;">{cells}</div>'
    return rows

def render_top_dimension(num, title, df_full, dim_col, dim_label, kicker, key='hotel'):
    """Top 10 a 2 columnas (5+5) por destino/corp/país RND."""
    df_top10 = df_full.head(10).reset_index(drop=True)
    df1 = df_top10.iloc[:5].reset_index(drop=True)
    df2 = df_top10.iloc[5:10].reset_index(drop=True)
    
    col1 = _render_dim_table_rnd(df1, dim_col, dim_label, start_idx=0)
    col2 = _render_dim_table_rnd(df2, dim_col, dim_label, start_idx=5) if len(df2) > 0 else ''
    
    body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
            if col2 else f'<div>{col1}</div>')
    
    return f'''<section id="top-{key}" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección {num}</div>
<h2 class="section-title">{title}</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · ordenado por tráfico ↓</span>
<p class="section-kicker">{kicker}</p>
</div>
</div>
{body}
</section>
'''

# ============ SECCIÓN PLAN DE ACCIÓN ============
def render_plan_accion():
    # Datos de los top problemas
    h_sc = TOP['sin_conv'].iloc[0]
    h_dnc = TOP['demanda_nc'].iloc[0]
    h_br = TOP['bajo_rend'].iloc[0]
    
    n_sc = (p80_hotel['Bookings']==0).sum()
    n_critmas = sev_nd['Crítica'] + sev_nd['Súper Crítica']
    
    # Badge superior = ÁREA OWNER · cluster (QW/MP/ES) va abajo (Fix #8)
    cug_rpm_wow = (M["CUG (UOP)_w18"]["rpm"]/M["CUG (UOP)_w17"]["rpm"]-1)*100
    
    def action(owner, cluster, code, plazo, accion, metrica):
        cluster_class = {'Quick Win':'qw','Mid Priority':'mp','Estratégica':'es'}.get(cluster,'qw')
        return f'''<div class="action-row {cluster_class}">
<div class="action-owner-badge">{owner}</div>
<div class="accion">{accion}</div>
<div class="action-meta-bottom">
<span class="cluster-tag">{cluster} · {code}</span>
<span class="meta-item"><strong>Plazo</strong> {plazo}</span>
<span class="meta-item"><strong>Métrica</strong> {metrica}</span>
</div>
</div>'''
    
    rows = ''
    rows += action('Supply Comercial / Supply Optimization', 'Quick Win', 'QW1', '5 días',
                   f'Escalar los <strong>{int(sev_nd["Súper Crítica"])} hoteles Súper Críticos</strong> del P80 (%NoDispo &gt;60%) · empezar por <strong>{truncate(clean_hotel_name(h_dnc["Hotel"]),38)}</strong> y similares.',
                   '%NoDispo &lt; 20%')
    rows += action('Supply Optimization / TPS', 'Quick Win', 'QW2', '1 semana',
                   f'Diagnóstico técnico Top 10 <strong>Sin Conversión</strong> de alto tráfico · revisar mapping, paridad, tarifas. Empezar por <strong>{truncate(clean_hotel_name(h_sc["Hotel"]),38)}</strong> ({fmt_big(h_sc["Trafico"])} búsquedas).',
                   'Conv Rate &gt; 0')
    rows += action('Supply Optimization', 'Mid Priority', 'MP1', '3 semanas',
                   f'Plan de saneamiento para <strong>{fmt_int_es(n_critmas)} hoteles Crítica/Súper Crítica</strong> de %NoDispo · separar por canasta y trabajar primero CUG y B2B-OP (weight 0,6).',
                   f'{int(n_critmas*0.5)} migrados a Revisar')
    rows += action('Supply Comercial / Wholesale', 'Mid Priority', 'MP2', '2 semanas',
                   f'Revisión de IPM en <strong>CUG</strong> ({fmt_num2(M["CUG (UOP)_w18"]["rpm"])}, {cug_rpm_wow:+.1f}% WoW) · canasta de mayor weight con deterioro pronunciado en GB.'.replace('+,','+').replace('.', ',', 1),
                   'IPM &gt; 600')
    rows += action('Supply Comercial / Supply Optimization', 'Estratégica', 'ES1', 'Q3',
                   f'Reducir <strong>cohorte Sin Conversión</strong> en P80 ({fmt_int_es(n_sc)} hoteles, {n_sc/len(p80_hotel)*100:.0f}% del P80) · proyecto trimestral de remediación técnica + comercial.',
                   '-30% vs baseline')
    rows += action('Supply Comercial / Wholesale', 'Estratégica', 'ES2', 'Q3',
                   'Definir <strong>SLAs de %NoDispo por corporativo</strong> para Top 10 corp por tráfico · contratos con cláusulas de severity-based pricing.',
                   'SLAs firmados')
    
    return f'''<section id="plan-accion">
<div class="section-head">
<div>
<div class="section-num">Sección 10</div>
<h2 class="section-title">Plan de acción</h2>
<span class="section-subtitle" style="color:#EA0074">Acciones priorizadas · agrupadas por Área Accountable</span>
<p class="section-kicker">El badge superior identifica al Área Accountable de cada acción. La etiqueta de horizonte (Quick Win · Mid Priority · Estratégica) y el código de seguimiento van debajo.</p>
</div>
</div>
<div class="action-grid">{rows}</div>
</section>
'''

# ============ NUEVO · BLOQUES CON TABS (post Week 18 mejora) ============
def _render_panel_top_table(df, cols, idx_offset=0):
    """Renderiza una tabla Top 5 a 2 cols dentro de un panel de tab."""
    df1 = df.iloc[:5].reset_index(drop=True)
    df2 = df.iloc[5:10].reset_index(drop=True) if len(df)>5 else None
    col1 = render_top_table('','',df1,cols)
    if df2 is not None and len(df2)>0:
        df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
        col2 = render_top_table('','',df2_renum,cols)
        return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
    return f'<div>{col1}</div>'

def render_bloque_hoteles():
    """Sección 03 · 3 tabs: Demanda NC · Bajo Rend · Sin Conv."""
    # Demanda NC
    cols_dnc = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dnc','label':'Pérdidas','width':'80px','fmt':lambda r:fmt_big(r['DemandaNoConvertida'])},
    ]
    df_dnc = pd.concat([TOP['demanda_nc'], TOP['demanda_nc_extra']], ignore_index=True)
    df_dnc.index = range(len(df_dnc))
    panel_dnc = _render_panel_top_table(df_dnc, cols_dnc)
    top1_dnc = df_dnc.iloc[0]
    kicker_dnc = f'Hoteles con mayor volumen absoluto de búsquedas que se perdieron por NoDispo. Combina tráfico × %NoDispo. Top 1: <strong>{truncate(top1_dnc["Hotel"],38)}</strong> ({fmt_big(top1_dnc["DemandaNoConvertida"])} búsquedas perdidas).'
    
    # Bajo Rendimiento
    cols_br = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'bk','label':'BKGS','width':'55px','fmt':lambda r:fmt_int_es(r['Bookings'])},
        {'key':'rpm','label':'IPM','width':'70px','fmt':lambda r:fmt_num2(r['RPM'])},
    ]
    df_br = pd.concat([TOP['bajo_rend'], TOP['bajo_rend_extra']], ignore_index=True)
    df_br.index = range(len(df_br))
    panel_br = _render_panel_top_table(df_br, cols_br)
    kicker_br = 'Hoteles del P80 con bookings &gt; 0 pero IPM en banda Crítica/Revisar — están convirtiendo, pero el income por millón de búsquedas no llega al target ≥ $650.'
    
    # Sin Conversión
    cols_sc = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'trafico','label':'Tráfico','width':'80px','fmt':lambda r:fmt_big(r['Trafico'])},
        {'key':'pctnd','label':'%NoDispo','width':'70px','fmt':lambda r:fmt_pct2(r['%NoDispo'])},
        {'key':'dest','label':'Destino','width':'120px','fmt':lambda r:truncate(r.get('Destino',''),18)},
    ]
    df_sc = pd.concat([TOP['sin_conv'], TOP['sin_conv_extra']], ignore_index=True)
    df_sc.index = range(len(df_sc))
    panel_sc = _render_panel_top_table(df_sc, cols_sc)
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    kicker_sc = f'{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings. Cohorte estructural: requiere diagnóstico técnico (errores de carga, mapping) o contractual (paridad, tarifas). No incluye en Severity de IPM.'
    
    panels = (
        f'<div class="tab-panel" data-tab="dnc"><p class="tab-kicker">{kicker_dnc}</p>{panel_dnc}</div>'
        f'<div class="tab-panel" data-tab="br"><p class="tab-kicker">{kicker_br}</p>{panel_br}</div>'
        f'<div class="tab-panel" data-tab="sc"><p class="tab-kicker">{kicker_sc}</p>{panel_sc}</div>'
    )
    
    return f'''<section id="por-hotel" style="margin-bottom:64px;">
<div class="section-head">
<div>
<div class="section-num">Sección 03</div>
<h2 class="section-title">Análisis por hotel</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 · 3 ópticas analíticas</span>
<p class="section-kicker">Hoteles del P80 vistos desde tres ángulos: demanda no convertida, bajo rendimiento de IPM, y sin conversión. Cada óptica responde a un tipo distinto de fuga de revenue.</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-h-dnc" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-br" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-sc" name="tabs-h" style="display:none" type="radio"/>
<div class="tabs-row">
<label class="tab-label" for="tab-h-dnc">Demanda NC</label>
<label class="tab-label" for="tab-h-br">Bajo Rendimiento</label>
<label class="tab-label" for="tab-h-sc">Sin Conversión</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
<div class="detail-callout" style="margin-top:18px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de cada óptica (Demanda NC · Bajo Rendimiento · Sin Conversión) está en pestañas separadas del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Rates_NoDispo_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bloque_dimensiones():
    """Sección 04 · 3 tabs: Corporativo · Destino · País."""
    
    def panel_for_dim(df_full, dim_col, dim_label):
        df_top10 = df_full.head(10).reset_index(drop=True)
        df1 = df_top10.iloc[:5].reset_index(drop=True)
        df2 = df_top10.iloc[5:10].reset_index(drop=True)
        col1 = _render_dim_table_rnd(df1, dim_col, dim_label, start_idx=0)
        col2 = _render_dim_table_rnd(df2, dim_col, dim_label, start_idx=5) if len(df2)>0 else ''
        if col2:
            return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
        return f'<div>{col1}</div>'
    
    panel_corp = panel_for_dim(TOP['corps_10'], 'CorpName', 'Corporativo')
    panel_dest = panel_for_dim(TOP['destinos_10'], 'Destino', 'Destino')
    panel_pais = panel_for_dim(TOP['paises_10'], 'PaisDestino', 'País')
    
    # Kickers
    top_corp = TOP['corps'].iloc[0]
    top_dest = TOP['destinos'].iloc[0]
    top_pais = TOP['paises'].iloc[0]
    k_corp = f'Distribución por corporativo. <strong>{top_corp["CorpName"]}</strong> lidera tráfico ({fmt_big(top_corp["Trafico"])}) con %NoDispo {fmt_pct2(top_corp["%NoDispo"])} y IPM ${fmt_num2(top_corp["RPM"])}.'
    k_dest = f'Distribución por destino. <strong>{top_dest["Destino"]}</strong> concentra {fmt_big(top_dest["Trafico"])} en búsquedas con %NoDispo {fmt_pct2(top_dest["%NoDispo"])} (banda {top_dest["BandaNoDispo"]}).'
    k_pais = f'Distribución por país. <strong>{top_pais["PaisDestino"]}</strong> concentra {fmt_big(top_pais["Trafico"])} de búsquedas con %NoDispo {fmt_pct2(top_pais["%NoDispo"])}.'
    
    panels = (
        f'<div class="tab-panel" data-tab="corp"><p class="tab-kicker">{k_corp}</p>{panel_corp}</div>'
        f'<div class="tab-panel" data-tab="dest"><p class="tab-kicker">{k_dest}</p>{panel_dest}</div>'
        f'<div class="tab-panel" data-tab="pais"><p class="tab-kicker">{k_pais}</p>{panel_pais}</div>'
    )
    
    return f'''<section id="por-dimension" style="margin-bottom:64px;">
<div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">Por dimensión</h2>
<span class="section-subtitle" style="color:#EA0074">Top 10 agregados · ordenado por tráfico ↓</span>
<p class="section-kicker">Distribución del tráfico P80 por corporativo, destino y país. Identifica concentraciones de demanda y patrones por dimensión geográfica.</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-d-corp" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-dest" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-pais" name="tabs-d" style="display:none" type="radio"/>
<div class="tabs-row">
<label class="tab-label" for="tab-d-corp">Corporativo</label>
<label class="tab-label" for="tab-d-dest">Destino</label>
<label class="tab-label" for="tab-d-pais">País</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
</section>
'''

# Render parte 2 completa
RESUMEN = render_resumen_ej()
SEV_COMBINADA = render_severities_combinadas()

# === NUEVO · 2 bloques con tabs (reemplazan 6 secciones apiladas) ===
BLOQUE_HOTELES = render_bloque_hoteles()
BLOQUE_DIM = render_bloque_dimensiones()

PLAN_ACCION = render_plan_accion()

PART2 = RESUMEN + SEV_COMBINADA + BLOQUE_HOTELES + BLOQUE_DIM + PLAN_ACCION

with open('part2_rnd.html','w') as f:
    f.write(PART2)
print(f"Part 2 RND escrito: {len(PART2):,} chars")
