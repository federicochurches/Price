"""
CATALOGO DE AREAS ACCOUNTABLE · v2 (post W18 — confirmado por usuario)

Estructura: 4 áreas accountable definidas por el negocio.
"""

AREAS_CATALOGO = {
    'supply_optimization': {
        'label': 'Supply Optimization',
        'descripcion': 'Diagnóstico técnico interno · escalamiento Súper Críticos · saneamiento severity · BI/dashboards',
    },
    'supply_optimization_tps': {
        'label': 'Supply Optimization / TPS',
        'descripcion': 'Diagnóstico Sin Conversión · mapping/paridad/inventario · auditoría connectivity Third Party',
    },
    'supply_comercial_supply_optimization': {
        'label': 'Supply Comercial / Supply Optimization',
        'descripcion': 'Casos críticos volumen · escalamiento KAM · cohorte Sin Conv estructural (proyecto trimestral)',
    },
    'supply_comercial_wholesale': {
        'label': 'Supply Comercial / Wholesale',
        'descripcion': 'RPM/GBM/ConvRate por canasta · pricing · SLAs corporativos · auditoría comercial canales',
    },
}

if __name__ == '__main__':
    for k, v in AREAS_CATALOGO.items():
        print(f"· {v['label']}")
        print(f"    {v['descripcion']}\n")
