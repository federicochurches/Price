# CHANGELOG · Proyecto PRICE · Supply Analytics

---
## Week 20 · 23 Mayo 2026 · Sesión 4 · Módulo histórico CR hotel/dim + Reformulación badges Opción D

### ✨ Feature 1 · Módulo histórico CR en Análisis por hotel + Análisis por dimensión

Pendiente cerrado de sesión 3: portar el módulo histórico de RND a las dos secciones equivalentes en CR.

**Nueva función:** `render_historico_seccion_cr(canvas_id_ef, canvas_id_cv, banda_ef, val_ef, banda_cv, val_cv)` en `render_cr_p2.py` (análoga a `render_historico_seccion_rnd`).

**Modificado:** `historico_module_v2.py` ahora registra listeners `hist-update` y `hist-reset` SIEMPRE (fuera del bloque `readyState`), permitiendo que wrappers externos disparen actualizaciones del canvas. Backward-compatible con el listener interno de `.kpi-card` (Hero y canastas siguen funcionando).

**Parámetro opcional:** `with_hist=True` en `render_top_table_cr` y `_render_dim_table` enriquece cada fila con `data-hist-w21/w20/cv-w21/cv-w20/label` + `cursor:pointer`.

**Integración:**
- `render_bloque_hoteles_cr` → canvas IDs `hcr-hotel-ef` y `hcr-hotel-cv` (debajo de los 4 tabs Críticos/BajoRend/SinConv/MenorCV)
- `render_bloque_dimensiones_cr` → canvas IDs `hcr-dim-ef` y `hcr-dim-cv` (debajo de los 3 tabs Corp/Destino/Channel)

**UX:** click en fila de tabla actualiza ambos módulos (Eficacia + ConvRate) sincronizadamente. Re-click resetea a Global. Aislamiento total: clicks en sección NO afectan cards hero y viceversa.

**Commit:** `6a0c38e` · feat(cr): módulo histórico reactivo en Análisis por hotel y por dimensión

### 🎨 Feature 2 · Reformulación badges severity (Opción D + paleta D)

Cierre del cambio que se había perdido en un revert. **Estilo Opción D** aplicado uniformemente a TODOS los badges del sistema (Hero, módulos históricos, severity tablas, pills en filas).

**Nuevo estilo:**
```css
font-size: 13px              /* canastas: 11px */
font-weight: 700
letter-spacing: .04em
text-transform: uppercase
padding: 10px 22px
border-radius: 3px
border: 1px solid {bd}
text-align: center
```

**Cambios funcionales:**
- Texto del badge: SOLO nombre de banda en mayúsculas (sin "· Target X%")
- Nueva función `target_caption(target_text, font_size='11px')` en `render_helpers.py` para renderizar el target como caption gris separado debajo del badge
- `banda_pill()` refactorizada: parámetro `target` se mantiene en firma por compatibilidad pero se ignora

**Módulo histórico CR:**
- Quitado el label "Banda" como title arriba del badge (línea 138 vieja del `_BANDA_COLORS` box)
- Quitado el prefijo "Banda: " del footer — ahora muestra solo `EXITOSA`, `REVISAR`, etc. en mayúsculas
- JS `updateMetrics()`: `el.textContent = banda.toUpperCase()` en lugar de `'Banda: ' + banda`

El módulo histórico RND ya estaba correcto desde sesión 2 — no requirió cambios.

### 🔧 Fix barrido · Cyan `#4FC3F4` → Verde teal `#085041` en Exitosa

Sesión 3 había aplicado el fix solo a `BANDA_COLORS` del `render_helpers.py`. Quedaron 22 referencias hardcodeadas a cyan que se escaparon. **Esta sesión barrió todas:**

