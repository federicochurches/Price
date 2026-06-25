## Sesión W26-rnd-ar-card · 25-06-2026

**Contexto:** Implementar card AR (Análisis de Rendimiento) de NoDispo en la sección RND — 2 cards lado a lado en el HERO (KPI izquierda, AR derecha). La card AR es espejo de la KPI con pills de banda (Críticos/Bajo Rendimiento/Sin Conversión) en vez de pills de dimensión. Branch: `feat/rnd-ar-card`.

### Cambios principales

**1. `render_rnd_p1.py` — función `render_ar_card_nodispo()`**
- Card AR nueva: espejo estructural de `render_kpi_card_nodispo()`.
- Headline 3,43% negro (`var(--ink)`), badge banda, gauge, wow box, línea de tráfico.
- Pills de banda: mismo estilo outline magenta que las pills KPI (no relleno sólido).
- 3 paneles de hotel filtrados por banda: Críticos (Crítica+SúperCrítica, BK>0), Bajo Rendimiento (Revisar+Aceptable, BK>0), Sin Conversión (BK=0). Ordenados por %NoDispo desc.
- **Fix crítico:** `.reset_index(drop=True)` en los 3 splits de banda — sin esto los índices del DataFrame eran no-secuenciales y todas las filas caían en `rest_html` (ocultas), tabla vacía.
- Canvas id único `hrnd-arcard-nd` — evita colisión con `hrnd-ar-nd` del panel compartido.
- Import explícito `_kpi_ver_mas_btn` (leading underscore omitido por `import *`).
- Insertada en el HERO: `kpis-hero` pasa de 1 a 2 cards (grilla `repeat(auto-fit,minmax(300px,1fr))`).

**2. `assemble_unified.py` — JS + CSS**
- `ar_setBand(card, band, el)`: alterna paneles `.ar-{card}-panel` por `data-band`, aplica estilo KPI a pills (relleno `#FCE4F1` activa, transparente inactivas).
- Eliminado CSS residual del layout 2-zonas viejo: `#kpicard-nd { padding:0 !important }` + ocultar stats sparkline NoDispo.
- Cableado click hotel → `hrnd-arcard-nd`: `kpicard-ar-nd` reconocido en `cardKey` switch, `_isHotelRow` forzado a `true`, `_dimV2` forzado a `'hotel'`. Canvas `hrnd-arcard-nd` agregado a `_allHistCids` y `_rCids` (reset). Click desde KPI card también actualiza AR card.
- `min-height:48px` en `.kpi-tab-rows > div[data-hist-w21]` — filas KPI y AR de igual alto → cards alineadas verticalmente.

**3. `build_hist_entity.py` + `render_rnd_p1.py` — RND_PAIS_HIST**
- `build_rnd_hist()`: agregado bucket `pais` (agrupando por `PaisDestino`).
- `render_rnd_p1.py` `_build_rnd_hist_json()`: emite `RND_PAIS_HIST` junto con CORP/DEST/HOTEL.
- `assemble_unified.py` click handler: cuando `_dimV2 === 'pais'` usa `window.RND_PAIS_HIST` en vez de caer a `RND_CORP_HIST` → sparkline W18-W25 al clickear un país en vista País de KPI NoDispo.

**4. `calc_supply.py` — eliminar paso [11/10] inventory**
- El paso que actualizaba automáticamente el CONFIG de `inventory/calc_inv.py` fue eliminado. No pertenece al pipeline de Supply.

### Decisiones tomadas
- Panel "Análisis de Rendimiento" compartido (CR+RND, abajo) **se queda intacto**. La card AR nueva convive con él temporalmente.
- Próxima tarea pendiente: ocultar la card NoDispo del panel compartido cuando se está en modo RND (sin impactar CR).
- Branch `feat/rnd-ar-card` validado visualmente por Fede — **pendiente merge a main**.

### Archivos modificados
`render_rnd_p1.py` · `assemble_unified.py` · `build_hist_entity.py` · `calc_supply.py`

### Pendientes (próxima sesión)
1. **Merge `feat/rnd-ar-card` → `main`** tras validación completa.
2. **Ocultar card NoDispo del panel AR compartido en modo RND** sin impactar CR.
3. **Pipeline W26** — datasets nuevos, pipeline completo 8 pasos.
4. **Cleanup código muerto** — 32 IDs huérfanos (`check_html`).
5. **Reconciliar `PROMPT_INV.md`** con valores W25 reales.

---

## Sesión W25-sparkline-hist · 23-06-2026

**Contexto:** Feature request + bug fixes masivos: rellenar W19-W23 en todos los sparklines de las 3 cards KPI y AR con datos históricos reales (corpus pickling de dataset histórico de Bookability). Fill coloreado por banda.

### Cambios principales

**1. BK_CORP_HIST / BK_HOTEL_HIST / BK_DEST_HIST (nuevo)**
- Dataset `Dataset_bookability_historico.xlsx` (157.910 filas, W16-W24, 128 corps, 30K hoteles) procesado.
- `calc_bk.py`: calcula `corp_hist_bk` + `hotel_hist_bk` + `dest_hist_bk` (weighted avg por Books).
- `render_cr_p1.py`: emite `BK_CORP_HIST` (124 corps, 7 vals W18-W24), `BK_HOTEL_HIST` (2.964 hoteles, 237 KB), `BK_DEST_HIST` (2.485 destinos, 142 KB). Cada función carga desde PICKLE_BK (no D global que es CR).
- `js_override.js`: KPI BK hotel view usa `BK_HOTEL_HIST[label]`; cross-filter BK dest usa `BK_DEST_HIST[dest]`.
- `assemble_unified.py`: AR3 hotel usa `BK_HOTEL_HIST[label]`; cross-filter BK usa `BK_DEST_HIST` cuando vista es destino.

**2. Fill coloreado por banda en sparklines SVG (`render_historico_svg.py`)**
- Antes: área bajo la curva = fill neutro ACCENT + 7% opacidad.
- Ahora: n-1 segmentos trapezoidales, cada uno coloreado con `getBanda(vals[i]).c` al 13% de opacidad. Aplicado en CR y RND (regenerar ambos part1).
- Afecta: `h-bk-panel`, `h-bk-ar`, `hcr-panel-ef`, `hcr-panel-cv`, `hrnd-panel-nd`, `hrnd-panel-ipm`, `hcr-ar-ef`, `hcr-ar-cv`, `hrnd-ar-nd`, `hrnd-ar-ipm`.

**3. Sparklines W19-W23 — fix definitivo para KPI cards EF/CV/ND/IPM**
- Root cause: cuando `view === 'corp'` y el usuario hacía click en un hotel cargado lazily, el cross-filter usaba el nombre del hotel como corp → lookup fallaba → solo W24-W25 actualizaban.
- Fix `assemble_unified.py`: agregar `_isHotelRow = data-cf-corp !== '' && data-cf-corp !== data-hist-label`. Si es hotel row, saltear el bloque cross-filter.
- Lookup por corp hist: `CR_CORP_HIST[data-cf-corp][cardKeyH]` o `RND_CORP_HIST[data-cf-corp][cardKeyH]` concatenado con W25 actual.

**4. Fix 'destino' vs 'dest' mismatch**
- `_kpiView` guarda `'destino'` pero el lookup comparaba `=== 'dest'`.
- Fix: `(_dimV2 === 'dest' || _dimV2 === 'destino')` en CR y RND lookup. También en BK cross-filter.
- Resultado: clickear un destino en EF/CV/ND/IPM KPI ahora muestra W18-W24 reales de ese destino.

**5. AR1/AR2 handler conflict + BR/SC vacío**
- Root cause: el handler de `js_override.js` seteaba `_arCrossFilter[n].hotel = hotelName` al hacer click. Al cambiar a "Bajo Rend.", `_arFilterApply` filtraba por ese hotel (que estaba en Críticos, no en BR → 0 resultados).
- Fix: cambiar toggle de cross-filter a `data-selected` attribute. NO setear `_arCrossFilter.hotel` para hotel view (self-filter rule: dimensión propia no se auto-filtra).
- También: re-agregar early return en `_handleKpiCardHistClick` para AR1/AR2 hotel (evitar conflicto entre los dos handlers que generaba comportamiento invertido de doble click).
- AR1/AR2 sparkline con hist: la función JS del handler AR ahora busca `CR_CORP_HIST[data-cf-corp][metric]` con métricas `ef/cv` (CR) o `nd/ipm` (RND).

### Cobertura de hist W18-W24 por dimensión

| Dimensión | CR EF/CV | RND ND/IPM | BK |
|---|---|---|---|
| Corp | `CR_CORP_HIST` 63 corps | `RND_CORP_HIST` 111 corps | `BK_CORP_HIST` 124 corps |
| Dest | `CR_DEST_HIST` 1054 dests | `RND_DEST_HIST` 3052 dests | `BK_DEST_HIST` 2485 dests |
| Hotel | proxy corp (data-cf-corp) | proxy corp (data-cf-corp) | `BK_HOTEL_HIST` 2964 hoteles |
| AR3 | — | — | `BK_HOTEL_HIST` (directo) |

### Commits de esta sesión
- `9cc7d1db` — fix: corp self-filter eliminado · BK early return eliminado
- `8c2aea1a` — fix: cf.hotel en hasCf · CR_MEMBERSHIP · poolToCardRow prevVal
- `2115885e` — fix: CR_MEMBERSHIP solo CR pool · buildSerie endpoint
- `236c08ed` — fix: AR hotel self-filter + sparkline AR CIDs correctos
- `98cd4558` — fix: hist-reset despacha a panel+AR+global
- `f701a50b` — feat: BK_CORP_HIST W18-W24 · 124 corps (dataset histórico)
- `b4453609` — feat: BK_HOTEL_HIST AR3 + fill coloreado por banda sparkline
- `7fc2cf54` — feat: KPI hotel view usa corp hist W18-W23
- `a587241e` — fix: W19-W23 sparklines todas las cards · fill coloreado RND · AR1/AR2
- `315ac456` — fix: destinos W19-W23 · AR BR/SC vacío · AR doble click · BK_DEST_HIST

### Archivos modificados (repo)
- `render_historico_svg.py` — fill coloreado por banda
- `render_cr_p1.py` — BK_CORP_HIST / BK_HOTEL_HIST / BK_DEST_HIST (3 funciones nuevas)
- `assemble_unified.py` — _isHotelRow, 'destino' fix, AR1/AR2 early return, BK_DEST_HIST cross-filter
- `js_override.js` — AR hotel handler: toggle data-selected, sin cross-filter self, corp hist
- `calc_bk.py` — corp_hist_bk, hotel_hist_bk, dest_hist_bk desde dataset acumulado
- `reports/week-25/SUPPLY_W25.html` — regenerado (14.614 KB)

### Pendientes próxima sesión
- Validar visualmente todos los fixes de sparkline (corp/dest/hotel en las 3 cards + AR)
- Verificar fill coloreado en RND Availability
- Seguir con el flujo normal W26 cuando lleguen los datasets

---

## Sesión W25-hist-corp-fix · 23-06-2026

**Contexto:** Bug report de Fede: el canvas histórico de `hcr-global-ef` no actualizaba visualmente al seleccionar un corp diferente (GRUPO POSADAS después de Iberostar). La sesión consistió en diagnóstico sistemático del mecanismo histUpdate_.

### Root cause encontrado
El canvas SÍ actualizaba correctamente. El `window['histUpdate_'+CID]` en el IIFE funciona bien. El problema de diagnóstico fue que `hcr-global-ef` vive en **Part 1** (render_cr_p1.py), y cuando se agregaron console.logs a `historico_module.py`, solo se regeneró `assemble_unified.py` (Part 3/panel) — Part 1 quedó con la versión **anterior sin logs**. Así los logs de `hcr-global-ef` nunca aparecían, dando la ilusión de que la función no se ejecutaba.

**Solución:** al agregar el diagnostic log y regenerar TANTO `render_cr_p1.py` como `assemble_unified.py`, los logs confirmaron el funcionamiento correcto:
```
[histUpdate_] CID=hcr-global-ef w_c=78.65 w_p=97.11 → s[0]=97.11, s[last]=78.65 ✓
[histUpdate_] CID=hcr-panel-ef w_c=78.65 w_p=97.11 → s[0]=97.11, s[last]=78.65 ✓
```

**Por qué "no se veía el cambio":** los screenshots mostraron la curva del canvas con valores 81.26% → drop. Esto ES el dato real de GRUPO POSADAS (W24≈81.26%, W25≈78.65%). Visualmente parece similar a Iberostar (W24≈81.60%, W25≈70.75%) porque ambos son corps "Crítica" con rango de eficacia parecido. No era un bug — era similitud de datos.

### Cambios de código (permanentes)
- **`historico_module.py`:** expone `window['histUpdate_'+CID]` desde cada canvas IIFE. Función recibe (w_c, w_p, w_a, lbl), llama buildSerie + drawCanvas internamente. Bypasea el event system (que tenía race conditions con _kpiPillRender).
- **`assemble_unified.py`:** corp handler usa `window['histUpdate_'+cid]` directo con setTimeout(50ms) en lugar de dispatch de evento `hist-update`. Esto elimina la race condition entre el event listener asíncrono y la ejecución sync de _kpiPillRender.

### Lección aprendida crítica
**Al modificar `historico_module.py`, regenerar TODOS los scripts que lo importan**, no solo uno:
- `assemble_unified.py` genera los canvases del panel (`hcr-panel-ef`, etc.)
- `render_cr_p1.py` genera los canvases globales (`hcr-global-ef`, etc.)
- `render_rnd_p1.py` genera los canvases RND
Si solo se regenera uno, los canvases del otro quedan con la versión vieja del módulo.

### Commits de esta sesión
- `632fc3ab` — diag: console.log en histUpdate_ y corp handler
- `980f76988c1e` — diag: console.log en hcr-global-ef (regenerado Part1 CR)
- `e9e7e393761c` — fix: histórico corp funcional · histUpdate_ directo · sin logs diagnóstico

### Archivos modificados (permanentes en repo)
- `historico_module.py` — expone histUpdate_
- `assemble_unified.py` — corp handler con histUpdate_ directo
- `reports/week-25/SUPPLY_W25.html` — regenerado (13,915 KB)

---

## Sesión W25-continuación · 22-06-2026

**Contexto:** Continuación de la sesión W25. Fixes de mail, diagnóstico Inventory, auto-config.

### Supply

**`calc_supply.py` — paso 11:** al terminar el pipeline, actualiza automáticamente `inventory/calc_inv.py` CONFIG (WEEK / WEEK_NUM / VOL_NUM / SNAPSHOT_DATE). Para W26+ el flujo es: correr Supply → `git checkout origin/main -- calc_inv.py` → `python run_inv.py --commit`. Sin edición manual del CONFIG nunca más.

**`render_mail_v3.py` — fixes adicionales:**
- Auto-fetch `INV_PP_PREV` desde HTML de semana anterior en GitHub (urllib.request) — funciona desde W26 sin config manual.
- Gap card: gauge añadido + badge WoW (delta invertido: gap baja = verde). Gauge neutro `#8A8377`.
- BK WoW fallback desde `historico_data.HIST_DATA['bk']['bookability']['global'][-1]` cuando pickle no tiene semana anterior. W25: −0.25pp (98.42% vs 98.67% W24).
- IPM card eliminada. NoDispo full-width (`grid-column:1/-1`).

### Inventory — diagnóstico completo

**FechaCreacion (sin acento):** el NUEVO_FORMATO rename en línea 109 ya lo manejaba — no era el bug.

**Diagnóstico definitivo:** el dataset `dataHoteles_contratos.xlsx` original no incluía los 44 hoteles nuevos de W25 (IDs 692116-692199). Los hoteles no existían en el archivo → netnew=0 es correcto para ese dataset. Fede actualizó el dataset con los 44 hoteles.

**snap_date fix (`calc_inv.py`):** `_snap_date = date.today()` en lugar de `date.fromisocalendar(YEAR_ACTUAL, WEEK_NUM, 7)` (domingo). Los hoteles creados el lunes de generación del dataset (W26 ISO) se reatribuyen al WEEK_NUM del CONFIG. Garantiza cobertura completa independientemente del día en que se corra.

**Bug descubierto en sesión:** el commit del snap_date fix usó como base `/mnt/project/calc_inv.py` (con CONFIG W24) en vez del archivo ya actualizado → el snap_date fix sobrescribió el CONFIG W25 con W24. Fix: commitear `inventory/calc_inv.py` con WEEK=W25 + snap_date fix en un solo commit correcto (`ebeece5385a7`). Luego paso 11 de calc_supply.py lo mantiene actualizado automáticamente.

**Aprendizaje:** al combinar CONFIG + código fix en calc_inv.py, siempre usar la versión del repo como base (git checkout del archivo) para no pisar cambios previos.

### Commits de continuación
- `a1bac8d5` — render_mail_v3 todos los fixes
- `2a17315c` — calc_inv snap_date fix (CONFIG W24 — incorrecto)
- `ebeece5385a7` — calc_inv CONFIG W25 + snap_date fix (correcto)
- `1944877e` — calc_supply paso 11 auto-update inv CONFIG
- `0ef7cac1` — PROMPT_CORE + PROMPT_INV + HISTORIAL W25
- `1fe08a23` — index.html W25 badge correcto

---

## Sesión W25-pipeline · 22-06-2026

**Contexto:** Pipeline W25 completo + fixes mail + diagnóstico y fix calc_inv.

### Supply — cambios de código

**`calc_supply.py`** — CONFIG actualizado a W25 (WEEK/VOL_NUM/PERIODO/FECHA_PUB).

**`historico_data.py`** — ventana rotada W17-W24 → W18-W25. Drop W17, add W24 en todos los scopes (global/op/cug/b2c). W24 global desde PROMPT_CORE; per-canasta desde M[canasta_w24] del pickle W25. `SEMANAS=['W18'...'W25']`. Bug resuelto: gráficas históricas mostraban W24 como último punto.

**`calc_bk.py`** — fix `agg_dim_wow`: cuando `df_prev` está vacío (dataset BK solo trae W25, sin W24), retorna cur con WoW=0 en vez de romper con KeyError en `g_prev[[col,...]]`. Fix adicional en global: `bk_prev < 0.1` → WoW = None (evita mostrar +98pp).

**`render_mail_v3.py`** — múltiples mejoras en una sola sesión:
- **Card IPM eliminada** — NoDispo ocupa full-width (`grid-column:1/-1`).
- **BK WoW correcto** — cuando `bk_prev=0` (sin semana anterior en pickle) usa `historico_data.HIST_DATA['bk']['bookability']['global'][-1]` como fallback (W24=98.67%). Badge muestra −0.25pp.
- **Inventory habilitado** — valores W25 reales: PP=58.892, GAP=11.108, Avance=84.1%, Ritmo=411/sem, Semanas=27. Extraídos automáticamente del INVENTORY_W25.html en GitHub.
- **Auto-fetch `INV_PP_PREV`** — `urllib.request` lee `actual` del HTML de la semana anterior desde GitHub. Elimina la necesidad de hardcodear el valor cada semana. Funciona desde W26 en adelante sin config manual.
- **Gap card**: gauge añadido + badge WoW (delta invertido: gap baja = verde). Badge no aparece cuando WoW=0.
- **Gauge Gap**: color neutro `#8A8377` (era cyan).

**Métricas W25 confirmadas:**
- CR Eficacia: 95.68% (+0.11pp) · CR ConvRate: 0.75% (−0.07pp)
- RND %NoDispo: 3.34% (+0.30pp) · BK: 98.42% (−0.25pp vs W24 histórico)
- Inventory PP: 58.892 (0 netnew en W25 — ver nota abajo)

### Inventory — diagnóstico y fix

**Diagnóstico `FechaCreacion`:** investigación completa del 0 netnew en W25.
- Campo usado: `FechaCreacion` (rename automático a `FechaCreación` en línea 109 del NUEVO_FORMATO block — ya estaba manejado).
- Diagnóstico: ningún PP hotel tiene `FechaCreacion` entre 15-21 jun en el dataset.
- Causa raíz: **el dataset se genera el lunes 22** (hoy, W26 ISO). Los hoteles nuevos tienen `FechaCreacion=2026-06-22`, fuera del corte `_snap_date = domingo(W25) = 21 jun`.

**`inventory/calc_inv.py`** — fix snap_date:
- `_snap_date = date.today()` en lugar de `date.fromisocalendar(YEAR_ACTUAL, WEEK_NUM, 7)`.
- Línea de reatribución: hoteles con `fecha_dt > _week_sunday` → `yw = snapshot_yw` (atribuidos al WEEK_NUM actual, no a W26).
- Esto garantiza que hoteles creados el lunes siguiente al cierre de semana siempre se cuenten en el reporte correcto.
- **Config también actualizado:** WEEK="W25", WEEK_NUM=25, VOL_NUM="25", SNAPSHOT_DATE="22 de Junio de 2026".

**Pendiente inmediato:** re-run `python run_inv.py --commit` con el fix para generar INVENTORY_W25.html correcto (con netnew reales del 22 jun) → luego regenerar Mail_W25.html con WoW de Inventory real.

### Commits de sesión
- `59722b4d` — Supply W25 + Excels
- `409444f3` — docs W25
- `faa23555` — calc_inv CONFIG W25
- `a1bac8d5` — render_mail_v3 todos los fixes
- `2a17315c` — calc_inv snap_date fix

---

## Sesión W25 · 22-06-2026

**Contexto:** Pipeline W25 completo. Datasets: CR W25, RND W25, BK W25, CR W24, RND W24.

**Cambios de código:**
- `historico_data.py` — ventana histórica rotada W17-W24 → W18-W25 (drop W17, add W24 per-canasta y global). SEMANAS=['W18'...'W25']. Valores W24 global desde PROMPT_CORE; per-canasta desde M[canasta_w24] del pickle W25.
- `calc_bk.py` — fix `agg_dim_wow` para manejar `df_prev` vacío (Dataset_bookability_W25.xlsx solo contiene W25, sin historial W24). WoW BK = N/A esta semana.
- `calc_supply.py` — CONFIG actualizado a W25 (PERIODO 15-21 jun 2026, FECHA_PUB 22 jun 2026).

**Métricas W25:**
- CR Eficacia: 95.68% (+0.11pp vs W24) — Exitosa
- CR ConvRate: 0.75% (-0.07pp vs W24) — Crítica
- RND %NoDispo: 3.34% (+0.30pp vs W24) — Aceptable
- BK Global: 98.42% (sin WoW — dataset solo W25)
- HTML: 13.57MB

**Issues resueltos en sesión:**
- BK df_prev vacío → pipeline rompía en agg_dim_wow (fix graceful no-WoW)
- Gráficas históricas mostraban W24 como última semana → SEMANAS no rotada

**3 fixes de deuda técnica pre-W25 verificados visualmente (todos OK):**
1. WoW per-canasta RND — badge WoW tráfico en KPI cards b2c/op/cug
2. Dedup RND_D ~700KB — check_html confirma 0 dups intra-canasta RND
3. Mail en _email/week-25/ — incluido en ZIP correctamente

**Commit:** 59722b4de7a2 · feat: Week 25 · Supply unificado + Excels consolidados · 15-21 jun 2026

