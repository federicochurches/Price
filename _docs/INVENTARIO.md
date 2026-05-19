# 📋 INVENTARIO DE /mnt/project
**Actualizado: 19 Mayo 2026 · W21 Ready**

---

## 📊 RESUMEN EJECUTIVO

- **Total archivos:** 37 (sin contar pickles temporales)
- **Total carpetas:** 4 (organizadas)
- **Tamaño:** ~650 KB (scripts limpio)
- **Estado:** ✅ LISTO PARA PRODUCCIÓN W21+
- **Documentación:** ✅ COMPLETA Y ACTUALIZADA

---

## 📁 ESTRUCTURA COMPLETA

### 🏠 RAÍZ (/mnt/project)

**Documentación:**
- `PROMPT_MAESTRO_v3_ACTUALIZADO.md` ⭐ **OFICIAL** — versión 3 completa con historial W19-W20
- `INVENTARIO_ACTUALIZADO.md` — este archivo
- `INVENTARIO.md` — versión anterior (obsoleta)
- `PROMPT_MAESTRO_W21.md` — resumen ejecutivo (obsoleto)

**Utilidades:**
- `ver_proyecto.sh` — script para ver contenido en tiempo real
- `vacio.txt` — archivo de prueba

---

### 📁 _docs/ (Governance · 2 archivos)

```
CHANGELOG.md (4 KB)
  → Historial de cambios consolidado W19-W20
  → Decisiones técnicas documentadas
  → Bugs corregidos con números de tracking

COMMIT_GUIDE.md (400 bytes)
  → Formato de commits para GitHub
  → Pre-commit checklist
  → Pasos para push al repo
```

---

### 📁 _email/ (Email · 1 archivo)

```
destinatarios.md (1.3 KB)
  → 28 personas para mailing semanal
  → Destinatarios en BCC
  → Actualizado W20
```

---

### 📁 _helpers/ (Vacía)
```
(Esta carpeta puede eliminarse · es legacy)
```

---

### 📁 _scripts/ (Scripts · 31 archivos)

#### 🐍 SCRIPTS PYTHON (25 archivos)

**CÁLCULOS (Core)**
```
calc_cr.py (22 KB) ⭐
  · Calcula métricas CheckRates
  · MIN_CR = 100 (hoteles con ≥100 CR/semana)
  · Genera: cr_wNN_data.pkl
  · ¡CRÍTICO! No cambiar MIN_CR

calc_rnd.py (19 KB) ⭐
  · Calcula métricas RatesNoDispo
  · MIN_TRAFICO = 50000 (equivalente en RND)
  · Genera: rnd_wNN_data.pkl
  · ¡CRÍTICO! No cambiar MIN_TRAFICO
```

**RENDERIZADO (Parte 1: KPIs)**
```
render_cr_p1.py (40 KB)
  · Genera KPIs y alertas CheckRates
  · Part 1 de reporte CR

render_rnd_p1.py (35 KB)
  · Genera KPIs RatesNoDispo
  · Part 1 de reporte RND
```

**RENDERIZADO (Parte 2: Severity + Análisis)**
```
render_cr_p2.py (61 KB)
  · Severity + Análisis por hotel/dimensión
  · Tabs interactivos CheckRates
  · Part 2 de reporte CR

render_rnd_p2.py (43 KB)
  · Severity + Análisis por hotel/dimensión
  · Part 2 de reporte RND
```

**RENDERIZADO (Parte 3: Análisis por Canasta)**
```
render_cr_p3.py (56 KB)
  · Análisis por canasta: B2C, B2B-OP, CUG
  · Part 3 de reporte CR

render_rnd_p3.py (47 KB)
  · Análisis por canasta: B2C, B2B-OP, CUG
  · Part 3 de reporte RND
```

**ENSAMBLADO & OUTPUTS**
```
assemble_cr.py (2 KB)
  · Ensambla part1 + part2 + part3 → HTML final
  · Output: CheckRates_Reporte_Editorial.html
  · Agrega nota de Metodología P90

assemble_rnd.py (2 KB)
  · Ensambla RND parts → HTML final
  · Output: RatesNoDispo_Reporte_Editorial.html
  · Agrega nota de Metodología P90

excel_cr.py (24 KB)
  · Genera Excel global CheckRates (37 pestañas)
  · Sort por Eficacia ascendente
  · Incluye columna "Channels" en tab Por Corporativo

excel_rnd.py (22 KB)
  · Genera Excel global RatesNoDispo (33 pestañas)
  · IPM en lugar de RPM
  · Colores de banda IPM aplicados

excel_cr_canastas.py (7 KB)
  · Genera 3 Excels CR: B2C, OP, CUG (9 pestañas c/u)

excel_rnd_canastas.py (8 KB)
  · Genera 3 Excels RND: B2C, OP, CUG (8 pestañas c/u)
```

