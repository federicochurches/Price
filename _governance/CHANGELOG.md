# CHANGELOG · Proyecto PRICE · Supply Analytics

---

## Week 19 · Mayo 2026

### ✨ Nuevas features

#### Hub index.html integrado al pipeline como Paso 6
- **`build_package.py` reescrito** — ahora es el Paso 6 obligatorio del pipeline semanal
- Genera `index.html` del hub **automáticamente** a partir de los pickles (`rnd_wNN_data.pkl` + `cr_wNN_data.pkl`)
- El HTML del hub incluye:
  - Login overlay con credenciales (sessionStorage · no persiste entre sesiones)
  - **Card featured** (semana actual): KPI strip 4 métricas (% NoDispo · IPM · Eficacia · Conv Rate) con bandas y WoW calculados desde pickle
  - **Severity pills** RND y CR con counts exactos del P80
  - Links directos a reportes editoriales y Excels globales
  - **Card historial** (semana anterior): KPIs compactos desde W(N-1) del pickle + links
- `index.html` **nunca se edita manualmente** — siempre se regenera con `build_package.py`
- `index.html` se incluye en la raíz del ZIP de release

#### ZIP con estructura completa del repo
- `build_package.py` genera `Price_WNN.zip` con la estructura exacta del repo:
  ```
  Price_WNN/
  ├── index.html
  ├── checkrates/week-NN/  (5 archivos)
  ├── rates-nodispo/week-NN/  (5 archivos)
  └── _email/week-NN/Mail_WNN.html
  ```
- El ZIP es el único deliverable para commit — no hay que mover archivos manualmente

### 🔧 Fixes

#### render_mail_v3.py — eliminada dependencia de metrics_recalc.pkl
- `metrics_recalc.pkl` nunca existió en el pipeline normal — causaba error en cada ejecución
- IPM y GBM ahora derivados directamente de `rnd_wNN_data.pkl` (`M['global_w18']['ipm']` y `M['global_w18']['gb_usd']`)
- Bloque `# CONFIG SEMANAL` al tope del archivo — solo cambiar 6 variables por semana
- Marcadores `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->` para el comando de draft Gmail
- Renombrado internamente RPM → IPM en el cuerpo del mail

#### excel_rnd.py — path del pickle corregido
- Tenía hardcodeado `/home/claude/final_w18/rnd_w18_data.pkl` → corregido a ruta relativa `rnd_wNN_data.pkl`

### 📝 Dataset W19 RND — incidencia y resolución
- Primera versión del dataset llegó con solo 5 columnas (faltaban `CorpName`, `PaisDestino`, `Destino`, `gb_usd`)
- Resolución: se solicitó dataset corregido al equipo de Data
- Segunda versión completa con 9 columnas, 157.994 filas, 0 nulls
- 8.581 filas con `DistributionCategory` = `-` o `HTML` (< 0.2% del tráfico) — filtradas automáticamente por el pipeline
- **Documentado para W20+:** validar columnas del dataset RND antes de correr el pipeline

### 📊 KPIs W19
| Métrica | W19 | WoW |
|---|---|---|
| % NoDispo (global P80) | 2,42% | ▼ 0,03pp |
| IPM (global P80) | $597 | ▼ 7,4% |
| Eficacia CR (global P80) | 93,88% | ▼ 0,25pp |
| Conv Rate CR (global P80) | 1,32% | ▲ 0,05pp |

### 🗂 Archivos modificados / creados
| Archivo | Cambio |
|---|---|
| `build_package.py` | Reescrito · genera index.html + ZIP · Paso 6 obligatorio |
| `render_mail_v3.py` | v3.2 · sin metrics_recalc.pkl · CONFIG SEMANAL · IPM |
| `excel_rnd.py` | Fix path pickle |
| `README.md` | Pipeline actualizado con Paso 6 · sección Hub · estructura ZIP |
| `CHECKLIST_PROYECTO_CLAUDE.md` | build_package.py como Paso 6 · 42 archivos esperados |
| `MAPA_DEPENDENCIAS.md` | Sección Hub expandida · reglas build_package.py |
| `CHANGELOG.md` | Este archivo |

---

