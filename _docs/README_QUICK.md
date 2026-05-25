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

**Week 20 · 11–17 may 2026**

| Métrica | W19 | W20 | WoW |
|---|---|---|---|
| %NoDispo | 2,31% | 2,81% | +0,50pp |
| IPM | $499 | $1.097 | +119,8% |
| Eficacia CR | 93,30% | 92,75% | −0,55pp |
| Conv Rate CR | 1,14% | 1,19% | +0,05pp |

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
