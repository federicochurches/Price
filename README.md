# PRICE · Supply Optimization

Repositorio de reportes semanales de **Supply Optimization** de PriceTravel Holding.

🌐 **Hub público:** https://federicochurches.github.io/Price/

---

## 📊 Reportes

Dos reportes editoriales semanales que analizan la performance del supply en una OTA:

### CheckRates
Análisis de eficacia técnica y conversión por canal (B2C · B2B-OP · CUG). Evalúa cuántos checkRates se hacen, qué porcentaje son exitosos, y cuántos terminan en booking.

**Métricas clave:** Eficacia · Conv Rate · CheckRates totales · Cluster (Connectivity / Tech / Conversion / Hybrid / Quick Win)

### Rates No Dispo
Análisis de disponibilidad y conversión por hotel/destino/corporativo. Identifica el tráfico que no se monetiza por falta de inventario.

**Métricas clave:** %NoDispo ponderado · Tráfico bloqueado · GB · RPM · Concentración por Corporativo

---

## 📁 Estructura del repo

```
Price/
├── README.md                    ← este archivo
├── index.html                   ← Hub público
│
├── _docs/                       ← documentación interna (CHANGELOG, etc)
├── _email/
│   └── week-NN/
│       └── Mail_WNN.html        ← mail unificado CR + RND por semana
├── _scripts/                    ← automatización (ver más abajo)
├── _template/
│   └── _TEMPLATE_Hub.html       ← template del hub
│
├── checkrates/
│   ├── _manual/
│   │   └── GUIA_EDITORIAL_CheckRates.html
│   ├── _template/
│   │   └── _TEMPLATE_CheckRates_Reporte_Editorial.html
│   └── week-NN/
│       ├── CheckRates_Reporte_Editorial.html
│       ├── Analisis_Checkrates_7d_WNN.xlsx
│       └── data_set_checkrates_WNN.xlsx
│
└── rates-nodispo/
    ├── _manual/
    │   └── GUIA_EDITORIAL_RatesNoDispo.html
    ├── _template/
    │   └── _TEMPLATE_RatesNoDispo_Reporte_Editorial.html
    └── week-NN/
        ├── RatesNoDispo_Reporte_Editorial.html
        ├── Analisis_Rates_NoDispo_7d_WNN.xlsx
        └── WeekNNRatesNoDispo.xlsx
```

---

## 🚀 Workflow semanal · cómo hacer un release

### Pre-requisitos (1 sola vez)
```bash
pip install pandas openpyxl
```

### Cada lunes · 4 pasos

#### 1. Recibir los 2 datasets crudos
- `data_set_checkrates_WNN.xlsx` (~4-5 MB)
- `WeekNNRatesNoDispo.xlsx` (~22 MB · **debe tener columna CorpName**)

Copialos a `_scripts/inputs/`.

#### 2. Generar Excels + Mail + actualizar index
```bash
cd ~/Documents/GitHub/Price
python _scripts/release_week.py --week 18 --periodo "27 Abr - 3 May 2026"
```

Esto genera automáticamente:
- ✅ `checkrates/week-18/Analisis_Checkrates_7d_W18.xlsx`
- ✅ `checkrates/week-18/data_set_checkrates_W18.xlsx`
- ✅ `rates-nodispo/week-18/Analisis_Rates_NoDispo_7d_W18.xlsx`
- ✅ `rates-nodispo/week-18/Week18RatesNoDispo.xlsx`
- ✅ `_email/week-18/Mail_W18.html`
- ✅ `index.html` (KPIs actualizados)

#### 3. Generar reportes editoriales HTML (manual con Claude)
Esta parte sigue siendo manual. En una nueva sesión con Claude:
- Subí los 2 datasets
- Pedí: "release WNN · CheckRates + Rates No Dispo · estructura W17"
- Claude genera los 2 HTMLs

Bajalos y movelos a:
- `checkrates/week-NN/CheckRates_Reporte_Editorial.html`
- `rates-nodispo/week-NN/RatesNoDispo_Reporte_Editorial.html`

