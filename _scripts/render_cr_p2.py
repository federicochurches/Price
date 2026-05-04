"""
Renderer CR W18 parte 2: Resumen Ejecutivo, Severity Eficacia/CR, Top 5
"""
import pickle, pandas as pd, numpy as np
from engine import *
from render_helpers import *

with open('cr_w18_data.pkl','rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']
TAB_EF = D['TAB_EF']; TAB_CV = D['TAB_CV']
CANASTA = D['CANASTA']
sev_ef_p80 = D['sev_ef_p80']; sev_cv_p80 = D['sev_cv_p80']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']
g_corp = D['g_corp']; g_channel = D['g_channel']; g_grupo = D['g_grupo']

CR_ACCENT = '#5C469C'

# ============ RESUMEN EJECUTIVO · 10 findings ============
def build_findings():
    """Genera 10 findings con estructura template: numero + titulo + desc."""
    ef = M['global_w18']['eficacia']; ef17 = M['global_w17']['eficacia']
    cv = M['global_w18']['conv_rate']; cv17 = M['global_w17']['conv_rate']
    cr18 = M['global_w18']['cr_unicos']; cr17 = M['global_w17']['cr_unicos']
    bk18 = M['global_w18']['bookings']; bk17 = M['global_w17']['bookings']
    
    ef_wow = (ef - ef17) * 100
    cv_wow = (cv - cv17) * 100
    cr_wow = (cr18/cr17 - 1) * 100 if cr17 else 0
    bk_wow = (bk18/bk17 - 1) * 100 if bk17 else 0
    
    n_p80 = len(p80_hotel)
    n_supcrit_ef = sev_ef_p80.get('Súper Crítica', 0)
    n_crit_ef = sev_ef_p80.get('Crítica', 0)
    n_critmas_ef = n_supcrit_ef + n_crit_ef
    
    n_sin_conv = sev_cv_p80.get('Sin Conversión', 0)
    n_crit_cv = sev_cv_p80.get('Crítica', 0)
    pct_sin_conv = n_sin_conv/n_p80*100
    
    cb = M['B2C_w18']; co = M['B2B (OP)_w18']; cu = M['CUG (UOP)_w18']
    
    g_pp = g_grupo[g_grupo['Grupo']=='Producto Propio'].iloc[0]
    g_tp = g_grupo[g_grupo['Grupo']=='Third Party'].iloc[0]
    
    top1_corp = TOP['corps_10'].iloc[0]
    h0 = TOP['criticos'].iloc[0]
    h_sc0 = TOP['sin_conv'].iloc[0]
    
    def es_pct(v, dec=2):
        return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}pp'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    
    findings = [
        {'numero': es_pct(ef*100,2),
         'titulo': 'Eficacia global · banda Aceptable',
         'desc': f'WoW {es_pp(ef_wow)} · sigue por debajo del target ≥97%, primera prioridad en remediación técnica.'},
        {'numero': es_pct(cv*100,2),
         'titulo': 'Conv Rate cae a banda Revisar',
         'desc': f'WoW {es_pp(cv_wow)} · deterioro neto pese al crecimiento del volumen CR ({es_pct1(cr_wow)}) — más demanda no se traduce en bookings ({es_pct1(bk_wow)}).'},
        {'numero': fmt_int_es(n_critmas_ef),
         'titulo': 'Hoteles P80 Severity Eficacia Crítica+',
         'desc': f'{es_pct(n_critmas_ef/n_p80*100,1)} del P80 · de ellos {n_supcrit_ef} Súper Críticos son los casos más urgentes para escalamiento técnico.'},
        {'numero': fmt_int_es(n_sin_conv),
         'titulo': 'Hoteles P80 Sin Conversión (BKGS=0)',
         'desc': f'{es_pct(pct_sin_conv,1)} del P80 · cohorte estructural separada de Severity ConvRate, con {fmt_int_es(n_crit_cv)} adicionales en Crítica (<0,8%).'},
        {'numero': es_pct(g_tp["ConvRate"]*100,2),
         'titulo': 'Channel Third Party · banda Crítica',
         'desc': f'frente a Producto Propio en {es_pct(g_pp["ConvRate"]*100,2)} · brecha sistémica que requiere auditoría comercial + técnica.'},
        {'numero': es_pct(h0["Eficacia"]*100,2),
         'titulo': f'{truncate(clean_hotel_name(h0["Hotel"]),32)} · peor Eficacia',
         'desc': f'Hotel #1 del ranking Críticos · {fmt_int_es(int(h0["CR_Unicos"]))} CR únicos · {h0["CorpName"]} · escalamiento técnico inmediato.'},
        {'numero': fmt_int_es(int(top1_corp["CR_Unicos"])),
         'titulo': f'{top1_corp["CorpName"]} · líder volumen CR',
         'desc': f'Eficacia {es_pct(top1_corp["Eficacia"]*100,2)} en banda {top1_corp["BandaEficacia"]} · su tamaño hace que cualquier mejora tenga impacto outsized.'},
        {'numero': es_pct(cu["conv_rate"]*100,2),
         'titulo': 'CUG · única canasta con Conv Rate Aceptable',
         'desc': f'B2C {es_pct(cb["conv_rate"]*100,2)} (Crítica) · B2B-OP {es_pct(co["conv_rate"]*100,2)} (Revisar) · canasta opaca premium opera mejor.'},
        {'numero': es_pct(cb["conv_rate"]*100,2),
         'titulo': 'B2C Conv Rate · banda Crítica',
         'desc': f'canasta minorista pierde ~4 de cada 5 oportunidades vs CUG ({es_pct(cu["conv_rate"]*100,2)}) · gap principal del producto público.'},
        {'numero': fmt_int_es(int(h_sc0["CR_Unicos"])),
         'titulo': f'{truncate(clean_hotel_name(h_sc0["Hotel"]),32)} · #1 Sin Conv',
         'desc': f'CR únicos sin convertir · {h_sc0["CorpName"]} · primer caso para revisión técnica esta semana (mapping/paridad/inventario).'},
    ]
    return findings

