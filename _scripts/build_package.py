"""
Paquete W18 · Nivel B
- Carpetas week-18/ con archivos correspondientes
- Hub (index.html) actualizado con cards W18 + W17 movido a archivo
- README_REPO.md actualizado con W18 y nota sobre fixes consolidados
- NIVEL_C_PENDIENTE.md documentando qué queda para W19
"""
import shutil, os
from pathlib import Path

ROOT = Path('/home/claude/repo_W18')
if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir()

# ============================================================================
# 1. ESTRUCTURA DE CARPETAS
# ============================================================================
print("Creando estructura de carpetas...")
(ROOT / 'rates-nodispo' / 'week-18').mkdir(parents=True)
(ROOT / 'checkrates' / 'week-18').mkdir(parents=True)
(ROOT / '_email' / 'week-18').mkdir(parents=True)

# ============================================================================
# 2. COPIAR ARCHIVOS DE W18 A LAS CARPETAS CORRESPONDIENTES
# ============================================================================
print("Copiando deliverables W18...")

# RND
shutil.copy('/mnt/user-data/outputs/Supply_RatesNoDispo_W18.html',
            ROOT / 'rates-nodispo' / 'week-18' / 'RatesNoDispo_Reporte_Editorial.html')
shutil.copy('/mnt/user-data/outputs/Analisis_Rates_NoDispo_W18.xlsx',
            ROOT / 'rates-nodispo' / 'week-18' / 'Analisis_Rates_NoDispo_7d.xlsx')
shutil.copy('/mnt/user-data/uploads/Dataset_RatesNoDispo_W18.xlsx',
            ROOT / 'rates-nodispo' / 'week-18' / 'Dataset_RatesNoDispo_W18.xlsx')

# CR
shutil.copy('/mnt/user-data/outputs/Supply_CheckRates_W18.html',
            ROOT / 'checkrates' / 'week-18' / 'CheckRates_Reporte_Editorial.html')
shutil.copy('/mnt/user-data/outputs/Analisis_CheckRates_W18.xlsx',
            ROOT / 'checkrates' / 'week-18' / 'Analisis_Checkrates_7d.xlsx')
shutil.copy('/mnt/user-data/uploads/Dataset_CheckRates_W18.xlsx',
            ROOT / 'checkrates' / 'week-18' / 'Dataset_CheckRates_W18.xlsx')

# Mail
shutil.copy('/mnt/user-data/outputs/Mail_W18.html',
            ROOT / '_email' / 'week-18' / 'Mail_W18.html')

print("✓ Archivos copiados")

# ============================================================================
# 3. HUB (index.html) actualizado con W18 + W17 movido a archivo
# ============================================================================
print("Generando index.html (hub W18)...")

template_hub = open('/mnt/project/_TEMPLATE_Hub.html').read()

# Reemplazar placeholders
hub = template_hub
hub = hub.replace('{{SEMANA}}', 'Week 18')
hub = hub.replace('{{SEMANA_RAW}}', 'Week18')
hub = hub.replace('{{WEEK_NUM_RAW}}', 'week-18')
hub = hub.replace('{{WEEK_LABEL}}', 'Week 18')
hub = hub.replace('{{PERIODO}}', '27 Abr – 3 May 2026')
hub = hub.replace('{{MES_ANO}}', 'May 2026')
hub = hub.replace('{{ND_META}}', '%NoDispo 3,01% · RPM 479,70 · 11.954 P80 sin BKGS')
hub = hub.replace('{{CK_META}}', 'Eficacia 94,36% · ConvRate 1,38% · Third Party Crítica')

# Fixear paths de cards activas: el template original apunta a Editorial/ subfolder pero los archivos van sueltos
hub = hub.replace(
    'rates-nodispo/week-18/Editorial/RatesNoDispo_Reporte_Editorial.html',
    'rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html')
hub = hub.replace(
    'checkrates/week-18/Editorial/CheckRates_Reporte_Editorial_Week18.html',
    'checkrates/week-18/CheckRates_Reporte_Editorial.html')