**Archivos modificados:** historico_data.py · calc_bk.py · calc_supply.py · reports/week-25/SUPPLY_W25.html · checkrates/week-25/* · rates-nodispo/week-25/* · _email/week-25/Mail_W25.html · index.html

---

# 📚 HISTORIAL DE SESIONES · Proyecto PRICE
**Arqueología de sesiones W16-W20 · Solo consultar ante bugs misteriosos o decisiones de contexto histórico**

> Este archivo NO se necesita para ejecutar el pipeline semanal.
> Para el contexto operativo vigente → ver `PROMPT_CORE.md`.


## Sesión W24-pills · 22 Jun 2026 · Pills de dimensión inactivas → MAYÚSCULA

**Problema (3er intento):** Fede reportó por tercera vez que "las pills siguen en minúscula en la versión commiteada". Los dos misses previos fueron por buscar en el set equivocado (badges de severity, que ya estaban uppercase vía `text-transform`). Esta vez se cazó en el HTML committeado: las pills del **selector de dimensión** (Destino/Corp/Hotel/Channel en CR · País/Destino/Corp/Hotel en RND) usaban `text-transform:none` en la **inactiva** — decisión del W24-layout (activa MAYÚS / inactiva title-case). Eso renderizaba "Corp", "Hotel", "Channel", "País" en title-case = lo que se veía "en minúscula".

**Decisión Fede:** todas las pills en MAYÚSCULA; la activa se distingue por el **relleno** (claro) + borde, no por el case.

**Cambios:**
- `render_cr_p1.py`: `text-transform:none → uppercase` en las 3 pills inactivas (`_PI` L55, `_PILL_INACT` L170/L338).
- `render_rnd_p1.py`: idem en las 2 pills inactivas (`_PILL_INACT` L185/L278).
- `assemble_unified.py`: `kpi_setView` L554 — `pill.style.textTransform = active ? 'uppercase' : 'none'` → **siempre** `'uppercase'`. Sin esto, al cambiar de dimensión el JS volvía a poner title-case en las inactivas.

**⚠️ Casi-regresión cazada por el grep de contexto:** el `sed` global `s/text-transform:none;/.../g` tocó por error un 3er `text-transform:none` en `render_rnd_p1.py` L334 que **no es pill** — es el subtítulo del IPM (`· Income Per Million · GB USD por millón`), que va en minúscula a propósito (el padre es uppercase). Revertido a `none` con `str_replace`. **Aprendizaje:** `text-transform:none` no es exclusivo de pills; antes de un sed global verificar contexto de cada ocurrencia.

**No se tocaron:** tabs de canasta (`.c-chip`, ya uppercase en `demo_css_w22.css`) ni pills de banda AR (Críticos/Bajo Rendimiento/Sin Conversión).

**Verificación:** 0 pills inactivas con `none`, 5 con `uppercase`, subtítulo IPM con `none` intacto (1). Regenerado part1 CR+RND (`VOL_NUM=24`) + reensamblado (`/tmp/SUPPLY_W24.html`, 15.717.287 B). Validado visual Fede. `PROMPT_CORE.md` regla de pills actualizada (inactiva ahora uppercase, ⚠️ no volver a `none`).

**Q clone repo local:** Fede preguntó si conviene reclonar el repo local. Respuesta: no necesario — el `git reset --hard origin/main` previo ya dejó el working tree idéntico al remoto; un clon no trae los gitignored (datasets, tokens, `_seguimiento/`). Recomendado quedarse con el repo actual.

---

## Sesión W24-mail · 22 Jun 2026 · Mail con Bookability + Inventory · KPIs en neutro

**Contexto:** Fede pidió regenerar el Mail con Bookability + Inventory. La "falla silenciosa" de W24 no era un crash — `render_mail_v3.py` genera bien, simplemente **no se corría** en el pipeline.

**Cambios en `render_mail_v3.py`:**
- Carga `PICKLE_BK` y agrega **Bookability** (98,67%, banda Exitosa via bandas de Eficacia) como **card full-width** en la sección Connectivities.
- **Inventory:** los `INV_*` (antes hardcodeados a 0 → bloque omitido) ahora se leen por **env var** (`INV_PP`/`INV_GAP`/`INV_PCT_AVANCE`/`INV_RITMO`/`INV_SEMANAS`/`INV_TARGET`). Para W24 se pasaron los números del `INVENTORY_W24.html` publicado: PP 58.895 · gap 11.105 · avance 84,1% · 28 sem · ritmo ~397.
- **KPIs en neutro** (pedido de Fede): los 6 gauges → gris `#8A8377` (sin band-color verde/ámbar/rojo) · números KPI → `#161616` (las 4 clases `.X-color` apuntan a neutro; identidad de sección queda en el borde izquierdo + dot). **WoW mantiene color** verde/rojo (señal direccional; Fede lo aprobó así).
- Fix cosmético: el `print` del tamaño tenía `{{ }}` escapados (imprimía literal).

**Pendiente:** engancharlo a `calc_supply.py` para que el Mail se genere solo cada semana (pasándole `PICKLE_BK` + los `INV_*`); para INV totalmente automático faltaría wirear los números del pipeline de Inventory.

**Validado:** visual de Fede ("Perfecto"). El Mail es un artefacto de email (no se commitea al repo) — se entrega `Mail_W24.html`; se commitea solo `render_mail_v3.py`.

---

## Sesión W24-histbadges · 22 Jun 2026 · Propagación Opción B a histórico + severity + AR · Aceptable blanco · git troubleshooting

**Contexto:** Fede señaló (con screenshot) que los badges del panel **Evolución Histórica** seguían pálidos pese al fix de Opción B del W24-layout. Al investigar aparecieron **3 superficies** que no se habían cubierto, cada una con su propio mapa/part.

**Diagnóstico — por qué quedaron pálidas:**
- **Panel histórico:** `historico_module.py` `_BANDA_COLORS` YA estaba en Opción B en la fuente (working tree), pero **nunca se commiteó ni se regeneró el HTML con él** — el commit W24-layout (`9d2c043`) no incluyó `historico_module.py` y horneó part1 con el módulo viejo. Mismo patrón "fix en fuente, no propagado al artefacto" que ya nos mordió antes.
- **Tablas de severity** (`render_severity` en p2 vía `banda_colors()`) y **cards AR** (`sev_badge_html_p2`): part2 se generó **antes** de migrar `BANDA_COLORS` y nunca se regeneró → colores viejos horneados.
- **`BC` de `AR3_CANVAS_JS`** (assemble) seguía con la paleta pálida + semanas stale W16-W23.

**Cambios:**
1. Migrado `BC` de `AR3_CANVAS_JS` a Opción B (assemble). (Las semanas W16-W23 stale quedaron como pendiente aparte — no se tocaron.)
2. **Aceptable fg `#5C3A00` → `#FFFFFF`** (blanco) en los **8 mapas** (los 6 previos + `historico_module._BANDA_COLORS` + `BC` de AR3). Fede lo pidió "blanco como las otras". **Caveat documentado:** blanco sobre el ámbar `#FBBF24` tiene contraste bajo (se lee flojo); se dejó así por pedido explícito, con la opción de oscurecer el bg a ~`#D97706` si molesta.
3. Regenerado **part1 + part2** CR/RND con **`VOL_NUM=24`** + reensamblado. (Casi se cuela una regresión: regeneré part1 sin `VOL_NUM` la primera vez → `wow_box` salió W19/W20; el diff tag-por-tag contra el publicado lo cazó. `VOL_NUM=24` es obligatorio al regenerar parts.)

**Validación:** diff tag-por-tag contra el HTML publicado (`8e1788f4`) = **236 líneas, 100% colores de banda**, sin tocar datos/métricas/labels (filtro de no-color → vacío). Visual de Fede ("Todo ok").

**git troubleshooting (máquina de Fede):** los commits por Git Tree API van directo al remoto y no tocan el git local, así que su working tree quedó "detrás" + a mitad de un merge conflictivo. Clave: su `inventory/calc_inv.py` LOCAL tenía trabajo W24 (UTF-8 stdout, `DEST_RENAME` Mexico City, ancla histórica) que NO estaba en el remoto (el repo tenía la versión W23). Se commiteó la versión W24 del proyecto (`/mnt/project/calc_inv.py`, md5 idéntico) al repo (commit `1a698eb0`) ANTES de que Fede resetee, para que `git reset --hard origin/main` no la pierda. Pendiente del lado de Fede: confirmar diff de `calc_supply.py` (se le abrió `less`; salir con `q`, usar `git --no-pager diff`) antes del reset.

**Archivos:** `historico_module.py`, `render_helpers.py`, `js_override.js`, `assemble_unified.py`, `reports/week-24/SUPPLY_W24.html` + docs · commits `1a698eb0` (calc_inv) + el de esta sesión.

---

## Sesión W24-layout · 21 Jun 2026 · Ajustes de layout: badges sólidos + pills 2-líneas + tabs simétricas

**Contexto:** tanda de ajustes visuales pedidos por Fede sobre `SUPPLY_W24.html`, iterando con validación visual. Hubo dos malentendidos de terminología resueltos en el camino (Fede usó "chips" para los badges de severity, no los chips de canasta; y "pills activas en verde" se refería a la segunda línea de cross-pills, no a la primera línea de dimensión).

**Cambios (todo en fuente, nunca el HTML):**
1. **Badges de severity → Opción B (sólido pleno, texto claro).** Se presentó un preview con 3 niveles (actual / A tinte profundo / B sólido pleno); Fede eligió primero A, luego B. Paleta final: Exitosa #1A6B4A/blanco · Aceptable #FBBF24/#5C3A00 · Revisar #F97316/blanco · Crítica #C0392B/blanco · Súper Crítica #2D2828/blanco · Sin Conv #8A8377/blanco. **Aprendizaje:** el color de banda está duplicado en **6 mapas** (`BANDA_COLORS` en render_helpers + `_AR_BANDA_C`, `getBanda` interno, mapa ~L3059, `ar3_bandColors` en js_override + `_bk` banda_colors en assemble). Se migraron por **par completo** (bg+fg juntos en todos sus formatos: objeto JS con/sin espacio, array, python quoted, bare getBanda con prefijo `lbl:`) — un replace de hex suelto habría roto las pills/accent-soft que comparten #E1F5EE/#FCE4F1.
2. **Esquema de pills en 2 líneas.** Primera línea (selector de dimensión) = color de sección (CR violet / RND magenta; activa relleno claro + MAYÚSCULA, inactiva outline + title-case). Segunda línea (cross-filter, al seleccionar un elemento) = SIEMPRE verde (CR y RND). Antes la primera línea activa estaba en verde y las cross de CR en violet. Tocados: `_PILL_ACTIVE`/`_PILL_INACT` (render_cr_p1/render_rnd_p1), `kpi_setView` (`sec_col`/`sec_bg`, assemble), `_kpiCrossFilterPillsRender` (assemble, `GR_*` siempre verde) + gemelo AR (js_override).
3. **Tabs de canasta simétricas + alto.** `.c-chip`: `flex:1`+`justify-content:center` (mismo ancho, llenan la barra) · `height:54px`→`min-height:54px` (estiran al alto de la barra de KPIs) · `:last-child` sin border-right (evita doble línea con el bloque KPI). El color de los chips se revirtió (Fede no lo pidió — solo simetría/alto).
4. **Severity badges sin target.** `banda_pill` ya no renderiza el `· Target ≥ X`; solo la banda. El "Target: Bookings" del masthead es otro elemento (intacto).

**Validación:** jsdom en cada paso (badges con texto blanco, primera línea = sección, cross-pills verdes, kpi_setView aplica colores+uppercase, 0 errores) + validación visual de Fede antes de commitear. Sin cambio de tamaño del HTML (solo strings de color/estilo).

**Archivos:** `demo_css_w22.css`, `render_helpers.py`, `render_cr_p1.py`, `render_rnd_p1.py`, `assemble_unified.py`, `js_override.js`, `reports/week-24/SUPPLY_W24.html` + docs.

---

## Sesión W24-rnd-percanasta · 21 Jun 2026 · Desglose per-canasta real de KPI cards RND + dedup _sb RND (−1,21MB)

### Contexto
Tras armar `check_html.py`, el barrido sobre W24 mostró `RND_CARD_TABS` byte-idéntico en las 4 canastas + `RND_D._sb` 4×. Fede clarificó el modelo de datos: **Global = total; cada canasta (B2C/Opaco/Ultra Opaco) = un desglose del Global por DistributionCategory.** → el idéntico-4× de RND_CARD_TABS NO era para deduplicar sino un **gap funcional**: las KPI cards de RND mostraban global en todas las canastas. (`render_rnd_p1.py` L440 tenía el comentario explícito "Usar TAB global para todas las canastas — por ahora global".)

### Fix 1 — desglose per-canasta (correctitud)
La data per-canasta YA estaba en el pickle: `CANASTA[c]` tiene `agg_pais`/`agg_dest`/`agg_corp`/`agg_hotel` con %NoDispo/IPM/Trafico/Bookings/bandas/WoW. `render_rnd_p1.py`: el build de `RND_CARD_TABS` ahora selecciona la fuente por canasta — global usa `TAB_NoDispo`/`TAB_RPM`, b2c/op/cug usan sus `agg_*` (`_AGG_BY_TKEY` + `_GLOBAL_SRC`; el row-builder re-ordena cada df). Resultado: 4 canastas distintas (b2c top Grecia 35,25% vs global Dinamarca 48,82%; corp 94/79/90/89). **Caveat:** los `agg_*` per-canasta no traen `Trafico_WoW_pct` (ni `agg_hotel` el `%NoDispo_W18`) → r[6] traf_wow y r[10] hist salen vacíos per-canasta (`.get(default)`, sin crash). Enriquecer = follow-up en calc_rnd.py.

### Fix 2 — dedup _sb RND (tamaño)
Los `_sb` de RND (`hotels_dnc_sb`/`br_sb`/`sc_sb`) se construyen de `g_hotel_rnd` (global, render_rnd_p2 L238) → idénticos 4×. `render_rnd_p2.py` los borra de `RND_D['b2c'/'op'/'cug']` tras `build_rnd_d`. `js_override.js` `_arRows`: `_sbData` generalizado a CR_D.global/RND_D.global según `isCR` (los reads ya tenían `|| dd[sbKey]`). RND_D 5,83→4,54MB.

### Validación
jsdom t10: 0 errores · RND_CARD_TABS nd[pais] 4 hashes distintos · b2c top Grecia vs global Dinamarca · RND_D.b2c._sb AUSENTE, global=1000 · RND `_arRows` 4 canastas OK · **CR intacto** (global/b2c crit=180/180, la generalización de `_sbData` no rompió CR). HTML 16,99→14,99MB (−1,21MB; total sesión 22→14,99, −7MB). + visual Fede.

### Nota meta
`check_html` no solo cazó bloat — destapó el gap funcional de RND per-canasta. Valida la tesis: hacer las clases de problema detectables en cada build encuentra cosas que el ojo no ve. Dups que quedan (intra-canasta `hotels==hotels_dnc`, `hotels_sc==hotels_ipm_sc` ~700KB) son más delicados (distintas keys, distintos consumidores) — no urgentes.

---

## Sesión W24-check-html · 21 Jun 2026 · Auditoría automática del HTML (composición · duplicados · presupuesto · huérfanos)

### Contexto
Tras encontrar tanto código muerto / data duplicada en el refactor (CR_HOTELS, _sb 4×, panel w22, handlers AR dim), Fede preguntó cómo *garantizar* que no haya más. Respuesta: no auditar más fuerte, sino hacer estas clases detectables automáticamente en cada build. → `check_html.py`.

### check_html.py
4 chequeos sobre el HTML generado:
1. **COMPOSICIÓN** — balance-match de cada `var NAME = {`/`[` top-level (consciente de strings), peso + % del total, ordenado.
2. **DUPLICADOS** — parsea los vars JSON, camina 2 niveles, hashea (md5) arrays/objetos ≥4KB, agrupa por hash → reporta los emitidos ≥2× con bytes redundantes. Es lo que habría cazado CR_HOTELS y los _sb 4× desde el inicio.
3. **PRESUPUESTO** — total + delta vs baseline local `.html_budget.json` (gitignored, regenera por build). Caza regresiones de tamaño.
4. **HUÉRFANOS** — `getElementById('X')` literales sin `id="X"` en el DOM · `onclick="fn("` sin `function fn`/asignación. (Caveat: IDs dinámicos `'ar'+n+'-th'` no se chequean → "candidatos a revisar".)

Expone `report(path, update=False)` (invocable) + `main()` (argv). Enganchado al final de `assemble_unified.py` en try/except no-fatal (si falla, el build ya está escrito). `.html_budget.json` → .gitignore.

### Barrido inicial sobre W24
- **DUPLICADOS ~4,44MB**, casi todo RND: `RND_CARD_TABS` 4× (global=b2c=op=cug, 806KB) + sub-arrays nd (503KB)/ipm (303KB) 4×; `RND_D._sb` 4× (sc_sb 514KB + dnc_sb 486KB + br_sb 321KB); internos `hotels==hotels_dnc` y `hotels_sc==hotels_ipm_sc` (~180KB c/u por canasta); `BK_CARD_TABS` 4× (98KB). Confirma que RND tiene los MISMOS patrones que CR (las dedup A/B aplicables análogamente).
- **HUÉRFANOS 32 IDs**: panel `w22-*` completo (`w22-ph`/`pd`/`td`/`tab-lbl-*`/`alertas-sub`/`report-tag`…) + elementos AR dim (`ar1-col-m`/`ar2-col-m`/`ar3-th-dim`/`ar3-books`/`ar3-vol`/`ar3-wow-pill`/`ar-strip-bk`…) + `tab-bk-destino`/`vch-d`/`vch-h`/`sb-panel-th`. Cero onclick sin función. Confirma el código muerto del panel w22 + handlers AR dim (#4).

### Pendientes que esto abre
- **Dedup RND** (~3MB, RND_CARD_TABS 4× + RND_D._sb 4× + internos) — mismo patrón bajo riesgo que B de CR. **PRÓXIMO.**
- **Cleanup #4** (código muerto) ahora trazable: tras limpiar, los IDs huérfanos correspondientes deben desaparecer del reporte.

---

## Sesión W24-B-sbdedup · 21 Jun 2026 · Dedup de los pools _sb del searchbox (−0,84MB)

### Contexto
Opción B del lazy AR CR (portar arrays hotel de `CR_D` al pool). Al medir `CR_D` por canasta se vio que el bloat real **no** eran los band arrays sino los `_sb` (pools del searchbox): `hotels_crit_sb` (180) / `hotels_br_sb` (645) / `hotels_sc_sb` (968) aparecían con **el mismo conteo y md5 en las 4 canastas** → duplicados 4× (~277KB × 4, ~840KB redundantes). Causa: se construyen de `g_hotel` (pool global, L281-286 de render_cr_p2), no de la canasta → globales por diseño.

### Cambios
- `render_cr_p2.py`: tras `CR_D = build_cr_d()`, borra los `_SB_KEYS` (`hotels_crit_sb`/`br_sb`/`sc_sb`/`dnc_sb`) de `CR_D['b2c'/'op'/'cug']`; quedan solo en `['global']`.
- `js_override.js` `_arRows`: `var _sbData = (isCR && CR_D.global) ? CR_D.global : dd;` y los dos reads (`sbRows` card1 L1120, `sbRows2` card2 L1151) usan `_sbData[sbKey] || dd[sbKey]`. RND sin tocar (lee su propio `_sb` de `RND_D[canasta]`).

### Validación
jsdom t9: 0 errores · `_sb` solo en global (180/645/968), AUSENTE en b2c/op/cug · `_arRows` global idéntico (crit=180/br=645/sc=968) · per-canasta lee `_sb` de global (b2c crit=180, 175 extras "Los Aluxes Hotel") · RND nd crit=1000 intacto. HTML 17,87→16,99MB. + visual Fede.

### Decisión — resto de B NO se hace
Los band arrays globales (~318KB) serían lo único más portable al pool (per-canasta 538KB se queda en DOM igual que las KPI cards). 318KB a cambio de tocar el formato de fila de las AR cards validadas = mala relación riesgo/beneficio. Se cierra B con la dedup. RND `_sb` probablemente tiene el mismo patrón 4× → follow-up de bajo riesgo cuando se ataque `RND_D` (5,6MB).

### Meta — cómo evitar acumular esto (planteado por Fede)
Propuesto `check_html.py` post-assemble: reporte de composición (peso de cada var top-level), detector de blobs byte-idénticos (md5), presupuesto de tamaño con delta vs build previo, y chequeo de huérfanos (IDs/`onclick` que el JS espera pero no están en el DOM). Más barrido único para inventariar lo existente. **Pendiente de construir** (Fede iba a decidir; quedó en standby tras "avanza con el commit").

---

## Sesión W24-A-dedup · 21 Jun 2026 · Elimina duplicación CR_HOTELS (−0,87MB) + tabla histórica W24

### Contexto
Pendiente #1 (lazy-ificar AR cards CR). Al scopearlo se vio que es grande: los arrays hotel de `CR_D` (1,93MB) se leen vía el accessor genérico `data()` en 15+ sitios de js_override (AR cards `_arRows` + variantes `hotels_ipm_*` + pools `_sb`), y `CR_HOTELS` (0,84MB) es un duplicado parcial. Se partió en **A** (matar la duplicación, seguro) + **B** (portar `CR_D` al pool, grande, sesión dedicada). Esta sesión = **Opción A** + el cosmético #4.

### Opción A — eliminar CR_HOTELS
`CR_HOTELS` se extraía de `CR_D` en render_cr_p2 (copia de hotels/crit/br/sc/cv). Su único consumidor era el `getRows` del panel w22 "Análisis de Rendimiento" en assemble — **panel que ya no existe en el DOM** (reemplazado por las AR cards; jsdom confirma `w22-th` no existe). Las AR cards y `data()` ya leían `CR_D` directo.
- `assemble_unified.py`: quitado el branch `if (CR_HOTELS...)` del `getRows`; queda `d2[key2] || dg[key2] || d2.hotels` (con fallback global de la key, preservando la semántica de `CR_HOTELS.global[key]`).
- `render_cr_p2.py`: eliminada la extracción + `CR_HOTELS_JSON` + `var CR_HOTELS=...` del PART2.
- `demo_js_main.js`: quitado `CR_HOTELS` del comentario de vars inyectadas.

### #4 — tabla "Datos históricos reales"
Header `W16-W22`→`W16-W24` + fila W24 (95,57% · 0,82% · 3,04% · $611, de `M.global_w24` de los pickles) + nota de que la ventana viva del módulo es móvil.

### Validación
jsdom t8: 0 errores · `typeof CR_HOTELS`=undefined · `CR_D.global` intacto (crit=110/br=405/sc=443/cv=1000) · `data()===CR_D.global` · `_arRows(1,*)`=180/645/968/1000 · `_arRows(2,crit)`=1000 · per-canasta b2c OK. HTML 18,78→17,87MB (−0,87MB). + visual Fede "Todo ok".

### Pendiente — Opción B (sesión dedicada)
Portar arrays hotel de `CR_D` (~1,9MB) al pool: enriquecer `CR_HOTEL_POOL` con `_sb`/`ipm`/campos que esperan los renderers + recablear los 15+ sitios `data().hotels_*`. Riesgo medio (toca AR cards validadas). RND (`RND_D` ~5,6MB) es un follow-up análogo.

---

## Sesión W24-hist-semanas · 21 Jun 2026 · Histórico W17-W24 dinámico + serie BK alineada al dato real

### Contexto
Pendiente #2 ("`_SEMANAS_HIST` stale W16-W23→W17-W24"). Resultó multi-punto: `_SEMANAS_HIST` (js_override.js L7, hardcodeado W16-W23) PISA los labels de TODOS los tooltips de canvas históricos por diseño ("SIEMPRE usar `_SEMANAS_HIST`"), aunque los datos ya eran W17-W24. Además se detectó que la serie BK de `historico_data.py` estaba **corrida una semana** vs `hist_by_week` del pickle (dato real): `historico_data W17=98.22` = `hist_by_week W18`; faltaba el W17 real (98.44). Las series CR ef/cv y RND nd/ipm SÍ estaban bien.

### Decisión
La última semana debe ser **W24** (8-14 jun) en TODAS las series; W25 (15-21 jun) aún no corrió. → ventana **W17-W24**, fuente BK autoritativa = `hist_by_week` (dato real, W24=98.67). Semanas dinámicas (ventana móvil): el año que viene W25 se auto-ajusta a W18-W25 sin tocar código.

### Cambios aplicados
**assemble_unified.py:** import `SEMANAS as _HSEM` de historico_data. Cómputo dinámico: `_SEM_JS`, `_SEM_BASE`, `_AR3_BK=[round(DB['hist_by_week'][w]['bk']*100,2) for w in _HSEM …]`. En FOOTER_JS (al embeber js_override): `.replace('var _SEMANAS_HIST = ["W16"…];', 'var _SEMANAS_HIST = {_SEM_JS};')`. Antes de GLOBAL_PANEL_SCRIPT: `AR3_CANVAS_JS` (histórico BK duplicado, era stale W16-W23 + VALS_DEF hardcodeado) → `SEMANAS` y `VALS_DEF` inyectados dinámicos desde `hist_by_week`.

**historico_data.py:** BK global `[98.22,98.26,98.17,98.25,98.40,98.43,98.43]` → `[98.44,98.22,98.26,98.17,98.25,98.40,98.43]` (W17-W23 real de `hist_by_week`; W24 dinámico).

**render_cr_p1.py (OUTPUT):** la card BK `h-bk-global` (L773, `_rh('bk',…)`) importa `historico_data` → regenerar part1_cr tomó el BK corregido. (SOURCE de render_cr_p1.py sin cambios en esta sesión.)

### Validación
jsdom (t7.js): los 10 canvas en `_HIST_CANON` con sem=W17-W24. BK consistente: `h-bk-global` y `h-ar3-bk-global` ambos `vals[0]=98.44 vals[-1]=98.67`. `_SEMANAS_HIST`=W17-W24. CR/RND sin cambios (t4: lazy 281/867, cross-filter OK, per-canasta 100, RND nd 46). Tamaño 17,91MB. + visual Fede "Todo correcto".

### Pendiente
**#4** (cleanup A2b handlers dim muertos de AR) diferido al refactor AR cards **#1**: aunque NO hay pills dim en el DOM, el código dim está entrelazado con funciones vivas (`_arRenderTable` corre en init y elige hotel/dim por `_arView[n]`; ramas dim condicionalmente muertas; `_arDimRows`/`_arRenderChan`/`_arCrossFilter` llamados desde esas ramas + L2317/L2347/L2399; `_arDim='corp'` inicial). La data dim YA está vacía (−952KB ya capturado) → es solo limpieza de código sin beneficio de tamaño/función, con riesgo de romper las cards AR validadas. El #1 reescribe ese código → lugar natural y seguro.

---

## Sesión W24-cr-lazy-unify · 21 Jun 2026 · CR sobre el motor lazy de RND (−4MB)

### Contexto
Tras cerrar B (RND KPI sobre pool lazy), el hotel de las KPI cards CR (ef/cv) seguía volcado al DOM (P15: 3.582 filas estáticas + `CR_CARD_TABS` hotel) ≈ ~4MB. Objetivo: unificar CR sobre la MISMA función lazy de RND y recuperar el peso. Continuación de sesión (post-refactor de Excels).

### Cambios aplicados
**Motor genérico (assemble_unified.py):** `_lazyHotelRender(report, card, cf, container)` + config `_HOTEL_POOL_CFG` {cr, rnd} (índices de campo/métrica/orden/grid por reporte) + `_poolToCardRow(h, report, metric)`. Los `_rndLazyHotelRender`/`_rndPoolToCardRow` quedaron como wrappers (cableado B intacto). El motor filtra por **cross-filter** (corp/dest/país), **banda** (`cf.bands`, vista sin cf) y **hotel exacto** (`cf.hotel`, searchbox).

**Pool CR (render_cr_p1.py):** `_build_cr_hotel_pool_json()` emite `CR_HOTEL_POOL` (3.582, ~0,39MB, 11 campos) + `_CR_BAND_NAMES`. `cru_wow` corregido a `/100` (paridad con `build_card_rows`).

**Cableado CR (`_kpiPillRender`):** rama `_isCR` con guarda `_canG` (solo canasta global usa pool) → con cross-filter `_lazyHotelRender('cr',...,cf)`, sin cf `{bands: activeBands}`. Per-canasta (b2c/op/cug) cae al manejo DOM viejo (CR_CARD_TABS[canasta], ~100 c/u).

**Searchbox pool-aware (`_kpiSbBuildDD`/`_kpiSbSelect` + `_kpiSbPoolFor`):** en vista hotel + canasta global, el dropdown sugiere desde el pool (CR y RND) y al seleccionar renderiza el hotel desde el pool si no está en el DOM, luego dispara su click + lo fija. Recupera lo que P15 habilitaba (buscar cualquier hotel) sin el DOM pesado.

**Recorte (render_cr_p1.py):** estático hotel `head(1000)→head(5)` (solo estructura/fallback) + hotel **global** de `CR_CARD_TABS` `3582→banda crit` (ef 281 / cv 867 — el default que `_kpiSortAttach` renderiza en carga y cambio de canasta; `w22_renderCardTabs` no llama `_kpiPillRender`, por eso el default no puede vaciarse). Per-canasta intacto.

### Decisión clave (per-canasta)
El pool es solo GLOBAL. `w22_renderCardTabs` delega en `_kpiSortAttach`, que **saltea si la lista está vacía** y NO dispara `_kpiPillRender`. Por eso: (a) el lazy corre solo en canasta global (guarda `_canG`); (b) el hotel global de `CR_CARD_TABS` se reduce a la banda crit (no se vacía) para que `_kpiSortAttach` tenga el default en carga/cambio de canasta. Las per-canasta siguen 100% por DOM.

### Validación (jsdom + visual Fede)
Paridad exacta de bandas vs `CR_CARD_TABS` (ef crit 281 / br 823 / sc 0 — Eficacia no tiene Sin Conversión; cv crit 867 / br 1168 / sc 968). Cross-filter (Iberostar 4 · Cancun 78 · Hilton 300). Per-canasta b2c 100 filas DOM (no pool). Switch global↔b2c OK. Searchbox alcanza+renderiza hotel Exitosa fuera del crit ("Hyatt Regency Vancouver"). RND intacto (nd Iberostar 46) + RND searchbox ahora también pool-aware (21K). **HTML 22→17,9MB (−4,1MB).**

### Pendiente (no en este refactor)
Lazy-ificar AR cards CR (`CR_D` 2,0MB + `CR_HOTELS` 0,88MB ≈ ~3MB más; B tampoco lo hizo en RND) · `_SEMANAS_HIST` stale js_override.js L7 (W16-W23→W17-W24) · reconciliar `PROMPT_INV`/`calc_inv` · cleanup A2b handlers dim muertos AR · `Mail_W24`/`index.html` no se generan (fallo silencioso).


## Sesión W24-excel-bands · 21 Jun 2026 · Refactor generadores de Excel (excel_cr.py · excel_rnd.py)

### Contexto
Revisión de la generación de Excels de Análisis tras el refactor AR solo-hotel (3 bandas). Federico pidió validar cuántos elementos se generaban por dimensión y alinear las hojas a las 3 bandas del AR. Tres decisiones: (1) eliminar hojas Dim duplicadas, (2) dejar las 3 bandas del AR, (3) unificar Top-N a **500**.

### Diagnóstico (data real del pickle)
- **24 hojas Dim duplicadas**: `Dim Corp`/`Dim Dest` (CR) y `Dim Corp/Dest ND/IPM` (RND) eran copias exactas de las hojas Corp/Dest tras el refactor AR solo-hotel.
- **Bug grave en Global**: `CANASTA` no tiene entrada `'global'` → para la canasta Global las hojas de hotel caían al fallback (`TAB_ND['hotel']`/`tab_ef['hotel']`) y las 4 mostraban **data idéntica**. La separación por banda no existía en Global.
- **Categorización vieja ≠ bandas del AR**: RND usaba `top_dnc`/`top_br`/`top_sc` (demanda no convertida / IPM Crítica-Revisar / Bookings=0), capeados a 10-50 filas; CR usaba `top_crit/br/sc/mcv` a 100. No coincidían con Críticos=Crítica+SúperCrítica / BajoRend=Revisar+Aceptable / SinConv=Bookings=0.
- **Títulos mentían**: RND `write_nd`/`write_ipm` decían "Top 100" pero hacían `head(1000)`.

### Hallazgo clave (no hubo que tocar calc)
El df hotel completo **por canasta ya estaba en el pickle**: `CANASTA[c]['p80_hotel']` (RND: B2C 5979 · OP 23669 · CUG 18242) y `CANASTA[c]['p80']` (CR: 515/1011/1548), ambos con bandas (`BandaNoDispo`/`BandaRPM` · `BandaEficacia`/`BandaConvRate`) **y WoW**. Global en `D['p80_hotel']` (RND 21183) / `p80_all` (CR 2116). Todo lo necesario para band-filtrar uniforme a 500 con WoW, sin re-correr calc.

### Cambios aplicados
**excel_rnd.py:** `write_nd`/`write_ipm` → título "Top 500" + `head(500)`. Nuevos helpers `band_split_nd(df)` (3 bandas, recalcula banda vía `banda_nodispo(sf(v))` igual que el display) y `hotel_source_rnd(can, can_id)`. Reemplazadas 4 hojas hotel + Hot IPM + 4 Dim por **3 hojas de banda** (`Hot Críticos`/`Hot Bajo Rend`/`Hot Sin Conv`, banda por %NoDispo). 64→**40 hojas** (10×4).

**excel_cr.py:** `write_combined` → "Top 500" + `head(500)`. Nuevo `band_split_ef(df)` (recalcula vía `banda_eficacia(round(v,4))` igual que el display). Reemplazadas 4 hojas hotel por **3 de banda** (banda por Eficacia, extra cols Channel/Destino/Corp). Eliminadas `Dim Corp`/`Dim Dest`. 40→**28 hojas** (7×4).

### Lección
El split de banda DEBE recalcular con la misma función + redondeo que el display, no usar la columna `BandaX` pre-calculada. Síntoma del mismatch: 1 fila "Exitosa" en la hoja "Bajo Rend" (borde Aceptable/Exitosa por redondeo a 4 decimales). Tras alinear: bandas 100% limpias.

### Validación
openpyxl: 0 hojas Dim · bandas difieren en Global (RND Crít44/Bajo500/Sin500 · CR Crít110/Bajo404/Sin443) y por canasta · spot-check de columnas Severity/Bookings correcto. Federico validó visual → commit.

---


## Sesión W24-rnd-pool-B · 21 Jun 2026 · C/D resueltos — cross-filter →hotel en RND vía pool completo lazy + cap-10

### Contexto
Continuación del debug de la "Revisión #8". Tras cerrar A (searchbox AR RND) y descartar la "lista enorme" como no-bug (era el click del usuario en "Ver más"), quedaban C y D: cruzar corp/dest/país → **hotel** en las KPI cards de RND daba vacío o casi vacío.

### Diagnóstico (data real del pickle)
- El pool hotel de RND en las KPI cards estaba capeado: **nd 500 / ipm 100**, mientras el universo (`p80_hotel`) es **21.183 hoteles**. Al cruzar por corp/dest/país, los hoteles relevantes caían fuera del top → vacío. (Ej. ipm corp `NH` = 0 hoteles en el pool de 100.)
- Los cruces que NO tocan hotel (país→corp, dest→corp, etc.) YA funcionaban — usan `RND_MEMBERSHIP` con los 94 corps completos. "No aparece Ver más" en país→corp = subconjunto ≤5 (correcto, no bug).
- Cuantificación A (cap 2000/1500) vs B (pool completo): A daba 57-69% cobertura y mostraba solo ~22% de los hoteles de cada selección; B da 100% (nd) / 70-75% (ipm, máximo posible). B además más liviana que A (JSON 2,6MB vs +4,1MB DOM).

### Diferencia con CR
CR ya estaba resuelto por P15 (pool completo 3582 **en DOM** como sb-hidden). RND no puede copiar eso: 21K en DOM = +29MB. Por eso RND usa pool en **JSON compacto + render lazy**. Pendiente acordado: unificar CR sobre el mismo motor lazy después (recupera ~4MB de DOM de CR).

### Implementación B (ya existía en source de sesión previa, faltaba regenerar)
- `render_rnd_p1.py` `_build_rnd_hotel_pool_json()`: emite `var RND_HOTEL_POOL` (21.183 filas, 12 campos: `[lab,corp,dest,pais,traf_str,traf_wow, nd_pct,nd_bidx,nd_wow, ipm_val,ipm_bidx,ipm_wow]`, banda como índice → `_RND_BAND_NAMES`). Llamado en PART1. JSON 2,93MB.
- `assemble_unified.py`: `_rndPoolToCardRow(h,metric)` (pool→14 campos de `_cardRow`), `_rndLazyHotelRender(card,cf,container)` (filtra pool por cf, ordena, 5 vis + 5 cf-extra + resto sb-hidden tope 300, header preservado), `_rndHotelRestore` (repone estático cacheado en `_rndHotelOrigHTML`). Cableado en el bloque hotel de `_kpiPillRender`: `if (_isRnd && _hasCf) { _rndLazyHotelRender(...); return; }`.
- **cap-10** también en el cross-filter NON-hotel (`_crossFilterNonHotel`): `else if (_shown <= _KPI_TOP_N+5) cf-extra; else oculto`. Esto cierra la "lista enorme" de destino (antes "Ver más" expandía a 30 → ahora 10).

### Validación
- jsdom (invocación directa sobre paneles RND sin switch de modo): 0 errores parse/init · `RND_HOTEL_POOL` 21183 · ipm `NH` 0→**1 hotel** · ipm Hilton/nd España/nd Cancun → 5 vis + 5 cf-extra + sb-hidden (cap-10 OK) · nd Iberostar 46 · cap-10 non-hotel destino España = 5+5 (antes 30) · CR ef Iberostar intacto (3582, no usa lazy) · restore Hilton 300→100 OK.
- Visual Fede: OK.

### Archivos
`render_rnd_p1.py` (pool), `assemble_unified.py` (lazy render + cap-10 + fix A searchbox AR + redesign searchbox KPI de sesión previa), `reports/week-24/SUPPLY_W24.html` (regenerado 19→22MB), `PROMPT_CORE.md`, `HISTORIAL_SESIONES.md`. js_override.js sin cambios.

### Pendiente
- Variante size-neutral de B (servir vista default desde el pool → achicar dump estático) + unificar CR sobre el motor lazy.
- `_SEMANAS_HIST` stale en js_override.js L7 (W16-W23 → W17-W24).
- Reconciliar PROMPT_INV.md / calc_inv.py (proyecto vs repo).
- Cleanup A2b (handlers dim muertos AR).

---

## Sesión W24-ar-hotel-only · 20 Jun 2026 · Refactor AR SOLO HOTEL + P15 pool completo + cierre de 9/10 bugs

### Contexto
Continuación de W24-cr-kpi-ar. Federico reporta 10 bugs (CR/RND × KPI/AR) y, durante el debug, nota que las dims corp/dest/channel de las cards AR son **redundantes** con las KPI cards (mismo ranking EF/CV/NoDispo) e **inconsistentes** para IPM. Decisión de diseño aprobada: AR queda **solo hotel**. Validación con jsdom headless (HTML ~19-20MB tarda ~32s en construir → timeout ≥120s, stub canvas en `beforeParse`).

### P15 · Pool completo CR KPI (opción A) ✅
- `calc_cr.py` `tab_eficacia`/`tab_convrate`: quitado `.head(N)` → `TAB_EF/CV['hotel']` = pool completo (3582 hoteles, todas las bandas).
- `render_helpers.py` `build_card_rows`: cap 1000→4000.
- `render_cr_p1.py`: render estático capeado a top-1000 (el JS lo reemplaza con el JSON completo → no infla HTML).
- Resuelve cobertura: corp→hotel y searchbox CR KPI alcanzan cualquier corp/hotel (ej. Iberostar, banda Exitosa). Solo CR KPI ef+cv (backlog: RND nd/ipm).

### Refactor AR SOLO HOTEL (Bloque A) ✅
- **A1 (UI):** removidas las 3 filas de pills de vista (assemble: ar1, ar2, ar3-vbk) vía regex. Navegación de bandas conservada (ar1/ar2 → `ar{n}-hfilt`/`ar_setPillFilt`; ar3 → `ar3-htab-row`/`ar3_setHotelTab`).
- **A2 (data):** vaciadas las dims en `build_canasta_data` returns (`render_cr_p2.py`, `render_rnd_p2.py`): `dims/corps/dests/chans = []`. Computación interna intacta (re/plan la usan). **HTML 20.06MB → 19.10MB (−952 KB).**
- Validado jsdom: pills vista ausentes, bandas presentes, hoteles renderizan, Ver más OK, 0 errores JS.

### Bugs (9/10 cerrados)

| # | Descripción | Fix |
|---|---|---|
| #1 | Channel BK KPI no generaba pill | Handler `.bk-row` (js_override): channel → cross-pill (`_kpiCrossFilter['bk'].channel`) + limpieza en `_bkResetGlobal` |
| #2 | Pills AR no marcaban (3 cards) | Resuelto por A1 (eliminadas). También: `_handleKpiCardHistClick` retorna temprano para kpicard-ar1/ar2 en vistas dim |
| #3 | Channel BK AR no seleccionaba | Resuelto por A1 |
| #4 | ConvRate AR mezclaba convrate+eficacia | Resuelto por A1 (la mezcla estaba en las dims). Confirmado: serie base `hcr-panel-cv`=convrate `[1.15..0.82]` separada de `hcr-panel-ef`=eficacia `[93.58..95.57]`; AR card 2 grafica convrate al panel convrate |
| #5/#10 | Sin botón Ver más en AR ef/cv y RND AR | Validado jsdom (`ar{n}-th-more` display:'' cuando rows>5) |
| #6 | Orden pills BK AR | Resuelto por A1 |
| #7 | Semanas hardcodeadas (W22/W23 en vez de W23/W24) | `wowBox` (js_override) usa `_VOL_NUM` dinámico, inyectado en FOOTER_JS de assemble (`var _VOL_NUM={int(VOL_NUM)};`). HALLAZGO: `_SEMANAS_HIST` (js L7) también stale W16-W23 → debería W17-W24 (pendiente) |
| #8 | Searchbox RND KPI: query queda activo, lista enorme, sin resaltar | ✅ **DELEGACIÓN.** Diagnóstico: el searchbox KPI (`sb-kpi-*`) muestra dropdown de sugerencias pero NO filtra/resalta filas del panel (`sb-search-hit=0`); no lo ataca `_attachArSb` (solo AR) ni `_attachPanelSb` (legacy muerto). CAUSA: el searchbox KPI estaba sin cablear (oninput=null) y un intento con input.oninput se borraba porque las cards KPI re-renderizan su región. SOLUCIÓN: delegación de eventos a nivel document (input/mousedown/click/focusout) que deriva la card del id sb-kpi-XXX, filtra el panel de la vista activa (_kpiView[card]), y al seleccionar dispara el click real de la fila (reusa _handleKpiCardHistClick) + limpia query + fija fila visible. Validado jsdom: typing "can"→6 hits+dropdown; seleccionar "Cancún"→query vacío, fila visible+resaltada, 11/249 filas (no lista enorme), gráfica OK |
| #9 | Searchbox RND AR no resaltaba | Resuelto por A1 |

### Pendientes
- `_SEMANAS_HIST` stale (W16-W23 → W17-W24).
- Cleanup A2b: remover handlers dim muertos de AR.
- Bloque D: optimización tamaño HTML (estilos inline→clase, pool compartido, JSON compacto).

---


## Sesión W24-cr-kpi-ar · 20 Jun 2026 · CR/Connectivity: cross-pills, channel, corp→hotel + análisis unificación

### Contexto
Continuación de W24-rnd-kpi. Federico reporta 4 temas en las cards de Connectivity (CR) y pide un análisis de unificación CR/RND × KPI/AR para estandarizar comportamientos. Validación con jsdom headless (V8 = Chrome para lógica JS).

### Bugs y fixes cerrados

| # | Descripción | Fix |
|---|---|---|
| C1 | Cross-pills en CR salían verdes; deben ser lila (acento CR) | `_kpiCrossFilterPillsRender` (assemble): color condicional `_isCR = card in ('ef','cv','bk')` → violeta `#EDE8F7`/`#5C469C`; RND queda verde `#E1F5EE`/`#1A6B4A` |
| C2 | corp→hotel en CR no mostraba hoteles | Lógica: el branch `_hasCf` del loop hotel combinaba banda + cross-filter, y la vista hotel CR tiene filtro de banda por defecto (Críticos). Fix: ignorar banda cuando hay cross-filter (igual que RND). **PERO** queda P15 (cobertura de pool): corps de buena eficacia no están en el pool de 1000 peores → sigue dando 0. Decisión de pipeline pendiente |
| C3 | Validar base del searchbox CR | Diagnóstico: KPI CR busca sobre el pool del panel hotel (~1000 peores por Eficacia); AR busca sobre `ar{n}-th` (P80 + extendido `_sb`). Mismo root cause que C2 (P15) |
| C4 | Channel: KPI no actualizaba gráfica ni mostraba pill; AR no dejaba seleccionar | KPI: las filas `.bk-row` del channel están en `.chan-wrap` (sin id, sin `.kpi-tab-rows` ni `-chan-div`) → el listener global las ignoraba. Handler nuevo dedicado (capture + `stopPropagation`) → canvas global + pill violeta (`channel` agregado a `_kpiCrossFilter`) + highlight. AR: el handler de dim retornaba temprano en `view==='chan' && isCR`; `_handleKpiCardHistClick` (path genérico ar1→`hcr-panel-ef`) YA lo maneja — se quitó un bloque AR redundante que causaba doble-fire (upd+reset) |

### Análisis de unificación CR/RND × KPI/AR (entregado a Federico)
- **Selección de fila:** corp/dest/país y channel ahora se comportan igual (selección + gráfica + pill). Canvas: KPI→global, AR→panel.
- **Cross-pills:** decisión canónica = color por sección (CR violeta, RND verde). Opción A elegida (verde se confundía con barra "Exitosa").
- **Cross-filter:** dimensión propia no se auto-filtra; cruzadas filtran + paginan. Membership corp↔dest↔país (RND); CR solo corp↔dest.
- **P15 · cobertura de pool (la divergencia estructural):** CR KPI hotel = ~1000-2300 peores por Eficacia; RND KPI = top 500 por NoDispo; AR = P80 + extendido. Por eso corp→hotel y searchbox no alcanzan corps de buena eficacia en CR. Propuesta: incluir pool extendido `sb-hidden` en panel hotel CR (como AR), o limitar vista Corp/Destino a entidades en pool. Pendiente decisión.

### Archivos modificados
`assemble_unified.py` (cross-pill color, channel KPI handler, corp→hotel band-ignore, `channel` en `_kpiCrossFilter`), `js_override.js` (AR channel: quitado bloque redundante). Sin cambios en `render_cr_p1.py`.

### Validación jsdom
CR cross-pill violeta ✓ · KPI channel (gráfica `hcr-global-ef` + pill "DerbySoft ×" + highlight persistente) ✓ · AR channel (1er click selecciona+grafica, 2º resetea) ✓ · regresión RND 5/5 (país no auto-filtra, cross-pill verde, país→destino pagina, limpiar→reset) ✓.

---

## Sesión W24-rnd-kpi · 20 Jun 2026 · Migración KPI cards RND + 6 bugs cross-filter/searchbox

### Contexto
Continuación de W24-kpi-unify. Migración de las 2 KPI cards de RND (NoDispo + IPM) del sistema viejo de radios CSS al sistema de pills de CR, y resolución de 6 bugs reportados con screenshots (cross-filter País→Destino, searchbox AR en vistas dim, etc.). Validación con jsdom headless.

### Causa raíz transversal (índices del array RND_CARD_TABS)
El array de filas de `RND_CARD_TABS` (en `render_rnd_p1.py · _build_rnd_card_tabs_json`) estaba **desalineado** respecto al de CR (`build_card_rows` en `render_helpers.py`). `_cardRow` (js_override.js) lee `hist_w21=r[9]`, `hist_w20=r[10]`, `cf_corp=r[11]`, `cf_dest=r[12]`, `cf_pais=r[13]`. El array RND tenía `None,'—','—'` en 9-11 y el histórico en 12-13 → al re-renderizar en JS, los `data-cf-*` salían corridos (país mostraba un número). **Fix:** reordenar nd_tab e ipm_tab al layout canónico `[lab,sub,bbg,bfg,banda,traf,traf_wow,val,wow,hist21(9),hist20(10),cf_corp(11),cf_dest(12),cf_pais(13)]`. El HTML estático (Python) estaba bien; el bug aparecía solo tras el re-render JS — por eso jsdom (que ejecuta JS) lo detectó y el grep del HTML inicial no.

### Bugs y fixes cerrados

| # | Descripción | Fix |
|---|---|---|
| B1 | KPI filtro País→Destino no filtraba (seleccionar Dinamarca seguía mostrando destinos de España) | Triple causa: (a) `g_dest` no conservaba país — agregado mapa destino→país en `calc_rnd.py` (`df18_p80.groupby('Destino')['PaisDestino'].agg(mode)`); (b) `build_kpi_tab_rows` no emitía `data-cf-*` — agregados; (c) `_kpiPillRender` solo filtraba panel hotel — agregado IIFE `_crossFilterNonHotel` que filtra el panel de la vista activa (corp/destino/pais) + filtro País→Destino vía `data-cf-pais`, evaluando TODAS las filas (ignora paginación) |
| B2 | Pill País sin nombre | Resuelto colateralmente al alinear índices (la pill lee del estado, ya mostraba "Dinamarca ×") |
| B3 | KPI: click en hotel buscado no selecciona ni grafica | `_handleKpiCardHistClick` no mapeaba nd/ipm a canvas — agregado `kpicard-nd→hrnd-global-nd`, `kpicard-ipm→hrnd-global-ipm` |
| B4 | AR Hotel sin pills Críticos/Bajo Rend/Sin Conv | `ar_setPillView` siempre ocultaba `ar{n}-hfilt` — cambiado a `display = (view==='hotel') ? '' : 'none'` |
| B5 | AR card 1 (%NoDispo) y card 2 (IPM) mostraban las mismas filas en dim | `_arDimRows`: card 2 RND reordena `base` por IPM DESC parseando r[6] ("$611") |
| B6 | AR searchbox no buscaba en Corporativo (match paginado quedaba oculto) | Dos handlers `oninput` competían (assemble `_attachArSb` + js_override L1526). Ambos usaban `display` sin `!important` → no ganaban a `.sb-hidden{display:none !important}`. Unificados con clase `.sb-search-hit{display:grid !important}` (mayor especificidad) + re-obtención del tbody por ID en cada filter |

### Migración KPI cards RND (NoDispo + IPM)
- `assemble_unified.py`: `_kpiView` ahora incluye `nd`/`ipm` (default 'pais'); CSS panels controlados por JS. `_kpiPillRender` extendido a vistas no-hotel.
- `render_helpers.py`: `_kpi_pill` compartido CR+RND; `build_kpi_tab_panel(default_tab=...)`; `build_kpi_tab_rows` emite `data-cf-corp/dest/pais`.
- `render_rnd_p1.py`: ambas cards migradas de radios `tab-nd-*`/`tab-rpm-*` a pills verdes; array RND_CARD_TABS alineado a índices canónicos.
- `js_override.js`: rama RND de `_initAllSort` por ID `kpicard-nd`/`kpicard-ipm`.

### Fix crítico del canvas (causa de "pills RND no clickeables")
Un error en `w22_redrawCanvas` (vía `w22_update`←`w22_setMode`) cortaba TODA la cadena al entrar a modo RND, dejando pills KPI sin enganchar. Solución: envolver el wrapper de `w22_redrawCanvas` (js_override.js) en try/catch global. **Regla:** un canvas problemático NUNCA debe cortar `w22_setMode`.

### Aprendizajes
- **jsdom parsea mal `data-*` tras re-render JS en algunos casos** pero ejecuta la lógica fielmente — verificar atributos con grep del HTML real, confiar en jsdom para el flujo.
- **Dos handlers de searchbox** (assemble + js_override) coexistían; siempre revisar si hay un segundo `oninput` que pise antes de declarar un fix de searchbox.
- **`.sb-hidden{display:none !important}` gana sobre inline sin important** → para mostrar un match paginado hay que usar una clase de mayor especificidad, no `style.display`.


## Sesión W24-kpi-unify · 20 Jun 2026 · KPI cards — unificación total de las 3 cards

### Contexto
Sesión larga de unificación de las 3 KPI cards (Eficacia, Conv Rate, Bookability) tras el refactor que las puso sobre el mismo motor `_kpiSortAttach`. Múltiples inconsistencias de comportamiento entre cards 1/2 (EF/CV) y 3 (BK) por sistemas de render paralelos. Validación final con **navegador headless jsdom** (no solo screenshots).

### Causa raíz transversal de las inconsistencias recurrentes
Las cards 1/2 (EF/CV) y la 3 (BK) usaban motores de render distintos en varias áreas. Cada fix tocaba destino/corp/hotel (que ya comparten `_kpiSortAttach`) pero el **channel** quedaba con su sistema paralelo: EF/CV renderizaban channel en JS (`w22_renderCardTabs` + `_buildChanRow`, sin sort), BK en Python (`_hdr` con `data-sort-key`, con sort). De ahí la divergencia que reaparecía.

### Bugs y fixes cerrados

| # | Descripción | Fix |
|---|---|---|
| Path bug | `calc_supply.py` reportaba "✓ SUPPLY" pero el HTML nuevo vivía solo en el ZIP; `reports/week-NN/` quedaba con versión vieja → >1h de confusión | **Paso 10** en `calc_supply.py`: copia el HTML desde `OUTPUTS_DIR` (multi-ubicación) a `reports/week-NN/` en disco. Commit `dddda979` |
| Pills filtro | Pills Críticos/Bajo Rend./Sin Conv. en KPI cards no tienen sentido (son de AR) | Vaciados `kpi-ef-hfilt`/`kpi-cv-hfilt`; `kpi_setView` nunca los muestra (`display:none`) |
| Pills color | Pills de vista y cross-pills en violeta | Todas las pills activas → **verde** `#1A6B4A`/`#E1F5EE` (Python `_PILL_ACTIVE` + `kpi_setView` + cross-pills) |
| Cross-pills orden | Orden fijo (corp, dest) | Orden = **orden de selección** vía array `_order` en `_kpiCrossFilter[card]` |
| HTML roto hotel | Cards 1/2 vista Hotel: filas apiladas sin grid | **(a)** array `ef.hotel` tenía 1981 filas (sin límite) → límite **1000**; **(b)** `_kpiPillRender` ponía `display:''` que rompía el grid → `display:grid` explícito |
| Sort EF/CV roto | `_initAllSort`/`w22_renderCardTabs` buscaban radios `tab-ef-*` inexistentes (refactor pills) → sort no se enganchaba | Buscar la card por ID `kpicard-ef`/`kpicard-cv` (igual que BK) |
| Cross-filter hotel | Seleccionar Accor mostraba hoteles de otros corps | **(a)** `activeTab` leía radios inexistentes → leer de `_kpiView`; **(b)** filas de hotel no tenían corp/dest → agregados `data-cf-corp`/`data-cf-dest` (array +2 elementos en `build_card_rows`); **(c)** con filtro activo, ignorar paginación para mostrar matches ocultos |
| Channel catálogo | BK mostraba Omnibees/RateFox/Travelgate, EF/CV no | Catálogo canónico unificado en las 3: PP=[DerbySoft,Internal,HBSI,SynXis,Siteminder,Travelclick,Omnibees] TP=[Expedia,HotelBeds,Hotel Unico,Travelgate,**RateFox**]; faltantes → "Sin Actividad" |
| Channel inconsistente | BK channel con sort+selección, EF/CV sin | **Unificado:** `_buildChanRow` (JS) y `chan_row`/`chan_row_cv` (Python) generan filas `.bk-row` con `data-sort-key`; reusa `window.bkSort`. Listener `CHAN_SORT_EFCV_JS` (script separado en GLOBAL_PANEL_SCRIPT) engancha sort+selección en `kpicard-ef`/`kpicard-cv` |

### Decisiones canónicas nuevas
- **Pills activas siempre verdes** (`#1A6B4A`/`#E1F5EE`) — vista y cross-pills. No más violeta.
- **Orden de cross-pills = orden de click** (array `_order`).
- **Límite 1000 filas buscables** en las cards (todas de W24). El Excel NO se afecta (se genera del dataset `p80_hotel`, no del JSON).
- **AR ya tenía** sort (`_arSort`) y selección (`data-selected`); solo se alineó el pool de búsqueda `SB_N` 500→1000.
- **Catálogo de channels idéntico en las 3 cards**; lo que difiere es qué channel tuvo datos en cada dataset (CR vs BK) — esperado.

### Aprendizajes clave
- **El HTML correcto vive en `Price_W24.zip` y (desde `dddda979`) en `reports/week-24/` en disco.** `assemble` escribe en `OUTPUTS_DIR` (raíz en local), `build_package` lo mete al ZIP; el paso 10 lo copia a `reports/`.
- **Validar con jsdom, no solo screenshots.** El HTML roto del hotel (1981 filas + `display:''`) y el listener de channel que no enganchaba (abortado por error `clearRect` de canvas en jsdom cuando estaba al final de `js_override.js`) se diagnosticaron con `node + jsdom`. Solución del listener: moverlo a un `<script>` separado en `GLOBAL_PANEL_SCRIPT` para que no dependa de que `js_override.js` llegue al final.
- **Funciones globales (listeners) van en scripts separados de `GLOBAL_PANEL_SCRIPT`, no al final de `js_override.js`** — si un IIFE previo aborta (ej. canvas en headless), el resto no corre.
- **El motor `bkSort` es genérico** (ordena por `data-{key}`): cualquier card con filas `.bk-row` + headers `data-sort-key` lo reusa.

### Commits de la sesión
`dddda979` (paso 10 copia HTML) · `30706083` (quitar pills filtro) · `2796d039` (pills verdes + orden + HTML roto + cross-filter) · `1923bc6a` (catálogo channels unificado) · `45335782` (límite filas + display grid + cross-filter ignora paginación) · `0a0aedd9` (channel EF/CV unificado sort+selección + límite 1000) · `caef6d9f` (SB_N AR → 1000)

---

## Sesión W23-inv-bugs · 11 Jun 2026 · Hotel Inventory — bugs UI interactivo

### Contexto
Sesión de corrección de bugs sobre `INVENTORY_W23.html`. Sin cambio de datos ni pipeline PRICE. Todos los fixes van a `calc_inv.py`.

### Bugs cerrados (B51–B64)

| # | Descripción | Fix |
|---|---|---|
| B51 | Sort Destino/Corp con filtro activo ignoraba el filtro | `udSortCol`/`udSortTotal`: reasignar `rowIdx` + `hApplyFilter()` al final |
| B52 | Orden pills: Región→Corp→Dest→Channel | HTML + nth-child autocomplete reordenados: Región→Destino→Corporativo→Channel |
| B53 | Pill corp persiste al limpiar / card PP muestra 11.286 | `corpSel.value=''` ANTES de `hFilterCorpByChannel('')` — evita re-asignación de hFCorp |
| B54 | Gráfico DerbySoft 16K en lugar de 36K | `actual_by_channel` en hist_data + base ajustada `= chActual - totalHistAll` |
| B55 | Pico artificial al filtrar región/corp | `actual_by_region`, `actual_by_corp`, `actual_by_dest` en hist_data |
| B56 | "Ver 10 más" dentro de lista al sortear con filtro activo | `hApplyFilter`: ocultar ver-más cuando hay filtro que muestra todas las filas |
| B57 | Third Party no clickeable en Channel View | `chRenderOverview`: filas TP sin onclick/cursor — agregados |
| B58 | Hotel Unico V2 sin datos en gráfico | `_CH_NORM` en `hGetDim()`: normaliza `Hotel Unico V2` → `Hotel Unico` |
| B59 | RateFox sin datos en gráfico | Agregado a `CHANNELS_TERCERO`, `CHANNEL_LABELS`, `hist_channels_tercero` |
| B60 | Third Party sin destinos al cambiar pill de tipo | `chRenderOverview`: 3 celdas → 5 columnas completas |
| B61 | % Gap vacío en Third Party al cambiar pill | `chRenderOverview`: calcula `hoteles/N*100` igual que HTML estático |
| B62 | Avg Dest vacío en Prod. Propio al cambiar pill | `chRenderOverview`: 4 celdas → 5 columnas con barra visual |
| B63 | Tabla Channel no sincroniza con pill PP/SP/HY | `CH_DATA["pp"]` creado desde `df_pp`; `_chTipoMap`: `pp:"todos"` → `pp:"pp"` |
| B64 | Card PP mostraba 11.286 tras limpiar filtros | `hClearFilters`/`hClearFilter`: agregar `updateCards({type:"all"})` |

### Archivos modificados
`calc_inv.py`

### Reglas nuevas
- `hClearFilters`: limpiar `corpSel.value` ANTES de `hFilterCorpByChannel('')`
- `chRenderOverview`: JS debe generar las mismas columnas que el HTML estático Python
- `_CH_NORM` en `hGetDim()`: mapa canónico para resolver mismatch nombre tabla↔dim_ch
- Al sortear: reasignar `rowIdx` y llamar `hApplyFilter()`, nunca setear `display` directamente

---

## Sesión W23-fixes-finales · 11-06-2026 · Pipeline local + fixes menores

### Pipeline local W23
Corrido desde la máquina de Federico con los datasets originales. Fixes aplicados:
- `calc_supply.py`: acepta `Dataset_bookability.xlsx` (minúscula) sin renombrar
- `calc_bk.py`: `_find()` busca variantes de nombre con glob
- `demo_css_w22.css`: `.c-chip` padding `22px` → `16px` (alinear con producción)
- `js_override.js`: header Channel `Trx` → `Tráfico` en cards AR de CR/RND

### Commits
- `f9a67fdc` calc_supply.py — validación acepta Dataset_bookability.xlsx
- `20837ef8` calc_bk.py — _find busca variantes de nombre
- `f0caffe1` demo_css_w22.css — .c-chip padding 16px
- `160ecb21` js_override.js — header Tráfico en Channel view

### Estado
SUPPLY_W23.html generado localmente y commiteado. Pipeline W24 listo.

---

## Sesión W23-cierre · 11-06-2026 · Auditoría pipeline + parche HTML W23

### Contexto
Sesión de cierre W23. Se auditó el flujo completo del pipeline, se corrigió un bug
de sintaxis en `assemble_unified.py`, y se parcheó `SUPPLY_W23.html` en producción
reemplazando únicamente el bloque `js_override.js` embebido — sin tocar los datos.

### Bug encontrado en auditoría
`assemble_unified.py` línea 233: CSS de card BK (`body[data-ar-mode='rnd']`) tenía
newlines reales y comillas simples crudas dentro de un string Python → `SyntaxError`
en tiempo de ejecución. Corregido escapando con `\'rnd\'`.

### Parche SUPPLY_W23.html
Estrategia: descargar el HTML correcto de producción, localizar el inicio del
`js_override.js` embebido (`var _KPI_TOP_N`), reemplazar solo ese bloque con el
nuevo `js_override.js` (138,371 chars). Datos, estructura HTML y demás scripts
intactos. Commit via Git Tree API → `685b3bf4`.

Resultado: 2 defs de `w22_setMode` en el HTML (1 del `GLOBAL_PANEL_SCRIPT` +
1 del nuevo `js_override`) — la segunda (la activa) tiene todos los side-effects
consolidados. Comportamiento correcto.

### Fixes activos en SUPPLY_W23.html
- P12: filtro cruzado Corp+Dest con pills eliminables en AR cards
- P13: ConvRate WoW en Críticos/BR (r[11]/r[12] en build_hotel_row — activo en W24+)
- Refactor `ar_updateKPIs` → `_AR_MODE_CFG` + `_arReadKpiData` + `_arApplyCard`
- `w22_setMode` consolidada (1 def activa con todos los side-effects)
- Searchbox 500 hoteles (pool `_sb` — activo en W24+, requiere re-pipeline para W23)
- `_arCrossFilter` y `_arCrossFilterPillsRender` disponibles

### Archivos modificados esta sesión
`js_override.js` · `assemble_unified.py` · `render_cr_p2.py` · `render_rnd_p2.py` ·
`calc_cr.py` · `build_package.py` · `extract_hist_data.py` (nuevo) ·
`SUPPLY_W23.html` (parche JS) · `PROMPT_CORE.md` · `HISTORIAL_SESIONES.md`

### Para W24
Pipeline estándar:
```powershell
python calc_supply.py
python extract_hist_data.py --week 24 --apply
python run_inv.py --commit
```
El hub (`index.html`) se regenera con `build_package.py` al final del pipeline.


---

## Sesión W23-P5 · 11-06-2026 · extract_hist_data.py

### Qué hace
Script utilitario que lee los pickles CR, RND y BK de la semana recién procesada
y actualiza `historico_data.py` automáticamente — reemplaza la actualización manual
de los arrays semana a semana.

### Uso
```bash
# Dry-run — muestra valores sin escribir
python extract_hist_data.py --week 24 --dir /ruta/a/pickles

# Apply — actualiza historico_data.py
python extract_hist_data.py --week 24 --dir /ruta/a/pickles --apply

# Con VOL_NUM del entorno (si ya corriste el pipeline)
python extract_hist_data.py --apply
```

### Lógica
- Lee `M['global_wNN']['eficacia']`, `M['global_wNN']['conv_rate']` del pickle CR
- Lee `M['global_wNN']['pct_nodispo']`, `M['global_wNN']['ipm']` del pickle RND
- Lee `bk_global` del pickle BK
- Repite para canastas: `B2C`, `B2B-OP`, `CUG` (16 valores en total por semana)
- Ventana móvil de 8 semanas: descarta la primera al llegar al límite
- Dry-run por default — `--apply` para escribir

### Archivos modificados
`extract_hist_data.py` (nuevo) · `PROMPT_CORE.md`

### Bugs cerrados
P5: extract_hist_data.py creado

### Estado del backlog
**0 bugs abiertos** — P1–P14 todos cerrados.


---

## Sesión W23-P12 · 11-06-2026 · Filtro cruzado Corp+Dest en cards AR

### Spec implementada
Click en fila Corp → activa filtro Corp (la vista permanece en Corp para elegir
el siguiente filtro). Click en fila Dest → añade filtro Dest en AND. Los filtros
activos aparecen como pills eliminables [Corp: AmEx ×] [Dest: Cancún ×] sobre
la tabla. Cambiar de pestaña Críticos/BR/SC mantiene los filtros activos.
Cambiar canasta o modo CR↔RND limpia los filtros.

### Arquitectura implementada

**Python (`render_cr_p2.py`, `render_rnd_p2.py`)**
- `build_hotel_row` y `build_hotel_row_rnd` extendidas con `r[11]=CorpName`, `r[12]=Destino`
- Estos campos son leídos del pickle (p80_hotel tiene ambas columnas)

**JS (`js_override.js`)**
- `_arCrossFilter = {1:{corp,dest}, 2:{corp,dest}}` — estado independiente por card
- `_arFilterApply(rows, n)` — filtra rows en AND antes de renderizar
- `_arCrossFilterPillsRender(n)` — dibuja los pills eliminables activos
- `_arCrossFilterClear(n, type)` — quita un filtro o todos
- Event listener único: detecta click en `.ar-cross-pill` (×) y en `[data-hist-label]` 
  cuando la vista activa es 'corp' o 'dest'
- `_arRows` (card 1 y 2) pasan por `_arFilterApply` al final
- Reset en `w22_setMode` (cambio CR↔RND) y en `w22_setC` (cambio canasta)

**HTML (`assemble_unified.py`)**
- Contenedores `ar1-cross-pills` y `ar2-cross-pills` insertados después de los pills 
  de filtro (Críticos/BR/SC), con `display:none` inicial

### Archivos modificados
`js_override.js` · `render_cr_p2.py` · `render_rnd_p2.py` · `assemble_unified.py`

### Bugs cerrados
P12: Filtro cruzado Corp+Dest en AND en cards AR

### Bugs abiertos
P5: `extract_hist_data.py` pendiente de crear


---

## Sesión W23-P13 · 11-06-2026 · Fix ConvRate WoW en Críticos/Bajo Rend.

### Causa raíz
`calc_cr.py` mergeaba `p80_hotel` con `g_hotel_w17` incluyendo `Eficacia_W17` y
`CR_Unicos_W17` pero **omitiendo `ConvRate_W17`**. Sin ese campo, `ConvRate_WoW_pp`
nunca se calculaba para `p80_hotel` → `df_hotel` → `df_crit/df_br/df_sc` →
`hotels_crit_rows/br/sc` → siempre `r[9] = '—'` en el HTML.

`g_hotel_w17` sí tenía `ConvRate_W17` (lo usa en otros merges dentro de las
canastas). Solo faltaba incluirlo en el merge de `p80_hotel` que alimenta
`render_cr_p2.py`.

### Fix
`calc_cr.py`: un solo cambio — añadir `'ConvRate_W17'` a la lista del merge y
calcular `p80_hotel['ConvRate_WoW_pp']`.

### Archivos modificados
`calc_cr.py`

### Bugs cerrados
P13: ConvRate WoW siempre `—` en Críticos/Bajo Rend./Sin Conv.


---

## Sesión W23-refactor-1 · 11-06-2026 · Refactor transparencia de cards

### Contexto
Refactor estructural para que los cambios en cards 1, 2 y 3 sean transparentes.
Se abordan las dos prioridades de mayor impacto/esfuerzo.

### Cambios aplicados

**Refactor 1: ar_updateKPIs → config + reader + apply**

Antes (10,728 chars): un bloque `if (isCR) {...} else {...}` de 150 líneas donde
CR y RND eran paralelos. Un bug en `cdata.banda_ef` había que corregirlo en dos sitios.

Después (3 objetos + 2 funciones + 1 orquestador):
- `_AR_MODE_CFG` — objeto de config por modo: qué canvas leer, targets, dirección WoW
- `_AR_BANDA_C` — paleta de bandas compartida (antes duplicada en 2 bloques)
- `_arReadKpiData(cdata, cfg)` — lee y normaliza datos UNA VEZ para cualquier modo
- `_arApplyCard(n, ...)` — aplica al DOM de la card n (parametrizado)
- `ar_updateKPIs()` — orquestador: config + read + apply(1) + apply(2)

Beneficio: un bug como `cdata.banda_ef` se corrige UNA VEZ en `_arReadKpiData`
y aplica automáticamente a CR y RND.

**Refactor 2: w22_setMode → una sola definición**

Antes: 4 redefiniciones encadenadas (`js_override.js` × 1 + monkey-patches × 3).
La DEF 1 nunca ejecutaba directamente. Cada monkey-patch añadía side-effects
invisibles desde los otros. Este fue el bug raíz de P14 (card BK en Availability).

Después: 1 sola función con todas las responsabilidades explícitas y ordenadas:
1. Estado (W.mode, W.canasta)
2. UI del segmented control
3. CSS accent global
4. Visibilidad de bloques KPI y Severity
5. Labels y headers según modo
6. Reset chips
7. Render (w22_update)
8. Side-effects nombrados: reset _SS, reset panel selection, init search (150ms), init sort (400ms)
9. Sync card3 (250ms)

`_patchMode` eliminado de `assemble_unified.py` — ya no es necesario.

### Archivos modificados
`js_override.js` · `assemble_unified.py`

### Beneficio inmediato
- Añadir un side-effect al cambio de modo → 1 línea en la sección correcta de `w22_setMode`
- Cambiar el comportamiento de KPIs para CR y RND → 1 línea en `_AR_MODE_CFG`
- Bug en lectura de datos KPI → 1 fix en `_arReadKpiData`, aplica a ambos modos


---

## Sesión W23-bk-s3 · 11-06-2026 · Fixes de Availability y UI

### Contexto
Tercera sesión de correcciones sobre W23. Enfoque en el bug persistente de
card BK en Availability y pulido de UI del switcher.

### Cambios aplicados

**Bug: Card BK persiste en Availability (P14) — causa raíz encontrada**
- Había 4 redefiniciones encadenadas de `w22_setMode` en el HTML
- La primera definición (con `_syncCard3`) nunca se ejecutaba — la 2a def la sobreescribía completamente
- La 2a def (en `js_override.js`) llamaba `w22_update()` y terminaba sin `_syncCard3`
- Fix: `_syncCard3` añadida al cierre de la 2a def con `setTimeout(250ms)`
  para que corra después del `setTimeout(200ms)` interno de `w22_update()`
- `assemble_unified.py`: mismo patrón en el closure de `_patchMode`

**Bug: Switcher AR en color (violet/magenta) en lugar de negro**
- `_syncCard3` seteaba `arBtnCr.style.background = modeCol` como inline style
- El inline style pisaba el CSS `.w22-seg-btn.on { background: var(--ink) }`
- Fix: `_syncCard3` ahora solo toggle la clase `.on` y deja `style.background = ''`
- El CSS maneja el color negro automáticamente

### Archivos modificados
`js_override.js` · `assemble_unified.py` · `SUPPLY_W23.html`

### Bugs cerrados
P14: Card BK persiste en Availability ← causa raíz en cadena de redefiniciones de w22_setMode
Switcher AR en negro ← inline style eliminado, CSS maneja el color

### Bugs abiertos
P13: ConvRate_WoW en hotels_crit/br/sc (r[9]='—') — fix en render_cr_p2.py
P12: Filtro cruzado pills Corp+Dest+Channel


---

---

## Sesión W23-bk-s2 · 10-06-2026 · Cards AR Bookability — fixes masivos

### Contexto
Segunda sesión de bugs post-W23 enfocada en la card 3 (Bookability) y en bugs
transversales a las 3 cards de Análisis de Rendimiento.

### Cambios aplicados

**BK_DATA completo (assemble_unified.py)**
- `_bk_rows` ahora usa `n=100` para dest/corp/hotel y `g_provider` completo para prov
- `BK_DATA.prov` pasa de 5 a 11 canales (Internal, DerbySoft, etc. con datos reales)
- `BK_DATA.hotel` pasa de 5 a 100 items → Ver más funciona en Hotel/Críticos

**_BK_TRX_WOW (assemble_unified.py + js_override.js)**
- Nuevo lookup generado desde `g_dest/g_corp/g_hotel` del pickle BK
- Normaliza key `dest` → `destino` para acceso correcto en JS
- WoW TRX ahora visible en Destino, Corp, Hotel

**_normBanda case-insensitive (js_override.js)**
- `_normBanda()` normaliza acentos y mayúsculas antes de comparar con bandMap
- Crítica → critica ✓, Revisar → revisar ✓
- Sin esta fix, filteredWithPos siempre vacío → fallback mostraba todos

**origPos local post-filtro (js_override.js)**
- `origPos = i+1` ahora se asigna dentro del subset filtrado, no sobre el dataset completo
- Bajo Rend. en card 3 numera 01,02,03... en lugar de 16,17,18...

**Sin Conv sin fallback (js_override.js)**
- BK_DATA no tiene hoteles con banda sinconv (todos tienen ≥5 books)
- El fallback se elimina para `_ar3_htab === 'sc'`
- Tab Sin Conv oculto en card 3 (`display:none`)

**Sort 3 estados en las 3 cards (js_override.js)**
- `_nd()` aplicado a `_arSort` y `_ar3Sort`: orig→asc→desc→orig
- Reset automático al cambiar pill/view: `_arPillRender`, `ar3_setView`, `ar3_setHotelTab`
- Indicadores `↑↓↕` leen `dir` en lugar de `asc:bool`

**origPos en ar_renderTable (js_override.js)**
- `ar_renderTable` acepta arrays planos y `{r, origPos}`
- `_arSort` pasa `{r, origPos}` para preservar ranking original
- `trow_ar(r, n, origPos)` recibe la posición correcta

**badge sin target (js_override.js)**
- `b1.textContent = efBanda` (sin `efTarget`)
- `cdata.band` y `cdata.band_cv` en lugar de `cdata.banda_ef`/`cdata.banda_cv` (inexistentes)

**Sin Conv card2 ordena por Tráfico DESC (js_override.js)**
- Para `hotels_sc` en card 2, sort por `r[4]` tráfico DESC
- Cards 1 y 2 muestran hoteles distintos en Sin Conv

**_syncCard3 + CSS data-ar-mode (assemble_unified.py)**
- `window._syncCard3` expuesto globalmente
- `w22_setMode` llama `_syncCard3` directamente + `data-ar-mode` en body
- CSS `body[data-ar-mode='rnd'] #kpicard-ar3 { display:none !important }` como fallback
- Card BK oculta en Availability (pendiente confirmar W24)

**UX card 3**
- Pills orden: Hotel → Corp → Destino → Channel
- Tab por defecto kpicard-bk: Channel (no Destino)
- Badges de severity: solo nombre, sin target
- ar3-th-more unificado con ar1/ar2 (mismo mecanismo `_moreBtn`)

**Bug pendiente de pipeline (P_NEW)**
- `r[9]` (ConvRate_WoW) siempre `'—'` en hotels_crit/br/sc → fix requiere `render_cr_p2.py`

### Archivos modificados
`assemble_unified.py` · `js_override.js` · `render_cr_p1.py`

### Bugs cerrados
BK_DATA completo · _normBanda · origPos local · Sin Conv · Sort 3 estados ·
badge sin target · Sin Conv card2 tráfico · ar3-th-more · pills orden card3

### Bug abierto
P_NEW: ConvRate_WoW en hotels_crit/br/sc arrays (pipeline Python)
P_BK_AVAIL: Card BK persiste en Availability (CSS fix pendiente confirmar)


---

## 📝 Sesión W24-pre · 09 Jun 2026 · Mail — sección Inventory

### Contexto
Sesión corta de mejora puntual al template del mail semanal (`render_mail_v3.py`). Sin cambios al pipeline de CR/RND ni a Inventory.

### Cambios aplicados

**`render_mail_v3.py`** — único archivo modificado:
- Añadida sección **State of PriceTravel Product · Inventory** con la misma jerarquía visual que Availability y Connectivities: `section-title` con dot cyan `#4FC3F4` + grid 2 cards.
  - Card 1: Producto Propio (`inv-color` cyan) + gauge de avance % + WoW pill opcional
  - Card 2: Gap al Target (`inv-red` `#FF3B30`) + ritmo necesario + semanas restantes
- CSS añadido: `.dot-inv`, `.kpi-card.inv::before`, `.kpi-value.inv-color`, `.kpi-value.inv-red`
- Subject actualizado: `…& Inventory` cuando `HAS_INV`
- Preheader incluye `PP X.XXX hoteles` cuando `HAS_INV`
- Lede condicional incluye `+ State of PriceTravel Product`
- CTA secundario `→ State of PriceTravel Product WNN` (oscuro, `display:block`) cuando `HAS_INV`
- **Estrategia de datos: Camino B** — CONFIG manual en el script (igual que `PERIODO`/`VOL_NUM`). Sin tocar `calc_inv.py`.
  - Si `INV_PP = 0` (default), `HAS_INV = False` → mail se genera igual que antes. Retrocompatible.
  - Los valores se copian del output de consola de `calc_inv.py` cada semana.

### Archivos modificados
| Archivo | Tipo de cambio |
|---------|---------------|
| `render_mail_v3.py` | Añadida sección Inventory + CONFIG manual + CSS |

### Archivos NO modificados
- `calc_inv.py` — sin cambios (Camino B no lo requiere)
- `assemble_unified.py`, `build_package.py`, etc. — sin cambios

### Decisiones de diseño
- Se evaluaron 3 opciones visuales (A: 2 cards mismo grid; B: 4 cards compactas; C: progress bar). Se eligió **Opción A** — máxima consistencia con RND/CR.
- Se evaluaron 3 estrategias de datos. Se eligió **Camino B** (config manual) por simplicidad — un solo archivo.

---

## 📝 Sesión W23 · 08 Jun 2026 · Hotel Inventory — drill semanal + optimización de tamaño

### Contexto
Fusión de los fixes de W22 con la optimización de tamaño de W23 sobre `calc_inv.py`. El problema raíz: al subir los cambios de peso (W23) se pisaron features de W22. Sesión larga de debugging con múltiples iteraciones. Descubrimiento clave: el "drill por semana que actualiza la tabla de distribución" que se creía perdido **nunca existió** en el `calc_inv.py` de W22fix ni en el HTML de producción W22 — la rama semanal siempre dejaba `onClickFn=null`. El drill real estaba solo en `INVENTORY_W22_FINAL_1.html` (versión que no se había portado al script).

### Cambios aplicados a `calc_inv.py`

**Optimización de tamaño (43MB → 12.4MB):**
- `HIST.snapshot` (región×corp×dest×tipo×channel×semana, ~80K rows) **eliminado** — era la causa de los 40MB
- Reemplazado por 3 índices compactos con keys cortas:
  - `dim_ch` (`w,m,t,ch,n`) — filtrado a últimos 2 años (`df_hist_dim = df_hist[df_hist['year'] >= YEAR_ACTUAL-1]`)
  - `dim_tipo` (`w,m,t,n`) — para filtro solo-tipo
  - `dim_hotel` (`w,m,r,c,d,t,n`) — incluye destino, para filtros región/corp/dest + drill
- `dim_hotel` NO se filtra por año (necesita histórico completo para el acumulado, si no la línea queda plana)

**Drill por semana → tabla de distribución (recuperado de W22_FINAL y portado a keys compactas):**
- `hDrillWeek(yw)`, `_snapTbody()`, `_renderDrillTable(rows,label,dim)`, `_renderDrillPill(label)`, `hDrillWeekReset()`
- Click en barra de semana → reescribe `ud-tbody` con hoteles nuevos de esa semana, agrupados por `udDim` (reg/corp/dest), columnas Total/PP/SP/HY/TP
- Pill "Nuevos WNN ×" en `hf-active-pills`; click en × o re-click en la barra → reset
- keyMap compacto: `{reg:'r', corp:'c', dest:'d'}`

**Bugs cerrados (B37–B45):**
- B37: línea plana — `sparseMap[r.yw]` daba undefined (dim compacto usa `w`) → `r.w||r.yw`
- B38: acum arrancaba en 0 con PROD. PROPIO → `HIST.actual_by_tipo` como base
- B39: `evt.stopPropagation is not a function` → `evt.native.stopPropagation()`
- B40: `activeRegions`/`activeTipo` not defined en `hRender` → redefinir local `_activeR/_activeC/_activeCh/_activeTipo`
- B41: drill semanal a tabla (desarrollo nuevo, no recuperación)
- B42: `dim_hotel` sin destino → agregado `d`
- B43: tabla GAP destacaba Con Directo → swap a Sin Directo (cyan)
- B44: pill PROD. PROPIO verde (`#E1F5EE`/`#1A6B4A`) + activación `_tryInit`
- B45: tamaño 43→12.4MB
- B46: pills activas en una fila, verde uniforme; botón menú mantiene color categoría
- B47: drill-pill verde (era violeta)
- B48: drill funciona en SIN CONTRAT (`_gapMode`/`_drillTbody` → `gap-tbody`)
- B49: VS GLOBAL eliminada en TODAS las celdas — header/celda GAP, fila GLOBAL principal, celdas drill (normal+GAP). Regla: toda celda última columna lleva `td-vs`
- B50/P6: Channel View — columna % Gap junto a Hoteles (barra cyan), ambas columnas % Gap mismo formato

**Limpieza W24:**
- `_ppRatio` hardcodeado (`53097/309591`) → dinámico `{pp}/{N}`
- Verificado: ningún `W23` hardcodeado fuera del bloque CONFIG. Para W24 solo cambiar CONFIG (L20-29)

### Aprendizajes
- **Fixes sobre HTML se pierden al regenerar**: durante la sesión se aplicaron varios fixes directo sobre el HTML que luego no estaban en el script. Regla: todo fix va al `calc_inv.py`, nunca solo al HTML.
- **El script no regenera si el HTML existe**: hay que `Remove-Item week-NN\INVENTORY_WNN.html` antes de correr.
- **Verificar versión antes de correr**: `Get-Content calc_inv.py | Select-String "_ppRatio"` — confirma que el archivo reemplazado es el correcto (descargas con mismo nombre pueden quedar cacheadas).
- **`calc_inv.py` no commitea** — genera HTML local; commit manual via GitHub Desktop (>1MB).

### Archivos modificados
- `calc_inv.py` (drill + optimización + 9 bugs + _ppRatio dinámico)
- `PROMPT_INV.md` → v15.0
- `PROMPT_CORE.md` (tamaño INVENTORY, duplicado eliminado)

### Pendientes
- Validar drill en ambos modos (normal + SIN CONTRAT) tras última corrida
- Commit `INVENTORY_W23.html` + `calc_inv.py` via GitHub Desktop
- Actualizar `README_QUICK.md` con métricas W23 publicadas

### Resueltos en la sesión (detalles visuales finales)
- Pill PROD. PROPIO: chip verde al cargar (botón menú queda violeta)
- Pills activas unificadas en una fila, color verde
- Columna VS GLOBAL eliminada en ambas tablas (principal + GAP)
- Drill por semana operativo también en modo SIN CONTRAT

### Cierre y limpieza de repo (W23)
- **Bug de GitHub Desktop con archivos grandes:** el push del `INVENTORY_W23.html` (12MB) falló silenciosamente — el commit aparecía pero el repo seguía sirviendo la versión vieja de 44MB en Netlify (loading page lenta). Resuelto subiendo el HTML por Git Tree API directo (blob → tree → commit → patch ref).
- **Última celda VS GLOBAL:** la fila GLOBAL de la tabla principal (`pct_bar_html(pp/N*100,"#4FC3F4")`) tenía `<td>—</td>` sin clase `td-vs`. Corregida. Regla reforzada: TODA celda de la última columna lleva `td-vs`.
- **Limpieza de repo:** borrados 11 archivos versionados por error (ya en `.gitignore`): `Price_W23_extracted/`, `__pycache__/`, `cr_w21_data.pkl`, `rnd_w21_data.pkl`, `Dataset_CheckRates_W19.xlsx`. Repo de 157 → 144 archivos.
- **`run_inv.py` (nuevo):** wrapper transparente del pipeline Inventory. 6 pasos verificados (valida CWD/dataset/token → verifica versión calc_inv.py → borra HTML viejo → corre → verifica tamaño → commit Git Tree API). Resuelve todos los puntos de fricción de W23. Subido a `inventory/run_inv.py`. Uso: `python run_inv.py [--commit]`.

### Aprendizajes W23 (workflow)
- GitHub Desktop NO es confiable para archivos >~10MB → usar siempre Git Tree API (vía `run_inv.py --commit` o manual).
- El `calc_inv.py` no regenera el HTML si ya existe → borrar antes de correr (run_inv.py lo hace solo).
- Correr siempre desde `inventory/` (run_inv.py valida el CWD).
- Verificar versión del script antes de correr (run_inv.py chequea 4 fixes canónicos).

---

## 📝 Sesión W22-pre · Junio 2026 · Hub v2 visual — ajustes finales

### Contexto
Sesión de ajustes visuales sobre el Hub (`build_package.py`). No se corrió pipeline PRICE. Objetivo: pulir el Hub antes de W22 con logo real, contraste de cards corregido, blur en inactivas, y eliminación de la sección "Últimas semanas".

### Cambios aplicados

#### `build_package.py` — Hub v2 visual

**Logo:**
- Eliminada la dependencia de `logo_b64.txt` externo (archivo que no existe en el proyecto Claude)
- `_LOGO_B64` ahora hardcodeado directamente en el script, extraído de `calc_inv.py` (mismo PNG)
- Login (`lock-logo-wrap`): sin cambios — ya usaba `{_LOGO_B64}` correctamente
- Hub header: reemplazado SVG geométrico + span "PriceTravel" por `<img>` con el logo real: `height:40px`, `filter:saturate(0) brightness(0)` — idéntico al login
- Bug corregido: `{{_LOGO_B64}}` (doble llave, literal) → `{_LOGO_B64}` (expansión correcta en f-string)

**Header del Hub:**
- Agregado `border-bottom:1px solid var(--rule)` + `padding-bottom:16px` — ancla el header visualmente
- Antes: flotaba suelto con solo el `border-top` grueso

**Contraste de cards:**
- Cards activas: `background:#EDE8DF` → `background:var(--paper)` (`#F8F4EC`) — se funden con el fondo del Hub
- Cards inactivas: `background:#EDE8DF` + `filter:grayscale(0.35)` → `background:#F0EBE2` + `backdrop-filter:blur(1.5px)` + velo `rgba(240,235,226,0.35)` — chip "En construcción" flota nítido z-index:3 encima del blur
- Eliminada la trama diagonal (`repeating-linear-gradient`) — reemplazada por el blur

**Sección "Últimas semanas" eliminada:**
- Bloque HTML `.archivo` completo eliminado del Hub — el historial de semanas anteriores ya existe en las pills de cada card activa
- CSS `.archivo`, `.archivo-title`, `.archivo-grid`, etc. eliminados
- JS de `recent-link` y toggle acordeón eliminado

### Archivos modificados
`build_package.py` · `PROMPT_CORE.md` · `HISTORIAL_SESIONES.md`

---

## 📝 Sesión W22-pre · Mayo 2026 · Refactor P9 + Fix Sort KPI

### Contexto
Sesión de pre-pipeline antes de recibir los datasets W22. No se corrió pipeline. Dos tareas ejecutadas: (1) refactor de centralización CR/RND documentado en `NOTA_REFACTOR_PENDIENTE.md`, (2) fix del sort en las cards KPI principales.

---

## 📝 Sesión W22-pre (cont.) · Mayo 2026 · Refactor P10 + Pipeline W21

### Contexto
Continuación de la sesión W22-pre. Se completó el refactor P10 (Bloque A + Bloque B) y se corrió el pipeline W21 completo con los archivos refactorizados.

### Cambios aplicados

#### Bloque A — Helpers de formato centralizados (sin impacto visual)

Funciones idénticas en `render_cr_p2.py` y `render_rnd_p2.py` movidas a `render_helpers.py`:

| Función | Descripción |
|---|---|
| `es_pct(v)` | Fracción → `'93,15%'` |
| `es_int(v)` | Entero con punto de miles `'746.111'` |
| `es_pct2(v)` | Ya viene en % `'1,57%'` |
| `es_ipm(v)` | IPM formateado `'$834'` |
| `banda_colors(banda)` | Lookup `(bg, fg)` desde `BANDA_COLORS` |
| `wow_arrow(pp)` | `▲1,2` / `▼0,5` / `—` para WoW en pp |
| `wow_arrow_abs(delta)` | `▲746.111` para WoW de tráfico |
| `sev_badge_html_p2(banda)` | Badge `<b>` para tablas AR |

`render_cr_p2.py`: 704 → 678 líneas (−26). `render_rnd_p2.py`: 553 → 538 líneas (−15).

#### Bloque B — Unificación JS + _mini_badge (con validación visual)

**`_mini_badge`** — ya existía en `render_helpers.py` (línea 42). Eliminada la definición local duplicada de `render_cr_p3.py` y `render_rnd_p3.py`.

**`_chanRow` + `chanRowAR` → `_buildChanRow`** en `js_override.js`:
- Unificadas en `_buildChanRow(r, i, opts)` donde `opts = {cardN, w20}`
- KPI card: `_buildChanRow(r, i, {})` · AR card: `_buildChanRow(r, i, {cardN:n, w20:true})`
- `js_override.js`: 1789 → 1779 líneas

#### Pipeline W21
Output idéntico en los 6 parciales. Validación visual confirmada: sort RND funciona + channels PP/TP correctos.

### Archivos modificados
`render_helpers.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_cr_p3.py` · `render_rnd_p3.py` · `js_override.js` · `PROMPT_CORE.md` · `HISTORIAL_SESIONES.md`

`render_cr_p1.py` (parte 2 del refactor)

#### Parte 2 — canasta_tab_rows + build_card_rows

**`canasta_tab_rows(df, dim_col, cfg)`** en `render_helpers.py`:
- Reemplaza `tab_rows_canasta()` duplicada en `render_cr_p3.py` y `render_rnd_p3.py`
- La diferencia CR/RND (columnas, WoW logic, bandas) se expresa como cfg dict
- `render_cr_p3.py`: 1122 → 1064 líneas (−58). `render_rnd_p3.py`: 984 → 945 líneas (−39)

**`build_card_rows(df, t_key, cfg)`** en `render_helpers.py`:
- Reemplaza `_build_card_rows_ef` y `_build_card_rows_cv` en `render_cr_p1.py`
- `render_cr_p1.py`: 653 → 607 líneas (−46)

**P11 detectado (no regresión):** `ConvRate_WoW_pp` solo existe en `TAB_CV` (100 hoteles con Bookings > 0), no en `p80_hotel` (1342). Los hoteles Sin Conversión muestran `—` en WoW ConvRate en cards AR. Preexistía antes del refactor.



---



### Cambios aplicados

#### Refactor P9 — Centralización CR/RND en `render_helpers.py`

**Problema raíz:** el bloque `for i, r in df_t.iterrows()` con toda la lógica de rows KPI se repetía 4 veces (Eficacia, ConvRate en CR · NoDispo, IPM en RND). Cualquier cambio visual requería tocar 4 archivos.

**Solución:** extraer a `render_helpers.py`:

| Función/Constante | Descripción |
|---|---|
| `KPI_TOP_N = 10` | Único punto de control del top N visible |
| `render_traf_wow_pill_pct(delta)` | Pill WoW de tráfico como % |
| `render_traf_wow_pill_abs(delta)` | Pill WoW de tráfico como delta absoluto |
| `render_traf_line_cr(curr, prev)` | Línea "Tráfico: 746.111 ↑pill" CR |
| `render_traf_line_rnd(curr, prev)` | Línea "Tráfico: 12,2B ↑pill" RND |
| `_resolve_label(r, t_key)` | Extrae `(raw_lab, lab, corp_sub)` según t_key |
| `build_kpi_tab_rows(df_t, t_key, cfg)` | Genera HTML de filas — corazón del refactor |
| `build_kpi_tab_panel(df_t, t_key, cfg, spec)` | Construye `<div class="tab-panel">` completo |

**Reducción de código:**
- `render_cr_p1.py`: 791 → 653 líneas (−138)
- `render_rnd_p1.py`: 538 → 458 líneas (−80)
- `render_helpers.py`: 481 → 775 líneas (+294 de funciones nuevas)

**Nota de diseño:** tabs `channel` y `canasta` conservan lógica ad-hoc (channel tiene split PP/TP con grid diferente; canasta no tiene WoW por fila). `build_kpi_tab_panel` devuelve `''` para `t_key='channel'`, delegando al caller.

#### Fix Sort KPI — 3 bugs corregidos en `js_override.js`

**Bug 1 — Sort RND nunca se enganchaba (crítico):**
`_initAllSort` solo iteraba `['ef','cv']` buscando IDs `tab-ef-*` y `tab-cv-*`. Las cards KPI de RND usan `tab-nd-*` y `tab-rpm-*`. `RND_CARD_TABS` no existe como variable JS. Resultado: el sort nunca se enganchaba en las cards NoDispo e IPM.
Fix: `_initAllSort` ahora bifurca por `W.mode`. Para RND itera `['nd','rpm']` y busca los IDs correctos. Si `RND_CARD_TABS` no existe, el sort opera sobre el DOM estático de Python (sin re-render JS).

**Bug 2 — Grid incorrecto en ConvRate post-sort:**
`_cardRow` hardcodeaba `minmax(0,1fr) 80px 56px 52px 54px 48px` (grid de Eficacia) para todas las cards. ConvRate usa `68px 40px` en la última columna.
Fix: `_cardRow` acepta parámetro `grid` opcional. Se agrega `_KPI_GRID = {ef, cv, nd, ipm}`. `_kpiSortAttach` y `w22_renderCardTabs` pasan el grid correcto por métrica.

**Bug 3 — `_injectHistAttrs` con args incorrectos:**
Post-sort llamaba `window._injectHistAttrs(card)` — elemento DOM en lugar de `(tbodyId, rows)`. Fix: eliminada la llamada incorrecta; los `data-hist-*` los inyecta directamente `_cardRow` en cada `<div>`.

**Fix adicional en `w22_renderCardTabs`:**
El guard al preservar el header: ahora verifica `!header.hasAttribute('data-row-idx')` antes de usar `header.outerHTML`, evitando que un row de datos sea tratado como header.

### Root causes documentados

| Bug | Causa | Fix |
|---|---|---|
| Sort RND sin efecto | `_initAllSort` no conocía IDs `tab-nd-*`/`tab-rpm-*` + `RND_CARD_TABS` undefined | Bifurcar por modo + buscar IDs RND correctos |
| ConvRate desalineada post-sort | `_cardRow` hardcodeaba grid de Eficacia | Pasar `grid` como parámetro desde `_KPI_GRID` |
| `_injectHistAttrs` silencioso | Se llamaba con `(card)` en lugar de `(tbodyId, rows)` | Eliminar llamada; `_cardRow` inyecta attrs directamente |

### Archivos modificados esta sesión
`render_helpers.py` · `render_cr_p1.py` · `render_rnd_p1.py` · `js_override.js` · `PROMPT_CORE.md` · `NOTA_REFACTOR_PENDIENTE.md` · `HISTORIAL_SESIONES.md`

### Pendiente para W22
- Pipeline W21 con los archivos actualizados (commit pendiente)
- `RND_CARD_TABS`: evaluar si conviene generarlo desde `render_rnd_p1.py` (análogo a `CR_CARD_TABS`) para que el sort RND tenga re-render JS completo, no solo DOM estático

---



### Contexto
Sesión de fixes sobre el reporte W21 ya publicado en Netlify. No se recibieron nuevos datasets. El pipeline **no se re-corrió** al cierre — HTML publicado refleja todos los cambios (commit 7d8e12e).

### Cambios aplicados

#### Channel — Cards KPI globales y Cards AR
- **Catálogo canónico completo**: PP = [DerbySoft, Internal, HBSI, SynXis, Siteminder, Travelclick, Omnibees] · TP = [Expedia, HotelBeds Apitude, Hotel Unico V2, Travelgate]. Channels sin datos de la semana muestran "sin actividad" con `opacity:0.45`.
- **Orden**: peor eficacia primero → inactivos al final. Sort en Python (`render_cr_p1.py` `_build_card_rows_chan`, `render_cr_p2.py` `chans_pp/tp`).
- **Nombres visibles**: fix `width:100%` + `min-width:0` + `display:block` en span del nombre. Grid `72px 52px 36px` + `gap:10px` entre PP/TP.
- **Filas clickeables**: `cursor:pointer` + `data-hist-label` + `data-hist-w21/w20` en todas las filas (activas e inactivas).
- **Listener de click extendido** (`assemble_unified.py PANEL_LISTENER_JS`): acepta tanto `<tbody>` (tablas AR) como `<div id="ar{n}-chan-div">`. Segundo click resetea a global. Sombra de canasta activa al seleccionar.
- **Cards KPI y AR unificadas**: `_chanRow` en `w22_renderCardTabs` y `chanRowAR` en `_arRenderChan` usan la misma lógica — catálogo, orden, estilo, inactivos.

#### Orden de ejecución JS — Bug crítico
- **`w22_update()` movido al final de `js_override.js`**: en `demo_js_main.js` el render inicial llamaba `w22_update()` antes de que `_cardRow` y `w22_renderCardTabs` estuvieran definidas (JS hoisting no aplica a `var` assignments). Resultado: todos los nombres de elementos aparecían vacíos. Fix: comentar `w22_update()` en `demo_js_main.js`, moverlo al final de `js_override.js` después de todas las definiciones.

#### W20 = `—` y WoW = `NaN` en cards AR
- **Root cause**: `ar_updateKPIs` leía `HIST_CR['hcr-panel-ef'].vals` que está vacío al cargar (el canvas del panel no se inicializa hasta después). El `||` de JS no descartaba el objeto vacío.
- **Fix definitivo**: agregar `ef_prev`, `cv_prev`, `ef_wow`, `cv_wow` directamente en `CR_CV` y `RND_CV` desde Python (`render_cr_p2.py`, `render_rnd_p2.py`). El JS lee de `cdata` que siempre está disponible sin depender del timing de HIST_CR.
- **Fix adicional**: `cdata.ef = '93,15%'` → se le agregaba `+'%'` → `'93,15%%'` → `parseFloat = NaN`. Removido el `+` extra.

#### Header "Week W21" → "Week 21"
- `render_cr_p1.py`: `{WEEK_NUM}` tomaba el env var `WEEK=W21`. Cambiado a `{VOL_NUM}` = `21`.

#### Espaciado visual
- `masthead` margin-bottom: 16px → 8px (`asset_shared_head.html`)
- Switcher padding-top: 20px → 10px (`assemble_unified.py`)
- Filter-wrap margin-top: 16px → 8px
- `kpis-hero` margin-bottom: 12px → 6px (`render_cr_p1.py`, `render_rnd_p1.py`)
- `.hero` padding: 16px/24px → 8px/12px (`asset_shared_head.html`)

#### Numeración cards AR
- Color `var(--ink-muted)` → `var(--ink)` negro (`js_override.js trow_ar`)

### Root causes documentados

| Bug | Causa | Fix |
|---|---|---|
| Nombres vacíos al cargar | `w22_update()` corría antes de que `_cardRow` estuviera definida | Mover al final de `js_override.js` |
| WoW = NaN en carga inicial | `HIST_CR['hcr-panel-ef'].vals` vacío en timing inicial | `ef_prev/ef_wow` calculados en Python y expuestos en `CR_CV` |
| Doble `%` en ef21 | `cdata.ef+'%'` cuando `cdata.ef` ya tenía `%` | Remover el `+` |
| Channel click no funciona | `row.closest('tbody')` = null para divs del channel | Extender listener a `closest('[id$="-chan-div"]')` |

### Archivos modificados esta sesión
`render_cr_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `js_override.js` · `assemble_unified.py` · `asset_shared_head.html` · `HISTORIAL_SESIONES.md` · `PROMPT_CORE.md`

### Pendiente para W22
- **Refactor centralización CR/RND**: ver `NOTA_REFACTOR_PENDIENTE.md` — ejecutar antes de recibir datasets W22. Urgencia alta: esta sesión evidenció que `_chanRow` y `chanRowAR` son prácticamente idénticas y se mantienen por separado.

---

## 📝 Sesión W21-post3 · Mayo 2026 · Sort + Top 10 + UX cards

### Contexto
Sesión de UX y funcionalidad sobre el HTML W21 generado en sesiones anteriores. No se recibieron nuevos datasets — todos los cambios son sobre el mismo pickle W21. El pipeline **no se re-corrió** al final (no es necesario: los scripts están actualizados y listos para W22).

### Cambios aplicados

#### Cards KPI globales (render_cr_p1.py · render_rnd_p1.py)
- **Top 10 fijo sin "Ver más"**: reemplazado el sistema top5+next5+botón por 10 rows siempre visibles. Eliminada clase `rows-more` de los primeros 10. Rows 10+ siguen con `sb-hidden`.
- **Formato tráfico**: `{número} Tráfico` → `<strong>Tráfico:</strong> {número}` en todas las cards (Eficacia, ConvRate, NoDispo, IPM).
- **Línea de tráfico en RND**: agregada a `render_kpi_card_nodispo()` y `render_kpi_card_rpm()` — no existía. Lee de `M['global_current']['trafico']` y prev de `M['global_w17']`.
- **Alertas Críticas eliminadas**: sección quitada de `assemble_unified.py / SHARED_CONTAINERS`.

#### Cards AR (js_override.js)
- **Top 10 fijo**: `ar_renderTable` hace `rows.slice(0,10)` sin botón "Ver más".
- **Numeración original preservada al ordenar**: `trow_ar(r, n, origPos)` — si el elemento era #47 en el ranking original, muestra `47.` incluso cuando aparece primero tras el sort.
- **Channel con split PP/TP en 2 columnas**: `_arRenderChan(n)` genera grid `1fr 1fr` igual a las cards KPI. La tabla se oculta y se muestra un div dedicado para Channel.
- **Persistencia de selección entre canastas**: `ar_update()` guarda el `data-hist-label` seleccionado y lo re-selecciona tras cambio de canasta.
- **Formato tráfico**: `{número} Tráfico` → `<strong>Tráfico:</strong> {número}` en `ar_updateKPIs`.
- **Banda separada card 2**: `band_cv`/`bbg_cv`/`bfg_cv` expuestos en `CR_CV` y `RND_CV` — card 2 usa la banda de IPM (RND) o ConvRate (CR), no la banda de NoDispo/Eficacia.
- **WoW tráfico**: `traf_wow` calculado en Python y expuesto en `CR_CV`/`RND_CV`.

#### Sistema de ordenamiento por columna (js_override.js)
- Clickear header Tráfico o Métrica ordena ASC → DESC → Original
- **Sort sobre 100 rows reales**: cards KPI leen de `CR_CARD_TABS[canasta]` (100 rows), cards AR leen de `_arRows()` / `_arDimRows()` en el momento del click
- Sin flechas en el texto del header (no desalinean columnas) — indicador visual: `underline + color accent` en la columna activa
- `_kpiSortAttach`: engancha en los span headers de `.kpi-tab-rows`; re-engancha siempre con los 100 originales
- `_arSortAttach`: distingue `ar{n}-th` (hotel) vs `ar{n}-td` (dim) para leer el source correcto; usa IIFE para closure correcto

#### Datos CR_CV / RND_CV (render_cr_p2.py · render_rnd_p2.py)
- Agregados: `trafico`, `vol`, `traf_wow`, `band_cv`, `bbg_cv`, `bfg_cv` — expuestos en el JSON de `CR_CV` y `RND_CV`
- RND usa `fmt_big()` para el tráfico (12,2B) igual que el subhead del hero

#### Searchbox filter (asset_shared_head.html)
- `ri < 5` → `ri < 10` en todos los puntos del filter — el reset de búsqueda mostraba solo 5 rows en vez de 10

#### JSON top 100 (render_cr_p2.py · render_rnd_p2.py)
- Todos los `.head(10)` → `.head(100)` en `build_canasta_data` y `build_canasta_data_rnd`
- CR_D y RND_D ahora tienen 100 rows en `hotels_crit`, `hotels_br`, `hotels_sc`, `corps`, `dests`
- Part 2 CR: 87K → 460K chars · Part 2 RND: 54K → 367K chars

### Root causes de bugs encontrados en esta sesión

**"Sort ordena solo los 10"**: el searchbox filter tenía `ri < 5` y reseteaba a 5 rows visibles al cargar. `w22_renderCardTabs` los sobreescribía con 10, pero `_kpiSort` capturaba el DOM antes de ese re-render. Fix: `ri < 10` + `_kpiSortAttach` lee de `CR_CARD_TABS` directamente.

**"Numeración nueva al ordenar"**: `trow_ar(r, n, idx+1)` donde `idx` era la posición en el sorted (0-9), no en el original. Fix: wrappear rows con `{r, origPos}` antes de ordenar.

**"Closures de sort incorrectos"**: el forEach con `var i` en IE-style no captura `i` correctamente. Fix: IIFE `(function(colIdx){...})(i)`.

### Archivos modificados esta sesión
`render_cr_p1.py` · `render_rnd_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `js_override.js` · `demo_js_main.js` · `asset_shared_head.html` · `assemble_unified.py` · `PROMPT_CORE.md` · `HISTORIAL_SESIONES.md` · `NOTA_REFACTOR_PENDIENTE.md` (nuevo)

### Pendiente para W22
- **Refactor centralización CR/RND**: ver `NOTA_REFACTOR_PENDIENTE.md` — ejecutar antes de recibir datasets W22

---

## 📝 Sesión W21 · Mayo 2026 · Migración HTML unificado + Excels consolidados

### Contexto
Migración arquitectural completa desde dos HTMLs separados (CR + RND) a un único `SUPPLY_WNN.html` con switcher interactivo. Simultáneamente, consolidación de 8 Excels en 2.

### Cambios aplicados

#### HTML unificado
- **`render_cr_p1.py`**: eliminada apertura `<html><body><div class="shell">`. Ahora genera `<section id="section-cr" class="report-section section-cr">`.
- **`render_rnd_p1.py`**: idem, genera `<section id="section-rnd" class="report-section section-rnd">`.
- **`render_cr_p3.py`**: eliminado `FOOTER` y cierre de documento. Solo cierra `</section>`.
- **`render_rnd_p3.py`**: eliminado `FOOTER`, `</div>` shell, `</body>`, `</html>`. Solo cierra `</section>`.
- **`asset_supply_head.html`** (nuevo): head unificado con scoping CSS `.section-cr` / `.section-rnd`. Todos los selectores de tabs llevan prefijo de sección para evitar colisiones de IDs. Incluye CSS del switcher y back-hub.
- **`assemble_unified.py`** (nuevo): reemplaza `assemble_cr.py` + `assemble_rnd.py`. Ensambla 6 parciales en `SUPPLY_WNN.html` con switcher sticky, back-hub, FOOTER_JS unificado (TOC observer + switcher JS + cr_setTab).

#### Excels consolidados (8 → 2)
- **`excel_cr.py`** (reescrito): función `build_sheet()` genera las 9 secciones por hoja. 4 hojas: Global · B2C · B2B-OP · CUG. Cada canasta = filtro de `p80_hotel` por `DistributionCategory`. Elimina `excel_cr_canastas.py`.
- **`excel_rnd.py`** (reescrito): función `build_sheet()` + helper `agg_dim()`. 4 hojas: Global · B2C · B2B-OP · CUG. Cada canasta = filtro de `df18`. Elimina `excel_rnd_canastas.py`.

#### Assets visuales (demo pre-W21)
- **`asset_shared_head.html`**: gaps reducidos — `.masthead margin-bottom: 16px → 8px`, `.hero padding-top: 16px → 8px`, `kpis-hero margin-top: 12px → 6px`.

### Estructura repo GitHub W21+
```
reports/week-NN/SUPPLY_WNN.html   ← nuevo
checkrates/week-NN/               ← solo Excels (sin HTML)
rates-nodispo/week-NN/            ← solo Excels (sin HTML)
```
W16-W20 mantienen estructura anterior.

### Archivos deprecados (excluir del ZIP proyecto)
`assemble_cr.py`, `assemble_rnd.py`, `excel_cr_canastas.py`, `excel_rnd_canastas.py`

### Pendiente (pasos 6-10 del plan de migración)
- `build_package.py`: carpeta `reports/week-NN/`, URL helper histórico, 2 cards hub con anchors
- `render_mail_v3.py`: URL unificada con anchor
- `run_pipeline.py`: paso 4 → `assemble_unified.py`, paso 5 → 2 scripts Excel
- `github_commit.py`: SCRIPT_FILES actualizado, EXCLUDE ampliado
- `update_docs.py`: URL unificada en README_QUICK

---

## 📚 Memoria de bugs históricos resueltos

1. **CSS especificidad tabs** · `.tab-panel{display:none}` del CSS hero anulaba `:checked ~`. Fix: prefix `.tabs-block` + `!important`.
2. **Channel CR ConvRate filtros** · `Bookings>5` y `CR_Unicos>100` excluían channels Third Party. Fix: sin filtros en `TAB_EF/TAB_CV['channel']`.
3. **banda_rpm thresholds viejos** · `engine.py` tenía 1/2.5/4. Fix: $200/$650/$1500 USD/M.
4. **CSS `--amber` en CR** · estaba `#EA0074` (magenta RND). Fix: `#5C469C` (violet) en `asset_cr_head.html`.
5. **Sev_dict pandas Series vs dict** · `sum(sev_dict.values())` falla con Series. Fix: `int(sev_dict.sum()) if hasattr(sev_dict, "sum") else int(sum(sev_dict.values()))`.
6. **Merge conflict `index.html` publicado** · conflict markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`) se publican como texto plano visible. Fix: sobreescribir con archivo limpio y hacer push directo. Ver `COMMIT_GUIDE.md`.
7. **Placeholders `{{}}` sin resolver en `index.html`** · al hacer `str_replace` quirúrgico. Fix: `build_package.py` genera el HTML completo sin placeholders — nunca editar a mano.
8. **`_WOW_NEUTRO` como string literal** en `_render_dim_table` en vez de variable. Fix: reemplazar strings literales por la variable.
9. **`g_channel_w17` no disponible** dentro de funciones de render porque `D` no era variable global. Fix: cargar explícitamente al nivel de módulo en `render_cr_p2.py`.
10. **`sin_conv` sin `Eficacia_WoW_pp`** · verificado — el enriquecimiento ocurre en render, el pickle no necesita cambiarse.
11. **`TAB_RPM` con `IPM=0`** — fix: `min_ipm=True` en `make_tab()`.
12. **Corps con tráfico <500K con NoDispo extrema** — fix: `MIN_T=500_000` en tabs de dimensión.
13. **`panel-header` 3 cols vs `panel-row` 4 cols** — desalineado visual. Fix: unificar a `1fr 62px 62px 46px`.
14. **CSS pintaba todos los nombres en magenta** · regla `.tab-panel div span:not(.tab-key)`. Fix: reemplazar por `.tab-panel div span.tab-val`.
15. **Métricas globales sobre `df18` completo** en lugar de P80. Fix: usar `p80_hotel` / `df18_p80`.
16. **`metrics_recalc.pkl` inexistente en `render_mail_v3.py`** · el archivo nunca existió en el pipeline normal. Fix: v3.2 deriva IPM y GBM directamente de `rnd_wNN_data.pkl` (`M['global_w18']['ipm']` y `M['global_w18']['gb_usd']`).
17. **Path hardcodeado en `excel_rnd.py`** · tenía `/home/claude/final_w18/rnd_w19_data.pkl`. Fix: ruta relativa `rnd_wNN_data.pkl`.
18. **ZIP del repo con prefijo `Price_WNN/`** · al descomprimir creaba subcarpeta en lugar de caer en raíz. Fix: `f.relative_to(ZIP_ROOT)` en lugar de `f.relative_to(ZIP_ROOT.parent)` en `build_package.py`.

---

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes visuales)

### WoW con unidades claras (RND)
- `pp` en %NoDispo, `%` relativo en IPM — en p1, p2, p3
- Tabla Análisis por Dimensión: 2 cols WoW separadas (`%NoDispo · WoW · IPM · WoW`)
- CSS grid: `1fr 62px 36px 58px 36px`

### WoW ConvRate en tabla dim CR
- Orden: `CR únicos · BKGS · ConvRate · WoW · Eficacia · WoW`
- Helper `_fmt_wow_cv` (pp) en `render_cr_p2.py`

### Tab Hotel Conv Rate — solo Bookings > 0
- Sin Conversión excluida del card Conv Rate (tiene su propia tab)

### Plan de Acción con Carryover
- `template_seguimiento.py`: bloque HTML Carryover con badge gris + `desde WNN`
- `build_package.py`: genera `plan_seguimiento_WNN.md`
- ES/MP → OPEN (auto) · QW → PENDIENTE_QW (revisión manual)
- Aplica global + canastas CR y RND

### Semana dinámica en masthead
- `VOL_NUM`, `PERIODO`, `MES_AÑO` en pickle (`calc_cr.py` y `calc_rnd.py`)

### CONFIG SEMANAL para W20
Cambiar en `calc_cr.py`: `WEEK='W20'`, `PERIODO`, `MES_AÑO`, `VOL_NUM`, rutas datasets W20 y W19
Cambiar en `calc_rnd.py`: mismo patrón

---

## 📝 Cambios post W19 · Mayo 2026 (sesión inicial pipeline)

### Pipeline · Paso 6 nuevo: build_package.py
- Genera `index.html` del hub automáticamente desde los pickles (KPIs, WoW, bandas, severity counts)
- Genera `Price_WNN.zip` con estructura del repo lista para commit sin prefijo de carpeta
- Config semanal al tope del script: `WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`

### render_mail_v3.py · v3.2
- Eliminada dependencia de `metrics_recalc.pkl` (bug #16)
- CONFIG SEMANAL al tope del archivo
- Marcadores `<!-- DRAFT_BODY_START -->` / `<!-- DRAFT_BODY_END -->` para extracción automática del body
- IPM en lugar de RPM en el cuerpo del mail

### Incidencia dataset RND W19
- Primera versión llegó con 5 columnas (faltaban `CorpName`, `PaisDestino`, `Destino`, `gb_usd`)
- Resolución: solicitar dataset corregido antes de correr el pipeline
- **Regla permanente:** validar las 9 columnas del dataset RND antes de ejecutar `calc_rnd.py`

### destinatarios.md
- Son **15** destinatarios (el prompt anterior decía 14 por error)
- Archivo incorporado al proyecto Claude y al ZIP de proyecto

---

## 📝 Cambios post W18 · CR (sesión validación visual Mayo 2026)

### Orden de secciones globales CR
- **RE movido antes de alertas**: orden final → RE → Alertas → Severity → Hoteles → Dimensión → Plan

### Visual / UX
- Pills WoW neutras con `_WOW_NEUTRO` (bg `#F2EEE6` · color `#8A8377`)
- Channel hero 100% eficacia: pill verde `= 0,0`
- Color Third Party: cyan → violet en dimensión global y canastas
- WoW en Análisis por Hotel canasta (4 cols: Hotel · ConvRate · Eficacia · WoW)
- WoW en Channel dimensión global y canasta
- Normalización destinos con `_CITY_DASH_PATTERN` en `render_helpers.py`
- RE margin-top: 64px→24px global · 32px→16px canasta
- Fondos: `--paper-soft: #F2EDE0` · tabs-block `var(--paper)`

### Archivos modificados
`render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_helpers.py` · `template_resumen.py` · `template_alertas.py` · `asset_cr_head.html`

---

## 📝 Cambios post W18 · RND (sesión completa Mayo 2026)

### Pipeline RND · calc_rnd.py reescrito
- Lee Excel directamente (sin pickles pre-procesados)
- Requiere W(N) + W(N-1) para WoW real
- `gb_usd.clip(lower=0)` por fila — cancelaciones negativas no deprimen IPM
- P80 aplicado consistentemente en TODAS las dimensiones
- `MIN_T = 500_000` en tabs de dimensión — evita outliers de bajo volumen

### P80 aplicado consistentemente — CR y RND
| Componente | CR | RND |
|---|---|---|
| Métricas globales | `df18_p80` | `p80_hotel` |
| Tabs hero | `df18_p80` | `g_pais/dest/corp` sobre `df18_p80` |
| Canasta: métricas | `sub18_p80` | `sub18_p80` |
| Canasta: agg Corp/Dest/País | `agg_dim(sub18_p80, ...)` | `agg_dim(sub18_p80, ...)` |
| Channel | `df18` completo | N/A |

### Archivos modificados
`calc_rnd.py` · `calc_cr.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `asset_rnd_head.html`

---

### Bug crítico · display:grid en TRs (sesión W21 cleanup post-migración)

**Síntoma:** En las pestañas hotel RND (Críticos/DNC/BR/SC), las filas se veían con fondo distinto y alineamiento ligeramente roto comparado con las dim tabs. Diferencias visuales sutiles entre pestañas que no debían existir.

**Causa raíz:** El JS de searchbox / "Ver más" en `asset_shared_head.html` setea `r.style.display = 'grid'` cuando muestra filas. Esto se escribió originalmente para filas que eran `<div>` con CSS grid, pero tras la migración W21 a HTML tables las filas son `<tr>`. Aplicar `display:grid` a un `<tr>` rompe el comportamiento `table-row` nativo: las celdas se renderizan como grid items en lugar de cells, el alineamiento de columnas se rompe y el fondo del TR pierde control sobre los TDs.

**Fix:** 7 reemplazos en `asset_shared_head.html` para hacer el display condicional al tipo de elemento:
```javascript
r.style.display = (r.tagName === 'TR' ? '' : 'grid');
```
Para TRs el `''` resetea al display nativo (`table-row`); para divs sigue aplicando `grid`. Mantiene compatibilidad con código legacy de grids al mismo tiempo que las nuevas tablas funcionan correctamente.

**Líneas afectadas:** 423 (filter searchbox), 458 (init), 492 / 495 (otro filter), 564 / 576 (otro toggle), 627 (Ver más / Ver menos toggle).


### Sesión post W21 · Bold values + CR dim col widths + bugs visuales menores

**Bold en valores Eficacia y ConvRate (CR):**
Los valores numéricos de Eficacia y ConvRate en CR ahora se renderizan con `font-weight:700`. Aplica:
- Globales (cards hero KPI 93,15% / 1,57%): `font-size:40px;font-weight:700`
- Canastas (cards KPI por canasta): `font-size:40px;font-weight:700`
- Filas internas de cards hero (destino/corp/hotel/channel): cell value `font-weight:700`
- Filas de tabla dim (Corp/Destino/Channel): TD value `font-weight:700`
- Filas de tabla hotel: TD value cuando `col.key in ('cv','ef')` → `font-weight:700`
- Filas hotel canasta: span values con `font-weight:700`
- Class `.efic` (canastas panel-row): `font-weight:700` en `asset_shared_head.html`

**CR dim · column widths reducidos:**
Las tablas de Análisis por dimensión (Corp/Destino/Channel) tenían colgroups con total 1236px que desbordaba el contenedor de ~1168px y cortaba la columna WoW final. Reducido a totales que caben:
- 8 cols (con WoW CV + WoW Ef): `[800, 76, 68, 52, 52, 32, 52, 32]` = 1164px
- 7 cols (con WoW Ef): `[800, 76, 78, 62, 60, 65, 42]` = 1183px
- 6 cols (sin WoW): `[800, 80, 80, 64, 64, 70]` = 1158px

**Verificaciones de bugs reportados:**
- Canastas WoW: confirmado presente en RND (358+348 con flechas) y CR (149+90)
- Guiones en columnas WoW: son hoteles/destinos sin data WoW (esperado, no bug)
- WoW ConvRate en hotel CR: presente en tabs crit/br/mcv (Sin Conversión no aplica - sin BKGS)

### Archivos modificados
`render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `asset_shared_head.html`


**Última actualización:** Mayo 2026 · post W19 · build_package + hub pipeline · bugs #16 #17 #18 · destinatarios 15

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes Excel + HTML)

### Excels CheckRates (CR)
- **Críticos** (global + canastas): sort explícito `sort_values('Eficacia', ascending=True)` — menor Eficacia primero
- **Por Corporativo** (global + canastas): agrega columna `Channels` con los canales únicos del corp via `hotel_channel_map`

### Excels Rates No Dispo (RND)
- **RPM → IPM (USD/M)**: todas las columnas de display renombradas — `.rename(columns={'RPM':'IPM (USD/M)','BandaRPM':'Banda IPM'})`
- **Colores de banda IPM**: nuevo parámetro `banda_col2` en `add_table()` permite colorear dos columnas de banda por fila
- **Sin Conversión**: agrega `Font(..., color='8A8377')` en `BAND_FONTS` para color muted correcto

### Reportes HTML CR
- **Headers tab hotel**: `'Checkrates'` → `'CR Únicos'` · `'ConvRate'` → `'Conv Rate'` (global + canastas)
- **Headers tabla dim**: `'CR'` → `'CR Únicos'` · `'CV'` → `'Conv Rate'` (Corp + Dest + Channel, global + canastas)

### Bugs corregidos
| Bug | Archivo | Descripción |
|---|---|---|
| #28 | `excel_cr.py` | Sort Críticos sin `ascending=True` explícito |
| #29 | `excel_cr.py` | Por Corporativo sin columna Channel |
| #30 | `excel_rnd.py` | Columnas `RPM`/`BandaRPM` visibles en Excel |
| #31 | `excel_rnd.py` | Colores banda IPM no aplicaban (`banda_col2`) |
| #32 | `excel_rnd.py` | `Sin Conversión` sin color en `BAND_FONTS` |
| #33 | `render_cr_p2.py` | Header tab hotel `Checkrates`/`ConvRate` |
| #34 | `render_cr_p2.py` | Header tabla dim `CR`/`CV` |
| #35 | `render_cr_p3.py` | Header dim canastas `CR`/`CV` |
| #36 | `calc_rnd.py` | `ZeroDivisionError` cuando dataset W(N-1) vacío |

### Archivos modificados
`excel_cr.py` · `excel_rnd.py` · `render_cr_p2.py` · `render_cr_p3.py` · `calc_rnd.py`

---

**Última actualización:** Mayo 2026 · post W19 · fixes Excel IPM/CR Únicos/Corp Channel · bugs #28–#36

## 📝 Cambios post W19 · Mayo 2026 (sesión fixes visuales + estructura)

### Nomenclatura archivos corregida
- `assemble_cr.py` y `assemble_rnd.py`: output ahora genera `CheckRates_Reporte_Editorial.html` y `RatesNoDispo_Reporte_Editorial.html` (no `Supply_CheckRates_WNN.html`)
- `build_package.py`: lee los archivos con el nombre canónico correcto

### Estructura ZIP repo — `_governance/` completa
- `CHANGELOG.md` y `COMMIT_GUIDE.md` se incluyen en `_governance/` (no en raíz)
- `build_package.py` los agrega automáticamente al ZIP

### `build_package.py` — limpieza automática post-empaquetado
- Al finalizar el Paso 6, elimina todos los archivos intermedios de `/mnt/user-data/outputs/`
- Solo quedan los dos ZIPs: `Price_WNN.zip` (repo) y el ZIP del proyecto Claude
- **Regla de entrega:** presentar SOLO los dos ZIPs al final del pipeline — nunca archivos sueltos

### Fixes visuales CR — canastas (`render_cr_p3.py`)
- **Tabs KPI cards**: nombres de filas en negro (`color:var(--ink)`) — antes heredaban violet del CSS global
- **WoW ConvRate en tab Hotel card CV**: enriquece `df_hot_cv` con `g_hotel_w17` para calcular `ConvRate_WoW_pp`
- **Tabla dim nombres**: `font-weight:400` y `color:var(--ink)` — antes bold y violet (`asset_cr_head.html`)
- **Channel split PP/TP**: presente en canastas · color de nombres en negro (no violet)

### Fixes visuales RND — canastas (`asset_rnd_head.html`)
- Grid panel-row: `1fr 62px 34px 58px 34px` → `1fr 64px 38px 62px 38px`
- Gap: `6px` → `10px` — más espacio entre columnas

### Fixes visuales CR — tab hotel global (`render_cr_p2.py`)
- Anchos de columna reducidos: `Checkrates 80px→72px` · `ConvRate/Eficacia 65px→58px` · `WoW 44px→38px`
- Más espacio para el nombre del hotel

### Tabs canasta — efecto folder (`render_rnd_p3.py`, `render_cr_p3.py`)
- El `extra_css` de cada canasta ahora incluye el estilo base del `tab-label` (border, radius, margin-bottom:-1px)
- Antes los tabs de canasta no mostraban el efecto "folder activo" — ahora coinciden con el hero global

### Headers de columna CR — labels finales
- Tab hotel: `'Checkrates'` (no `'CR Únicos'`) y `'ConvRate'` (no `'Conv Rate'`) — versión corta para que entre en una línea
- Tabla dim: `'Checkrates'`, `'ConvRate'` — mismo criterio

### WoW sin unidad `pp` en pills de pestañas
- Las pills WoW en las pestañas de tabs muestran `+10,36` (sin `pp`) — más compacto
- El hero box WoW (recuadro grande W17/WoW/W18) conserva `pp` — tiene espacio suficiente
- Aplica en RND y CR, global y canastas

### Bugs corregidos
| Bug | Archivo | Descripción |
|---|---|---|
| #37 | `assemble_cr.py` | Nombre output `Supply_CheckRates_WNN.html` → `CheckRates_Reporte_Editorial.html` |
| #38 | `assemble_rnd.py` | Nombre output `Supply_RatesNoDispo_WNN.html` → `RatesNoDispo_Reporte_Editorial.html` |
| #39 | `build_package.py` | ZIP sin `CHANGELOG.md` y `COMMIT_GUIDE.md` en `_governance/` |
| #40 | `build_package.py` | Archivos intermedios sueltos en outputs tras pipeline — fix: limpieza automática |
| #41 | `render_cr_p3.py` | Nombres en violet en tabs KPI canasta — fix: `color:var(--ink)` explícito |
| #42 | `render_cr_p3.py` | WoW ConvRate faltaba en tab Hotel del card CV canasta |
| #43 | `asset_cr_head.html` | `.panel-row .label` bold y violet — fix: `font-weight:400;color:var(--ink)` |
| #44 | `render_rnd_p3.py` `render_cr_p3.py` | Tabs canasta sin efecto folder — fix: CSS base `tab-label` en `extra_css` |
| #45 | `render_cr_p2.py` | Columnas tab hotel muy anchas — fix: anchos reducidos |
| #46 | todos los render | Pills WoW con `pp` en pestañas — fix: quitar `pp` solo en pills, mantener en hero box |

### Archivos modificados
`assemble_cr.py` · `assemble_rnd.py` · `build_package.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `render_rnd_p1.py` · `render_cr_p1.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

**Última actualización:** Mayo 2026 · post W19 · fixes visuales canastas + nomenclatura + WoW pills + build_package limpieza · bugs #37–#46

---

## 📝 Cambios post W19 · Mayo 2026 (sesión verificación integridad W20)

### Audits + Documentación nueva
- `audit_w20.md` — Verificación integridad proyecto · detecta inconsistencias config
- `READY_W20.md` — Checklist pre-flight W20 · config semanal paso a paso

### Limpieza proyecto Claude
- ❌ Eliminado `_TEMPLATE_Hub.html` del proyecto Claude — vive SOLO en GitHub bajo `_template/`
- Proyecto ahora tiene **46 archivos** (limpio · sin archivos obsoletos)

### Status pre-W20
- ✅ Pipeline completamente funcional (6 pasos)
- ✅ Config semanal lista (5 variables en 4 scripts)
- ✅ Documentación consolidada
- ✅ Decisiones de bandas + colores sin cambios respecto a W19

---

**Última actualización:** Mayo 2026 · post W19 · audits W20 + limpieza proyecto

---

## 🐛 FIX #47 · calc_cr.py · Inconsistencia CONFIG WEEK

**Problema detectado (11 mayo 2026):**
- `calc_cr.py` línea 12 decía: `WEEK = 'W18'`
- Pero línea 33-34 leía: `Dataset_CheckRates_W19.xlsx` + W18
- Y línea 378 generaba: `cr_w19_data.pkl`
- Y línea 381 printaba: `cr_w18_data.pkl` (confuso)

**Mismatch:** CONFIG decía W18, pero datasets y output eran W19 (confusión operativa)

**Solución aplicada (11 mayo 2026):**
```python
# Línea 12: Cambiar de
WEEK = 'W18'

# A:
WEEK = 'W19'

# Línea 381: Cambiar de
print(f"✅ Pickle guardado: cr_w18_data.pkl")

# A:
print(f"✅ Pickle guardado: cr_w19_data.pkl")
```

**Status:** ✅ APLICADO · calc_cr.py ahora alineado con datasets W19

**Impacto:** Pipeline W19 funcional · W20 tendrá CONFIG correcta desde inicio

---

**Última actualización:** Mayo 2026 · FIX #47 aplicado · calc_cr.py CONFIG alineado

---

## 📝 Módulo Histórico CR · Evolución Histórica (Mayo 2026 · post W20)

### Qué se agregó
Módulo **"Evolución Histórica"** reactivo en todas las cards KPI del reporte CheckRates:
- **2 cards globales** (Hero · Eficacia + ConvRate) — `render_cr_p1.py`
- **6 cards canasta** (B2B-OP · CUG · B2C × Eficacia + ConvRate) — `render_cr_p3.py`

### Posición en el DOM de cada card
```
valor grande → pill banda → gauge 5 niveles → wow_box → tabs (10 elementos) → [MÓDULO]
```

### Funcionalidad
- **Estado default:** datos globales de la card visibles sin interacción
- **Click en elemento** (destino / corp / hotel / channel): canvas + 5 métricas + banda se actualizan
- Elemento seleccionado queda highlighted con `var(--accent-soft)`
- **Curva (Canvas):** escala LOCAL del elemento — muestra el trend exacto W14-W21
- **Barras (Sparkline):** escala GLOBAL vs target de la card — muestra severidad relativa al objetivo
- Datos W14-W20 ficticios · W21 real del pickle · W20 del elemento desde `Eficacia_W17` / `ConvRate_W17`

### Colores
Usa exclusivamente variables CSS del sistema (`var(--paper)`, `var(--accent)`, etc.) + colores exactos de `_BANDA_COLORS` en `render_helpers.py`. Súper Crítica: badge negro/blanco, footer texto oscuro (`#161616`).

### Archivos modificados
| Archivo | Cambio |
|---|---|
| `historico_module_v2.py` | **NUEVO** · función `render_historico_cr()` · módulo completo |
| `render_cr_p1.py` | Import + llamada en `render_kpi_card_eficacia` y `render_kpi_card_convrate` · rows con `data-hist-*` |
| `render_cr_p3.py` | Import + llamada en `kpi_card_canasta` · `tab_rows_canasta` con `data-hist-*` |

### Pendiente (próximas sesiones)
- Módulo histórico en secciones Análisis por Hotel y Análisis por Dimensión (CR)
- Módulo histórico en RND (misma arquitectura)
- Datos históricos reales W14-W20 cuando estén disponibles en pickle (reemplazar `_FICTICIOS`)

19. **Labels canvas ilegibles en módulo histórico CR** · `rgba(100,90,80,0.55)` y `font-size:7px` → Fix: `0.80` y `8px`. Archivo: `historico_module_cr.py`.
20. **Curva plana en módulo histórico CR** · fixtures con variación insuficiente → Fix: nuevos valores con delta realista entre semanas. Archivo: `historico_module_cr.py`.
21. **`W14`/`W21` hardcodeados en footer sparkline** · mostraba siempre W14-W21 sin importar `current_week` → Fix: `{semanas[0]}` / `{semanas[-1]}` dinámicos. Aplica en `historico_module_cr.py` y `historico_module_rnd.py`.
22. **IPM accent `#A86A1D` reemplazado por `#7C2D12`** en fix de paleta global → afectaba `ACCENT_HEX` de módulos IPM en HTML. Fix: reemplazo quirúrgico por `#4FC3F4` solo en contexto IPM.
23. **No había forma de volver a Global** en módulo histórico tras seleccionar elemento → Fix: label "Global" clickeable + click en fila activa hace toggle/reset.
24. **Módulos históricos clonados sin listeners** — los módulos `hrnd-hotel-nd/ipm` y `hrnd-dim-nd/ipm` eran copias del global generado antes de que se agregaran `hist-update`/`hist-reset`. Fix: listeners inyectados directamente en los 4 módulos del HTML.
25. **`data-hist-nd="0.0"` en todas las filas** — la extracción de %NoDispo e IPM del HTML renderizado no matcheaba el patrón de spans. Fix: regex actualizado para extraer valores reales de cada fila.
26. **Exitosa turquesa `#4FC3F4` en severity** — la variable `--green:#4FC3F4` en el CSS head + colores hardcodeados en barras de progreso y pills. Fix: `--green:#085041` + replace de `#4FC3F4` en barras/pills de Exitosa. El cyan queda solo para CUG y IPM accent en RND.
27. **Gauge grosor inconsistente** — iteraciones con `height:3px/4px/8px` generaban barras desproporcionadas. Fix definitivo: todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros. → Fix: label "Global" clickeable + click en fila activa hace toggle/reset. · mostraba siempre W14-W21 sin importar `current_week` → Fix: `{semanas[0]}` / `{semanas[-1]}` dinámicos. Aplica en `historico_module_cr.py` y `historico_module_rnd.py`.

---
---

## 📝 Módulo Histórico CR · Evolución Histórica (Mayo 2026 · post W20 · sesión 1)

### Qué se agregó
Módulo **"Evolución Histórica"** reactivo en todas las cards KPI del reporte CheckRates:
- **2 cards globales** (Hero · Eficacia + ConvRate) — `render_cr_p1.py`
- **6 cards canasta** (B2B-OP · CUG · B2C × Eficacia + ConvRate) — `render_cr_p3.py`

### Posición en el DOM de cada card
```
valor grande → pill banda → gauge 5 niveles → wow_box → tabs (10 elementos) → [MÓDULO]
```

### Funcionalidad
- **Estado default:** datos globales visibles sin interacción
- **Click en elemento:** canvas + 5 métricas + banda se actualizan con datos del elemento
- **Curva (Canvas):** escala LOCAL del elemento — trend exacto W14-W21
- **Barras (Sparkline):** escala GLOBAL vs target — severidad relativa al objetivo
- Datos W14-W20 ficticios · W21 real del pickle · W20 desde `Eficacia_W17` / `ConvRate_W17`
- Título: "Evolución Histórica" (genérico, no limita a 8W)

### Archivos modificados
| Archivo | Cambio |
|---|---|
| `historico_module_v2.py` | **NUEVO** · función `render_historico_cr()` |
| `render_cr_p1.py` | Import + llamada en ambas cards globales · rows con `data-hist-*` incluyendo Channel |
| `render_cr_p3.py` | Import + llamada en `kpi_card_canasta` · `tab_rows_canasta` con `data-hist-*` |

---

## 📝 Módulo Histórico RND + Fixes CR (Mayo 2026 · post W20 · sesión 2)

### Módulo Histórico RND — `historico_module_rnd.py`

**NoDispo** (escala invertida — menor = mejor):
- Accent: `#EA0074` magenta · Target: `< 5%`
- Curva: eje Y invertido · zona relleno arriba de la curva (zona mala)
- Sparkline: barra más alta = más NoDispo = peor
- Métricas: "Mín 8W" verde · "Máx 8W" rojo

**IPM** (escala normal — mayor = mejor):
- Accent: `#A86A1D` amber · Target: `≥ $650`
- W20 del elemento desde columna `IPM_W18` del pickle
- Métricas: "Máx 8W" verde · "Mín 8W" rojo

**Cobertura:** 8 cards — 2 globales + 6 canastas

### Fixes CR aplicados
- **Channel tab clickeable**: `chan_row` y `chan_row_cv` con `data-hist-*`
- **Badge Súper Crítica dinámico**: `bbEl.style.color = bc.fg` en JS
- **Canvas = sparkline ancho**: `pR=10` · label target en HTML

### Archivos nuevos/modificados
| Archivo | Cambio |
|---|---|
| `historico_module_rnd.py` | **NUEVO** · módulo histórico RND completo |
| `render_rnd_p1.py` | Import + data-hist-* + módulo en ambas cards globales |
| `render_rnd_p3.py` | Import + data-hist-* en tab_rows_canasta + módulo en kpi_card_canasta |
| `render_cr_p1.py` | Channel clickeable (chan_row + chan_row_cv) |
| `historico_module_v2.py` | Fix JS badge Súper Crítica dinámico |

### Pendientes para W21+
- Fix color badge Súper Crítica en RND
- Ajustes spacing: tabs-row margin-top · módulo margin-top
- Módulo histórico en Análisis por Hotel y Dimensión (CR + RND)
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 3 · Fixes visuales módulos históricos + colores severity)

### Sistema de colores severity — correcciones definitivas

**Exitosa:** `#4FC3F4` (cyan) → `#085041` (verde teal) en todos los contextos:
- Barras de progreso del severity principal
- Pills de banda Exitosa
- Variable CSS `--green: #4FC3F4` → `--green: #085041` en `asset_cr_head.html` y `asset_rnd_head.html`
- Gauge de 5 niveles en `render_helpers.py` (4 ocurrencias)
- `template_severity.py` para tablas Severity (5 ocurrencias)
- `historico_module_v2.py` `_BANDA_COLORS` dict

**Súper Crítica:** `#161616` (negro) → `#A32D2D` (rojo oscuro) en pills (no en barras del gauge, que siguen negras).

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — mismo grosor, colores sólidos puros, sin transparencia. La banda activa se identifica por la pill encima, no por el gauge.

### Cyan `#4FC3F4` queda SOLO en 2 lugares válidos
1. `IPM_ACCENT` en `historico_module_rnd.py` (Arctic Blue corporativo, accent visual IPM)
2. Label "🔌 Third Party" en `render_cr_p1.py` líneas 197, 338 (color identitario Third Party CR)

### Módulos históricos Análisis por Hotel y Dimensión (RND)
- Resuelto problema de listeners faltantes: los módulos clonados `hrnd-hotel-nd/ipm` y `hrnd-dim-nd/ipm` ahora escuchan eventos `hist-update` y `hist-reset` correctamente
- Click en fila actualiza canvas + métricas + banda
- Click en label "Global" vuelve a vista por defecto

### Archivos modificados
`render_helpers.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `historico_module_rnd.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html`

### Pendientes que quedaron al cierre
- Módulo histórico en secciones Análisis por Hotel y Dimensión (CR) — pendiente desde W20 (cerrado en sesión 4)
- Datos históricos reales W14-W20 en pickle (siguen ficticios)

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 4 · Módulo histórico CR hotel/dim + Reformulación badges Opción D)

### Feature 1 · Módulo histórico CR en Análisis por hotel + Análisis por dimensión

Pendiente cerrado: portar el módulo histórico de RND a las dos secciones equivalentes en CR.

**Implementación:**
- Nueva función `render_historico_seccion_cr(canvas_id_ef, canvas_id_cv, banda_ef, val_ef, banda_cv, val_cv)` en `render_cr_p2.py` (análoga a `render_historico_seccion_rnd`)
- Listeners `hist-update` / `hist-reset` agregados a `historico_module_v2.py` para que el módulo CR pueda ser controlado desde wrappers externos (backward-compatible con el listener interno de `.kpi-card` de Hero/canastas)
- Parámetro opcional `with_hist=True` en `render_top_table_cr` y `_render_dim_table`: enriquece filas con `data-hist-w21/w20/cv-w21/cv-w20/label` + `cursor:pointer`
- Integración en `render_bloque_hoteles_cr` y `render_bloque_dimensiones_cr` con canvas IDs `hcr-hotel-ef/cv` y `hcr-dim-ef/cv`

**UX:** click en fila de tabla → ambos módulos (Ef + CV) se actualizan en sincronía. Re-click → reset a Global. Aislamiento: clicks en sección NO afectan cards hero y viceversa.

### Feature 2 · Reformulación badges severity (Opción D + paleta D)

Cierre del cambio que se había perdido en un revert. **Estilo Opción D** aplicado uniformemente a TODOS los badges del sistema:

```css
font-size: 13px              (canastas: 11px)
font-weight: 700
letter-spacing: .04em
text-transform: uppercase
padding: 10px 22px
border-radius: 3px
border: 1px solid {bd}
text-align: center
```

**Texto del badge:** solo nombre de banda en mayúsculas. **El "Target X%" ya NO va dentro del badge** — se renderiza como caption gris separado debajo, mediante nueva función helper `target_caption(target_text, font_size='11px')` en `render_helpers.py`.

**Función `banda_pill()` refactor:** el parámetro `target` se mantiene en la firma por compatibilidad pero se ignora (el target ahora se inyecta vía `target_caption()` por separado).

**Módulo histórico CR:** además del estilo Opción D, se quitó:
- La palabra "Banda" como label arriba del badge en la box principal
- El prefijo "Banda: " del footer (ahora dice solo `EXITOSA`, `REVISAR`, etc. en mayúsculas)

El módulo histórico RND ya estaba correcto desde sesión 2 — no requirió cambios en este barrido.

### Bugs corregidos
| Bug | Archivo(s) | Descripción |
|---|---|---|
| #81 | `render_helpers.py` | `banda_pill()` rediseñada · estilo Opción D · padding 10px 22px · font 13px · text-align center |
| #82 | `render_helpers.py` | Nueva función `target_caption()` para mostrar target separado del badge |
| #83 | `render_cr_p1.py`, `render_rnd_p1.py`, `render_cr_p3.py`, `render_rnd_p3.py` | Hero + canastas usan `pill_with_target` (pill + caption) en lugar de pill con target embebido |
| #84 | `historico_module_v2.py` | Quitar label "Banda" arriba del badge en módulo histórico CR |
| #85 | `historico_module_v2.py` | Footer del módulo histórico CR: quitar prefijo "Banda: " · mostrar solo nombre en mayúsculas |
| #86 | `historico_module_v2.py` JS | `updateMetrics()`: `el.textContent = banda.toUpperCase()` en lugar de `'Banda: ' + banda` |
| #87 | `render_helpers.py` `gauge_5levels` | Exitosa cyan `#4FC3F4` → verde teal `#085041` en 4 variantes (nodispo, rpm, eficacia, convrate) |
| #88 | `render_cr_p2.py` | Exitosa cyan → verde en 3 lugares (severity gauges) + fallback `#E8F7FD` → `#E1F5EE` |
| #89 | `render_rnd_p2.py` | Exitosa cyan → verde en 4 lugares (severity gauges + tablas dim) |
| #90 | `render_rnd_p3.py` | COLORS canastas Exitosa cyan → verde |
| #91 | `template_severity.py` | Exitosa bg/fg cyan → verde teal en 5 lugares |
| #92 | `asset_cr_head.html`, `asset_rnd_head.html` | Var CSS `--green` y `--green-soft` cyan → verde · `exec-mini-card.qw` border cyan → verde |
| #93 | `snippet_alertas_canasta*.html` (+ duplicados en `snippets/`) | `border-top:3px solid` cyan → verde |

### Archivos modificados
`render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `historico_module_v2.py` · `template_severity.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `snippet_alertas_canasta.html` · `snippet_alertas_canasta_rnd.html` · `snippets/snippet_alertas_canasta*.html` (duplicados)

### Documentación actualizada
`_docs/BANDAS.md` (reescrito completo con paleta D + estilo Opción D + thresholds + cyan excepciones)

### Pendientes que quedan abiertos
- ~~Decisión sobre `_docs/CHANGELOG.md` duplicado~~ (resuelto W20s4: `_governance/` eliminado, canon vive en `_docs/CHANGELOG.md`)
- Validación visual final del reporte CR W20 regenerado con badges Opción D
- Regenerar reporte RND W20 con los mismos cambios
- Datos históricos reales W14-W20 en pickle (reemplazar `_FICTICIOS`)
- Restaurar search box (tarea conocida desde sesiones huérfanas)

---

**Última actualización:** Mayo 2026 · post W20 sesión 4 · módulo histórico CR hotel+dim + Opción D badges + paleta D Exitosa verde + sin "Banda" label + target caption separado · bugs #81–#93

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 5 · Tab Críticos RND + Searchbox cobertura completa)

### Tab "Críticos" en Análisis por hotel RND (4ª óptica)

La sección Análisis por hotel RND tenía solo 3 tabs (Demanda NC · Bajo Rendimiento · Sin Conversión). Faltaba la 4ª óptica: **hoteles con `BandaNoDispo` en Crítica o Súper Crítica** (`%NoDispo > 20%`).

**Implementación:**
- `_scripts/asset_rnd_head.html`: agregado `tab-h-crit` al CSS (selectores de visibilidad de panel y tab activo).
- `_scripts/render_rnd_p2.py`:
  - Bloque `cols_crit` + `df_crit_all` filtrando `p80_hotel` por `BandaNoDispo ∈ ['Crítica','Súper Crítica']`, sorted desc por `%NoDispo`, top 50.
  - Input `<input id="tab-h-crit">` + label `<label for="tab-h-crit">Críticos</label>` agregados al bloque de tabs.
  - Panel `crit` agregado al string `panels`.
  - Subtítulo de sección: "3 ópticas analíticas" → **"4 ópticas analíticas"**.

**Resultado validado W20:** 358 hoteles del P80 (337 Crítica + 21 Súper Crítica). Top 1: Grand Hyatt Istanbul 93.22%.

### Searchbox cliente-side · cobertura completa

El searchbox ya existía como helper en `render_helpers.py` + JS auto-attach en assets head. Esta sesión cerró el último gap: el filtrado en las **canastas colapsables**.

**Cambios:**
- `_scripts/render_cr_p3.py` y `render_rnd_p3.py`:
  - Filas `panel-row` enriquecidas con `data-hist-label="{label}"`
  - Bloques hotel/dim de cada canasta: `id="canasta-{idx_str}-{hotel|dim}-{cr|rnd}"` + `searchbox_html(...)`

**Cobertura final: 18 searchboxes (9 por reporte):**
- Hero KPI cards
- Análisis por hotel
- Análisis por dimensión
- Canastas B2C/OP/CUG × hotel+dim (6)

**Comportamiento:**
- Filtrado **instantáneo** cliente-side
- **Case-insensitive y sin acentos** (NFD normalize)
- **Contador** dinámico: `"X de Y visibles"` al filtrar
- Color focus por reporte: magenta RND, violet CR
- Búsqueda solo en **primera columna** (`data-hist-label`)

### Bugs reportados verificados

Auditoría completa con playwright:

| Bug reportado | Diagnóstico |
|---|---|
| `Uncaught SyntaxError: Unexpected token 'else'` × 6 | **Falso positivo** — ya resuelto en commits previos (0 errores JS verificados) |
| Severity cards con transparencia | **Falso positivo** — paleta D con colores sólidos |
| Módulos históricos no aparecen en RND | **Falso positivo** — 8 módulos funcionando |
| Severity canastas sin paleta D | **Falso positivo** — paleta D aplicada |
| Tab Críticos faltante en Análisis por hotel RND | **REAL** — corregido |

### Archivos modificados
`_scripts/asset_rnd_head.html` · `_scripts/render_rnd_p2.py` · `_scripts/render_cr_p3.py` · `_scripts/render_rnd_p3.py` · `rates-nodispo/week-20/RatesNoDispo_Reporte_Editorial.html` · `checkrates/week-20/CheckRates_Reporte_Editorial.html`

### Commits
- `05bd9c7` · fix(rnd): agregar tab Críticos en Análisis por hotel (4ª óptica)
- `86a9bef` · feat(canastas): searchbox en Análisis por hotel + dim de cada canasta CR/RND

### Pendientes
- Datos históricos reales W14-W20 en pickle (hoy `_FICTICIOS`)
- Persistencia de filtro searchbox entre tabs (decisión pendiente)
- Validar pipeline completo con datasets W21 cuando llegue la semana

---

---

## 📝 Cambios post W20 · Mayo 2026 (sesión 6 · Histórico real W16-W20 + Limpieza legacy)

### Histórico real W16-W20 reemplaza `_FICTICIOS`

Generados pickles W16-W20 desde datasets reales y extraídos KPIs globales a `_scripts/historico_data.py`.

**Adapter para W16/W17 RND** (estructura distinta):
- W16/W17: 4 sheets (`Canasta ALL` + B2C + OP + UOP) → usar `Canasta ALL`
- W17 bug: columna `html` mal nombrada → renombrar a `CorpName`
- W18+: 1 sheet `Sheet1`

**Nuevo módulo `historico_data.py`:**
```python
HIST_DATA = {
    'cr':  {'eficacia':{...}, 'convrate':{...}},
    'rnd': {'nodispo':{...},  'ipm':{...}}
}
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']

def get_serie(reporte, metrica, scope, val_actual):
    """Devuelve serie [W16..val_actual] desde HIST_DATA + W{current}."""
```

**Cambios en módulos históricos:**
- `historico_module_v2.py` (CR) y `historico_module_rnd.py` (RND): eliminado dict `_FICTICIOS`, importan `get_serie` y `SEMANAS`
- Ventana: 8 semanas (W14-W21) → **5 semanas reales (W16-W20)**
- Cambio conceptual: `val_actual` es la semana ACTUAL del reporte, NO la próxima
- Labels: `8W` → `5W` (Máx, Mín, Prom)
- Footer eje X dinámico: `{semanas[0]}` / `{semanas[-1]}`

**Decisión: ventana de 5 semanas reales (Opción A)** — datos auditables > más puntos. Plan de evolución natural a 8 reales en ~3 semanas (W23).

### Limpieza legacy: `_scripts/{lib,snippets,templates}/` (-1522 líneas)

Eliminados archivos del pipeline anterior no usados por código vivo:
- `_scripts/lib/` (5 archivos) · `_scripts/snippets/` (4 duplicados) · `_scripts/snippet_*.html` (4 en raíz) · `_scripts/templates/mail_template.html`

Estado final `_scripts/`: **44 archivos** (antes 58).

### ZIP del proyecto Claude · `proyecto_claude_W20.zip`

Empaquetado limpio para reemplazar el proyecto en claude.ai:
- 259 KB · 51 archivos
- `_docs/` (7 .md) + `_scripts/` (43) + `destinatarios.md`
- Sin HTMLs generados, sin pickles, sin datasets, sin __pycache__

### Datos reales W16-W20 visibles

| Métrica | W16 | W17 | W18 | W19 | W20 |
|---|---|---|---|---|---|
| CR Eficacia global | 93.27% | 93.58% | 93.71% | 93.30% | 92.75% |
| CR ConvRate global | 1.29% | 1.15% | 1.02% | 1.14% | 1.19% |
| RND %NoDispo global | 3.69% | 3.63% | 2.84% | 2.31% | 2.81% |
| RND IPM global | $661 | $574 | $524 | $499 | $1.097 |

### Commits sesión 6

- `c2c1226` · feat(w20s6): histórico real W16-W20 reemplaza `_FICTICIOS`
- `abc031a` · refactor(w20s6): eliminar legacy `_scripts/{lib,snippets,templates}/`

### Pendientes

- Util `extract_hist_data.py` para automatizar la actualización del histórico
- Auditar el salto IPM W19→W20 ($499→$1097) — ¿real o ruido?
- Revocar PAT GitHub al final de las sesiones

---

**Última actualización:** Mayo 2026 · post W20 sesión 6 · Histórico real W16-W20 + ventana 5W + cleanup legacy

---

## 📝 Cambios post W20 · Mayo 2026 (sesiones 7–13 · UI/UX completo + Searchbox + Top 100)

### Resumen de sesiones

| Sesión | Commits | Cambio principal |
|---|---|---|
| s7 | `0116d4e`, `3d0eb7a` | UI minimalista inicial, autocomplete, severity |
| s8 | `41fcdef` | Rediseño completo: footer fuera, RE/Plan compactos, badge al lado |
| s9 | `0645a93` | Searchbox dentro de cards + Top 100 en DOM |
| s10 | `a1e52f7`, `7e6f2c5` | Gauge paleta D, severity paleta D, cards menos altas, canastas interactivas, banners Excel |
| s11 | `9d7cfa1` | Top 100 hotel/dim global+canastas, searchbox canastas, estilos 11px, badges paleta D |
| s12 | `5e27145` | RND tabs ancho, click canasta CR, cards más compactas, label hist muted, search limpia al cambiar tab |
| s13 | `3e5ebd2` | Cross-tab search correcto, severity RND paleta D, top 100 RND hotel/dim, canastas RND interactivas |

### Cards KPI hero — estructura final

3 secciones visuales dentro del mismo contenedor:
1. **KPI + gauge + badge/WoW**: valor 40px + badge paleta D + gauge 6px + wow_box compacto
2. **Searchbox + pestañas**: `sb-input` inline debajo de las tabs; 10 visibles / 90 sb-hidden
3. **Evolución Histórica**: módulo `historico_module_v2/rnd` reactivo

Sizing: `font-size:40px` hero / `36px` canastas · `padding:12px 16px` card.

### Searchbox — reglas de funcionamiento final

- **Solo tab activo**: `getActiveRows()` usa `getComputedStyle(panel).display !== 'none'`
- **Top 100 en DOM**: `data-row-idx` en cada fila; primeras 10 sin `sb-hidden`
- **Al cambiar tab**: el searchbox se limpia (listener `change` en radios)
- **Sin dropdown**: filtrado inline únicamente
- **Cross-tab**: el JS opera solo sobre el panel CSS-visible

### Layout tablas hotel y dimensión

```
Col izq: filas 1-5 + su header
Col der: filas 6-10 (visibles) + filas 11-100 (sb-hidden)
Al buscar → gridTemplateColumns:1fr (lista única)
```

### Severity RND — estado correcto

`render_rnd_p2.py render_severities_combinadas` usa el dict `BADGE_COLORS` con:
- `Súper Crítica: bg=#A32D2D, fg=#FCEBEB` (sólida)
- Resto: bg pastel / fg texto oscuro (conforme BANDAS.md)

### Análisis por tipo de producto

**Eliminado de PART2 CR** (`CHAN_AGR` removido de `PART2`). La función `render_channel_agrupado()` existe pero no se incluye en el ensamblado.

### Bugs pendientes para W21

| # | Descripción |
|---|---|
| P1 | Canastas RND: eje X histórico muestra "undefined" |
| P2 | Canasta CR dim: click no siempre actualiza histórico |
| P3 | Cards KPI canasta: filas de tab sin header por columna |
| P4 | `BANDA_COLORS` puede no estar disponible en `render_rnd_p3.py` |
| P5 | `extract_hist_data.py` pendiente |

### Archivos modificados en sesiones 7–13 (completo)

```
_scripts/calc_cr.py              TOP → head(100) para todos los pools
_scripts/calc_rnd.py             TOP → head(100) + corps/destinos/paises → 100
_scripts/render_cr_p1.py         Card layout 3 secciones, sb-input, font 40px, <span> accent
_scripts/render_cr_p2.py         render_top_table_cr + _render_panel + _render_dim_table actualizados
_scripts/render_cr_p3.py         tab_panel_hotel/dim 2 cols, searchbox, listener hist, render_historico_seccion_cr local
_scripts/render_rnd_p1.py        Card layout 3 secciones, sb-input, font 40px
_scripts/render_rnd_p2.py        render_top_table + _render_panel + _render_dim_table_rnd + severity paleta D
_scripts/render_rnd_p3.py        tab_panel_hotel 2 cols+badge+corp, listener hist, render_historico_seccion_rnd local
_scripts/historico_module_v2.py  Label "Global" → var(--ink-muted)
_scripts/historico_module_rnd.py Label "Global" → var(--ink-muted)
_scripts/render_helpers.py       gauge_5levels: height 6px, opacity 1, sin labels, sin Conversión #8A8377
_scripts/template_resumen.py     <strong> → <span> en titulo de finding
_scripts/template_severity.py    render_severity_row paleta D canónica
_scripts/asset_cr_head.html      display:block tabs activos, getActiveRows, clear-on-change, kpi-card box-sizing
_scripts/asset_rnd_head.html     display:block tabs activos (era grid 1fr 1fr), getActiveRows, idem
```

---

**Última actualización:** Mayo 2026 · post W20 sesiones 7-13 · commits s7→s13 · UI/UX + Searchbox + Histórico completo


---

## 📝 Cambios post W20 · Mayo 2026 (sesiones 14-15 · Fixes visuales batch 2)

### Badges en listas KPI — regla definitiva
- **SÍ badge**: Destino · Corp · País · Channel · Canasta — en KPI cards globales y canastas
- **NO badge**: Hotel — suprimido en `render_cr_p1/p3.py` y `render_rnd_p1/p3.py` (flag `t_key == 'hotel'` o `parse_hotel`)
- Badge en **análisis por dimensión** → tab Channel: `render_chan_table` en `render_bloque_dimensiones_cr` incluye `mini_badge(BandaEficacia)` al lado del nombre
- `_mini_badge` y `mini_badge` centralizados en `render_helpers.py` (accesibles vía `from render_helpers import *`)

### Paleta D — Aceptable naranja definitivo
- `gauge_5levels`: Aceptable `#5C469C` (violet incorrecto) → `#F59E0B` (naranja sólido)
- `historico_module_v2.py`: Aceptable violet → `bg:#FEF3C7 fg:#92400E` (naranja pastel)
- Revisar: `#D4A878` (ocre) → `#F59E0B` (naranja sólido) ya desde sesión 13

### Opción C searchbox — especificación definitiva
- `.sb-inline-wrap`: `position:relative` + `border-left:1px solid var(--rule)` + padding
- `.sb-inline`: `width:120px` + `font-size:10px` + transición en `:focus`
- `.sb-clear-btn`: `position:absolute;right:4px;top:50%` — visible solo cuando `input.value` no vacío
- `buildLabels()`: construye labels desde `getActiveRows(false)` — solo tab activo, sin cross-card
- Implementado en: análisis por hotel (4 tabs), análisis por dimensión (3 tabs), KPI cards (inline)

### Canastas en KPI cards globales
- `panel_html = col1 + col2 + rest` para `t_key in ('canasta', 'channel')` — ya no usa el vacío `rows_html`
- Las 3 canastas (B2C · CUG · B2B OP) ahora visibles en el tab Canasta de ambas cards globales

### Análisis por dimensión · tab Channel
- `render_chan_table`: badge de banda inline al lado del nombre del canal
- Badge se calcula como `r.get('BandaEficacia','') or banda_eficacia(ef_val)`

### Archivos modificados (sesiones 14-15)
`render_helpers.py` · `historico_module_v2.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

**Última actualización:** 23 Mayo 2026 · post W20 s14-15 · badges hotel suprimido · Aceptable naranja · Opción C searchbox definitivo · mini_badge centralizado
---

## 📝 Cambios post W20 · Mayo 2026 (sesión 15+ · Searchbox Prop A+D + wow_pill V1)

### Sistema de searchbox — 3 modos JS (migración completa)

Rediseño del sistema de búsqueda inline. Antes: un único `sb-inline-wrap` compartido entre todos los tabs de un bloque → filtraba cross-tab. Ahora: un searchbox **por contexto** con lógica de aislamiento.

#### Nuevas funciones en `render_helpers.py`

| Función | Uso |
|---|---|
| `wow_pill_html(delta, unit, prefix_pos, prefix_neg)` | Pill verde/rojo/gris border-radius:20px |
| `searchbox_pill_html(input_id, accent_color, placeholder, count_id)` | Pill en tabs-row de KPI cards (Prop A) |
| `searchbox_header_html(input_id, accent_color, placeholder, th_id)` | Header integrado en col1 de tabla (Prop D) |

#### Regla definitiva: cero duplicación

- **KPI cards (hero + canastas)** → `searchbox_pill_html()` al final de `tabs_labels`
- **Tablas hotel + dim (global + canastas)** → `searchbox_header_html()` como primera columna del `<div>` header
- **`sb-inline-wrap` en `tabs-row` de bloques** → **eliminados** (eran el único searchbox antes)

#### wow_pill V1 en KPI-top

```python
# En kpi_card_canasta y cards hero, debajo del badge:
_wow_pp = wow_pill_html(delta, unit='pp')          # CR: Eficacia / ConvRate
_wow_rnd = wow_pill_html(-delta, unit='pp',         # RND NoDispo: invertida
                          prefix_pos='↓', prefix_neg='↑')
```

La pill aparece en `display:flex;align-items:flex-end` junto al valor grande y el badge, con caption "vs sem. ant." delante.

#### JS Engine W21 en `asset_*_head.html`

Tres funciones de auto-attach:
- `attachPill()` — para `[data-sb-pill]`: filtra panel activo, reset al cambiar tab
- `attachTable()` — para `[data-sb-table]`: filtra `[data-lbl]` en bloque padre
- `attachSearchbox()` — modo legado `[data-sb-scope]`: sin cambios de interfaz, + empty state + fix A2

**fix A1:** empty state `"Sin resultados para «query»"` cuando ninguna fila coincide.  
**fix A2:** al cambiar tab, input se vacía y grid resetea a `1fr 1fr`.

#### data-lbl en filas de tabla

Las filas de tablas hotel ahora llevan `data-lbl="hotel corp"` y las de dim `data-lbl="nombre"` para que `attachTable` (Prop D) filtre por ese atributo.

### Commits de esta sesión
- `b121f55` · feat(W20s): searchbox Prop A+D + wow_pill V1 · CR+RND global+canastas
- `97e9d07` · regen(W20): reportes editoriales CR+RND con searchbox Prop A+D · wow_pill V1

### Archivos modificados
`render_helpers.py` · `asset_cr_head.html` · `asset_rnd_head.html` · `render_cr_p1.py` · `render_rnd_p1.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_cr_p3.py` · `render_rnd_p3.py`

---

**Última actualización:** Mayo 2026 · post W20 sesión 15+ · Searchbox Prop A+D + wow_pill V1 · 3 modos JS engine


---

## 📝 Cambios post W20 · Mayo 2026 (sesión fixes colores + UI · commits b63591f–4289f22)

### Paleta canónica definitiva — ÚNICA FUENTE: `BANDA_COLORS` en `render_helpers.py`

| Banda | bg | fg | barra severidad |
|---|---|---|---|
| Exitosa | `#E1F5EE` | `#1A6B4A` | `#1A6B4A` |
| Aceptable | `#FEF9C3` | `#713F12` | `#FCD34D` |
| Revisar | `#FED7AA` | `#C2410C` | `#F97316` |
| Crítica | `#FCE4F1` | `#99162B` | `#C0392B` |
| Súper Crítica | `#161616` | `#FFFFFF` | `#DC2626` |
| Sin Conversión | `#F2EEE6` | `#5F5E5A` | `#8A8377` |

**`#5C469C`** es el accent de CR (subheads, tabs, alert cards) — NO es color de banda.  
**`#F97316`** es la barra de Revisar — diferente del fg `#C2410C`.  
**Súper Crítica** = negro sólido en todos los contextos (badge, barra, histórico, canastas).

### Bugs corregidos

- **Autocomplete (bug raíz):** `attachPill` tenía código huérfano del `showEmpty` que cerraba la función antes de `var dropdown`. `buildDD` quedaba fuera del scope → dropdown nunca aparecía. Reescritura limpia en `asset_cr_head.html` y `asset_rnd_head.html`.
- **`attachTable` crash:** `dropdown` declarado después del `clearBtn.addEventListener` → `dropdown=undefined`. Fix: declarar antes.
- **Layout horizontal análisis por hotel:** `attachSearchbox` sobreescribía `gridTemplateColumns:1fr 1fr` en todos los `.kpi-tab-rows`. Línea eliminada.
- **Layout horizontal análisis por dimensión:** wrappers `<div>` sin clase tomaban `display:flex` del selector `.tab-panel > div:not(...)`. Fix: `class="tbl-wrap"` + `.tbl-wrap{display:block}` + `:not(.tbl-wrap)` en el selector.
- **Barra de progreso Revisar:** `#D4A878` (ocre) → `#F97316` (naranja) en `render_cr_p2` y `render_rnd_p2`.
- **Badge Súper Crítica rosa:** `#FECACA`/`#7F1D1D` → `#161616`/`#FFFFFF` en 8 archivos.
- **Badge NoDispo hotel (RND):** exclusión `if t_key == 'hotel'` eliminada.
- **Resumen Ejecutivo sin bold:** `font-weight:600` en títulos de `render_finding`.
- **Análisis por dimensión 2 cols:** `render_top_dimension` ahora pasa `df_all` (10 filas) con `rows-more` en filas 5-9.

### Regla de workflow para cambios de color

Cuando se cambia un color, siempre hacer `grep -r '#COLOR'` en **todos** los archivos antes de asumir que está corregido. Los colores están hardcodeados en múltiples archivos independientes. Verificar siempre con audit post-build antes de pushear.

### Pendientes para siguiente sesión

- Colores en canastas CR y RND (verificar visualmente)
- Módulo histórico: Súper Crítica negro en canvas/sparkline
- `extract_hist_data.py` para automatizar historial W21+
- Verificar "Ver 5 más" en todas las tabs

**Última actualización:** Mayo 2026 · post W20 sesión fixes · bugs #48–#59 · paleta canónica definitiva



---

## 📝 Cambios post W20 · Mayo 2026 (sesión final · Fixes UI/UX + Pipeline W20 completo)

### Pipeline W20 con WoW real
- Primera ejecución con datasets W19 reales (antes W19 era vacío)
- WoW CR: Eficacia 93,30%→92,75% (−0,55pp) · ConvRate 1,14%→1,19% (+0,05pp)
- WoW RND: %NoDispo 2,33%→2,74% (+0,41pp) · IPM $499→$1.217 (+144%)

### Bugs CSS críticos resueltos

**Bug #74 (a64115d4):** `asset_cr_head.html` tenía DOS instancias de la regla legacy de color de spans. La segunda tenía `color:#5C469C !important` → ganaba sobre cualquier inline style → todos los valores en tabs de cards KPI aparecían en violeta. Eliminada.

**Bug #75 (049b6fb6):** `searchbox_header_html` generaba el `sb-pill` directo como hijo de celda de grid (`1fr`) → el pill se estiraba al 100% del ancho. Fix: envolver en `<div style="display:flex;align-items:center;">`.

### Cambios de diseño

- **Súper Crítica**: negro sólido (`#161616`/`#FFFFFF`) → gris cálido (`#EDECEC`/`#4A3F3F`) — menos contraste, más armónico con otras bandas pastel
- **Badge Severity como columna**: movido de inline-junto-al-nombre a columna separada en todas las tablas de análisis hotel y dimensión (CR y RND)
- **Headers de columna en tabs KPI**: filas `Severity | Eficacia | WoW` / `Severity | %NoDispo | WoW` / `Severity | IPM | WoW` agregadas sobre las filas de datos
- **Conv Rate 68px**: columna expandida de 54px a 68px para que el label entre en una línea
- **Headers RND corregidos**: card izquierda (NoDispo) → `%NoDispo`, card derecha (IPM) → `IPM` (estaban al revés)
- **Top 50 → Top 100**: todos los callouts de descarga Excel
- **RE sin bold**: `font-weight:400` en div card del Resumen Ejecutivo cancela herencia del header
- **Separación Severity/RE en RND**: `margin-top:48px` en `<section id="severity-combinada">`

### Estado de archivos del proyecto Claude
ZIP: `ProyectoClaude_PRICE_W20.zip` · 280 KB · 43 archivos · generado 24/05/2026

---

**Última actualización:** 24 Mayo 2026 · Pipeline W20 completo · WoW real · Fixes UI/UX batch final

---

## 📝 Cambios post W20 · Mayo 2026 (Sprint A + B + Fixes globales vs canastas)

### Sprint A · Fixes rápidos

| Bug | Archivo | Descripción |
|---|---|---|
| A | `render_cr_p3.py`, `render_rnd_p3.py` | Headers de columna faltaban en tabs KPI de canastas → `tab_rows_canasta` ahora genera `Severity / Métrica / WoW` |
| B | `render_cr_p1.py` | "vs sem. ant." faltaba en hero global CR → agregado a ambas cards (Eficacia + ConvRate) |
| C | `render_cr_p3.py` | `wow_pill_html` parseaba `wow_str` con string manipulation frágil → `wow_delta` (float) pasado directamente |
| I | confirmado resuelto | Eje X "undefined" en histórico RND canastas → era bug de versión anterior, ya resuelto desde sesión 6 |
| J | `render_cr_p3.py`, `render_rnd_p3.py` | Regex listener `render_historico_seccion_cr/rnd` no matcheaba `canasta-{idx}-hotel-cr` → regex sin guión final |

### Sprint B · Centralización de helpers

**Nuevas funciones en `render_helpers.py`:**

```python
tab_column_header(cols, widths)     # Header columnas para tabs KPI — reemplaza _tab_hdr hardcodeados
make_wow_pill_row(wow_v, ...)       # Pill WoW filas de tabs — unifica CR (inline) con RND (CSS class)
wow_box(..., compact=False/True)    # compact=True = canastas; elimina wow_box_canasta() local
```

**Regla:** cualquier cambio visual en KPI cards → editar solo `render_helpers.py`.

### Fix searchbox canastas — scope aislado

Canastas CR migradas de CSS radio tabs a JS tabs aislados:
- Panels: `class="tab-panel"` → `class="tp-{card_id}"`  
- `getActivePanel()` en `asset_cr_head.html` y `asset_rnd_head.html`: busca primero `.tp-*` para aislar scope del searchbox por canasta

### Fix layout KPI cards — global vs canastas

Todas las cards KPI ahora tienen estructura idéntica:
- `font-size: 40px` (era 36px en canastas)
- `align-items: flex-start` (era `center` en canastas)
- `gap: 14px` (era `12px` en canastas)
- Badge a la derecha del valor, "vs sem. ant." debajo del número (igual que global)
- "vs sem. ant." agregado a global RND (faltaba)

### Fix Análisis por Hotel y Dimensión — canastas

**Análisis por Hotel:**
- Columna `Severity` (badge paleta D) como columna separada en CR y RND canastas
- RND: columnas expandidas para incluir WoW NoDispo + WoW IPM

**Análisis por Dimensión:**
- Columna `Severity` separada en CR y RND canastas
- Patrón de visibilidad: `5 visible + 5 rows-more + 90 sb-hidden` (igual que global)
- Botón "Ver 5 más" agregado

### Regla de mantenimiento global vs canastas

| Tipo | Tocar |
|---|---|
| Visual puro | Solo `render_helpers.py` |
| Datos (nueva columna) | `calc_*.py` + `render_*_p1.py` + `render_*_p3.py` |
| Estructura tabs | `asset_*_head.html` + p1 + p3 |
| Módulo histórico | `historico_module_v2/rnd.py` + verificar IDs |

### Archivos modificados
`render_helpers.py` · `render_cr_p1.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p3.py` · `asset_cr_head.html` · `asset_rnd_head.html`

---

**Última actualización:** Mayo 2026 · post W20 · Sprint A+B + fixes global vs canastas · commits 8e934bdf · b3daea6a · e61c87ce

---

## 🤖 Proceso de commit automático (W21+)

### Flujo estándar tras cualquier cambio

**1. Actualizar docs** (antes de commitear):
```bash
# Para pipeline completo:
python3 update_docs.py --week 21 --periodo "18–24 may 2026" --tipo pipeline

# Para fix puntual:
python3 update_docs.py --week 21 --tipo fix --descripcion "Fix badges canastas"
```

**2. Commit + ZIP**:
```bash
python3 github_commit.py --week 21 --periodo "18–24 may 2026" --token ghp_xxx
```

**O en un solo comando** (si hay `github_token` en el YAML):
```bash
python3 run_pipeline.py WEEK_CONFIG_W21.yml   # Pasos 7+8 se ejecutan solos
```

### Lo que hace cada script

**`update_docs.py`** — actualiza los 3 documentos canónicos:
- `CHANGELOG.md`: bloque con tabla KPIs reales (del pickle), outputs generados, commits
- `README.md`: sección "Última semana publicada" con KPIs + URLs
- `PROMPT_MAESTRO_v3.md`: bloque de cambios de la semana

**`github_commit.py`** — hace el commit vía API GitHub:
- Combina: contenido del `Price_WNN.zip` + scripts en `_scripts/` + docs en `_docs/`
- Genera `ProyectoClaude_PRICE_WNN.zip` con los archivos del proyecto Claude

### Invariante: siempre docs antes de commit

> Nunca commitear sin haber corrido `update_docs.py` primero.  
> El paso 7 del pipeline lo garantiza automáticamente.

---

## 📝 Pipeline W20 · Mayo 2026 (ejecutado 24/05/2026)

**Período:** 11–17 may 2026  
**Tipo:** Pipeline completo (7 pasos: calc → render → assemble → excel → mail → hub → docs)

- RND: NoDispo 2,81% (+0,33pp) · IPM $1.194 (+81,7%)
- CR: Eficacia 92,75% (-0,71pp) · ConvRate 1,19% (+0,03pp)

### Archivos modificados
`rnd_w20_data.pkl` · `cr_w20_data.pkl` · `RatesNoDispo_Reporte_Editorial.html` · `CheckRates_Reporte_Editorial.html` · 8 Excels · `Mail_W20.html` · `index.html`

---

**Última actualización:** Mayo 2026 · Pipeline W20 · 11–17 may 2026

---

## 📝 Cambios · 24 May 2026 · W20

**Descripción:** Fix batch UI: ConvRate sin bold, WoW ConvRate dim canastas CR, Severity left-align, parse_hotel=False, Channel clickeable CR, Tráfico col RND hotel canastas, IPM badge violeta alertas RND

### Archivos modificados
_(ver CHANGELOG para detalle)_

---

**Última actualización:** May 2026 · Fix batch UI: ConvRate sin bold, WoW ConvRate dim canastas C

---

## 📝 Cambios · 24 May 2026 · W20

**Descripción:** Batch fixes: undefined histórico canal, HotelBeds rename, channel split canastas, hotel IDs, bold análisis, colores dim negro

### Archivos modificados
_(ver CHANGELOG para detalle)_

---

---

## 📝 Cambios · 24 May 2026 · Channel split canónico CR

**Descripción:** Channel split CR (global + canastas) ahora itera sobre catálogo fijo en vez de filtrar por `.isin()`. Canales sin datos esa semana aparecen atenuados con `—` en vez de desaparecer.

### Problema
`.isin(LISTA)` sobre el DataFrame disponible → si Travelclick, Omnibees u otro canal no tenía tráfico esa semana, desaparecía del tab Channel sin aviso visual.

### Solución
| Función | Archivo | Descripción |
|---|---|---|
| `_sorted_canonical()` + `_lookup_chan()` | `render_cr_p1.py` | Card Eficacia global · HotelBeds con startswith |
| `_sorted_canonical_cv()` | `render_cr_p1.py` | Card ConvRate global |
| `_build_chan_df()` | `render_cr_p2.py` | Análisis por dimensión tab Channel · dummy rows NaN · kicker "activos" |
| `_sorted_c()` + guard `_val_is_nan` | `render_cr_p3.py` | Canastas · `tab_rows_canasta` |

### Comportamiento de filas sin datos
- `opacity:.45` · `pointer-events:none` · sin badge · todos los valores `—`
- Se renderizan al final de cada grupo (PP o TP), después de los que tienen datos

### Archivos modificados
`render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py`



---

## 📝 Cambios post W21 · Mayo 2026 (sesión W21 · Migración a HTML tables + cleanup visual)

### Migración CSS grid → HTML table en tablas grandes
Las tablas de "Análisis por hotel" y "Análisis por dimensión" (RND + CR) reescritas usando HTML `<table>` con `table-layout:fixed` + `<colgroup>` con anchos explícitos por columna. Motivo: CSS grid con `1fr` + columnas fijas dejaba espacio inconsistente entre columnas en distintos viewports y la columna del nombre acaparaba todo el sobrante.

**Patrón nuevo:**
- `<table style="width:100%;border-collapse:collapse;table-layout:fixed;">`
- `<colgroup>` con `<col style="width:800px">` para nombre + cols de datos fijas
- Truco: width:800px en nombre hace que esa columna absorba casi todo el espacio sobrante (proporcionalmente) en lugar de distribuirse entre cols de datos
- `<thead>` + `<tbody>` con `<tr>` y `<td>` reales
- Padding: 12px en bordes (left primera col, right última col), 8px en intermedias

**Funciones reescritas:**
- `render_top_table()` en `render_rnd_p2.py`
- `_render_dim_table_rnd()` en `render_rnd_p2.py`
- `render_top_table_cr()` en `render_cr_p2.py`
- `_render_dim_table()` en `render_cr_p2.py`

### Anchos de columnas calibrados con Geist 7px-11px
Test diagnóstico (`test_geist.html`) confirmó anchos reales:
- SÚPER CRÍTICA: 62px → cell 80px ✅
- ACEPTABLE: 48px → cell 80px ✅
- Pill WoW `↑11,02`: ~50px → cell 56px ✅

### Canastas RND/CR · Grids reducidos
Los grids internos de canastas (panel_inner_rnd, tab_panel_hotel, etc) reducidos para evitar overflow en contenedor de 2 columnas (~570px cada uno):
- RND hotel/dim canasta: `1fr 70px 60px 50px 32px 50px 32px`
- CR hotel/dim canasta: `minmax(0,1fr) 70px 56px 48px 52px 30px 52px 30px`
- Agregado `width:100%` a todos los grids de canastas

### `.tbl-wrap` overflow-x:hidden
Cambio en `asset_shared_head.html`:
```css
.tbl-wrap{display:block;max-width:100%;overflow-x:hidden;box-sizing:border-box;}
```
Recorta cualquier contenido que desborde en lugar de mostrar scrollbar horizontal — soluciona el scrollbar visible que aparecía bajo las canastas.

### Kickers removidos de hotel y dim (RND + CR)
Los `<p class="tab-kicker">` que precedían las tablas en cada tab panel fueron removidos. Quedaba texto descriptivo redundante encima de cada tabla. Las funciones siguen calculando las variables `kicker_*` para potencial uso futuro pero ya no se renderizan.

**Tabs afectados:**
- RND hotel: crit, dnc, br, sc
- RND dim: corp, dest, pais
- CR hotel: crit, br, sc, mcv
- CR dim: corp, dest, chan

### Headers WoW unificados en canastas CR
"WoW CV" y "WoW Ef" → "WoW" (4 instancias en `render_cr_p3.py`).

### Pestañas CR alineadas
`<div class="tabs-row">` en hotel CR ahora con `style="align-items:flex-end;"` para que coincida con el patrón RND.

### Ver más button reposicionado
- Antes: `margin-top:6px;margin-left:12px`
- Ahora: `margin-top:12px;margin-left:0`
Aplicado en todos los renders (RND p2/p3, CR p2/p3).

### Bugs identificados durante la sesión
- **CSS regla heredada:** `#tab-nd-pais:checked ~ .tab-panels .tab-panel[data-tab="pais"] {display:grid;grid-template-columns:1fr 1fr}` hacía que los tab-panels activos fueran grids de 2 columnas → KPI cards y tablas quedaban en 50% del ancho. Fix: `display:block` (cubierto en sesiones previas).
- **Geist vs system-ui:** El test diagnóstico inicial mostraba que sin Geist las tablas se veían bien. Geist tiene métricas distintas — calibración de columnas debe hacerse con Geist cargado.

### Archivos modificados
`render_rnd_p2.py` · `render_rnd_p3.py` · `render_cr_p2.py` · `render_cr_p3.py` · `asset_shared_head.html`

**Pipeline W21 ejecutado completo:** reportes HTML, 8 Excels, Mail_W21.html, index.html hub, Price_W21.zip (19MB), ProyectoClaude_PRICE_W21.zip (43 archivos planos).

---

## Sesión Post-W21 · Mayo 2026 · Visual polish: sev-badge, toggle, wow-pill, colwidths

### Contexto
Sesión de correcciones visuales post-pipeline W21, sin cambio de datos. Todos los cambios son de presentación HTML/CSS/JS. No se ejecutó pipeline completo — se hizo render parcial + validación visual iterativa.

### .sev-badge · Clase CSS unificada
Se creó la clase `.sev-badge` en `asset_shared_head.html` y se aplicó a **todas** las severity badges en todos los renders (4582 instancias RND + 2891 CR). Reemplaza styles inline largos y heterogéneos.

Especificación final:
- `font-size:7px` (antes variaba entre 7-9px por archivo)
- Sin `min-width` — evita truncado de "SÚPER CRÍTICA" en cols de 60px
- `outline:1px solid rgba(0,0,0,0.15)` — visibilidad contra fondo crema sin alterar box-sizing
- `letter-spacing:.02em` para que "SÚPER CRÍTICA" quepa en el espacio disponible

### Migración wow-pill · margin-left removido
El CSS de `.wow-pill` tenía `margin-left:4px` que causaba un "guion fantasma" visible al lado de los pills en las tablas. Removido.

`_fmt_wow_cv()` en `render_cr_p2.py` convertido a **inline style completo** (no depende de clase CSS) para independencia de cache del browser.

### Toggle "Ver más / Ver menos" · Bug fix
El handler JS buscaba `.rows-more` para ocultar filas en el segundo click (colapsar). Como la clase se remueve en el primer expand, el segundo click no encontraba las filas y no colapsaba. Fix: selector cambiado a `[data-row-idx]` filtrando índices 5-9, que es estable entre toggles.

### wow_box · outer_bg unificado
`wow_box(compact=True)` para canastas usaba `outer_bg:var(--paper)` que se mimetizaba con el fondo de `.canasta-content` (también `var(--paper)`), haciendo invisibles las celdas W(N-1) y W(N). Cambiado a `var(--paper-soft)` para ambos modos (compact y global), garantizando contraste.

### Colwidths calibrados
**RND hotel/dim (7 cols):** sin cambio  
**CR dim 8-cols:** `[800, 60, 56, 48, 50, 52, 50, 52]` = 1168px  
— WoW cols aumentadas de 32px → 52px para mostrar pills con 2 decimales sin truncado  
**CR dim 7-cols:** `[800, 64, 60, 50, 58, 78, 58]` = 1168px  
**CR dim 6-cols:** `[800, 70, 72, 60, 80, 86]` = 1168px  

**Canastas RND dim:** grid `1fr 60px 54px 48px 48px 52px 48px`  
**Canastas RND hotel:** grid `1fr 60px 48px 48px 52px 48px`  
**Canastas CR hotel:** grid `1fr 60px 50px 48px 52px 48px`  

### Severity header alineado al centro
TH "SEVERITY" en todas las tablas hotel y dim (CR + RND) cambiado a `text-align:center` con padding simétrico (`pl=0, pr=0`) para que el texto quede centrado sobre los badges centrados. Badge TD también `text-align:center`.

### Padding última columna: 20px → 12px
El padding-right:20px en la última celda (WoW Eficacia/IPM) comprimía el espacio del pill. Reducido a 12px en `render_cr_p2.py` y `render_rnd_p2.py`.

### Súper Crítica · color definitivo
Después de iteraciones: `bg:#E8E6E3, fg:#2D2828` (gris oscuro sobre gris claro). El outline del sev-badge garantiza la separación visual contra el papel crema. **No se cambió a rojo** — mantiene semántica de la Paleta D.

### Regla de workflow establecida
No correr pipeline completo en cada iteración de fix visual. Flujo correcto:
1. Fix en script → render parcial → assemble → validación visual → (si OK) pipeline completo.

### Archivos modificados
`asset_shared_head.html` · `render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py`

---

## Sesión Post-W21 (segunda parte) · Mayo 2026 · WoW NaN en pickles + CSS tabs fondo

### Bug sistémico: WoW NaN en TOP[] y CANASTA[]

**Causa raíz:** `g_hotel_w17` en `calc_rnd.py` usaba `agg_hotel()` que agrupa por `Hotel + Corp + País + Destino`, generando 234 hoteles duplicados. Al hacer `p80_hotel.merge(g_hotel_w17, on='Hotel')`, los duplicados producían joins incorrectos → `NoDispo_WoW_pp` quedaba NaN para los sub-dfs derivados.

El problema afectaba **tres niveles**:
1. `TOP['demanda_nc']`, `TOP['bajo_rend']`, `TOP['sin_conv']` — **calc_rnd.py**
2. `TOP['criticos']`, `TOP['bajo_rend']` — **calc_cr.py** (construidos antes de TAB_EF/TAB_CV)
3. Todos los sub-dfs de `CANASTA[]` — ambos calcs (construidos antes del enriquecimiento)

**Fix permanente (3 commits):**
- `calc_rnd.py`: `g_hotel_w17` ahora agrega solo por Hotel (sin duplicados) + bloque post-construcción que enriquece `TOP[]` y `CANASTA[]` con WoW desde `p80_hotel`
- `calc_cr.py`: bloque post-construcción que enriquece `TOP[]` con WoW desde `TAB_EF['hotel']` + `TAB_CV['hotel']`, y `CANASTA[]` con el mismo lookup

**Patrón de enriquecimiento (canon para W22+):**
```python
# Al final de cada calc_*.py, antes del pickle.dump:
_wow_lkp = p80_hotel[['Hotel','NoDispo_WoW_pp','IPM_WoW_pp']].drop_duplicates('Hotel')
for _ck, _cd in CANASTA_DATA.items():
    for _sk, _df in _cd.items():
        if 'Hotel' in _df.columns and _df['NoDispo_WoW_pp'].notna().sum() == 0:
            _df2 = _df.drop(columns=[...]).merge(_wow_lkp, on='Hotel', how='left')
            _cd[_sk] = _df2
```

### Bug CSS: fondo oscuro en tabs activos RND

**Causa raíz:** En `asset_shared_head.html`, los selectores de tabs activos (Críticos, DNC, BR, SC, Corp, Destino, País) terminaban en coma **sin cerrar el bloque** `{display:block;}`. El CSS concatenaba esos selectores con las propiedades de `.canasta-block` que seguía inmediatamente, haciendo que los tab-panels activos heredaran `background:var(--paper-soft)` → fondo más oscuro visible en pantalla.

**Fix:** cada grupo de selectores ahora cierra correctamente:
```css
.tabs-block #tab-h-crit:checked ~ .tab-panels .tab-panel[data-tab="crit"],
.tabs-block #tab-h-dnc:checked ~ .tab-panels .tab-panel[data-tab="dnc"],
.tabs-block #tab-h-br:checked ~ .tab-panels .tab-panel[data-tab="br"],
.tabs-block #tab-h-sc:checked ~ .tab-panels .tab-panel[data-tab="sc"]{display:block;}
```

### Proceso de trabajo post-sesión

Se definió el flujo completo de trabajo semanal documentado en `README_QUICK.md`. Ver sección correspondiente.

### Commits de esta sesión
- `ae26570a` — Fix WoW RND: TOP[] enriquecido desde p80_hotel
- `09249569` — Fix WoW CR: TOP[] enriquecido desde TAB_EF/TAB_CV
- `2259c8c5` — Fix WoW canastas: CANASTA[] sub-dfs enriquecidos
- `4fc00936` — Fix CSS: tabs activos `{display:block;}` en shared_head

### Archivos modificados
`calc_rnd.py` · `calc_cr.py` · `asset_shared_head.html`

---

## Sesión Post-W21 (tercera parte) · Mayo 2026 · Correcciones Excel

### Problemas identificados y corregidos

**1. Top 50 → Top 100 en hojas de hotel RND canastas**
Los sub-dfs `bajo_rend` y `sin_conv` del pickle solo tenían 50 rows. Las hojas de Excel derivaban de esas claves en vez de usar `p80_hotel` directamente. Fix: construir el top 100 desde `canasta_data['p80_hotel']` filtrando y ordenando localmente.

**2. Top 10 → Top 100 en hojas de hotel CR canastas**
Las claves `critic`, `bajo`, `sin_conv`, `menor_cv` del pickle CANASTA CR tenían 10 rows (construidas con `head(10)` para el reporte editorial HTML). Fix: derivar desde `canasta_data['p80']` con el mismo criterio de filtro y orden.

**3. Orden corregido**
- RND hojas hotel: `%NoDispo DESC` (mayor a menor) en todas las tabs
- RND Sin Conversión: `Trafico DESC`
- CR hojas hotel: `Eficacia ASC` (menor = peor primero) en todas las tabs

**4. Formato % corregido en canastas**
Las tablas de canasta no tenían `num_formats` → los valores aparecían como float crudo (0.4944...). Agregado `num_formats={'%NoDispo':'0.00%', 'Eficacia':'0.00%', 'ConvRate':'0.00%', 'IPM':'$#,##0'}` en todas las `add_table()` calls.

**5. Nombre hotel CR sin ID**
Los hoteles en el pickle CR tienen prefijo `(100091) - Hotel Name`. La función `clean_hotel_name()` (ya existente en `excel_cr.py`) se extendió a `excel_cr_canastas.py` aplicándose después de derivar los dfs desde `p80`.

### Archivos modificados
`excel_rnd.py` · `excel_rnd_canastas.py` · `excel_cr.py` · `excel_cr_canastas.py`

---

## Sesión Post-W21 (cuarta parte) · Mayo 2026 · Channel y orden dims en Excels CR

### Bug: Channel = '—' en todas las pestañas de hotel

**Causa raíz (doble):**
1. `hotel_channel_map` tiene claves con ID `"(100091) - Hotel Name"` pero `p80_hotel['Hotel']` ya fue limpiado a `"Hotel Name"`. El `.map(hotel_channel_map)` nunca matcheaba → `'—'` siempre.
2. En `excel_cr_canastas.py`, la limpieza se hacía dentro de un loop `for _df_name in [critic, bajo, ...]` sin `.copy()` → las asignaciones no persistían en el DataFrame original.

**Fix:**
- Construir `_hcm_clean = {clean_hotel_name(k): v for k, v in hotel_channel_map.items()}` como lookup global antes de cualquier uso.
- Reemplazar el loop por función `_enrich(df)` que hace `.copy()` explícito, limpia el nombre, inserta Channel en posición 3 y agrega Rk.

```python
def _enrich(df):
    if df.empty or 'Hotel' not in df.columns: return df
    df = df.copy()
    df['Hotel'] = df['Hotel'].apply(clean_hotel_name)
    if _hcm_clean and 'Channel' not in df.columns:
        df.insert(min(3, len(df.columns)), 'Channel', df['Hotel'].map(_hcm_clean).fillna('—'))
    if 'Rk' not in df.columns:
        df.insert(0, 'Rk', range(1, len(df)+1))
    return df
```

### Bug: orden dims con None primero en vez de último

`sort_values('Eficacia', ascending=True)` sin `na_position` pone los `None/NaN` primero. Fix: agregar `na_position='last'` en todos los sort de dims (Corp, Destino, Channel) en `excel_cr.py` y `excel_cr_canastas.py`.

### Archivos modificados
`excel_cr.py` · `excel_cr_canastas.py`

---

## Sesión Post-W21 (quinta parte) · Mayo 2026 · Histórico W17-W21

### Bug: eje X del histórico mostraba W20 en vez de W21

**Causa raíz:** `historico_data.py` tenía `SEMANAS = ['W16','W17','W18','W19','W20']` con arrays de 4 valores (W16-W19). El render agrega `val_actual` como 5° valor, que ahora es W21, pero el eje X seguía etiquetando el último como "W20".

**Fix:** actualizar `historico_data.py`:
- `SEMANAS`: `['W16','W17','W18','W19','W20']` → `['W17','W18','W19','W20','W21']`
- Arrays: descartar W16, agregar W20 (extraído de `df18` del pickle W21)
- W21 sigue siendo dinámico — se agrega en runtime desde el pickle vigente

**Valores W20 incorporados (extraídos de df18 del pickle W21):**

| Scope | RND %NoDispo | RND IPM | CR Eficacia | CR ConvRate |
|---|---|---|---|---|
| global | 2.59% | $677 | 93.34% | 1.63% |
| op | 2.24% | $688 | 93.96% | 1.59% |
| cug | 2.82% | $787 | 92.28% | 2.90% |
| b2c | 3.31% | $248 | 92.01% | 0.39% |

**Regla para W22+:** agregar el valor W21 a cada scope en `HIST_DATA`, descartar W17, actualizar `SEMANAS` al nuevo rango. El 5° valor siempre viene del pickle vigente (dinámico).

### Archivos modificados
`historico_data.py`

---

## Pipeline W21 · Mayo 2026 · 26 May 2026

**Período:** 18–24 may 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`RatesNoDispo_Reporte_Editorial.html` · `CheckRates_Reporte_Editorial.html` · 8 Excels · `Mail_W21.html` · `index.html` · `Price_W21.zip`

---

## Fix · W21 · 26 May 2026

**Descripción:** update_docs.py reescrito + hook en github_commit.py → docs auto-actualizados en cada commit

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Cleanup: renders migrados a historico_module unificado, eliminar módulos obsoletos

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Cleanup: EXCLUDE list en ZIP del proyecto, historico_module unificado

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Docs: PROMPT_CORE + CHANGELOG_NIVEL3 actualizados con cleanup historico_module

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Cleanup final: sincronización GitHub ↔ Proyecto Claude · repo limpio

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix histórico: eje X muestra las 5 semanas W17-W21 (no solo W17 y W21)

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix histórico: labels W17-W21 equiespaciados con position:absolute left:N%

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix histórico: spark bars normalizadas relativas al rango de la serie, fix val_actual*100

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix histórico: lineWidth=2px (curva no superficie), val_actual fracción→% correcto

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix histórico: CR accent #5C469C, area fill suave, puntos en color accent

### Archivos modificados
_(ver commit en GitHub)_

---

## Fix · W21 · 26 May 2026

**Descripción:** Fix gauge: Súper Crítica usa gris #8A8377 coherente con badge (como IPM Sin Conv)

### Archivos modificados
_(ver commit en GitHub)_

---

## Sesión Post-W21 (sexta parte) · Mayo 2026 · Fixes historico_module

### Contexto
Al migrar de `historico_module_v2.py` + `historico_module_rnd.py` → `historico_module.py` unificado, varios parámetros quedaron rotos porque las convenciones de escala diferían entre los módulos viejos.

### Bugs corregidos (7 commits)

**1. Eje X — solo 2 labels (W17 y W21)**
El footer usaba `justify-content:space-between` con 2 `<span>`. Fix: `position:absolute; left:N%` para N=0/25/50/75/100 → 5 labels equiespaciados.

**2. Curva parece superficie rellena**
`lineWidth = Math.round(el.width / (vals.length * 3))` producía ~25px para canvas de 380px → apariencia de área sólida. Fix: `lineWidth = 2` fijo.

**3. Color CR gris en vez de violeta**
`accent: 'var(--accent)'` no funciona en canvas 2D. Fix: `'#5C469C'` hex directo con `accent_rgb: '92,70,156'`.

**4. Valores incorrectos — "ACTUAL: 0.03%"**
`val_actual` viene como fracción del pickle (`0.0263`) pero `HIST_DATA` tiene valores en % (`2.63`). Se removió el `*100` en una sesión anterior rompiendo esto. Fix: restaurar `val_actual * 100` para `nodispo/eficacia/convrate`; IPM directo.

**5. Spark bars todas iguales**
`bar_ceil` fijo global (ej: 60% para NoDispo, $3000 para IPM) → ratio ≈0.05 → height=2px para todos. Fix: normalizar contra rango real: `ratio = (v - min) / (max - min)`.

**6. Area fill suave**
Agregado `rgba(accent, 0.12)` bajo la curva para legibilidad visual.

**7. Gauge Súper Crítica rojo en vez de gris**
El gauge usaba `#C0392B` (rojo) para Súper Crítica igual que Crítica. Fix: `#8A8377` gris coherente con el badge. Aplicado en `render_helpers.py` en `gauge_5levels()` y `BANDA_COLORS['bar']`.

### Archivos modificados
`historico_module.py` · `render_helpers.py`

### Commits
`9392e5c0` · `411805956` · `9b5fa36f` · `879d6bf9` · `f6a6b5f4` · `a4cf3d29`

---

## Fix · W21 · 26 May 2026

**Descripción:** Docs: PROMPT_CORE + HISTORIAL actualizados con fixes historico_module

### Archivos modificados
_(ver commit en GitHub)_

---

## Pipeline W21 · May 2026 · 26 May 2026

**Período:** 19-25 mayo 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`SUPPLY_W21.html` (unificado CR+RND) · 2 Excels (4 hojas c/u) · `Mail_W21.html` · `index.html` · `Price_W21.zip`

---

## Pipeline W21 · May 2026 · 26 May 2026

**Período:** 19-25 mayo 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`SUPPLY_W21.html` (unificado CR+RND) · 2 Excels (4 hojas c/u) · `Mail_W21.html` · `index.html` · `Price_W21.zip`

---

## Pipeline W21 · May 2026 · 26 May 2026

**Período:** 19-25 mayo 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`SUPPLY_W21.html` (unificado CR+RND) · 2 Excels (4 hojas c/u) · `Mail_W21.html` · `index.html` · `Price_W21.zip`

---

## Pipeline W21 · May 2026 · 26 May 2026

**Período:** 19-25 mayo 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`SUPPLY_W21.html` (unificado CR+RND) · 2 Excels (4 hojas c/u) · `Mail_W21.html` · `index.html` · `Price_W21.zip`

---

## Pipeline W21 · May 2026 · 26 May 2026

**Período:** 19-25 mayo 2026  
**Tipo:** Pipeline completo

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| RND %NoDispo | 2,81% | 2,63% | -0,17pp |
| RND IPM | $1.266 | $834 | -34,1% |
| CR Eficacia | 93,34% | 93,15% | -0,19pp |
| CR ConvRate | 1,63% | 1,57% | -0,07pp |

### Archivos generados
`SUPPLY_W21.html` (unificado CR+RND) · 2 Excels (4 hojas c/u) · `Mail_W21.html` · `index.html` · `Price_W21.zip`

**Última actualización:** W21 (pipeline) · May 2026 · 19-25 mayo 2026

---

## Sesión W22-pre · Mayo 2026 · Refactor P10 completo + P11 + Documentación

### Contexto
Sesión de refactor y fixes sin datasets nuevos. Pipeline W21 re-corrido con todos los cambios aplicados y validado visualmente. Cinco commits en total.

### Refactor P10 — Bloque A (helpers de formato)

Funciones idénticas en `render_cr_p2.py` y `render_rnd_p2.py` movidas a `render_helpers.py`:

| Función | Descripción |
|---|---|
| `es_pct`, `es_int`, `es_pct2`, `es_ipm` | Formateo de valores numéricos |
| `banda_colors` | Lookup `(bg, fg)` desde `BANDA_COLORS` |
| `wow_arrow`, `wow_arrow_abs` | Pills WoW en pp y absoluto |
| `sev_badge_html_p2` | Badge `<b>` para tablas AR |

`render_cr_p2.py`: 704 → 678 líneas. `render_rnd_p2.py`: 553 → 538 líneas.

### Refactor P10 — Bloque B (unificaciones JS + p3)

**`_mini_badge`** — ya existía en `render_helpers.py` (línea 42). Eliminada definición local duplicada de `render_cr_p3.py` y `render_rnd_p3.py`.

**`_chanRow` + `chanRowAR` → `_buildChanRow(r, i, opts)`** en `js_override.js`:
- `opts = {}` para KPI cards · `opts = {cardN:n, w20:true}` para AR cards
- `js_override.js`: 1789 → 1779 líneas

**`canasta_tab_rows(df, dim_col, cfg)`** en `render_helpers.py`:
- Reemplaza `tab_rows_canasta()` duplicada en `render_cr_p3.py` y `render_rnd_p3.py`
- La diferencia CR/RND (columnas, WoW logic, bandas) se expresa como cfg dict
- `render_cr_p3.py`: 1122 → 1064 líneas. `render_rnd_p3.py`: 984 → 945 líneas

**`build_card_rows(df, t_key, cfg)`** en `render_helpers.py`:
- Reemplaza `_build_card_rows_ef` + `_build_card_rows_cv` en `render_cr_p1.py`
- `render_cr_p1.py`: 653 → 607 líneas

### Decisiones de diseño — qué NO se unificó y por qué

| Componente | Razón para no unificar |
|---|---|
| `render_canasta_block` (p3 CR vs RND) | Lógica interna divergente: métricas, escalas, columnas, bandas y WoW pills completamente distintos. Unificar agregaría más complejidad que la que elimina |
| `_build_rnd_card_tabs_json` | Scaffolding similar a CR pero datos completamente distintos (`%NoDispo`, `IPM`, `Trafico`). Mismo razonamiento |

### P11 — Bugs de WoW y "Ver más" cerrados

**`ConvRate_WoW_pp` para todos los hoteles P80:**
- Root cause: `calc_cr.py` solo mergeaba `Eficacia_W17` y `CR_Unicos_W17` en `p80_hotel`. `ConvRate_W17` no se incluía → solo 100 de 1342 hoteles tenían WoW.
- Fix: agregar `ConvRate_W17` al merge + calcular `ConvRate_WoW_pp` para todos.

**`BandaConvRate` con Bookings reales:**
- Root cause: `tab_convrate()` no calculaba `BandaConvRate` en `df_d`/`df_c`/`df_h`. `build_card_rows` usaba `banda_convrate(val, 0)` → todos "Sin Conversión".
- Fix: agregar `BandaConvRate = banda_convrate(ConvRate, Bookings)` en `tab_convrate()` y `tab_convrate_for()`.

**WoW Corp en cards AR CR:**
- Root cause: `dim_rows` en `build_canasta_data` tenía `'—'` hardcodeado para WoW ConvRate.
- Fix: calcular `wow_cv_pp` desde `g_corp_w17['ConvRate_W17']`.

**WoW Dest en cards AR CR:**
- Root cause: merge duplicado de `g_dest_w17` generaba columnas `_x`/`_y`. El código entraba por el `elif` que recalculaba `g_dest` desde `df_hotel` sin hacer merge completo.
- Fix: unificar merge en un solo lugar antes del loop, con todas las columnas WoW en una sola operación.

**WoW IPM Corp en cards AR RND:**
- Root cause: `dim_rows` en `render_rnd_p2.py` tenía `'—'` hardcodeado para `r[9]` (WoW IPM). `g_corp` ya tenía `IPM_WoW_pp` pero no se leía.
- Fix: calcular `wow_ipm_str` desde `row.get('IPM_WoW_pp')` con escala `(wow_ipm / ipm_base) * 100`.

**"Ver más" no expandía filas:**
- Root cause 1: `display:''` (string vacío) no es un valor válido para `<tr>` — el browser lo ignora. El valor correcto es `display:'table-row'`.
- Root cause 2: `addEventListener('click')` en botón JS dinámico era interceptado por el listener global del panel histórico.
- Fix: `_moreBtn` detecta el botón HTML estático existente (`ar{n}-th-more`) con `querySelector('button[id$="-more"]')` y lo activa con `onclick` inline + `display:'table-row'` para `<tr>`.

### Pipeline W21 validado
Output visual confirmado: sort RND/CR funcionando · WoW Corp/Dest/IPM correctos · "Ver más" expande filas 6-10 · BandaConvRate correcta en tab Destino.

### Documentación
- `NOTA_REFACTOR_PENDIENTE.md` reescrita como guía de arquitectura vigente "Dónde tocar qué"
- `PROMPT_CORE.md` limpiado: 648 → 434 líneas · 50 → 35 reglas NUNCA · sección archivos eliminada (→ `README_QUICK.md`) · triggers de mantenimiento por archivo agregados
- `PROMPT_CORE.md` sección nueva: checklist de cierre de sesión + tabla de triggers por archivo

### Archivos modificados
`calc_cr.py` · `render_helpers.py` · `render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `js_override.js` · `NOTA_REFACTOR_PENDIENTE.md` · `PROMPT_CORE.md` · `HISTORIAL_SESIONES.md`

### Commits
- `8f98d4c` — W22-pre fix P9+sort
- `61068429` — pipeline W21 + P10 Bloque A+B
- `57738dcb` — P10 Parte 2 (render_cr_p1, cr_p3, rnd_p3)
- `7cc8a169` — P10 completo + canasta_tab_rows + build_card_rows
- `a825ddf8` — P11 cerrado: WoW Corp/Dest/IPM + BandaConvRate + Ver más
- `76db80f8` — NOTA_REFACTOR_PENDIENTE reescrita
- `14556b9d` — PROMPT_CORE limpieza
- `de2f0953` — PROMPT_CORE triggers de mantenimiento


---

## 📝 Sesión Junio 2026 · Hotel Inventory + Hub v2 + calc_supply.py

### Contexto
Sesión de desarrollo del módulo Hotel Inventory (`calc_inv.py`) y actualización del Hub. No se corrió pipeline PRICE. Tres tracks paralelos: (1) fixes iterativos sobre `calc_inv.py`, (2) rediseño del Hub con 6 módulos, (3) nuevo script `calc_supply.py`.

### Track 1 — calc_inv.py · Fixes acumulados

**Sistema de pills unificado (`udSyncBadges`):**
- Reemplaza múltiples sistemas de pills por una función única que lee el estado real (`hFRegion`, `hFChannel`, `hFCorp`, `udActiveFilter`)
- Usa `Set` para deduplicar — si el mismo valor viene de dos fuentes, aparece una sola pill
- El × de cada pill limpia ambas fuentes simultáneamente

**Combos siempre cyan:**
- `color:var(--accent)!important` en todos los combos habilitados — borde y texto cyan sin importar si dicen "Todos" o tienen valor

**Columnas siempre visibles:**
- `col-show-XX` ya no oculta otras columnas — todas PP/SP/Hybrid/TP visibles siempre
- `_tryInit` inicia con `udContent('all')` para mostrar todas las columnas por defecto

**Channel view:**
- Click en channel filtra el gráfico histórico (no drill de hoteles)
- Sin banner "Filtro activo", sin texto "Hacé clic..."
- RateFox → Third Party normal (`residual=False`)
- PP: Avg Dest con barra visual; Third Party: % Gap (`hoteles/N*100`)
- `max_avg_dest` definido antes del loop `p_rows`

**Otros fixes:**
- `× Limpiar` oculto hasta que `hIsFiltered()` sea true
- Espacio entre filas de pills (border-bottom separador)
- `hPopulateWeeks` llamado en `hInit` → semanas pre-populadas
- `months_by_year` desde `acum_weeks` con cap a `snapshot_month`
- Masthead con `height:12px` spacer + padding aumentado
- Header ordenable PP/SP/Hybrid con `udSortCol()`
- `gapSyncDim()` respeta `udActiveFilter` + `udActiveFilters`
- Excel generado automáticamente al final: 5 hojas (Resumen/Región/Corp/Destino/Channel)
- Footer con botón `⬇ Excel Inventory`

**Bugs cerrados en esta sesión:** B9–B22 (ver PROMPT_INV.md v12.0)

### Track 2 — Hub v2 · 6 módulos

**Diseño nuevo (`build_package.py`):**
- Título "Hub" + tag "Supply Optimization" + logo PriceTravel con ícono a la derecha
- 3 secciones: Activos · En construcción · Backlog
- Cards fondo `#EDE8DF` (mismo tono que el Hub)
- Cards inactivas: trama diagonal + chip flotante (🔧 llave / 🔒 candado)
- Backlog con opacidad 55%

**6 módulos:**
| # | Módulo | Estado |
|---|---|---|
| 1 | Weekly KPIs (CR + RND) | ✅ Activo — con KPIs reales W21 + WoW |
| 2 | Hotel Inventory | 🔵 Beta |
| 3 | RateCode Inventory | 🚧 En construcción (15%) |
| 4 | Supply Troubleshooting (Rocket Chat) | 🚧 En construcción (60%) |
| 5 | Optimization Strategy Layer | 📋 Backlog |
| 6 | Alertas | 📋 Backlog |

**Estructura repo actualizada:**
```
inventory/week-NN/
    INVENTORY_WNN.html
    Analisis_Inventory_WNN.xlsx
```
`build_package.py` incluye esta carpeta en el ZIP del repo.

### Track 3 — calc_supply.py

Script standalone que reemplaza el pipeline de 10 pasos para CR+RND:
- Bloque CONFIG al principio (WEEK, VOL_NUM, PERIODO, etc.)
- 4 datasets en la misma carpeta
- Ejecuta los scripts del pipeline en orden via `runpy`
- Pickles en `/tmp/` para no ensuciar la carpeta de trabajo
- Coexiste con el pipeline oficial — no lo reemplaza

### Pendientes para próxima sesión (INV)
- Fixes residuales pills: doble pill, pill métrica, Marriott pisa filtro anterior, Channel sin pills
- Destino como cuarta dimensión en filtros del histórico

### Archivos generados/modificados
`calc_inv.py` · `build_package.py` · `calc_supply.py` · `PROMPT_INV.md` (v12.0)

---

## Pipeline W22 · Junio 2026 · 02 Jun 2026

**Período:** 26 may – 1 jun 2026
**Tipo:** Pipeline completo

### KPIs W22

| Métrica | W21 | W22 | WoW |
|---|---|---|---|
| CR Eficacia | 93,15% | **94,21%** | +0,86pp 🟢 |
| CR ConvRate | 1,57% | **1,00%** | -0,57pp 🔴 |
| RND %NoDispo | 2,63% | **2,61%** | -0,02pp ≈ |
| RND IPM | $834 | **$653** | -21,7% 🔴 |

**Por canastas CR:** Eficacia mejora en todos (CUG +2,49pp · B2C +0,80pp · OP +0,31pp). ConvRate cae en todos.
**Por canastas RND:** NoDispo estable. IPM cae ~20-27% en todos los canales.

### Cambios aplicados

#### Compatibilidad dataset CR W22
Dataset `Dataset_CheckRates_W22.xlsx` no incluye columna `Successful UniqueChkRts`.
Fix en `calc_cr.py` (función `load_and_clean`): si la columna está ausente, se deriva automáticamente como `round(Efectividad en CheckRates × CR_Unicos)`. Compatibilidad permanente para datasets futuros.

#### Histórico expandido a 7 semanas (W16–W22)
- `historico_data.py`: ventana expandida de 5 → 7 semanas. `SEMANAS = ['W16'...'W22']`. Arrays de 4 → 6 valores estáticos; el 7° (semana actual) sigue siendo dinámico desde el pickle.
- Datos W16 global: reales del historial. Datos W16 por canasta: estimados con ratios W17.
- Con W23 se alcanza la ventana objetivo de 8 semanas; desde W24 ventana móvil.
- Bug corregido en `_hist_vals()` de `assemble_unified.py`: condición `len(base) == 4` → `len(base) >= 1` (fallaba con arrays de 6 valores).
- `js_override.js` y `assemble_unified.py`: array de semanas actualizado a 7 elementos.

#### Fix puntos canvas — todos visibles
Los puntos intermedios de las gráficas históricas eran prácticamente invisibles (`alpha=0.6, rgba con opacidad 0.5, radio=2`). Fix aplicado en 3 archivos fuente:
- `historico_module.py` (fuente principal del JS canvas)
- `js_override.js` (re-draws al cambiar canasta)
- `demo_js_main.js` (canvas inicial)

Cambio: todos los puntos con `alpha=1.0`, color sólido `ACCENT_HEX`, radio `2.5`. El último punto mantiene radio `3.5` + anillo blanco `#FDFCF9` para distinguir la semana actual.

### Archivos modificados
`calc_cr.py` · `calc_supply.py` · `assemble_unified.py` · `historico_data.py` · `historico_module.py` · `js_override.js` · `demo_js_main.js`

### Archivos generados
`SUPPLY_W22.html` · `Analisis_CheckRates_W22.xlsx` · `Analisis_RatesNoDispo_W22.xlsx` · `Mail_W22.html` · `Price_W22.zip` · `ProyectoClaude_PRICE_W22.zip`

---

## Pendientes para W23

- **Histórico 8 semanas:** agregar valores W22 a cada array en `historico_data.py` → ventana completa W16–W23
- **P5 · `extract_hist_data.py`:** util para extraer KPIs del pickle y actualizar `historico_data.py` automáticamente cada semana
- **`update_docs.py`:** regenerar — falta en el proyecto, genera warning en el commit

---

## Post-Pipeline W22 · Visual & Infrastructure · 03 Jun 2026

### Hub (`index.html` + `build_package.py`)
- Header: badge `WEEK NN` amarillo `#FCB000` texto dark grey · título `Hub` violet `#5C469C` · `Supply Optimization` dark grey
- Badges unificados: todos amarillo `#FCB000` + texto `#333132` (ACTIVO, BETA, EN CONSTRUCCIÓN, BACKLOG)
- Labels de sección eliminados (ACTIVOS / EN CONSTRUCCIÓN / BACKLOG)
- Card 1: bajada → "Connectivities Health & Availability Success" · KPIs: Eficacia CR · %NoDispo · IPM
- Card 2: "Hotel Inventory" → "State of PriceTravel Product" · label "Total" · sin "htls" · rojo `#E53935`
- Card Inventory clickeable → `inventory/week-NN/INVENTORY_WNN.html`

### Masthead Connectivities & Hotel Availability
- Título: `Connectivities` cyan `#4FC3F4` · `& Hotel` negro · `Availability` cyan `#4FC3F4`
- Loading screen: barra violet `#5C469C`
- Archivos: `render_cr_p1.py` · `render_rnd_p1.py` · `assemble_unified.py`

### Pipeline Inventory (`calc_inv.py`)
- Movido a `inventory/calc_inv.py` en el repo GitHub
- `OUTPUT_DIR = Path(f"week-{WEEK_NUM:02d}")` — outputs en subcarpeta automática
- Loading screen cyan `#4FC3F4` — mismo patrón que Supply
- Footer: botón "← Volver al Hub"
- Rojo: `#C0392B` → `#E53935` (24 ocurrencias)
- `INPUT_FILE = "dataHoteles_contratos.xlsx"` (nombre real del dataset)

### Infrastructure
- `session_init.py` — nuevo script de bootstrap: clona repo al inicio de sesión
- Proyecto Claude: 4 archivos (PROMPT_CORE + PROMPT_INV + calc_inv + text2.txt)
- Docs y scripts viven en el repo — no subirlos al proyecto Claude
- `build_package.py` incluye `inventory/calc_inv.py` en el ZIP del repo
- `.gitignore` actualizado — excluye datasets Excel y pickles

### Pendientes para W23
- Segunda corrida `calc_inv.py` W22 con rojo `#E53935` + loading cyan + footer Hub
- Reorganizar scripts en subcarpetas del repo (alto riesgo — dejar para W24)
- `extract_hist_data.py` — automatizar actualización histórico
- `update_docs.py` — eliminar warning del commit

---

## Post-Pipeline W22 · Hub visual fixes · 03 Jun 2026 (continuación)

### Masthead Connectivities & Hotel Availability — color final
- `Connectivities` → magenta `#EA0074` (antes cyan)
- `& Hotel` → negro `var(--ink)`
- `Availability` → magenta `#EA0074` (antes cyan)
- Loading bar → magenta `#EA0074` (antes violet)
- Archivos: `render_cr_p1.py` · `render_rnd_p1.py` · `assemble_unified.py`

### Hub — fixes adicionales
- Card 2 clickeable → `inventory/week-NN/INVENTORY_WNN.html`
- KPIs card 2: Total · P. Propio · Gap 2026 · sin "htls" · rojo `#FF3B30`
- Badges WoW: variables Python pre-calculadas (no f-strings con expresiones)
- Grid cards activas: `repeat(2,minmax(0,1fr))` + `min-width:0` en rpt-card
- Todas las ocurrencias `#C0392B` → `#FF3B30` en build_package.py

### Inventory calc_inv.py — fixes
- Rojo `#FF3B30` (24 ocurrencias, antes `#C0392B`)
- Loading screen cyan `#4FC3F4`
- Footer: botón "← Volver al Hub"
- OUTPUT_DIR automático `week-{WEEK_NUM:02d}/`

---

## Cierre sesión W22 · Hub + Inventory final · 03 Jun 2026

### Estado final deployado ✅
- **SUPPLY_W22.html** — Connectivities+Availability magenta · loading magenta · barra violet eliminada
- **INVENTORY_W22.html** — rojo #FF3B30 · loading cyan · Volver al Hub · footer beige · Evolución Histórica del Producto
- **Hub (index.html)** — Hub violet · Supply Optimization dark grey · badges FCB000 · 2 cols fijas · badges WoW · sin labels sección

### Pendientes W23
- Instrucciones PowerShell completas para ambos pipelines
- `extract_hist_data.py` — automatizar histórico
- Segunda corrida Inventory cada semana después del git pull
- Agregar W22 al histórico en `historico_data.py` cuando se procese W23

### Lección aprendida
- `build_package.py` tiene múltiples capas de parches — para W23 conviene auditar el bloque de cards del Hub de una vez antes de tocar nada
- El ZIP del proyecto Claude se genera SIEMPRE después de actualizar docs

---

## Fix pipeline local · calc_supply.py · 03 Jun 2026

### Problema resuelto
- `calc_supply.py` guardaba pickles en `tempfile.gettempdir()` (C:\Temp\)
- Los renders buscaban los pickles ahí pero con path largo que fallaba
- Fix: `Path(__file__).parent` — pickles en el mismo directorio que el script

### Git pull lento
- `git pull` se cuelga con archivos grandes (SUPPLY_W22.html 7MB)
- Alternativa: `git fetch origin && git reset --hard origin/main`
- Los datasets no se pierden (están en .gitignore)

### Dependencias verificadas en PC local
- Python 3.14.5 · pandas 3.0.3 · openpyxl 3.1.5 · xlsxwriter 3.2.9 · numpy 2.4.6

---

## Sesión Inventory fixes · 05 Jun 2026

### Contexto
Pipeline Inventory W22 con nuevo dataset (tipo_Ht_contrato_2). Múltiples fixes de clasificación, gráfico histórico y UI interactiva.

### Cambios en calc_inv.py
- Compatibilidad nuevo dataset: tipo_Ht_contrato_2 → TipoHotel, solo_propios, sin_contrato_valido, FechaCreacion sin tilde, Expedia.1→Expedia_tercero
- df_hist filtrado hasta fin de W22 (date.fromisocalendar(YEAR, WEEK, 7))
- df_hist_pp para gráfico histórico default (Solo Propio + Hybrid)
- dim_tipo_idx: índice por tipo sin duplicar por corp/región
- hGetDim: fix para Prod. Propio (filtra Solo Propio + Hybrid), usa dim_tipo cuando solo hay filtro de tipo
- CSS: gap-pill.active → violet, th-vs/td-vs display:none (VS GLOBAL eliminado), col-show resaltado
- udToggleContent: hFTipo correcto + _fromToggle flag
- udContent: _fromToggle, hFTipo correcto para todos los tipos, regex fix className, gap→Third Party, sindir resaltado
- _tryInit: default PROD. PROPIO activo al cargar
- Penetración → % Propio en tabla gap

### Pendientes documentados
- P7: Columnas tabla — resaltar header columna activa según pill (sin cambiar visibilidad)
- P8: Tooltip gráfico histórico — fondo menos contrastante que negro
- P6: Channel View — columna % Gap junto a Hoteles en tabla Third Party
- Hotel Unico V2 sin datos en gráfico histórico — investigar FechaCreación

### Lección aprendida
- Nunca parchar el HTML manualmente — siempre llevar los fixes al calc_inv.py
- Git Tree API para archivos > 1MB (SUPPLY_W22.html 7MB, INVENTORY_W22.html 6.7MB)
- Los fixes de JS/CSS complejos requieren sesión dedicada con foco

---

## Cierre sesión · 05 Jun 2026 (continuación)

### Fixes calc_inv.py aplicados
- FF3B30 → #6A6A6A en todas las cards
- Sort todas las columnas con indicador ↑↓ + dataset key fix (guiones→underscore)
- hFChannel limpiado al salir de vista channel
- hGetDim · tipoMatch en bloque channel (Prod.Propio = Solo Propio + Hybrid)
- Pills contratación: solo PROD. PROPIO + SIN CONTRAT.
- Tooltip beige tenue

### Pendientes próxima sesión
- P6: Channel View · % Gap junto a Hoteles
- P7: Resaltar header columna activa según pill
- P8: (resuelto — tooltip beige)
- Commitear INVENTORY_W22.html con todos los fixes (el HTML local tiene los cambios pero no se pudo subir)
- Verificar sort columnas funciona correctamente
- Verificar filtros channel + región funcionan correctamente

---

## Sesión W23 inicio · 08 Jun 2026

### Contexto
Inicio pipeline W23 Inventory. Dataset W23 disponible localmente en `inventory/`.

### Issue
- Al editar el CONFIG en calc_inv.py localmente se rompió una línea del HTML
- Solución: `git fetch origin && git reset --hard origin/main` y re-editar solo el CONFIG
- SNAPSHOT_DATE_UPPER debe estar en el CONFIG (ya está en el repo desde W22)

### CONFIG W23
```python
WEEK          = "W23"
WEEK_NUM      = 23
VOL_NUM       = "23"
YEAR_ACTUAL   = 2026
SNAPSHOT_DATE = "9 de Junio de 2026"
SNAPSHOT_DATE_UPPER = SNAPSHOT_DATE.upper()
INPUT_FILE    = "dataHoteles_contratos.xlsx"
```
---

## Sesión W23 Supply · 08–09 Jun 2026

### Contexto
Commit de outputs W23 generados localmente. Diagnóstico de peso excesivo del HTML y fix de links de descarga en el footer.

### Archivos commiteados
- `reports/week-23/SUPPLY_W23.html` — 9.56 MB (corregido desde 13.75 MB)
- `checkrates/week-23/Analisis_CheckRates_W23.xlsx` — 239 KB
- `rates-nodispo/week-23/Analisis_RatesNoDispo_W23.xlsx` — 1.16 MB

### Bug cerrado · Scripts de datos duplicados en SUPPLY_WNN.html

**Síntoma:** HTML de W23 pesaba 13.75 MB (W22 pesaba ~7 MB).

**Causa:** `assemble_unified.py` embebía `CR_CV` / `RND_CV` / `CR_D` / `CR_AL` dos veces:
1. En `p2_cr` y `p2_rnd` incluidos directamente en el body (scripts ~1.9MB y ~2.3MB)
2. En `FOOTER_JS` vía `_extract_last_script(p2_cr)` y `_extract_last_script(p2_rnd)` (re-emite los mismos datos junto con `demo_js_main.js` + `js_override.js`)

**Fix en `assemble_unified.py`:**
- Agregada función `_strip_last_script(html)` que elimina el último `<script>…</script>` de un HTML parcial
- Al incluir `p2_cr` y `p2_rnd` en el body se usa `_strip_last_script()` para no duplicar
- El script de datos sigue en `FOOTER_JS` (único lugar correcto)

**Ahorro:** ~4.2 MB por semana. W23: 13.75 MB → 9.56 MB.

### Bug cerrado · Links footer Excel devuelven 403 en Netlify

**Síntoma:** Botones "⬇ Excel CheckRates" y "⬇ Excel Rates No Dispo" no descargaban.

**Causa:** Links usaban rutas relativas (`../../checkrates/week-NN/...`). Netlify devuelve **403** al servir `.xlsx` directamente aunque el `netlify.toml` tiene la config correcta.

**Fix en `assemble_unified.py`:**
```python
# Antes (ruta relativa → Netlify 403)
href="../../checkrates/week-{VOL_NUM}/Analisis_CheckRates_W{VOL_NUM}.xlsx"

# Después (raw.githubusercontent.com → 200 OK)
href="https://raw.githubusercontent.com/federicochurches/Price/main/checkrates/week-{VOL_NUM}/Analisis_CheckRates_W{VOL_NUM}.xlsx"
```
Aplica igual para `rates-nodispo`. El fix es permanente — W24+ sale correcto de fábrica.

### Proceso de re-pipeline en Claude (sin datasets locales)

Cuando se corre el pipeline en Claude y no están los pickles W(N-1):
1. Copiar datasets W(N-1) desde las carpetas del repo (`checkrates/week-NN/`, `rates-nodispo/week-NN/`)
2. Correr `calc_cr.py` y `calc_rnd.py` con env vars W(N-1) para generar los pickles previos
3. Luego correr `calc_supply.py` normalmente con los datasets W(N)

Los datasets W21 y W22 están en el repo en sus respectivas carpetas week-NN.

### Lecciones aprendidas
- `assemble_unified.py` usa `_extract_last_script()` para sacar datos de p2 → siempre stripear p2 antes de incluirlo en el body para no duplicar
- Netlify 403 en xlsx es estructural — usar siempre `raw.githubusercontent.com` para links de descarga
- Después de commitear `assemble_unified.py`, verificar que el HTML generado tiene los links correctos antes de asumir que el fix aplicó (el repo clonado puede estar desactualizado)
- `present_files()` es necesario para que el usuario vea el HTML — no basta con generarlo en outputs

### Scripts modificados
- `assemble_unified.py` — `_strip_last_script()` + links footer raw.githubusercontent.com


---

## Sesión W23 Bookability · 10 Jun 2026

### Contexto
Incorporar **Bookability** como 3ª card KPI cross-canasta en el reporte Connectivities. Sesión extendida de iteración visual con múltiples regeneraciones, fix de severity persistente vía JS, refactor del layout de Channel en las 3 cards, ordenamiento clickable unificado, y agregado del módulo Bookability en la sección Severity.

### Dataset
- `Dataset_Bookability_W23.xlsx` (acumulado W16-W24, 157.910 filas)
- Columnas: Provider, LOB, SourceMarket, Destination, Corporate, Hotel, Semana, Bookability, Books
- **Bookability ponderada:** `sum(Bookability × Books) / sum(Books)`
- **W23 global:** 98.43% · WoW +0.03pp · Banda Exitosa
- **Histórico W16-W23:** [98.28, 98.44, 98.22, 98.26, 98.17, 98.25, 98.40, 98.43]
- W24 (volumen parcial 6172 books) excluido del histórico

### Archivos modificados
- `calc_bk.py` — NUEVO. Genera `bk_w23_data.pkl` con:
  - `bk_global`, `bk_prev`, `bk_wow`, `books_global`, `books_global_prev`
  - `g_provider`, `g_dest`, `g_corp`, `g_hotel` (con `BK_WoW_pp`, `Books_WoW_abs`, `Books_WoW_pct`, `CorpName` mergeado en hoteles)
  - `TOP_PROVIDER`, `TOP_DEST`, `TOP_CORP`, `TOP_HOTEL`
  - `hist_by_week` (W16-W24 desde dataset acumulado)
  - `sev_bk_p80` (conteos por banda)
  - Usa mismo `_CHANNEL_RENAME` que CR (`HotelBeds Apitude → HotelBeds`, `Hotel Unico V2 → Hotel Unico`)
- `render_cr_p1.py` — `render_kpi_card_bookability()` con todas las pestañas (Destino/Corp/Hotel/Channel), ordenamiento clickable, helpers compartidos
- `render_cr_p2.py` — `render_severity()` con tercera columna Bookability
- `historico_module.py` — `bookability` en `getBanda` (rama de eficacia) + `target_disp` + `metric in ('eficacia','convrate','nodispo','bookability')` para conversión %; `margin-top:auto` en el wrapper para alinear los 3 históricos al fondo
- `historico_data.py` — `'bk': {'bookability': {'global': [W16..W22]}}` (W23 dinámico desde pickle)
- `assemble_unified.py` — Carga DB BK, agrega card 3 en HERO + en AR, `BK_JS_DATA` + `BK_SORT_JS` en GLOBAL_PANEL_SCRIPT, IDs `w22-strip-bk-item`/`w22-strip-bk-sep`, label `Severity Eficacia`/`Severity NoDispo`
- `render_helpers.py` — `searchbox_pill_html()` sin `border-left`/`margin-left:auto` agresivo
- `js_override.js` — `_cardRow` grid 5 cols sin badge sev, `_KPI_GRID` actualizado, `hdrLabels` sin Severity en EF/CV, `_KPI_RCOLS` expandido a todas las columnas, flechas `↕/↑/↓`, `_buildChanRow` sin badge + con TRX, `_arRenderChan` flex column + header con columnas, `w22_setMode` oculta BK item en RND y cambia label Severity, `CATALOG_TP` unificado, `h-bk-global` en lista de tooltip patch
- `asset_supply_head.html` — Reglas CSS tabs BK (channel/destino/corp/hotel)

### Bugs cerrados

**Severity persistente en cards 1 y 2 — diagnóstico clave**

El HTML estático generado por Python no incluía `sev-badge` ni columna Severity. PERO en el browser seguía apareciendo. Causa raíz:

- La función `_cardRow` en `js_override.js` **re-renderiza** las filas KPI cards en runtime (al cambiar canasta, sortear, etc.) con un grid de 6 columnas e inyecta el `sev-badge`.
- Fix: cambiar `_cardRow` a grid 5 cols, quitar la generación del badge.
- También arreglar `_KPI_GRID`, `hdrLabels` y limpiar el "<span></span>" extra del header.

**Lección:** Cuando un fix visual no se ve en runtime, buscar funciones JS que re-rendericen el elemento (no solo HTML estático).

**Histórico BK mostraba "CRÍTICA" con valor 98.43%**

`getBanda` en `historico_module.py` no tenía caso explícito para `METRIC === 'bookability'`. Caía en la rama por defecto (IPM) donde `v < 200 → 'Crítica'`. Fix: agregar `bookability` a la rama de Eficacia.

**Histórico BK no traía W23 (mostraba solo hasta W22)**

`historico_module.py` convierte `val_actual` (fracción del pickle) a % solo si `metrica in ('eficacia','convrate','nodispo')`. Bookability caía en el `else` con `round(val_actual, 1)` → 0.9843 → 1.0 → display incorrecto.

Fix: agregar 'bookability' a la lista de conversión a %.

**Botón "Ver más" arriba en card BK después de sort**

El `bkSort` usaba `appendChild` que mueve las filas al final del contenedor, dejando el botón "Ver más" arriba. Fix: usar `insertBefore` con el botón como referencia, mantener wrapper `bk-more` para filas 6-10 ocultas, preservar estado expandido del botón.

**Banda Eficacia 94,53% mostraba "ACEPTABLE" en barra superior sin contexto**

Causa: el badge `w22-strip-band` muestra una sola banda pero el label decía solo "Severity" — no especificaba qué métrica era la referencia. Fix: label dinámico "Severity Eficacia" (CR) / "Severity NoDispo" (RND).

**Bookability visible en modo Availability (debería ser CR-only)**

Bookability solo aplica a Connectivities (CR). Fix: IDs en `w22-strip-bk-item`/`-sep` + lógica en `w22_setMode` para `display:none` en modo RND. Misma lógica para `ar-strip-bk-*`.

### Decisiones de diseño

- **Bookability como 3ª card** (no reemplaza ninguna)
- **Color BK fijo:** `#333132`
- **Cross-canasta:** no aplica filtro de canasta
- **Tabs orden BK:** `Destino · Corp · Hotel · Channel` (Channel a la derecha, Destino default — mismo que EF/CV)
- **Sin columna Severity en filas de las 3 cards** (cards KPI)
- **Columnas BK:** Channel/Hotel/etc · Trx (bold) · WoW · BK% · WoW (5 cols)
- **Header abreviado:** "BK%" en lugar de "Bookability"
- **Sub-label corporativo** debajo del nombre del hotel en tab Hotel
- **Sin palabra "Area"** en nombres de destinos (display)
- **Histórico BK W16-W23** (excluye W24 con volumen parcial)
- **Searchbox** en línea separada (debajo de tabs, alineado derecha)
- **Channel unificado en las 3 cards:** flex-column (PP arriba, TP abajo) + header con columnas + sin badge severity
- **Ordenamiento clickable unificado:** flechas `↕/↑/↓` en todas las cards KPI, todas las columnas sorteables
- **Alineación de los 3 históricos:** `kpi-card` con `display:flex; flex-direction:column` + histórico con `margin-top:auto` para que se empujen todos al fondo de la card

### Reglas nuevas en PROMPT_CORE

1. La función `_cardRow` en `js_override.js` re-renderiza las filas EF/CV en runtime con grid 5 cols sin severity. **Cambios visuales en filas KPI requieren tocar también `_cardRow`.**
2. Para alinear los 3 históricos al fondo: `kpi-card` debe tener `display:flex; flex-direction:column;` y el histórico `margin-top:auto`.
3. Bookability solo aplica a Connectivities — ocultar via JS en w22_setMode cuando `m === 'rnd'`.
4. `getBanda` en `historico_module.py` debe tener caso para cada métrica nueva. Bookability usa bandas de Eficacia (≥97% Exitosa).
5. `target_disp` en `historico_module.py` debe tener entrada para cada métrica nueva.
6. Cuando se agrega métrica nueva al pipeline (ej. Bookability), agregarla a la condición de conversión a % en `historico_module.py`: `if metrica in ('eficacia','convrate','nodispo','bookability')`.
7. Channel layout canónico (cards 1, 2 y 3 + AR): flex-column con PP arriba, TP abajo, header con columnas (Channel/Trx/Métrica/WoW), sin badge severity.

### Scripts modificados
- `calc_bk.py` (nuevo)
- `render_cr_p1.py`
- `render_cr_p2.py`
- `historico_module.py`
- `historico_data.py`
- `assemble_unified.py`
- `render_helpers.py`
- `js_override.js`
- `asset_supply_head.html`

---

## Sesión W24 · 15-06-2026 · Bugs B68/B69 + Pipeline W24

### Contexto
Pipeline W24 (8–14 jun 2026). Métricas: CR Eficacia 95.55% (Aceptable, +0.75pp) · Conv Rate 0.82% (Revisar) · RND %NoDispo 3.02% · Bookability 98.67% (Exitosa, +0.24pp). Sesión de múltiples fixes post-pipeline antes de distribución.

### Bugs cerrados

#### B68 — SyntaxError en Chrome: regex inválida (`js_override.js` L1)
- **Síntoma:** Strip superior (EFICACIA/CONV RATE/BOOKABILITY) mostraba "—", cards AR no inicializaban. Error en consola Chrome: `supply_w24:5226 Uncaught SyntaxError: Invalid regular expression: missing /`
- **Root cause:** `js_override.js` comenzaba con `/` suelto en L1 (faltaba el `*` para abrir `/*`). En W23 Chrome lo toleraba; en W24 el script 17 creció de 4.5MB a 6.5MB y cambió el contexto de parseo — Chrome interpretó el `/` como inicio de regex inválida e interrumpió toda la ejecución JS.
- **Fix:** Corregir L1-L7 de `js_override.js`:
  - Antes: `/\n  /* Reset filtros...` + `* Semanas históricas...*/`
  - Después: `/* Reset filtros cruzados al cambiar canasta */\n...\n/* Semanas históricas... */`
- **Archivos:** `js_override.js`, `SUPPLY_W24.html` regenerado
- **Commit:** `60ac46b7`

#### B69 — Botón "Ver más" duplicado en cards AR (3 iteraciones)
- **Síntoma v1:** Dos "VER MÁS" en cards 1 y 2. Card 3 sin botón.
- **Root cause:** `_moreBtnAll` usaba `tbody.closest('table')` pero `ar1-th` es un `div`, no `table` → retorna `null`. El loop `querySelectorAll('.kpi-tab-rows')` también procesaba `ar1-th` y creaba un `div.kpi-more-btn` dinámico, mientras que el loop `[1,2].forEach` no activaba el botón estático.
- **Fix v1:** Dos cambios en `_moreBtnAll`:
  1. Loop `.kpi-tab-rows` excluye divs AR con `/^ar\d+-/.test(el.id)`
  2. Loop `[1,2].forEach` usa `getElementById('ar1-rows-wrap')` como container

- **Síntoma v2:** Aún duplicado. Root cause real: `ar_renderTable()` ya activaba `ar1-th-more` directamente, y el loop `[1,2].forEach` de `_moreBtnAll` también lo activaba → doble activación + div dinámico residual.
- **Fix v2:** Eliminar completamente el loop `[1,2].forEach` de `_moreBtnAll` — `ar_renderTable()` es la única fuente de verdad para cards AR 1/2.

- **Síntoma v3:** Card 3 (BK) sin botón. Root cause: el código buscaba `getElementById('ar3-more-wrap')` que no existe. El botón es `ar3-more-btn` con id que termina en `-btn` no en `-more` → `_moreBtn` no lo encontraba.
- **Fix v3:** Activar `ar3-more-btn` directamente con la misma lógica que `ar_renderTable` usa para ar1/ar2 — chequear `filteredWithPos.length > _KPI_TOP_N` y setear `display:''` + `onclick` explícito.

- **Síntoma v4:** `ar3-more-btn` más pequeño que ar1/ar2. Root cause: le faltaba `width:100%;margin-top:4px;` y el div contenedor tenía `text-align:center`. Además, el `div.kpi-more-btn` dinámico de cards KPI tenía estilo diferente (9px, sin borde).
- **Fix v4:** 
  - `assemble_unified.py`: `ar3-more-btn` con `width:100%;margin-top:4px;`, contenedor sin `text-align:center`
  - `js_override.js`: `kpi-more-btn` cambiado de `div` a `button` con mismo estilo que AR buttons

- **Commits:** `646bc669` · `b6b2dade` · `c33a2b3e` · `e2f542e1`

### Pipeline W24
- **Datasets:** 6 datasets validados (CR/RND/BK W24 + W23, bookability semanal y acumulado)
- **RateFox** agregado a Third Party en `calc_bk.py`
- **Bookability W24:** `Dataset_bookability_W24.xlsx` filtrado `Semana==24` para cur (62.857 books reales vs 6.172 del acumulado incompleto)
- **index.html:** actualizado con KPIs W24 (95.6% / 0.82% / 3.04% / $611)
- **Commits:** pipeline W24 + 5 commits de fixes post-pipeline

### Scripts modificados esta sesión
- `js_override.js` — B68 (L1 slash), B69 (Ver más duplicado × 4 iteraciones), kpi-more-btn estandarizado
- `assemble_unified.py` — ar3-more-btn width:100% + wrapper sin text-align:center
- `calc_bk.py` — RateFox Third Party, lógica bookability semanal vs acumulado
- `render_cr_p1.py` — clasificación _PROPIO/_TERCERO dinámica desde TipoProvider
- `historico_data.py` — ventana móvil W17-W24
- `calc_supply.py` — CONFIG W24
- `SUPPLY_W24.html` — regenerado múltiples veces (fixes B68+B69)
- `index.html` — KPIs W24

### Lección aprendida
- **Script 17 en W24 creció 2MB** (4.5MB → 6.5MB) por más hoteles/datos — cambió el contexto de parseo de Chrome y expuso el bug latente de B68 que en W23 era inofensivo.
- **`ar_renderTable()` es la única fuente de verdad** para los botones Ver más de las cards AR 1/2. `_moreBtnAll` no debe interferir con AR.
- **Netlify delay:** cuando hay múltiples commits seguidos, Netlify puede omitir deploys intermedios. Forzar redeploy con commit explícito del `index.html`.

---

## Sesión W25-hist-entity · 24-06-2026

### Contexto
Sesión de debugging intensivo de sparklines W19-W23 en KPI cards, AR cards y channel view. Todos los bugs se originaban en que el historial W19-W23 usaba proxy corp (igual para todos los hoteles/providers del mismo corp).

### Bugs resueltos

#### BK sparkline arriba de la tabla
- **Síntoma:** El sparkline `h-bk-panel` aparecía encima de la tabla de destinos en la card Bookability.
- **Root cause:** El outer div del sparkline (`<div style="margin-top:12px;border-top...">`) envolvía a `kpi-bk-panels` — era su padre, no su hermano. El CSS del div se aplicaba sobre el container de toda la tabla.
- **Fix:** Reorder quirúrgico en el HTML: mover el contenido del sparkline (label + canvas + IIFE) para que quede DESPUÉS del cierre de `kpi-bk-panels`, dentro del mismo outer div pero al final. También corregido en `render_cr_p1.py`.
- **Commits:** `99bfac2b` (intento fallido que rompió el HTML) → `7b12215d` (revert) → `08ce1f33` (fix correcto con balance de divs verificado, net=1)

#### Bug 1 — BK KPI channel sparkline visible desde cualquier tab
- **Síntoma:** El sparkline de Bookability no era visible en la vista Channel.
- **Root cause:** `h-bk-panel` estaba en el tab `hotel` (display:none en otras vistas).
- **Fix:** Mover el sparkline fuera de los tabs. Commits `99bfac2b`, `7b12215d`.

#### Bug 2 — AR1/AR2 hotel view doble-toggle cancelaba selección
- **Root cause:** Dos listeners bubble registraban el mismo click. El de `assemble_unified.py` seleccionaba (data-selected='1'). El de `js_override.js` lo veía como ya seleccionado y deseleccionaba en el mismo frame. El usuario no veía nada.
- **Fix:** Eliminar el bloque `if (view === 'hotel')` del listener de `js_override.js` — solo `_handleKpiCardHistClick` maneja hotel view en AR. Commit `8b65087c`.

#### Bug 3 — AR1/AR2 KPI value y WoW box no actualizaban
- **Síntoma:** Al seleccionar un hotel en AR, el número grande y el bloque W24/W25/WoW no cambiaban.
- **Root cause:** El handler solo actualizaba el sparkline pero no los elementos estáticos de la card.
- **Fix:** Agregar actualización de `ar-kpi-N` y `ar-N-wowbox` al seleccionar hotel; `_arPillRender` al deseleccionar. Commit `5fc55f92`.

#### Bug 4 — Destinos sin historial W19-W23 (Medellin, El Cairo, Bávaro)
- **Root cause:** Mismatch de nombre: el label del HTML era `"Medellin"` pero `CR_DEST_HIST` tenía `"Medellin Area"`. El 87% de los destinos en el dict histórico tienen sufijo ` Area` que el pickle actual no tiene.
- **Fix:** Lookup con fallback `+Area`/`-Area` en `_handleKpiCardHistClick`. Commit `7b12215d`.

#### Bug 5 — Historial W19-W23 igual para todos los hoteles/providers del mismo corp
- **Root cause estructural:** El historial W19-W23 usaba `CR_CORP_HIST[corp][metric]` como proxy para todos los hoteles de un corp → Holiday Inn Madrid e Holiday Inn Roma mostraban la misma curva (IHG). Igual para channels (DerbySoft, SynXis, etc. usaban el global).
- **Fix pipeline:** `build_hist_entity.py` extendido para agregar dimensiones `hotel` y `provider` en `build_cr_hist` (6024 hoteles, 10 providers W18-W24) y `hotel` en `build_rnd_hist`.
- **Fix render:** `render_cr_p1.py` emite `CR_HOTEL_HIST` y `CR_PROVIDER_HIST`; `render_rnd_p1.py` emite `RND_HOTEL_HIST`.
- **Fix handler:** `assemble_unified.py` usa `CR_HOTEL_HIST[nombre]` primero, fallback corp. Channel usa `CR_PROVIDER_HIST[label][ck]` para historial real. AR hotel view: mismo patrón.
- **Para W25 sin re-pipeline:** los dicts inyectados directamente en el HTML (CR_HOTEL_HIST 818KB, 6024 hoteles; CR_PROVIDER_HIST 1KB, 10 providers). Commits `f78b53b0` → `e0fe5465`.

#### Bug 6 — Doble-listener en _handleKpiCardHistClick para AR
- **Root cause:** El listener global de `assemble_unified.py` capturaba clicks en `ar1-th` (kpi-tab-rows) y llamaba `_handleKpiCardHistClick` que tenía un `return` vacío para hotel view. El handler real de `js_override.js` L1957 nunca llegaba.
- **Fix:** `_handleKpiCardHistClick` ahora hace el trabajo completo para AR hotel view (ya no return vacío). Commit `8b43f01c`.

### Scripts modificados
- `build_hist_entity.py` — agrega hotel+provider en build_cr_hist, hotel en build_rnd_hist
- `render_cr_p1.py` — emite CR_HOTEL_HIST, CR_PROVIDER_HIST; sparkline BK al final
- `render_rnd_p1.py` — emite RND_HOTEL_HIST
- `assemble_unified.py` — lookup hotel→corp fallback, channel CR_PROVIDER_HIST, AR hotel view completo, KPI+wowbox update, +Area fallback
- `js_override.js` — elimina bloque HOTEL VIEW duplicado
- `SUPPLY_W25.html` — múltiples patches directos (sin re-pipeline disponible)

### Lecciones aprendidas
- **Cambios en `assemble_unified.py` no se reflejan en HTML existentes** — siempre aplicar también el patch directo al HTML cuando no hay pickles para regenerar.
- **Reorder de divs en HTML generado** — respetar la jerarquía de divs: un div con `net=1` (sin cierre propio) envuelve al siguiente elemento. Verificar siempre con conteo de opens/closes.
- **Dos listeners bubble en el mismo elemento** — el registrado primero en el tiempo gana. Si `assemble_unified.py` y `js_override.js` ambos escuchan el mismo click, el de assemble siempre ejecuta primero.
- **`CR_HOTEL_HIST` key format** — los nombres en el pool tienen prefijo `(ID) - Nombre` pero `build_hist_entity.py` ya los limpia. Los nombres en `hotels_br` de `CR_D` NO tienen el prefijo. El regex `replace(/^\(\d+\)\s*-\s*/, '')` es idempotente (no cambia si no hay prefijo).

### Cobertura histórica final W25
- Corp: 63 CR / 111 RND / 124 BK
- Dest: 1054 CR / 3052 RND / 2485 BK
- Hotel: 6024 CR / en pipeline RND (pendiente re-run)
- Provider/Channel: 10 CR (DerbySoft, SynXis, HBSI, Expedia, HotelBeds Apitude, Internal, Siteminder, Travelclick, Hotel Unico V2, Omnibees)

---

## Sesión W25-visual · 24-06-2026 (tarde)

### Contexto
Sesión de mejoras visuales sobre `SUPPLY_W25.html`. Pickles W25 disponibles en container. Clone fresco en `/home/claude/Price_fresh/`.

### Cambios aplicados y funcionando ✅

#### Channels — col TRX en 1 línea
- `52px/56px → 68px` en todos los `_mkHdr`/`_buildChanRow` de `js_override.js` y `render_cr_p1.py`
- Afecta: KPI EF channel, KPI CV channel, KPI BK channel, AR channel

#### AR BK card — sin WoW TRX
- Grid `5cols → 4cols` (nombre · TRX · BK% · WoW)
- Header: columna WoW TRX eliminada
- Filas: `wPill(_BK_TRX_WOW...)` eliminado
- `js_override.js`: `ar3_renderTable`

#### Severity RND — solo %NoDispo (sin IPM)
- `render_rnd_p2.py`: `render_severity()` → solo columna %NoDispo, eliminada columna IPM
- `assemble_unified.py`: CSS `body[data-ar-mode='rnd'] #kpicard-ar2 { display:none }` — AR2 oculto en RND

