"""
historico_data.py · Datos históricos reales W20-W26 para módulos de evolución histórica.

Estructura:
    HIST_DATA[reporte][metrica][scope] = [W20, W21, W22, W23, W24, W25, W26] (7 valores)

    El 8° valor (semana actual del reporte, W27) lo agrega el render dinámicamente
    desde el pickle vigente.

    Ventana móvil de 8 semanas: W20–W27 (se descartaron W18/W19 al entrar W27).

Cobertura por scope:
    - 'global' : KPI agregado del P80 completo
    - 'op'     : Canasta B2B Opaco
    - 'cug'    : Canasta CUG
    - 'b2c'    : Canasta B2C

IMPORTANTE (W27): IPM eliminado de RND — ya no se reporta en Excels ni en HTML.
No usar 'ipm' como key de HIST_DATA['rnd']; RND solo expone 'nodispo'.

Fuente de los valores agregados:
    - CR eficacia/convrate W25-W26: recalculados desde Dataset_CheckRates_W25/W26.xlsx
      (Eficacia = Successful UniqueChkRts / CheckRates Únicos · ConvRate = Bookings / CheckRates Únicos ·
      filtro MIN_CR=100 por fila).
    - RND nodispo W25: recalculado desde Dataset_RatesNoDispo_W25.xlsx (MIN_TRAFICO=50.000 canónico).
    - RND nodispo W26: recalculado desde el dataset CORREGIDO de tráfico (segunda entrega) —
      el primer dataset W26 traía el tráfico colapsado ~26x (anomalía real de esa semana) y
      requería override MIN_TRAFICO=2000; con el dataset corregido corre con el umbral canónico
      50.000 sin overrides. Valor global 2.87% (no 2.67% del cálculo con override, descartado).
    - BK bookability W20-W26: recalculado desde Dataset_bookability_W27.xlsx (acumulado, trae
      Semana 20-28), ponderado sum(Bookability×Books)/sum(Books), filtro MIN_BOOKS=5.
      Reemplaza los valores previos de HIST_DATA['bk'] (metodología distinta/desactualizada).

Para extender (W27+): descartar W20 y agregar W27 a cada array (CR y RND); BK ídem con el
próximo acumulado.
"""

# Semanas que cubre la serie histórica (ventana móvil de 8 semanas).
# La última semana del reporte se agrega dinámicamente en runtime.
SEMANAS = ["W20", "W21", "W22", "W23", "W24", "W25", "W26", "W27"]

HIST_DATA = {
    'cr': {
        'eficacia': {
            'global': [93.34, 93.15, 94.21, 94.53, 95.57, 95.68, 95.13],
            'op':     [93.96, 93.81, 94.68, 94.04, 95.3, 95.15, 94.41],
            'cug':    [92.28, 92.11, 92.74, 95.04, 96.12, 96.04, 95.5],
            'b2c':    [92.01, 91.88, 92.41, 94.14, 95.81, 95.53, 94.99],
        },
        'convrate': {
            'global': [1.63, 1.57, 1.0, 0.84, 0.82, 0.75, 1.01],
            'op':     [1.59, 1.52, 0.92, 0.63, 0.64, 0.63, 0.75],
            'cug':    [2.9, 2.74, 2.12, 1.23, 1.24, 1.01, 1.36],
            'b2c':    [0.39, 0.36, 0.28, 0.18, 0.15, 0.14, 0.19],
        },
    },
    'rnd': {
        'nodispo': {
            'global': [2.59, 2.63, 2.61, 2.87, 3.04, 3.39, 2.87],
            'op':     [2.24, 2.28, 2.26, 3.02, 3.22, 3.34, 2.87],
            'cug':    [2.82, 2.89, 2.87, 2.6, 2.79, 3.32, 2.94],
            'b2c':    [3.31, 3.38, 3.36, 3.35, 3.28, 3.78, 2.61],
        },
        # 'ipm' eliminado W27 — ya no se reporta.
    },
    'bk': {
        'bookability': {
            'global': [98.63, 98.97, 98.96, 99.06, 99.35, 99.18, 99.37],
        },
    },
}


def get_serie(reporte, metrica, scope, val_actual):
    '''Devuelve la serie completa W20-W{current} (8 valores) para un scope.

    reporte    : 'cr' | 'rnd' | 'bk'
    metrica    : 'eficacia' | 'convrate' (CR)  ·  'nodispo' (RND)  ·  'bookability' (BK)
    scope      : 'global' | 'op' | 'cug' | 'b2c'
    val_actual : valor W{current} (se agrega al final de la serie histórica)

    Si scope no está en HIST_DATA, devuelve serie de 8 valores con val_actual repetido.
    '''
    base = HIST_DATA.get(reporte, {}).get(metrica, {}).get(scope)
    if base is None:
        return [val_actual] * len(SEMANAS)
    # base tiene 7 valores (W20-W26). val_actual es W27.
    return list(base) + [val_actual]
