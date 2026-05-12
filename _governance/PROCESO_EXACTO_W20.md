# 🚀 PROCESO EXACTO PARA EJECUTAR W20

**Versión final · Con los 4 scripts nuevos**

---

## 📋 PREREQUISITOS (antes de W20)

### 1. Verificar sincronización proyecto Claude
```bash
# En proyecto Claude
ls -la /mnt/project | grep -E "(setup_week|run_pipeline|package_project|sync_project)"
# Deben existir los 4 scripts .sh
```

### 2. Tener datasets listos
```
Dataset_RatesNoDispo_W20.xlsx    ← En /mnt/project/
Dataset_RatesNoDispo_W19.xlsx    ← En /mnt/project/
Dataset_CheckRates_W20.xlsx      ← En /mnt/project/
Dataset_CheckRates_W19.xlsx      ← En /mnt/project/
```

---

## 🎯 PROCESO W20 (PASO A PASO)

### **PASO 1: Config automática (2 segundos)**

Cuando recibas los datasets W20, ejecuta:

```bash
cd /mnt/project
bash setup_week.sh 20 "12–18 may 2026" "Mayo 2026" 19 "5–11 may 2026"
```

**Qué hace:**
- Cambia `WEEK=20` en `calc_rnd.py`
- Cambia `WEEK=20` en `calc_cr.py`
- Cambia `WEEK=20, PERIODO='12–18 may 2026'` en `build_package.py`
- Cambia `WEEK=20` en `render_mail_v3.py`
- Verifica que todo está listo

**Output esperado:**
```
✅ setup_week.sh completado
✅ 4 archivos configurados para W20
✅ Datasets detectados: RND + CR × 2 (W20 + W19)
```

---

### **PASO 2: Pipeline completo (25 minutos)**

Ejecuta:

```bash
cd /mnt/project
bash run_pipeline.sh 20
```

**Qué hace:**
- Ejecuta `calc_rnd.py` → genera `rnd_w20_data.pkl`
- Ejecuta `calc_cr.py` → genera `cr_w20_data.pkl`
- Ejecuta los 6 render scripts (RND p1/p2/p3 + CR p1/p2/p3)
- Ejecuta 2 assemble scripts → HTMLs finales
- Ejecuta 2 excel scripts → 8 Excels (4 RND + 4 CR)
- Ejecuta `render_mail_v3.py` → `Mail_W20.html`
- Ejecuta `build_package.py` → `index.html` + `Price_W20.zip`

**Mientras se ejecuta:** puedes ir a tomar café ☕

**Output esperado:**
```
[1/14] ⏳ Cálculos RND...
        ✅ (2m 15s)
[2/14] ⏳ Cálculos CR...
        ✅ (1m 45s)
[3/14] ⏳ RND Part 1 (Hero + KPIs)...
        ✅ (45s)
... (todos verdes)
[14/14] ⏳ Hub + ZIP repo...
        ✅ (30s)

════════════════════════════════════
📊 PIPELINE COMPLETADO
════════════════════════════════════
✅ TODO EXITOSO
   Tiempo total: 25m 30s

Outputs generados:
  ✓ rnd_w20_data.pkl
  ✓ cr_w20_data.pkl
  ✓ RatesNoDispo_Reporte_Editorial.html
  ✓ CheckRates_Reporte_Editorial.html
  ✓ 4 Excels RND
  ✓ 4 Excels CR
  ✓ Mail_W20.html
  ✓ index.html (hub)
  ✓ Price_W20.zip (repo)

✨ Pipeline W20 LISTO PARA PRODUCCIÓN
════════════════════════════════════
```

---

### **PASO 3: Validación manual (5 minutos)**

Verifica los outputs:

```bash
# Ver archivos generados
ls -lh RatesNoDispo_Reporte_Editorial.html
ls -lh CheckRates_Reporte_Editorial.html
ls -lh Analisis_*.xlsx
ls -lh Mail_W20.html
ls -lh Price_W20.zip
```

**Checklist visual:**
- [ ] Abre `RatesNoDispo_Reporte_Editorial.html` en navegador
  - [ ] Hero box con datos W20
  - [ ] Colores de bandas correctos
  - [ ] Tablas con hoteles
- [ ] Abre `CheckRates_Reporte_Editorial.html` en navegador
  - [ ] Hero box con datos W20
  - [ ] Tabs con canales correctos
  - [ ] Eficacia y ConvRate visibles
- [ ] Abre un Excel (ej: `Analisis_Rates_NoDispo_7d.xlsx`)
  - [ ] Datos de W20
  - [ ] Colores de banda correctos
  - [ ] Fórmulas funcionan

---

### **PASO 4: Preparar sincronización (2 minutos)**

```bash
bash sync_project.sh 20
```

**Qué hace:**
- Genera `Proyecto_PRICE_Claude_W20.zip`
- Crea `SYNC_INSTRUCCIONES_W20.txt`
- Crea `SYNC_RESUMEN_W20.md`

