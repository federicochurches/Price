"""
historico_data.py · Datos históricos reales W16-W22 para módulos de evolución histórica.

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W16, W17, W18, W19, W20, W21] (6 valores)
    
    El 7° valor (semana actual del reporte, W22) lo agrega el render dinámicamente
    desde el pickle vigente.

    Con W23 se alcanza la ventana objetivo de 8 semanas:
    arrays pasarán a 7 valores estáticos + 1 dinámico.

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

Para extender (W23+): agregar el valor W22 a cada array.
Para W24+: descartar W16 y mantener ventana de 8 semanas móvil.

Notas sobre W16:
    - Datos globales: extraídos del historial de sesiones (pickles reales).
    - Datos por canasta: estimados con ratios W16/W17 de referencia (no hay pickle W16
      individual por canasta). Margen de error ~1-2%; reemplazar cuando estén disponibles.
"""

# Semanas que cubre la serie histórica (ventana de 7 semanas → 8 con W23).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20', 'W21', 'W22', 'W23']

# Datos reales extraídos de los pickles W16-W21 (Mayo–Junio 2026)
# W16 por canasta: estimado con ratios W16/W17 global (global W16=93.27 vs W17=93.58 → ratio ≈0.9967)
HIST_DATA = {
    'cr': {
        'eficacia': {
            #          W16     W17     W18     W19     W20     W21
            'global': [93.27,  93.58,  93.71,  93.30,  93.34,  93.15,  94.21],
            'op':     [93.72,  94.03,  94.25,  93.87,  93.96,  93.81,  94.68],
            'cug':    [92.38,  92.69,  92.65,  92.54,  92.28,  92.11,  92.74],
            'b2c':    [91.82,  92.12,  92.18,  91.49,  92.01,  91.88,  92.41],
        },
        'convrate': {
            #          W16    W17    W18    W19    W20    W21
            'global': [1.29,  1.15,  1.02,  1.14,  1.63,  1.57,  1.00],
            'op':     [1.12,  1.00,  0.94,  1.06,  1.59,  1.52,  0.92],
            'cug':    [2.65,  2.38,  1.82,  2.07,  2.90,  2.74,  2.12],
            'b2c':    [0.33,  0.30,  0.27,  0.25,  0.39,  0.36,  0.28],
        },
    },
    'rnd': {
        'nodispo': {
            #          W16    W17    W18    W19    W20    W21
            'global': [3.69,  3.63,  2.84,  2.31,  2.59,  2.63,  2.61],
            'op':     [3.24,  3.18,  2.62,  1.93,  2.24,  2.28,  2.26],
            'cug':    [4.40,  4.34,  3.07,  2.73,  2.82,  2.89,  2.87],
            'b2c':    [4.55,  4.48,  3.68,  3.36,  3.31,  3.38,  3.36],
        },
        'ipm': {
            #           W16     W17     W18     W19     W20     W21
            'global': [661.0,  574.0,  524.0,  499.0,  677.0,  834.0,  653.0],
            'op':     [604.0,  523.0,  534.0,  479.0,  688.0,  851.0,  667.0],
            'cug':    [998.0,  866.0,  659.0,  656.0,  787.0,  962.0,  952.0],
            'b2c':    [211.0,  183.0,  206.0,  188.0,  248.0,  301.0,  298.0],
        },
    },

    'bk': {
        'bookability': {
            # Bookability global ponderada (%) W16-W22 — W23 se agrega dinámicamente
            'global': [98.28, 98.44, 98.22, 98.26, 98.17, 98.25, 98.40],
        },
    },

}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W16-W{current} (7 valores) para un scope.
    
    reporte    : 'cr' | 'rnd'
    metrica    : 'eficacia' | 'convrate' (CR)  o  'nodispo' | 'ipm' (RND)
    scope      : 'global' | 'op' | 'cug' | 'b2c'
    val_actual : valor W{current} (se agrega al final de la serie histórica)
    
    Si scope no está en HIST_DATA, devuelve serie de 7 valores con val_actual repetido.
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        return [val_actual] * len(SEMANAS)
    # base tiene 7 valores (W16-W22). val_actual es W23.
    return list(base) + [val_actual]
