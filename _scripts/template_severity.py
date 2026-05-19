"""
Helper · Severidad por canasta (Eficacia + Conv Rate o %NoDispo + RPM)
siguiendo estructura del template literal: 2 columnas, cada una con tabla de 5 filas
y barra horizontal proporcional.

API:
  render_severity_table(title, icon, accent_color, levels, total)
    levels: list of (label, banda_color, banda_bg, rango_text, count, distribution_pct)
"""

def render_severity_row(label, banda_bg, banda_fg, rango, distribution_pct, count, total):
    pct_label = f'{count/total*100:.1f}%'.replace('.',',') if total > 0 else '0,0%'
    return f'''<div style="display:grid;grid-template-columns:100px 70px 1fr 60px 50px;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--rule-soft);">
<span style="display:inline-block;padding:3px 8px;background:{banda_bg} !important;color:{banda_fg} !important;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;text-align:center;">{label}</span>
<span style="font-size:10px;color:var(--ink-muted);font-variant-numeric:tabular-nums;">{rango}</span>
<div style="height:11px;background:var(--paper-soft);position:relative;"><div style="position:absolute;left:0;top:0;height:100%;width:{distribution_pct}%;background:{banda_fg};"></div></div>
<span style="font-weight:600;text-align:right;font-variant-numeric:tabular-nums;font-size:11px;">{count:,}</span>
<span style="font-weight:500;text-align:right;color:var(--ink-muted);font-size:10px;">{pct_label}</span>
</div>'''.replace(',','.')

def render_severity_block(title, icon, header_color, levels_data, total):
    """
    title: '% Eficacia', 'Conv Rate', '% No Dispo', 'RPM'
    icon: '●' o el que aplique
    header_color: color del título y bullet
    levels_data: lista de dicts:
      {'label':'Exitosa','rango':'> 97%','count':3080,'bg':'#E8F7FD','fg':'#4FC3F4'}
    total: total para calcular %
    """
    # Encabezado
    header_row = f'''<div style="display:grid;grid-template-columns:100px 70px 1fr 60px 50px;gap:8px;padding:7px 0;border-bottom:2px solid var(--ink);margin-bottom:4px;">
<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">Nivel</span>
<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">Rango</span>
<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);">Distribución</span>
<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);text-align:right;">Hot.</span>
<span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);text-align:right;">%</span>
</div>'''
    
    rows = ''
    max_count = max((l['count'] for l in levels_data), default=1)
    for level in levels_data:
        dist_pct = (level['count']/max_count*100) if max_count > 0 else 0
        rows += render_severity_row(
            level['label'], level['bg'], level['fg'],
            level['rango'], dist_pct, level['count'], total
        )
    
    return f'''<div>
<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink);margin-bottom:14px;display:flex;align-items:center;gap:8px;">
<span style="color:{header_color};">{icon}</span><span>{title}</span>
</div>
{header_row}
{rows}
</div>'''


def render_severity_2cols(left_block, right_block):
    return f'''<h3 style="font-size:15px;font-weight:600;margin:32px 0 16px;color:var(--ink);">Severity</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
{left_block}
{right_block}
</div>'''


# Datos predefinidos de bandas
LEVELS_EFICACIA = [
    {'label':'Exitosa', 'rango':'> 97%', 'bg':'#E8F7FD', 'fg':'#4FC3F4'},
    {'label':'Aceptable', 'rango':'93–97%', 'bg':'#EDE8F7', 'fg':'#5C469C'},
    {'label':'Revisar', 'rango':'85–93%', 'bg':'#FFF4E0', 'fg':'#A86A1D'},
    {'label':'Crítica', 'rango':'60–85%', 'bg':'#FCE4F1', 'fg':'#C0392B'},
    {'label':'Súper Crítica', 'rango':'< 60%', 'bg':'#161616', 'fg':'#FFFFFF'},
]

LEVELS_CONVRATE = [
    {'label':'Exitosa', 'rango':'> 2,5%', 'bg':'#E8F7FD', 'fg':'#4FC3F4'},
    {'label':'Aceptable', 'rango':'1,5–2,5%', 'bg':'#EDE8F7', 'fg':'#5C469C'},
    {'label':'Revisar', 'rango':'0,8–1,5%', 'bg':'#FFF4E0', 'fg':'#A86A1D'},
    {'label':'Crítica', 'rango':'< 0,8%', 'bg':'#FCE4F1', 'fg':'#C0392B'},
    {'label':'Sin Conv', 'rango':'BKGS=0', 'bg':'#F2EEE6', 'fg':'#8A8377'},
]

LEVELS_NODISPO = [
    {'label':'Exitosa', 'rango':'< 3%', 'bg':'#E8F7FD', 'fg':'#4FC3F4'},
    {'label':'Aceptable', 'rango':'3–5%', 'bg':'#EDE8F7', 'fg':'#5C469C'},
    {'label':'Revisar', 'rango':'5–20%', 'bg':'#FFF4E0', 'fg':'#A86A1D'},
    {'label':'Crítica', 'rango':'20–60%', 'bg':'#FCE4F1', 'fg':'#C0392B'},
    {'label':'Súper Crítica', 'rango':'> 60%', 'bg':'#161616', 'fg':'#FFFFFF'},
]

LEVELS_RPM = [
    {'label':'Exitosa', 'rango':'≥ $1500', 'bg':'#E8F7FD', 'fg':'#4FC3F4'},
    {'label':'Aceptable', 'rango':'$650–$1500', 'bg':'#EDE8F7', 'fg':'#5C469C'},
    {'label':'Revisar', 'rango':'$200–$650', 'bg':'#FFF4E0', 'fg':'#A86A1D'},
    {'label':'Crítica', 'rango':'< $200', 'bg':'#FCE4F1', 'fg':'#C0392B'},
    {'label':'Sin Conv', 'rango':'BKGS=0', 'bg':'#F2EEE6', 'fg':'#8A8377'},
]

def make_severity_levels(sev_dict, levels_template):
    """Construye lista de levels con counts de un dict {Banda: count}.
    Maneja sinónimos: 'Sin Conversión' -> 'Sin Conv'."""
    syn = {'Sin Conv':'Sin Conversión'}
    out = []
    for lvl in levels_template:
        key = syn.get(lvl['label'], lvl['label'])
        out.append({**lvl, 'count': int(sev_dict.get(key, 0))})
    return out
