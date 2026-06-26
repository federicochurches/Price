"""
engine.py · Bandas D · Supply Analytics W18
Sistema de bandas: NoDispo, Eficacia, ConvRate, IPM (antes RPM)

W26+: Bandas diferenciadas por tier de destino (PRIMARIO / SECUNDARIO / TERCIARIO).
Funciones tiered: banda_nodispo_tiered(), banda_eficacia_tiered()
Funciones planas (sin tier): banda_nodispo(), banda_eficacia() — aplican rangos Secundario,
  usadas como fallback y en dimensiones distintas a Destino (corp, canal, país).
"""

import os
import re
import csv

# ── Carga del mapa de clasificación de destinos ─────────────────
# dest_classification.csv vive en la raíz del repo junto a engine.py
_DEST_TIER_MAP = {}  # nombre_normalizado → 'PRIMARIO'|'SECUNDARIO'|'TERCIARIO'

def _normalize_dest(name):
    """Normaliza el nombre de un destino para el join."""
    n = name.strip()
    # Quitar "(and vicinity), XX, US" y variantes
    n = re.sub(r'\s*\(and vicinity\),?\s*[\w\s]*,?\s*US$', '', n, flags=re.IGNORECASE)
    # Quitar sufijo " Area"
    n = re.sub(r'\s+Area$', '', n, flags=re.IGNORECASE)
    # Quitar sufijo de estado ", XX, US"
    n = re.sub(r',\s*\w{2},?\s*US$', '', n, flags=re.IGNORECASE)
    return n.strip().lower()

def _load_dest_tier_map():
    """Carga dest_classification.csv una sola vez en _DEST_TIER_MAP."""
    global _DEST_TIER_MAP
    if _DEST_TIER_MAP:
        return
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'dest_classification.csv')
    if not os.path.exists(csv_path):
        return
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            key = _normalize_dest(row['DestinoNombre'])
            _DEST_TIER_MAP[key] = row['DestinoClasificacion'].strip().upper()

def get_dest_tier(destino):
    """Devuelve el tier de un destino: 'PRIMARIO', 'SECUNDARIO' o 'TERCIARIO'.
    Si no hay match en el mapa, devuelve 'TERCIARIO' (más permisivo = menos ruido).
    """
    _load_dest_tier_map()
    key = _normalize_dest(str(destino))
    return _DEST_TIER_MAP.get(key, 'TERCIARIO')

# ── Bandas planas (sin tier) — rangos Secundario ────────────────
# Usadas en dimensiones distintas a Destino (corp, canal, país global)
# y como fallback donde no aplica la diferenciación.

def banda_nodispo(pct):
    """% NoDispo · rangos Secundario (comportamiento histórico sin cambios)."""
    if pct > 0.60: return 'Súper Crítica'
    if pct > 0.20: return 'Crítica'
    if pct > 0.05: return 'Revisar'
    if pct > 0.03: return 'Aceptable'
    return 'Exitosa'

def banda_eficacia(ef):
    """% Eficacia · rangos Secundario (comportamiento histórico sin cambios)."""
    if ef < 0.60: return 'Súper Crítica'
    if ef < 0.85: return 'Crítica'
    if ef < 0.93: return 'Revisar'
    if ef < 0.97: return 'Aceptable'
    return 'Exitosa'

# ── Bandas tiered por destino ────────────────────────────────────

def banda_nodispo_tiered(pct, destino):
    """% NoDispo con rangos diferenciados por tier de destino.

    Primario  : Exitosa <2% · Aceptable 2-4% · Revisar 4-15% · Crítica 15-50% · SC >50%
    Secundario: Exitosa <3% · Aceptable 3-5% · Revisar 5-20% · Crítica 20-60% · SC >60%
    Terciario : Exitosa <5% · Aceptable 5-10%· Revisar 10-25%· Crítica 25-70% · SC >70%
    """
    tier = get_dest_tier(destino)
    if tier == 'PRIMARIO':
        if pct > 0.50: return 'Súper Crítica'
        if pct > 0.15: return 'Crítica'
        if pct > 0.04: return 'Revisar'
        if pct > 0.02: return 'Aceptable'
        return 'Exitosa'
    elif tier == 'TERCIARIO':
        if pct > 0.70: return 'Súper Crítica'
        if pct > 0.25: return 'Crítica'
        if pct > 0.10: return 'Revisar'
        if pct > 0.05: return 'Aceptable'
        return 'Exitosa'
    else:  # SECUNDARIO — rangos históricos
        if pct > 0.60: return 'Súper Crítica'
        if pct > 0.20: return 'Crítica'
        if pct > 0.05: return 'Revisar'
        if pct > 0.03: return 'Aceptable'
        return 'Exitosa'

def banda_eficacia_tiered(ef, destino):
    """% Eficacia con rangos diferenciados por tier de destino.

    Primario  : Exitosa ≥98% · Aceptable 95-98% · Revisar 88-95% · Crítica 65-88% · SC <65%
    Secundario: Exitosa ≥97% · Aceptable 93-97% · Revisar 85-93% · Crítica 60-85% · SC <60%
    Terciario : Exitosa ≥95% · Aceptable 90-95% · Revisar 80-90% · Crítica 55-80% · SC <55%
    """
    tier = get_dest_tier(destino)
    if tier == 'PRIMARIO':
        if ef < 0.65: return 'Súper Crítica'
        if ef < 0.88: return 'Crítica'
        if ef < 0.95: return 'Revisar'
        if ef < 0.98: return 'Aceptable'
        return 'Exitosa'
    elif tier == 'TERCIARIO':
        if ef < 0.55: return 'Súper Crítica'
        if ef < 0.80: return 'Crítica'
        if ef < 0.90: return 'Revisar'
        if ef < 0.95: return 'Aceptable'
        return 'Exitosa'
    else:  # SECUNDARIO — rangos históricos
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
    Bandas correctas:
    - Sin Conversión: BKGS=0
    - Crítica: < $199
    - Revisar: $200–$499
    - Aceptable: $500–$649
    - Exitosa: ≥ $650
    """
    if bookings == 0: return 'Sin Conversión'
    if rpm < 199: return 'Crítica'
    if rpm < 500: return 'Revisar'
    if rpm < 650: return 'Aceptable'
    return 'Exitosa'

# Alias para compatibilidad
banda_ipm = banda_rpm
