# _scripts · Pipeline de generación de reportes

Pipeline Python para generar los Reportes Editoriales (HTML), Excels de Análisis, Hub index y ZIP de release a partir de los datasets crudos semanales.

---

## 📋 Inventario de archivos

### Cálculo y agregación
| Archivo | Función |
|---|---|
| `engine.py` | Funciones core: bandas (`banda_nodispo`, `banda_rpm`, `banda_eficacia`, `banda_convrate`), agregaciones, Pareto P80, channel grupo |
| `render_helpers.py` | Helpers de formato: `fmt_int_es`, `fmt_pct2`, `fmt_num2`, `fmt_big`, `clean_hotel_name`, `truncate`, `banda_pill`, `gauge_5levels`, `wow_box` |
| `calc_rnd.py` | Calcula métricas globales y por canasta RND → guarda `rnd_wNN_data.pkl` |
| `calc_cr.py` | Calcula métricas globales y por canasta CR → guarda `cr_wNN_data.pkl` |
| `areas_catalogo.py` | Catálogo Áreas Accountable v2 + función de mapeo |

### Renderers HTML por sección
| Archivo | Genera |
|---|---|
| `render_rnd_p1.py` | Masthead + Hero KPI + Alertas globales (RND) → `part1_rnd.html` |
| `render_rnd_p2.py` | Resumen Ejecutivo + Severity + Análisis por hotel + Dimensión (con módulos históricos) + Plan (RND) → `part2_rnd.html` |
| `render_rnd_p3.py` | Análisis por Canasta RND (B2B-OP · CUG · B2C) → `part3_rnd.html` |
| `render_cr_p1.py` | Masthead + Hero KPI Eficacia/ConvRate (CR) → `part1_cr.html` |
| `render_cr_p2.py` | Resumen Ejecutivo + Alertas + Severity + Análisis por hotel + Dimensión + Plan (CR) → `part2_cr.html` |
| `render_cr_p3.py` | Análisis por Canasta CR → `part3_cr.html` |

### Helpers de template
| Archivo | Función |
|---|---|
| `template_resumen.py` | `render_resumen_ejecutivo(findings, accent_color, scope, header_title)` |
| `template_alertas.py` | `render_alertas_block(scope_text, accent, card_h, card_d, card_c)` |
| `template_severity.py` | `render_severity_block(...)` + `render_severity_2cols(...)` + `LEVELS_*` predefinidos |
| `historico_module_v2.py` | `render_historico_cr(metric_type, banda_actual, val_actual, canvas_id, current_week)` — módulo Evolución Histórica para CheckRates (Eficacia + ConvRate) · usado en Hero, canastas, hotel, dim |
| `historico_module_rnd.py` | `render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id, current_week)` — módulo Evolución Histórica para RatesNoDispo (NoDispo + IPM) · usado en Hero, canastas, hotel, dim |

### Ensamblado y Excel
| Archivo | Genera |
|---|---|
| `assemble_rnd.py` | Une part1+part2+part3 RND + footer → `Supply_RatesNoDispo_WNN.html` |
| `assemble_cr.py` | Une part1+part2+part3 CR + footer → `Supply_CheckRates_WNN.html` |
| `excel_rnd.py` | 4 Excels RND (global 33 pests. + 3 canasta 8 pests. c/u) |
| `excel_cr.py` | 4 Excels CR (global 37 pests. + 3 canasta 9 pests. c/u) |

### Mail, hub y package
| Archivo | Genera |
|---|---|
| `render_mail_v3.py` | Mail semanal HTML (`Mail_WNN.html`) |
| `build_package.py` | **index.html del hub** + ZIP con estructura completa del repo listo para commit |

---

---

## 📈 Módulos Históricos · Evolución Semanal (W20+)

Bloque HTML+JS reactivo que muestra la tendencia de 8 semanas de una métrica dentro de cada card KPI.

### Cobertura (12 módulos por reporte tras sesión 4)

