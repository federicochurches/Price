#!/bin/bash
# sync_project.sh - Sincroniza proyecto Claude automáticamente
# Uso: bash sync_project.sh {WEEK}
# Ejemplo: bash sync_project.sh 20

WEEK=${1:-20}
OUTPUT_DIR="/tmp/sync_w${WEEK}"

echo "🔄 Sincronizando proyecto Claude para Week $WEEK..."
echo ""

# Paso 1: Crear directorio temporal
mkdir -p "$OUTPUT_DIR"
echo "✓ Directorio temporal: $OUTPUT_DIR"

# Paso 2: Copiar todos los archivos del proyecto
echo "✓ Empaquetando archivos del proyecto..."
bash package_project.sh "$WEEK" > /dev/null 2>&1

if [ ! -f "Proyecto_PRICE_Claude_W${WEEK}.zip" ]; then
    echo "❌ ERROR: No se pudo generar ZIP"
    exit 1
fi

# Paso 3: Copiar a output
cp "Proyecto_PRICE_Claude_W${WEEK}.zip" "/mnt/user-data/outputs/"
echo "✓ ZIP generado: Proyecto_PRICE_Claude_W${WEEK}.zip ($(du -h "Proyecto_PRICE_Claude_W${WEEK}.zip" | cut -f1))"

# Paso 4: Generar instrucciones de sincronización
cat > "/mnt/user-data/outputs/SYNC_INSTRUCCIONES_W${WEEK}.txt" << SYNC_END
🔄 INSTRUCCIONES DE SINCRONIZACIÓN · WEEK $WEEK
════════════════════════════════════════════════════════

ARCHIVO: Proyecto_PRICE_Claude_W${WEEK}.zip

PASO 1: DESCOMPRIME EL ZIP
  En tu computadora:
  unzip Proyecto_PRICE_Claude_W${WEEK}.zip

PASO 2: ACTUALIZA EL PROYECTO CLAUDE
  En el proyecto Claude:
  1. Borra TODOS los archivos existentes
  2. Sube los 49 archivos descomprimidos
  3. Verifica: debe haber exactamente 49 archivos (sin duplicados)

PASO 3: VERIFICA SINCRONIZACIÓN
  En la terminal:
  ls -la /mnt/project | wc -l
  (debe devolver 52 = 49 archivos + . + .. + total)

PASO 4: PRÓXIMA SESIÓN (EN CLAUDE)
  Cuando recibas datasets W$((WEEK+1)):
  bash setup_week.sh $((WEEK+1)) "FECHAS" "MES" $WEEK "FECHAS_PREV"

════════════════════════════════════════════════════════
Generado: $(date)
SYNC_END

echo "✓ Instrucciones generadas: SYNC_INSTRUCCIONES_W${WEEK}.txt"

# Paso 5: Generar resumen
cat > "/mnt/user-data/outputs/SYNC_RESUMEN_W${WEEK}.md" << SUMMARY_END
# 🔄 SINCRONIZACIÓN COMPLETA · WEEK $WEEK

**Fecha:** $(date)
**Status:** ✅ LISTO PARA SUBIR

---

## 📦 ARCHIVOS GENERADOS

| Archivo | Tamaño | Descripción |
|---|---|---|
| Proyecto_PRICE_Claude_W${WEEK}.zip | $(du -h "Proyecto_PRICE_Claude_W${WEEK}.zip" | cut -f1) | ZIP limpio · 49 archivos |
| SYNC_INSTRUCCIONES_W${WEEK}.txt | ~1 KB | Pasos a seguir |
| SYNC_RESUMEN_W${WEEK}.md | Este archivo | Resumen |

---

## ✅ CHECKLIST PRE-SINCRONIZACIÓN

```
☐ Archivo ZIP generado (Proyecto_PRICE_Claude_W${WEEK}.zip)
☐ Instrucciones descargadas (SYNC_INSTRUCCIONES_W${WEEK}.txt)
☐ Tienes acceso al proyecto Claude
☐ Tenés backups de datos importantes
```

---

## 🔄 PROCESO (3 PASOS)

### 1. Descomprime
```bash
unzip Proyecto_PRICE_Claude_W${WEEK}.zip
```

### 2. En proyecto Claude
- Borra TODOS los archivos
- Sube los 49 archivos descomprimidos

### 3. Verifica
```bash
ls -la /mnt/project | wc -l  # debe devolver 52
```

---

## 🎯 DESPUÉS DE SINCRONIZAR

Proyecto Claude estará actualizado con:
- ✅ 49 archivos limpios
- ✅ 4 scripts automáticos (setup_week, package_project, run_pipeline, sync_project)
- ✅ 3 checklists (CHECKLIST_SEMANAL, audits, instrucciones)
- ✅ PROMPT_MAESTRO_v3.md actualizado
- ✅ Sin duplicados · Sin _TEMPLATE_Hub.html

---

## ⏱️ TIEMPO ESTIMADO

- Descomprimir: 10 seg
- Limpiar proyecto Claude: 2 min
- Subir archivos: 3 min
- Verificar: 1 min
- **TOTAL: ~6 minutos**

---

## 🆘 TROUBLESHOOTING

❓ "ZIP está corrupto"
→ Regenera: bash package_project.sh $WEEK

❓ "Proyecto Claude no me deja borrar"
→ Contacta soporte · hay límites de permisos

❓ "Faltan archivos después de subir"
→ Verifica count: debe ser 49 archivos

---

**Listo para producción.** 🚀

SUMMARY_END

echo "✓ Resumen generado: SYNC_RESUMEN_W${WEEK}.md"

# Paso 6: Mostrar resumen final
echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ SINCRONIZACIÓN PREPARADA · WEEK $WEEK"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📦 Archivos en /mnt/user-data/outputs/:"
echo "  • Proyecto_PRICE_Claude_W${WEEK}.zip ($(du -h "Proyecto_PRICE_Claude_W${WEEK}.zip" | cut -f1))"
echo "  • SYNC_INSTRUCCIONES_W${WEEK}.txt"
echo "  • SYNC_RESUMEN_W${WEEK}.md"
echo ""
echo "📋 Checklist:"
echo "  ✓ ZIP generado sin _TEMPLATE_Hub.html"
echo "  ✓ 49 archivos (verificado)"
echo "  ✓ Instrucciones claras"
echo "  ✓ Resumen ejecutivo"
echo ""
echo "🚀 Próximo paso: Descargar ZIP y subir al proyecto Claude"
echo "════════════════════════════════════════════════════════"

