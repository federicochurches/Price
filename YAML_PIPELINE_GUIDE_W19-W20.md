# 📋 DOCUMENTACIÓN · FLUJO YAML PIPELINE W19-W20 · Mayo 2026

## 🎯 RESUMEN EJECUTIVO

El pipeline de Supply Optimization ahora se ejecuta **100% automático con configuración YAML centralizada**.

### Antes (W20 sesión inicial):
- 35 min · editar 5 scripts manualmente · 6 pasos manuales
- Config semanal dispersa en múltiples archivos

### Ahora (W19-W20 con YAML):
- **20 min · 1 comando · config YAML única**
- Validación automática de datasets
- Logs detallados con timestamps
- 0 cambios de código necesarios

---

## 📦 ESTRUCTURA DE ARCHIVOS REQUERIDOS

### Directorio: `/mnt/project/`
```
/mnt/project/
├── _scripts/           (scripts Python + assets HTML)
│   ├── calc_rnd.py
│   ├── calc_cr.py
│   ├── render_rnd_p1/2/3.py
│   ├── render_cr_p1/2/3.py
│   ├── assemble_rnd.py
│   ├── assemble_cr.py
│   ├── excel_rnd.py
│   ├── excel_cr.py
│   ├── render_mail_v3.py
│   ├── build_package.py
│   ├── run_pipeline.py          ← NUEVO: orquestador YAML
│   ├── engine.py
│   ├── render_helpers.py
│   ├── template_alertas.py
│   ├── template_resumen.py
│   ├── template_severity.py
│   ├── template_seguimiento.py
│   ├── areas_catalogo.py
│   ├── asset_rnd_head.html
│   ├── asset_rnd_masthead.html
│   ├── asset_rnd_footer.html
│   ├── asset_cr_head.html
│   ├── asset_cr_masthead.html
│   └── asset_cr_footer.html
├── _config/            (NUEVO: config YAML centralizada)
│   ├── WEEK_CONFIG_W19.yml      ← creado sesión W19-W20
│   ├── WEEK_CONFIG_W20.yml      ← creado sesión W19-W20
│   └── WEEK_CONFIG_W21.yml      (ya existía)
├── _docs/              (docs internas)
│   ├── CHANGELOG.md
│   └── COMMIT_GUIDE.md
├── destinatarios.md    (15 destinatarios email)
└── PROMPT_MAESTRO_v3.md
```

### Directorio: `/mnt/user-data/uploads/`
**DATASETS REQUERIDOS (4 por semana):**
```
Dataset_CheckRates_WNN.xlsx        ← semana actual
Dataset_CheckRates_W(NN-1).xlsx    ← semana anterior (para WoW)
Dataset_RatesNoDispo_WNN.xlsx      ← semana actual
Dataset_RatesNoDispo_W(NN-1).xlsx  ← semana anterior (para WoW)
```

**Para W21 necesitarías:**
- Dataset_CheckRates_W21.xlsx
- Dataset_CheckRates_W20.xlsx
- Dataset_RatesNoDispo_W21.xlsx
- Dataset_RatesNoDispo_W20.xlsx

---

## 🔧 CAMBIOS APLICADOS SESIÓN W19-W20

### 1. **run_pipeline.py - CORRECCIÓN DE RUTAS**

**Archivo:** `/mnt/project/_scripts/run_pipeline.py`

**Cambio Línea 181:**
```python
# ANTES:
project_dir = Path(config['paths']['project'])

# AHORA:
project_dir = Path(config['paths']['project']) / '_scripts'
```

**Razón:** Los scripts están en `_scripts/`, no en raíz.

---

### 2. **render_cr_p1.py - REMOVER FALLBACKS HARDCODEADOS**

**Archivo:** `/mnt/project/_scripts/render_cr_p1.py`

**Cambios:**

#### Línea 2 (comentario):
```python
# ANTES:
"""Renderer · Reporte Editorial CR W18"""

# AHORA:
"""Renderer · Reporte Editorial CR W20"""
```

#### Línea 28-29 (remover fallback a W18):
```python
# ANTES:
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', M.get('global_w18', {}))
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', M.get('global_w17', {}))

# AHORA:
M['global_current'] = M.get(f'global_w{WEEK_NUM_INT}', {})
M['global_prev'] = M.get(f'global_w{WEEK_PREV_INT}', {})
```

**Razón:** Fallbacks hardcodeados causaban que W19 mostrara datos de W18.

#### Línea 54-55 (header dinámico):
```python
# ANTES:
<div style="...">Week 18</div>
<div style="...">27 abr – 3 may {MES_AÑO}</div>

# AHORA:
<div style="...">Week {WEEK_NUM}</div>
<div style="...">12-18 may {MES_AÑO}</div>
```

**Razón:** Header debe reflejar semana actual desde YAML.

---