#### AR1 RND — sparkline side-by-side
- `assemble_unified.py`: `#ar1-body display:flex inline`, `#ar1-hist-cr-wrap` abajo (CR), `#ar1-hist-wrap` 210px al costado (RND, `display:none` por defecto)
- `demo_css_w22.css`: `body[data-ar-mode='rnd'] #ar1-hist-wrap { display:flex }` + oculta `ar1-hist-cr-wrap`

#### Excels mejorados
- `excel_rnd.py`: `write_nd_hotel()` con columnas Corp+Destino · nueva tab **AR Consolidado** (3 bandas top500) → 29 hojas
- `excel_cr.py`: nueva tab **AR Consolidado** (3 bandas top500 con Channel+Destino+Corp) → 29 hojas

#### SVG sparkline — overflow:hidden
- `render_historico_svg.py`: SVG `overflow:visible → overflow:hidden` + div container `overflow:hidden`
- Evita que el halo del último punto (`r=8`) desborde el contenedor

#### Pills dimensión — todas MAYÚSCULA
- `render_cr_p1.py` + `render_rnd_p1.py`: `text-transform:none → uppercase` en pills inactivas
- `assemble_unified.py`: `textTransform` siempre `'uppercase'` en `kpi_setView`

#### KPI NoDispo — layout restaurado a W24 original
- Después de múltiples iteraciones de rediseño (Opciones A/B/C, 2-zonas, 3-módulos) que no quedaron bien visualmente, se revirtió a `render_rnd_p1.py` del commit `b395672` (W24)
- Eliminada `render_kpi_card_rpm()` del script restaurado (IPM no se muestra en W25)
- Layout final: simple, `padding:12px 16px`, sin grid experimental

