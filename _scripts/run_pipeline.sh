#!/bin/bash
# run_pipeline.sh - Ejecuta todo el pipeline en una sola llamada
# Uso: bash run_pipeline.sh {WEEK}
# Ejemplo: bash run_pipeline.sh 20

WEEK=${1:-20}

echo "🚀 Iniciando pipeline completo para Week $WEEK..."
echo ""

# Verificar que existan los datasets
if [ ! -f "Dataset_RatesNoDispo_W${WEEK}.xlsx" ]; then
    echo "❌ ERROR: Dataset_RatesNoDispo_W${WEEK}.xlsx no encontrado"
    exit 1
fi

if [ ! -f "Dataset_CheckRates_W${WEEK}.xlsx" ]; then
    echo "❌ ERROR: Dataset_CheckRates_W${WEEK}.xlsx no encontrado"
    exit 1
fi

# Arrays para tracking
declare -a STEPS=(
    "calc_rnd.py:Cálculos RND"
    "calc_cr.py:Cálculos CR"
    "render_rnd_p1.py:RND Part 1 (Hero + KPIs)"
    "render_rnd_p2.py:RND Part 2 (Core + Severity)"
    "render_rnd_p3.py:RND Part 3 (Canastas)"
    "render_cr_p1.py:CR Part 1 (Hero + Alertas)"
    "render_cr_p2.py:CR Part 2 (Core + Severity)"
    "render_cr_p3.py:CR Part 3 (Canastas)"
    "assemble_rnd.py:Ensamble RND"
    "assemble_cr.py:Ensamble CR"
    "excel_rnd.py:Excel RND (4 archivos)"
    "excel_cr.py:Excel CR (4 archivos)"
    "render_mail_v3.py:Generación Mail"
    "build_package.py:Hub + ZIP repo"
)

TOTAL_STEPS=${#STEPS[@]}
CURRENT_STEP=1
FAILED_STEPS=()
TOTAL_TIME=0

# Ejecutar cada paso
for STEP_INFO in "${STEPS[@]}"; do
    SCRIPT="${STEP_INFO%%:*}"
    DESCRIPTION="${STEP_INFO##*:}"
    
    echo "[$CURRENT_STEP/$TOTAL_STEPS] ⏳ $DESCRIPTION..."
    
    START_TIME=$(date +%s)
    
    if python "$SCRIPT" > /tmp/pipeline_${SCRIPT%.py}.log 2>&1; then
        END_TIME=$(date +%s)
        ELAPSED=$((END_TIME - START_TIME))
        TOTAL_TIME=$((TOTAL_TIME + ELAPSED))
        
        # Convertir segundos a min:sec
        MINS=$((ELAPSED / 60))
        SECS=$((ELAPSED % 60))
        
        echo "        ✅ $DESCRIPTION (${MINS}m ${SECS}s)"
    else
        END_TIME=$(date +%s)
        ELAPSED=$((END_TIME - START_TIME))
        TOTAL_TIME=$((TOTAL_TIME + ELAPSED))
        
        echo "        ❌ FALLO: $DESCRIPTION"
        FAILED_STEPS+=("$SCRIPT")
        
        # Mostrar últimas líneas del error
        echo "        Error log:"
        tail -5 /tmp/pipeline_${SCRIPT%.py}.log | sed 's/^/          /'
    fi
    
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo ""
done

# Resumen final
echo "════════════════════════════════════════════════════════"
echo "📊 PIPELINE COMPLETADO"
echo "════════════════════════════════════════════════════════"

TOTAL_MINS=$((TOTAL_TIME / 60))
TOTAL_SECS=$((TOTAL_TIME % 60))

if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    echo "✅ TODO EXITOSO"
    echo "   Tiempo total: ${TOTAL_MINS}m ${TOTAL_SECS}s"
    echo ""
    echo "Outputs generados:"
    echo "  ✓ rnd_w${WEEK}_data.pkl"
    echo "  ✓ cr_w${WEEK}_data.pkl"
    echo "  ✓ RatesNoDispo_Reporte_Editorial.html"
    echo "  ✓ CheckRates_Reporte_Editorial.html"
    echo "  ✓ 4 Excels RND"
    echo "  ✓ 4 Excels CR"
    echo "  ✓ Mail_W${WEEK}.html"
    echo "  ✓ index.html (hub)"
    echo "  ✓ Price_W${WEEK}.zip (repo)"
    echo ""
    echo "✨ Pipeline W${WEEK} LISTO PARA PRODUCCIÓN"
else
    echo "❌ FALLOS DETECTADOS (${#FAILED_STEPS[@]}):"
    for FAILED in "${FAILED_STEPS[@]}"; do
        echo "   - $FAILED"
    done
    echo ""
    echo "⏱️  Tiempo parcial: ${TOTAL_MINS}m ${TOTAL_SECS}s"
    exit 1
fi

echo "════════════════════════════════════════════════════════"
