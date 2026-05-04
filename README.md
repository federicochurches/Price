# PRICE · Supply Optimization · Weekly Reports

Reportes semanales de **Supply CheckRates** y **Supply Rates No Dispo** para PriceTravel, dirigidos al equipo de Supply Optimization, Comercial y Stakeholders ejecutivos.

URL pública: https://federicochurches.github.io/Price/

---

## 📦 Última edición · Week 18 · 27 Abr – 3 May 2026

| Reporte | Métrica clave | Banda | Link |
|---|---|---|---|
| **Supply Rates No Dispo** | % NoDispo 3,01% (▼0,88pp WoW) · RPM $479,70/M | Aceptable / Revisar | [Editorial](rates-nodispo/week-18/RatesNoDispo_Reporte_Editorial.html) |
| **Supply CheckRates** | Eficacia 94,36% (▲0,25pp WoW) · Conv Rate 1,38% (▼0,12pp) | Aceptable / Revisar | [Editorial](checkrates/week-18/CheckRates_Reporte_Editorial.html) |

---

## 🔄 Glosario de métricas (vigente desde Week 18)

| Sigla | Significado | Fórmula |
|---|---|---|
| **% de No Disponibilidad** | % búsquedas sin disponibilidad | `TraficoNoDispo / Trafico` |
| **RPM (GBM USD/M)** | **Gross Booking USD por millón** de búsquedas | `gb_usd / Trafico × 1.000.000` |
| **Eficacia** (CR) | % CheckRates exitosos | `Successful / CR_Únicos` |
| **Conv Rate** (CR) | Bookings / CheckRates | `Bookings / CR_Únicos` |

> **Nota Week 18:** la métrica RPM ahora se interpreta como Gross Booking USD por millón (antes era reservas por millón). Bandas y target actualizados (ver `_governance/BANDAS.md`).

---

## 🎯 Catálogo de Áreas Accountable · v2 (vigente desde Week 18)

| Área | Cobertura |
|---|---|
| **Supply Optimization** | Diagnóstico técnico interno · escalamiento Súper Críticos · saneamiento severity · BI/dashboards |
| **Supply Optimization / TPS** | Diagnóstico Sin Conversión · mapping/paridad/inventario · auditoría connectivity Third Party |
| **Supply Comercial / Supply Optimization** | Casos críticos volumen · escalamiento KAM · cohorte Sin Conv estructural |
| **Supply Comercial / Wholesale** | RPM/GBM/ConvRate por canasta · pricing · SLAs corporativos · auditoría comercial canales |

Ver `_governance/AREAS_ACCOUNTABLE.md` para detalle completo de mapeo.

---

## 📁 Estructura del repo

```
Price/
├── README.md
├── index.html
├── _template/                                  # SOLO template del Hub
│   └── _TEMPLATE_Hub.html
├── _governance/                                # NO se publica · documentación
│   ├── BANDAS.md                               # bandas calibradas y thresholds
│   ├── AREAS_ACCOUNTABLE.md                    # catálogo v2
│   ├── CHANGELOG.md                            # cambios por semana
│   └── ESTRUCTURA_TEMPLATE.md                  # estructura editorial
├── _scripts/                                   # NO se publica · pipeline Python
│   ├── README.md
│   ├── engine.py                               # bandas + agregaciones
│   ├── render_helpers.py                       # formato + clean_hotel_name
│   ├── calc_cr.py / calc_rnd.py
│   ├── render_cr_p1/p2/p3.py
│   ├── render_rnd_p1/p2/p3.py
│   ├── assemble_*.py                           # ensamblado HTML
│   ├── excel_*.py                              # Excel Top 50
│   ├── render_mail_v3.py
│   ├── template_resumen.py / alertas.py / severity.py
│   ├── areas_catalogo.py
│   └── snippets/                               # snippets literales del template
├── _email/                                     # NO se publica
│   └── week-NN/Mail_WNN.html
├── rates-nodispo/
│   ├── _template/
│   │   └── _TEMPLATE_RatesNoDispo_Reporte.html
│   ├── _manual/
│   │   └── GUIA_EDITORIAL_RatesNoDispo.html
│   └── week-NN/
│       ├── RatesNoDispo_Reporte_Editorial.html
│       ├── Analisis_Rates_NoDispo_7d.xlsx
│       └── Dataset_RatesNoDispo_WNN.xlsx
└── checkrates/
    ├── _template/
    │   └── _TEMPLATE_CheckRates_Reporte.html
    ├── _manual/
    │   └── GUIA_EDITORIAL_CheckRates.html
    └── week-NN/
        ├── CheckRates_Reporte_Editorial.html
        ├── Analisis_Checkrates_7d.xlsx
        └── Dataset_CheckRates_WNN.xlsx
```

> **Convención Week 18:** En la raíz `_template/` SOLO va el template del Hub. Los templates de cada reporte y sus guías editoriales viven en `<seccion>/_template/` y `<seccion>/_manual/` respectivamente.

---

## 📋 Secciones del Reporte Editorial

### Estructura post Week 18

**Header** (masthead) → **Métricas globales inline** → **Cards Hero** (KPI principal + secundario con tabs País/Destino/Corp/Hotel/Canasta/Channel) → **Alertas Críticas** (3 cards) → **Resumen Ejecutivo** (10 findings · 2 columnas con valor numérico destacado) → **Severidad** → **Top 5/10 listings por sección** → **Plan de Acción** (6 acciones · 2 columnas · catálogo Áreas Accountable v2) → **Análisis por Canasta** (B2C · B2B-OP · CUG, cada una con su propio bloque interno completo)

**Cada canasta contiene:** KPI block · Alertas Críticas · Resumen Ejecutivo · Severidad · Tabs por dimensión · Top 10 Bajo Rendimiento · Top 10 Sin Conversión · Síntesis ejecutiva · Plan de Acción

> Ver `_governance/ESTRUCTURA_TEMPLATE.md` para detalle exacto.

---

## 🚀 Workflow Semanal

1. Recibir datasets crudos (`Dataset_<Reporte>_W<NN>.xlsx` single-sheet) y guardarlos en `{seccion}/week-NN/`
2. Correr pipeline desde `_scripts/`: `python calc_*.py && python render_*.py && python assemble_*.py && python excel_*.py`
3. Validar resultados con screenshots
4. Generar mail desde `_email/week-NN/Mail_WNN.html`
5. Commit GitHub: `feat: datos Week-NN · [fecha]`
6. Enviar mail con 12 destinatarios en BCC (ver `_email/destinatarios.md`)

---

**PriceTravel · Supply Optimization** · Última actualización: Week 18 · Mayo 2026