| Archivo | Lugares | Tipo |
|---|---|---|
| `render_helpers.py` | 4 ocurrencias (`gauge_5levels` variantes) | Hardcoded Exitosa color |
| `render_cr_p2.py` | 3 ocurrencias + fallback bg `#E8F7FD` → `#E1F5EE` | Severity gauges + fallback |
| `render_rnd_p2.py` | 4 ocurrencias (severity + tablas dim) | Hardcoded Exitosa |
| `render_rnd_p3.py` | 1 (COLORS canastas) | Hardcoded |
| `template_severity.py` | 5 ocurrencias (Severity tables) | bg/fg de banda Exitosa |
| `historico_module_v2.py` | 1 (`_BANDA_COLORS['Exitosa']`) | Dict de colores módulo CR |
| `asset_cr_head.html` · `asset_rnd_head.html` | Var CSS `--green` y `--green-soft` + `exec-mini-card.qw` border | CSS |
| `snippet_alertas_canasta.html` + `_rnd.html` (+ duplicados en `snippets/`) | `border-top:3px solid` | CSS inline |

**Cyan `#4FC3F4` queda SOLO en 2 lugares válidos:**
1. `IPM_ACCENT` en `historico_module_rnd.py` línea 10 (Arctic Blue corporativo, accent visual IPM)
2. Label "🔌 Third Party" en `render_cr_p1.py` líneas 197, 338 (color identitario familia Third Party CR)

### 📋 Bugs corregidos #81–#93
- #81 `banda_pill()` rediseñada · estilo Opción D
- #82 Nueva función helper `target_caption()`
- #83 Hero + canastas usan `pill_with_target` (pill + caption separado)
- #84 Módulo histórico CR: quitar label "Banda" arriba del badge
- #85 Módulo histórico CR footer: quitar prefijo "Banda: "
- #86 JS `updateMetrics()` `historico_module_v2.py`: textContent solo nombre en mayúsculas
- #87 `gauge_5levels` Exitosa cyan → verde (4 variantes)
- #88 `render_cr_p2.py` Exitosa cyan → verde (3) + fallback bg cyan → verde
- #89 `render_rnd_p2.py` Exitosa cyan → verde (4)
- #90 `render_rnd_p3.py` COLORS canastas Exitosa cyan → verde
- #91 `template_severity.py` Exitosa bg/fg cyan → verde teal (5)
- #92 Var CSS `--green` y `--green-soft` cyan → verde + `exec-mini-card.qw` border
- #93 Snippets alertas canasta border-top cyan → verde

### 🗂 Archivos modificados
**Código:** `render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html` · `snippets/snippet_alertas_canasta*.html` (duplicados)

**Documentación:** `_docs/BANDAS.md` (reescrito completo) · `_docs/PROMPT_MAESTRO_v3.md` (sesión 3 + 4 documentadas)

### ⏸ Pendientes que quedan abiertos
- Validación visual final del reporte CR W20 regenerado con badges Opción D
- Regenerar reporte RND W20 con los mismos cambios
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)
- ~~Decisión sobre `_docs/CHANGELOG.md` duplicado~~ ✅ resuelto: `_governance/` eliminado, canon unificado en `_docs/CHANGELOG.md`
- Restaurar search box (tarea conocida desde sesiones huérfanas previas)
- Commit + push de los cambios de esta sesión

### 🚫 Bugs descartados en esta sesión
- Bug 2 · CR canasta dim números pegados (sesión 4 inicial): descartado tras verificar que pertenecía a una rama huérfana de un revert
- Bug 4 · Search box no revela (sesión 4 inicial): descartado por misma razón
- Bug 5 · RND sin search en hotel (sesión 4 inicial): descartado por misma razón

---
## Week 20 · 22 Mayo 2026 · Sesión 3 · Fixes visuales módulos históricos + colores severity

### 🎨 Sistema de colores severity — correcciones

**Exitosa:** `#4FC3F4` (cyan) → `#085041` (verde teal) en todos los contextos:
- Barras de progreso del severity principal
- Pills de banda Exitosa
- Variable CSS `--green: #4FC3F4` → `--green: #085041`
- Gauge de 5 niveles del módulo histórico

**Súper Crítica:** `#161616` (negro) → `#A32D2D` (rojo oscuro) en gauges

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros, sin transparencia

### ✨ Módulos históricos Análisis por Hotel y Dimensión (RND) — funcionalidad completa

