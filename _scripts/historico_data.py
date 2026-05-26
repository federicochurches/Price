"""
historico_data.py · Datos históricos reales W16-W21 para módulos de evolución histórica.

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W17, W18, W19, W20] (4 valores)
    
    El 5° valor (semana actual del reporte, W21) lo agrega el render dinámicamente
    desde el pickle vigente.

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

Para extender (W22+): agregar el valor W21 a cada array y descartar W17
(mantener ventana de 5 semanas móvil).
"""

# Semanas que cubre la serie histórica (ventana de 5 semanas).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ['W17', 'W18', 'W19', 'W20', 'W21']

# Datos reales extraídos de los pickles W17-W21 (Mayo 2026)
HIST_DATA = {
    'cr': {
        'eficacia': {
            'global': [93.58, 93.71, 93.3,  93.34],
            'op':     [94.03, 94.25, 93.87, 93.96],
            'cug':    [92.69, 92.65, 92.54, 92.28],
            'b2c':    [92.12, 92.18, 91.49, 92.01],
        },
        'convrate': {
            'global': [1.15, 1.02, 1.14, 1.63],
            'op':     [1.0,  0.94, 1.06, 1.59],
            'cug':    [2.38, 1.82, 2.07, 2.90],
            'b2c':    [0.3,  0.27, 0.25, 0.39],
        },
    },
    'rnd': {
        'nodispo': {
            'global': [3.63, 2.84, 2.31, 2.59],
            'op':     [3.18, 2.62, 1.93, 2.24],
            'cug':    [4.34, 3.07, 2.73, 2.82],
            'b2c':    [4.48, 3.68, 3.36, 3.31],
        },
        'ipm': {
            'global': [574.0, 524.0, 499.0, 677.0],
            'op':     [523.0, 534.0, 479.0, 688.0],
            'cug':    [866.0, 659.0, 656.0, 787.0],
            'b2c':    [183.0, 206.0, 188.0, 248.0],
        },
    },
}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W17-W{current} (5 valores) para un scope.
    
    reporte    : 'cr' | 'rnd'
    metrica    : 'eficacia' | 'convrate' (CR)  o  'nodispo' | 'ipm' (RND)
    scope      : 'global' | 'op' | 'cug' | 'b2c'
    val_actual : valor W{current} (se agrega al final de la serie histórica)
    
    Si scope no está en HIST_DATA, devuelve serie de 5 valores con val_actual repetido.
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        return [val_actual] * len(SEMANAS)
    # base tiene W17, W18, W19, W20. val_actual es W21.
    return list(base) + [val_actual]