| Scope | CR (Eficacia + ConvRate) | RND (NoDispo + IPM) |
|---|---|---|
| **Global** (Hero) | `hcr-global-ef` · `hcr-global-cv` | `hrnd-global-nd` · `hrnd-global-ipm` |
| **B2B-OP** (canasta) | `hcr-op-ef` · `hcr-op-cv` | `hrnd-op-nd` · `hrnd-op-ipm` |
| **CUG** (canasta) | `hcr-cug-ef` · `hcr-cug-cv` | `hrnd-cug-nd` · `hrnd-cug-ipm` |
| **B2C** (canasta) | `hcr-b2c-ef` · `hcr-b2c-cv` | `hrnd-b2c-nd` · `hrnd-b2c-ipm` |
| **Análisis por hotel** | `hcr-hotel-ef` · `hcr-hotel-cv` ✅ W20s4 | `hrnd-hotel-nd` · `hrnd-hotel-ipm` |
| **Análisis por dimensión** | `hcr-dim-ef` · `hcr-dim-cv` ✅ W20s4 | `hrnd-dim-nd` · `hrnd-dim-ipm` |

### Componentes de cada módulo

- **Canvas** — curva de tendencia con escala LOCAL al elemento, target line, labels X dinámicos
- **5 métricas** — Actual · Máx 8W · Mín 8W · Prom 8W · Banda
- **Sparkline** — 8 barras en escala GLOBAL vs target
- **Interactividad** — click en cualquier fila de la tabla actualiza canvas, métricas y banda

### Uso en render scripts

```python
from historico_module_v2 import render_historico_cr

hist_html = render_historico_cr(
    metric_type='eficacia',   # 'eficacia' | 'convrate'
    banda_actual='Exitosa',
    val_actual=0.9740,        # float [0,1] para eficacia; float % para convrate
    canvas_id='hcr-global-ef',
    current_week='W20'        # ← SIEMPRE la semana actual, nunca la próxima
)
```

```python
from historico_module_rnd import render_historico_rnd

hist_html = render_historico_rnd(
    metric_type='nodispo',    # 'nodispo' | 'ipm'
    banda_actual='Revisar',
    val_actual=0.0820,        # float [0,1] para nodispo; float USD/M para ipm
    canvas_id='hrnd-global-nd',
    current_week='W20'        # ← SIEMPRE la semana actual, nunca la próxima
)
```

### Wrapper de sección (Análisis por hotel + Análisis por dimensión)

Para las secciones que necesitan 2 módulos lado a lado (Eficacia + ConvRate, o NoDispo + IPM), existe un wrapper que conecta los clicks de filas con eventos custom:

```python
# CR (en render_cr_p2.py)
hist_section_cr = render_historico_seccion_cr(
    canvas_id_ef='hcr-hotel-ef',
    canvas_id_cv='hcr-hotel-cv',
    banda_ef=..., val_ef=...,
    banda_cv=..., val_cv=...,
)

# RND (en render_rnd_p2.py)
hist_section_rnd = render_historico_seccion_rnd(
    canvas_id_nd='hrnd-hotel-nd',
    canvas_id_ipm='hrnd-hotel-ipm',
    banda_nd=..., val_nd=...,
    banda_ipm=..., val_ipm=...,
)
```

Los módulos escuchan eventos `hist-update` y `hist-reset` disparados por el wrapper externo cuando el usuario clickea una fila con atributos `data-hist-*`.

### Ventana histórica · 5 semanas reales (post W20 sesión 6)

Los módulos históricos usan una **ventana fija de 5 semanas reales** definida en `_scripts/historico_data.py`:

```python
SEMANAS = ['W16', 'W17', 'W18', 'W19', 'W20']  # ventana actual
```

**Decisión de diseño:** se prefirió 5 semanas reales antes que 8 con ficticios marcados. Razón: datos auditables en un reporte de decisión > más puntos en la curva.

**Plan de evolución (cómo extender la ventana cuando lleguen W21+):**