**ORQUESTACIÓN & MAIL**
```
run_pipeline.py (13 KB) ⭐
  · Orquestador principal
  · Ejecuta 6 pasos en orden (calc → render → assemble → excel → mail → package)
  · COMANDO ÚNICO para ejecutar W21: python3 run_pipeline.py

render_mail_v3.py (17 KB)
  · Genera draft de mail semanal
  · Output: Mail_WNN.html
  · Extrae body entre markers <!-- DRAFT_BODY_START/END -->

build_package.py (39 KB)
  · Genera ZIP de release (Price_WNN.zip)
  · Crea hub index.html
  · Genera logs detallados
  · Limpia archivos intermedios automáticamente
```

**HELPERS & TEMPLATES**
```
engine.py (1 KB)
  · Bandas (5 niveles) para %NoDispo, Eficacia, ConvRate, IPM
  · Thresholds y colores

render_helpers.py (10 KB)
  · Formateo español
  · clean_hotel_name()
  · truncate()
  · banda_pill()
  · _CITY_DASH_PATTERN

template_resumen.py (2 KB)
  · Renderiza Resumen Ejecutivo (10 findings)

template_alertas.py (2 KB)
  · Renderiza alertas críticas (3 cards)

template_severity.py (5 KB)
  · Renderiza bloques severity

template_seguimiento.py (5 KB)
  · Renderiza Plan de Acción + Carryover

areas_catalogo.py (1 KB)
  · Catálogo de áreas accountable

__init__.py (0 bytes)
  · Init Python package
```

#### 🌐 ASSETS HTML (6 archivos)

```
asset_cr_head.html (26 KB)
  · CSS + variables de color CheckRates
  · Tema: violet (#5C469C)
  · Headers globales

asset_cr_masthead.html (12 KB)
  · Masthead con logo CheckRates
  · Banner superior

asset_cr_footer.html (1.5 KB)
  · Footer CheckRates
  · Links y info final

asset_rnd_head.html (25 KB)
  · CSS + variables RatesNoDispo
  · Tema: magenta (#EA0074)
  · Headers globales

asset_rnd_masthead.html (12 KB)
  · Masthead con logo RND
  · Banner superior

asset_rnd_footer.html (880 bytes)
  · Footer RND
  · Links y info final
```

---

## ⚙️ CONFIGURACIÓN CRÍTICA (NO CAMBIAR)

### MIN_CR = 100
**Archivo:** `_scripts/calc_cr.py` línea 62
**Propósito:** Filtra hoteles con ≥100 CheckRates/semana
**Beneficio:** Elimina ruido, métrica única honesta
**Bug resuelto:** #111 (Iberostar OP gap 13.70%)

### MIN_TRAFICO = 50000
**Archivo:** `_scripts/calc_rnd.py` línea 85
**Propósito:** Equivalente en RatesNoDispo
**Mismo criterio:** Universo representativo

### P90 (percentil 90)
**Concepto:** Hoteles que acumulan ~90% tráfico
**Aplicación:** DESPUÉS de MIN_CR/MIN_TRAFICO
**Nota:** Se agrega automáticamente en reportes

---

## 🚀 FLUJO DE TRABAJO W21+

### 1. VALIDACIÓN PRE-PIPELINE

**Verificar datasets en `/mnt/user-data/uploads/`:**
- ✓ `Dataset_CheckRates_W21.xlsx`
- ✓ `Dataset_CheckRates_W20.xlsx` (WoW)
- ✓ `Dataset_RatesNoDispo_W21.xlsx` (9 columnas)
- ✓ `Dataset_RatesNoDispo_W20.xlsx` (WoW)

**Validación RND: 9 columnas obligatorias**
```
CorpName · Hotel · PaisDestino · Destino · 
DistributionCategory · Trafico · %NoDispo · 
Bookings · gb_usd
```