def render_resumen_ej():
    """Resumen Ejecutivo siguiendo estructura template:
    header overline + card border-top + grid 2 cols + findings con valor destacado."""
    from template_resumen import render_resumen_ejecutivo
    findings = build_findings()
    return render_resumen_ejecutivo(findings, accent_color=CR_ACCENT, scope='global')

# ============ SECCIÓN SEVERITY EFICACIA ============
def render_severity_eficacia():
    levels = [
        ('Súper Crítica','&lt; 60%','#161616'),
        ('Crítica','60–85%','#C0392B'),
        ('Revisar','85–93%','#D4A878'),
        ('Aceptable','93–97%','#5C469C'),
        ('Exitosa','≥ 97%','#4FC3F4'),
    ]
    total = int(sev_ef_p80.sum())
    rows = ''
    for name, rng, color in levels:
        n = int(sev_ef_p80.get(name, 0))
        pct = n/total*100 if total else 0
        bar_w = max(min(pct, 100), 0.5)
        bg = "rgba(22,22,22,.80)" if name=="Súper Crítica" else BANDA_COLORS[name]["bg"]
        fg = "#FFFFFF" if name=="Súper Crítica" else BANDA_COLORS[name]["fg"]
        rows += (f'<div style="display:grid;grid-template-columns:110px 70px 1fr 65px 50px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule-soft);">'
                 f'<span style="display:inline-block;padding:3px 8px;background:{bg};color:{fg};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                 f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                 f'<div style="height:12px;background:var(--paper-soft);position:relative;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{color};"></div></div>'
                 f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                 f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                 f'</div>')
    
    n_critmas = int(sev_ef_p80.get('Crítica',0) + sev_ef_p80.get('Súper Crítica',0))
    n_supc = int(sev_ef_p80.get('Súper Crítica',0))
    n_exito = int(sev_ef_p80.get('Exitosa',0))
    
    return f'''<section id="severity-eficacia">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">Severity · Eficacia</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">P80 · {fmt_int_es(total)} hoteles · target ≥ 97%</span>
<p class="section-kicker">Distribución de hoteles del Top volumen CR (P80) por banda de Eficacia (success/CR únicos).</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>{rows}</div>
<div class="pull-note" style="margin-top:0;"><strong>Interpretación.</strong> {fmt_int_es(n_exito)} hoteles ({n_exito/total*100:.1f}%) en zona Exitosa. <strong>{fmt_int_es(n_critmas)} hoteles ({n_critmas/total*100:.1f}%)</strong> en Crítica+ requieren escalamiento técnico: {n_supc} Súper Críticos son la primera prioridad.</div>
</div>
</section>
'''

