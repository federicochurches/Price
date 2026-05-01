#!/bin/bash
# ==========================================================================
# PRICE · Release W17 + Regeneración W16 · Script de commit
# ==========================================================================
# Uso:
#   1. Descomprimir PRICE_Release_W17.zip
#   2. Editar PACKAGE_DIR y REPO_DIR
#   3. Ejecutar: bash _scripts/commit_W17.sh
# ==========================================================================

set -e

PACKAGE_DIR="$HOME/Downloads/release_W17"
REPO_DIR="$HOME/Documents/GitHub/Price"

echo ""
echo "==========================================="
echo "PRICE · Commit W17 + Regeneración W16"
echo "==========================================="
echo ""
echo "Paquete: $PACKAGE_DIR"
echo "Repo:    $REPO_DIR"
echo ""

[ ! -d "$PACKAGE_DIR" ] && { echo "✗ ERROR: $PACKAGE_DIR no existe"; exit 1; }
[ ! -d "$REPO_DIR/.git" ] && { echo "✗ ERROR: $REPO_DIR no es un repo git"; exit 1; }

echo "Esto va a copiar:"
echo ""
echo "RAÍZ:"
echo "  index.html"
echo "  _docs/README.md"
echo "  _email/Mail_W17.html"
echo "  _scripts/commit_W17.sh"
echo "  _template/_TEMPLATE_Hub.html"
echo ""
echo "CHECKRATES:"
echo "  checkrates/_manual/GUIA_EDITORIAL_CheckRates.html"
echo "  checkrates/_template/_TEMPLATE_CheckRates_Reporte_Editorial.html"
echo "  checkrates/week-16/CheckRates_Reporte_Editorial.html (regenerado)"
echo "  checkrates/week-16/Analisis_Checkrates_7d_W16.xlsx (regenerado)"
echo "  checkrates/week-17/CheckRates_Reporte_Editorial.html"
echo "  checkrates/week-17/Analisis_Checkrates_7d_W17.xlsx"
echo ""
echo "RATES NO DISPO:"
echo "  rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html"
echo "  rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte_Editorial.html"
echo "  rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html (regenerado)"
echo "  rates-nodispo/week-16/Analisis_Rates_NoDispo_7d_W16.xlsx (regenerado)"
echo "  rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html"
echo "  rates-nodispo/week-17/Analisis_Rates_NoDispo_7d_W17.xlsx"
echo ""
read -p "¿Continuar? [y/N] " -n 1 -r
echo ""
[[ ! $REPLY =~ ^[Yy]$ ]] && { echo "Cancelado."; exit 0; }

# Crear estructura
echo ""
echo "▶ Creando estructura..."
mkdir -p "$REPO_DIR/_docs" "$REPO_DIR/_email" "$REPO_DIR/_scripts" "$REPO_DIR/_template"
mkdir -p "$REPO_DIR/checkrates/_manual" "$REPO_DIR/checkrates/_template"
mkdir -p "$REPO_DIR/checkrates/week-16" "$REPO_DIR/checkrates/week-17"
mkdir -p "$REPO_DIR/rates-nodispo/_manual" "$REPO_DIR/rates-nodispo/_template"
mkdir -p "$REPO_DIR/rates-nodispo/week-16" "$REPO_DIR/rates-nodispo/week-17"

# Copiar
echo ""
echo "▶ Copiando archivos..."

# Raíz
cp "$PACKAGE_DIR/index.html" "$REPO_DIR/index.html" && echo "  ✓ index.html"
cp "$PACKAGE_DIR/_docs/README.md" "$REPO_DIR/_docs/README.md" && echo "  ✓ _docs/README.md"
cp "$PACKAGE_DIR/_email/Mail_W17.html" "$REPO_DIR/_email/Mail_W17.html" && echo "  ✓ _email/Mail_W17.html"
cp "$PACKAGE_DIR/_scripts/commit_W17.sh" "$REPO_DIR/_scripts/commit_W17.sh"
chmod +x "$REPO_DIR/_scripts/commit_W17.sh" && echo "  ✓ _scripts/commit_W17.sh"
cp "$PACKAGE_DIR/_template/_TEMPLATE_Hub.html" "$REPO_DIR/_template/_TEMPLATE_Hub.html" && echo "  ✓ _template/_TEMPLATE_Hub.html"

# CheckRates
cp "$PACKAGE_DIR/checkrates/_manual/GUIA_EDITORIAL_CheckRates.html" "$REPO_DIR/checkrates/_manual/" && echo "  ✓ checkrates/_manual/GUIA_EDITORIAL_CheckRates.html"
cp "$PACKAGE_DIR/checkrates/_template/_TEMPLATE_CheckRates_Reporte_Editorial.html" "$REPO_DIR/checkrates/_template/" && echo "  ✓ checkrates/_template/_TEMPLATE_CheckRates_Reporte_Editorial.html"
cp "$PACKAGE_DIR/checkrates/week-16/CheckRates_Reporte_Editorial.html" "$REPO_DIR/checkrates/week-16/" && echo "  ✓ checkrates/week-16/CheckRates_Reporte_Editorial.html"
cp "$PACKAGE_DIR/checkrates/week-16/Analisis_Checkrates_7d_W16.xlsx" "$REPO_DIR/checkrates/week-16/" && echo "  ✓ checkrates/week-16/Analisis_Checkrates_7d_W16.xlsx"
cp "$PACKAGE_DIR/checkrates/week-17/CheckRates_Reporte_Editorial.html" "$REPO_DIR/checkrates/week-17/" && echo "  ✓ checkrates/week-17/CheckRates_Reporte_Editorial.html"
cp "$PACKAGE_DIR/checkrates/week-17/Analisis_Checkrates_7d_W17.xlsx" "$REPO_DIR/checkrates/week-17/" && echo "  ✓ checkrates/week-17/Analisis_Checkrates_7d_W17.xlsx"