## Week 18 · Mayo 2026 · sesión validación visual CR + RND completo

### 🐛 Bugs corregidos (CR)
- **Bug #8:** `_WOW_NEUTRO` como string literal en `_render_dim_table` en vez de variable
- **Bug #9:** `g_channel_w17` no disponible dentro de funciones de render — fix: cargar explícitamente al nivel de módulo en `render_cr_p2.py`
- **Bug #10:** verificado que `sin_conv` tiene `Eficacia_WoW_pp` correctamente

### 🐛 Bugs corregidos (RND)
- **Bug #11:** `TAB_RPM` con `IPM=0` — fix: `min_ipm=True` en `make_tab()`
- **Bug #12:** Corps con tráfico <500K con NoDispo extrema — fix: `MIN_T=500_000`
- **Bug #13:** `panel-header` 3 cols vs `panel-row` 4 cols — fix: unificar a `1fr 62px 62px 46px`
- **Bug #14:** Regla CSS pintaba todos los nombres en magenta — fix: `.tab-panel div span.tab-val`
- **Bug #15:** Métricas globales calculadas sobre `df18` completo — fix: usar `p80_hotel`

### ✨ Nuevas features (CR)
- Pills WoW neutras con `_WOW_NEUTRO` visual (bg #F2EEE6 · color muted)
- Channel hero 100% eficacia: pill verde `= 0,0`
- Color Third Party: cyan → violet en dimensión global y canastas
- WoW en Análisis por Hotel canasta (4 cols: Hotel · ConvRate · Eficacia · WoW)
- WoW en Channel dimensión (global y canasta)
- Normalización destinos con `_CITY_DASH_PATTERN`
- RE margin-top reducido: 64px→24px global · 32px→16px canasta
- Fondos unificados: `--paper-soft: #F2EDE0` · tabs-block `var(--paper)`

### ✨ Nuevas features (RND)
- `calc_rnd.py` reescrito: lee Excel directamente, P80 consistente en todas las dimensiones
- WoW real en tabs globales y canasta
- `MIN_T = 500_000` en tabs de dimensión
- 4 cols en `panel-row` (Nombre · %NoDispo · IPM · WoW)
- `section-title` negro (no hereda magenta)

### 📁 Archivos modificados
`render_cr_p1.py` · `render_cr_p2.py` · `render_cr_p3.py` · `render_rnd_p1.py` · `render_rnd_p2.py` · `render_rnd_p3.py` · `calc_rnd.py` · `calc_cr.py` · `render_helpers.py` · `template_resumen.py` · `template_alertas.py` · `asset_cr_head.html` · `asset_rnd_head.html`

### 🗂 Optimización proyecto Claude
- Eliminados `_TEMPLATE_CheckRates_Reporte.html` + `_TEMPLATE_RatesNoDispo_Reporte.html` + 4 snippets (~722KB)
- CHECKLIST: 51 → 41 archivos esperados

---

## Week 17 · Abril 2026

(no aplicaba changelog formal)

- Sistema de bandas D introducido
- Sin Conversión separada como cohorte aparte
- Pills Súper Crítica con transparencia 80%
- Channel agrupado en CR (Producto Propio vs Third Party)
- Tabs hero estilo folder

---

## 🆕 Mejora · Reorganización secciones globales (post Week 18)

**Fecha:** 5 mayo 2026

### Antes
6 secciones globales apiladas en cada reporte.

### Ahora
2 bloques con tabs por reporte:

**RND:**
- Sección 03 · Análisis por hotel · 3 tabs (Demanda NC · Bajo Rend · Sin Conv)
- Sección 04 · Por dimensión · 3 tabs (Corp · Destino · País)

**CR:**
- Sección 04 · Análisis por hotel · 4 tabs (Críticos · Bajo Rend · Sin Conv · Menor ConvRate)
- Sección 05 · Por dimensión · 3 tabs (Corp · Destino · Channel con split PP/TP)

### CSS clave aprendido
La regla `.tab-panel{display:none}` del CSS hero original tiene la misma especificidad que `:checked ~ .tab-panels .tab-panel{display:block}`. Solución: prefijar con `.tabs-block` + `!important`. Documentado en ESTRUCTURA_TEMPLATE.md.
