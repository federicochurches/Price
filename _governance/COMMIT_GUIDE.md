# Commit Guide · Week 18

```bash
# Desde la raíz del repo Price/
cp -r W18_Package_Final/* .
git add .
git commit -m "feat: Week 18 · template completo + bandas RPM corregidas + estructura _template/_manual por sección · 4-may-2026"
git push origin main
```

## Estructura del repo (post Week 18)

```
Price/
├── README.md
├── index.html
├── _template/                                  # SOLO hub
│   └── _TEMPLATE_Hub.html
├── _governance/                                # docs decisiones
│   ├── BANDAS.md
│   ├── AREAS_ACCOUNTABLE.md
│   ├── ESTRUCTURA_TEMPLATE.md
│   └── CHANGELOG.md
├── _scripts/                                   # pipeline Python
├── _email/                                     # mails (no se publica)
├── rates-nodispo/
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   ├── _manual/GUIA_EDITORIAL_RatesNoDispo.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx
│       └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    ├── _manual/GUIA_EDITORIAL_CheckRates.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx
        └── Dataset_CheckRates_WNN.xlsx
```

## Validación post-commit

1. Verificar https://federicochurches.github.io/Price/ → muestra Week 18
2. Click en Supply Rates No Dispo y confirmar:
   - Header "Week 18"
   - Card RPM banda **Revisar** · target ≥ $650
   - No hay H1 narrativo
   - Análisis por canasta con Alertas + Resumen + Severity + Síntesis + Plan
3. Click en Supply CheckRates · confirmar lo mismo

## Mail

Abrir `_email/week-18/Mail_W18.html` · copiar body · enviar con 12 destinatarios en BCC.