# ============ SECCIÓN SEVERITY CONVRATE ============
def render_severity_convrate():
    levels = [
        ('Sin Conversión','BKGS=0','#161616'),
        ('Crítica','&lt; 0,8%','#C0392B'),
        ('Revisar','0,8–1,5%','#D4A878'),
        ('Aceptable','1,5–2,5%','#5C469C'),
        ('Exitosa','≥ 2,5%','#4FC3F4'),
    ]
    total = int(sev_cv_p80.sum())
    rows = ''
    for name, rng, color in levels:
        n = int(sev_cv_p80.get(name, 0))
        pct = n/total*100 if total else 0
        bar_w = max(min(pct, 100), 0.5)
        rows += (f'<div style="display:grid;grid-template-columns:130px 70px 1fr 65px 50px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule-soft);">'
                 f'<span style="display:inline-block;padding:3px 8px;background:{BANDA_COLORS[name]["bg"]};color:{BANDA_COLORS[name]["fg"]};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                 f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                 f'<div style="height:12px;background:var(--paper-soft);position:relative;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{color};"></div></div>'
                 f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                 f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                 f'</div>')
    
    n_sc = int(sev_cv_p80.get('Sin Conversión',0))
    n_crit = int(sev_cv_p80.get('Crítica',0))
    n_proc = total - n_sc
    
    return f'''<section id="severity-convrate">
<div class="section-head">
<div>
<div class="section-num">Sección 03</div>
<h2 class="section-title">Severity · ConvRate</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">P80 · {fmt_int_es(total)} hoteles · target ≥ 2,5%</span>
<p class="section-kicker">Distribución por ConvRate (Bookings/CR únicos). Sin Conversión es cohorte aparte (BKGS=0); Severity se aplica a hoteles procesables.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>{rows}</div>
<div class="pull-note" style="margin-top:0;"><strong>Interpretación.</strong> <strong>{fmt_int_es(n_sc)} hoteles ({n_sc/total*100:.1f}%) sin conversión</strong> (BKGS=0): cohorte estructural — diagnóstico técnico/contractual. De los {fmt_int_es(n_proc)} procesables, {fmt_int_es(n_crit)} en Crítica (&lt;0,8%) son la primera fila de escalamiento.</div>
</div>
</section>
'''

# ============ SECCIÓN TOP 5 helper ============
def render_top_table_cr(df, cols_def, accent_color=CR_ACCENT):
    grid = ' '.join(c['width'] for c in cols_def)
    header = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {accent_color};margin-bottom:4px;">'
    for c in cols_def:
        h_align = c.get('align','right')
        color = accent_color if c.get('key') in ('hotel','label') else 'var(--ink-muted)'
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
                hotel_name = truncate(clean_hotel_name(r.get('Hotel') or '-'), 36)
                sub = r.get('CorpName','')
                row_cells += (f'<div><div style="font-weight:600;color:{accent_color};line-height:1.3;" title="{r.get("Hotel","")}">{i+1}. {hotel_name}</div>'
                              f'<div style="font-size:10px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.06em;margin-top:1px;">{sub}</div></div>')
            else:
                row_cells += f'<span style="text-align:{align};color:{color};font-weight:600;font-variant-numeric:tabular-nums;">{val}</span>'
        rows += f'<div style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;">{row_cells}</div>'
    return rows

