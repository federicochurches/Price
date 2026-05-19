# ✅ Checklist · Archivos del proyecto Claude · PRICE

**Última actualización:** Mayo 2026 · post W20 · FLUJO YAML AUTOMÁTICO INTEGRADO

---

## 📁 Archivos esperados (43 archivos)

> ✨ **NUEVO W21+:** Flujo YAML automatizado integrado. Ver `run_pipeline.py` + `WEEK_CONFIG_W21.yml` + guías YAML.

### Documentación / governance (10 + 3 YAML nuevas)

| Archivo | Contenido |
|---|---|
| `README.md` | overview, **flujo YAML + pipeline clásico**, estructura ZIP, workflow |
| `PROMPT_MAESTRO_v3.md` | rol, reglas, **instrucciones W21+ con YAML**, decisiones consolidadas |
| `ESTRUCTURA_TEMPLATE.md` | estructura literal global y por canasta |
| `CHANGELOG.md` | cambios por semana |
| `CHECKLIST_PROYECTO_CLAUDE.md` | este archivo |
| `COMMIT_GUIDE.md` | guía para commit a GitHub |
| `NIVEL_C_PENDIENTE.md` | TODOs futuros |
| `MAPA_DEPENDENCIAS.md` | mapa de dependencias entre scripts |
| `Playbook_Mail_Semanal.md` | workflow del mail |
| **`YAML_PIPELINE_GUIDE.md`** | **NUEVO · Guía completa flujo YAML (5000+ palabras)** |
| **`IMPLEMENTACION_YAML_COMPLETADA.md`** | **NUEVO · Arquitectura + decisiones técnicas YAML** |
| **`QUICK_REFERENCE_YAML.md`** | **NUEVO · Cheat sheet 1 página para W21+** |
| `GUIA_EDITORIAL_RatesNoDispo.html` | guía estilo RND · referencia canónica visual |
| `GUIA_EDITORIAL_CheckRates.html` | guía estilo CR · referencia canónica visual |

> ⚠️ Los `_TEMPLATE_*.html` y snippets se eliminaron — pesan ~720KB y el pipeline no los necesita. La referencia visual vive en el repo GitHub.
|---|---|
| `calc_cr.py` | cálculo métricas CR → pickle |
| `calc_rnd.py` | cálculo métricas RND → pickle |
| `render_cr_p1.py` / `p2.py` / `p3.py` | renderers CR (hero · core · canastas) |
| `render_rnd_p1.py` / `p2.py` / `p3.py` | renderers RND (hero · core · canastas) |
| `assemble_cr.py` / `assemble_rnd.py` | ensamblado HTML final |

### Helpers de template (3)

| Archivo | Función |
|---|---|
| `template_resumen.py` | helper Resumen Ejecutivo |
| `template_alertas.py` | helper Alertas Críticas (3 cards) |
| `template_severity.py` | helper Severidad por canasta |

### Excel + mail + hub + package (6)

| Archivo | Función |
|---|---|
| `excel_cr.py` | 4 Excels CR (global 37 pests. + 3 canasta) |
| `excel_rnd.py` | 4 Excels RND (global 33 pests. + 3 canasta) |
| `render_mail_v3.py` | mail semanal HTML · v3.2 sin dependencia metrics_recalc.pkl |
| `send_email.py` | envío SMTP |
| `build_package.py` | **PASO 6 · genera index.html del hub + ZIP repo** |

### Assets HTML (6)

| Archivo | Función |
|---|---|
| `asset_cr_head.html` | `<head>` + CSS CR (violet) |
| `asset_cr_masthead.html` | masthead CR |
| `asset_cr_footer.html` | footer CR |
| `asset_rnd_head.html` | `<head>` + CSS RND (magenta) |
| `asset_rnd_masthead.html` | masthead RND |
| `asset_rnd_footer.html` | footer RND |

---

## ❌ Archivos que NO deben estar en el proyecto

- ❌ `_TEMPLATE_RatesNoDispo_Reporte.html` / `_TEMPLATE_CheckRates_Reporte.html` (eliminados · 696KB · referencia en repo)
- ❌ Snippets `snippet_*.html` (eliminados · redundantes)
- ❌ `RatesNoDispo_Reporte_Editorial.html` / `CheckRates_Reporte_Editorial.html` (deliverables · van al repo)
- ❌ `Analisis_*.xlsx` (deliverables · van al repo)
- ❌ `Dataset_*_W{NN}.xlsx` (datos crudos · van al repo)
- ❌ Pickles intermedios (`*_data.pkl`)
- ❌ Parciales HTML (`part1_*.html`, `part2_*.html`, `part3_*.html`)
- ❌ `index.html` (se genera automáticamente · va al repo · no al proyecto Claude)
- ❌ `Price_W{NN}.zip` (deliverable · no al proyecto Claude)

---

## 🔄 Qué actualizar cada semana

### Siempre (antes de correr el pipeline)
- `Mail_W{NN}.html` — sustituir por el de la semana anterior

### Siempre (después de correr el pipeline)
- `CHANGELOG.md` — agregar bloque Week NN aunque no haya cambios estructurales

### Solo si hay cambios estructurales
- `GUIA_EDITORIAL_*.html` — si cambiaron reglas editoriales
- `engine.py` — si recalibrás bandas
- `template_resumen.py` / `template_alertas.py` / `template_severity.py` — si cambiás estructura visual
- `asset_*_head.html` — si cambiás CSS
- `build_package.py` — si cambiás el diseño del hub

### No suelen cambiar semana a semana
- `render_*_p[1|2|3].py` y `calc_*.py` — solo si hay bug o feature nueva

---

## 🚦 Pre-flight check antes de empezar Week NN+1

1. `Mail_W{NN}.html` del envío anterior está en el proyecto ✓
2. `CHANGELOG.md` tiene anotado el último commit ✓
3. Datasets W(NN+1) y W(NN) disponibles en `/mnt/user-data/uploads/` ✓
4. Si hubo cambios estructurales, assets y guías editoriales actualizados ✓
5. `build_package.py` tiene `WEEK_PREV` y `PERIODO_PREV` correctos para el historial ✓

---

## ⚠️ Importante: cómo subir archivos al proyecto Claude

El proyecto Claude **no reemplaza** archivos con el mismo nombre — los duplica. Para evitar acumulación:

1. **Antes de subir el ZIP delta** → borrar los archivos viejos que van a ser reemplazados
2. **O una vez por mes** → borrar todo y subir el ZIP completo limpio (42 archivos)

Si el proyecto llega a >55 archivos es señal de que hay duplicados acumulados.