**Output:**
```
════════════════════════════════════
✅ SINCRONIZACIÓN PREPARADA · WEEK 20
════════════════════════════════════

📦 Archivos en /mnt/user-data/outputs/:
  • Proyecto_PRICE_Claude_W20.zip (232 KB)
  • SYNC_INSTRUCCIONES_W20.txt
  • SYNC_RESUMEN_W20.md

📋 Checklist:
  ✓ ZIP generado sin _TEMPLATE_Hub.html
  ✓ 51 archivos (verificado)
  ✓ Instrucciones claras
  ✓ Resumen ejecutivo

🚀 Próximo paso: Descargar ZIP y subir al proyecto Claude
════════════════════════════════════
```

---

### **PASO 5: Commit a GitHub (5 minutos)**

```bash
# Desde la carpeta del repo
cd ~/Price/  # o tu ruta

# Agrega outputs
git add rates-nodispo/week-20/
git add checkrates/week-20/
git add index.html
git add _governance/audit_w20.md
git add _governance/READY_W20.md

# Commit
git commit -m "feat: Week 20 · RatesNoDispo + CheckRates · 12–18 may 2026"

# Push
git push origin main
```

**Output:**
```
✅ Archivos en staging
✅ Commit creado
✅ Push a origin/main completado
✅ Repo actualizado

GitHub ahora tiene W20 con todos los reportes
```

---

### **PASO 6: Actualizar proyecto Claude (3 minutos)**

Solo si el proyecto se desincronizó:

```bash
# En proyecto Claude
bash sync_project.sh 20

# Luego:
# 1. Descargar Proyecto_PRICE_Claude_W20.zip
# 2. En proyecto Claude:
#    - Borra TODO
#    - Sube los 51 archivos descomprimidos
# 3. Verifica: 51 archivos sin duplicados
```

---

### **PASO 7: Draft mail semanal (10 minutos)**

Usa `Mail_W20.html` como base:

```bash
# El script genera Mail_W20.html
# Úsalo para draft en Gmail
```

---

## ⏱️ TIEMPO TOTAL

```
PASO 1 (Config)              2 seg
PASO 2 (Pipeline)           25 min    ← Automático (vos no haces nada)
PASO 3 (Validación)          5 min    ← Manual (abre archivos)
PASO 4 (Sync prep)           2 min    ← Automático
PASO 5 (Git commit)          5 min    ← Manual (git commands)
PASO 6 (Proyecto sync)       3 min    ← Manual (subir ZIP)
PASO 7 (Draft mail)         10 min    ← Manual (Gmail)
                            ──────
TOTAL:                      50 min
```

**Pero ACTIVO (donde haces algo): ~30 min**
**Pasivo (el script trabaja): ~20 min**

---

## 🎯 CHECKLIST FINAL W20

```
LUNES
□ Recibir datasets W20
□ bash setup_week.sh 20 "12–18 may" "Mayo" 19 "5–11 may"
□ bash run_pipeline.sh 20  ← Esperar 25 min
□ Validar HTMLs en navegador
□ Validar Excels
□ bash sync_project.sh 20

MARTES
□ Descargar ZIP
□ Actualizar proyecto Claude
□ Verificar 51 archivos

MIÉRCOLES
□ git add + git commit + git push
□ Draft mail
□ Publicar en hub

VIERNES
□ Todo publicado ✅
```

---

## 🆘 TROUBLESHOOTING

### Si `run_pipeline.sh` falla en paso X

```bash
# Ver qué falló
tail -20 /tmp/pipeline_render_rnd_p1.log

# Opción A: Ejecutar manualmente el script que falló
cd /mnt/project
python render_rnd_p1.py

# Opción B: Desde claude para help
# "Fallo en render_rnd_p1.py línea 145: IndexError"
```

### Si falta dataset

```bash
bash setup_week.sh 20 "..." "..." 19 "..."
# Te dirá: ❌ ERROR: Dataset_RatesNoDispo_W20.xlsx no encontrado
# → Subir el dataset a /mnt/project/ y reintentar
```

### Si el ZIP está corrupto

```bash
bash package_project.sh 20
# Regenera Proyecto_PRICE_Claude_W20.zip
```

---

## ✅ RESULTADO FINAL

Después de seguir estos 7 pasos:

```
📊 REPORTES PUBLICADOS
├── RatesNoDispo_Reporte_Editorial.html ✅
├── CheckRates_Reporte_Editorial.html ✅
├── 8 Excels (4 RND + 4 CR) ✅
└── Mail_W20.html ✅

🌐 HUB ACTUALIZADO
└── index.html con W20 ✅

📦 REPO GITHUB
└── federicochurches/Price actualizado ✅

📁 PROYECTO CLAUDE
└── Sincronizado con repo ✅
```

**W20 LISTO PARA PRODUCCIÓN.** 🚀