### Commits de la sesión (orden cronológico)
- `e47a3c80` — Opción B NoDispo (descartada) + channels 68px + severity sin IPM + AR1 side-by-side
- `3f2ad2a1` — Excels: Corp+Destino en hotels RND + AR Consolidado CR+RND
- `223601d4` — BK AR sin WoW TRX + AR1 side-by-side fix
- `18c9169` → múltiples commits de layout NoDispo (todos descartados)
- `705bd0d4` — Revert NoDispo a W24 original
- `b061aed` — Fix final: layout W24 sin IPM ✅

### Scripts modificados (estado final)
- `render_rnd_p1.py` — layout W24 restaurado, sin `render_kpi_card_rpm`
- `render_rnd_p2.py` — severity solo %NoDispo
- `render_cr_p1.py` — channels 68px, pills uppercase
- `js_override.js` — channels 68px, AR BK sin WoW TRX, AR2 oculto RND
- `assemble_unified.py` — AR1 side-by-side, CSS overrides
- `demo_css_w22.css` — AR1 RND CSS
- `render_historico_svg.py` — overflow:hidden
- `excel_rnd.py` — Corp+Destino en hotels, AR Consolidado
- `excel_cr.py` — AR Consolidado

### Lecciones aprendidas
- **Rediseño de cards complejas sin poder previsualizar** → siempre presentar opciones como HTML standalone primero, validar visualmente, y solo entonces tocar los scripts
- **`.kpi-card { padding:16px }` global** pisa cualquier `padding:0` inline → necesita `!important` o override por ID
- **`render_historico_svg.py` genera SVG con `overflow:visible`** → en contenedores angostos el halo del último punto desborda; fix: `overflow:hidden` en SVG y container
- **Restaurar desde commit específico** es más confiable que múltiples str_replace cuando el script tuvo demasiadas iteraciones