### 3. **excel_cr.py - ORDENAR TODOS LOS EXCELS POR EFICACIA**

**Archivo:** `/mnt/project/_scripts/excel_cr.py`

**Cambios - Global (líneas 130-206):**

| Línea | Pestaña | Antes | Ahora |
|-------|---------|-------|-------|
| 131-133 | Bajo Rendimiento | `sort_values('CR_Unicos', asc=False)` | `sort_values('Eficacia', asc=True)` |
| 141-143 | Sin Conversión | `sort_values('CR_Unicos', asc=False)` | `sort_values('Eficacia', asc=True)` |
| 181 | Por Destino | `sort_values('CR_Unicos', asc=False)` | `sort_values('Eficacia', asc=True)` |
| 191 | Por Channel | `sort_values('CR_Unicos', asc=False)` | `sort_values('Eficacia', asc=True)` |
| 206 | Menor ConvRate | `sort_values('ConvRate')` | `sort_values('Eficacia', asc=True)` |

**Cambios - Canastas (líneas 298-371):**

Idem (todos por Eficacia ascendente):
- Línea 298: Bajo Rendimiento canasta
- Línea 311: Sin Conversión canasta
- Línea 343: Por Destino canasta
- Línea 354: Por Channel canasta
- Línea 371: Menor ConvRate canasta

**Razón:** Todos los Excels ahora muestran hoteles/corps CRÍTICOS primero (eficacia baja).

---

### 4. **CREAR ARCHIVOS CONFIG YAML**

**Archivo: `/mnt/project/_config/WEEK_CONFIG_W19.yml`**
```yaml
week: 19
vol_num: "19"
periodo: "05–11 may 2026"
mes_año: "Mayo 2026"
fecha_pub: "Lunes 12 mayo 2026"

week_prev: 18
vol_num_prev: "18"
periodo_prev: "28 abr–4 may 2026"

week_prev2: 17
vol_num_prev2: "17"
periodo_prev2: "21–27 abr 2026"

paths:
  project: "/mnt/project"
  outputs: "/mnt/user-data/outputs"
  uploads: "/mnt/user-data/uploads"

datasets:
  ratesno_dispo_w19: "Dataset_RatesNoDispo_W19.xlsx"
  ratesno_dispo_w18: "Dataset_RatesNoDispo_W18.xlsx"
  checkrates_w19: "Dataset_CheckRates_W19.xlsx"
  checkrates_w18: "Dataset_CheckRates_W18.xlsx"

pipeline:
  - calc_rnd
  - calc_cr
  - render_rnd
  - render_cr
  - assemble
  - excel
  - mail
  - build_package

verbose: true
abort_on_non_critical_fail: false
```

**Archivo: `/mnt/project/_config/WEEK_CONFIG_W20.yml`**
```yaml
week: 20
vol_num: "20"
periodo: "12–18 may 2026"
mes_año: "Mayo 2026"
fecha_pub: "Lunes 19 mayo 2026"

week_prev: 19
vol_num_prev: "19"
periodo_prev: "05–11 may 2026"

week_prev2: 18
vol_num_prev2: "18"
periodo_prev2: "28 abr–4 may 2026"

paths:
  project: "/mnt/project"
  outputs: "/mnt/user-data/outputs"
  uploads: "/mnt/user-data/uploads"

datasets:
  ratesno_dispo_w20: "Dataset_RatesNoDispo_W20.xlsx"
  ratesno_dispo_w19: "Dataset_RatesNoDispo_W19.xlsx"
  checkrates_w20: "Dataset_CheckRates_W20.xlsx"
  checkrates_w19: "Dataset_CheckRates_W19.xlsx"

pipeline:
  - calc_rnd
  - calc_cr
  - render_rnd
  - render_cr
  - assemble
  - excel
  - mail
  - build_package

verbose: true
abort_on_non_critical_fail: false
```

---

## 🚀 CÓMO EJECUTAR PRÓXIMAS SEMANAS

### Para Week 21 (ejemplo):

**Paso 1:** Crear config YAML
```bash
# Copiar template y editar 7 líneas
cp /mnt/project/_config/WEEK_CONFIG_W20.yml /mnt/project/_config/WEEK_CONFIG_W21.yml

# Editar:
# - week: 21
# - vol_num: "21"
# - periodo: "19–25 may 2026"
# - mes_año: "Mayo 2026"
# - fecha_pub: "Lunes 26 mayo 2026"
# - week_prev: 20, vol_num_prev: "20"
# - datasets: W21 + W20
```

**Paso 2:** Verificar datasets
```bash
ls /mnt/user-data/uploads/Dataset_*W21.xlsx
ls /mnt/user-data/uploads/Dataset_*W20.xlsx
# Deben existir 4 archivos: CheckRates W21/W20 + RatesNoDispo W21/W20
```