**Problema raíz resuelto:** los módulos clonados (`hrnd-hotel-nd/ipm`, `hrnd-dim-nd/ipm`) no tenían los listeners `hist-update` y `hist-reset` que permiten que el click en una fila actualice el canvas.

**Fixes aplicados:**
- Listeners `hist-update` y `hist-reset` agregados a los 4 módulos clonados directamente en el HTML
- `data-hist-nd` e `data-hist-ipm` con valores reales extraídos del HTML (antes eran `0.0`)
  - Hotel: %NoDispo real de cada fila (ej. `39.5%`, `56.33%`)
  - Dimensión: %NoDispo e IPM real de cada corporativo/destino/país
- Canvas IDs correctos: `hrnd-hotel-nd`, `hrnd-hotel-ipm`, `hrnd-dim-nd`, `hrnd-dim-ipm`
- Balance de divs corregido (eliminación de `</div>` huérfano en línea 5151)

### 🔧 Fixes de usabilidad módulo histórico

- **Badge banda centrado** vertical y horizontal: `display:flex;align-items:center;justify-content:center;min-height:44px`
- **`resetToGlobal` scope fix:** función definida antes del `addEventListener` en `attachListeners()`
- **Reset a Global:** click en label "GLOBAL" o en fila activa resetea la vista (inline fix en módulos clonados)
- **Severity → Severity** (mayúscula) en ambos reportes

### 🗂 Archivos modificados
`CheckRates_Reporte_Editorial.html` · `RatesNoDispo_Reporte_Editorial.html`

---
## Week 20 · 22 Mayo 2026 · Fixes visuales + módulo histórico en secciones RND

### 🎨 Nueva paleta sistema de bandas D

Rediseño completo de colores en `render_helpers.py`, `historico_module_cr.py` y `historico_module_rnd.py`:

| Banda | Antes | Ahora |
|---|---|---|
| Exitosa | Celeste `#0D7A99` | Verde teal `#085041` |
| Aceptable | Violet `#5C469C` | Violet oscuro `#3C3489` |
| Revisar | Marrón `#A86A1D` | Naranja `#7C2D12` / `#F97316` |
| Crítica | Rojo `#C0392B` | Rojo oscuro `#99162B` |
| Súper Crítica | Negro `rgba(22,22,22,.80)` | Rojo `#A32D2D` / texto `#FCEBEB` |

Aplicado en Python (3 archivos) y en los 2 HTMLs W20 (458 reemplazos CR + 380 RND).

### 🎨 IPM accent → cyan corporativo `#4FC3F4`

`historico_module_rnd.py`: `IPM_ACCENT` cambia de `#A86A1D` (amber viejo) a `#4FC3F4` (Arctic Blue corporativo).

Consistencia final:

| Reporte | Métrica 1 | Métrica 2 |
|---|---|---|
| CheckRates | Eficacia → magenta `#EA0074` | ConvRate → violet `#5C469C` |
| RatesNoDispo | NoDispo → magenta `#EA0074` | IPM → cyan `#4FC3F4` |

### ✨ Módulo histórico en Análisis por Hotel y Dimensión (RND)

**`render_rnd_p2.py`** — nueva función `render_historico_seccion_rnd()`:
- Módulo doble (NoDispo + IPM lado a lado) debajo del tabs-block en cada sección
- Cada fila de hotel y dimensión tiene `data-hist-nd`, `data-hist-ipm`, `data-hist-nd-prev`, `data-hist-ipm-prev`, `data-hist-label`
- Click en cualquier fila de cualquier tab actualiza ambos módulos vía `CustomEvent` (`hist-update`)
- Click en "Global" o en fila activa resetea a vista global (`hist-reset`)
- Canvas IDs: `hrnd-hotel-nd`, `hrnd-hotel-ipm`, `hrnd-dim-nd`, `hrnd-dim-ipm`

**`historico_module_rnd.py`** — nuevos listeners:
- `hist-update`: recibe `{cid, w_curr, w_prev, label}` → redibuja canvas + métricas
- `hist-reset`: resetea a datos globales

### 🔧 Fixes de usabilidad · módulo histórico

