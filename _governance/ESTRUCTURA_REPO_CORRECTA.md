# 📁 ESTRUCTURA CORRECTA DEL REPO PRICE

**Este documento es la FUENTE DE VERDAD para armar ZIPs**

## Estructura real en GitHub (federicochurches/Price)

```
Price/
├── README.md                                    ✅ RAÍZ
├── CHANGELOG.md                                 ✅ RAÍZ (ACTUALIZAR AQUÍ)
├── PROMPT_MAESTRO_v3.md                         ✅ RAÍZ (si existe)
│
├── _email/                                      ✅ CARPETA EN RAÍZ
│   └── week-NN/
│       └── Mail_WNN.html
│
├── _governance/                                 ✅ CARPETA EN RAÍZ
│   ├── CHANGELOG.md                              (copy de raíz)
│   └── COMMIT_GUIDE.md
│
├── _scripts/                                    ✅ CARPETA EN RAÍZ (LOCAL)
│   ├── *.py                                      (40+ archivos Python)
│   ├── *.sh                                      (shell scripts)
│   ├── asset_*.html                              (HTML assets VAN AQUÍ)
│   ├── GUIA_EDITORIAL_*.html                     (guías VAN AQUÍ)
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
│       ├── Analisis_Rates_NoDispo_CUG_7d.xlsx
│       └── Dataset_RatesNoDispo_W20.xlsx         (opcional)
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
        ├── Analisis_Checkrates_CUG_7d.xlsx
        └── Dataset_CheckRates_W20.xlsx           (opcional)
```

---

## ❌ CARPETAS QUE NO EXISTEN EN REPO Y NUNCA DEBEN IR

- ❌ `_assets/` (NO existe, nunca crear)
- ❌ `_docs/` (NO existe en GitHub, es local en /mnt/project)
- ❌ `_config/` (NO existe, es local)
- ❌ `_helpers/` (NO existe, es local)
- ❌ `_helpers_backup/` (NO existe, es local)

---

## ✅ ARCHIVOS QUE VAN EN RAÍZ

| Archivo | Qué hace | Incluir en ZIP |
|---------|----------|----------------|
| `README.md` | Descripción del proyecto | ✅ SÍ |
| `CHANGELOG.md` | Historial de cambios | ✅ SÍ (ACTUALIZAR) |
| `PROMPT_MAESTRO_v3.md` | Documentación del proyecto | ✅ SÍ (si existe) |
| `FIXES_W20_FINAL.md` | Guía de bugs W20 | ⚠️ SOLO para W20 |
| `READY_W21.md` | Guía ejecutable W21 | ⚠️ SOLO para W21+ |

---

## ✅ ARCHIVOS QUE VAN EN _GOVERNANCE/

| Archivo | Origen | Incluir en ZIP |
|---------|--------|----------------|
| `CHANGELOG.md` | Copy de raíz | ✅ SÍ |
| `COMMIT_GUIDE.md` | Copy de /mnt/project/_docs | ✅ SÍ |
| `EXCLUSIONES_ZIP.md` | Copy de /mnt/project/_docs | ❓ OPCIONAL |

---

## ✅ ARCHIVOS QUE VAN EN _EMAIL/

| Archivo | Origen | Incluir en ZIP |
|---------|--------|----------------|
| `destinatarios.md` | Lista de 15 destinatarios | ✅ SÍ |
| `week-NN/Mail_WNN.html` | Mail generado semanal | ✅ SÍ (generado) |

---

## ✅ ARCHIVOS QUE VAN EN _SCRIPTS/

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
asset_rnd_masthead.html ✅ (actualizado W20: fecha removida)
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

## ✅ ARCHIVOS QUE VAN EN rates-nodispo/week-NN/

```
RatesNoDispo_Reporte_Editorial.html        ✅ REPORTE FINAL
Analisis_Rates_NoDispo_7d.xlsx              ✅ Global (33 pestañas)
Analisis_Rates_NoDispo_B2C_7d.xlsx          ✅ Canasta B2C (8 pestañas)
Analisis_Rates_NoDispo_OP_7d.xlsx           ✅ Canasta OP (8 pestañas)
Analisis_Rates_NoDispo_CUG_7d.xlsx          ✅ Canasta CUG (8 pestañas)
```

