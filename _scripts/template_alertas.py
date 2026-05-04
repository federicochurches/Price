"""
Helper · Alertas Críticas (3 cards: Hoteles · Destinos · Channels/Corp)
siguiendo estructura literal del template.

Cada card tiene:
- Header con icono + nombre de categoría + accent color
- 2 sub-celdas: una con badge "Eficacia"/"% Nodispo" y otra con badge "Conv Rate"/"RPM"
- Cada sub-celda: badge tipo + nombre del hotel/destino/channel + valor grande

API:
  render_alertas_criticas(scope_text, accent_color, dim1, dim2, dim3)
  
  scope_text: 'Casos Críticos de la Semana' o 'Casos Críticos · Canasta B2C'
  dim1, dim2, dim3: dicts con clave 'titulo' (Hoteles/Destinos/etc) e 'icon' y dos sub-celdas.
"""

def render_alert_subcell(badge_label, badge_color, badge_bg, name, value, value_color):
    return f'''<div style="background:var(--paper);padding:8px 10px;border-radius:3px;">
<div style="font-size:9px;font-weight:700;color:{badge_color};background:{badge_bg};padding:2px 5px;border-radius:2px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;">{badge_label}</div>
<div style="font-size:11px;font-weight:700;color:var(--ink);line-height:1.2;margin-top:6px;">{name}</div>
<div style="font-size:18px;font-weight:600;color:{value_color};margin-top:6px;letter-spacing:-.02em;line-height:1;">{value}</div>
</div>'''

def render_alert_card(title, icon, accent_color, subcell1, subcell2):
    """subcell1, subcell2: HTML strings de render_alert_subcell."""
    return f'''<div style="background:var(--paper-soft);border-radius:4px;padding:10px;border-top:3px solid {accent_color};">
<div style="font-size:10px;font-weight:700;color:{accent_color};letter-spacing:.10em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
<span>{icon}</span><span>{title}</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
{subcell1}
{subcell2}
</div>
</div>'''

def render_alertas_block(scope_text, accent_color, card_hoteles, card_destinos, card_corp_or_channel):
    """
    accent_color: color del reporte (#EA0074 RND, #5C469C CR)
    card_*: HTML strings de render_alert_card
    """
    return f'''<div class="alerts-block" style="margin:0 0 24px;">
<div style="font-size:11px;color:{accent_color};font-weight:700;letter-spacing:.10em;text-transform:uppercase;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
<span>📍</span><span>{scope_text}</span>
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
{card_hoteles}
{card_destinos}
{card_corp_or_channel}
</div>
</div>'''
