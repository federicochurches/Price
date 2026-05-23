"""
historico_data.py · Datos históricos reales W16-W20 para módulos de evolución histórica.

Generado automáticamente desde los pickles cr_w{16-20}_data.pkl y rnd_w{16-20}_data.pkl
(extracción de KPIs globales por canasta).

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W16, W17, W18, W19] (4 valores)
    
    El 5° valor (semana actual del reporte, ej. W20) lo agrega el render dinámicamente
    desde el pickle vigente.

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

Para extender (W21+), agregar el valor a cada array y descartar el W16 más antiguo
(mantener ventana de 5 semanas móvil).
"""

# Semanas que cubre la serie histórica (ventana de 5 semanas).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']

# Datos reales extraídos de los pickles W16-W20 (Mayo 2026)
HIST_DATA = {
    'cr': {
        'eficacia': {
            'global': [93.27, 93.58, 93.71, 93.3],
            'op': [93.67, 94.03, 94.25, 93.87],
            'cug': [91.5, 92.69, 92.65, 92.54],
            'b2c': [93.22, 92.12, 92.18, 91.49],
        },
        'convrate': {
            'global': [1.29, 1.15, 1.02, 1.14],
            'op': [1.11, 1.0, 0.94, 1.06],
            'cug': [3.0, 2.38, 1.82, 2.07],
            'b2c': [0.21, 0.3, 0.27, 0.25],
        },
    },
    'rnd': {
        'nodispo': {
            'global': [3.69, 3.63, 2.84, 2.31],
            'op': [3.12, 3.18, 2.62, 1.93],
            'cug': [4.76, 4.34, 3.07, 2.73],
            'b2c': [4.12, 4.48, 3.68, 3.36],
        },
        'ipm': {
            'global': [661.0, 574.0, 524.0, 499.0],
            'op': [585.0, 523.0, 534.0, 479.0],
            'cug': [1101.0, 866.0, 659.0, 656.0],
            'b2c': [170.0, 183.0, 206.0, 188.0],
        },
    },
}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W16-W{current} (5 valores) para un scope.
    
    reporte    : 'cr' | 'rnd'
    metrica    : 'eficacia' | 'convrate' (CR)  o  'nodispo' | 'ipm' (RND)
    scope      : 'global' | 'op' | 'cug' | 'b2c'  (o nombre específico de hotel/dim si está)
    val_actual : valor W{current} (se agrega al final de la serie histórica)
    
    Si scope no está en HIST_DATA, devuelve serie de 5 valores con `val_actual` repetido
    (placeholder hasta tener datos por hotel/dim).
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        # Fallback: scope desconocido (ej. hotel específico) — repetir val_actual
        return [val_actual] * len(SEMANAS)
    # base tiene W16, W17, W18, W19. val_actual es W20.
    return list(base) + [val_actual]
