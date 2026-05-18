# 📁 ESTRUCTURA VISUAL DE /mnt/project/

**Proyecto Claude Local · PRICE · Supply Analytics**

---

## 🎯 RESUMEN RÁPIDO

```
56 archivos totales:
  • 15 documentación .md (PROMPT_MAESTRO, README, etc)
  • 2 NEW (config_w20.yaml + validate_yaml_config.py)
  • 14 scripts pipeline Python
  • 8 helpers Python
  • 6 assets HTML (CSS + headers + footers)
  • 2 guías editoriales HTML
  • 1 mail HTML
  • 5 scripts shell (.sh)
```

---

## 📚 DOCUMENTACIÓN (15 .md)

| Archivo | Propósito |
|---|---|
| **PROMPT_MAESTRO_v3.md** | ⭐ Contexto operativo completo (730 líneas) |
| README.md | Decisiones consolidadas + arquitectura |
| CHANGELOG.md | Historial cronológico de cambios |
| ESTRUCTURA_TEMPLATE.md | Snippets HTML + CSS literales |
| CHECKLIST_PROYECTO_CLAUDE.md | Inventario de 42 archivos |
| COMMIT_GUIDE.md | Guía de commits |
| Playbook_Mail_Semanal.md | Workflow operativo semanal |
| MAIL_DRAFT_FLUJO.md | Comando único para draft Gmail |
| MAPA_DEPENDENCIAS.md | Dependencias entre scripts |
| NIVEL_C_PENDIENTE.md | TODOs futuros post W19+ |
| CHECKLIST_SEMANAL.md | Checklist semanal |
| EXCLUSIONES_ZIP.md | Qué no incluir en ZIP |
| READY_W20.md | Estado pre-W20 |
| audit_w20.md | Auditoría W20 |
| destinatarios.md | 15 emails para envío mail |

---

## 🎯 CONFIGURACIÓN SEMANAL (NEW · PHASE 1 PUNTO 1)

| Archivo | Propósito |
|---|---|
| **config_w20.yaml** | ⭐ Centraliza 17 variables (week, periodo, datasets, pickles) |

**Cambias AQUÍ cada semana:**
```yaml
week: 20
vol_num: 20
periodo: "12–18 may 2026"
dataset_rnd_actual: "Dataset_RatesNoDispo_W20.xlsx"
dataset_rnd_prev: "Dataset_RatesNoDispo_W19.xlsx"
# ... 12 valores más
```

---

## ✅ VALIDACIÓN (NEW · PHASE 1 PUNTO 1)

| Archivo | Propósito |
|---|---|
| **validate_yaml_config.py** | Valida config_w20.yaml antes de ejecutar pipeline |

**Ejecutas:**
```bash
python validate_yaml_config.py
# Output: ✅ VALIDACIÓN COMPLETADA EXITOSAMENTE
```

---

## 🔧 PIPELINE PASO 1: CÁLCULOS (2 scripts)

Lee `config_w20.yaml` automáticamente. Genera pickles con datos procesados.

| Script | Entrada | Salida |
|---|---|---|
| **calc_rnd.py** | Dataset_RatesNoDispo_W20 + W19 | rnd_w20_data.pkl |
| **calc_cr.py** | Dataset_CheckRates_W20 + W19 | cr_w20_data.pkl |

---

## 🎨 PIPELINE PASO 2-3: RENDERING (6 scripts)

Lee pickles y genera HTML. 3 partes por reporte (RND + CR).

| Script | Propósito |
|---|---|
| render_rnd_p1.py | RND: KPIs hero + alertas críticas |
| render_rnd_p2.py | RND: Resumen core + severity + tabs |
| render_rnd_p3.py | RND: Análisis por canasta |
| render_cr_p1.py | CR: KPIs hero + alertas |
| render_cr_p2.py | CR: Resumen core + severity + tabs |
| render_cr_p3.py | CR: Análisis por canasta |

---

## 📊 PIPELINE PASO 4-5: ASSEMBLY & EXCEL (4 scripts)

| Script | Salida |
|---|---|
| assemble_rnd.py | RatesNoDispo_Reporte_Editorial.html |
| assemble_cr.py | CheckRates_Reporte_Editorial.html |
| excel_rnd.py | 4 Excels RND (1 global + 3 canasta) |
| excel_cr.py | 4 Excels CR (1 global + 3 canasta) |

---

## 📨 PIPELINE PASO 6: MAIL & HUB (2 scripts)

Lee `config_w20.yaml` automáticamente.

| Script | Salida |
|---|---|
| **render_mail_v3.py** | Mail_W20.html (mail semanal) |
| **build_package.py** | index.html (hub) + Price_W20.zip |