# Mover W17 al archivo · agregar W17 a los grupos archivo y reactivar W16
# El template viene con Week 16 activo + Week 15 disabled · ahora queremos:
# - Week 18 = card activa (ya configurado)
# - Archivo: Week 17 active, Week 16 active, Week 15 disabled

# Bloque RND archivo (reemplazar)
old_rnd_archivo = '''      <div class="archivo-grupo">
        <div class="archivo-label" style="color:#EA0074;">Supply Rates No Dispo</div>
        <a href="rates-nodispo/week-16/Editorial/RatesNoDispo_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 16</span>
          <span class="archivo-periodo">13–19 Abr 2026</span>
        </a>
        <a href="rates-nodispo/week-15/Editorial/RatesNoDispo_Reporte_Editorial.html" class="archivo-link archivo-disabled">
          <span class="archivo-week">Week 15</span>
          <span class="archivo-periodo">6–12 Abr 2026</span>
        </a>
      </div>'''

new_rnd_archivo = '''      <div class="archivo-grupo">
        <div class="archivo-label" style="color:#EA0074;">Supply Rates No Dispo</div>
        <a href="rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 17</span>
          <span class="archivo-periodo">20–26 Abr 2026</span>
        </a>
        <a href="rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 16</span>
          <span class="archivo-periodo">13–19 Abr 2026</span>
        </a>
        <a href="rates-nodispo/week-15/RatesNoDispo_Reporte_Editorial.html" class="archivo-link archivo-disabled">
          <span class="archivo-week">Week 15</span>
          <span class="archivo-periodo">6–12 Abr 2026</span>
        </a>
      </div>'''

hub = hub.replace(old_rnd_archivo, new_rnd_archivo)

# Bloque CR archivo (reemplazar)
old_cr_archivo = '''      <div class="archivo-grupo">
        <div class="archivo-label" style="color:#5C469C;">Supply CheckRates</div>
        <a href="checkrates/week-16/Editorial/CheckRates_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 16</span>
          <span class="archivo-periodo">13–19 Abr 2026</span>
        </a>
        <a href="checkrates/week-15/Editorial/CheckRates_Reporte_Editorial.html" class="archivo-link archivo-disabled">
          <span class="archivo-week">Week 15</span>
          <span class="archivo-periodo">6–12 Abr 2026</span>
        </a>
      </div>'''

new_cr_archivo = '''      <div class="archivo-grupo">
        <div class="archivo-label" style="color:#5C469C;">Supply CheckRates</div>
        <a href="checkrates/week-17/CheckRates_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 17</span>
          <span class="archivo-periodo">20–26 Abr 2026</span>
        </a>
        <a href="checkrates/week-16/CheckRates_Reporte_Editorial.html" class="archivo-link">
          <span class="archivo-week">Week 16</span>
          <span class="archivo-periodo">13–19 Abr 2026</span>
        </a>
        <a href="checkrates/week-15/CheckRates_Reporte_Editorial.html" class="archivo-link archivo-disabled">
          <span class="archivo-week">Week 15</span>
          <span class="archivo-periodo">6–12 Abr 2026</span>
        </a>
      </div>'''

hub = hub.replace(old_cr_archivo, new_cr_archivo)

(ROOT / 'index.html').write_text(hub, encoding='utf-8')
print("✓ index.html generado")

