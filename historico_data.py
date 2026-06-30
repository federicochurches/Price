"""
historico_data.py · Datos históricos reales W18-W24 para módulos de evolución histórica.

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W18, W19, W20, W21, W22, W23, W24] (7 valores)
    
    El 8° valor (semana actual del reporte, W25) lo agrega el render dinámicamente
    desde el pickle vigente.

    Ventana móvil de 8 semanas: W18–W25 (se descartó W17 al entrar W25).

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

Para extender (W26+): descartar W18 y agregar W25 a cada array.
"""

# Semanas que cubre la serie histórica (ventana móvil de 8 semanas).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ["W19", "W20", "W21", "W22", "W23", "W24", "W25", "W26"]

# Datos reales extraídos de los pickles W18-W24 (Mayo–Junio 2026)
# W24 global: valores P80-filtrados del run W24 real (PROMPT_CORE)
# W24 per-canasta: extraídos del pickle W25 (M[canasta_w24])
HIST_DATA = {
    'cr': {
        'eficacia': {
            'global': [93.3, 93.34, 93.15, 94.21, 94.53, 95.57, 95.68],
            'op': [93.87, 93.96, 93.81, 94.68, 94.04, 95.3, 95.15],
            'cug': [92.54, 92.28, 92.11, 92.74, 95.04, 96.12, 96.04],
            'b2c': [91.49, 92.01, 91.88, 92.41, 94.14, 95.81, 95.53],
        },
        'convrate': {
            'global': [1.14, 1.63, 1.57, 1.0, 0.84, 0.82, 0.75],
            'op': [1.06, 1.59, 1.52, 0.92, 0.63, 0.64, 0.63],
            'cug': [2.07, 2.9, 2.74, 2.12, 1.23, 1.24, 1.01],
            'b2c': [0.25, 0.39, 0.36, 0.28, 0.18, 0.15, 0.14],
        },
    },
    'rnd': {
        'nodispo': {
            'global': [2.31, 2.59, 2.63, 2.61, 2.87, 3.04, 3.39],
            'op': [1.93, 2.24, 2.28, 2.26, 3.02, 3.22, 3.34],
            'cug': [2.73, 2.82, 2.89, 2.87, 2.6, 2.79, 3.32],
            'b2c': [3.36, 3.31, 3.38, 3.36, 3.35, 3.28, 3.78],
        },
        'ipm': {
            'global': [499.0, 677.0, 834.0, 653.0, 534.0, 611.0, 834.0],
            'op': [479.0, 688.0, 851.0, 667.0, 334.0, 395.0, 566.0],
            'cug': [656.0, 787.0, 962.0, 952.0, 872.0, 1041.0, 1305.0],
            'b2c': [188.0, 248.0, 301.0, 298.0, 228.0, 254.0, 378.0],
        },
    },
    'bk': {
        'bookability': {
            'global': [98.26, 98.17, 98.25, 98.4, 98.43, 98.67, 98.42],
        },
    },
}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W18-W{current} (8 valores) para un scope.
    
    reporte    : 'cr' | 'rnd'
    metrica    : 'eficacia' | 'convrate' (CR)  o  'nodispo' | 'ipm' (RND)
    scope      : 'global' | 'op' | 'cug' | 'b2c'
    val_actual : valor W{current} (se agrega al final de la serie histórica)
    
    Si scope no está en HIST_DATA, devuelve serie de 8 valores con val_actual repetido.
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        return [val_actual] * len(SEMANAS)
    # base tiene 7 valores (W18-W24). val_actual es W25.
    return list(base) + [val_actual]
