# CHANGELOG · Proyecto PRICE · Supply Analytics

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