# ============================================================================
# 4. README_REPO.md (separado del prompt maestro · documentación del repo)
# ============================================================================
print("Generando README_REPO.md...")
readme = '''# PRICE · Supply Optimization · Weekly Reports

Reportes semanales de **Supply CheckRates** y **Supply Rates No Dispo** para PriceTravel.

URL pública: https://federicochurches.github.io/Price/

## 📦 Última edición

**Week 18 · 27 Abr – 3 May 2026 · Vol. 04**

- 📊 [Supply Rates No Dispo](rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html) · %NoDispo 3,01% (Aceptable, ▼0,88pp WoW) · RPM 479,70
- 📊 [Supply CheckRates](checkrates/week-18/CheckRates_Reporte_Editorial.html) · Eficacia 94,36% · ConvRate 1,38% (Revisar, ▼0,12pp WoW)

## 📁 Estructura del repo

```
Price/
├── index.html              ← Hub público con cards de la última semana
├── README.md               ← Este archivo
├── _email/                 ← (NO se publica · solo local) mails semanales
├── _scripts/               ← (NO se publica · solo local) scripts de procesamiento
├── _template/
│   └── _TEMPLATE_Hub.html
├── rates-nodispo/
│   ├── _manual/GUIA_EDITORIAL_RatesNoDispo.html
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html  ← deliverable público
│       ├── Analisis_Rates_NoDispo_7d.xlsx       ← Excel Top 50 (13 pestañas)
│       └── Dataset_RatesNoDispo_WNN.xlsx        ← dataset crudo
└── checkrates/
    ├── _manual/GUIA_EDITORIAL_CheckRates.html
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx           ← Excel Top 50 (17 pestañas)
        └── Dataset_CheckRates_WNN.xlsx
```

## 🔄 Sistema de bandas D · vigente desde Week 18

A partir de Week 18 se aplican las decisiones consolidadas post-W17 (ver `FIXES_PENDIENTES_W18.md`):

- **Sistema bandas D · 5 niveles separando "Sin Conversión" de Severity**
  - Hoteles con BKGS = 0 son cohorte estructural aparte (diagnóstico técnico/contractual)
  - Severity solo aplica a hoteles procesables (BKGS > 0)
- **Plan de Acción reordenado** · badge owner como protagonista, cluster (Quick Win · Mid · Estratégica) y código de seguimiento van debajo
- **Plan de Acción dentro de cada canasta** · cada canasta (B2C · B2B-OP · CUG) tiene 6 acciones específicas
- **Channel agrupado destacado en CR** · Producto Propio vs Third Party
- **Capitalización editorial** · todos los findings arrancan con mayúscula
- **Excels estandarizados** · CR 17 pestañas (incluyen Por Destino y Por Channel) · RND 13 pestañas
- **Datasets single-sheet** · una fila por combinación Hotel × Canasta (× Channel para CR)

> **Nota sobre auditoría histórica:** Las semanas anteriores a W18 (W15, W16, W17) usan el formato anterior. No se regeneraron retroactivamente para preservar la trazabilidad de lo que efectivamente se envió a los destinatarios cada semana.

## 📅 Workflow semanal

1. Recibir datasets Week-NN (single-sheet) → guardar en `{seccion}/week-NN/Dataset_*.xlsx`
2. Procesar con scripts → generar Excels de análisis (Top 50) y reportes editoriales
3. Commit a `rates-nodispo/week-NN/` y `checkrates/week-NN/`
4. Actualizar `index.html` con cards Week-NN
5. Generar mail desde `_email/week-NN/Mail_WNN.html`
6. Enviar a 12 destinatarios en BCC (ver `destinatarios.md` local)

## 📌 Próximos cambios estructurales (Week 19)

Ver `NIVEL_C_PENDIENTE.md` para el plan de actualización de templates, guías editoriales y playbook que se aplicarán post-feedback de W18.

---

**PriceTravel · Supply Optimization**  
Última actualización: Mayo 2026 · post W18
'''
(ROOT / 'README.md').write_text(readme, encoding='utf-8')
print("✓ README.md generado")

