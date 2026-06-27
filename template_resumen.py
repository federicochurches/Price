"""
Helper · Resumen Ejecutivo · Nuevo diseño v9 (W26+)

Estructura:
- Header overline pequeño + título (fuera del card)
- Card con border-top 3px acento, fondo blanco, padding 0 14px
- Lista vertical: cada finding con círculo numerado + título 13px bold
  + valor métrico como badge derecho + descripción/drilldown sangrado

API:
  render_resumen_ejecutivo(findings, accent_color, header_title='Resumen Ejecutivo')

  findings: list of dicts, cada uno con:
    - 'numero': string métrico (ej '−11.1%', '93.9%') → badge derecho
    - 'titulo': string del finding (ej 'Conv Rate cae fuerte')
    - 'desc':   string descriptivo / drilldown HTML
"""

def render_finding(idx, finding, accent_color):
    num     = idx + 1
    numero  = finding.get('numero', '')
    titulo  = finding.get('titulo', '') or finding.get('n', '')
    desc    = finding.get('desc', '')   or finding.get('d', '')
    is_last = finding.get('_last', False)
    border_b = 'none' if is_last else '1px dashed var(--rule-soft)'

    badge_html = (
        f'<span style="flex-shrink:0;align-self:flex-start;margin-left:10px;'
        f'margin-top:2px;font-size:9px;font-weight:700;color:{accent_color};'
        f'background:var(--paper-soft);padding:2px 8px;border-radius:2px;'
        f'white-space:nowrap;">{numero}</span>'
    ) if numero else ''

    desc_html = (
        f'<div style="padding:7px 0 0 32px;">{desc}</div>'
    ) if desc else ''

    return (
        f'<li style="padding:11px 0;border-bottom:{border_b};list-style:none;">'
        f'<div style="display:flex;align-items:flex-start;gap:10px;">'
        f'<span style="flex-shrink:0;width:22px;height:22px;border-radius:50%;'
        f'background:{accent_color};color:#fff;font-size:10px;font-weight:700;'
        f'display:inline-flex;align-items:center;justify-content:center;margin-top:1px;">{num}</span>'
        f'<span style="font-size:13px;font-weight:700;color:var(--ink);line-height:1.35;flex:1;">{titulo}</span>'
        f'{badge_html}'
        f'</div>'
        f'{desc_html}'
        f'</li>'
    )

def render_resumen_ejecutivo(findings, accent_color, scope='global', header_title='Resumen Ejecutivo'):
    """
    findings: lista de dicts con 'numero', 'titulo', 'desc'.
    accent_color: '#EA0074' (RND) o '#5C469C' (CR).
    scope: 'global' o 'canasta'.
    """
    margin_top = '24px' if scope == 'global' else '16px'

    # Marcar el último para quitar el border-bottom
    items_tagged = []
    for i, f in enumerate(findings):
        tagged = dict(f)
        tagged['_last'] = (i == len(findings) - 1)
        items_tagged.append(tagged)

    items_html = ''.join(render_finding(i, f, accent_color) for i, f in enumerate(items_tagged))

    return (
        f'<!-- Resumen Ejecutivo · diseño v9 -->\n'
        f'<div style="margin-top:{margin_top};font-size:11px;color:var(--ink);font-weight:700;'
        f'letter-spacing:.10em;text-transform:uppercase;margin-bottom:6px;">'
        f'{header_title}</div>\n'
        f'<ul style="list-style:none;padding:0 14px;margin:0 0 18px;background:#fff;'
        f'border:1px solid var(--rule);border-top:3px solid {accent_color};border-radius:3px;">\n'
        f'{items_html}'
        f'</ul>'
    )
