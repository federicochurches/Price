#!/bin/bash
# setup_week.sh - Configurar proyecto para semana específica
# Uso: bash setup_week.sh 20 "12–18 may 2026" "Mayo 2026" 19 "5–11 may 2026"

WEEK=${1:-20}
PERIODO=${2:-"12–18 may 2026"}
MES_AÑO=${3:-"Mayo 2026"}
WEEK_PREV=${4:-19}
PERIODO_PREV=${5:-"5–11 may 2026"}

echo "🔧 Configurando proyecto para Week $WEEK..."

# 1. calc_rnd.py
echo "✓ Actualizando calc_rnd.py..."
sed -i "s/WEEK = 'W[0-9]\+'/WEEK = 'W$WEEK'/g" calc_rnd.py
sed -i "s/VOL_NUM = '[0-9]\+'/VOL_NUM = '$WEEK'/g" calc_rnd.py
sed -i "s/PERIODO = .*/PERIODO = '$PERIODO'/g" calc_rnd.py
sed -i "s/MES_AÑO = .*/MES_AÑO = '$MES_AÑO'/g" calc_rnd.py

# 2. calc_cr.py
echo "✓ Actualizando calc_cr.py..."
sed -i "s/WEEK = 'W[0-9]\+'/WEEK = 'W$WEEK'/g" calc_cr.py
sed -i "s/VOL_NUM = '[0-9]\+'/VOL_NUM = '$WEEK'/g" calc_cr.py
sed -i "s/PERIODO = .*/PERIODO = '$PERIODO'/g" calc_cr.py
sed -i "s/MES_AÑO = .*/MES_AÑO = '$MES_AÑO'/g" calc_cr.py

# 3. build_package.py
echo "✓ Actualizando build_package.py..."
sed -i "s/WEEK = [0-9]\+/WEEK = $WEEK/g" build_package.py
sed -i "s/WEEK_PREV = [0-9]\+/WEEK_PREV = $WEEK_PREV/g" build_package.py
sed -i "s/PERIODO = .*/PERIODO = '$PERIODO'/g" build_package.py
sed -i "s/PERIODO_PREV = .*/PERIODO_PREV = '$PERIODO_PREV'/g" build_package.py

# 4. render_mail_v3.py
echo "✓ Actualizando render_mail_v3.py..."
sed -i "s/WEEK = 'W[0-9]\+'/WEEK = 'W$WEEK'/g" render_mail_v3.py
sed -i "s/VOL_NUM = '[0-9]\+'/VOL_NUM = '$WEEK'/g" render_mail_v3.py
sed -i "s/PERIODO = .*/PERIODO = '$PERIODO'/g" render_mail_v3.py

echo ""
echo "✅ Proyecto configurado para Week $WEEK"
echo "   PERIODO: $PERIODO"
echo "   MES_AÑO: $MES_AÑO"
echo "   WEEK_PREV: $WEEK_PREV"
echo ""
echo "Próximo paso: python calc_rnd.py"
