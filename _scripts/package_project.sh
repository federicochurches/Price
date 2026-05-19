#!/bin/bash
# package_project.sh - Generar ZIP limpio del proyecto
# Uso: bash package_project.sh 20

WEEK=${1:-20}
OUTPUT_FILE="Proyecto_PRICE_Claude_W${WEEK}.zip"

echo "📦 Empaquetando proyecto para Week $WEEK..."
echo "   Excluyendo: _TEMPLATE_Hub.html, .pyc, __pycache__, .git"
echo ""

# Generar ZIP excluido _TEMPLATE_Hub.html
zip -r "$OUTPUT_FILE" . \
  -x "*.pyc" "__pycache__/*" ".git/*" "_TEMPLATE_Hub.html" \
  > /dev/null 2>&1

# Verificar que NO esté _TEMPLATE_Hub.html
if unzip -l "$OUTPUT_FILE" | grep -q "_TEMPLATE_Hub"; then
  echo "❌ ERROR: _TEMPLATE_Hub.html sigue en el ZIP"
  exit 1
fi

SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
FILES=$(unzip -l "$OUTPUT_FILE" | grep "files$" | awk '{print $2}')

echo "✅ ZIP generado correctamente"
echo "   Archivo: $OUTPUT_FILE"
echo "   Tamaño: $SIZE"
echo "   Archivos: $FILES"
echo ""
echo "Próximo paso: Descomprime el ZIP y sube al proyecto Claude"