# ============================================================================
# 5. NIVEL_C_PENDIENTE.md (qué queda para W19)
# ============================================================================
print("Generando NIVEL_C_PENDIENTE.md...")
nivel_c = '''# 📋 NIVEL C · Pendientes para Week 19

> **Decisión post W18:** los archivos correctos para esta semana se publicaron como Nivel B (deliverables + hub + README). Los templates y guías editoriales NO se actualizaron en W18 para dar tiempo a recoger feedback de los 12 destinatarios sobre el nuevo formato antes de cristalizar la documentación de proceso.
> 
> **Aplicar en W19** una vez tengamos respuestas/observaciones del equipo.

---

## ✅ Aplicado en W18 (Nivel B)

- Carpetas `rates-nodispo/week-18/` y `checkrates/week-18/` creadas con sus 3 archivos cada una (reporte editorial + Excel análisis + dataset crudo)
- Carpeta `_email/week-18/` con `Mail_W18.html` (estructura ejecutiva: resumen + plan acción consolidado por owner)
- `index.html` actualizado con cards W18 activas y W17 movido al archivo
- `README.md` del repo actualizado con W18 y nota sobre vigencia del sistema de bandas D
- Reportes editoriales y Excels generados con los 11 fixes post-W17 aplicados (sistema bandas D, badge owner protagonista, plan acción dentro de canasta, capitalización findings, Excels 17/13 pestañas, etc.)

## 🔧 Pendiente para W19 (Nivel C)

### 1. Actualizar templates HTML

**`_template/_TEMPLATE_Hub.html`**
- Validar si la estructura de cards y archivo sigue funcionando bien después de tener varias semanas con el formato nuevo
- Considerar mostrar 4-5 semanas en archivo (no solo 2) ahora que la cadencia es estable

**`rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte.html`**
- Refactorizar para reflejar la estructura W18:
  - Plan de Acción con badge owner como protagonista (no Quick Win/Cluster arriba)
  - Bloque "Plan de Acción · canasta {X}" dentro de cada `<details>` de canasta
  - Findings del Resumen Ejecutivo capitalizados desde el template
  - CSS de `.action-row` con `action-owner-badge` y `action-meta-bottom`
- Considerar si los placeholders existentes siguen sirviendo o conviene rehacerlos

**`checkrates/_template/_TEMPLATE_CheckRates_Reporte.html`**
- Mismas refactorizaciones que RND
- Asegurar que el bloque "Channel agrupado" (Producto Propio vs Third Party) esté en el template
- Tab Channel debe traer todos los providers (Omnibees etc · Fix #6)

### 2. Actualizar guías editoriales

**`rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html`**
- Documentar el sistema de bandas D · 5 niveles separando Sin Conversión
- Documentar la regla "Plan de Acción dentro de cada canasta"
- Documentar formato Excel estándar 13 pestañas
- Actualizar el ejemplo de Plan de Acción con la nueva estructura (owner arriba)

**`checkrates/_manual/GUIA_EDITORIAL_CheckRates.html`**
- Mismas actualizaciones que RND
- Documentar Channel agrupado (Producto Propio vs Third Party)
- Documentar formato Excel estándar 17 pestañas (vs 14 anterior)
- Documentar regla "Tab Channel debe traer todos los providers"

### 3. Actualizar playbook del mail

**`Playbook_Mail_Semanal.md`**
- Documentar el nuevo formato ejecutivo del mail (vs el formato W17 con KPI strips + 5 hallazgos por reporte)
- Estructura: Resumen ejecutivo + Plan de acción consolidado por owner + Links a reportes
- Plantilla de "Foco de la semana" como lead-in al plan de acción
- Decision: agrupar acciones por owner (no por horizonte) cuando aplican a la misma cohorte cross-reporte

### 4. Decisiones a validar con feedback W18

Antes de cristalizar la documentación, recoger respuestas a:

- ¿El nuevo mail ejecutivo es más útil que el formato W17?
- ¿La división por owner (Tech, Supply, Comercial, Pricing-Producto) tiene sentido para el equipo o conviene otra agrupación?
- ¿Los reportes editoriales completos (con KPIs hero, 10 findings, severity, etc.) se siguen leyendo o quedan como referencia profunda?
- ¿Falta alguna dimensión de análisis recurrente que no esté en los Excels? (ej. cohort de hoteles nuevos vs maduros)

---

## 📝 Acción específica para Week 19

1. **Lunes W19 (12 mayo):** revisar respuestas/feedback al mail W18
2. **Aplicar refactor de templates + guías + playbook** según feedback
3. **Commit `feat: Nivel C · templates y guías post W18 feedback`**
4. **Actualizar este documento** con el cambio de status

---

**Generado:** Mayo 2026 · post W18  
**Próxima revisión:** Lunes 12 de mayo (Week 19)
'''
(ROOT / 'NIVEL_C_PENDIENTE.md').write_text(nivel_c, encoding='utf-8')
print("✓ NIVEL_C_PENDIENTE.md generado")

