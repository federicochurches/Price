"""
Renderer CR W20 parte 2: Resumen Ejecutivo, Severity Eficacia/CR, Top 5
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
import os, pandas as pd, numpy as np

from engine import *
from render_helpers import *
from template_seguimiento import render_seguimiento_block
from render_cr_p1 import render_alerts_block
from historico_module_v2 import render_historico_cr

with open(os.getenv('PICKLE_CR', 'cr_w20_data.pkl'),'rb') as f:
    D = pickle.load(f)
M = D['M']; TOP = D['TOP']


# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
TAB_EF = D['TAB_EF']; TAB_CV = D['TAB_CV']
CANASTA = D['CANASTA']
sev_ef_p80 = D['sev_ef_p80']; sev_cv_p80 = D['sev_cv_p80']
g_hotel = D['g_hotel']; p80_hotel = D['p80_hotel']
g_corp = D['g_corp']; g_channel = D['g_channel']; g_grupo = D['g_grupo']
g_corp_w17 = D.get('g_corp_w17', None)
g_dest_w17 = D.get('g_dest_w17', None)
g_hotel_w17 = D.get('g_hotel_w17', None)
g_channel_w17 = D.get('g_channel_w17', None)
hotel_channel_map = D.get('hotel_channel_map', {})

WEEK_NUM      = D.get('VOL_NUM', '19')
WEEK_PREV_NUM = str(int(WEEK_NUM) - 1)
SEGUIMIENTO_FILE = f'_seguimiento/plan_seguimiento_W{WEEK_PREV_NUM}.md'


# ── FIX: RENOMBRAR KEYS DINÁMICAMENTE ──────────────────────────────────────────
WEEK_NUM_INT = int(D.get('VOL_NUM', '19'))
WEEK_PREV_INT = WEEK_NUM_INT - 1
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', {})
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', {})
M['global_current'] = M['global_current']
M['global_w17'] = M['global_prev']
# ─────────────────────────────────────────────────────────────────────────────

# Enriquecer TOP hoteles con WoW Eficacia/ConvRate y Channel
def _enrich_hotel_df(df):
    out = df.copy()
    if g_hotel_w17 is not None and 'Hotel' in out.columns:
        out = out.merge(g_hotel_w17[['Hotel','Eficacia_W17','ConvRate_W17']], on='Hotel', how='left')
        out['Eficacia_WoW_pp'] = (out['Eficacia'] - out['Eficacia_W17']) * 100
        out['ConvRate_WoW_pp'] = (out['ConvRate'] - out['ConvRate_W17']) * 100 if 'ConvRate' in out.columns else None
    if hotel_channel_map:
        out['Channel'] = out['Hotel'].map(hotel_channel_map).fillna('N/D')
    return out

for _key in ['criticos','criticos_extra','bajo_rend','bajo_rend_extra','sin_conv','sin_conv_extra','menor_cv']:
    if _key in TOP:
        TOP[_key] = _enrich_hotel_df(TOP[_key])

CR_ACCENT = '#5C469C'

# ============ RESUMEN EJECUTIVO · 10 findings ============
def build_findings():
    """Genera 10 findings con estructura template: numero + titulo + desc."""
    ef = M['global_current']['eficacia']; ef17 = M['global_w17']['eficacia']
    cv = M['global_current']['conv_rate']; cv17 = M['global_w17']['conv_rate']
    cr18 = M['global_current']['cr_unicos']; cr17 = M['global_w17']['cr_unicos']
    bk18 = M['global_current']['bookings']; bk17 = M['global_w17']['bookings']
    
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
    
    cb = M[f'B2C_w{WEEK_NUM_INT}']; co = M[f'B2B (OP)_w{WEEK_NUM_INT}']; cu = M[f'CUG (UOP)_w{WEEK_NUM_INT}']
    
    g_pp = g_grupo[g_grupo['Grupo']=='Producto Propio'].iloc[0]
    g_tp = g_grupo[g_grupo['Grupo']=='Third Party'].iloc[0]
    
    top1_corp = TOP['corps_10'].iloc[0]
    h0 = TOP['criticos'].iloc[0]
    h_sc0 = TOP['sin_conv'].iloc[0]
    
    def es_pct(v, dec=2):
        return f'{v:.{dec}f}%'.replace('.',',')
    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}'.replace('.',',')
    def es_pct1(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.1f}%'.replace('.',',')
    
    findings = [
        {'numero': es_pct(ef*100,2),
         'titulo': 'Eficacia global · banda Aceptable',
         'desc': f'sigue por debajo del target ≥97%, primera prioridad en remediación técnica.'},
        {'numero': es_pct(cv*100,2),
         'titulo': 'Conv Rate cae a banda Revisar',
         'desc': f'deterioro neto pese al crecimiento del volumen CR ({es_pct1(cr_wow)}) — más demanda no se traduce en bookings ({es_pct1(bk_wow)}).'},
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

    ef = M['global_current']['eficacia']; ef17 = M['global_w17']['eficacia']
    cv = M['global_current']['conv_rate']; cv17 = M['global_w17']['conv_rate']
    ef_wow = (ef - ef17) * 100
    cv_wow = (cv - cv17) * 100
    banda_ef = banda_eficacia(ef)
    banda_cv = banda_convrate(cv, M['global_current']['bookings'])

    def pill_b(nombre):
        bc = BANDA_COLORS.get(nombre, BANDA_COLORS['Sin Conversión'])
        return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
                f'border-radius:2px;background:{bc["bg"]};color:{bc["fg"]};'
                f'text-transform:uppercase;letter-spacing:.05em;vertical-align:middle;margin:0 2px;">{nombre}</span>')

    def pill_d(texto, mejora):
        color = '#2F6C34' if mejora else '#C0392B'
        bg    = '#EAF3DE' if mejora else '#FCE8E6'
        return (f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;'
                f'border-radius:3px;background:{bg};color:{color};vertical-align:middle;margin:0 2px;">{texto}</span>')

    def es_pp(v):
        sign = '+' if v >= 0 else ''
        return f'{sign}{v:.2f}'.replace('.', ',')

    def es_pct(v, dec=2):
        return f'{v:.{dec}f}%'.replace('.', ',')

    wow_str_ef = es_pp(ef_wow)
    wow_str_cv = es_pp(cv_wow)

    findings = build_findings()

    # Variables necesarias para enriquecer findings con pills
    cb = M[f'B2C_w{WEEK_NUM_INT}']; co = M[f'B2B (OP)_w{WEEK_NUM_INT}']; cu = M[f'CUG (UOP)_w{WEEK_NUM_INT}']
    g_pp = g_grupo[g_grupo['Grupo']=='Producto Propio'].iloc[0]
    g_tp = g_grupo[g_grupo['Grupo']=='Third Party'].iloc[0]
    top1_corp = TOP['corps_10'].iloc[0]

    # Calcular bandas de todos los elementos con pills
    banda_tp_cv = banda_convrate(g_tp["ConvRate"], 1)
    banda_pp_cv = banda_convrate(g_pp["ConvRate"], 1)
    banda_top1_ef = top1_corp["BandaEficacia"]
    banda_cug_cv = banda_convrate(cu["conv_rate"], cu["bookings"])
    banda_b2c_cv = banda_convrate(cb["conv_rate"], cb["bookings"])
    banda_op_cv  = banda_convrate(co["conv_rate"], co["bookings"])

    # Enriquecer finding 0 (Eficacia) con pill banda + WoW
    f0 = findings[0]
    findings[0] = {**f0,
        'titulo': f'Eficacia global · {pill_b(banda_ef)}',
        'desc':   f'{pill_d(wow_str_ef, ef_wow > 0)} · {f0["desc"]}'
    }
    # Enriquecer finding 1 (Conv Rate) con pill banda + WoW
    f1 = findings[1]
    findings[1] = {**f1,
        'titulo': f'Conv Rate · {pill_b(banda_cv)}',
        'desc':   f'{pill_d(wow_str_cv, cv_wow > 0)} · {f1["desc"]}'
    }
    # Finding 2 (Severity Crítica+) — pill Crítica
    f2 = findings[2]
    findings[2] = {**f2,
        'titulo': f'Hoteles P80 Severity Eficacia · {pill_b("Crítica")}+',
    }
    # Finding 3 (Sin Conversión) — pill Sin Conversión
    f3 = findings[3]
    findings[3] = {**f3,
        'titulo': f'Hoteles P80 · {pill_b("Sin Conversión")} (BKGS=0)',
    }
    # Finding 4 (Third Party ConvRate) — pill banda TP
    f4 = findings[4]
    findings[4] = {**f4,
        'titulo': f'Channel Third Party · {pill_b(banda_tp_cv)}',
        'desc': f'frente a Producto Propio {es_pct(g_pp["ConvRate"]*100,2)} {pill_b(banda_pp_cv)} · brecha sistémica que requiere auditoría comercial + técnica.'
    }
    # Finding 6 (corp líder) — pill banda eficacia del corp
    f6 = findings[6]
    findings[6] = {**f6,
        'desc': f'Eficacia {es_pct(top1_corp["Eficacia"]*100,2)} {pill_b(banda_top1_ef)} · su tamaño hace que cualquier mejora tenga impacto outsized.'
    }
    # Finding 7 (CUG) — pill banda CUG
    f7 = findings[7]
    findings[7] = {**f7,
        'titulo': f'CUG · única canasta con Conv Rate · {pill_b(banda_cug_cv)}',
        'desc': f'B2C {es_pct(cb["conv_rate"]*100,2)} {pill_b(banda_b2c_cv)} · B2B-OP {es_pct(co["conv_rate"]*100,2)} {pill_b(banda_op_cv)} · canasta opaca premium opera mejor.'
    }
    # Finding 8 (B2C) — pill banda B2C
    f8 = findings[8]
    findings[8] = {**f8,
        'titulo': f'B2C Conv Rate · {pill_b(banda_b2c_cv)}',
    }

    return render_resumen_ejecutivo(findings, accent_color=CR_ACCENT, scope='global')

# ============ SECCIÓN SEVERITY EFICACIA ============
def render_severity_eficacia():
    levels = [
        ('Súper Crítica','&lt; 60%','#C0392B'),
        ('Crítica','60–85%','#C0392B'),
        ('Revisar','85–93%','#F97316'),
        ('Aceptable','93–97%','#FCD34D'),
        ('Exitosa','≥ 97%','#1A6B4A'),
    ]
    total = int(sev_ef_p80.sum())
    rows = ''
    for name, rng, bar_color in levels:
        n = int(sev_ef_p80.get(name, 0))
        pct = n/total*100 if total else 0
        bar_w = max(min(pct, 100), 0.5)
        # Badge paleta D: Súper Crítica fondo sólido oscuro, resto bg pastel + fg oscuro
        bc = BANDA_COLORS.get(name, BANDA_COLORS['Sin Conversión'])
        badge_bg = bc['bg']; badge_fg = bc['fg']
        rows += (f'<div style="display:grid;grid-template-columns:110px 70px 1fr 65px 50px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--rule-soft);">'
                 f'<span style="display:inline-block;padding:3px 8px;background:{badge_bg};color:{badge_fg};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                 f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                 f'<div style="height:8px;background:var(--paper-soft);position:relative;border-radius:2px;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{bar_color};border-radius:2px;"></div></div>'
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
<div>{rows}</div>
</section>
'''

# ============ SECCIÓN SEVERITY · Eficacia + ConvRate combinada en 2 cols ============
def render_severities_combinadas():
    """Severity Eficacia + ConvRate lado a lado · una sola sección."""
    
    def render_table(sev_dict, levels_data):
        total = int(sev_dict.sum()) if hasattr(sev_dict, "sum") else int(sum(sev_dict.values()))
        rows = ''
        for name, rng, _ in levels_data:
            n = int(sev_dict.get(name, 0))
            pct = n/total*100 if total else 0
            bar_w = max(min(pct, 100), 0.5)
            # Badge paleta D: BANDA_COLORS es la única fuente de verdad
            bc = BANDA_COLORS.get(name, BANDA_COLORS['Sin Conversión'])
            badge_bg = bc['bg']; badge_fg = bc['fg']; bar_color = bc['bar']
            rows += (f'<div style="display:grid;grid-template-columns:120px 80px 1fr 60px 45px;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">'
                     f'<span style="display:inline-block;padding:3px 8px;background:{badge_bg};color:{badge_fg};font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{name}</span>'
                     f'<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rng}</span>'
                     f'<div style="height:8px;background:var(--paper-soft);position:relative;border-radius:2px;"><div style="position:absolute;left:0;top:0;height:100%;width:{bar_w}%;background:{bar_color};border-radius:2px;"></div></div>'
                     f'<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{fmt_int_es(n)}</span>'
                     f'<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct:.1f}%</span>'
                     f'</div>')
        return rows, total
    
    levels_ef = [
        ('Súper Crítica','&lt; 60%','#C0392B'),
        ('Crítica','60–85%','#C0392B'),
        ('Revisar','85–93%','#F97316'),
        ('Aceptable','93–97%','#FCD34D'),
        ('Exitosa','≥ 97%','#1A6B4A'),
    ]
    levels_cv = [
        ('Sin Conversión','BKGS=0','#8A8377'),
        ('Crítica','&lt; 0,8%','#C0392B'),
        ('Revisar','0,8–1,5%','#F97316'),
        ('Aceptable','1,5–2,5%','#FCD34D'),
        ('Exitosa','≥ 2,5%','#1A6B4A'),
    ]
    
    rows_ef, total_ef = render_table(sev_ef_p80, levels_ef)
    rows_cv, total_cv = render_table(sev_cv_p80, levels_cv)
    
    n_critmas_ef = int(sev_ef_p80.get('Crítica',0) + sev_ef_p80.get('Súper Crítica',0))
    n_supc_ef = int(sev_ef_p80.get('Súper Crítica',0))
    n_sc = int(sev_cv_p80.get('Sin Conversión',0))
    n_crit_cv = int(sev_cv_p80.get('Crítica',0))
    n_proc = total_cv - n_sc
    
    return f'''<section id="severity-combinada" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head">
<div>
<div class="section-num">Sección 02</div>
<h2 class="section-title">Severity</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">P80 · {fmt_int_es(total_ef)} hoteles</span>
<p class="section-kicker">Distribución de hoteles del Top volumen CR (P80) por banda de Eficacia (target ≥ 97%) y Conv Rate (target ≥ 2,5%). Sin Conversión es cohorte aparte (BKGS=0); Severity ConvRate se aplica solo a procesables.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:#EA0074;margin:0 0 12px;">Eficacia</h3>
{rows_ef}
</div>
<div>
<h3 style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{CR_ACCENT};margin:0 0 12px;">Conv Rate</h3>
{rows_cv}
</div>
</div>
</section>
'''


_WOW_NEUTRO = '<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F2EEE6;color:#8A8377;">—</em>'

def _fmt_wow_cv(v):
    """WoW ConvRate en pp — verde si sube."""
    import math
    if v is None or (isinstance(v,float) and (math.isnan(v) or math.isinf(v))) or abs(v) < 0.001:
        return '<em class="wow-pill nd">—</em>'
    mejora = v > 0
    cls = 'dn' if mejora else 'up'
    arrow = '↑' if v > 0 else '↓'
    txt = f'{arrow}{abs(v):.2f}'.replace('.', ',')
    return f'<em class="wow-pill {cls}">{txt}</em>'

def _fmt_wow(v):
    """Formatea delta WoW: pill verde/rojo o pill gris neutro."""
    import math
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return _WOW_NEUTRO
    if abs(v) < 0.005:
        return _WOW_NEUTRO
    arrow = '↑' if v > 0 else '↓'
    wc = '#2F6C34' if v > 0 else '#C0392B'
    wb = '#EAF3DE' if v > 0 else '#FCE8E6'
    txt = f'{arrow}{abs(v):.1f}'.replace('.', ',')
    return f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wb};color:{wc};">{txt}</em>'

# ============ SECCIÓN TOP 5 helper ============
def render_top_table_cr(df, cols_def, accent_color=CR_ACCENT, with_hist=False, start_idx=0, show_header=True, sb_id=None):
    """Tabla de top hoteles/dims: top 100, primeras 10 visibles, resto sb-hidden.
    sb_id: si se pasa y show_header=True, la primera columna del header es un searchbox integrado (Prop D).
    """
    grid = ' '.join(c['width'] for c in cols_def)
    header = ''
    if show_header:
        _hd = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:0 0 6px 0;border-bottom:2px solid {accent_color};margin-bottom:2px;">'
        for idx_c, c in enumerate(cols_def):
            if idx_c == 0 and sb_id:
                # Prop D: primera columna = searchbox integrado
                _hd += searchbox_header_html(sb_id, accent_color=accent_color,
                                              placeholder='Hotel o corporativo…',
                                              th_id=f'th-{sb_id}')
            else:
                h_align = c.get('align','right')
                color = accent_color if c.get('key') in ('hotel','label') else 'var(--ink-muted)'
                _hd += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{color};text-align:{h_align};padding:9px 0;">{c["label"]}</span>'
        _hd += '</div>'
        header = _hd

    rows_html = header
    for i, r in df.iterrows():
        row_num = i + 1  # posición 1-based real del df
        row_idx = i      # 0-based para sb-hidden (primeras 10 visibles)
        row_cells = ''
        for c in cols_def:
            align = c.get('align','right')
            val = c['fmt'](r) if callable(c['fmt']) else c['fmt']
            if c.get('key') == 'hotel':
                hotel_name = truncate(clean_hotel_name(r.get('Hotel') or '-'), 36)
                sub = clean_corp_name(r.get('CorpName',''))
                chan = r.get('Channel', hotel_channel_map.get(r.get('Hotel',''), ''))
                sub_line = f'{sub} · {chan}' if chan and chan not in ('', 'N/D', sub) else sub
                row_cells += (f'<div>'
                              f'<div style="font-size:11px;font-weight:600;color:var(--ink);line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{r.get("Hotel","")}">{row_num}. {hotel_name}</div>'
                              f'<div style="font-size:9px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.05em;margin-top:1px;">{sub_line}</div>'
                              f'</div>')
            elif c.get('key') == 'bnd':
                bnd_val = r.get('BandaEficacia','') or r.get('BandaConvRate','')
                bc = BANDA_COLORS.get(bnd_val, BANDA_COLORS['Sin Conversión'])
                row_cells += (f'<div style="display:flex;align-items:center;">'
                              f'<span style="font-size:8px;font-weight:700;padding:2px 5px;border-radius:2px;'
                              f'background:{bc["bg"]};color:{bc["fg"]};text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;">{bnd_val}</span>'
                              f'</div>')
            elif c.get('key') == 'wow':
                row_cells += f'<span style="text-align:right;font-size:11px;">{val}</span>'
            else:
                row_cells += f'<span style="text-align:{align};color:var(--ink);font-size:11px;font-variant-numeric:tabular-nums;">{val}</span>'
        hist_attrs = ''
        if with_hist:
            ef_curr = round(float(r.get('Eficacia', 0)) * 100, 4)
            ef_prev = ef_curr - float(r.get('Eficacia_WoW_pp', 0) or 0)
            cv_curr = round(float(r.get('ConvRate', 0)) * 100, 4)
            cv_prev = cv_curr - float(r.get('ConvRate_WoW_pp', 0) or 0)
            lbl = truncate(clean_hotel_name(r.get('Hotel') or '-'), 28)
            hist_attrs = (f' data-hist-w21="{ef_curr}" data-hist-w20="{round(ef_prev,4)}"'
                          f' data-hist-cv-w21="{cv_curr}" data-hist-cv-w20="{round(cv_prev,4)}"'
                          f' data-hist-label="{lbl}"')
        # Prop D: las filas llevan data-lbl para que attachTable las encuentre
        lbl_for_tbl = truncate(clean_hotel_name(r.get('Hotel') or '-'), 36) if sb_id else ''
        tbl_attr = f' data-lbl="{lbl_for_tbl} {clean_corp_name(r.get("CorpName",""))}"' if sb_id else ''
        cursor = 'cursor:pointer;' if with_hist else ''
        if row_idx < 5: hidden = ''
        elif row_idx < 10: hidden = ' rows-more'
        else: hidden = ' sb-hidden'
        rows_html += (f'<div{hist_attrs}{tbl_attr} class="{hidden.strip()}" data-row-idx="{row_idx}"'
                      f' style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;'
                      f'padding:7px 0;border-bottom:1px solid var(--rule-soft);{cursor}">{row_cells}</div>')
    # Botón Ver 5 más (si hay filas rows-more)
    n_total = len(df)
    if n_total > 5:
        rows_html += (f'<button class="rows-toggle" '
                      f'style="margin-top:6px;background:none;border:none;cursor:pointer;'
                      f'font-size:10px;font-weight:600;color:{accent_color};letter-spacing:.04em;'
                      f'text-transform:uppercase;padding:4px 0;display:flex;align-items:center;gap:4px;">'
                      f'<span class="toggle-label">Ver 5 más</span> '
                      f'<span class="toggle-icon" style="font-size:12px;">↓</span></button>')
    return rows_html

def render_criticos():
    df1 = TOP['criticos']
    df2 = TOP['criticos_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'Checkrates','width':'72px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'cv','label':'ConvRate','width':'58px','fmt':lambda r:fmt_pct2(r['ConvRate'])},
        {'key':'wowcv','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow_cv(r.get('ConvRate_WoW_pp', float('nan')))},
        {'key':'ef','label':'Eficacia','width':'58px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'wow','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))},
    ]
    import pandas as _pd; df_all = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = render_top_table_cr(df_all, cols)
    
    return f'''<section id="hoteles-criticos" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">Hoteles críticos</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · peor Eficacia con BKGS&gt;0 · ordenado ↑</span>
<p class="section-kicker">Hoteles del P80 con mayor severidad por Eficacia. Combinan volumen CR alto con tasa de errores elevada — primer foco de remediación técnica.</p>
</div>
</div>
<div>{col1}</div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 100 de <strong>Hoteles Críticos</strong> está en la pestaña <em>«Críticos»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Checkrates_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bajo_rendimiento():
    df1 = TOP['bajo_rend']
    df2 = TOP['bajo_rend_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'Checkrates','width':'72px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'cv','label':'ConvRate','width':'58px','fmt':lambda r:fmt_pct2(r['ConvRate'])},
        {'key':'wowcv','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow_cv(r.get('ConvRate_WoW_pp', float('nan')))},
        {'key':'ef','label':'Eficacia','width':'58px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'wow','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))},
    ]
    import pandas as _pd; df_all = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = render_top_table_cr(df_all, cols)
    
    return f'''<section id="bajo-rendimiento" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
<div>
<div class="section-num">Sección 05</div>
<h2 class="section-title">Bajo rendimiento</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · alto volumen CR · ConvRate Crítica/Revisar · ordenado por CR ↓</span>
<p class="section-kicker">Hoteles con tráfico significativo pero ConvRate insuficiente. Convierten, pero por debajo del target ≥2,5% — oportunidad de tunning de pricing/disponibilidad.</p>
</div>
</div>
<div>{col1}</div>
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 100 de <strong>Bajo Rendimiento</strong> está en la pestaña <em>«Bajo Rendimiento»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Checkrates_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_sin_conv():
    df1 = TOP['sin_conv']
    df2 = TOP['sin_conv_extra']
    cols = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'Checkrates','width':'72px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'ef','label':'Eficacia','width':'62px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'wow','label':'WoW','width':'44px','fmt':lambda r:_fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))},
    ]
    import pandas as _pd; df_all = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = render_top_table_cr(df_all, cols) if len(df2)>0 else ''
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    
    body = f'<div>{col1}</div>'
    
    return f'''<section id="sin-conversion" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
<div>
<div class="section-num">Sección 06</div>
<h2 class="section-title">Sin conversión</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · alto CR · 0 BKGS · ordenado por CR ↓</span>
<p class="section-kicker">{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings pese a tener volumen de check-rates. Diagnóstico técnico (errores de carga, mapping, inventario) o contractual. No entra en Severity de ConvRate.</p>
</div>
</div>
{body}
<div class="detail-callout" style="margin-top:24px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 100 de <strong>Sin Conversión</strong> está en la pestaña <em>«Sin Conversión»</em> del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Checkrates_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

# ============ SECCIÓN POR DIMENSIÓN (Corp / Destino / Channel) ============
def _render_dim_table(df, dim_col, dim_label, start_idx=0, wow_col=None, with_hist=False, sb_id=None):
    """Tabla de dimensión (corp/destino/channel).
    sb_id: si se pasa, la primera columna del header es searchbox integrado (Prop D).
    Badge de banda: Corporativo (BandaEficacia), Destino (BandaEficacia), Channel (ver render_chan_table).
    """
    """Tabla dimensión: 100 filas, 10 visibles, resto sb-hidden. Estilos unificados."""
    import math
    has_wow = wow_col and wow_col in df.columns
    has_cv_wow = 'ConvRate_WoW_pp' in df.columns if df is not None and hasattr(df, 'columns') else False
    if has_wow and has_cv_wow:
        grid = '1fr 72px 80px 60px 68px 38px 68px 38px'
    elif has_wow:
        grid = '1fr 72px 90px 70px 70px 75px 50px'
    else:
        grid = '1fr 72px 90px 70px 70px 75px'
    headers = [dim_label,'Severity','Checkrates','BKGS','ConvRate']
    if has_cv_wow: headers.append('WoW')
    headers.append('Eficacia')
    if has_wow: headers.append('WoW')

    # Header: Prop D si sb_id, normal en caso contrario
    rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:4px 0;border-bottom:2px solid {CR_ACCENT};margin-bottom:4px;align-items:end;">'
    for idx_h, label in enumerate(headers):
        if idx_h == 0 and sb_id:
            rows += searchbox_header_html(sb_id, accent_color=CR_ACCENT,
                                          placeholder=f'{dim_label}…',
                                          th_id=f'th-{sb_id}')
        else:
            align = 'left' if label in (dim_label, 'Severity') else 'right'
            color = CR_ACCENT if label==dim_label else 'var(--ink-muted)'
            rows += f'<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{color};text-align:{align};padding:9px 0;">{label}</span>'
    rows += '</div>'

    for i, r in df.iterrows():
        row_idx = start_idx + i   # 0-based para sb-hidden
        bnd = r.get('BandaEficacia','')
        bc = BANDA_COLORS.get(bnd, BANDA_COLORS['Sin Conversión'])
        badge_cell = (f'<div style="display:flex;align-items:center;">'
                      f'<span style="font-size:8px;font-weight:700;padding:2px 5px;border-radius:2px;'
                      f'background:{bc["bg"]};color:{bc["fg"]};text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;">{bnd}</span>'
                      f'</div>')
        n = row_idx + 1
        label_val = clean_corp_name(r[dim_col]) if dim_col == 'CorpName' else (clean_destino_name(r[dim_col]) if dim_col == 'Destino' else truncate(r[dim_col], 28))
        cv_val = r.get('ConvRate', None)
        cv_str = fmt_pct2(cv_val) if cv_val is not None and not (isinstance(cv_val, float) and math.isnan(cv_val)) else '—'
        cells = (f'<div style="overflow:hidden;"><span style="font-size:11px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;">{n}. {label_val}</span></div>'
                 f'{badge_cell}'
                 f'<span style="text-align:right;color:var(--ink);font-size:11px;font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-size:11px;font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                 f'<span style="text-align:right;color:var(--ink);font-size:11px;font-variant-numeric:tabular-nums;">{cv_str}</span>'
                 f'{_fmt_wow_cv(r.get("ConvRate_WoW_pp", float("nan"))) if has_cv_wow else ""}'
                 f'<span style="text-align:right;color:var(--ink);font-size:11px;font-weight:600;font-variant-numeric:tabular-nums;">{fmt_pct2(r["Eficacia"])}</span>')
        if has_wow:
            wow_v = r.get(wow_col, None)
            try:
                if wow_v is not None and wow_v == wow_v and not math.isnan(float(wow_v)) and abs(wow_v) >= 0.005:
                    mejora = wow_v > 0
                    wc = '#2F6C34' if mejora else '#C0392B'
                    wbg = '#EAF3DE' if mejora else '#FCE8E6'
                    arrow = '↑' if wow_v > 0 else '↓'
                    txt = f'{arrow}{abs(wow_v):.1f}'.replace('.', ',')
                    wow_html = f'<em style="font-style:normal;display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:{wbg};color:{wc};text-align:right;">{txt}</em>'
                else:
                    wow_html = _WOW_NEUTRO
            except:
                wow_html = _WOW_NEUTRO
            cells += wow_html
        hist_attrs = ''
        if with_hist:
            ef_curr = round(float(r.get('Eficacia', 0)) * 100, 4)
            wow_v = r.get(wow_col) if wow_col else 0
            try: wow_f = float(wow_v) if wow_v == wow_v else 0
            except: wow_f = 0
            ef_prev = ef_curr - wow_f
            cv_curr = round(float(r.get('ConvRate', 0)) * 100, 4)
            cv_wow = r.get('ConvRate_WoW_pp', 0)
            try: cv_wow_f = float(cv_wow) if cv_wow == cv_wow else 0
            except: cv_wow_f = 0
            cv_prev = cv_curr - cv_wow_f
            lbl_short = truncate(str(label_val), 28)
            hist_attrs = (f' data-hist-w21="{ef_curr}" data-hist-w20="{round(ef_prev, 4)}"'
                          f' data-hist-cv-w21="{cv_curr}" data-hist-cv-w20="{round(cv_prev, 4)}"'
                          f' data-hist-label="{lbl_short}"')
        cursor = 'cursor:pointer;' if with_hist else ''
        if row_idx < 5: hidden = ''
        elif row_idx < 10: hidden = ' rows-more'
        else: hidden = ' sb-hidden'
        tbl_attr = f' data-lbl="{label_val}"' if sb_id else ''
        rows += (f'<div{hist_attrs}{tbl_attr} class="{hidden.strip()}" data-row-idx="{row_idx}"'
                 f' style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;'
                 f'padding:7px 0;border-bottom:1px solid var(--rule-soft);{cursor}">{cells}</div>')
    return rows

def render_top_dimension(num, title, df_full, dim_col, dim_label, kicker, key='hotel'):
    """Top 10 a 2 columnas (5+5). df_full debe tener al menos 10 rows ideal."""
    df_top10 = df_full.head(10).reset_index(drop=True)
    df1 = df_top10.iloc[:5].reset_index(drop=True)
    df2 = df_top10.iloc[5:10].reset_index(drop=True)
    
    import pandas as _pd; df_all_dim = _pd.concat([df1, df2]).reset_index(drop=True)
    col1 = _render_dim_table(df_all_dim, dim_col, dim_label, start_idx=0)
    
    body = f'<div>{col1}</div>'
    
    return f'''<section id="top-{key}" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
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
        bc = BANDA_COLORS.get(b, BANDA_COLORS['Sin Conversión'])
        return f'<span style="display:inline-block;font-size:9px;font-weight:700;padding:2px 7px;border-radius:2px;background:{bc["bg"]};color:{bc["fg"]};text-transform:uppercase;letter-spacing:.05em;">{b}</span>'
    
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
    
    cards = grupo_card(g_pp,'#5C469C','🏠') + grupo_card(g_tp, CR_ACCENT,'🔌')
    
    cv_gap = (g_pp['ConvRate'] - g_tp['ConvRate'])*100
    cr_share_tp = g_tp['CR_Unicos']/(g_pp['CR_Unicos']+g_tp['CR_Unicos'])*100
    
    return f'''<section id="channel-agrupado" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
<div>
<div class="section-num">Sección 07</div>
<h2 class="section-title">🔌 Análisis por tipo de producto</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Producto Propio vs Third Party</span>
<p class="section-kicker">Vista consolidada por familia de canal según decisión post Week 17. Producto Propio: DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees. Third Party: Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate.</p>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px;">{cards}</div>
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
<h2 class="section-title">📋 Plan de acción</h2>
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
<div class="accion">Revisión integral del producto <strong>B2C</strong> (ConvRate Crítica {fmt_pct2(M[f"B2C_w{WEEK_NUM_INT}"]["conv_rate"])}) · pricing, UX, mapping, fee structure.</div>
<div class="action-meta-bottom"><span class="cluster-tag">Estratégica · ES2</span><span class="meta-item"><strong>Plazo</strong> Q3</span><span class="meta-item"><strong>Métrica</strong> ConvRate &gt; 1,5%</span></div>
</div>
</div>
{render_seguimiento_block(SEGUIMIENTO_FILE, accent_color='#5C469C')}
</section>
'''

# Render parte 2 completa
RESUMEN = render_resumen_ej()
SEV_COMBINADA = render_severities_combinadas()

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
    COLOR_TP = CR_ACCENT
    
    def render_split_table(df, dim_col, color_b):
        grid = '1fr 90px 70px 75px 70px'
        rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {color_b};margin-bottom:4px;">'
        for label in ['Channel','CR','BKGS','Eficacia','ConvRate']:
            align = 'left' if label=='Channel' else 'right'
            color = color_b if label=='Channel' else 'var(--ink-muted)'
            rows += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{align};">{label}</span>'
        rows += '</div>'
        for i, r in df.iterrows():
            bnd = r.get('BandaEficacia','')
            bc = BANDA_COLORS.get(bnd, BANDA_COLORS['Sin Conversión'])
            bnd_bg = bc['bg']; bnd_fg = bc['fg']
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
    
    return f'''<section id="top-channel" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;"><div class="section-head">
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

# ============ NUEVO · BLOQUES CON TABS (post mejora secciones globales) ============
def _render_panel_top_table_cr(df, cols, with_hist=False, sb_id=None):
    """Panel: col1(filas 1-5) + col2(filas 6-10) con header en cada col, filas 11-100 sb-hidden.
    sb_id: si se pasa, el header de col1 integra searchbox_header_html en la primera columna (Prop D).
    """
    df = df.reset_index(drop=True)  # index 0..N
    df1 = df.iloc[:5].copy()        # index 0-4
    import pandas as _pd
    df_all = _pd.concat([df1, df.iloc[5:]]).reset_index(drop=True)

    # Construir tabla única con searchbox si aplica
    if sb_id:
        cols_mod = list(cols)
        col1 = render_top_table_cr(df_all, cols_mod, with_hist=with_hist, sb_id=sb_id)
    else:
        col1 = render_top_table_cr(df_all, cols, with_hist=with_hist)

    return f'<div class="tbl-wrap">{col1}</div>'

def render_historico_seccion_cr(canvas_id_ef, canvas_id_cv,
                                 banda_ef, val_ef,
                                 banda_cv, val_cv):
    """
    Módulo histórico doble (Eficacia + ConvRate) para secciones de análisis CR.
    Un wrapper por sección — se actualiza al clickear cualquier fila de la tabla.
    canvas_id_ef : ej. 'hcr-hotel-ef'
    canvas_id_cv : ej. 'hcr-hotel-cv'
    """
    html_ef = render_historico_cr('eficacia', banda_ef, val_ef, canvas_id_ef)
    html_cv = render_historico_cr('convrate', banda_cv, val_cv, canvas_id_cv)

    js = f"""
