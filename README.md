# PRICE · Scripts de Automatización

Automatización del proceso de release semanal · Supply Optimization.

---

## 🚀 Workflow del lunes (release semanal)

### Pre-requisitos
1. Tener el repo Price clonado localmente
2. Python 3.8+ instalado
3. Dependencias instaladas (1 sola vez):
   ```
   pip install pandas openpyxl
   ```

### Pasos

#### 1. Recibir los 2 datasets crudos
Cada lunes recibís:
- `data_set_checkrates_W{NN}.xlsx` (CheckRates · ~4-5 MB)
- `Week{NN}RatesNoDispo.xlsx` (Rates No Dispo · ~22 MB · **debe tener columna CorpName**)

#### 2. Ponerlos en `_scripts/inputs/`
Copiá los 2 archivos a la carpeta `_scripts/inputs/` del repo Price.

#### 3. Correr el script de generación
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
- ✅ `index.html` (actualizado con KPIs nuevos)

#### 4. Generar reportes editoriales HTML (en Claude)
Esta parte **sigue siendo manual**:
1. Abrir una sesión con Claude
2. Pedir "release W{NN} · CheckRates + Rates No Dispo · datasets en /mnt/project"
3. Claude genera los 2 HTMLs
4. Bajarlos y ponerlos en:
   - `checkrates/week-{NN}/CheckRates_Reporte_Editorial.html`
   - `rates-nodispo/week-{NN}/RatesNoDispo_Reporte_Editorial.html`

#### 5. Commit + Push
```bash
python _scripts/commit_release.py --week 18 --periodo "27 Abr - 3 May 2026"
```

El script:
- Verifica que TODOS los archivos esperados estén en sus rutas
- Si falta alguno, te avisa exactamente cuál
- `git add .`
- `git commit -m "feat: release W18 · 27 Abr - 3 May 2026"`
- `git push origin main`
- Te muestra las URLs públicas

#### 6. Mandar el mail
Abrí `_email/week-18/Mail_W18.html` en Chrome · Ctrl+A · Ctrl+C · pegá en Gmail.

---

## 📁 Estructura

```
_scripts/
├── release_week.py          ← genera Excels + Mail + actualiza index
├── commit_release.py        ← git add + commit + push
├── inputs/                  ← acá poner los 2 datasets crudos cada semana
├── lib/
│   ├── calculate_kpis.py    ← cálculo de KPIs y Top 50
│   ├── generate_xlsx.py     ← genera Excels con 11 pestañas
│   ├── generate_mail.py     ← genera mail unificado
│   └── update_index.py      ← actualiza index.html
├── templates/
│   └── mail_template.html   ← template del mail con placeholders
└── README.md                ← este archivo
```

---

## 🐛 Troubleshooting

### "Dataset CR no encontrado"
El script busca un archivo en `inputs/` que tenga "checkrates" + "W{NN}" en el nombre. Verifica:
- `data_set_checkrates_W18.xlsx` ✅
- `data_set_CheckRates_W18.xlsx` ✅ (case insensitive)
- `checkrates_18.xlsx` ❌ (falta "data_set" o usar `--cr-input` para forzar)

Si el nombre no coincide, usá `--cr-input <path>` explícito.

### "Dataset RND no encontrado"
Mismo principio · busca "nodispo" + "W{NN}" o "Week{NN}".

### "Falta CorpName en RND"
El export del W17 no tenía esa columna. Para futuros releases, asegurate que el export de RND incluya `CorpName`. Si falta, el script igual genera todo pero la pestaña "Concentración por Corp" queda con un aviso.

### "Error en git push"
Probable conflicto de merge. Hacé `git pull origin main` antes y resolvé.

### "Archivos faltantes" al hacer commit
El script `commit_release.py` valida que estén:
- Los 2 reportes editoriales HTML (manual)
- Los 2 Excels (los genera `release_week.py`)
- Los 2 datasets crudos (los copia `release_week.py`)
- El mail HTML (lo genera `release_week.py`)
- index.html

Si falta alguno, completá lo que diga el mensaje y volvé a correr.

---

## 📊 KPIs calculados

### CheckRates
- Hoteles totales · P80 · CK total · BKGS · Eficacia · CR
- Hoteles con 0 BKGS y %
- Severity Eficacia (5 niveles): Exitosa · Aceptable · Revisar · Crítica · Súper Crítica
- Severity CR (5 niveles)
- Top 50 críticos con cluster (Connectivity / Tech / Conversion / Hybrid / Quick Win)
- Concentración por Corporativo con %Portfolio + %Share
- Canastas B2C / OP / CUG (Top 50 cada una)

### Rates No Dispo
- Hoteles activos · P80 · Tráfico · BKGS · GB · %NoDispo ponderado
- Hoteles con 0 BKGS y %
- Severity %NoDispo (5 niveles): 0-3% / 3-5% / 5-20% / 20-60% / >60%
- Top 50 Demanda No Convertida (alto Tráfico · 0 BKGS)
- Concentración por Corporativo (si hay CorpName) · si no, fallback Por Destino
- Top 50 por Destino · Top 50 por País
- Canastas B2C / OP / CUG

---

## 🔧 Configuración avanzada

### Cambiar el template del mail
Editá `_scripts/templates/mail_template.html`. Los placeholders disponibles son:
- `{{WEEK}}` `{{WEEK_PADDED}}` `{{PERIODO}}`
- CR: `{{CR_TOTAL_HOT}}` `{{CR_P80}}` `{{CR_EFICACIA}}` `{{CR_CR}}` `{{CR_TOTAL_CK}}` `{{CR_TOTAL_BKGS}}` `{{CR_ZERO_BKGS}}` `{{CR_ZERO_PCT}}` `{{CR_TOP_CORPS}}` `{{CR_SEV_SUPER}}` `{{CR_SEV_CRITICA}}`
- RND: `{{RND_TOTAL_HOT}}` `{{RND_P80}}` `{{RND_NODISPO}}` `{{RND_TRAFICO}}` `{{RND_BKGS}}` `{{RND_GB}}` `{{RND_ZERO_BKGS}}` `{{RND_ZERO_PCT}}` `{{RND_TOP_CORPS}}` `{{RND_SEV_SUPER}}` `{{RND_SEV_CRITICA}}`

### Modificar el Plan de Acción del Excel
Editá las funciones `generate_cr_xlsx` y `generate_rnd_xlsx` en `_scripts/lib/generate_xlsx.py` · sección "Plan de Acción".

### Cambiar criterios de Severity
Editá las funciones `calculate_cr_kpis` y `calculate_rnd_kpis` en `_scripts/lib/calculate_kpis.py` · diccionarios `severity_eficacia`, `severity_cr`, `severity`.

---

## 📅 Ahorro de tiempo estimado

Antes (manual): ~60 min cada release
Después (automatizado): ~10 min cada release (datasets + reportes editoriales en Claude + 1 comando)

**Ahorro: ~50 min/semana = ~3.5 hs/mes**