def render_criticos():
    df1 = TOP['criticos']
    df2 = TOP['criticos_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'CR únicos','width':'80px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'ef','label':'Eficacia','width':'70px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'cv','label':'ConvRate','width':'70px','fmt':lambda r:fmt_pct2(r['ConvRate'])},
    ]
    col1 = render_top_table_cr(df1, cols)
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table_cr(df2_renum, cols)
    
    return f'''<section id="hoteles-criticos" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">Hoteles críticos</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · peor Eficacia con BKGS&gt;0 · ordenado ↑</span>
<p class="section-kicker">Hoteles del P80 con mayor severidad por Eficacia. Combinan volumen CR alto con tasa de errores elevada — primer foco de remediación técnica.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Hoteles Críticos</strong> está en la pestaña <em>«Críticos»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_CheckRates_W18.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bajo_rendimiento():
    df1 = TOP['bajo_rend']
    df2 = TOP['bajo_rend_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'CR únicos','width':'80px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'ef','label':'Eficacia','width':'70px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'cv','label':'ConvRate','width':'70px','fmt':lambda r:fmt_pct2(r['ConvRate'])},
    ]
    col1 = render_top_table_cr(df1, cols)
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table_cr(df2_renum, cols)
    
    return f'''<section id="bajo-rendimiento" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 05</div>
<h2 class="section-title">Bajo rendimiento</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · alto volumen CR · ConvRate Crítica/Revisar · ordenado por CR ↓</span>
<p class="section-kicker">Hoteles con tráfico significativo pero ConvRate insuficiente. Convierten, pero por debajo del target ≥2,5% — oportunidad de tunning de pricing/disponibilidad.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Bajo Rendimiento</strong> está en la pestaña <em>«Bajo Rendimiento»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_CheckRates_W18.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_sin_conv():
    df1 = TOP['sin_conv']
    df2 = TOP['sin_conv_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'CR únicos','width':'80px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'ef','label':'Eficacia','width':'70px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'dest','label':'Destino','width':'120px','fmt':lambda r:truncate(r['Destino'],18)},
    ]
    col1 = render_top_table_cr(df1, cols)
    df2_renum = df2.copy(); df2_renum.index = range(5, 5+len(df2_renum))
    col2 = render_top_table_cr(df2_renum, cols) if len(df2)>0 else ''
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    
    body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
            if col2 else f'<div>{col1}</div>')
    
    return f'''<section id="sin-conversion" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 06</div>
<h2 class="section-title">Sin conversión</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · alto CR · 0 BKGS · ordenado por CR ↓</span>
<p class="section-kicker">{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings pese a tener volumen de check-rates. Diagnóstico técnico (errores de carga, mapping, inventario) o contractual. No entra en Severity de ConvRate.</p>
</div>
</div>
{body}
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 50 de <strong>Sin Conversión</strong> está en la pestaña <em>«Sin Conversión»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_CheckRates_W18.xlsx">Excel ↗</a>
</div>
</section>
'''