# Rates No Dispo
cp "$PACKAGE_DIR/rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html" "$REPO_DIR/rates-nodispo/_manual/" && echo "  ✓ rates-nodispo/_manual/GUIA_EDITORIAL_RatesNoDispo.html"
cp "$PACKAGE_DIR/rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte_Editorial.html" "$REPO_DIR/rates-nodispo/_template/" && echo "  ✓ rates-nodispo/_template/_TEMPLATE_RatesNoDispo_Reporte_Editorial.html"
cp "$PACKAGE_DIR/rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html" "$REPO_DIR/rates-nodispo/week-16/" && echo "  ✓ rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html"
cp "$PACKAGE_DIR/rates-nodispo/week-16/Analisis_Rates_NoDispo_7d_W16.xlsx" "$REPO_DIR/rates-nodispo/week-16/" && echo "  ✓ rates-nodispo/week-16/Analisis_Rates_NoDispo_7d_W16.xlsx"
cp "$PACKAGE_DIR/rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html" "$REPO_DIR/rates-nodispo/week-17/" && echo "  ✓ rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html"
cp "$PACKAGE_DIR/rates-nodispo/week-17/Analisis_Rates_NoDispo_7d_W17.xlsx" "$REPO_DIR/rates-nodispo/week-17/" && echo "  ✓ rates-nodispo/week-17/Analisis_Rates_NoDispo_7d_W17.xlsx"

# Git
echo ""
echo "▶ git status:"
cd "$REPO_DIR"
git status --short

echo ""
read -p "¿Continuar con git add + commit + push? [y/N] " -n 1 -r
echo ""
[[ ! $REPLY =~ ^[Yy]$ ]] && { echo "Cancelado · archivos copiados pero NO commiteados."; exit 0; }

echo ""
echo "▶ git add..."
git add index.html _docs/ _email/ _scripts/ _template/ checkrates/ rates-nodispo/

echo "▶ git commit..."
git commit -m "feat: release W17 ampliado + regeneración retroactiva W16

W17 (20-26 Abr 2026) + W16 regenerado (13-19 Abr 2026)

Cambios estructurales aplicados a ambos reportes en ambas semanas:

- Severity unificada en 5 niveles (Exitosa · Aceptable · Revisar · Crítica · Súper Crítica)
- Canastas colapsables con <details> HTML5 nativo · pill Expandir/Contraer
- Naming editorial consistente (Severidad → Críticos → Bajo Rend → Concentración → No convierten → Plan)
- Concentración por Corporativo con %Portfolio + %Share
- Tabs Top 5 por canasta · Destino/Corp/Hotel/Provider (CheckRates)
- Banner de alertas por canasta (CheckRates)
- Tablas Top 10 a 2 columnas
- Método con fondo oscuro · cards categorizadas
- Mail unificado (CR + RND en un solo mail)

Reorganización del repo:
- _docs/    → README
- _email/   → mail unificado
- _scripts/ → scripts de commit
- _template/→ template del Hub en raíz; templates de reportes siguen por subcarpeta

Datos:
- CR W16: 32.835 hoteles · 4.720 P80 · Eficacia 93.95% · CR 1.67% · 30.333 BKGS
- CR W17: 32.857 hoteles · 4.860 P80 · Eficacia 94.12% · CR 1.50% · 29.001 BKGS
- RND W16: 53.985 hoteles · 16.051 P80 · %NoDispo 3.81% · 16.1M tráfico · 40.175 BKGS · \$9.48M GB
- RND W17: 54.004 hoteles · 19.346 P80 · %NoDispo 3.91% · 17.2M tráfico · 39.267 BKGS · \$8.90M GB

Excels regenerados desde cero · Top 50 por pestaña.

W16 regenerado retroactivamente con datasets crudos:
- W16 RND tiene CorpName · Concentración por Corporativo real
- W17 RND no tiene CorpName en export · usado Concentración por Destino como proxy
- Acción crítica W18: re-exportar W17 RND con CorpName

Mail unificado Vol. 03:
- KPI strip por reporte
- Plan acción con badges QW/MP/ES
- Sección 'Cambios estructurales del reporte W17'

Próximo release: lunes 5 de mayo · Week 18"

echo "▶ git push origin main..."
git push origin main

echo ""
echo "==========================================="
echo "✓ COMMIT COMPLETADO"
echo "==========================================="
echo ""
echo "URLs públicas:"
echo "  Hub:           https://federicochurches.github.io/Price/"
echo "  CR W17:        https://federicochurches.github.io/Price/checkrates/week-17/CheckRates_Reporte_Editorial.html"
echo "  RND W17:       https://federicochurches.github.io/Price/rates-nodispo/week-17/RatesNoDispo_Reporte_Editorial.html"
echo "  CR W16:        https://federicochurches.github.io/Price/checkrates/week-16/CheckRates_Reporte_Editorial.html"
echo "  RND W16:       https://federicochurches.github.io/Price/rates-nodispo/week-16/RatesNoDispo_Reporte_Editorial.html"
echo ""
echo "GitHub Pages tarda 1-2 minutos en desplegar."
echo ""
echo "Próximo paso: enviar mail unificado al equipo (_email/Mail_W17.html)"
