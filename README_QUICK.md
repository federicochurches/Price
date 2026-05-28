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
├── *.py / *.html / *.js / *.css      ← pipeline completo en raíz
├── *.md                              ← docs operativos en raíz
├── _email/week-NN/
│   └── Mail_WNN.html
├── _seguimiento/
│   └── plan_seguimiento_WNN.md
├── reports/week-NN/                      ← W21+ HTML unificado
│   └── SUPPLY_WNN.html
├── rates-nodispo/week-NN/                ← solo Excels + Dataset
│   ├── Analisis_RatesNoDispo_WNN.xlsx    (4 hojas: Global · B2C · B2B-OP · CUG)
│   └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/week-NN/                   ← solo Excels + Dataset
    ├── Analisis_CheckRates_WNN.xlsx      (4 hojas: Global · B2C · B2B-OP · CUG)
    └── Dataset_CheckRates_WNN.xlsx
```

> **W22-pre:** carpetas `_scripts/` y `_docs/` eliminadas — todos los archivos viven en la raíz del repo.

---

## 📌 Última semana publicada

**W21 · 19-25 mayo 2026 · May 2026**

| Métrica | Valor | WoW |
|---|---|---|
| RND %NoDispo | 2,63% | -0,17pp |
| RND IPM | $834 | -34,1% |
| CR Eficacia | 93,15% | -0,19pp |
| CR ConvRate | 1,57% | -0,07pp |

🔗 [Hub](https://analytics-desk.netlify.app) · [Supply W21](https://federicochurches.github.io/Price/reports/week-21/SUPPLY_W21.html) · [CR](https://federicochurches.github.io/Price/reports/week-21/SUPPLY_W21.html#section-cr) · [RND](https://federicochurches.github.io/Price/reports/week-21/SUPPLY_W21.html#section-rnd)


## 🗂️ Inventario de scripts (raíz del repo)

### Pipeline principal
| Archivo | Función |
|---|---|
| `run_pipeline.py` | Orquestador · comando único W21+ |
| `calc_cr.py` | Cálculos CR → pickle |
| `calc_rnd.py` | Cálculos RND → pickle |
| `render_cr_p1/p2/p3.py` | Render parciales CR |
| `render_rnd_p1/p2/p3.py` | Render parciales RND |
| `assemble_unified.py` | Ensambla HTML unificado SUPPLY_WNN.html (W21+) |
| `excel_cr.py` / `excel_rnd.py` | 1 Excel por reporte · 4 hojas c/u (W21+) |
| `render_mail_v3.py` | Draft mail semanal |
| `build_package.py` | Hub index.html + ZIP |
| `github_commit.py` | Commit API GitHub + ZIP proyecto Claude |

### Helpers y templates
| Archivo | Función |
|---|---|
| `engine.py` | Bandas + thresholds |
| `render_helpers.py` | Formateo, pills, searchbox, wow_box |
| `historico_module.py` | Módulo histórico unificado CR+RND (W21+) |
| `historico_data.py` | Serie real W17-W21 · semana actual dinámica desde pickle |
| `template_resumen.py` | Resumen Ejecutivo |
| `template_alertas.py` | Alertas críticas |
| `template_severity.py` | Bloques severity |
| `template_seguimiento.py` | Plan de Acción |
| `areas_catalogo.py` | Catálogo áreas accountable |

### Assets HTML
| Archivo | Función |
|---|---|
| `asset_supply_head.html` | Head unificado · scoping CR/RND · switcher (W21+) |
| `asset_shared_head.html` | CSS compartido CR+RND |
| `asset_cr_head.html` | Head CR standalone (legacy W16-W20) |
| `asset_cr_masthead.html` | Header CR con logo |
| `asset_cr_footer.html` | Footer CR (legacy) |
| `asset_rnd_head.html` | Head RND standalone (legacy W16-W20) |
| `asset_rnd_masthead.html` | Header RND con logo |
| `asset_rnd_footer.html` | Footer RND (legacy) |

### Documentación en el proyecto
| Archivo | Función |
|---|---|
| `PROMPT_CORE.md` | Contexto operativo vigente |
| `HISTORIAL_SESIONES.md` | Arqueología sesiones W16-W20 |
| `BANDAS.md` | Paleta canónica completa |
| `COMMIT_GUIDE.md` | Workflow de commit |
| `destinatarios.md` | 15 destinatarios BCC |

| `NOTA_REFACTOR_PENDIENTE.md` | Refactor centralización CR/RND — ejecutar en W22 |

---

**Última actualización:** Mayo 2026 · W21-post3

---

## 🔄 Proceso de trabajo · Ciclo completo

### A) Corrección visual / fix de código (sin cambio de datos)

```
1. IDENTIFICAR el bug (screenshot + análisis HTML)
2. APLICAR fix en script(s)
3. RE-RENDER parciales + assemble_unified (sin pipeline completo):
      python3 render_rnd_p*.py
      python3 render_cr_p*.py
      python3 assemble_unified.py
4. PAUSA → validación visual del usuario (abrir SUPPLY_WNN.html)
   ↳ Si hay otro fix → volver al paso 2
   ↳ Si OK → continuar
5. PIPELINE COMPLETO:
      python3 excel_rnd.py
      python3 excel_cr.py
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
4. RE-RENDER + assemble_unified → PAUSA validación visual
5. Si OK → PIPELINE COMPLETO (paso A.5)
6. DOCUMENTAR + actualizar `historico_data.py`:
      - Agregar KPIs W{N} a cada scope en HIST_DATA (global, op, cug, b2c)
      - Descartar la semana más antigua del array
      - Actualizar SEMANAS = [W{N-3}, W{N-2}, W{N-1}, W{N}, W{N+1}]
      - El valor W{N+1} (semana actual) siempre viene dinámico del pickle
7. COMMIT con mensaje:
      "feat: Week NN · Supply unificado + Excels consolidados · DD-MM-YYYY"
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