# ============ SECCIÓN POR DIMENSIÓN (Corp / Destino / Channel) ============
def _render_dim_table(df, dim_col, dim_label, start_idx=0):
    """Renderiza una tabla (1 columna) con N filas. start_idx para numerar continuo."""
    grid = '1fr 90px 70px 75px 70px'
    rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {CR_ACCENT};margin-bottom:4px;">'
    for label in [dim_label,'CR únicos','BKGS','Eficacia','ConvRate']:
        align = 'left' if label==dim_label else 'right'
        color = CR_ACCENT if label==dim_label else 'var(--ink-muted)'
        rows += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{align};">{label}</span>'
    rows += '</div>'
    
    for i, r in df.iterrows():
        bnd = r.get('BandaEficacia','')
        bnd_color = BANDA_COLORS.get(bnd,{}).get('fg', CR_ACCENT)
        bnd_bg = "rgba(22,22,22,.80)" if bnd=="Súper Crítica" else BANDA_COLORS.get(bnd,{}).get('bg','#E8F7FD')
        bnd_fg = "#FFFFFF" if bnd=="Súper Crítica" else bnd_color
        pill = (f'<span style="display:inline-block;font-size:8px;font-weight:700;padding:2px 6px;border-radius:2px;'
                f'background:{bnd_bg};color:{bnd_fg};text-transform:uppercase;letter-spacing:.05em;margin-left:6px;">{bnd}</span>')
        n = start_idx + i + 1
        cells = (f'<div><div style="font-weight:600;color:{CR_ACCENT};line-height:1.3;">{n}. {truncate(r[dim_col],28)}{pill}</div></div>'
                 f'<span style="text-align:right;color:{CR_ACCENT};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                 f'<span style="text-align:right;color:{CR_ACCENT};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["Eficacia"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["ConvRate"])}</span>')
        rows += f'<div style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;">{cells}</div>'
    return rows

def render_top_dimension(num, title, df_full, dim_col, dim_label, kicker, key='hotel'):
    """Top 10 a 2 columnas (5+5). df_full debe tener al menos 10 rows ideal."""
    df_top10 = df_full.head(10).reset_index(drop=True)
    df1 = df_top10.iloc[:5].reset_index(drop=True)
    df2 = df_top10.iloc[5:10].reset_index(drop=True)
    
    col1 = _render_dim_table(df1, dim_col, dim_label, start_idx=0)
    col2 = _render_dim_table(df2, dim_col, dim_label, start_idx=5) if len(df2) > 0 else ''
    
    body = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;"><div>{col1}</div><div>{col2}</div></div>'
            if col2 else f'<div>{col1}</div>')
    
    return f'''<section id="top-{key}" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección {num}</div>
<h2 class="section-title">{title}</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · ordenado por CR únicos ↓</span>
<p class="section-kicker">{kicker}</p>
</div>
</div>
{body}
</section>
'''

# Channel agrupado · sección destacada (decisión post Week 17)
def render_channel_agrupado():
    g = g_grupo
    g_pp = g[g['Grupo']=='Producto Propio'].iloc[0]
    g_tp = g[g['Grupo']=='Third Party'].iloc[0]
    
    def pill_banda(b):
        bg = "rgba(22,22,22,.80)" if b=="Súper Crítica" else BANDA_COLORS.get(b,{}).get('bg','#E8F7FD')
        fg = "#FFFFFF" if b=="Súper Crítica" else BANDA_COLORS.get(b,{}).get('fg', CR_ACCENT)
        return f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;border-radius:2px;background:{bg};color:{fg};text-transform:uppercase;letter-spacing:.05em;">{b}</span>'
    
    def grupo_card(g, color_b, icon):
        return (f'<div style="background:var(--paper);border-radius:4px;padding:18px;border-top:3px solid {color_b};">'
                f'<div style="font-size:11px;font-weight:700;color:{color_b};letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;">'
                f'<span>{icon}</span><span>{g["Grupo"]}</span></div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;font-variant-numeric:tabular-nums;">'
                f'<div><div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700;">CR únicos</div>'
                f'<div style="font-size:22px;font-weight:700;color:var(--ink);margin-top:2px;">{fmt_int_es(g["CR_Unicos"])}</div></div>'
                f'<div><div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Bookings</div>'
                f'<div style="font-size:22px;font-weight:700;color:var(--ink);margin-top:2px;">{fmt_int_es(g["Bookings"])}</div></div>'
                f'<div><div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700;">Eficacia</div>'
                f'<div style="font-size:22px;font-weight:700;color:{color_b};margin-top:2px;">{fmt_pct2(g["Eficacia"])}</div>'
                f'<div style="margin-top:4px;">{pill_banda(g["BandaEficacia"])}</div></div>'
                f'<div><div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.08em;font-weight:700;">ConvRate</div>'
                f'<div style="font-size:22px;font-weight:700;color:{color_b};margin-top:2px;">{fmt_pct2(g["ConvRate"])}</div>'
                f'<div style="margin-top:4px;">{pill_banda(g["BandaConvRate"])}</div></div>'
                f'</div></div>')
    
    cards = grupo_card(g_pp,'#5C469C','🏠') + grupo_card(g_tp,'#4FC3F4','🔌')
    
    cv_gap = (g_pp['ConvRate'] - g_tp['ConvRate'])*100
    cr_share_tp = g_tp['CR_Unicos']/(g_pp['CR_Unicos']+g_tp['CR_Unicos'])*100
    
    return f'''<section id="channel-agrupado" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 07</div>
<h2 class="section-title">Channel agrupado</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Producto Propio vs Third Party</span>
<p class="section-kicker">Vista consolidada por familia de canal según decisión post Week 17. Producto Propio: DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees. Third Party: Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px;">{cards}</div>
<div class="pull-note"><strong>Brecha sistémica.</strong> Third Party representa solo {cr_share_tp:.1f}% del volumen pero su ConvRate ({fmt_pct2(g_tp["ConvRate"])}) está {cv_gap:.2f}pp por debajo de Producto Propio ({fmt_pct2(g_pp["ConvRate"])}). El gap señala un problema de canal: pricing, competitividad o latencia técnica de los integradores externos. Acción sugerida: auditoría de paridad y tarifas en Expedia/HotelBeds, principales operadores Third Party.</div>
</section>
'''.replace(',1f', '.1f')