- Label "Global" clickeable (subrayado punteado + `cursor:pointer`) → resetea a vista global
- Click en fila ya seleccionada → deselecciona y resetea (toggle)
- Aplica en `historico_module_cr.py` y `historico_module_rnd.py` + los 2 HTMLs W20

### 📝 Fixes editoriales

- `Severidad` → `Severity` en ambos reportes (7 reemplazos)
- Footer eliminado en RND para consistencia con CR
- Semanas canvas W14-W21 → W13-W20 en los HTMLs (fix aplicado directo en HTML)

### 🗂 Archivos modificados
`render_rnd_p2.py` · `render_helpers.py` · `historico_module_cr.py` · `historico_module_rnd.py` · `CheckRates_Reporte_Editorial.html` · `RatesNoDispo_Reporte_Editorial.html`

---
## Week 20 · 22 Mayo 2026 · Fixes módulos históricos CR + RND

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #72 | `historico_module_cr.py` | Labels canvas en `rgba(100,90,80,0.55)` y `font-size:7px` → `0.80` y `8px` (legibles) |
| #73 | `historico_module_cr.py` | Datos ficticios con variación insuficiente → fixtures con variación realista W(N-7)-W(N) |
| #74 | `historico_module_cr.py` | `W14`/`W21` hardcodeados en footer sparkline → `{semanas[0]}` / `{semanas[-1]}` dinámicos |
| #75 | `historico_module_rnd.py` | `W14`/`W21` hardcodeados en footer sparkline → `{semanas[0]}` / `{semanas[-1]}` dinámicos |

### 📐 Detalle

**Fix #72-#73 (CR):** El canvas mostraba labels ilegibles (gris pálido, fuente diminuta) y la curva aparecía casi plana por insuficiente variación en los datos ficticios. Fix: alpha `0.55 → 0.80`, font `7px → 8px`, nuevos fixtures con delta realista por semana.

**Fix #74 (CR) + #75 (RND):** El footer del sparkline mostraba siempre `W14 ... W21` hardcodeado, independientemente de `current_week`. Fix: se reemplaza por `{semanas[0]}` y `{semanas[-1]}`, que se calculan dinámicamente a partir de `current_week`. Con `current_week='W20'` → muestra `W13 ... W20`.

### ⚠️ Regla operativa: `current_week` = semana ACTUAL

Al integrar los módulos en los render scripts, usar siempre la semana que se está reportando:
- Hoy W20 → `current_week='W20'` → genera W13-W20
- Próximo lunes W21 → `current_week='W21'` → genera W14-W21

### 🗂 Archivos modificados
`historico_module_cr.py` · `historico_module_rnd.py`

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
- Ajustes spacing: tabs-row margin-top · módulo margin-top
- Módulo histórico en Análisis por Hotel y Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle

---

## Week 20 · 21 Mayo 2026 · Módulo Histórico CR · "Evolución Histórica"

### ✨ Feature: Módulo Histórico Reactivo en CheckRates

**Nuevo archivo:** `historico_module_v2.py`
- Función `render_historico_cr()` — genera bloque HTML+JS completo
- Canvas con curva de tendencia (escala local) + sparkline (escala global vs target)
- 5 métricas: Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- Interactivo: click en cualquiera de los 10 elementos del tab actualiza el módulo
- Colores del sistema D exactos · Súper Crítica badge negro/blanco · footer texto oscuro
- Título: "Evolución Histórica"

**Modificado:** `render_cr_p1.py`
- Import `historico_module_v2`
- `render_kpi_card_eficacia` y `render_kpi_card_convrate`: módulo después de `.tab-panels`
- Rows de tabs con `data-hist-w21`, `data-hist-w20`, `data-hist-label`
- `chan_row` y `chan_row_cv`: Channel tab clickeable

**Modificado:** `render_cr_p3.py`
- Import `historico_module_v2`
- `kpi_card_canasta`: módulo después de `.tab-panels`
- `tab_rows_canasta`: rows con `data-hist-*`

**Cobertura CR:** 8 cards — 2 globales + 6 canastas (B2B-OP · CUG · B2C × Eficacia + ConvRate)

---