---

## 🛠️ HELPERS & UTILIDADES (8 scripts)

Funciones compartidas usadas por múltiples scripts.

| Script | Funcionalidad |
|---|---|
| engine.py | Bandas + thresholds (eficacia, convrate, RPM, nodispo) |
| render_helpers.py | Format español, clean_hotel_name, truncate, banda_pill |
| template_resumen.py | Render Resumen Ejecutivo |
| template_alertas.py | Render alertas críticas |
| template_severity.py | Render bloques severity |
| template_seguimiento.py | Render seguimiento plan |
| areas_catalogo.py | Catálogo áreas accountable v2 |
| send_email.py | Envío de email |

---

## 🎬 ASSETS HTML (6 archivos)

CSS, headers, footers que se injectan en reportes.

| Asset | Propósito |
|---|---|
| asset_rnd_head.html | CSS variables RND (magenta) |
| asset_rnd_masthead.html | Header RND con logo |
| asset_rnd_footer.html | Footer RND |
| asset_cr_head.html | CSS variables CR (violet) |
| asset_cr_masthead.html | Header CR con logo |
| asset_cr_footer.html | Footer CR |

---

## 📖 GUÍAS EDITORIALES (2 HTML)

Referencia visual de estilos.

| Guía | Propósito |
|---|---|
| GUIA_EDITORIAL_RatesNoDispo.html | Referencia visual RND · colores, tipografía |
| GUIA_EDITORIAL_CheckRates.html | Referencia visual CR · colores, tipografía |

---

## 📧 MAIL (1 HTML)

| Archivo | Propósito |
|---|---|
| Mail_W19.html | Mail última semana · referencia para draft |

---

## 🚀 SCRIPTS DE EJECUCIÓN (5 scripts)

| Script | Propósito |
|---|---|
| **run_pipeline.sh** | Ejecuta TODO el pipeline en orden |
| setup_week.sh | Setup para nueva semana |
| sync_project.sh | Sincroniza proyecto |
| package_project.sh | Empaqueta para release |
| release_week.py | Release automation |

---

## 🔄 FLUJO DE EJECUCIÓN COMPLETO

```
Paso 1: VALIDACIÓN
  python validate_yaml_config.py
  
Paso 2: CÁLCULOS
  python calc_rnd.py         → rnd_w20_data.pkl
  python calc_cr.py          → cr_w20_data.pkl
  
Paso 3: RENDERING (RND)
  python render_rnd_p1.py    → parte 1
  python render_rnd_p2.py    → parte 2
  python render_rnd_p3.py    → parte 3
  
Paso 4: RENDERING (CR)
  python render_cr_p1.py     → parte 1
  python render_cr_p2.py     → parte 2
  python render_cr_p3.py     → parte 3
  
Paso 5: ASSEMBLY
  python assemble_rnd.py     → RatesNoDispo_Reporte_Editorial.html
  python assemble_cr.py      → CheckRates_Reporte_Editorial.html
  
Paso 6: EXCEL
  python excel_rnd.py        → 4 Excels RND
  python excel_cr.py         → 4 Excels CR
  
Paso 7: MAIL & HUB
  python render_mail_v3.py   → Mail_W20.html
  python build_package.py    → index.html + Price_W20.zip
```

**O simplemente:**
```bash
bash run_pipeline.sh 20
```

---

## ✨ ARCHIVOS NUEVOS HOY (PHASE 1 PUNTO 1)

| Archivo | Tipo | Propósito |
|---|---|---|
| config_w20.yaml | YAML | Centraliza 17 variables semanales |
| validate_yaml_config.py | Python | Validador automático pre-pipeline |

---

## 🔄 SCRIPTS MODIFICADOS HOY

| Script | Cambio |
|---|---|
| calc_rnd.py | + import yaml · Lee config_w20.yaml |
| calc_cr.py | + import yaml · Lee config_w20.yaml |
| render_mail_v3.py | + import yaml · Lee config_w20.yaml |
| build_package.py | + import yaml · Lee config_w20.yaml |

---

## 📊 ESTADÍSTICAS

```
Total archivos:      56
Documentación:       15 .md
Scripts Python:      14 pipeline + 8 helpers = 22
Assets HTML:         6 (CSS + headers + footers)
Guías:               2 HTML
Mail:                1 HTML
Scripts shell:       5 .sh
YAML:                1 (NEW)

Tamaño total:        ~750 KB
Líneas Python:       ~2,500 líneas
Líneas HTML:         ~1,200 líneas
```

---

**Status:** ✅ Estructura visual lista · 56 archivos organizados

