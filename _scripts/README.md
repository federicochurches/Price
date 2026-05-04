# _scripts · Pipeline de generación de reportes

Pipeline Python para generar los Reportes Editoriales (HTML) y Excel de Análisis a partir de los datasets crudos semanales.

---

## 📋 Inventario de archivos

### Cálculo y agregación
| Archivo | Función |
|---|---|
| `engine.py` | Funciones core: bandas (`banda_nodispo`, `banda_rpm`, `banda_eficacia`, `banda_convrate`), agregaciones (`make_hotel_agg`, `aggregate_*`), Pareto P80, channel grupo |
| `render_helpers.py` | Helpers de formato: `fmt_int_es`, `fmt_pct2`, `fmt_num2`, `fmt_big`, `clean_hotel_name`, `truncate`, `banda_pill`, `gauge_5levels`, `wow_box` |
| `calc_rnd.py` | Calcula métricas globales y por canasta RND → guarda `rnd_w18_data.pkl` |
| `calc_cr.py` | Calcula métricas globales y por canasta CR → guarda `cr_w18_data.pkl` |
| `areas_catalogo.py` | Catálogo Áreas Accountable v2 + función de mapeo desde v1 |

### Renderers HTML por sección
| Archivo | Genera |
|---|---|
| `render_rnd_p1.py` | Masthead + Hero KPI + Alertas globales (RND) → `part1_rnd.html` |
| `render_rnd_p2.py` | Resumen Ejecutivo + Severity + Demanda NC + Bajo Rend + Sin Conv + Corp/Dest/País + Plan (RND) → `part2_rnd.html` |
| `render_rnd_p3.py` | Análisis por Canasta RND (B2B-OP, CUG, B2C cada uno con KPI + Alertas + Resumen + Severity + Tabs + Bajo10 + SinConv10 + Síntesis + Plan) → `part3_rnd.html` |
| `render_cr_p1.py` | Masthead + Hero KPI Eficacia/ConvRate + Alertas globales (CR) → `part1_cr.html` |
| `render_cr_p2.py` | Resumen Ejecutivo + Severity + Críticos + Bajo Rend + Sin Conv + Channel agrupado + Corp/Dest/Channel + Menor ConvRate + Plan (CR) → `part2_cr.html` |
| `render_cr_p3.py` | Análisis por Canasta CR (similar a RND) → `part3_cr.html` |

### Helpers de template
| Archivo | Replica del template |
|---|---|
| `template_resumen.py` | `render_resumen_ejecutivo(findings, accent_color, scope, header_title)` |
| `template_alertas.py` | `render_alertas_block(scope_text, accent, card_h, card_d, card_c)` |
| `template_severity.py` | `render_severity_block(...)` + `render_severity_2cols(...)` + `LEVELS_*` predefinidos |

### Ensamblado y Excel
| Archivo | Genera |
|---|---|
| `assemble_rnd.py` | Une part1+part2+part3 RND + footer → `Supply_RatesNoDispo_W18.html` |
| `assemble_cr.py` | Une part1+part2+part3 CR + footer → `Supply_CheckRates_W18.html` |
| `excel_rnd.py` | Excel Top 50 RND con 12 pestañas (sin Ficha Técnica desde W18) |
| `excel_cr.py` | Excel Top 50 CR con 14 pestañas (sin Ficha Técnica desde W18) |

### Mail y package
| Archivo | Genera |
|---|---|
| `render_mail_v3.py` | Mail semanal HTML para BCC a 12 destinatarios |
| `build_package.py` | ZIP con estructura para commit a GitHub |

---

## 🚀 Cómo correr el pipeline (orden importa)

```bash
cd _scripts/

# 1. Cálculo · genera pickles con métricas
python calc_rnd.py
python calc_cr.py

# 2. Renderers · cada uno escribe su parte
python render_rnd_p1.py
python render_rnd_p2.py
python render_rnd_p3.py
python render_cr_p1.py
python render_cr_p2.py
python render_cr_p3.py

# 3. Limpiar footer duplicado en p3 (workaround)
python -c "
import re
for f in ['part3_rnd.html','part3_cr.html']:
    txt = open(f).read()
    fixed = re.sub(r'<footer>\s*<span>[^<]*</span>\s*<span>[^<]*</span>\s*</footer>','',txt,flags=re.DOTALL)
    open(f,'w').write(fixed)
"

# 4. Ensamblado final
python assemble_rnd.py
python assemble_cr.py

# 5. Excel de análisis
python excel_rnd.py
python excel_cr.py

# 6. Mail (opcional)
python render_mail_v3.py

# 7. ZIP package
python build_package.py
```

---

## ⚠️ Reglas para mantener consistencia

### Cuando se modifica una banda:
1. Actualizar `engine.py` (función `banda_*`)
2. Actualizar `excel_*.py` (etiquetas de rango en pestañas Severity)
3. Actualizar `template_severity.py` (constantes `LEVELS_*`)
4. Actualizar templates HTML en `_template/` (rangos visibles)
5. Actualizar `_governance/BANDAS.md`
6. Re-correr todo el pipeline desde `calc_*.py` para que se propaguen las bandas a los pickles

### Cuando se modifica el catálogo de Áreas:
1. Actualizar `areas_catalogo.py` (lista canónica + mapeo)
2. Actualizar `render_*_p2.py` y `render_*_p3.py` (action-owner-badge)
3. Actualizar `_governance/AREAS_ACCOUNTABLE.md`

### Cuando se modifica la estructura editorial:
1. Mirar el `_template/_TEMPLATE_*.html` correspondiente PRIMERO
2. Extraer snippet literal del template
3. Actualizar el helper en `template_*.py` (si aplica)
4. Actualizar el renderer correspondiente (`render_*_p[1|2|3].py`)
5. Actualizar `_governance/ESTRUCTURA_TEMPLATE.md`

> **Lección Week 18:** los renderers no deben re-construir HTML desde cero. Deben replicar el snippet literal del template. Si querés cambiar visual, cambiá primero en el template y después propagá al renderer.

---

## 📁 Datos generados por el pipeline

```
_scripts/
├── *.py                           # código fuente
├── *_data.pkl                     # pickles intermedios (no commitear)
├── part1_*.html / part2_*.html / part3_*.html  # parciales (no commitear)
├── snippets/                      # snippets literales del template (referencia)
└── asset_*_head.html / asset_*_footer.html / asset_*_masthead.html
```

Los outputs finales (`Supply_*_W18.html`, `Analisis_*_W18.xlsx`) se mueven a `rates-nodispo/week-18/` o `checkrates/week-18/` antes del commit.