#### 4. Commit + Push
```bash
python _scripts/commit_release.py --week 18 --periodo "27 Abr - 3 May 2026"
```

El script verifica que TODOS los archivos esperados estén · si falta uno te avisa cuál · y hace `git add . && git commit && git push origin main` automáticamente.

#### 5. Mandar el mail
Abrí `_email/week-NN/Mail_WNN.html` en Chrome · Ctrl+A · Ctrl+C · pegá en Gmail.

**Asunto:** `Supply Optimization · Week NN · CheckRates + Rates No Dispo`

---

## 🤖 Automatización · `_scripts/`

```
_scripts/
├── release_week.py          ← genera Excels + Mail + actualiza index
├── commit_release.py        ← validación + git add + commit + push
├── inputs/                  ← acá poner los 2 datasets crudos cada semana
├── lib/
│   ├── calculate_kpis.py    ← cálculo de KPIs y Top 50
│   ├── generate_xlsx.py     ← genera Excels con 11 pestañas
│   ├── generate_mail.py     ← genera mail unificado
│   └── update_index.py      ← actualiza index.html
└── templates/
    └── mail_template.html   ← template del mail con placeholders
```

**Antes:** ~60 min de trabajo manual cada lunes
**Después:** ~10 min · solo datasets en `inputs/` + 2 comandos + reportes editoriales con Claude

---

## 📊 Severity (5 niveles · CR + RND)

### CheckRates · Eficacia
| Nivel | Rango |
|---|---|
| Exitosa | > 97% |
| Aceptable | 93-97% |
| Revisar | 85-93% |
| Crítica | 60-85% |
| Súper Crítica | < 60% |

### CheckRates · Conv Rate
| Nivel | Rango |
|---|---|
| Exitosa | > 3% |
| Aceptable | 1.74-3% |
| Revisar | 1-1.74% |
| Crítica | 0.5-1% |
| Súper Crítica | < 0.5% |

### Rates No Dispo · %NoDispo
| Nivel | Rango |
|---|---|
| Exitosa | 0-3% |
| Aceptable | 3-5% |
| Revisar | 5-20% |
| Crítica | 20-60% |
| Súper Crítica | > 60% |

---

## 📅 Destinatarios del mail

Rafael Durand · Bellanira Hernandez · Maria Alejandra Rico · Javier Parra · Alonso Mis · Ingrid Kuhnne · David Carrillo · Hugo Ascencio · Jesús Lizarraga · Alejandro Flores · Gabriela Guerra · Barbara Rodriguez

---

## 🐛 Troubleshooting

### "Dataset no encontrado"
El script busca archivos en `_scripts/inputs/` con patrones específicos. Verificá que los nombres incluyan:
- Para CR: `data_set_checkrates_W{NN}.xlsx`
- Para RND: `Week{NN}RatesNoDispo.xlsx`

Si los nombres no coinciden, usá `--cr-input` y `--rnd-input` para pasar paths explícitos.

### "Falta CorpName en RND"
Si el export de RND no incluye CorpName, el script igual genera todo · pero la pestaña "Concentración por Corporativo" del Excel queda con un aviso. **Acción:** pedir al equipo de data que incluya CorpName en el export.

### "Archivos faltantes" al hacer commit
`commit_release.py` valida 8 archivos esperados. Si falta alguno, te dice cuál. Completá lo que falte (típicamente los 2 reportes editoriales HTML que se generan con Claude) y volvé a correr.

### "Error en git push"
Probable conflicto de merge. Hacé `git pull origin main` antes y resolvé.

---

## 📝 Changelog

Ver `_docs/CHANGELOG.md` para el historial completo de releases y cambios estructurales.

**Release actual:** Week 17 (20-26 Abr 2026)
**Próximo release:** Lunes con datos de Week 18

---

## 🎨 Sistema de color

- **CheckRates · accent:** `#5C469C` (violeta)
- **Rates No Dispo · accent:** `#EA0074` (magenta)
- **Paper:** `#F8F4EC`
- **Ink:** `#161616`

Tipografía: Geist (Google Fonts).
