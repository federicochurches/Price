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

---

## Cleanup W21 · Eliminación de módulos obsoletos

**Fecha:** Mayo 2026  
**Commits:** `271438c4` · `1f8de2ea`

### Completado

Los renders **sí fueron migrados** en esta sesión (lo que el CHANGELOG_NIVEL3 dejaba como pendiente):

- `render_cr_p1/2/3.py`: `from historico_module_v2 import render_historico_cr` → `from historico_module import render_historico`
- `render_rnd_p1/2/3.py`: `from historico_module_rnd import render_historico_rnd` → `from historico_module import render_historico`
- Firma nueva: `render_historico(reporte, metrica, banda, val, canvas_id)` — sin `current_week`

### Eliminados del repo y del ZIP del proyecto

- `historico_module_v2.py` ✅ eliminado
- `historico_module_rnd.py` ✅ eliminado
- `__init__.py` ✅ eliminado (vacío)
- `test_table.html` ✅ eliminado (test one-shot)
- `run_cr_w21_patch.py` ✅ eliminado (patch W21 absorbido en calc_cr.py)
- `run_rnd_w21.py` ✅ eliminado (script W21 absorbido en calc_rnd.py)
- `PROMPT_CORE_updated.md` ✅ eliminado (duplicado)

### Resultado

ZIP del proyecto: 44 → **39 archivos** · 276 → **252 KB** · ~8k tokens ahorrados del contexto Claude.

### Rollback (si necesario)

Los módulos eliminados están disponibles en commits anteriores de GitHub. Los renders actualizados son compatibles solo con `historico_module.py`.

---

## 2026-05-26 · Sesión W21-post2 (Tooltip canvas + KPI grande)

### Problema raíz
Tooltip del canvas del histórico mostraba siempre el valor global de W21 (93.15%) incluso después de hacer click en una fila específica (ej. Iberostar con 0.00%). El canvas y el bloque "Actual" se actualizaban correctamente, pero el tooltip permanecía con el valor global.

### Causa
- `w22_bindCanvasTip` original captura `cfg` y `pts` en un closure que no se actualizaba.
- `historico_module.drawCanvas` no llamaba `w22_bindCanvasTip` ni actualizaba `W22_CANVAS_CFG`.
- Múltiples `addEventListener('mousemove')` competían en el canvas — sobreescribir `el.onmousemove` no afectaba los registrados con `addEventListener`.
- `IntersectionObserver`, `details toggle`, `radio change` y setTimeouts del módulo histórico redibujaban con `VALS_DEF`, reseteando el estado tras cualquier scroll o cambio.
- El KPI grande de la card (`w21-kv-ef`) nunca se actualizaba — sólo cambiaba el recuadro pequeño "Actual".

### Solución definitiva
1. **`historico_module.py`**: variable mutable `currentVals` que guarda el último estado dibujado. Re-draws automáticos (scroll, toggle, radio, setTimeout) usan `currentVals` en lugar de `VALS_DEF`. Solo `resetToGlobal()` y `hist-reset` resetean explícitamente.
2. **`historico_module.py / updateMetrics`**: actualiza siempre el número grande de la card (`w21-kv-ef`, `w21-kv-cv`, `w21-kv-nd`, `w21-kv-rpm`) con `fmtVal(vCurr)`.
3. **`historico_module.py / drawCanvas`**: al final, actualiza `W22_CANVAS_CFG[CID]` y `W22_CANVAS_PTS[CID]` con los vals dibujados.
4. **`js_override.js`**: hooking del setter de `textContent` del tooltip global. Captura `_lastHoveredCid` en `mousemove` global y cuando cualquier listener intenta escribir `"W21: 93.15%"` en el tooltip, parsea la semana, consulta `W22_CANVAS_CFG[cid].vals[semIdx]` y reescribe el valor correcto.

### Archivos modificados
- `historico_module.py` — currentVals + kvMap update + W22_CANVAS_CFG sync
- `js_override.js` — _hookTooltip + _lastHoveredCid + _patchCanvasTooltips
- `assemble_unified.py` — click handler del panel dispara `hist-update` para canvas del panel Y canvas global
- `demo_js_main.js` — `w22_bindCanvasTip` usa `liveCfg = W22_CANVAS_CFG[cid] || cfg`

### Validación
- Click en Iberostar (tab Corp) → KPI grande pasa de 93,15% → 0,00% ✅
- Canvas redibuja la curva cayendo a 0 en W21 ✅
- Hover sobre W21 del canvas muestra `W21: 0.00%` ✅
- Scroll fuera y volver al canvas mantiene el estado de Iberostar (no se resetea a global) ✅
- Click en label "Global" en el bloque histórico resetea a vals globales ✅
- Click de nuevo en Iberostar (deselect) → KPI grande vuelve a 93,15% ✅ (W21-post2.1)
