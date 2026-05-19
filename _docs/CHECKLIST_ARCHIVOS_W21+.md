# ✅ CHECKLIST ARCHIVOS PROYECTO · Pipeline W21+

## 📂 ESTRUCTURA FINAL POST W19-W20

### `/mnt/project/_scripts/` (36 archivos Python + HTML)

**Scripts críticos (modificados W19-W20):**
- [ ] `run_pipeline.py` → línea 181: `project_dir = Path(...) / '_scripts'`
- [ ] `render_cr_p1.py` → línea 2,28-29,54-55: sin fallbacks, header dinámico
- [ ] `excel_cr.py` → líneas 130-206: todas las pestañas ordenadas por Eficacia ↑

**Scripts sin cambios pero requeridos:**
- [ ] `calc_rnd.py`
- [ ] `calc_cr.py`
- [ ] `render_rnd_p1.py`, `render_rnd_p2.py`, `render_rnd_p3.py`
- [ ] `render_cr_p2.py`, `render_cr_p3.py`
- [ ] `assemble_rnd.py`, `assemble_cr.py`
- [ ] `excel_rnd.py`
- [ ] `render_mail_v3.py`
- [ ] `build_package.py`
- [ ] `engine.py` (bandas IPM 5 niveles)
- [ ] `render_helpers.py` (gauge, clean_hotel_name)
- [ ] `template_resumen.py`
- [ ] `template_alertas.py`
- [ ] `template_severity.py` (LEVELS_RPM 5 bandas)
- [ ] `template_seguimiento.py`
- [ ] `areas_catalogo.py`

**Assets HTML (CSS + headers + footers):**
- [ ] `asset_rnd_head.html` (CSS magenta RND)
- [ ] `asset_rnd_masthead.html`
- [ ] `asset_rnd_footer.html`
- [ ] `asset_cr_head.html` (CSS violet CR)
- [ ] `asset_cr_masthead.html`
- [ ] `asset_cr_footer.html`

**Total esperado:** 36 archivos

---

### `/mnt/project/_config/` (YAML configs - NUEVO)

**Para ejecutar W21, crear:**
- [ ] `WEEK_CONFIG_W21.yml` (copiar W20, editar 7 líneas)
  - [ ] `week: 21`
  - [ ] `vol_num: "21"`
  - [ ] `periodo: "19–25 may 2026"`
  - [ ] `mes_año: "Mayo 2026"`
  - [ ] `fecha_pub: "Lunes 26 mayo 2026"`
  - [ ] `week_prev: 20`, `vol_num_prev: "20"`
  - [ ] `datasets: W21 + W20`

**Templates existentes (reference):**
- [ ] `WEEK_CONFIG_W19.yml` (creado sesión W19-W20)
- [ ] `WEEK_CONFIG_W20.yml` (creado sesión W19-W20)
- [ ] `WEEK_CONFIG_W21.yml` (ya existía)

---

### `/mnt/project/_docs/` (Documentación)

- [ ] `CHANGELOG.md` (histórico cambios)
- [ ] `COMMIT_GUIDE.md` (formato commit GitHub)

---

### `/mnt/project/` (Raíz)

**Archivos de proyecto:**
- [ ] `destinatarios.md` (15 destinatarios BCC mail)
- [ ] `PROMPT_MAESTRO_v3.md` (contexto operativo)

**NEW - Documentación sesión W19-W20:**
- [ ] `YAML_PIPELINE_GUIDE_W19-W20.md` (cómo ejecutar YAML)
- [ ] `IBEROSTAR_EFICACIA_ANALYSIS_W20.md` (análisis discrepancia)

---

## 📊 DATASETS REQUERIDOS (`/mnt/user-data/uploads/`)

**Para cada semana WNN necesitas exactamente 4 datasets:**

### Formato
```
Dataset_CheckRates_WNN.xlsx       (actual)
Dataset_CheckRates_W(NN-1).xlsx   (anterior - para WoW)
Dataset_RatesNoDispo_WNN.xlsx     (actual)
Dataset_RatesNoDispo_W(NN-1).xlsx (anterior - para WoW)
```

### Para W21
- [ ] `Dataset_CheckRates_W21.xlsx` (3.7-4.1 MB)
- [ ] `Dataset_CheckRates_W20.xlsx` (ya existe)
- [ ] `Dataset_RatesNoDispo_W21.xlsx` (7.6-9.6 MB)
- [ ] `Dataset_RatesNoDispo_W20.xlsx` (ya existe)