| Semana actual | Acción | Ventana final |
|---|---|---|
| **W21** (próxima) | Editar `historico_data.HIST_DATA`: agregar valor W20 a cada array, renombrar `SEMANAS` a `[W16..W21]` | 6 semanas |
| **W22** | Idem · agregar W21 a HIST_DATA · SEMANAS = `[W16..W22]` | 7 semanas |
| **W23** | Idem · agregar W22 · SEMANAS = `[W16..W23]` | **8 semanas reales** |
| **W24+** | Ventana móvil de 8: descartar la semana más antigua y agregar la nueva | 8 semanas reales |

**Para extraer los datos de cada semana nueva**, ejecutar `calc_cr.py` y `calc_rnd.py` con la semana correspondiente y leer del pickle:
- CR: `M['global_w{N}']['eficacia']` y `['conv_rate']` (multiplicar por 100)
- RND: `M['global_w{N}']['pct_nodispo']` (multiplicar por 100) y calcular IPM = `gb_usd / trafico * 1M`
- Repetir para canastas: `M['B2B (OP)_w{N}']`, `M['CUG (UOP)_w{N}']`, `M['B2C_w{N}']`

**Util pendiente** (no urgente): `extract_hist_data.py` que automatice este append leyendo todos los pickles W16-W{current}.

**val_actual conceptual:** desde sesión 6, `val_actual` que reciben los módulos históricos es el valor de la **semana ACTUAL** del reporte (no la próxima). El módulo lo agrega como último punto de la serie automáticamente.

**Gauge de 5 niveles:** todas las barras `height:6px · opacity:1` — colores sólidos puros, grosor uniforme. La banda activa se identifica por la pill encima, no por el gauge.

### Estilo de badges severity (post W20 sesión 4)

Todos los badges del sistema usan el **estilo Opción D**:
- `font-size: 13px` (canastas: 11px)
- `padding: 10px 22px`
- `border: 1px solid {bd}`
- `text-transform: uppercase`
- `text-align: center`

El texto del badge es **solo el nombre de la banda en mayúsculas**. El target se muestra como caption gris separado debajo, vía `target_caption()` en `render_helpers.py`.

Ver `_docs/BANDAS.md` para la paleta D completa y todos los detalles del sistema.

---

## 🔍 Searchbox cliente-side (post W20 sesión 5)

Filtro instantáneo en todas las tablas del reporte. **18 searchboxes funcionales** (9 por reporte).

### Cobertura

| Sección | CR | RND |
|---|---|---|
| Hero KPI cards | ✅ 1 | ✅ 1 |
| Análisis por hotel | ✅ 1 | ✅ 1 |
| Análisis por dimensión | ✅ 1 | ✅ 1 |
| Canastas (B2C/OP/CUG × hotel+dim) | ✅ 6 | ✅ 6 |

### Comportamiento

- **Filtrado instantáneo cliente-side** (event `input`)
- **Case-insensitive y sin acentos** vía `String.prototype.normalize('NFD')` — `"cancun"` matchea `"Cancún"`
- **Contador** dinámico: `"X de Y visibles"` al filtrar, `"Y filas"` en estado base
- Color focus por reporte: **magenta** RND (`#EA0074`), **violet** CR (`#5C469C`)
- Búsqueda solo en la **primera columna** (nombre del hotel/destino/corp/channel) vía atributo `data-hist-label` en cada fila

### Arquitectura

| Componente | Ubicación |
|---|---|
| Helper Python (render del input + counter) | `_scripts/render_helpers.py::searchbox_html(input_id, scope_selector, placeholder)` |
| CSS + JS auto-attach | `_scripts/asset_cr_head.html` y `_scripts/asset_rnd_head.html` |
| Función JS principal | `window.attachSearchbox(scopeSelector, inputId, counterId)` |
| Atributo en cada fila filtrable | `data-hist-label="{nombre}"` |

### Cómo agregar un searchbox nuevo

```python
# En cualquier render script
from render_helpers import searchbox_html

html = f'''
<div id="mi-seccion">
  {searchbox_html('sb-mi-seccion', '#mi-seccion', 'Buscar...')}
  <table>...</table>  <!-- filas con data-hist-label="..." -->
</div>
'''
```