### Pendientes para próxima sesión
1. Re-run `calc_inv.py` W25 con dataset actualizado
2. Mail W25 final
3. Pipeline W26 normal
4. Cleanup código muerto (32 IDs huérfanos)
5. Rediseño card NoDispo (en sesión dedicada con HTML standalone)

---

## Sesión W25 · Inventory filter bug · 24-06-2026

### Contexto
Debug del módulo Inventory (INVENTORY_W25.html). Fede reportó que al seleccionar Región México en el widget de Distribución, la tabla de destinos no mostraba nada.

### Causa raíz
**Doble bug:**

1. **Normalización unicode corrupta** (ya había fix en `calc_inv.py` de sesión anterior, pero el HTML de W25 tenía versión vieja horneada): la función `_nr3` en `udSetDim` usaba `replace(/[\u0300-\u036f]/g,'')` pero los caracteres del rango estaban literalmente corruptos (NFD raw) por PowerShell al escribir el archivo → la regex no matcheaba nada → `_nr3('México') !== _nr3('México')` → filtro fallaba silenciosamente. Fix: reemplazar 6 ocurrencias corruptas por `charCodeAt(0)<0x0300` en el HTML parcheado.

2. **Bug en `hApplyFilter` línea 2548** (el bug real que bloqueaba la vista): incluso después de filtrar correctamente por región, la lógica hacía `r.style.display = (idx < 10 || isSel) ? '' : 'none'`. Los destinos de México empiezan en `idx=48`, por lo que todos quedaban ocultos. Fix: `r.style.display = (activeRegion || idx < 10 || isSel) ? '' : 'none'`

