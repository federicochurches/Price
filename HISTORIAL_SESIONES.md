# 📚 HISTORIAL DE SESIONES · Proyecto PRICE
**Arqueología de sesiones W16-W20 · Solo consultar ante bugs misteriosos o decisiones de contexto histórico**

> Este archivo NO se necesita para ejecutar el pipeline semanal.
> Para el contexto operativo vigente → ver `PROMPT_CORE.md`.

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

## Panel AR CR/RND — searchbox + 1000 rows + fixes JS · 05 Jun 2026

### Contexto
Bug detectado por Federico: Excel CR/RND cargaba los mismos hoteles en todas las pestañas.
Panel AR de CR sin searchbox, rows 6-10 no clickeables, selección se perdía al cambiar pestaña.

### Bug cerrado — Excel CR/RND pestañas repetidas (P12)
- **Causa:** `TAB_NoDispo`/`TAB_RPM` son estructuras globales en `excel_rnd.py`. El loop de
  canastas las usaba sin filtrar → País/Dest/Corp/Dim mostraban datos globales en B2C, Opaco y CUG.
- **Fix (`excel_rnd.py`):** En cada iteración, detectar `can_id is None` (Global) vs canasta
  específica. Para canastas: usar `can.get('agg_pais')`, `can.get('agg_dest')`, `can.get('agg_corp')`
  del pickle (ya calculados por canasta en `calc_rnd.py`). Las hojas Dim también corregidas.
- **CR no tenía el bug** — `TAB_EF_BY_CANASTA`/`TAB_CV_BY_CANASTA` ya filtraban por `can_key`.

### 1.000 rows por pestaña (antes 100)
Todos los `head(100)` subidos a `head(1000)` en:
- `render_cr_p2.py` — tabs Críticos, BR, Sin Conv, Menor CV + dims Corp y Dest
- `render_rnd_p2.py` — todos los tabs del panel AR
- `render_rnd_p3.py` — cards KPI de canastas (dest, corp, hotel, pais, rpm)
- `excel_cr.py` — función `write_combined`
- `excel_rnd.py` — funciones `write_nd` y `write_ipm`

### Fix 1 — Searchbox panel AR (`render_cr_p2.py` + `js_override.js`)
- HTML del searchbox (dos pills: `sb-panel-th` y `sb-panel-td`) inyectado directamente
  en `render_analisis_rendimiento()`, encima de cada tabla `w22-th` y `w22-td`.
- Handler JS propio `initPanelSearch()` en `js_override.js` — no usa `attachPill` de
  `asset_shared_head.html` (requiere `.kpi-card`/`.canasta-block` que el panel AR no tiene).
- Filtra por `[data-hist-label]` en el tbody activo. Se limpia al cambiar tab.
- Se re-inicializa al cambiar canasta o modo CR↔RND.

### Fix 2 — Rows 6-1000 clickeables (`js_override.js`)
- `_injectHistAttrs` solo inyectaba `data-hist-w21` en el render inicial.
  Rows con clase `rows-more` no tenían el atributo → click listener no disparaba.
- Fix: patch de `_moreBtn` que agrega inyección de attrs al expandir, usando
  `_lastRows` guardado en cada `w22_renderTable`.

### Fix 3 — Persistencia selección entre pestañas (`js_override.js`)
- Al cambiar de pestaña (Críticos → Bajo Rendimiento), `w22_renderTable` re-escribe
  el tbody y perdía el highlight del hotel seleccionado.
- Fix: `_selectedPanelLabel` guarda el label seleccionado. Cada `w22_renderTable` re-aplica
  el highlight si el label existe en los nuevos rows. Segundo click o cambio de canasta/modo limpia.

### Archivos modificados
`excel_rnd.py` · `excel_cr.py` · `render_cr_p2.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `js_override.js`

### Pendientes W23
- Aplicar mismos fixes de searchbox + 1000 rows al panel AR de RND (si lo tiene)
- `extract_hist_data.py` sigue pendiente (P5)

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