# ============ PLAN DE ACCIÓN ============
def render_plan_accion():
    h_crit = TOP['criticos'].iloc[0]
    h_sc = TOP['sin_conv'].iloc[0]
    h_top = TOP['corps_10'].iloc[0]
    
    n_supc = int(sev_ef_p80.get('Súper Crítica',0))
    n_critmas = int(sev_ef_p80.get('Crítica',0) + sev_ef_p80.get('Súper Crítica',0))
    n_sc_total = int(sev_cv_p80.get('Sin Conversión',0))
    
    g_tp = g_grupo[g_grupo['Grupo']=='Third Party'].iloc[0]
    
    return f'''<section id="plan-accion">
<div class="section-head">
<div>
<div class="section-num">Sección 11</div>
<h2 class="section-title">Plan de acción</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Acciones priorizadas · agrupadas por Área Accountable</span>
<p class="section-kicker">El badge superior identifica al Área Accountable de cada acción. La etiqueta de horizonte (Quick Win · Mid Priority · Estratégica) y el código de seguimiento van debajo.</p>
</div>
</div>
<div class="action-grid">
<div class="action-row qw">
<div class="action-owner-badge">Supply Optimization</div>
<div class="accion">Escalar los <strong>{n_supc} hoteles Súper Críticos</strong> de Eficacia (P80, &lt;60%) · empezar por <strong>{truncate(clean_hotel_name(h_crit["Hotel"]),38)}</strong> ({fmt_pct2(h_crit["Eficacia"])} Eficacia, {fmt_int_es(h_crit["CR_Unicos"])} CR).</div>
<div class="action-meta-bottom"><span class="cluster-tag">Quick Win · QW1</span><span class="meta-item"><strong>Plazo</strong> 5 días</span><span class="meta-item"><strong>Métrica</strong> Eficacia &gt; 85%</span></div>
</div>
<div class="action-row qw">
<div class="action-owner-badge">Supply Optimization / TPS</div>
<div class="accion">Diagnóstico técnico Top 10 <strong>Sin Conversión</strong> · revisar mapping, paridad, inventario. Empezar por <strong>{truncate(clean_hotel_name(h_sc["Hotel"]),38)}</strong> ({fmt_int_es(h_sc["CR_Unicos"])} CR sin BKGS).</div>
<div class="action-meta-bottom"><span class="cluster-tag">Quick Win · QW2</span><span class="meta-item"><strong>Plazo</strong> 1 semana</span><span class="meta-item"><strong>Métrica</strong> Bookings &gt; 0</span></div>
</div>
<div class="action-row mp">
<div class="action-owner-badge">Supply Optimization / TPS</div>
<div class="accion">Auditar canal <strong>Third Party</strong> ({fmt_pct2(g_tp["ConvRate"])} ConvRate Crítica) · revisar paridad de tarifas y velocidad de respuesta de Expedia y HotelBeds Apitude.</div>
<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority · MP1</span><span class="meta-item"><strong>Plazo</strong> 2 semanas</span><span class="meta-item"><strong>Métrica</strong> ConvRate &gt; 0,8%</span></div>
</div>
<div class="action-row mp">
<div class="action-owner-badge">Supply Optimization</div>
<div class="accion">Plan de saneamiento para <strong>{fmt_int_es(n_critmas)} hoteles Crítica/Súper Crítica</strong> de Eficacia · priorizar canasta CUG (mejor ConvRate) y B2B-OP (volumen).</div>
<div class="action-meta-bottom"><span class="cluster-tag">Mid Priority · MP2</span><span class="meta-item"><strong>Plazo</strong> 3 semanas</span><span class="meta-item"><strong>Métrica</strong> {int(n_critmas*0.5)} a Revisar</span></div>
</div>
<div class="action-row es">
<div class="action-owner-badge">Supply Comercial / Supply Optimization</div>
<div class="accion">Reducir <strong>cohorte Sin Conversión</strong> en P80 ({fmt_int_es(n_sc_total)} hoteles, {n_sc_total/len(p80_hotel)*100:.0f}%) · proyecto trimestral de remediación técnica + comercial.</div>
<div class="action-meta-bottom"><span class="cluster-tag">Estratégica · ES1</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> -25% vs baseline</span></div>
</div>
<div class="action-row es">
<div class="action-owner-badge">Supply Comercial / Wholesale</div>
<div class="accion">Revisión integral del producto <strong>B2C</strong> (ConvRate Crítica {fmt_pct2(M["B2C_w18"]["conv_rate"])}) · pricing, UX, mapping, fee structure.</div>
<div class="action-meta-bottom"><span class="cluster-tag">Estratégica · ES2</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> ConvRate &gt; 1,5%</span></div>
</div>
</div>
</section>
'''

