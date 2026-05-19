# 📁 ESTRUCTURA CORRECTA DEL REPO PRICE

**Este documento es la FUENTE DE VERDAD para armar ZIPs**

## ⚠️ REGLA DE ORO - MÁS IMPORTANTE

**RAÍZ = COMPLETAMENTE VACÍA**

```
❌ NO COPIAR NADA A RAÍZ
❌ NO INCLUIR README.md en raíz
❌ NO INCLUIR CHANGELOG.md en raíz
❌ NO INCLUIR PROMPT_MAESTRO_v3.md en raíz
❌ NO INCLUIR NADA en raíz

✅ RAÍZ DEBE ESTAR 100% VACÍA
```

---

## Estructura real en GitHub (federicochurches/Price)

```
Price/
├── _email/                                      ✅ CARPETA EN RAÍZ
│   ├── destinatarios.md
│   └── week-NN/
│       └── Mail_WNN.html
│
├── _governance/                                 ✅ CARPETA EN RAÍZ
│   ├── CHANGELOG.md
│   └── COMMIT_GUIDE.md
│
├── _scripts/                                    ✅ CARPETA EN RAÍZ
│   ├── *.py                                      (28 archivos Python)
│   ├── *.sh                                      (shell scripts)
│   ├── asset_*.html                              (HTML assets)
│   ├── GUIA_EDITORIAL_*.html                     (guías)
│   └── __init__.py
│
├── rates-nodispo/
│   ├── _manual/
│   │   └── GUIA_EDITORIAL_RatesNoDispo.html
│   ├── _template/
│   │   └── _TEMPLATE_RatesNoDispo_Reporte.html
│   └── week-20/                                  ✅ REPORTES + EXCELS W20
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx
│       ├── Analisis_Rates_NoDispo_B2C_7d.xlsx
│       ├── Analisis_Rates_NoDispo_OP_7d.xlsx
│       └── Analisis_Rates_NoDispo_CUG_7d.xlsx
│
└── checkrates/
    ├── _manual/
    │   └── GUIA_EDITORIAL_CheckRates.html
    ├── _template/
    │   └── _TEMPLATE_CheckRates_Reporte.html
    └── week-20/                                  ✅ REPORTES + EXCELS W20
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx
        ├── Analisis_Checkrates_B2C_7d.xlsx
        ├── Analisis_Checkrates_OP_7d.xlsx
        └── Analisis_Checkrates_CUG_7d.xlsx
```

**NOTA:** La raíz está VACÍA. README, CHANGELOG y PROMPT_MAESTRO no van en el repo.

---

## ❌ ARCHIVOS QUE NUNCA VAN EN RAÍZ

```
❌ README.md                 (NO va en repo)
❌ CHANGELOG.md              (NO va en repo, va en _governance/)
❌ PROMPT_MAESTRO_v3.md      (NO va en repo, es documentación local)
❌ FIXES_W20_FINAL.md        (NO va en repo)
❌ READY_W21.md              (NO va en repo)
❌ Cualquier otro .md        (van en _governance/ si es gobernanza)
```

---

## ❌ CARPETAS QUE NO EXISTEN EN REPO Y NUNCA DEBEN IR

- ❌ `_assets/` (NO existe, nunca crear)
- ❌ `_docs/` (NO existe en GitHub, es local en /mnt/project)
- ❌ `_config/` (NO existe, es local)
- ❌ `_helpers/` (NO existe, es local)
- ❌ `_helpers_backup/` (NO existe, es local)

---

## ✅ _GOVERNANCE/ - 2 ARCHIVOS

| Archivo | Origen | Incluir |
|---------|--------|---------|
| `CHANGELOG.md` | /mnt/project/_docs/ | ✅ SÍ |
| `COMMIT_GUIDE.md` | /mnt/project/_docs/ | ✅ SÍ |

---

## ✅ _EMAIL/ - 1 ARCHIVO