### Archivos modificados
- **`INVENTORY_W25.html`** — HTML parcheado directamente (6 normalizaciones corruptas + bug hApplyFilter línea 2548). No requiere regeneración desde calc_inv.py.
- **`calc_inv.py`** — Ya tenía la lógica correcta en su `hApplyFilter` (línea 2503 del script). No se modificó.

### Estado final
- ✅ Destinos de México visibles al seleccionar la región
- ✅ `calc_inv.py` ya tiene la lógica correcta para futuros builds
- El HTML parcheado es el entregable de esta sesión (no se commitó al repo — es un fix de emergencia sobre el HTML generado)

### Lecciones aprendidas
- **PowerShell corrompe rangos unicode NFD** en archivos escritos con `Out-File` → usar `[System.IO.File]::WriteAllText` o leer con `encoding='utf-8-sig'` en Python
- **`hApplyFilter` y `udSetDim` ambos operan sobre los dest-rows** — al agregar lógica de filtro por región en `udSetDim`, hay que asegurar que `hApplyFilter` también respeta la región al decidir qué filas mostrar (no solo aplicar el filtro de región sino también eliminar la restricción de `idx < 10`)
- Los destinos de México tienen `data-row-idx` 48+ (son los destinos 49-50 en el ranking global) — cualquier restricción de top-N sin excepción de región los oculta

### Pendientes
1. **Pipeline W26 normal** — próxima sesión
2. **Mail W26**
3. **Cleanup código muerto** (32 IDs huérfanos)
4. **Reconciliar `PROMPT_INV.md`** con valores W25 reales
5. **Rediseño card NoDispo** — sesión dedicada con HTML standalone