# ============================================================================
# 6. COMMIT_GUIDE.md (cómo hacer el commit en git)
# ============================================================================
print("Generando COMMIT_GUIDE.md...")
commit_guide = '''# 🚀 Cómo aplicar este paquete al repo

## 1. Estructura del paquete

Este paquete contiene la estructura exacta que va al repo de GitHub. Tiene:

```
.
├── README.md                       ← README del repo (actualizar)
├── NIVEL_C_PENDIENTE.md            ← NUEVO archivo · documenta deuda técnica
├── index.html                      ← Hub actualizado con cards W18
├── _email/week-18/Mail_W18.html    ← NUEVO · mail ejecutivo (no se publica · solo local)
├── rates-nodispo/week-18/          ← NUEVA carpeta
│   ├── RatesNoDispo_Reporte_Editorial.html
│   ├── Analisis_Rates_NoDispo_7d.xlsx
│   └── Dataset_RatesNoDispo_W18.xlsx
└── checkrates/week-18/             ← NUEVA carpeta
    ├── CheckRates_Reporte_Editorial.html
    ├── Analisis_Checkrates_7d.xlsx
    └── Dataset_CheckRates_W18.xlsx
```

## 2. Aplicar al repo local

Desde la raíz de tu clone local de `Price`:

```bash
# 1. Copiar los archivos del ZIP descomprimido a la raíz del repo
#    (sobrescribe README.md, index.html y agrega las carpetas nuevas)
cp -r W18_Package/* /path/to/Price/

# 2. Verificar status
cd /path/to/Price
git status
```

Deberías ver:
- `modified: README.md`
- `modified: index.html`
- `new file: NIVEL_C_PENDIENTE.md`
- `new file: rates-nodispo/week-18/...` (3 archivos)
- `new file: checkrates/week-18/...` (3 archivos)
- `new file: _email/week-18/Mail_W18.html`

## 3. Verificar `.gitignore`

Asegurate de que `_email/` esté en `.gitignore` (no se publica). Si no está:

```bash
echo "_email/" >> .gitignore
git rm --cached -r _email/ 2>/dev/null || true
```

> **IMPORTANTE:** El mail tiene datos de los destinatarios y no debe publicarse. Mantenerlo siempre local.

## 4. Commit

```bash
git add .
git commit -m "feat: datos Week-18 · RatesNoDispo + CheckRates · sistema bandas D · 4-may-2026"
git push origin main
```

## 5. Verificar en producción

Una vez pusheado:

1. Esperar 1-2 minutos a que GitHub Pages actualice
2. Visitar https://federicochurches.github.io/Price/
3. Verificar que:
   - Las cards muestran Week 18
   - Los meta de cada card son correctos (%NoDispo 3,01% para RND · Eficacia 94,36% para CR)
   - Los links activos funcionan
   - El archivo muestra Week 17 activa, Week 16 activa, Week 15 disabled

## 6. Enviar el mail

1. Abrir `_email/week-18/Mail_W18.html` en el navegador local
2. Seguir las instrucciones del recuadro amarillo (copiar asunto, copiar cuerpo)
3. Pegar en Gmail/Outlook
4. Agregar 12 destinatarios en CCO (ver `destinatarios.md` local)
5. Verificar que las URLs de los reportes funcionan (deben apuntar a `https://federicochurches.github.io/Price/...week-18/...`)
6. Enviar

---

**Generado:** Mayo 2026 · post W18
'''
(ROOT / 'COMMIT_GUIDE.md').write_text(commit_guide, encoding='utf-8')
print("✓ COMMIT_GUIDE.md generado")

# ============================================================================
# 7. RESUMEN
# ============================================================================
print("\n" + "="*60)
print("PAQUETE NIVEL B · W18 · estructura final:")
print("="*60)

import subprocess
result = subprocess.run(['find', str(ROOT), '-type', 'f'], capture_output=True, text=True)
files = sorted(result.stdout.strip().split('\n'))
for f in files:
    rel = Path(f).relative_to(ROOT)
    size = os.path.getsize(f)
    if size > 1024 * 1024:
        size_str = f'{size/1024/1024:.1f} MB'
    elif size > 1024:
        size_str = f'{size/1024:.0f} KB'
    else:
        size_str = f'{size} B'
    print(f'  {rel}  ({size_str})')

print(f"\nTotal archivos: {len(files)}")
print(f"Carpeta paquete: {ROOT}")