**Paso 3:** Ejecutar pipeline (20 minutos)
```bash
cd /mnt/project/_scripts
python3 run_pipeline.py /mnt/project/_config/WEEK_CONFIG_W21.yml
```

**Paso 4:** Validar outputs
```bash
ls -lh /mnt/user-data/outputs/
# CheckRates_Reporte_Editorial.html ← debe decir "Week W21"
# RatesNoDispo_Reporte_Editorial.html ← debe decir "Week W21"
# Analisis_*.xlsx (8 archivos) ← excels ordenados por eficacia
```

**Paso 5:** Commit a GitHub
```bash
unzip /mnt/user-data/outputs/Price_W21.zip -d /tmp/price_repo
cd /tmp/price_repo
git add -A
git commit -m "feat: Week 21 · RatesNoDispo + CheckRates + hub · 26-05-2026"
git push origin main
```

---

## ✅ CHECKLIST PRE-EJECUCIÓN PIPELINE

Antes de correr `python3 run_pipeline.py`, verificar:

- [ ] **Config YAML existe:** `/mnt/project/_config/WEEK_CONFIG_WNN.yml`
- [ ] **Valores YAML correctos:** week, vol_num, periodo, mes_año, fecha_pub
- [ ] **Datasets presentes:**
  - [ ] `Dataset_CheckRates_WNN.xlsx` en `/mnt/user-data/uploads/`
  - [ ] `Dataset_CheckRates_W(NN-1).xlsx` en `/mnt/user-data/uploads/`
  - [ ] `Dataset_RatesNoDispo_WNN.xlsx` en `/mnt/user-data/uploads/`
  - [ ] `Dataset_RatesNoDispo_W(NN-1).xlsx` en `/mnt/user-data/uploads/`
- [ ] **Scripts actualizados:** render_cr_p1.py, excel_cr.py, run_pipeline.py
- [ ] **Limpiar outputs previos:** `rm -f *.pkl /mnt/user-data/outputs/*.html /mnt/user-data/outputs/*.xlsx`

---

## 📊 BANDAS IPM FINALES (CONFIRMADAS W19-W20)

| Banda | Rango | Color | Status |
|-------|-------|-------|--------|
| Sin Conversión | BKGS=0 | #8A8377 gris | ✅ |
| Crítica | < $199 | #C0392B rojo | ✅ |
| Revisar | $200–$499 | #D4A878 amber | ✅ |
| Aceptable | $500–$649 | #5C469C violet | ✅ |
| Exitosa | ≥ $650 | #4FC3F4 cyan | ✅ |

**Archivos que controlan bandas IPM (NO cambiar):**
- `engine.py` (función `banda_rpm()`)
- `render_helpers.py` (gauge 5 niveles)
- `render_rnd_p2.py` (levels_ipm)
- `template_severity.py` (LEVELS_RPM)
- `excel_rnd.py` (iteración bandas ~128 y ~284)

---

## 🐛 BUGS CORREGIDOS SESIÓN W19-W20

| # | Archivo | Fix | Status |
|---|---------|-----|--------|
| #101 | run_pipeline.py | Rutas scripts desde _scripts/ | ✅ |
| #102 | render_cr_p1.py | Remover fallback global_w18 | ✅ |
| #103 | render_cr_p1.py | Header dinámico Week {WEEK_NUM} | ✅ |
| #104 | excel_cr.py | Ordenar Bajo Rend por Eficacia | ✅ |
| #105 | excel_cr.py | Ordenar Sin Conv por Eficacia | ✅ |
| #106 | excel_cr.py | Ordenar Por Dest por Eficacia | ✅ |
| #107 | excel_cr.py | Ordenar Por Channel por Eficacia | ✅ |
| #108 | excel_cr.py | Ordenar Menor ConvRate por Eficacia | ✅ |
| #109 | excel_cr.py | Idem canastas (5 pestañas × 3 canastas) | ✅ |

---

## 📝 PRÓXIMAS ACCIONES POST-W20

- [ ] Investigar discrepancia Iberostar eficacia (85.56% dataset vs 99.25% excel OP)
- [ ] Verificar si P80 o filtros en calc_cr.py causan la discrepancia
- [ ] Documentar si es comportamiento esperado o bug
- [ ] Hacer render_mail_v3.py compatible con W19 (requiere global_w17)

---

## 🎓 LECCIONES APRENDIDAS

1. **Pickles cacheados:** SIEMPRE `rm -f *.pkl` antes de regenerar
2. **Fallbacks hardcodeados:** PELIGRO - usan datos de semana vieja
3. **Config centralizada:** YAML > múltiples scripts manuales
4. **Validación datasets:** Pipeline rechaza ejecución si faltan datasets
5. **Rutas relativas:** Usar Path() para compatibilidad cross-platform

---

**Última actualización:** 19 mayo 2026 · W19-W20 · YAML Pipeline funcional
**Próxima revisión:** W21 (si aplican cambios)