El JS de `asset_*_head.html` detecta automáticamente todos los `.sb-input[data-sb-scope]` al cargar la página.

---

## 🚀 FLUJO EJECUTABLE W21+ · 1 COMANDO (NUEVO - Mayo 2026)

### ✨ Pipeline automatizado con YAML

**ANTES (W20):** Editar scripts + ejecutar 6 pasos manualmente (35 min)  
**AHORA (W21+):** 1 comando automático (20 min)

```bash
# Setup (2 min)
cp WEEK_CONFIG_W20.yml WEEK_CONFIG_W21.yml
vim WEEK_CONFIG_W21.yml  # Cambiar: week, vol_num, periodo, fecha_pub, week_prev, periodo_prev, week_prev2

# Ejecutar (15 min · completamente automático)
python3 run_pipeline.py WEEK_CONFIG_W21.yml

# Output
✅ PIPELINE COMPLETADO EXITOSAMENTE
   ZIP: /mnt/user-data/outputs/Price_W21.zip
   Log: /mnt/user-data/outputs/pipeline_W21_run_*.log
   Summary: /mnt/user-data/outputs/pipeline_W21_summary.json
```

### Cómo funciona

1. **run_pipeline.py** lee `WEEK_CONFIG_W21.yml`
2. Inyecta variables de entorno: `WEEK`, `VOL_NUM`, `PERIODO`, `PICKLE_RND`, `PICKLE_CR`, etc.
3. Ejecuta 6 pasos en secuencia:
   - Validación pre-ejecución (verifica 4 datasets)
   - `calc_rnd.py` + `calc_cr.py` (cálculos)
   - `render_*_p*.py` (rendering HTML)
   - `assemble_*.py` (ensamble)
   - `excel_*.py` (Excels)
   - `render_mail_v3.py` + `build_package.py` (mail + hub + ZIP)
4. Genera logs detallados + resumen JSON
5. **Listo para GitHub commit**

---

## 🚀 Pipeline clásico (manual, si necesitas)

```bash
# CONFIG en cada script: cambiar WEEK, PERIODO, PICKLE_* al inicio de cada archivo

# 1. Cálculo · genera pickles con métricas y WoW
python calc_rnd.py       # → rnd_wNN_data.pkl
python calc_cr.py        # → cr_wNN_data.pkl

# 2. Renderers · genera parciales HTML
python render_rnd_p1.py  # → part1_rnd.html
python render_rnd_p2.py  # → part2_rnd.html
python render_rnd_p3.py  # → part3_rnd.html
python render_cr_p1.py   # → part1_cr.html
python render_cr_p2.py   # → part2_cr.html
python render_cr_p3.py   # → part3_cr.html

# 3. Ensamblado · une parciales en reportes finales
python assemble_rnd.py   # → RatesNoDispo_Reporte_Editorial.html
python assemble_cr.py    # → CheckRates_Reporte_Editorial.html

# 4. Excel · genera 4 archivos por reporte (8 total)
python excel_rnd.py      # → Analisis_Rates_NoDispo_7d.xlsx + 3 canasta
python excel_cr.py       # → Analisis_Checkrates_7d.xlsx + 3 canasta

# 5. Mail
python render_mail_v3.py # → Mail_WNN.html

# 6. Hub + ZIP
python build_package.py  # → index.html + Price_WNN.zip
```

> **Paso 6 es el paso final obligatorio.** Genera el `index.html` del hub con KPIs y severity pills extraídos automáticamente del pickle, y empaqueta todos los archivos en el ZIP con la estructura correcta del repo lista para commit.

---

## 🗂 Estructura del ZIP generado por build_package.py

