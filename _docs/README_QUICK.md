# 📋 README · Proyecto PRICE · Supply Analytics
**W21+ · Mayo 2026**

---

## 🌐 URLs de producción

| Destino | URL | Acceso |
|---|---|---|
| Hub Netlify | https://analytics-desk.netlify.app | `pricetravel` / `supply2026` |
| GitHub Pages | https://federicochurches.github.io/Price/ | Público |
| Repo GitHub | https://github.com/federicochurches/Price | Privado |

---

## 📁 Estructura del repo

```
Price/
├── index.html                        ← hub · NO editar manualmente
├── _docs/                            (no se publica)
│   ├── PROMPT_CORE.md                ← contexto operativo vigente
│   ├── HISTORIAL_SESIONES.md         ← arqueología W16-W20
│   ├── BANDAS.md                     ← paleta canónica completa
│   └── COMMIT_GUIDE.md
├── _scripts/                         (no se publica)
│   └── *.py / *.html                 ← pipeline completo
├── _email/week-NN/
│   └── Mail_WNN.html
├── _seguimiento/
│   └── plan_seguimiento_WNN.md
├── rates-nodispo/week-NN/
│   ├── RatesNoDispo_Reporte_Editorial.html
│   ├── Analisis_Rates_NoDispo_7d.xlsx        (33 pestañas)
│   ├── Analisis_Rates_NoDispo_B2C_7d.xlsx    (8 pestañas)
│   ├── Analisis_Rates_NoDispo_OP_7d.xlsx     (8 pestañas)
│   ├── Analisis_Rates_NoDispo_CUG_7d.xlsx    (8 pestañas)
│   └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/week-NN/
    ├── CheckRates_Reporte_Editorial.html
    ├── Analisis_Checkrates_7d.xlsx            (37 pestañas)
    ├── Analisis_Checkrates_B2C_7d.xlsx        (9 pestañas)
    ├── Analisis_Checkrates_OP_7d.xlsx         (9 pestañas)
    ├── Analisis_Checkrates_CUG_7d.xlsx        (9 pestañas)
    └── Dataset_CheckRates_WNN.xlsx
```

---

## 📌 Última semana publicada

**Week 21 · 25–31 may 2026**

| Métrica | W20 | W21 | WoW |
|---|---|---|---|
| %NoDispo | 2,74% | 2,59% | −0,15pp |
| IPM | $1.097 | $829 | −24,4% |
| Eficacia CR | 93,30% | 93,15% | −0,15pp |
| Conv Rate CR | 1,19% | 1,57% | +0,38pp |

---

## 🗂️ Inventario de scripts (`_scripts/`)

### Pipeline principal
| Archivo | Función |
|---|---|
| `run_pipeline.py` | Orquestador · comando único W21+ |
| `calc_cr.py` | Cálculos CR → pickle |
| `calc_rnd.py` | Cálculos RND → pickle |
| `render_cr_p1/p2/p3.py` | Render parciales CR |
| `render_rnd_p1/p2/p3.py` | Render parciales RND |
| `assemble_cr.py` / `assemble_rnd.py` | Ensambla HTML final |
| `excel_cr.py` / `excel_rnd.py` | Excels globales |
| `excel_cr_canastas.py` / `excel_rnd_canastas.py` | Excels por canasta |
| `render_mail_v3.py` | Draft mail semanal |
| `build_package.py` | Hub index.html + ZIP |
| `update_docs.py` | Actualiza CHANGELOG + README + PROMPT_CORE |
| `github_commit.py` | Commit API GitHub + ZIP proyecto Claude |

### Helpers y templates
| Archivo | Función |
|---|---|
| `engine.py` | Bandas + thresholds |
| `render_helpers.py` | Formateo, pills, searchbox, wow_box |
| `historico_module_v2.py` | Módulo histórico CR |
| `historico_module_rnd.py` | Módulo histórico RND |
| `historico_data.py` | Serie real W16-W20 |
| `template_resumen.py` | Resumen Ejecutivo |
| `template_alertas.py` | Alertas críticas |
| `template_severity.py` | Bloques severity |
| `template_seguimiento.py` | Plan de Acción |
| `areas_catalogo.py` | Catálogo áreas accountable |

### Assets HTML
| Archivo | Función |
|---|---|
| `asset_cr_head.html` | CSS + JS CR (violet) |
| `asset_cr_masthead.html` | Header CR |
| `asset_cr_footer.html` | Footer CR |
| `asset_rnd_head.html` | CSS + JS RND (magenta) |
| `asset_rnd_masthead.html` | Header RND |
| `asset_rnd_footer.html` | Footer RND |

