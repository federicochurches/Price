# 🚀 GETTING STARTED · Week 21+ · Flujo YAML

**¿Necesitas ejecutar W21?** Aquí están las instrucciones de inicio rápido.

---

## 1️⃣ Adjuntar Datasets (5 min)

Coloca los 4 archivos en `/mnt/user-data/uploads/`:

```
Dataset_RatesNoDispo_W21.xlsx   ← NUEVO (semana actual)
Dataset_RatesNoDispo_W20.xlsx   ← ANTERIOR (para WoW)
Dataset_CheckRates_W21.xlsx     ← NUEVO
Dataset_CheckRates_W20.xlsx     ← ANTERIOR
```

---

## 2️⃣ Preparar Config (2 min)

```bash
cd /mnt/project
cp WEEK_CONFIG_W20.yml WEEK_CONFIG_W21.yml
```

Edita **7 líneas** en `WEEK_CONFIG_W21.yml`:

```yaml
week: 21                          # ← Cambiar de 20 a 21
vol_num: "21"                     # ← Cambiar de 20 a 21
periodo: "19–25 may 2026"         # ← Cambiar fechas (semana actual)
fecha_pub: "Lunes 26 mayo 2026"   # ← Cambiar lunes (publicación)
week_prev: 20                     # ← Cambiar de 19 a 20
periodo_prev: "12–18 may 2026"    # ← Cambiar fechas (semana anterior)
week_prev2: 19                    # ← Cambiar de 18 a 19
```

---

## 3️⃣ Ejecutar Pipeline (15 min)

```bash
python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

Espera a ver:

```
✅ PIPELINE COMPLETADO EXITOSAMENTE
   ZIP: /mnt/user-data/outputs/Price_W21.zip
```

---

## 4️⃣ Verificar + Commit (3 min)

```bash
# Descomprimir ZIP
cd /repo/Price
unzip /mnt/user-data/outputs/Price_W21.zip

# Commit
git add .
git commit -m "feat: Week 21 · RatesNoDispo + CheckRates · 19–25 may 2026"
git push origin main
```

---

## ❓ ¿Algo falló?

Revisa el log:

```bash
cat /mnt/user-data/outputs/pipeline_W21_run_*.log | tail -100
```

**Soluciones rápidas:**
- "Dataset incompletos" → Verifica `/mnt/user-data/uploads/` tiene 4 archivos
- "YAML parsing error" → Revisa indentación en WEEK_CONFIG_W21.yml
- Paso X falló → Busca error en log

---

## 📚 Documentación Completa

- **`YAML_PIPELINE_GUIDE.md`** — Guía detallada (5000+ palabras)
- **`QUICK_REFERENCE_YAML.md`** — Cheat sheet

---

## ⏱️ Timeline Total

| Paso | Tiempo |
|---|---|
| Adjuntar datasets | 5 min |
| Actualizar config | 2 min |
| Ejecutar pipeline | 12 min |
| Commit a GitHub | 3 min |
| **TOTAL** | **22 min** |

---

**¡Listo! W21 ejecutado correctamente.**

Para W22+, repite: `cp WEEK_CONFIG_W{N}.yml WEEK_CONFIG_W{N+1}.yml` → edita 7 líneas → `python3 run_pipeline.py WEEK_CONFIG_W{N+1}.yml`