| Archivo | Origen | Incluir |
|---------|--------|---------|
| `destinatarios.md` | /mnt/project/destinatarios.md | ✅ SÍ |

---

## ✅ _SCRIPTS/ - 40+ ARCHIVOS

### Python scripts (INCLUIR SIEMPRE)
```
calc_rnd.py, calc_cr.py
render_rnd_p1.py, render_rnd_p2.py, render_rnd_p3.py
render_cr_p1.py, render_cr_p2.py, render_cr_p3.py
excel_rnd.py, excel_cr.py
excel_rnd_canastas.py, excel_cr_canastas.py (NUEVOS W20+)
assemble_rnd.py, assemble_cr.py
engine.py
render_helpers.py
template_resumen.py, template_alertas.py, template_severity.py, template_seguimiento.py
run_pipeline.py
send_email.py
build_package.py
areas_catalogo.py
release_week.py
```

### HTML assets (INCLUIR SIEMPRE en _scripts, NO en _assets)
```
asset_rnd_masthead.html
asset_rnd_head.html
asset_rnd_footer.html
asset_cr_masthead.html
asset_cr_head.html
asset_cr_footer.html
GUIA_EDITORIAL_RatesNoDispo.html
GUIA_EDITORIAL_CheckRates.html
```

### Shell scripts (INCLUIR SIEMPRE)
```
run_pipeline.sh
setup_week.sh
sync_project.sh
package_project.sh
```

---

## ✅ rates-nodispo/week-NN/ - 5 ARCHIVOS

```
RatesNoDispo_Reporte_Editorial.html        ✅ REPORTE FINAL
Analisis_Rates_NoDispo_7d.xlsx              ✅ Global (33 pestañas)
Analisis_Rates_NoDispo_B2C_7d.xlsx          ✅ Canasta B2C (8 pestañas)
Analisis_Rates_NoDispo_OP_7d.xlsx           ✅ Canasta OP (8 pestañas)
Analisis_Rates_NoDispo_CUG_7d.xlsx          ✅ Canasta CUG (8 pestañas)
```

---

## ✅ checkrates/week-NN/ - 5 ARCHIVOS

```
CheckRates_Reporte_Editorial.html           ✅ REPORTE FINAL
Analisis_Checkrates_7d.xlsx                 ✅ Global (37 pestañas)
Analisis_Checkrates_B2C_7d.xlsx             ✅ Canasta B2C (9 pestañas)
Analisis_Checkrates_OP_7d.xlsx              ✅ Canasta OP (9 pestañas)
Analisis_Checkrates_CUG_7d.xlsx             ✅ Canasta CUG (9 pestañas)
```

---

## 🔴 ARCHIVOS QUE NUNCA INCLUIR EN ZIP

```
❌ *.pkl                                     (pickles - temporales, se regeneran)
❌ part*.html                                (parciales HTML - intermedios)
❌ __pycache__/                              (cache de Python)
❌ *.pyc                                     (compiled Python)
❌ Datasets (Dataset_*.xlsx)                 (entrada, no output)
❌ Mail_WNN.html en raíz                     (va en _email/week-NN/)
❌ README.md en raíz                         (NO va en repo)
❌ CHANGELOG.md en raíz                      (va solo en _governance/)
❌ PROMPT_MAESTRO_v3.md en raíz              (NO va en repo)
```

---

## 📋 CHECKLIST PARA ARMAR ZIP (RÁPIDO Y CORRECTO)

