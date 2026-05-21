
---

---

## Week 20 · 21 Mayo 2026 · Módulo Histórico RND + Fixes CR

### ✨ Feature: Módulo Histórico Reactivo en RatesNoDispo

**Nuevo archivo:** `historico_module_rnd.py`
- Función `render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id, hist_vals, global_ceil)`
- Dos métricas diferenciadas:
  - `nodispo`: escala invertida (menor = mejor) · accent magenta `#EA0074` · target `< 5%`
  - `ipm`: escala normal (mayor = mejor) · accent amber `#A86A1D` · target `≥ $650`
- Canvas curva escala LOCAL + sparkline escala GLOBAL vs target
- Label target en HTML (esquina sup. derecha) — no dibujado dentro del canvas
- `pR=10` en canvas para igualar ancho con sparkline
- Interactivo: click en elemento actualiza canvas, métricas y banda

**Modificado:** `render_rnd_p1.py`
- Import `historico_module_rnd`
- `render_kpi_card_nodispo`: rows con `data-hist-*` · módulo después de `.tab-panels`
- `render_kpi_card_rpm`: idem · W20 del elemento desde `IPM_W18`

**Modificado:** `render_rnd_p3.py`
- Import `historico_module_rnd`
- `tab_rows_canasta`: rows con `data-hist-*` para NoDispo e IPM
- `kpi_card_canasta`: módulo inyectado después de `{panels}` · antes de `{js_tabs}`

**Cobertura RND:** 8 cards — 2 globales + 6 canastas

### 🐛 Fixes CR

**`render_cr_p1.py`** — Channel tab ahora clickeable:
- `chan_row` (Eficacia): agrega `data-hist-*` + `cursor:pointer`
- `chan_row_cv` (ConvRate): idem · W20 desde `ConvRate_W17`
- Bug corregido: `rows_pp` undefined tras edición — restaurado en ambas funciones

**`historico_module_v2.py`** — Badge Súper Crítica dinámico:
- JS `updateMetrics`: agrega `bbEl.style.color = bc.fg`

### 📐 Fix visual: canvas = sparkline ancho
- `pR` reducido de `38` a `10` en `historico_module_rnd.py`
- Label target movido a HTML posicionado

### ⏳ Pendientes registrados
- Fix color badge Súper Crítica en RND
- Ajustes spacing: `tabs-row margin-top` y módulo `margin-top`
- Módulo histórico en Análisis por Hotel y Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle

---


## Week 20 · 21 Mayo 2026 · Módulo Histórico RND + Fixes CR

### ✨ Feature: Módulo Histórico Reactivo en RatesNoDispo

**Nuevo archivo:** `historico_module_rnd.py`
- Función `render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id, hist_vals, global_ceil)`
- Dos métricas con lógica diferenciada:
  - `nodispo`: escala invertida (menor = mejor) · accent magenta `#EA0074` · target `< 5%`
  - `ipm`: escala normal (mayor = mejor) · accent amber `#A86A1D` · target `≥ $650`
- Canvas curva escala LOCAL + sparkline escala GLOBAL vs target
- Label target en HTML (esquina sup. derecha del div) — no dentro del canvas
- `pR=10` en canvas para igualar ancho con sparkline
- Interactivo: click en elemento actualiza canvas, métricas y banda

**Modificado:** `render_rnd_p1.py`
- Import `historico_module_rnd`
- `render_kpi_card_nodispo`: rows con `data-hist-w21/w20/label` · módulo después de `.tab-panels`
- `render_kpi_card_rpm`: idem · W20 del elemento desde `IPM_W18`

**Modificado:** `render_rnd_p3.py`
- Import `historico_module_rnd`
- `tab_rows_canasta`: rows con `data-hist-*` para NoDispo e IPM
- `kpi_card_canasta`: módulo inyectado después de `{panels}` · antes de `{js_tabs}`

**Cobertura RND:** 8 cards — 2 globales (NoDispo + IPM) + 6 canastas

### 🐛 Fixes CR

**`render_cr_p1.py`** — Channel tab ahora clickeable:
- `chan_row` (Eficacia): agrega `data-hist-w21/w20/label` + `cursor:pointer`
- `chan_row_cv` (ConvRate): idem · W20 desde `ConvRate_W17`
- Bug corregido: `rows_pp` undefined tras edición — restaurado en ambas funciones

**`historico_module_v2.py`** — Badge Súper Crítica dinámico:
- JS `updateMetrics`: agrega `bbEl.style.color = bc.fg` al actualizar banda
- Fix aplica cuando se clickea un elemento que resulta en banda Súper Crítica

### 📐 Fix visual: canvas = sparkline ancho
- `pR` reducido de `38` a `10` — la curva ahora ocupa el mismo ancho que las barras
- Label target movido a HTML posicionado (no dibujado en canvas)
- Aplica en `historico_module_rnd.py`

### ⏳ Pendientes registrados
- Fix color badge Súper Crítica en RND (menor · para W21)
- Ajustes spacing: `tabs-row margin-top` 14px→6px · módulo `margin-top` 16px→6px
- Módulo histórico en secciones Análisis por Hotel y Dimensión (CR + RND)

---

**Última actualización:** Mayo 2026 · post W20 · Módulo Histórico RND · Fixes CR channel + Súper Crítica
