"""
engine.py · Bandas D · Supply Analytics W18
Sistema de bandas: NoDispo, Eficacia, ConvRate, IPM (antes RPM)
"""

def banda_nodispo(pct):
    """% NoDispo · 5 niveles."""
    if pct > 0.60: return 'Súper Crítica'
    if pct > 0.20: return 'Crítica'
    if pct > 0.05: return 'Revisar'
    if pct > 0.03: return 'Aceptable'
    return 'Exitosa'

def banda_eficacia(ef):
    """% Eficacia · 5 niveles."""
    if ef < 0.60: return 'Súper Crítica'
    if ef < 0.85: return 'Crítica'
    if ef < 0.93: return 'Revisar'
    if ef < 0.97: return 'Aceptable'
    return 'Exitosa'

def banda_convrate(cv, bookings=1):
    """Conv Rate · sistema D · Sin Conversión separada."""
    if bookings == 0: return 'Sin Conversión'
    if cv < 0.008: return 'Crítica'
    if cv < 0.015: return 'Revisar'
    if cv < 0.025: return 'Aceptable'
    return 'Exitosa'

def banda_rpm(rpm, bookings=1):
    """IPM (antes RPM) · sistema D · Sin Conversión separada.
    Bandas (target ≥ $650):
    - Sin Conversión: BKGS=0
    - Crítica: < $200
    - Revisar: $200–$650
    - Exitosa: ≥ $650
    """
    if bookings == 0: return 'Sin Conversión'
    if rpm < 200: return 'Crítica'
    if rpm < 650: return 'Revisar'
    return 'Exitosa'

# Alias para compatibilidad
banda_ipm = banda_rpm