```
Price_WNN/
├── index.html                                      ← hub actualizado (raíz del repo)
├── checkrates/
│   └── week-NN/
│       ├── CheckRates_Reporte_Editorial.html
│       ├── Analisis_Checkrates_7d.xlsx             (37 pestañas)
│       ├── Analisis_Checkrates_B2C_7d.xlsx         (9 pestañas)
│       ├── Analisis_Checkrates_OP_7d.xlsx          (9 pestañas)
│       └── Analisis_Checkrates_CUG_7d.xlsx         (9 pestañas)
├── rates-nodispo/
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx          (33 pestañas)
│       ├── Analisis_Rates_NoDispo_B2C_7d.xlsx      (8 pestañas)
│       ├── Analisis_Rates_NoDispo_OP_7d.xlsx       (8 pestañas)
│       └── Analisis_Rates_NoDispo_CUG_7d.xlsx      (8 pestañas)
└── _email/
    └── week-NN/
        └── Mail_WNN.html
```

---

## ⚙️ CONFIG SEMANAL · qué cambiar en cada script

Cada script tiene un bloque `# ── CONFIG SEMANAL ──` al tope. Solo hay que editar esas variables:

| Script | Variables a cambiar |
|---|---|
| `calc_rnd.py` | Rutas de archivos Excel W(N) y W(N-1) |
| `calc_cr.py` | `WEEK`, `PERIODO`, `MES_AÑO`, `VOL_NUM`, rutas Excel |
| `render_mail_v3.py` | `WEEK`, `PERIODO`, `VOL_NUM`, `PICKLE_RND`, `PICKLE_CR`, `OUT_FILE` |
| `build_package.py` | `WEEK`, `PERIODO`, `FECHA_PUB`, `WEEK_PREV`, `PERIODO_PREV`, `PICKLE_RND`, `PICKLE_CR` |

Los demás scripts (`render_*.py`, `assemble_*.py`, `excel_*.py`) detectan el pickle automáticamente — no requieren cambios de semana en semana.

---

## 🌐 Hub · index.html

El `index.html` se genera **automáticamente** en `build_package.py`. Lo que hace:

1. Lee los pickles `rnd_wNN_data.pkl` y `cr_wNN_data.pkl`
2. Extrae KPIs, WoW, bandas y severity counts
3. Genera HTML con:
   - **Card featured** (semana actual): KPI strip 4 métricas + severity pills RND y CR + links a reportes y Excels
   - **Historial** (semana anterior): KPIs compactos + links
   - Login overlay con credenciales `pricetravel` / `supply2026`
4. Escribe `index.html` en `/mnt/user-data/outputs/`
5. Lo incluye en la raíz del ZIP

**Nunca editar `index.html` manualmente** — se sobreescribe en cada ejecución de `build_package.py`.

---

## ⚠️ Reglas para mantener consistencia

### Cuando se modifica una banda:
1. Actualizar `engine.py`
2. Actualizar `excel_*.py` (etiquetas de rango en pestañas Severity)
3. Actualizar `template_severity.py` (constantes `LEVELS_*`)
4. Actualizar `_docs/BANDAS.md`
5. Re-correr todo el pipeline desde `calc_*.py`

### Cuando se modifica el catálogo de Áreas:
1. Actualizar `areas_catalogo.py`
2. Actualizar `render_*_p2.py` y `render_*_p3.py`
3. Actualizar `_docs/AREAS_ACCOUNTABLE.md`

### Cuando se modifica la estructura editorial:
1. Extraer snippet literal del template
2. Actualizar el helper en `template_*.py` (si aplica)
3. Actualizar el renderer correspondiente
4. Actualizar `_docs/ESTRUCTURA_TEMPLATE.md`

### Cuando se modifica el hub:
1. Editar `build_package.py` (función `build_index()`)
2. Actualizar `_docs/MAPA_DEPENDENCIAS.md` (sección Hub)
3. Nunca editar `index.html` directamente — siempre vía `build_package.py`

---

## 📁 Archivos generados (no commitear directamente)

