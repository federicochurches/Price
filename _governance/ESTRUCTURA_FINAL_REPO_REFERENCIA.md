# 📋 ESTRUCTURA FINAL DEL REPO · Referencia para build_package.py

**Última actualización:** Mayo 2026
**Status:** ✅ Estructura consolidada y documentada
**Aplica a:** Todos los ZIPs generados a partir de W21+

---

## 🏗️ ESTRUCTURA CORRECTA DEL REPOSITORIO

```
Price/
│
├─ 📄 index.html                  ← Hub público (ÚNICA excepción en raíz)
├─ 📄 README.md                   ← Overview (ÚNICA excepción en raíz)
├─ 📄 .gitignore                  ← Git config (ÚNICA excepción en raíz)
│
├─ 📁 _scripts/                   ← SCRIPTS PRINCIPALES (25+ archivos)
│  ├─ run_pipeline.py             ← Orquestador YAML (principal)
│  ├─ calc_rnd.py
│  ├─ calc_cr.py
│  ├─ render_rnd_p1.py
│  ├─ render_rnd_p2.py
│  ├─ render_rnd_p3.py
│  ├─ render_cr_p1.py
│  ├─ render_cr_p2.py
│  ├─ render_cr_p3.py
│  ├─ render_mail_v3.py
│  ├─ assemble_rnd.py
│  ├─ assemble_cr.py
│  ├─ excel_rnd.py
│  ├─ excel_cr.py
│  ├─ build_package.py
│  └─ (otros scripts y carpetas internas)
│
├─ 📁 _helpers/                   ← FUNCIONES COMPARTIDAS (7 archivos)
│  ├─ engine.py
│  ├─ render_helpers.py
│  ├─ template_resumen.py
│  ├─ template_alertas.py
│  ├─ template_severity.py
│  ├─ template_seguimiento.py
│  └─ areas_catalogo.py
│
├─ 📁 _assets/                    ← ASSETS HTML (8 archivos)
│  ├─ asset_rnd_head.html
│  ├─ asset_rnd_masthead.html
│  ├─ asset_rnd_footer.html
│  ├─ asset_cr_head.html
│  ├─ asset_cr_masthead.html
│  ├─ asset_cr_footer.html
│  ├─ GUIA_EDITORIAL_RatesNoDispo.html
│  └─ GUIA_EDITORIAL_CheckRates.html
│
├─ 📁 _config/                    ← CONFIGURACIÓN SEMANAL (2+ archivos)
│  ├─ WEEK_CONFIG_W21.yml
│  ├─ WEEK_CONFIG_W22.yml
│  └─ (W23, W24, etc.)
│
├─ 📁 _docs/                      ← DOCUMENTACIÓN (13+ archivos)
│  ├─ PROMPT_MAESTRO_v3.md
│  ├─ GETTING_STARTED_W21.md
│  ├─ YAML_PIPELINE_GUIDE.md
│  ├─ IMPLEMENTACION_YAML_COMPLETADA.md
│  ├─ QUICK_REFERENCE_YAML.md
│  ├─ ESTRUCTURA_TEMPLATE.md
│  ├─ MAPA_DEPENDENCIAS.md
│  ├─ Playbook_Mail_Semanal.md
│  └─ (otros .md de documentación)
│
├─ 📁 _governance/                ← GOVERNANCE Y AUDITORÍA (15+ archivos)
│  ├─ CHANGELOG.md
│  ├─ COMMIT_GUIDE.md
│  ├─ audit_w20.md
│  ├─ CHECKLIST_PROYECTO_CLAUDE.md
│  ├─ ESTADO_DOCUMENTACION_ACTUALIZADO.md
│  ├─ STATUS_FINAL_W20.md
│  ├─ READY_W20.md
│  ├─ NIVEL_C_PENDIENTE.md
│  └─ _seguimiento/
│     └─ plan_seguimiento_WNN.md
│
├─ 📁 checkrates/                 ← REPORTES CR (EXISTÍA ANTES)
│  ├─ _manual/
│  │  └─ GUIA_EDITORIAL_CheckRates.html
│  └─ week-NN/
│     ├─ CheckRates_Reporte_Editorial.html
│     ├─ Analisis_Checkrates_7d.xlsx
│     ├─ Analisis_Checkrates_B2C_7d.xlsx
│     ├─ Analisis_Checkrates_OP_7d.xlsx
│     ├─ Analisis_Checkrates_CUG_7d.xlsx
│     └─ Dataset_CheckRates_WNN.xlsx
│
├─ 📁 rates-nodispo/              ← REPORTES RND (EXISTÍA ANTES)
│  ├─ _manual/
│  │  └─ GUIA_EDITORIAL_RatesNoDispo.html
│  └─ week-NN/
│     ├─ RatesNoDispo_Reporte_Editorial.html
│     ├─ Analisis_Rates_NoDispo_7d.xlsx
│     ├─ Analisis_Rates_NoDispo_B2C_7d.xlsx
│     ├─ Analisis_Rates_NoDispo_OP_7d.xlsx
│     ├─ Analisis_Rates_NoDispo_CUG_7d.xlsx
│     └─ Dataset_RatesNoDispo_WNN.xlsx
│
├─ 📁 _email/                     ← MAILS (EXISTÍA ANTES)
│  └─ week-NN/
│     └─ Mail_WNN.html
│
└─ (NO EN RAÍZ · generados localmente)
   ├─ rnd_wNN_data.pkl            ← Pickles (NO en repo)
   ├─ cr_wNN_data.pkl             ← Pickles (NO en repo)
   └─ Dataset_*.xlsx              ← Datasets (NO en repo inicial)

```

