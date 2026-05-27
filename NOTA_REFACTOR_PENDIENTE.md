# 🔧 REFACTOR PENDIENTE · Sesión W21-post3

**Fecha:** 2026-05-26  
**Prioridad:** Alta — ejecutar al inicio de la sesión W22, antes de recibir datos

---

## Problema

El pipeline tiene código duplicado entre CR y RND, y entre cards KPI globales y cards AR. Cualquier cambio visual (formato tráfico, numeración, top N, etc.) hay que aplicarlo en hasta 4 lugares distintos. Esta sesión lo evidenció: el fix de `ri<5→ri<10` tuvo que aplicarse en el searchbox, en los 4 loops de tab panels de Python, y en el JS.

---

## Plan de refactor

### 1. Extraer loop de tab panels a `render_helpers.py`

El bloque `for i, r in df_t.iterrows()` con la lógica de `_cls`, `_row`, `top5/rest` se repite **4 veces** (Eficacia, ConvRate en CR · NoDispo, IPM en RND). Extraer a:

```python
# render_helpers.py
def build_kpi_tab_panel(df_t, t_key, cols_config):
    """
    cols_config = {
      'val_col': 'Eficacia',          # columna de la métrica principal
      'val_fmt': fmt_pct2,            # función de formato
      'banda_fn': banda_eficacia,     # función de banda
      'traf_col': 'CR_Unicos',        # columna de tráfico
      'wow_col': 'Eficacia_WoW_pp',  # columna de WoW
      'grid': 'minmax(0,1fr) 80px …',# grid CSS
      'headers': ['Severity','Tráfico','WoW','Eficacia','WoW'],
      'top_n': 10,                    # rows visibles
    }
    → devuelve panel_html (str)
    """
```

Impacto: `render_cr_p1.py` y `render_rnd_p1.py` pasan de ~250 líneas de loop a 4 llamadas de 10 líneas.

### 2. Extraer `_traf_line` a `render_helpers.py`

```python
# render_helpers.py
def render_traf_line(trafico_val, trafico_prev=None, accent='var(--ink)'):
    """
    Genera el div 'Tráfico: 12,2B ↑pill'
    Usado en: render_cr_p1 (2x), render_rnd_p1 (2x), ar_updateKPIs (JS)
    """
```

### 3. Unificar `build_canasta_data` y `build_canasta_data_rnd`

Ambas tienen la misma estructura: reciben métricas, calculan WoW, construyen rows. Extraer la scaffolding a `render_helpers.py` con parámetros para la métrica.

### 4. Agregar regla al PROMPT_CORE

> "Toda lógica de presentación compartida CR/RND va en `render_helpers.py`. Nunca duplicar en `render_cr_p1` y `render_rnd_p1`."

---

## Archivos impactados

| Archivo | Cambio |
|---|---|
| `render_helpers.py` | Agregar `build_kpi_tab_panel()`, `render_traf_line()` |
| `render_cr_p1.py` | Reemplazar 4 loops por llamadas a helpers |
| `render_rnd_p1.py` | Idem |
| `render_cr_p2.py` | Extraer scaffolding de `build_canasta_data` |
| `render_rnd_p2.py` | Idem |
| `PROMPT_CORE.md` | Agregar regla de centralización |

---

## Criterio de éxito

Un cambio en el top N visible (hoy `10`) debe requerir modificar **1 sola línea** en `render_helpers.py`, no 4+ archivos.

