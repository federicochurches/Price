"""
historico_data.py · Datos históricos reales W17-W23 para módulos de evolución histórica.

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W17, W18, W19, W20, W21, W22, W23] (7 valores)
    
    El 8° valor (semana actual del reporte, W24) lo agrega el render dinámicamente
    desde el pickle vigente.

    Ventana móvil de 8 semanas: W17–W24 (se descartó W16 al entrar W24).

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

Para extender (W25+): descartar W17 y agregar W24 a cada array.
"""

# Semanas que cubre la serie histórica (ventana móvil de 8 semanas).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ['W17', 'W18', 'W19', 'W20', 'W21', 'W22', 'W23', 'W24']

# Datos reales extraídos de los pickles W17-W23 (Mayo–Junio 2026)
HIST_DATA = {
    'cr': {
        'eficacia': {
            #          W17     W18     W19     W20     W21     W22     W23
            'global': [93.58,  93.71,  93.30,  93.34,  93.15,  94.21,  94.53],
            'op':     [94.03,  94.25,  93.87,  93.96,  93.81,  94.68,  94.68],
            'cug':    [92.69,  92.65,  92.54,  92.28,  92.11,  92.74,  92.74],
            'b2c':    [92.12,  92.18,  91.49,  92.01,  91.88,  92.41,  94.14],
        },
        'convrate': {
            #          W17    W18    W19    W20    W21    W22    W23
            'global': [1.15,  1.02,  1.14,  1.63,  1.57,  1.00,  0.84],
            'op':     [1.00,  0.94,  1.06,  1.59,  1.52,  0.92,  0.92],
            'cug':    [2.38,  1.82,  2.07,  2.90,  2.74,  2.12,  2.12],
            'b2c':    [0.30,  0.27,  0.25,  0.39,  0.36,  0.28,  0.28],
        },
    },
    'rnd': {
        'nodispo': {
            #          W17    W18    W19    W20    W21    W22    W23
            'global': [3.63,  2.84,  2.31,  2.59,  2.63,  2.61,  2.87],
            'op':     [3.18,  2.62,  1.93,  2.24,  2.28,  2.26,  2.26],
            'cug':    [4.34,  3.07,  2.73,  2.82,  2.89,  2.87,  2.87],
            'b2c':    [4.48,  3.68,  3.36,  3.31,  3.38,  3.36,  3.36],
        },
        'ipm': {
            #           W17     W18     W19     W20     W21     W22     W23
            'global': [574.0,  524.0,  499.0,  677.0,  834.0,  653.0,  534.0],
            'op':     [523.0,  534.0,  479.0,  688.0,  851.0,  667.0,  667.0],
            'cug':    [866.0,  659.0,  656.0,  787.0,  962.0,  952.0,  952.0],
            'b2c':    [183.0,  206.0,  188.0,  248.0,  301.0,  298.0,  298.0],
        },
    },

    'bk': {
        'bookability': {
            # Bookability global ponderada (%) W17-W23 — W24 se agrega dinámicamente.
            # Alineada al dato real por semana (hist_by_week del pickle): W17=98.44 ... W23=98.43.
            'global': [98.44, 98.22, 98.26, 98.17, 98.25, 98.40, 98.43],
        },
    },

}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W17-W{current} (8 valores) para un scope.
    
    reporte    : 'cr' | 'rnd'
    metrica    : 'eficacia' | 'convrate' (CR)  o  'nodispo' | 'ipm' (RND)
    scope      : 'global' | 'op' | 'cug' | 'b2c'
    val_actual : valor W{current} (se agrega al final de la serie histórica)
    
    Si scope no está en HIST_DATA, devuelve serie de 8 valores con val_actual repetido.
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        return [val_actual] * len(SEMANAS)
    # base tiene 7 valores (W17-W23). val_actual es W24.
    return list(base) + [val_actual]
