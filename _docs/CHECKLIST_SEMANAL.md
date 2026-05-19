# 📋 CHECKLIST SEMANAL · Proyecto PRICE

**Usa este checklist cada semana para no olvidar nada.**

---

## 📅 SEMANA W{NN}

Fecha: __________ | Fechas dato: __________ | MES/AÑO: __________

---

## 🚀 PASO 0: PRE-FLIGHT (1 min)

```
Datasets recibidos:
☐ Dataset_RatesNoDispo_W{NN}.xlsx
☐ Dataset_RatesNoDispo_W{NN-1}.xlsx
☐ Dataset_CheckRates_W{NN}.xlsx
☐ Dataset_CheckRates_W{NN-1}.xlsx

Validación RND (9 columnas):
☐ CorpName
☐ Hotel
☐ PaisDestino
☐ Destino
☐ DistributionCategory
☐ Trafico
☐ %NoDispo
☐ Bookings
☐ gb_usd
```

---

## 🔧 PASO 1: CONFIG SEMANAL (2 min)

```bash
# Terminal:
cd /ruta/proyecto
bash setup_week.sh {WEEK} "{PERIODO}" "{MES_AÑO}" {WEEK_PREV} "{PERIODO_PREV}"
```

**Ejemplo para W20:**
```bash
bash setup_week.sh 20 "12–18 may 2026" "Mayo 2026" 19 "5–11 may 2026"
```

☐ Script ejecutado sin errores

---

## 🧮 PASO 2-6: PIPELINE (30 min)

```bash
python calc_rnd.py      # ~3 min → rnd_w{NN}_data.pkl
python calc_cr.py       # ~2 min → cr_w{NN}_data.pkl
python render_rnd_p1.py # ~1 min
python render_rnd_p2.py # ~1 min
python render_rnd_p3.py # ~1 min
python render_cr_p1.py  # ~1 min
python render_cr_p2.py  # ~2 min
python render_cr_p3.py  # ~2 min
python assemble_rnd.py  # ~1 min → RatesNoDispo_Reporte_Editorial.html
python assemble_cr.py   # ~1 min → CheckRates_Reporte_Editorial.html
python excel_rnd.py     # ~3 min → 4 Excels RND
python excel_cr.py      # ~3 min → 4 Excels CR
python render_mail_v3.py # ~1 min → Mail_W{NN}.html
python build_package.py  # ~2 min → index.html + Price_W{NN}.zip
```

☐ Todos los pasos ejecutados sin errores
☐ Archivos output verificados

---

## 📦 PASO 7: PACKAGING PROYECTO (2 min)

```bash
bash package_project.sh {WEEK}
```

**Ejemplo para W20:**
```bash
bash package_project.sh 20
```

Archivo generado: `Proyecto_PRICE_Claude_W{NN}.zip`

☐ ZIP generado correctamente
☐ Verificado: sin _TEMPLATE_Hub.html
☐ Tamaño ~224 KB

---

## 📤 PASO 8: ACTUALIZAR PROYECTO CLAUDE (5 min)

```
1. Descomprime Proyecto_PRICE_Claude_W{NN}.zip
2. En el proyecto Claude:
   ☐ Borra TODOS los archivos
   ☐ Sube los archivos descomprimidos
   ☐ Verifica: 45 archivos sin duplicados
```

---

## 📨 PASO 9: MAIL SEMANAL (5 min)

**Comando:**
```
Generá el draft del mail Week NN
```

☐ Draft creado en Gmail
☐ Validado por Federico
☐ Enviado

---

## 🔗 PASO 10: COMMIT REPO GITHUB (5 min)

**ZIP de repo:**
Descarga `Price_W{NN}.zip` (generado en build_package.py)

```bash
unzip Price_W{NN}.zip
cd Price/
git add .
git commit -m "feat: Week {NN} · RatesNoDispo + CheckRates + hub index · {DD-MM-YYYY}"
git push origin main
```

☐ Commit pusheado
☐ URL repo verificada

---

## ✅ FINAL CHECKLIST

```
☐ Pipeline ejecutado sin errores
☐ Reportes HTML visualizados en navegador
☐ Excels generados (8 archivos)
☐ Mail validado y enviado
☐ Proyecto Claude actualizado
☐ Repo GitHub pusheado
☐ Hub index.html accesible en https://analytics-desk.netlify.app
```

---

## ⏱️ TIEMPO TOTAL ESTIMADO

| Paso | Tiempo |
|---|---|
| Pre-flight | 1 min |
| Config semanal | 2 min |
| Pipeline | 30 min |
| Packaging | 2 min |
| Proyecto Claude | 5 min |
| Mail | 5 min |
| GitHub | 5 min |
| **TOTAL** | **~50 min** |

---

## 🆘 TROUBLESHOOTING

### El pipeline falla
→ Verifica datasets (9 columnas RND, 10 CR)
→ Revisa líneas de error en terminal

### ZIP tiene _TEMPLATE_Hub.html
→ Ejecuta: `bash package_project.sh {WEEK}` nuevamente

### Proyecto Claude tiene duplicados
→ Borra TODO antes de descomprimir ZIP

### Mail no envía
→ Verifica credenciales Gmail
→ Confirma 15 destinatarios en destinatarios.md

---

**Última revisión:** Mayo 2026
**Próxima semana:** W{NN+1}