# Render parte 2 completa
RESUMEN = render_resumen_ej()
SEV_EF = render_severity_eficacia()
SEV_CV = render_severity_convrate()
CRITICOS = render_criticos()
BAJO_REND = render_bajo_rendimiento()
SIN_CONV = render_sin_conv()

def kicker_corp_cr():
    top1 = TOP['corps_10'].iloc[0]
    return f'Top corporativos por volumen CR. <strong>{top1["CorpName"]}</strong> lidera con {fmt_int_es(top1["CR_Unicos"])} CR · Eficacia {fmt_pct2(top1["Eficacia"])} (banda {top1["BandaEficacia"]}) y ConvRate {fmt_pct2(top1["ConvRate"])} (banda {top1["BandaConvRate"]}).'

def kicker_dest_cr():
    top1 = TOP['destinos'].iloc[0]
    return f'Top destinos por volumen CR. <strong>{top1["Destino"]}</strong> con {fmt_int_es(top1["CR_Unicos"])} CR · Eficacia {fmt_pct2(top1["Eficacia"])} y ConvRate {fmt_pct2(top1["ConvRate"])}.'

def kicker_chan_cr():
    top1 = TOP['channels'].iloc[0]
    return f'Top channels por volumen CR. <strong>{top1["ExternalProviderName"]}</strong> concentra {fmt_int_es(top1["CR_Unicos"])} CR · Eficacia {fmt_pct2(top1["Eficacia"])} (banda {top1["BandaEficacia"]}).'

POR_CORP = render_top_dimension('08','Por corporativo', TOP['corps_10'], 'CorpName','Corporativo', kicker_corp_cr(), 'corp')
POR_DEST = render_top_dimension('09','Por destino', TOP['destinos'], 'Destino','Destino', kicker_dest_cr(), 'dest')