### 2. CONFIGURAR SEMANA

**En `_scripts/calc_cr.py` línea 12:**
```python
WEEK = 'W21'  # Cambiar de W20 a W21
```

**NO cambiar en calc_rnd.py:**
```python
MIN_TRAFICO = 50000  # ¡MANTENER!
```

### 3. EJECUTAR PIPELINE

```bash
cd /mnt/project/_scripts
python3 run_pipeline.py
```

**Internamente ejecuta (6 pasos):**
1. calc_rnd.py
2. calc_cr.py
3. render_*_p1.py, render_*_p2.py, render_*_p3.py
4. assemble_rnd.py, assemble_cr.py
5. excel_rnd.py, excel_cr.py (+ canastas)
6. build_package.py

### 4. OUTPUTS EN `/mnt/user-data/outputs/`

```
CheckRates_Reporte_Editorial.html        ← Reporte HTML
RatesNoDispo_Reporte_Editorial.html      ← Reporte HTML

Analisis_Checkrates_7d.xlsx              ← Global (37 pestañas)
Analisis_Checkrates_B2C_7d.xlsx          ← Canasta (9 pestañas)
Analisis_Checkrates_OP_7d.xlsx           ← Canasta (9 pestañas)
Analisis_Checkrates_CUG_7d.xlsx          ← Canasta (9 pestañas)

Analisis_Rates_NoDispo_7d.xlsx           ← Global (33 pestañas)
Analisis_Rates_NoDispo_B2C_7d.xlsx       ← Canasta (8 pestañas)
Analisis_Rates_NoDispo_OP_7d.xlsx        ← Canasta (8 pestañas)
Analisis_Rates_NoDispo_CUG_7d.xlsx       ← Canasta (8 pestañas)

Mail_W21.html                             ← Draft mail semanal
Price_W21.zip                             ← ZIP de release (repo completo)
pipeline_W21_run_*.log                    ← Log de ejecución
pipeline_W21_summary.json                 ← Metadatos
```

### 5. REVISAR + PUBLICAR

- Descargar HTMLs desde outputs
- Revisar visualmente
- Commitear ZIP a GitHub
- Enviar mail a 28 destinatarios

---

## 📌 CHECKLIST PRE-EJECUCIÓN W21

- [ ] Datasets W21 + W20 en `/mnt/user-data/uploads/`
- [ ] Verificar 9 columnas RND correctas
- [ ] WEEK='W21' en calc_cr.py
- [ ] MIN_CR=100 sin cambios
- [ ] MIN_TRAFICO=50000 sin cambios
- [ ] Ejecutar `python3 run_pipeline.py`
- [ ] Verificar outputs en `/mnt/user-data/outputs/`
- [ ] Revisar reportes HTML
- [ ] Descargar Price_W21.zip
- [ ] Commitear a GitHub
- [ ] Enviar mail semanal

---

## 🐛 BUGS HISTÓRICOS (RESUELTOS)

| # | Problema | Solución | Status |
|---|----------|----------|--------|
| #111 | P80 con ruido (Iberostar OP) | MIN_CR=100 + MIN_TRAFICO=50K | ✅ |
| #47 | CONFIG WEEK desalineado | Sincronizar scripts | ✅ |
| #16 | metrics_recalc.pkl inexistente | render_mail_v3.py v3.2 | ✅ |
| #28-#36 | Fixes Excel IPM/CR | Colores, headers | ✅ |
| #37-#46 | Fixes visuales canastas | Nomenclatura, CSS | ✅ |

---

## 📞 REFERENCIA RÁPIDA

**PROMPT OFICIAL:** `/mnt/project/PROMPT_MAESTRO_v3_ACTUALIZADO.md`
- Historial completo W19-W20
- Decisiones técnicas documentadas
- Bugs con tracking

**DOCUMENTACIÓN GOVERNANCE:** `/mnt/project/_docs/`
- CHANGELOG.md
- COMMIT_GUIDE.md

**DESTINATARIOS:** `/mnt/project/_email/destinatarios.md` (28 personas)

**SCRIPTS CORE:** `/mnt/project/_scripts/` (31 archivos)

---

**Última actualización:** 19 Mayo 2026 · W21 Ready · MIN_CR=100 Consolidado