## Week 20 · 21 Mayo 2026 · Módulo Histórico CR · "Evolución Histórica"

### ✨ Feature: Módulo Histórico Reactivo en CheckRates

**Nuevo archivo:** `historico_module_v2.py`
- Función `render_historico_cr()` — genera bloque HTML+JS completo
- Canvas con curva de tendencia (escala local) + sparkline (escala global vs target)
- 5 métricas: Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- Interactivo: click en cualquiera de los 10 elementos del tab actualiza el módulo
- Colores del sistema D exactos (`render_helpers.py BANDA_COLORS`)
- Súper Crítica: badge negro/blanco · footer texto oscuro (legible sobre fondo claro)
- Título: "Evolución Histórica" (genérico, no limita a 8W)

**Modificado:** `render_cr_p1.py`
- Import `historico_module_v2`
- `render_kpi_card_eficacia`: módulo inyectado después de `.tab-panels`
- `render_kpi_card_convrate`: idem
- Rows de tabs con `data-hist-w21`, `data-hist-w20`, `data-hist-label`

**Modificado:** `render_cr_p3.py`
- Import `historico_module_v2`
- `kpi_card_canasta`: módulo inyectado después de `.tab-panels`
- `tab_rows_canasta`: rows con `data-hist-*` attrs

**Cobertura:** 8 cards — 2 globales (Hero) + 6 canastas (B2B-OP · CUG · B2C × Eficacia + ConvRate)

**Pendiente:**
- Módulo en Análisis por Hotel + Dimensión (CR)
- Módulo en RND (misma arquitectura)
- Datos históricos reales cuando estén en pickle

---

## Week 20 · 19 Mayo 2026 · MIN_CR=100 + Metodología consolidada + Fixes críticos

### 🎯 Cambios Arquitectónicos (CRÍTICOS)

**MIN_CR = Universo operacionalmente relevante:**
- ✅ `calc_cr.py` línea 62: `MIN_CR = 100` (hoteles con ≥100 CheckRates/semana)
- ✅ `calc_rnd.py` línea 85: `MIN_TRAFICO = 50000` (equivalente en RND)
- ✅ Filtro aplicado ANTES de calcular percentiles (P90)
- ✅ Elimina ruido de hoteles pequeños, una métrica única y honesta
- ✅ Impacto: Iberostar OP ahora consistente (99.25%, 3 hoteles ≥100 CR)

**P90 + Nota de Metodología:**
- ✅ `assemble_cr.py`: Agrega caja informativa sobre P90 + MIN_CR
- ✅ `assemble_rnd.py`: Idem
- ✅ Documentación clara en reportes HTML

**Destinatarios actualizados:**
- ✅ `destinatarios.md`: 28 personas (15 originales + 13 nuevos)

---

## Week 20 · 19 Mayo 2026 · Fixes críticos + creación de nuevos scripts

### 🐛 Bugs corregidos (8 total)

| Bug | Archivo | Descripción |
|---|---|---|
| #60 | `render_helpers.py` | `WEEK_NUM = "W18"` hardcodeado → `os.getenv('WEEK', 'W20')` dinámico |
| #63 | `render_*_p*.py` | Imports relativos (`from .._scripts.engine`) → absolutos (`sys.path.insert()` + `from engine`) |
| #64 | `render_rnd_p3.py`, `render_cr_p3.py` | `wow_box_canasta()` con W17/W18 hardcodeados → variables dinámicas `W{WEEK_NUM_INT-1}` / `W{WEEK_NUM_INT}` |
| #65 | Todos `render_*.py` | Keys pickle `M['global_w18']` hardcodeadas → alias dinámico `M['global_current']` post-load |
| #66 | `asset_rnd_masthead.html` | Fecha `<span>Lunes 27 De Abril De 2026</span>` hardcodeada → eliminada (permite dinamismo) |
| #67 | `assemble_rnd.py`, `assemble_cr.py` | Headers con "Week 18" en lugar de "Week 20" → sed masivo post-render |
| #68 | `calc_rnd.py` | **CRÍTICO:** `banda_rpm()` se aplicaba solo con IPM, sin parámetro `Bookings` → nunca retornaba "Sin Conversión" (11.463 hoteles perdidos) → fix: `lambda r: banda_rpm(r['IPM'], r['Bookings'])` en líneas 53 y 66 |
| #69 | `calc_rnd.py`, `calc_cr.py` | Imports relativos → absolutos: `from engine import banda_nodispo, banda_rpm` |
| #70 | `calc_rnd.py`, `calc_cr.py` | Paths datasets hardcodeados (carpeta actual) → absolutos `/mnt/user-data/uploads/` + fallback `/mnt/project/` |
| #71 | `calc_rnd.py`, `calc_cr.py` | Pickles guardados en carpeta actual → absolutos `/mnt/project/rnd_w{VOL_NUM}_data.pkl` |