# === SECCIÓN POR CHANNEL · split Producto Propio + Third Party ===
def render_por_channel_split():
    """Sección Por Channel dividida en dos sub-tablas: Producto Propio y Third Party.
    Decisión post W17 · todos los channels mostrados (no Top 5/10), agrupados por familia.
    """
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    
    df_all = TOP['channels']
    df_pp = df_all[df_all['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_tp = df_all[df_all['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    
    # Color de cada split: PP = violet (color principal CR), TP = cyan (CUG / complementario)
    COLOR_PP = '#5C469C'
    COLOR_TP = '#4FC3F4'
    
    def render_split_table(df, dim_col, color_b):
        grid = '1fr 90px 70px 75px 70px'
        rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {color_b};margin-bottom:4px;">'
        for label in ['Channel','CR únicos','BKGS','Eficacia','ConvRate']:
            align = 'left' if label=='Channel' else 'right'
            color = color_b if label=='Channel' else 'var(--ink-muted)'
            rows += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{align};">{label}</span>'
        rows += '</div>'
        for i, r in df.iterrows():
            bnd = r.get('BandaEficacia','')
            bnd_color = BANDA_COLORS.get(bnd,{}).get('fg', color_b)
            bnd_bg = "rgba(22,22,22,.80)" if bnd=="Súper Crítica" else BANDA_COLORS.get(bnd,{}).get('bg','#E8F7FD')
            bnd_fg = "#FFFFFF" if bnd=="Súper Crítica" else bnd_color
            pill = (f'<span style="display:inline-block;font-size:8px;font-weight:700;padding:2px 6px;border-radius:2px;'
                    f'background:{bnd_bg};color:{bnd_fg};text-transform:uppercase;letter-spacing:.05em;margin-left:6px;">{bnd}</span>')
            cells = (f'<div><div style="font-weight:600;color:{color_b};line-height:1.3;">{i+1}. {truncate(r[dim_col],30)}{pill}</div></div>'
                     f'<span style="text-align:right;color:{color_b};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                     f'<span style="text-align:right;color:{color_b};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["Eficacia"])}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["ConvRate"])}</span>')
            rows += f'<div style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;">{cells}</div>'
        return rows
    
    tabla_pp = render_split_table(df_pp, 'ExternalProviderName', COLOR_PP)
    tabla_tp = render_split_table(df_tp, 'ExternalProviderName', COLOR_TP)
    
    top1_pp = df_pp.iloc[0] if len(df_pp)>0 else None
    top1_tp = df_tp.iloc[0] if len(df_tp)>0 else None
    
    kicker = f'Channels segregados por familia (decisión post Week 17). <strong style="color:{COLOR_PP};">Producto Propio</strong>: {len(df_pp)} channels · <strong style="color:{COLOR_TP};">Third Party</strong>: {len(df_tp)} channels.'
    
    return f'''<section id="top-channel" style="margin-bottom:80px;"><div class="section-head">
<div>
<div class="section-num">Sección 10</div>
<h2 class="section-title">Por channel</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Producto Propio · Third Party · ordenado por CR ↓</span>
<p class="section-kicker">{kicker}</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
<div>
<div style="font-size:11px;font-weight:700;color:{COLOR_PP};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;">🏠 Producto Propio</div>
{tabla_pp}
</div>
<div>
<div style="font-size:11px;font-weight:700;color:{COLOR_TP};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;">🔌 Third Party</div>
{tabla_tp}
</div>
</div>
</section>
'''

POR_CHAN = render_por_channel_split()

CHAN_AGR = render_channel_agrupado()
PLAN_ACCION = render_plan_accion()

PART2 = RESUMEN + SEV_EF + SEV_CV + CRITICOS + BAJO_REND + SIN_CONV + CHAN_AGR + POR_CORP + POR_DEST + POR_CHAN + PLAN_ACCION

with open('part2_cr.html','w') as f:
    f.write(PART2)
print(f"Part 2 CR escrito: {len(PART2):,} chars")
