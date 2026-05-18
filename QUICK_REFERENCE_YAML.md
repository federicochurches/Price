# 🚀 QUICK REFERENCE CARD · Pipeline YAML

## Comando Único (W21+)

```bash
cd /mnt/project
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

---

## Setup W21 (3 pasos · 5 min)

### 1️⃣ Adjuntar datasets
```
/mnt/user-data/uploads/
  ├── Dataset_RatesNoDispo_W21.xlsx ← NUEVO
  ├── Dataset_RatesNoDispo_W20.xlsx ← WoW
  ├── Dataset_CheckRates_W21.xlsx   ← NUEVO
  └── Dataset_CheckRates_W20.xlsx   ← WoW
```

### 2️⃣ Actualizar config (2 min)
```bash
cp WEEK_CONFIG_W20.yml WEEK_CONFIG_W21.yml
```

Edit 7 líneas en `WEEK_CONFIG_W21.yml`:
```yaml
week: 21                          # ← Cambiar
vol_num: "21"                     # ← Cambiar
periodo: "19–25 may 2026"         # ← Cambiar
fecha_pub: "Lunes 26 mayo 2026"   # ← Cambiar
week_prev: 20                     # ← Cambiar
periodo_prev: "12–18 may 2026"    # ← Cambiar
week_prev2: 19                    # ← Cambiar
```

### 3️⃣ Ejecutar pipeline (15 min)
```bash
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

Output:
```
✅ PIPELINE COMPLETADO EXITOSAMENTE
   ZIP: /mnt/user-data/outputs/Price_W21.zip
```

---

## Archivo Salida

```
Price_W21.zip (11 MB)
├── index.html                                (hub)
├── checkrates/week-21/
│   ├── CheckRates_Reporte_Editorial.html
│   ├── Analisis_Checkrates_7d.xlsx + B2C/OP/CUG
│   └── Dataset_CheckRates_W21.xlsx
└── rates-nodispo/week-21/
    ├── RatesNoDispo_Reporte_Editorial.html
    ├── Analisis_Rates_NoDispo_7d.xlsx + B2C/OP/CUG
    └── Dataset_RatesNoDispo_W21.xlsx
```

---

## Variables de Entorno (Automáticas)

```bash
WEEK=W21
VOL_NUM=21
PERIODO="19–25 may 2026"
MES_AÑO="Mayo 2026"
FECHA_PUB="Lunes 26 mayo 2026"
PICKLE_RND=rnd_w21_data.pkl
PICKLE_CR=cr_w21_data.pkl
PROJECT_DIR=/mnt/project
OUTPUTS_DIR=/mnt/user-data/outputs
```

---

## Timeline

| Paso | Tiempo |
|---|---|
| Adjuntar datasets | 5 min |
| Editar WEEK_CONFIG.yml | 2 min |
| `run_pipeline.py` | 12 min |
| Revisar ZIP | 1 min |
| **TOTAL** | **20 min** |

---

## Troubleshooting

### ❌ "Dataset incompletos"
```bash
ls -lh /mnt/user-data/uploads/Dataset_*
# Debe haber 4 archivos: RND W21/W20, CR W21/W20
```

### ❌ "YAML parsing error"
```bash
python3 -c "import yaml; yaml.safe_load(open('WEEK_CONFIG_W21.yml'))"
# Si hay error, revisar sintaxis YAML (indentación, comillas)
```

### ❌ "Paso X falló"
```bash
cat /mnt/user-data/outputs/pipeline_W21_run_*.log | grep "PASO: X" -A 20
```

### ✅ "Paso Excel falló pero continuó"
→ Expected! Excel es non-critical. Pipeline continúa con Mail + Hub.

---

## Logs

```bash
# Ver log completo
cat /mnt/user-data/outputs/pipeline_W21_run_*.log

# Ver resumen JSON
cat /mnt/user-data/outputs/pipeline_W21_summary.json

# Filtrar por paso
grep "SUCCESS\|ERROR" /mnt/user-data/outputs/pipeline_W21_run_*.log
```

---

## Para W22, W23, ...

```bash
# Copiar config anterior
cp WEEK_CONFIG_W{N}.yml WEEK_CONFIG_W{N+1}.yml

# Editar 7 líneas (mismo patrón siempre)
vim WEEK_CONFIG_W{N+1}.yml

# Ejecutar
python3 run_pipeline.py WEEK_CONFIG_W{N+1}.yml
```

---

## Commit a GitHub

```bash
cd /repo/Price
unzip /mnt/user-data/outputs/Price_W21.zip
git add .
git commit -m "feat: Week 21 · RatesNoDispo + CheckRates + hub · 19–25 may 2026"
git push origin main
```

---

## Rollback (si algo falla crítico)

```bash
# Revisar log para error
tail -100 /mnt/user-data/outputs/pipeline_W21_run_*.log

# Eliminar pickles problemáticos
rm /mnt/project/rnd_w21_data.pkl /mnt/project/cr_w21_data.pkl

# Reejecutar
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

---

## Status Check

```bash
# ¿Pipeline finalizó OK?
grep "SUCCESS" /mnt/user-data/outputs/pipeline_W21_summary.json

# ¿ZIP está listo?
ls -lh /mnt/user-data/outputs/Price_W21.zip
unzip -t /mnt/user-data/outputs/Price_W21.zip  # Test ZIP integridad
```

---

## Docs Completos

- `YAML_PIPELINE_GUIDE.md` — Guía completa (troubleshooting detallado)
- `IMPLEMENTACION_YAML_COMPLETADA.md` — Arquitectura y decisiones
- `run_pipeline.py` — Código fuente (bien comentado)

---

**⏱️ W20: 35 min · W21+: 20 min · Ahorro: 15 min/semana = 13 horas/año**

