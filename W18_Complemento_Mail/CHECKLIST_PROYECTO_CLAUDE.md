# ✅ Checklist · Archivos del proyecto Claude · PRICE

**Última actualización:** 4 mayo 2026 · post W18

Lista de archivos que deben estar cargados en el proyecto Claude para que la próxima sesión pueda arrancar el pipeline sin reconstruir nada. El proyecto NO contiene los datasets ni los outputs (HTML/Excel) — eso vive en el repo GitHub.

---

## 📁 Archivos esperados (51 archivos)

### Documentación / governance (10)

| Archivo | Contenido |
|---|---|
| `README.md` | overview, glosario, estructura repo, workflow |
| `BANDAS.md` | sistema de bandas D · thresholds y colores |
| `AREAS_ACCOUNTABLE.md` | catálogo Áreas v2 + mapeo desde v1 |
| `ESTRUCTURA_TEMPLATE.md` | estructura literal global y por canasta |
| `CHANGELOG.md` | cambios por semana |
| `CHECKLIST_PROYECTO_CLAUDE.md` | este archivo |
| `COMMIT_GUIDE.md` | guía para commit a GitHub |
| `NIVEL_C_PENDIENTE.md` | TODOs futuros |
| `PROMPT_MAESTRO_v2.md` | rol y reglas Claude |
| `Playbook_Mail_Semanal.md` | workflow del mail |

### Templates HTML (5)

| Archivo | Contenido |
|---|---|
| `_TEMPLATE_Hub.html` | template del hub (raíz) |
| `_TEMPLATE_RatesNoDispo_Reporte.html` | template editorial RND con placeholders |
| `_TEMPLATE_CheckRates_Reporte.html` | template editorial CR con placeholders |
| `GUIA_EDITORIAL_RatesNoDispo.html` | guía estilo RND |
| `GUIA_EDITORIAL_CheckRates.html` | guía estilo CR |

### Mail / destinatarios (3)

| Archivo | Contenido |
|---|---|
| `Mail_W{NN}.html` | mail de la última semana (referencia) |
| `mail_template.html` | template base del mail |
| `destinatarios.md` | 12 destinatarios BCC |

### Pipeline core (4)

| Archivo | Función |
|---|---|
| `engine.py` | bandas + agregaciones + helpers core |
| `render_helpers.py` | formato números español + clean_hotel_name |
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
| `template_resumen.py` | helper Resumen Ejecutivo (snippet template literal) |
| `template_alertas.py` | helper Alertas Críticas (3 cards) |
| `template_severity.py` | helper Severidad por canasta (2 cols) |

### Excel + mail + package (5)

| Archivo | Función |
|---|---|
| `excel_cr.py` | Excel Top 50 CR |
| `excel_rnd.py` | Excel Top 50 RND |
| `render_mail_v3.py` | mail semanal HTML |
| `send_email.py` | envío SMTP (opcional) |
| `build_package.py` | empaquetado ZIP final para commit |

### Assets HTML (6)

| Archivo | Función |
|---|---|
| `asset_cr_head.html` | `<head>` + CSS CR |
| `asset_cr_masthead.html` | masthead CR |
| `asset_cr_footer.html` | footer CR |
| `asset_rnd_head.html` | `<head>` + CSS RND |
| `asset_rnd_masthead.html` | masthead RND |
| `asset_rnd_footer.html` | footer RND |

### Snippets (referencia · 4)

| Archivo | Contenido |
|---|---|
| `snippet_resumen_global_cr.html` | snippet literal Resumen CR |
| `snippet_resumen_global_rnd.html` | snippet literal Resumen RND |
| `snippet_alertas_canasta.html` | snippet alertas canasta CR |
| `snippet_alertas_canasta_rnd.html` | snippet alertas canasta RND |

---

## ❌ Archivos que NO deben estar en el proyecto

Estos viven en el repo GitHub o en `/mnt/user-data/outputs/` durante la sesión:

- ❌ `RatesNoDispo_Reporte_Editorial.html` y `CheckRates_Reporte_Editorial.html` (deliverables · van al repo)
- ❌ `Analisis_*.xlsx` (deliverables · van al repo)
- ❌ `Dataset_*_W{NN}.xlsx` (datos crudos · van al repo)
- ❌ `Supply_*_W{NN}.html` (preview suelto · descarte después de commit)
- ❌ Pickles intermedios (`*_data.pkl`)
- ❌ Parciales HTML (`part1_*.html`, `part2_*.html`, `part3_*.html`)
- ❌ Versiones viejas de scripts (`render_mail.py`, `render_mail_v2.py`)

---

## 🔄 Qué actualizar cada semana

### Archivos que cambian SIEMPRE cada semana

- `Mail_W{NN}.html` — el del último envío (sustituye al de la semana anterior)
- `CHANGELOG.md` — agregar bloque nuevo si hubo cambios estructurales

### Archivos que cambian SOLO si hay cambios estructurales

- `_TEMPLATE_*.html` (raíz del proyecto) — solo si modificás el editorial
- `GUIA_EDITORIAL_*.html` — solo si actualizás reglas editoriales
- `engine.py` — solo si recalibrás bandas
- `BANDAS.md` — solo si recalibrás bandas
- `AREAS_ACCOUNTABLE.md` — solo si agregás/sacás áreas
- `ESTRUCTURA_TEMPLATE.md` — solo si cambiás secciones del editorial
- `template_resumen.py` / `template_alertas.py` / `template_severity.py` — solo si cambiás la estructura visual

### Archivos que NO suelen cambiar

- Los `render_*_p[1|2|3].py` y `calc_*.py` solo si hay un bug o feature nueva
- `asset_*_head.html` solo si cambia el CSS (color, tipografía, layout)

---

## 🚦 Pre-flight check antes de empezar Week NN+1

1. **Mail_W{NN}.html del envío anterior** está en el proyecto
2. **CHANGELOG.md** tiene anotado el último commit
3. Si hubo cambios estructurales en Week NN, los `_TEMPLATE_*.html` y guías editoriales están actualizados
4. Datasets Week NN+1 disponibles en `/mnt/user-data/uploads/`

Si algo falta, pedir ZIP de complemento al final de la sesión anterior.