<script>
(function() {{
  var section = document.getElementById('hist-{canvas_id_ef}-container');
  if (!section) return;
  var parent = section.closest('section') || document.body;

  function resetToGlobal() {{
    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    document.dispatchEvent(new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_ef}'}}}}));
    document.dispatchEvent(new CustomEvent('hist-reset', {{detail: {{cid: '{canvas_id_cv}'}}}}));
  }}

  parent.addEventListener('click', function(e) {{
    var row = e.target.closest('[data-hist-w21]');
    if (!row) return;
    // Solo filas DENTRO del bloque de tabs (no en los módulos históricos mismos)
    if (e.target.closest('.kpi-card')) return;
    if (row.getAttribute('data-selected-hist') === '1') {{ resetToGlobal(); return; }}

    var ef_curr = parseFloat(row.getAttribute('data-hist-w21'));
    var ef_prev = parseFloat(row.getAttribute('data-hist-w20') || ef_curr);
    var cv_curr = parseFloat(row.getAttribute('data-hist-cv-w21'));
    var cv_prev = parseFloat(row.getAttribute('data-hist-cv-w20') || cv_curr);
    var lbl = row.getAttribute('data-hist-label') || '';

    parent.querySelectorAll('[data-hist-w21]').forEach(function(r) {{
      r.style.background = ''; r.removeAttribute('data-selected-hist');
    }});
    row.setAttribute('data-selected-hist', '1');
    row.style.background = 'var(--accent-soft)';

    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{
      cid: '{canvas_id_ef}', w_curr: ef_curr, w_prev: ef_prev, label: lbl
    }}}}));
    document.dispatchEvent(new CustomEvent('hist-update', {{detail: {{
      cid: '{canvas_id_cv}', w_curr: cv_curr, w_prev: cv_prev, label: lbl
    }}}}));
  }});
}})();
</script>"""

    return f'''<div id="hist-{canvas_id_ef}-container"
     style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;margin-bottom:8px;">
  <div>{html_ef}</div>
  <div>{html_cv}</div>
</div>{js}'''


def render_bloque_hoteles_cr():
    """Sección 04 · 4 tabs: Críticos · Bajo Rend · Sin Conv · Menor CR."""
    cols_main = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'bnd','label':'Severity','width':'72px','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'Checkrates','width':'72px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'cv','label':'ConvRate','width':'58px','fmt':lambda r:fmt_pct2(r['ConvRate'])},
        {'key':'wowcv','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow_cv(r.get('ConvRate_WoW_pp', float('nan')))},
        {'key':'ef','label':'Eficacia','width':'58px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'wow','label':'WoW','width':'38px','fmt':lambda r:_fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))},
    ]
    cols_sc = [
        {'key':'hotel','label':'Hotel','width':'1fr','fmt':lambda r:'','align':'left'},
        {'key':'bnd','label':'Severity','width':'72px','fmt':lambda r:'','align':'left'},
        {'key':'cr','label':'Checkrates','width':'72px','fmt':lambda r:fmt_int_es(r['CR_Unicos'])},
        {'key':'ef','label':'Eficacia','width':'62px','fmt':lambda r:fmt_pct2(r['Eficacia'])},
        {'key':'wow','label':'WoW','width':'44px','fmt':lambda r:_fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))},
    ]
    
    df_crit = TOP['criticos'].reset_index(drop=True)
    panel_crit = _render_panel_top_table_cr(df_crit, cols_main, with_hist=True, sb_id='sb-h-crit')
    
    df_br = TOP['bajo_rend'].reset_index(drop=True)
    panel_br = _render_panel_top_table_cr(df_br, cols_main, with_hist=True, sb_id='sb-h-br')
    
    df_sc = TOP['sin_conv'].reset_index(drop=True)
    panel_sc = _render_panel_top_table_cr(df_sc, cols_sc, with_hist=True, sb_id='sb-h-sc')
    
    df_mcv = TOP['menor_cv'].head(100).reset_index(drop=True)
    panel_mcv = _render_panel_top_table_cr(df_mcv, cols_main, with_hist=True, sb_id='sb-h-mcv')
    
    n_total_sc = (p80_hotel['Bookings']==0).sum()
    
    k_crit = 'Hoteles del P80 con mayor severidad por Eficacia. Combinan volumen CR alto con tasa de errores elevada — primer foco de remediación técnica.'
    k_br = 'Hoteles con tráfico significativo pero ConvRate insuficiente. Convierten, pero por debajo del target ≥2,5% — oportunidad de tunning de pricing/disponibilidad.'
    k_sc = f'{fmt_int_es(n_total_sc)} hoteles del P80 con cero bookings pese a tener volumen de check-rates. Diagnóstico técnico (errores de carga, mapping, inventario) o contractual.'
    k_mcv = 'Top 10 hoteles con BKGS&gt;0 ordenados por menor ConvRate · listados sin importar volumen, foco directo en conversión.'
    
    panels = (
        f'<div class="tab-panel" data-tab="crit"><p class="tab-kicker">{k_crit}</p>{panel_crit}</div>'
        f'<div class="tab-panel" data-tab="br"><p class="tab-kicker">{k_br}</p>{panel_br}</div>'
        f'<div class="tab-panel" data-tab="sc"><p class="tab-kicker">{k_sc}</p>{panel_sc}</div>'
        f'<div class="tab-panel" data-tab="mcv"><p class="tab-kicker">{k_mcv}</p>{panel_mcv}</div>'
    )
    
    hist_hotel = render_historico_seccion_cr(
        canvas_id_ef = 'hcr-hotel-ef',
        canvas_id_cv = 'hcr-hotel-cv',
        banda_ef = banda_eficacia(M['global_current']['eficacia']),
        val_ef   = M['global_current']['eficacia'],
        banda_cv = banda_convrate(M['global_current']['conv_rate'], M['global_current']['bookings']),
        val_cv   = M['global_current']['conv_rate'],
    )
    
    return f'''<section id="por-hotel" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head">
<div>
<div class="section-num">Sección 04</div>
<h2 class="section-title">🏨 Análisis por hotel</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 · 4 ópticas analíticas</span>
<p class="section-kicker">Hoteles del P80 vistos desde cuatro ángulos analíticos: críticos (peor eficacia con BKGS&gt;0), bajo rendimiento (ConvRate insuficiente con volumen), sin conversión (BKGS=0), y menor ConvRate (peores conversores absolutos).</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-h-crit" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-br" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-sc" name="tabs-h" style="display:none" type="radio"/>
<input id="tab-h-mcv" name="tabs-h" style="display:none" type="radio"/>
<div class="tabs-row">
<label class="tab-label" for="tab-h-crit">Críticos</label>
<label class="tab-label" for="tab-h-br">Bajo Rendimiento</label>
<label class="tab-label" for="tab-h-sc">Sin Conversión</label>
<label class="tab-label" for="tab-h-mcv">Menor ConvRate</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
{hist_hotel}
<div class="detail-callout" style="margin-top:18px;">
<div><div class="lbl">Detalle completo</div><div class="msg">El Top 100 de cada óptica está en pestañas separadas del Excel adjunto.</div></div>
<a class="badge-link" href="Analisis_Checkrates_7d.xlsx">Excel ↗</a>
</div>
</section>
'''

def render_bloque_dimensiones_cr():
    """Sección 05 · 3 tabs: Corporativo · Destino · Channel (split PP/TP integrado en panel)."""

    def _add_wow(df_top10, dim_col, ref_df, ef_col='Eficacia_W17', cv_col='ConvRate_W17'):
        """Merge WoW W17 al dataframe de dimensión."""
        if ref_df is None: return df_top10, None
        merged = df_top10.merge(ref_df[[dim_col, ef_col, cv_col]], on=dim_col, how='left')
        merged['Eficacia_WoW_pp'] = (merged['Eficacia'] - merged[ef_col]) * 100
        merged['BandaEficacia'] = merged['Eficacia'].apply(banda_eficacia)
        if cv_col in merged.columns:
            merged['ConvRate_WoW_pp'] = (merged['ConvRate'] - merged[cv_col]) * 100
        return merged, 'Eficacia_WoW_pp'

    def panel_for_dim(df_full, dim_col, dim_label, ref_df=None, sb_id=None):
        df_top = df_full.head(100).reset_index(drop=True)
        df_top_wow, wow_col = _add_wow(df_top, dim_col, ref_df)
        if 'BandaEficacia' not in df_top_wow.columns:
            df_top_wow['BandaEficacia'] = df_top_wow['Eficacia'].apply(banda_eficacia)
        rows_html = _render_dim_table(df_top_wow, dim_col, dim_label, start_idx=0, wow_col=wow_col, with_hist=True, sb_id=sb_id)
        return f'<div class="tbl-wrap">{rows_html}</div>'

    panel_corp = panel_for_dim(TOP['corps_10'], 'CorpName', 'Corporativo', ref_df=g_corp_w17, sb_id='sb-d-corp')
    panel_dest = panel_for_dim(TOP['destinos'], 'Destino', 'Destino', ref_df=g_dest_w17, sb_id='sb-d-dest')
    
    # Channel · split PP/TP en el mismo panel
    PRODUCTO_PROPIO = ['DerbySoft','Internal','HBSI','SynXis','Siteminder','Travelclick','Omnibees']
    THIRD_PARTY     = ['Expedia','HotelBeds Apitude','Hotel Unico V2','Travelgate']
    df_chan = TOP['channels']

    # Merge WoW channel con g_channel_w17
    g_ch_w17 = g_channel_w17
    if g_ch_w17 is not None:
        # Merge WoW — incluir ConvRate_W17 si está disponible
        w17_cols = ['ExternalProviderName','Eficacia_W17']
        if 'ConvRate_W17' in g_ch_w17.columns: w17_cols.append('ConvRate_W17')
        df_chan = df_chan.merge(g_ch_w17[w17_cols], on='ExternalProviderName', how='left')
        df_chan['Eficacia_WoW_pp'] = (df_chan['Eficacia'] - df_chan['Eficacia_W17']) * 100
        if 'ConvRate_W17' in df_chan.columns:
            df_chan['ConvRate_WoW_pp'] = (df_chan['ConvRate'] - df_chan['ConvRate_W17']) * 100

    df_pp = df_chan[df_chan['ExternalProviderName'].isin(PRODUCTO_PROPIO)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)
    df_tp = df_chan[df_chan['ExternalProviderName'].isin(THIRD_PARTY)].sort_values('CR_Unicos', ascending=False).reset_index(drop=True)

    def render_chan_table(df, color_b):
        import math
        has_wow    = 'Eficacia_WoW_pp' in df.columns
        has_cv_wow = 'ConvRate_WoW_pp' in df.columns
        # Grid: Channel · CR únicos · BKGS · ConvRate · WoW · Eficacia · WoW
        if has_wow and has_cv_wow:
            grid = '1fr 80px 60px 68px 40px 68px 40px'
        elif has_wow:
            grid = '1fr 90px 70px 70px 75px 50px'
        else:
            grid = '1fr 90px 70px 70px 75px'
        headers = ['Channel','Checkrates','BKGS','ConvRate']
        if has_cv_wow: headers.append('WoW')
        headers.append('Eficacia')
        if has_wow: headers.append('WoW')
        rows = f'<div style="display:grid;grid-template-columns:{grid};gap:10px;padding:8px 0;border-bottom:2px solid {color_b};margin-bottom:4px;">'
        for label in headers:
            align = 'left' if label=='Channel' else 'right'
            color = color_b if label=='Channel' else 'var(--ink-muted)'
            rows += f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:{color};text-align:{align};">{label}</span>'
        rows += '</div>'
        for i, r in df.iterrows():
            cv_val = r.get('ConvRate', None)
            cv_str = fmt_pct2(cv_val) if cv_val is not None and not (isinstance(cv_val, float) and (math.isnan(cv_val) or math.isinf(cv_val))) else '—'
            ef_val = r.get('Eficacia', None)
            ef_str = fmt_pct2(ef_val) if ef_val is not None and not (isinstance(ef_val, float) and (math.isnan(ef_val) or math.isinf(ef_val))) else '—'
            # data attrs para módulo histórico reactivo
            _ef21 = round(float(ef_val) * 100, 4) if ef_val and not (isinstance(ef_val, float) and math.isnan(float(ef_val))) else 0
            _ef20_raw = r.get('Eficacia_W17', ef_val)
            _ef20 = round(float(_ef20_raw) * 100, 4) if _ef20_raw and not (isinstance(_ef20_raw, float) and math.isnan(float(_ef20_raw))) else _ef21
            _cv21 = round(float(cv_val) * 100, 4) if cv_val and not (isinstance(cv_val, float) and math.isnan(float(cv_val))) else 0
            _cv20_raw = r.get('ConvRate_W17', cv_val)
            _cv20 = round(float(_cv20_raw) * 100, 4) if _cv20_raw and not (isinstance(_cv20_raw, float) and math.isnan(float(_cv20_raw))) else _cv21
            _lbl_chan = truncate(r["ExternalProviderName"],28)
            _bnd_ch = r.get('BandaEficacia','') or (banda_eficacia(ef_val) if ef_val else '')
            _bdg_ch = mini_badge(_bnd_ch)
            cells = (f'<div><div style="font-weight:600;color:{color_b};line-height:1.3;display:flex;align-items:center;gap:4px;">{i+1}. {_lbl_chan}{_bdg_ch}</div></div>'
                     f'<span style="text-align:right;color:{color_b};font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["CR_Unicos"])}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{fmt_int_es(r["Bookings"])}</span>'
                     f'<span style="text-align:right;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;">{cv_str}</span>'
                     f'{_fmt_wow_cv(r.get("ConvRate_WoW_pp", float("nan"))) if has_cv_wow else ""}'
                     f'<span style="text-align:right;color:{color_b};font-weight:600;font-variant-numeric:tabular-nums;">{ef_str}</span>')
            if has_wow:
                cells += _fmt_wow(r.get('Eficacia_WoW_pp', float('nan')))
            rows += (f'<div class="kpi-row" style="display:grid;grid-template-columns:{grid};gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule-soft);font-size:12px;cursor:pointer;transition:background .12s;" '
                     f'data-hist-w21="{_ef21}" data-hist-w20="{_ef20}" '
                     f'data-hist-cv-w21="{_cv21}" data-hist-cv-w20="{_cv20}" '
                     f'data-hist-label="{_lbl_chan}">{cells}</div>')
        return rows
    
    panel_chan = (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">'
        f'<div><div style="font-size:11px;font-weight:700;color:#5C469C;letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;">🏠 Producto Propio</div>{render_chan_table(df_pp, "#5C469C")}</div>'
        f'<div><div style="font-size:11px;font-weight:700;color:var(--ink-muted);letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;">🔌 Third Party</div>{render_chan_table(df_tp, CR_ACCENT)}</div>'
        f'</div>'
    )
    
    top_corp = TOP['corps_10'].iloc[0]
    top_dest = TOP['destinos'].iloc[0]
    
    k_corp = f'Top corporativos por volumen CR. <strong>{top_corp["CorpName"]}</strong> lidera con {fmt_int_es(top_corp["CR_Unicos"])} CR · Eficacia {fmt_pct2(top_corp["Eficacia"])} (banda {top_corp["BandaEficacia"]}) y ConvRate {fmt_pct2(top_corp["ConvRate"])}.'
    k_dest = f'Top destinos por volumen CR. <strong>{top_dest["Destino"]}</strong> con {fmt_int_es(top_dest["CR_Unicos"])} CR · Eficacia {fmt_pct2(top_dest["Eficacia"])} y ConvRate {fmt_pct2(top_dest["ConvRate"])}.'
    k_chan = f'Channels segregados por familia. <strong style="color:#5C469C;">Producto Propio</strong>: {len(df_pp)} channels · <strong style="color:{CR_ACCENT};">Third Party</strong>: {len(df_tp)} channels.'
    
    panels = (
        f'<div class="tab-panel" data-tab="corp"><p class="tab-kicker">{k_corp}</p>{panel_corp}</div>'
        f'<div class="tab-panel" data-tab="dest"><p class="tab-kicker">{k_dest}</p>{panel_dest}</div>'
        f'<div class="tab-panel" data-tab="chan"><p class="tab-kicker">{k_chan}</p>{panel_chan}</div>'
    )
    
    hist_dim = render_historico_seccion_cr(
        canvas_id_ef = 'hcr-dim-ef',
        canvas_id_cv = 'hcr-dim-cv',
        banda_ef = banda_eficacia(M['global_current']['eficacia']),
        val_ef   = M['global_current']['eficacia'],
        banda_cv = banda_convrate(M['global_current']['conv_rate'], M['global_current']['bookings']),
        val_cv   = M['global_current']['conv_rate'],
    )
    
    return f'''<section id="por-dimension" style="margin-bottom:64px;border-top:1px solid var(--rule);padding-top:48px;">
<div class="section-head">
<div>
<div class="section-num">Sección 05</div>
<h2 class="section-title">📊 Análisis por dimensión</h2>
<span class="section-subtitle" style="color:{CR_ACCENT}">Top 10 agregados · ordenado por CR únicos ↓</span>
<p class="section-kicker">Distribución del volumen P80 por corporativo, destino y channel. Channel mantiene el split Producto Propio · Third Party para análisis de connectivity.</p>
</div>
</div>
<div class="tabs-block">
<input checked id="tab-d-corp" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-dest" name="tabs-d" style="display:none" type="radio"/>
<input id="tab-d-chan" name="tabs-d" style="display:none" type="radio"/>
<div class="tabs-row" style="align-items:flex-end;">
<label class="tab-label" for="tab-d-corp">Corporativo</label>
<label class="tab-label" for="tab-d-dest">Destino</label>
<label class="tab-label" for="tab-d-chan">Channel</label>
</div>
<div class="tab-panels">{panels}</div>
</div>
{hist_dim}
</section>
'''

BLOQUE_HOTELES_CR = render_bloque_hoteles_cr()
BLOQUE_DIM_CR = render_bloque_dimensiones_cr()

PLAN_ACCION = render_plan_accion()

ALERTAS_GLOBAL = render_alerts_block()
PART2 = RESUMEN + ALERTAS_GLOBAL + SEV_COMBINADA + BLOQUE_HOTELES_CR + BLOQUE_DIM_CR + PLAN_ACCION

with open('part2_cr.html','w') as f:
    f.write(PART2)
print(f"Part 2 CR escrito: {len(PART2):,} chars")