---

## ✅ ARCHIVOS QUE VAN EN checkrates/week-NN/

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
❌ Archivos de /mnt/project/ no mencionados  (son locales, no repo)
```

---

## 📋 CHECKLIST PARA ARMAR ZIP

Antes de crear un ZIP, verificar:

```bash
# 1. Copiar SOLO estos archivos a raíz
✅ README.md
✅ CHANGELOG.md (ACTUALIZADO con entrada WNN)
✅ PROMPT_MAESTRO_v3.md (si existe)

# 2. Copiar SOLO estos a _governance/
✅ _governance/CHANGELOG.md (copy de raíz)
✅ _governance/COMMIT_GUIDE.md

# 3. Copiar a _email/
✅ _email/destinatarios.md

# 4. Copiar a _scripts/ (40+ archivos)
✅ _scripts/*.py (todos los scripts)
✅ _scripts/*.sh (todos los shells)
✅ _scripts/asset_*.html (HTML assets)
✅ _scripts/GUIA_EDITORIAL_*.html
✅ _scripts/__init__.py

# 5. Copiar a rates-nodispo/week-NN/
✅ RatesNoDispo_Reporte_Editorial.html
✅ Analisis_Rates_NoDispo_7d.xlsx
✅ Analisis_Rates_NoDispo_B2C_7d.xlsx
✅ Analisis_Rates_NoDispo_OP_7d.xlsx
✅ Analisis_Rates_NoDispo_CUG_7d.xlsx

# 6. Copiar a checkrates/week-NN/
✅ CheckRates_Reporte_Editorial.html
✅ Analisis_Checkrates_7d.xlsx
✅ Analisis_Checkrates_B2C_7d.xlsx
✅ Analisis_Checkrates_OP_7d.xlsx
✅ Analisis_Checkrates_CUG_7d.xlsx

# 7. Limpiar ANTES de zipar
❌ Eliminar *.pkl
❌ Eliminar part*.html
❌ Eliminar __pycache__/
❌ Eliminar *.pyc
❌ Eliminar _assets/ (NO EXISTE en repo)
❌ Eliminar _docs/ (NO EXISTE en repo)
❌ Eliminar _config/ (NO EXISTE en repo)
❌ Eliminar _helpers* (NO EXISTEN en repo)

# 8. Crear ZIP sin carpeta contenedora
cd /tmp/Price_Final && zip -r ../Price_WNN_FINAL.zip . -q
```

---

## 🎯 RESUMEN

| Qué | Dónde | Incluir ZIP |
|-----|-------|------------|
| Scripts Python | `_scripts/` | ✅ SÍ |
| HTML assets | `_scripts/` | ✅ SÍ (NO en _assets) |
| Shell scripts | `_scripts/` | ✅ SÍ |
| README, CHANGELOG, PROMPT | Raíz | ✅ SÍ |
| CHANGELOG copy | `_governance/` | ✅ SÍ |
| COMMIT_GUIDE | `_governance/` | ✅ SÍ |
| destinatarios.md | `_email/` | ✅ SÍ |
| Reportes HTML | `rates-nodispo/week-NN/` | ✅ SÍ |
| Excels RND | `rates-nodispo/week-NN/` | ✅ SÍ |
| Reportes HTML | `checkrates/week-NN/` | ✅ SÍ |
| Excels CR | `checkrates/week-NN/` | ✅ SÍ |
| **Pickles** | **NINGÚN LADO** | ❌ NO |
| **Parciales HTML** | **NINGÚN LADO** | ❌ NO |
| **_assets/** | **NO EXISTE** | ❌ NO |
| **_docs/** | **NO EXISTE** | ❌ NO |
| **_config/** | **NO EXISTE** | ❌ NO |

---

**Última actualización:** Mayo 19, 2026
**Status:** 🟢 ESTRUCTURA CORRECTA DEFINIDA