```bash
# 0. LIMPIAR ESTRUCTURA TEMPORAL
rm -rf /tmp/Price_Final
mkdir -p /tmp/Price_Final

# 1. CREAR CARPETAS (NO ARCHIVOS EN RAÍZ)
mkdir -p /tmp/Price_Final/_scripts
mkdir -p /tmp/Price_Final/_governance
mkdir -p /tmp/Price_Final/_email
mkdir -p /tmp/Price_Final/rates-nodispo/week-NN
mkdir -p /tmp/Price_Final/checkrates/week-NN

# 2. ❌ NO COPIAR NADA A RAÍZ
# (La raíz queda vacía)

# 3. COPIAR _GOVERNANCE (2 archivos)
cp /mnt/project/_docs/CHANGELOG.md /tmp/Price_Final/_governance/
cp /mnt/project/_docs/COMMIT_GUIDE.md /tmp/Price_Final/_governance/

# 4. COPIAR _EMAIL (1 archivo)
cp /mnt/project/destinatarios.md /tmp/Price_Final/_email/

# 5. COPIAR _SCRIPTS (28 Python + 4 shells + 8 HTML)
cp /mnt/project/_scripts/*.py /tmp/Price_Final/_scripts/
cp /mnt/project/_scripts/*.sh /tmp/Price_Final/_scripts/
cp /mnt/project/_scripts/__init__.py /tmp/Price_Final/_scripts/
cp /mnt/project/_scripts/asset_*.html /tmp/Price_Final/_scripts/
cp /mnt/project/_scripts/GUIA_EDITORIAL_*.html /tmp/Price_Final/_scripts/

# 6. COPIAR REPORTES Y EXCELS
cp /mnt/user-data/outputs/RatesNoDispo_Reporte_Editorial.html /tmp/Price_Final/rates-nodispo/week-NN/
cp /mnt/user-data/outputs/CheckRates_Reporte_Editorial.html /tmp/Price_Final/checkrates/week-NN/
cp /mnt/user-data/outputs/Analisis_Rates_NoDispo_*.xlsx /tmp/Price_Final/rates-nodispo/week-NN/
cp /mnt/user-data/outputs/Analisis_Checkrates_*.xlsx /tmp/Price_Final/checkrates/week-NN/

# 7. CREAR ZIP (sin carpeta contenedora)
cd /tmp/Price_Final && zip -r /mnt/user-data/outputs/Price_WNN_FINAL.zip . -q

# 8. VERIFICAR QUE RAÍZ ESTÁ VACÍA
unzip -l /mnt/user-data/outputs/Price_WNN_FINAL.zip | grep "^.*[A-Z].*\.md$" | grep -v "/" && echo "❌ ERROR: Hay archivos en raíz" || echo "✅ OK: Raíz vacío"

# 9. LIMPIAR
rm -rf /tmp/Price_Final
```

---

## 🎯 RESUMEN EN UNA TABLA

| Qué | Dónde | Incluir | Cantidad |
|-----|-------|---------|----------|
| **RAÍZ** | **VACÍO** | ❌ NO | 0 |
| README.md | Raíz | ❌ NO | 0 |
| CHANGELOG.md | Raíz | ❌ NO | 0 |
| PROMPT_MAESTRO_v3.md | Raíz | ❌ NO | 0 |
| CHANGELOG.md | _governance/ | ✅ SÍ | 1 |
| COMMIT_GUIDE.md | _governance/ | ✅ SÍ | 1 |
| destinatarios.md | _email/ | ✅ SÍ | 1 |
| *.py | _scripts/ | ✅ SÍ | 28 |
| *.sh | _scripts/ | ✅ SÍ | 4 |
| asset_*.html | _scripts/ | ✅ SÍ | 6 |
| GUIA_EDITORIAL_*.html | _scripts/ | ✅ SÍ | 2 |
| __init__.py | _scripts/ | ✅ SÍ | 1 |
| Reporte HTML | rates-nodispo/week-NN/ | ✅ SÍ | 1 |
| Excels RND | rates-nodispo/week-NN/ | ✅ SÍ | 4 |
| Reporte HTML | checkrates/week-NN/ | ✅ SÍ | 1 |
| Excels CR | checkrates/week-NN/ | ✅ SÍ | 4 |
| **TOTAL** | | | **60** |

---

**Última actualización:** Mayo 19, 2026
**Status:** 🟢 ESTRUCTURA CORRECTA DEFINIDA - RAÍZ VACÍA