### Documentación en el proyecto
| Archivo | Función |
|---|---|
| `PROMPT_CORE.md` | Contexto operativo vigente |
| `HISTORIAL_SESIONES.md` | Arqueología sesiones W16-W20 |
| `BANDAS.md` | Paleta canónica completa |
| `COMMIT_GUIDE.md` | Workflow de commit |
| `destinatarios.md` | 15 destinatarios BCC |

---

**Última actualización:** Mayo 2026 · W21+

---

## 🔄 Proceso de trabajo · Ciclo completo

### A) Corrección visual / fix de código (sin cambio de datos)

```
1. IDENTIFICAR el bug (screenshot + análisis HTML)
2. APLICAR fix en script(s)
3. RE-RENDER parciales + assemble (sin pipeline completo):
      python3 render_rnd_p*.py && python3 assemble_rnd.py
      python3 render_cr_p*.py  && python3 assemble_cr.py
4. PAUSA → validación visual del usuario (abrir HTML local)
   ↳ Si hay otro fix → volver al paso 2
   ↳ Si OK → continuar
5. PIPELINE COMPLETO:
      python3 excel_rnd.py && python3 excel_rnd_canastas.py
      python3 excel_cr.py  && python3 excel_cr_canastas.py
      python3 render_mail_v3.py
      python3 build_package.py        ← genera Price_WNN.zip
6. DOCUMENTAR cambios en PROMPT_CORE.md + HISTORIAL_SESIONES.md
7. COMMIT GitHub:
      python3 github_commit.py --week NN --periodo "..." --tipo fix         --mensaje "Descripción del fix"         --scripts-dir /tmp --outputs-dir /mnt/user-data/outputs
   ↳ Genera automáticamente ProyectoClaude_PRICE_WNN.zip
8. SUBIR ProyectoClaude ZIP al Proyecto Claude (manual)
```

**Regla crítica:** nunca correr pipeline completo en cada iteración de fix visual. Solo después de validación confirmada.

---

### B) Pipeline semanal (nuevos datasets)

```
1. RECIBIR datasets WNN y W(N-1)
2. VALIDAR columnas (ver sección "Validación pre-pipeline" en PROMPT_CORE)
3. CALCULAR pickles:
      WEEK=WNN VOL_NUM=NN PERIODO="DD–DD mes YYYY" ...
      python3 calc_rnd.py
      python3 calc_cr.py
4. RE-RENDER + assemble → PAUSA validación visual
5. Si OK → PIPELINE COMPLETO (paso A.5)
6. DOCUMENTAR + actualizar historico_data.py con KPIs de la semana
7. COMMIT con mensaje:
      "feat: Week NN · RatesNoDispo + CheckRates + hub index · DD-MM-YYYY"
8. SUBIR ZIP al Proyecto Claude
```

---

### C) Actualizar Proyecto Claude (qué subir y cuándo)

| Archivo | Cuándo actualizar |
|---|---|
| `ProyectoClaude_PRICE_WNN.zip` | Cada pipeline semanal + cada fix relevante |
| `PROMPT_CORE.md` | Cuando hay nuevas reglas, bugs cerrados, o decisiones de diseño |
| `HISTORIAL_SESIONES.md` | Al cerrar cada sesión de trabajo |

**El ZIP siempre incluye TODOS los archivos plano** (sin carpetas): `.py` + `.html` + `.md`.  
El commit de GitHub genera el ZIP automáticamente → solo hay que descargarlo y subirlo al Proyecto Claude.

---

### D) Variables de entorno (copiar y pegar cada sesión)

```bash
export WEEK=W21
export VOL_NUM=21
export PERIODO="18–24 may 2026"
export MES_ANO="Mayo 2026"
export FECHA_PUB="LUNES 26 de Mayo de 2026"
export PICKLE_RND=/tmp/rnd_w21_data.pkl
export PICKLE_CR=/tmp/cr_w21_data.pkl
export GITHUB_TOKEN=ghp_...   # revocar y renovar periódicamente
```

---

### E) Diagnóstico rápido de WoW faltante

Si los reportes muestran `—` donde debería haber pills de WoW:

```python
import pickle, pandas as pd
with open('/tmp/rnd_w21_data.pkl','rb') as f:
    d = pickle.load(f)

# Chequear TOP y CANASTA
for k, v in d['TOP'].items():
    if isinstance(v, pd.DataFrame) and 'NoDispo_WoW_pp' in v.columns:
        print(k, v['NoDispo_WoW_pp'].notna().sum(), '/', len(v))
```

Si el resultado es `0/N` → el pickle fue generado con un orden incorrecto.  
**Fix:** correr el bloque de enriquecimiento manual (ver `calc_rnd.py` sección `Enriquecer TOP[]`).
