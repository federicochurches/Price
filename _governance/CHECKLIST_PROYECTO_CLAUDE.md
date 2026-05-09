# ✅ Checklist · Archivos del proyecto Claude · PRICE

**Última actualización:** Mayo 2026 · post W18 · optimización espacio

Lista de archivos que deben estar cargados en el proyecto Claude para que la próxima sesión pueda arrancar el pipeline sin reconstruir nada. El proyecto NO contiene los datasets ni los outputs (HTML/Excel) — eso vive en el repo GitHub.

---

## 📁 Archivos esperados (41 archivos)

### Documentación / governance (10)

| Archivo | Contenido |
|---|---|
| `README.md` | overview, glosario, estructura repo, workflow |
| `PROMPT_MAESTRO_v3.md` | rol, reglas, decisiones consolidadas |
| `ESTRUCTURA_TEMPLATE.md` | estructura literal global y por canasta |
| `CHANGELOG.md` | cambios por semana |
| `CHECKLIST_PROYECTO_CLAUDE.md` | este archivo |
| `COMMIT_GUIDE.md` | guía para commit a GitHub |
| `NIVEL_C_PENDIENTE.md` | TODOs futuros |
| `MAIL_DRAFT_FLUJO.md` | comando único para draft Gmail |
| `MAPA_DEPENDENCIAS.md` | mapa de dependencias entre scripts |
| `Playbook_Mail_Semanal.md` | workflow del mail |

### Guías editoriales HTML (2)

| Archivo | Contenido |
|---|---|
| `GUIA_EDITORIAL_RatesNoDispo.html` | guía estilo RND · referencia canónica visual |
| `GUIA_EDITORIAL_CheckRates.html` | guía estilo CR · referencia canónica visual |

> ⚠️ Los `_TEMPLATE_*.html` y snippets se eliminaron — pesan ~720KB y el pipeline no los necesita. La referencia visual vive en el repo GitHub.

### Mail (1)

| Archivo | Contenido |
|---|---|
| `Mail_W{NN}.html` | mail de la última semana enviada (referencia para draft) |

### Pipeline core (4)

| Archivo | Función |
|---|---|
| `engine.py` | bandas + thresholds + helpers core |
| `render_helpers.py` | formato números español + clean_hotel/destino/corp |
| `areas_catalogo.py` | catálogo Áreas Accountable v2 |
| `commit_release.py` / `release_week.py` | scripts de release |

### Pipeline cálculo y render (10)

| Archivo | Función |
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

### Excel + mail + package (5)

| Archivo | Función |
|---|---|
| `excel_cr.py` | Excel Top 50 CR (4 archivos) |
| `excel_rnd.py` | Excel Top 50 RND (4 archivos) |
| `render_mail_v3.py` | mail semanal HTML |
| `send_email.py` | envío SMTP |
| `build_package.py` | empaquetado ZIP final para commit |

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

- ❌ `_TEMPLATE_RatesNoDispo_Reporte.html` / `_TEMPLATE_CheckRates_Reporte.html` (eliminados · pesan 696KB · referencia en repo)
- ❌ Snippets `snippet_*.html` (eliminados · redundantes con renders)
- ❌ `RatesNoDispo_Reporte_Editorial.html` / `CheckRates_Reporte_Editorial.html` (deliverables · van al repo)
- ❌ `Analisis_*.xlsx` (deliverables · van al repo)
- ❌ `Dataset_*_W{NN}.xlsx` (datos crudos · van al repo)
- ❌ Pickles intermedios (`*_data.pkl`)
- ❌ Parciales HTML (`part1_*.html`, `part2_*.html`, `part3_*.html`)

---

## 🔄 Qué actualizar cada semana

### Siempre
- `Mail_W{NN}.html` — sustituye al de la semana anterior
- `CHANGELOG.md` — agregar bloque si hubo cambios estructurales

### Solo si hay cambios estructurales
- `GUIA_EDITORIAL_*.html` — si actualizás reglas editoriales
- `engine.py` — si recalibrás bandas
- `template_resumen.py` / `template_alertas.py` / `template_severity.py` — si cambiás estructura visual
- `asset_*_head.html` — si cambiás CSS

### No suelen cambiar
- `render_*_p[1|2|3].py` y `calc_*.py` — solo si hay bug o feature nueva

---

## 🚦 Pre-flight check antes de empezar Week NN+1

1. `Mail_W{NN}.html` del envío anterior está en el proyecto
2. `CHANGELOG.md` tiene anotado el último commit
3. Si hubo cambios estructurales, guías editoriales y assets actualizados
4. Datasets Week NN+1 disponibles en `/mnt/user-data/uploads/`