---

## ✅ REGLAS DE ESTRUCTURA

### **QUÉ VA EN RAÍZ (SOLO 3):**
- ✅ `index.html` (hub público)
- ✅ `README.md` (overview)
- ✅ `.gitignore` (config git)

### **NUNCA EN RAÍZ:**
- ❌ Archivos .py (van a `_scripts/`)
- ❌ Archivos .md de documentación (van a `_docs/` o `_governance/`)
- ❌ Archivos .yml de config (van a `_config/`)
- ❌ Archivos HTML de assets (van a `_assets/`)
- ❌ Pickles o datasets grandes (no comitear)

### **CARPETAS OBLIGATORIAS:**
- ✅ `_scripts/` (scripts principales)
- ✅ `_helpers/` (funciones compartidas)
- ✅ `_assets/` (assets HTML)
- ✅ `_config/` (WEEK_CONFIG_*.yml)
- ✅ `_docs/` (documentación de usuario)
- ✅ `_governance/` (auditoría y cambios)
- ✅ `checkrates/` (reportes CR)
- ✅ `rates-nodispo/` (reportes RND)
- ✅ `_email/` (mails)

---

## 🔄 IMPLICACIONES PARA build_package.py

### **Cambios necesarios en build_package.py:**

1. **NO incluir en ZIP:**
   ```python
   EXCLUDE_FILES = [
       '*.pkl',                          # Pickles
       'Dataset_*.xlsx',                 # Datasets grandes
       '.backup_*',                      # Backups
       '__pycache__',                    # Cache Python
       '.git',                           # Repo git
       'inputs/',                        # Carpetas de trabajo
   ]
   ```

2. **Verificar estructura antes de empaquetar:**
   ```python
   REQUIRED_FOLDERS = [
       '_scripts',
       '_helpers',
       '_assets',
       '_config',
       '_docs',
       '_governance',
       'checkrates',
       'rates-nodispo',
       '_email',
   ]
   
   MUST_BE_IN_ROOT = [
       'index.html',
       'README.md',
       '.gitignore',
   ]
   
   MUST_NOT_BE_IN_ROOT = [
       '*.py',
       '*.md',
       '*.yml',
   ]
   ```

3. **Validar en cada generación de ZIP:**
   ```python
   def validate_structure():
       for folder in REQUIRED_FOLDERS:
           if not os.path.exists(folder):
               raise FileNotFoundError(f"Carpeta obligatoria faltante: {folder}")
       
       # Verificar que no hay archivos sueltos en raíz
       for file in glob.glob('*.py'):
           if file != 'run_pipeline.py':  # Excepción temporal
               raise FileExistsError(f"Archivo {file} no debería estar en raíz")
   ```

---

## 📊 CAMBIOS DESDE W20 A W21+

| Aspecto | W20 | W21+ |
|--------|-----|------|
| **Archivos en raíz** | 65+ (caótico) | 3 (limpio) |
| **Carpetas organizadas** | No | Sí (8 carpetas) |
| **run_pipeline.py ubicación** | Raíz | `_scripts/` |
| **Configs YAML** | Scattered | `_config/` |
| **Documentación** | Raíz + scattered | `_docs/` + `_governance/` |
| **Scripts** | Raíz | `_scripts/` |
| **Helpers** | Raíz | `_helpers/` |
| **Assets** | Raíz | `_assets/` |

---

## 🚀 PARA FUTUROS ZIPs (W21+)

### **Checklist de build_package.py:**

```python
# Antes de generar ZIP:
□ Validar que _scripts/, _helpers_, _assets_, _config/, _docs/, _governance/ existen
□ Verificar que raíz contiene SOLO: index.html, README.md, .gitignore
□ Eliminar o no incluir: pickles, datasets grandes, .backup_*, __pycache__
□ Generar ZIP sin duplicados
□ Incluir documentación YAML en ZIP (si no está)
□ Generar log de estructura (qué se incluyó, qué no)
□ Producir resumen: "ZIP listo para descomprimir directamente en raíz del repo"
```

### **Comando post-generación:**

```bash
# Después de generar Price_WNN.zip:
unzip -l Price_WNN.zip | grep -E "^(Archive|  .*/)" | head -50
# Verificar que la estructura es correcta
```

---

## 📝 NOTAS IMPORTANTES

1. **Los ZIPs deben ser descomprimibles directamente en la raíz del repo** sin crear subcarpetas.

2. **No incluir archivos temporales** en el ZIP (pickles, datasets, backups).

3. **Documentación siempre en carpetas**, nunca en raíz.

4. **La estructura es ahora ESTÁNDAR** para W21, W22, W23, etc.

5. **Si algo no está en su carpeta correcta**, build_package.py debe advertir o rechazar la generación.

---

## ✅ ESTRUCTURA VALIDADA

Esta estructura fue implementada en **Mayo 2026** y está lista para:
- ✅ W21+ sin cambios
- ✅ GitHub Pages hosting
- ✅ CI/CD pipelines
- ✅ Escalabilidad futura

**NUNCA volver a tener 65+ archivos caóticos en raíz.**