### 🆕 Scripts nuevos

| Script | Descripción | Status |
|---|---|---|
| `excel_rnd_canastas.py` | Genera 3 Excels por canasta (B2C, OP, CUG) para RND · 8 pestañas c/u | ✅ Creado + testeado |
| `excel_cr_canastas.py` | Genera 3 Excels por canasta (B2C, OP, CUG) para CR · 9 pestañas c/u | ✅ Creado + testeado |

### 📝 Documentación nueva

| Archivo | Descripción |
|---|---|
| `FIXES_W20_FINAL.md` | Guía completa de todos los bugs, cambios permanentes y checklist para W21+ |

### 🗂 Archivos modificados

**Scripts de cálculo:**
- `calc_rnd.py` (líneas 6, 37, 53, 66, ~315)
- `calc_cr.py` (líneas 10, 39, 387)

**Scripts de render:**
- `render_rnd_p1.py` (imports, alias dinámicos)
- `render_rnd_p2.py` (imports, alias dinámicos)
- `render_rnd_p3.py` (imports, alias dinámicos, wow_box_canasta)
- `render_cr_p1.py` (imports, alias dinámicos)
- `render_cr_p2.py` (imports, alias dinámicos)
- `render_cr_p3.py` (imports, alias dinámicos, wow_box_canasta)

**Scripts de ensamble y Excel:**
- `assemble_rnd.py` (footer, headers fixes)
- `assemble_cr.py` (footer, headers fixes)
- `excel_rnd.py` (sin cambios críticos)
- `excel_cr.py` (sin cambios críticos)

**Assets:**
- `asset_rnd_masthead.html` (fecha hardcodeada eliminada)

**Helpers:**
- `engine.py` (banda_rpm confirmada correcta)
- `render_helpers.py` (WEEK_NUM dinámico)

### ✅ Validaciones finales W20

- ✅ Week 20 en todos los headers
- ✅ Fechas correctas: 12–18 may 2026
- ✅ **Sin Conversión: 11.463 hoteles (61.0% del P80)** ← BUG #68 corregido
- ✅ Severity IPM suma correctamente: 11.463 + 1.580 + 1.356 + 1.683 + 2.706 = 18.788
- ✅ IPM $1.183,30 = Aceptable ($650-$1500) ← Correcto
- ✅ 8 Excels generados (4 RND + 4 CR)
- ✅ Top 100 en RND canastas (10 + 40 extra)
- ✅ Top 10 en CR canastas
- ✅ WoW blocks dinámicos (W20 vs W19)

### 📊 Outputs W20 finales

**HTMLs:** 2
- `RatesNoDispo_Reporte_Editorial.html` (473 KB)
- `CheckRates_Reporte_Editorial.html` (611 KB)

**Excels:** 8
- `Analisis_Rates_NoDispo_7d.xlsx` + B2C/OP/CUG (4 total)
- `Analisis_Checkrates_7d.xlsx` + B2C/OP/CUG (4 total)

**Pickles:** 2
- `rnd_w20_data.pkl` (61 MB)
- `cr_w20_data.pkl` (20 MB)

### 🔍 Impacto

