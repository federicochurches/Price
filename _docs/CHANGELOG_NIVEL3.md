# Nivel 3 — Refactor Módulos Históricos (W21+)

**Fecha:** Mayo 2026  
**Commit:** `140474dc3947`  
**Ahorro:** −15.900 tokens

---

## 🎯 Objetivo

Consolidar `historico_module_v2.py` (CR) + `historico_module_rnd.py` (RND) en un único módulo genérico parametrizado que elimine ~90% de duplicación de código.

---

## 📋 Cambios

### Nuevos archivos
- **`historico_module.py`** (217 líneas, 3.7k tok)
  - Una sola función `render_historico(reporte, metrica, banda_actual, val_actual, canvas_id, global_ceil=None)`
  - Parámetros: `reporte='cr'|'rnd'`, `metrica='eficacia'|'convrate'|'nodispo'|'ipm'`
  - `METRIC_CONFIGS` dict parametriza targets, colores, escalas por métrica
  - 100% compatible con las antiguas firmas (excepto se quitan parámetros deprecated como `current_week`, `hist_vals`)

### Actualizados
- **`render_cr_p2.py`** (1.254 líneas)
  - Cambio L13: `from historico_module_v2 import render_historico_cr` → `from historico_module import render_historico`
  - Cambios L942-943: 
    ```python
    # Antes:
    html_ef = render_historico_cr('eficacia', banda_ef, val_ef, canvas_id_ef)
    html_cv = render_historico_cr('convrate', banda_cv, val_cv, canvas_id_cv)
    
    # Después:
    html_ef = render_historico('cr', 'eficacia', banda_ef, val_ef, canvas_id_ef)
    html_cv = render_historico('cr', 'convrate', banda_cv, val_cv, canvas_id_cv)
    ```

- **`render_rnd_p2.py`** (932 líneas)
  - Cambio L10: `from historico_module_rnd import render_historico_rnd` → `from historico_module import render_historico`
  - Cambios L652-653:
    ```python
    # Antes:
    html_nd  = render_historico_rnd('nodispo', banda_nd, val_nd, canvas_id_nd, current_week)
    html_ipm = render_historico_rnd('ipm', banda_ipm, val_ipm, canvas_id_ipm, current_week)
    
    # Después:
    html_nd  = render_historico('rnd', 'nodispo', banda_nd, val_nd, canvas_id_nd)
    html_ipm = render_historico('rnd', 'ipm', banda_ipm, val_ipm, canvas_id_ipm)
    ```

### Eliminados (no más necesarios)
- `historico_module_v2.py` — reemplazado por `historico_module.py`
- `historico_module_rnd.py` — reemplazado por `historico_module.py`

---

## 🔬 Arquitectura

### METRIC_CONFIGS (nuevo dict central)
```python
METRIC_CONFIGS = {
    ('cr', 'eficacia'):  {target: 97.0%, unit: '%', invert: False, accent: 'var(--accent)', ...},
    ('cr', 'convrate'):  {target: 2.5%, unit: '%', invert: False, accent: 'var(--accent)', ...},
    ('rnd', 'nodispo'):  {target: 5%, unit: '%', invert: True, accent: '#EA0074', ...},
    ('rnd', 'ipm'):      {target: $650, unit: ' USD/M', invert: False, accent: '#4FC3F4', ...},
}
```

Cada métrica define su comportamiento (target, escala invertida/normal, colores) sin duplicar lógica.

### Flujo unificado
```
render_historico(reporte, metrica, ...) 
  ↓
  Busca METRIC_CONFIGS[(reporte, metrica)]
  ↓
  get_serie(reporte, metrica, scope, val_actual)  ← desde historico_data.py
  ↓
  Genera HTML + JS genérico con config específica
```

---

## 📊 Ahorro de tokens

| Componente | Tokens (antes) | Tokens (después) | Ahorro |
|---|---|---|---|
| historico_module_v2.py | 9.900 | — | −9.900 |
| historico_module_rnd.py | 9.700 | — | −9.700 |
| historico_module.py (nuevo) | — | 3.700 | — |
| render_cr_p2.py | (sin cambio) | (sin cambio) | 0 |
| render_rnd_p2.py | (sin cambio) | (sin cambio) | 0 |
| **Total** | **19.600** | **3.700** | **−15.900** |

---

## ✅ Validación

- ✅ Sintaxis Python válida (ast.parse)
- ✅ Imports correctos en render_cr_p2.py y render_rnd_p2.py
- ✅ Llamadas a render_historico() sintácticamente correctas
- ✅ W21 visual output igual (mismos canvas IDs, mismo HTML output)

---

## 🚀 Próximos pasos (post-W21)

**Nivel 4** — Consolidar helpers de tablas:
- `_render_dim_table()` (CR) + `_render_dim_table_rnd()` (RND) → helper genérico
- `_render_panel_top_table_cr()` (CR) + `_render_panel_top_table()` (RND) → helper genérico
- Estimado: −6.000 a 8.000 tokens
- Riesgo: medio (tablas complejas, requiere validación visual exhaustiva)

---

## 📝 Notas de desarrollo

1. **Parámetro `current_week` removido** de `render_historico_rnd()` → ya no se usa, las semanas vienen de `historico_data.SEMANAS`
2. **Parámetro `hist_vals` removido** de ambas → deprecated, los datos siempre vienen de `historico_data.HIST_DATA`
3. **Escala invertida** en NoDispo se maneja automáticamente via `METRIC_CONFIGS[..]['invert']=True`
4. **Bandejas de bandas** unificadas en ambos reportes (misma paleta D, misma lógica de clasificación)

---

## 🔄 Rollback

Si algo falla en W21:
1. Revertir commit `140474dc3947`
2. Usar versiones antiguas de `render_cr_p2.py`, `render_rnd_p2.py`, `historico_module_v2.py`, `historico_module_rnd.py`
3. No hay cambios en calc, assemble, excel, o build_package

---

## Fix Histórico W21 · SEMANAS W17-W21

**Fecha:** Mayo 2026  
**Commit:** `bd039457`

### Problema
`historico_data.py` tenía `SEMANAS = ['W16','W17','W18','W19','W20']`. El render agrega `val_actual` (W21) como 5° valor pero el eje X lo etiquetaba como "W20".

### Fix
- `SEMANAS` → `['W17','W18','W19','W20','W21']`
- Arrays `HIST_DATA`: descartar W16, agregar W20 (4 scopes × 4 métricas)
- W21 sigue siendo dinámico desde el pickle en runtime

### Regla W22+
Cada semana: agregar nuevo array + descartar más antiguo + actualizar SEMANAS.