```
_scripts/
├── *_wNN_data.pkl          # pickles intermedios
├── part1_*.html            # parciales
├── part2_*.html
└── part3_*.html

/mnt/user-data/outputs/     # outputs finales → van al ZIP
├── Supply_CheckRates_WNN.html
├── Supply_RatesNoDispo_WNN.html
├── Analisis_Checkrates_7d.xlsx  (+ B2C/OP/CUG)
├── Analisis_Rates_NoDispo_7d.xlsx  (+ B2C/OP/CUG)
├── Mail_WNN.html
├── index.html              ← generado por build_package.py
└── Price_WNN.zip           ← ZIP final para commit
```


## Bugs críticos a recordar para W20+

- **`calc_rnd.py` CONFIG SEMANAL**: cambiar `df18` → W(N) y `df17` → W(N-1). Si ambos apuntan al mismo archivo el WoW es todo cero (Bug #19).
- **`calc_cr.py` CONFIG SEMANAL**: `df18` → W(N), `df17` → W(N-1). El pickle se llama `cr_wNN_data.pkl`.
- **Header masthead** toma `VOL_NUM` del pickle — no hay que tocarlo manualmente.
- **plan_seguimiento** se genera en `_seguimiento/` — editar antes del pipeline para mover QW resueltos a `## CERRADO`.

---

## 📊 Módulo Histórico · `historico_module_v2.py` (Mayo 2026)

Nuevo helper compartido que genera el bloque **"Evolución Histórica"** reactivo.

```
historico_module_v2.py   ← NUEVO · importado por render_cr_p1.py y render_cr_p3.py
```

### Función principal
```python
render_historico_cr(metric_type, banda_actual, val_actual, canvas_id,
                    hist_vals=None, global_ceil=None)
```

| Parámetro | Descripción |
|---|---|
| `metric_type` | `'eficacia'` \| `'convrate'` |
| `banda_actual` | String banda sistema D |
| `val_actual` | Float [0,1] — valor semana actual |
| `canvas_id` | ID único del canvas (ej: `'hcr-global-ef'`, `'hcr-op-cv'`) |
| `hist_vals` | Lista 7 floats W14-W20 en % (None = ficticios por scope) |
| `global_ceil` | Techo para barras sparkline (default = target de la métrica) |

### Lógica diferenciada curva vs barras
| Elemento | Escala | Muestra |
|---|---|---|
| Canvas (curva) | Local del elemento | Forma del trend — sube/baja/volátil |
| Sparkline (barras) | Global vs `global_ceil` | Severidad relativa al target |

### Interactividad
Cada row del tab lleva `data-hist-w21`, `data-hist-w20`, `data-hist-label`.
Click → el JS del módulo reconstruye la serie y redibuja sin recargar.

### Scope del canvas_id
El scope (global/op/cug/b2c) se infiere automáticamente del `canvas_id`:
- Contiene `'op'` → datos ficticios B2B-OP
- Contiene `'cug'` → datos ficticios CUG
- Contiene `'b2c'` → datos ficticios B2C
- Ninguno → datos ficticios global

---

**Última actualización:** Mayo 2026 · post W20 · historico_module_v2.py agregado

---

## 📊 Módulo Histórico CR · `historico_module_v2.py` (Mayo 2026)

```
historico_module_v2.py   ← NUEVO · importado por render_cr_p1.py y render_cr_p3.py
```

### Función principal
```python
render_historico_cr(metric_type, banda_actual, val_actual, canvas_id,
                    hist_vals=None, global_ceil=None)
```

| Parámetro | Descripción |
|---|---|
| `metric_type` | `'eficacia'` \| `'convrate'` |
| `banda_actual` | String banda sistema D |
| `val_actual` | Float [0,1] — valor semana actual |
| `canvas_id` | ID único (ej: `'hcr-global-ef'`, `'hcr-op-cv'`) |
| `hist_vals` | Lista 7 floats W14-W20 en % (None = ficticios por scope) |
| `global_ceil` | Techo sparkline (default = target de la métrica) |

### Lógica diferenciada curva vs barras
| Elemento | Escala | Muestra |
|---|---|---|
| Canvas (curva) | Local del elemento | Forma del trend — sube/baja/volátil |
| Sparkline (barras) | Global vs `global_ceil` | Severidad relativa al target |

---

## 📊 Módulo Histórico RND · `historico_module_rnd.py` (Mayo 2026)

```
historico_module_rnd.py   ← NUEVO · importado por render_rnd_p1.py y render_rnd_p3.py
```

### Función principal
```python
render_historico_rnd(metric_type, banda_actual, val_actual, canvas_id,
                     hist_vals=None, global_ceil=None)
```

| Parámetro | Descripción |
|---|---|
| `metric_type` | `'nodispo'` \| `'ipm'` |
| `banda_actual` | String banda sistema D |
| `val_actual` | Float [0,1] para nodispo · USD/M para ipm |
| `canvas_id` | ID único (ej: `'hrnd-global-nd'`, `'hrnd-op-ipm'`) |
| `hist_vals` | Lista 7 floats W14-W20 (None = ficticios por scope) |
| `global_ceil` | Techo sparkline (default: 0.60 nodispo · 3000 ipm) |

### Diferencias vs módulo CR
| Aspecto | CR | RND |
|---|---|---|
| Métricas | Eficacia / ConvRate | NoDispo / IPM |
| Escala NoDispo | N/A | Invertida — menor = mejor |
| Accent | `#5C469C` violet | `#EA0074` magenta · `#A86A1D` amber |
| W20 elemento | `Eficacia_W17` / `ConvRate_W17` | `NoDispo_W17` / `IPM_W18` |
| Mejor | Máx verde · Mín rojo | NoDispo: Mín verde · IPM: Máx verde |
| Label target | Dibujado en canvas | HTML posicionado sobre canvas |

---

## 📊 Estado módulos históricos W20

| Sección | CR | RND |
|---|---|---|
| Cards KPI Severity (hero) | ✅ | ✅ |
| Cards KPI canastas | ✅ | ✅ |
| Análisis por Hotel | ✅ `hcr-hotel-ef` · `hcr-hotel-cv` (W20s4) | ✅ `hrnd-hotel-nd` · `hrnd-hotel-ipm` |
| Análisis por Dimensión | ✅ `hcr-dim-ef` · `hcr-dim-cv` (W20s4) | ✅ `hrnd-dim-nd` · `hrnd-dim-ipm` |

## 🎨 Colores accent por métrica

| Reporte | Métrica | Accent canvas |
|---|---|---|
| CR | Eficacia | `#EA0074` magenta |
| CR | ConvRate | `#5C469C` violet |
| RND | NoDispo | `#EA0074` magenta |
| RND | IPM | `#4FC3F4` cyan corporativo (Arctic Blue) |

> **Cyan `#4FC3F4` se usa SOLO en 2 lugares:**
> 1. Accent IPM en módulos históricos RND (`IPM_ACCENT` en `historico_module_rnd.py`)
> 2. Label "🔌 Third Party" en sección por channel CR (`render_cr_p1.py`)
>
> En todo el resto del sistema: **Exitosa = `#085041` verde teal** (variable CSS `--green`).

## 📐 Gauge 5 niveles — regla definitiva

Todas las barras: `height:6px · opacity:1` — colores sólidos puros, grosor uniforme.  
Sin transparencia. La banda activa se identifica por la pill encima, no por el gauge.

## 🏷️ Estilo de badges severity (post W20 sesión 4)

**Estilo Opción D** aplicado uniformemente a TODOS los badges:
- `font-size: 13px` (canastas: 11px)
- `padding: 10px 22px` · `border-radius: 3px`
- `border: 1px solid {bd}` · `text-align: center`
- `text-transform: uppercase` · solo el nombre de la banda
- Target X% como caption gris **separado** debajo (vía `target_caption()` helper)

Ver `_docs/BANDAS.md` para la paleta D completa, los thresholds por métrica y los archivos canónicos.

---

**Última actualización:** Mayo 2026 · post W20 sesión 4 · módulo histórico CR hotel+dim ✅ · badges Opción D · paleta D · target caption separado del badge

