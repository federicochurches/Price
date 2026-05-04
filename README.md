# PRICE · Supply Optimization · Weekly Reports

Reportes semanales de **Supply CheckRates** y **Supply Rates No Dispo** para PriceTravel.

URL pública: https://federicochurches.github.io/Price/

## 📦 Última edición

**Week 18 · 27 Abr – 3 May 2026 · Vol. 04**

- 📊 [Supply Rates No Dispo](rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html) · % No Disponibilidad 3,01% (Aceptable, ▼0,88pp WoW) · RPM 2,23 reservas/M · GBM $479,70/M
- 📊 [Supply CheckRates](checkrates/week-18/CheckRates_Reporte_Editorial.html) · Eficacia 94,36% · Conv Rate 1,38% (Revisar, ▼0,12pp WoW)

## 📁 Estructura del repo

```
Price/
├── index.html              ← Hub público
├── README.md
├── _email/                 ← (NO se publica · solo local) mails semanales
├── rates-nodispo/week-NN/
│   ├── RatesNoDispo_Reporte_Editorial.html
│   ├── Analisis_Rates_NoDispo_7d.xlsx       (Excel Top 50, 13 pestañas)
│   └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/week-NN/
    ├── CheckRates_Reporte_Editorial.html
    ├── Analisis_Checkrates_7d.xlsx           (Excel Top 50, 17 pestañas)
    └── Dataset_CheckRates_WNN.xlsx
```

## 🔄 Glosario de métricas · vigente desde Week 18

A partir de Week 18 introducimos un glosario actualizado para distinguir mejor las métricas monetarias y de conversión:

| Sigla | Significado | Fórmula |
|---|---|---|
| **% de No Disponibilidad** | % de búsquedas sin disponibilidad | `TraficoNoDispo / Trafico` |
| **RPM** | **Reservas Por Millón** de búsquedas | `Bookings / Trafico × 1.000.000` |
| **GBM** | **Gross Booking por Millón** (USD) | `gb_usd / Trafico × 1.000.000` |
| **Eficacia** (CR) | % de CheckRates exitosos | `Successful / CheckRates_Únicos` |
| **Conv Rate** (CR) | Bookings / CheckRates | `Bookings / CheckRates_Únicos` |

> **Importante:** hasta Week 17 reportábamos "RPM" como `gb_usd / Trafico × 1M` (la métrica monetaria que ahora llamamos GBM). Desde Week 18 separamos en dos métricas distintas. La transición completa a la nueva nomenclatura en reportes editoriales y Excels se aplica desde Week 19. Los reportes Week 18 publicados conservan la nomenclatura original; el mail Week 18 introduce el cambio con nota explicativa.

## 🔄 Sistema de Bandas D · actualizadas para nuevas métricas

Las bandas se calibraron con la distribución del P80 Week 18 procesables (BKGS>0, RPM>0):

**RPM (Reservas/M)** · target ≥ 4
- Sin Conversión: BKGS=0 | Crítica: <2 | Revisar: 2–4 | Aceptable: 4–7 | Exitosa: >7

**GBM (USD/M)** · target ≥ $650
- Sin Conversión: BKGS=0 | Crítica: <$200 | Revisar: $200–$650 | Aceptable: $650–$1.500 | Exitosa: >$1.500

> Nota sobre auditoría histórica: las semanas anteriores a Week 18 (W15-W17) usan el formato anterior. No se regeneraron retroactivamente para preservar la trazabilidad histórica.

## 🎯 Catálogo de Áreas Accountable · v2 (post Week 18)

Definidas por el negocio para asignar ownership en planes de acción:

| Área | Descripción |
|---|---|
| **Supply Optimization** | Diagnóstico técnico interno · escalamiento Súper Críticos · saneamiento severity · BI/dashboards |
| **Supply Optimization / TPS** | Diagnóstico Sin Conversión · mapping/paridad/inventario · auditoría connectivity Third Party |
| **Supply Comercial / Supply Optimization** | Casos críticos volumen · escalamiento KAM · cohorte Sin Conv estructural (proyectos trimestrales) |
| **Supply Comercial / Wholesale** | RPM/GBM/ConvRate por canasta · pricing · SLAs corporativos · auditoría comercial canales |

## 📅 Workflow semanal

1. Recibir datasets Week-NN (single-sheet) → guardar en `{seccion}/week-NN/Dataset_*.xlsx`
2. Procesar con scripts → generar Excels de análisis y reportes editoriales
3. Commit a `rates-nodispo/week-NN/` y `checkrates/week-NN/`
4. Actualizar `index.html` con cards Week-NN
5. Generar mail desde `_email/week-NN/Mail_WNN.html`
6. Enviar a 12 destinatarios en BCC (ver `destinatarios.md` local)

## 📌 Próximos cambios estructurales (Week 19)

Ver `NIVEL_C_PENDIENTE.md` para el plan de actualización de templates, guías editoriales y playbook que se aplicarán post-feedback de Week 18.

---

**PriceTravel · Supply Optimization**  
Última actualización: Mayo 2026 · post Week 18