- **Criticidad:** 🔴 Alta (Bug #68 afectaba 11.463 hoteles del P80)
- **Alcance:** Global (todos los reports RND) + Canastas (B2C/OP/CUG)
- **Permanencia:** Todos los fixes son estructurales, NO se repiten en W21+

### 📋 Checklist para W21+

Ver `FIXES_W20_FINAL.md` para checklist completo de validación y configuración.

---



### 🐛 Bug corregido

| Bug | Archivo | Descripción |
|---|---|---|
| #47 | `calc_cr.py` | CONFIG decía WEEK='W18' pero generaba cr_w19_data.pkl · desalineamiento — fix: WEEK='W19' + print message correcto |

**Problema detectado:** En audit pre-W20, calc_cr.py tenía CONFIG WEEK='W18' pero leía datasets W19 y generaba cr_w19_data.pkl. Mismatch confuso.

**Solución:** 
- Línea 12: `WEEK = 'W18'` → `WEEK = 'W19'`
- Línea 381: print message → `cr_w19_data.pkl`

**Status:** ✅ Aplicado · calc_cr.py ahora 100% alineado con pipeline W19

**Impacto:** Zero impacto en W19 (pipeline funcional por casualidad). W20 comenzará con CONFIG correcta desde inicio.

### 📝 Archivos modificados
`calc_cr.py` · `PROMPT_MAESTRO_v3.md`

---

## Post W19 · Mayo 2026 · sesión fixes Excel + HTML

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #28 | `excel_cr.py` | Pestañas Críticos no ordenadas por Eficacia ↑ — fix: `sort_values('Eficacia', ascending=True)` global + canastas |
| #29 | `excel_cr.py` | `Por Corporativo` (global + canastas) sin columna Channel — fix: groupby `hotel_channel_map` → columna `Channels` con valores únicos |
| #30 | `excel_rnd.py` | Columnas `RPM` y `BandaRPM` visibles en Excel — fix: `.rename()` → `IPM (USD/M)` y `Banda IPM` en todas las hojas |
| #31 | `excel_rnd.py` | Colores de banda IPM no se aplicaban — fix: `banda_col2` en `add_table()` para colorear dos columnas de banda por fila |
| #32 | `excel_rnd.py` | `Sin Conversión` sin color en `BAND_FONTS` — fix: `Font(..., color='8A8377')` |
| #33 | `render_cr_p2.py` | Header tab hotel `'Checkrates'` → `'CR Únicos'`, `'ConvRate'` → `'Conv Rate'` (5 ocurrencias) |
| #34 | `render_cr_p2.py` | Header tabla dim `'CR'` → `'CR Únicos'`, `'CV'` → `'Conv Rate'` (Corp + Dest + Channel) |
| #35 | `render_cr_p3.py` | Header dim canastas `'CR'` → `'CR Únicos'`, `'CV'` → `'Conv Rate'` |
| #36 | `calc_rnd.py` | `ZeroDivisionError` en print final cuando dataset W18 vacío — fix: guard `if t17>0` |

### 🗂 Archivos modificados
`excel_cr.py` · `excel_rnd.py` · `render_cr_p2.py` · `render_cr_p3.py` · `calc_rnd.py`

---
## Week 19 · Mayo 2026 · sesión fixes visuales + features

### 🐛 Bugs corregidos

| Bug | Archivo | Descripción |
|---|---|---|
| #16 | `render_mail_v3.py` | Dependencia de `metrics_recalc.pkl` inexistente |
| #17 | `excel_rnd.py` | Path hardcodeado `/home/claude/final_w18/rnd_w19_data.pkl` |
| #18 | `build_package.py` | ZIP con prefijo `Price_WNN/` |
| #19 | `calc_rnd.py` | `df17` cargaba W19 en lugar de W18 — WoW era 0 |
| #20 | `render_rnd_p1.py` | Card IPM: condición `ipm_w17 > 0` siempre False (columna `IPM_W17` inexistente) |
| #21 | `render_rnd_p3.py` | `_enrich_wow` buscaba `IPM_W17` en vez de `IPM_W18` |
| #22 | `render_rnd_p1/p2/p3.py` | WoW IPM en USD absoluto (`↑$105`) — fix: convertir a % |
| #23 | `render_rnd_p1/p2/p3.py` | WoW %NoDispo sin unidad (`+4,58`) — fix: sufijo `pp` |
| #24 | `render_cr/rnd_p1.py` | Header masthead "Week 18" hardcodeado — fix: leer `VOL_NUM` del pickle |
| #25 | `render_cr_p2.py` | `_fmt_wow_cv` faltaba — syntax error en concatenación |
| #26 | `calc_cr.py` | Pickle salía como `cr_w18_data.pkl` — fix: `cr_w19_data.pkl` |
| #27 | `calc_cr.py` | `df17` buscaba `Dataset_CheckRates_W17.xlsx` inexistente — fix: W18 |

### ✨ Nuevas features

#### WoW con unidades claras en RND (global + canastas)
- `%NoDispo WoW` siempre con sufijo `pp`
- `IPM WoW` en porcentaje relativo (no USD absoluto)
- Aplica en p1 (hero), p2 (dim global), p3 (canastas)

#### Tabla Análisis por Dimensión RND — 2 columnas WoW separadas
- Orden: `Nombre · %NoDispo · WoW · IPM · WoW`
- Grid: `1fr 62px 36px 58px 36px`
- `asset_rnd_head.html` CSS actualizado

#### WoW ConvRate en tabla Análisis por Dimensión CR
- Orden: `Nombre · CR únicos · BKGS · ConvRate · WoW · Eficacia · WoW`
- Grid: `1fr 80px 60px 68px 38px 68px 38px`
- Helper `_fmt_wow_cv` (pp) en `render_cr_p2.py`

#### Tab Hotel Conv Rate — filtro Sin Conversión
- Solo `Bookings > 0` — Sin Conversión tiene su tab propia
- Fix en `render_cr_p1.py` y `calc_cr.py`

#### Plan de Acción + Sistema Carryover
- `template_seguimiento.py`: genera bloque HTML de carryover
- `build_package.py`: genera `plan_seguimiento_WNN.md`
- Lógica: ES/MP → `## OPEN` (auto), QW → `## PENDIENTE_QW` (revisión manual)
- Visual: separador "📋 Carryover", badge `CARRYOVER` gris, badge `desde WNN`
- Aplica en global + canastas de CR y RND

#### Estructura ZIP repo corregida
- `_governance/_seguimiento/plan_seguimiento_WNN.md`
- Datasets crudos incluidos automáticamente

#### Semana dinámica en masthead
- `VOL_NUM`, `PERIODO`, `MES_AÑO` almacenados en pickle y leídos en render p1

### 📊 KPIs W19 (valores finales post-fixes)
| Métrica | W19 | WoW |
|---|---|---|
| % NoDispo (P80) | 2,42% | ▼ 0,55pp |
| IPM (P80) | $597 | ▼ 7,4% |
| Eficacia CR (P80) | 93,88% | ▼ 0,25pp |
| Conv Rate CR (P80) | 1,32% | ▲ 0,05pp |

### 🗂 Archivos modificados
`calc_cr.py` · `calc_rnd.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `asset_rnd_head.html` · `build_package.py` · `template_seguimiento.py` · `MAIL_DRAFT_FLUJO.md`

---

## Week 19 · Mayo 2026 · sesión inicial pipeline

### Nuevas features
- `build_package.py` Paso 6: genera `index.html` hub + `Price_WNN.zip`
- `render_mail_v3.py` v3.2: sin `metrics_recalc.pkl`, CONFIG SEMANAL, marcadores DRAFT

### Fixes
- `excel_rnd.py` path pickle · ZIP sin prefijo de carpeta

### Incidencia dataset RND
- Primera versión con 5 columnas → solicitado corregido antes de pipeline

---

## Week 18 · Mayo 2026

### Bugs #8–#15 corregidos (ver versiones anteriores)
### Features CR: WoW neutro, Third Party violet, WoW hotel canasta y channel
### Features RND: calc_rnd reescrito, WoW real, MIN_T=500K, 4 cols panel-row

---

## Week 17 · Abril 2026
- Bandas D, Sin Conversión separada, pills Súper Crítica, Channel agrupado CR, tabs hero
