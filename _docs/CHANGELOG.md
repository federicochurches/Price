# CHANGELOG · Proyecto PRICE · Supply Analytics

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
