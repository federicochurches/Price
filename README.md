# PRICE · Supply Optimization · Weekly Reports

Reportes semanales de **Supply CheckRates** y **Supply Rates No Dispo** para PriceTravel.

URL pública: https://federicochurches.github.io/Price/

## 📦 Última edición

**Week 18 · 27 Abr – 3 May 2026 · Vol. 04**

- 📊 [Supply Rates No Dispo](rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html) · %NoDispo 3,01% (Aceptable, ▼0,88pp WoW) · RPM 479,70
- 📊 [Supply CheckRates](checkrates/week-18/CheckRates_Reporte_Editorial.html) · Eficacia 94,36% · ConvRate 1,38% (Revisar, ▼0,12pp WoW)

## 📁 Estructura del repo

```
Price/
├── index.html              ← Hub público con cards de la última semana
├── README.md               ← Este archivo
├── _email/                 ← (NO se publica · solo local) mails semanales
├── _scripts/               ← (NO se publica · solo local) scripts de procesamiento
├── _template/
│   └── _TEMPLATE_Hub.html
├── rates-nodispo/
│   ├── _manual/GUIA_EDITORIAL_RatesNoDispo.html
│   ├── _template/_TEMPLATE_RatesNoDispo_Reporte.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html  ← deliverable público
│       ├── Analisis_Rates_NoDispo_7d.xlsx       ← Excel Top 50 (13 pestañas)
│       └── Dataset_RatesNoDispo_WNN.xlsx        ← dataset crudo
└── checkrates/
    ├── _manual/GUIA_EDITORIAL_CheckRates.html
    ├── _template/_TEMPLATE_CheckRates_Reporte.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx           ← Excel Top 50 (17 pestañas)
        └── Dataset_CheckRates_WNN.xlsx
```

## 🔄 Sistema de bandas D · vigente desde Week 18

A partir de Week 18 se aplican las decisiones consolidadas post-W17 (ver `FIXES_PENDIENTES_W18.md`):

- **Sistema bandas D · 5 niveles separando "Sin Conversión" de Severity**
  - Hoteles con BKGS = 0 son cohorte estructural aparte (diagnóstico técnico/contractual)
  - Severity solo aplica a hoteles procesables (BKGS > 0)
- **Plan de Acción reordenado** · badge owner como protagonista, cluster (Quick Win · Mid · Estratégica) y código de seguimiento van debajo
- **Plan de Acción dentro de cada canasta** · cada canasta (B2C · B2B-OP · CUG) tiene 6 acciones específicas
- **Channel agrupado destacado en CR** · Producto Propio vs Third Party
- **Capitalización editorial** · todos los findings arrancan con mayúscula
- **Excels estandarizados** · CR 17 pestañas (incluyen Por Destino y Por Channel) · RND 13 pestañas
- **Datasets single-sheet** · una fila por combinación Hotel × Canasta (× Channel para CR)

> **Nota sobre auditoría histórica:** Las semanas anteriores a W18 (W15, W16, W17) usan el formato anterior. No se regeneraron retroactivamente para preservar la trazabilidad de lo que efectivamente se envió a los destinatarios cada semana.

## 📅 Workflow semanal

1. Recibir datasets Week-NN (single-sheet) → guardar en `{seccion}/week-NN/Dataset_*.xlsx`
2. Procesar con scripts → generar Excels de análisis (Top 50) y reportes editoriales
3. Commit a `rates-nodispo/week-NN/` y `checkrates/week-NN/`
4. Actualizar `index.html` con cards Week-NN
5. Generar mail desde `_email/week-NN/Mail_WNN.html`
6. Enviar a 12 destinatarios en BCC (ver `destinatarios.md` local)

## 📌 Próximos cambios estructurales (Week 19)

Ver `NIVEL_C_PENDIENTE.md` para el plan de actualización de templates, guías editoriales y playbook que se aplicarán post-feedback de W18.

---

**PriceTravel · Supply Optimization**  
Última actualización: Mayo 2026 · post W18
