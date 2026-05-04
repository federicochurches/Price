"""
Helper · Resumen Ejecutivo siguiendo estructura literal del template.

Estructura: 
- Header overline pequeño con 🎯 + título (fuera del card)
- Card con border-top 3px negro, fondo paper-soft, padding 28px 32px
- Grid 2 columnas (5 findings cada una) · gap:14px 28px
- Cada finding: <li flex>
    span N° (gris muted)
    span valor numérico destacado (color del reporte)
    span <strong>Título</strong> Descripción (sin highlights .hl)

API:
  render_resumen_ejecutivo(findings, accent_color, header_title='Resumen Ejecutivo')
  
  findings: list of 10 dicts, cada uno con:
    - 'numero': string (ej '−11.1%', '93.9%', '5.465', 'Top 3', '$650')
    - 'titulo': string corto (ej 'Conv Rate cae fuerte')
    - 'desc':   string (ej 'De 1.55% a 1.38% — caída concentrada en Wyndham...')
"""

def render_finding(idx, finding, accent_color):
    n_str = str(idx + 1) + '.'
    valor = finding.get('numero','')
    titulo = finding.get('titulo','')
    desc = finding.get('desc','')
    return f'''<li style="display:flex;gap:10px;align-items:baseline;font-size:12.5px;line-height:1.55;color:var(--ink-soft);margin-bottom:14px;">
<span style="flex-shrink:0;display:inline-block;width:18px;font-weight:700;color:var(--ink-muted);font-size:11px;text-align:right;">{n_str}</span>
<span style="flex-shrink:0;display:inline-block;min-width:55px;font-weight:700;color:{accent_color};font-size:13px;text-align:right;letter-spacing:-.01em;font-variant-numeric:tabular-nums;">{valor}</span>
<span style="flex:1;"><strong style="color:var(--ink);">{titulo}</strong> {desc}</span>
</li>'''

def render_resumen_ejecutivo(findings, accent_color, scope='global', header_title='Resumen Ejecutivo'):
    """
    findings: lista de 10 dicts.
    accent_color: '#EA0074' (RND) o '#5C469C' (CR).
    scope: 'global' o 'canasta' (para ajustar margin-top).
    """
    margin_top = '64px' if scope == 'global' else '32px'
    
    col1_items = ''.join(render_finding(i, f, accent_color) for i, f in enumerate(findings[:5]))
    col2_items = ''.join(render_finding(i+5, f, accent_color) for i, f in enumerate(findings[5:10]))
    
    return f'''<!-- Resumen Ejecutivo · header fuera del card · estilo template -->
<div style="margin-top:{margin_top};font-size:11px;color:var(--ink);font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
<span style="color:{accent_color};">🎯</span><span>{header_title}</span>
</div>
<div style="padding:28px 32px;background:var(--paper-soft);border:1px solid var(--rule);border-top:3px solid #161616;border-radius:6px;margin-bottom:24px;">
<div class="exec-2cols" style="display:grid;grid-template-columns:1fr 1fr;gap:14px 28px;">
<ol style="list-style:none;padding:0;margin:0;">
{col1_items}
</ol>
<ol style="list-style:none;padding:0;margin:0;">
{col2_items}
</ol>
</div>
</div>'''