### Validación
```bash
# Antes de ejecutar pipeline:
for f in Dataset_CheckRates_W21.xlsx Dataset_CheckRates_W20.xlsx \
         Dataset_RatesNoDispo_W21.xlsx Dataset_RatesNoDispo_W20.xlsx; do
  [ -f "/mnt/user-data/uploads/$f" ] && echo "✓ $f" || echo "✗ FALTA: $f"
done
```

---

## 🚀 FLUJO EJECUCIÓN W21 (referencia rápida)

```bash
# 1. Verificar config YAML existe
cat /mnt/project/_config/WEEK_CONFIG_W21.yml

# 2. Verificar datasets (ver validación arriba)

# 3. Limpiar outputs previos
cd /mnt/project/_scripts
rm -f *.pkl
rm -f /mnt/user-data/outputs/*.html /mnt/user-data/outputs/*.xlsx

# 4. Ejecutar pipeline (20 min)
python3 run_pipeline.py /mnt/project/_config/WEEK_CONFIG_W21.yml

# 5. Validar outputs
ls -lh /mnt/user-data/outputs/
# Deben existir: *.html + 8 Excels (4 RND + 4 CR)

# 6. Verificar header en HTML
grep "Week W21\|Week 21" /mnt/user-data/outputs/CheckRates_Reporte_Editorial.html

# 7. Commit (opcional)
unzip /mnt/user-data/outputs/Price_W21.zip -d /tmp/price_w21
cd /tmp/price_w21
git add -A
git commit -m "feat: Week 21 · RatesNoDispo + CheckRates + hub · DD-MM-YYYY"
git push origin main
```

---

## 🔧 CAMBIOS POR SCRIPT (resumen ejecutivo)

| Script | Línea | Cambio | W21+ |
|--------|-------|--------|------|
| run_pipeline.py | 181 | `/_scripts` en path | ✅ Aplicado |
| render_cr_p1.py | 2 | Comentario W20 | ✅ Reemplazar W21 |
| render_cr_p1.py | 28-29 | Remover fallback W18 | ✅ Aplicado |
| render_cr_p1.py | 54-55 | Header `{WEEK_NUM}` | ✅ Aplicado |
| excel_cr.py | 5 líneas | Sort → Eficacia ↑ | ✅ Aplicado |
| excel_cr.py | 15 líneas | Sort canastas → Eficacia ↑ | ✅ Aplicado |

---

## ⚠️ VALIDACIONES PRE-EJECUCIÓN

Checklist antes de `python3 run_pipeline.py WEEK_CONFIG_WNN.yml`:

- [ ] Config YAML existe: `/mnt/project/_config/WEEK_CONFIG_WNN.yml`
- [ ] Valores YAML tienen la week correcta (WNN)
- [ ] 4 datasets en `/mnt/user-data/uploads/`:
  - [ ] Dataset_CheckRates_WNN.xlsx
  - [ ] Dataset_CheckRates_W(NN-1).xlsx
  - [ ] Dataset_RatesNoDispo_WNN.xlsx
  - [ ] Dataset_RatesNoDispo_W(NN-1).xlsx
- [ ] Pickles viejos borrados: `rm -f /mnt/project/_scripts/*.pkl`
- [ ] Outputs viejos borrados: `rm -f /mnt/user-data/outputs/*.html *.xlsx`
- [ ] Scripts sin syntax errors: revisar render_cr_p1.py si editaste

---

## 📝 PRÓXIMAS ACCIONES POST W21

- [ ] Actualizar YAML_PIPELINE_GUIDE con W21 si hubo cambios
- [ ] Revisar si render_mail_v3.py necesita actualización (requiere global_w17)
- [ ] Documentar si hay nuevos bugs en CHANGELOG.md
- [ ] Mantener pickles de W20/W21 para deltas futuros (si aplica)

---

## 🎓 NOTAS IMPORTANTES

1. **Pickles:** Se regeneran cada pipeline. NO necesitas guardarlos entre semanas.
2. **Datasets:** Deben llegar de fuente externa (Federico). Son 4 por semana.
3. **YAML:** Cambios permiten config centralizada sin tocar código Python.
4. **P80:** Los Excels reportan hoteles del P80 (80% tráfico), no todos. Es intencional.
5. **Headers:** Ahora dinámicos `{WEEK_NUM}` desde pickle, no hardcodeados.

---

**Última actualización:** 19 mayo 2026 · Post W19-W20 · YAML Pipeline fully operational
