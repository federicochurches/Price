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
| `render_rnd_p2.py` | Resumen Ejecutivo + Severity + Análisis por hotel + Dimensión + Plan (RND) → `part2_rnd.html` |
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

## 🚀 Pipeline semanal · orden de ejecución

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
python assemble_rnd.py   # → Supply_RatesNoDispo_WNN.html
python assemble_cr.py    # → Supply_CheckRates_WNN.html

# 4. Excel · genera 4 archivos por reporte (8 total)
python excel_rnd.py      # → Analisis_Rates_NoDispo_7d.xlsx + 3 canasta
python excel_cr.py       # → Analisis_Checkrates_7d.xlsx + 3 canasta

# 5. Mail
python render_mail_v3.py # → Mail_WNN.html

# 6. Hub + ZIP · NUEVO desde W19
python build_package.py  # → index.html (hub actualizado) + Price_WNN.zip
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
4. Actualizar `_governance/BANDAS.md`
5. Re-correr todo el pipeline desde `calc_*.py`

### Cuando se modifica el catálogo de Áreas:
1. Actualizar `areas_catalogo.py`
2. Actualizar `render_*_p2.py` y `render_*_p3.py`
3. Actualizar `_governance/AREAS_ACCOUNTABLE.md`

### Cuando se modifica la estructura editorial:
1. Extraer snippet literal del template
2. Actualizar el helper en `template_*.py` (si aplica)
3. Actualizar el renderer correspondiente
4. Actualizar `_governance/ESTRUCTURA_TEMPLATE.md`

### Cuando se modifica el hub:
1. Editar `build_package.py` (función `build_index()`)
2. Actualizar `_governance/MAPA_DEPENDENCIAS.md` (sección Hub)
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
- **plan_seguimiento** se genera en `_governance/_seguimiento/` — editar antes del pipeline para mover QW resueltos a `## CERRADO`.
