# 📦 PRICE · Week 17 · Commit Etapa 2

Paquete completo listo para commit a GitHub. Estructura respeta el README v1.6.

---

## 🚀 Cómo hacer el commit

### Opción A · Un solo commit grande (recomendado)

```bash
# Desde la raíz del repo Price/
# Copiar el contenido del paquete encima (sobrescribe lo existente)
cp -r PRICE_W17_Etapa2_Commit/* .

git add .
git commit -m "feat: Etapa 2 · Severity 5 niveles + Hero tabs + horizontalización · Week 17

- Templates rediseñados (CR + RND) con 9 layouts horizontalizados
- Severity unificado: Crítica + Muy Crítica → Crítica Severa
- Conv Rate Etapa 2: BK/Successful (no BK/CK)
- Plan numerado 1-10 sin códigos QW/MP/ES
- Hero Variante B: bajada + KPI cards con tabs CSS-only
- Reportes W17 republicados en formato Etapa 2
- xlsx W17 reconstruidos: 11 hojas RND · 16 hojas CR según contrato
- Guías editoriales v1.6 actualizadas
- Mails W17 con anuncio del rediseño
- Hub: Week 18 placeholder · Week 17 archivado con badge ETAPA 2
- README v1.6 con changelog completo

13 archivos en total. Próximo release: Week 18 (lunes 5 mayo) en formato nativo Etapa 2."

git push
```

### Opción B · Dos commits separados (CR y RND)

```bash
# Primer commit: CheckRates
git add checkrates/ _editorial/GUIA_EDITORIAL_CheckRates.html mail/Mail_CheckRates_W17.html
git commit -m "feat: CheckRates · Etapa 2 · Week 17

- Template rediseñado: §02 unifica Severity Eficacia + Conv Rate
- Severity 5+5 niveles con paleta unificada
- Conv Rate fórmula Etapa 2 (BK/Successful)
- xlsx W17 con 16 pestañas según contrato
- Guía editorial v1.6 + mail W17 con anuncio Etapa 2"

# Segundo commit: RatesNoDispo (incluye bugfix)
git add rates-nodispo/ _editorial/GUIA_EDITORIAL_RatesNoDispo.html mail/Mail_RatesNoDispo_W17.html
git commit -m "feat: RatesNoDispo · Etapa 2 · Week 17 + bugfix

- Template rediseñado: 13 secciones horizontalizadas
- Severity 5 niveles (Crítica + Muy Crítica → Crítica Severa)
- Hero Variante B con tabs (Por Canasta · Corp · Hotel/Destino)
- xlsx W17 con 11 pestañas según contrato
- BUGFIX: removidas 290 líneas zombie tras </body>
- Plan numerado 1-10 sin códigos QW/MP/ES"

# Tercer commit: Hub + README + global
git add index.html README.md
git commit -m "chore: Hub Week 18 placeholder + README v1.6 Etapa 2

- Hub: Week 18 placeholder en cards principales
- Week 17 movido al archivo con badge ETAPA 2
- README v1.6: changelog Etapa 2 completo + paleta + reglas BK/Suc
- Calendario W17 marcado como Re-publicado Etapa 2"

git push
```

---

## 📋 Validaciones pre-commit

### URLs en Hub

```bash
# Verificar que los archivos referenciados existen
grep -oE 'href="(checkrates|rates-nodispo)[^"]*"' index.html
```

### URLs en mails

Los mails apuntan a `analytics-desk.netlify.app/<reporte>/week-17/...`. Confirmá que la estructura de Netlify sigue esa convención antes de enviar el lunes.

### xlsx sin errores

```bash
# Si tenés Excel/LibreOffice, abrir cada xlsx y verificar:
# - 11 hojas RND · 16 hojas CR
# - Sin #REF! ni #DIV/0!
# - Pestañas con headers correctos
```

---

## 📂 Inventario del paquete

```
PRICE_W17_Etapa2_Commit/
├── index.html                                                  (Hub)
├── README.md                                                   (v1.6)
├── COMMIT_INSTRUCTIONS.md                                      (este archivo)
│
├── _editorial/
│   ├── GUIA_EDITORIAL_CheckRates.html                          (v1.6 · 541 líneas)
│   └── GUIA_EDITORIAL_RatesNoDispo.html                        (v1.6 · 472 líneas)
│
├── checkrates/
│   ├── _template/
│   │   └── Template_CheckRates_Reporte_Editorial.html          (2.120 líneas · 589 placeholders)
│   └── week-17/
│       ├── CheckRates_Reporte_Editorial.html                 (2.120 líneas · datos W17)
│       └── Analisis_Checkrates_7d.xlsx                       (16 pestañas · Top 20)
│
├── rates-nodispo/
│   ├── _template/
│   │   └── Template_RatesNoDispo_Reporte_Editorial.html        (2.325 líneas · 607 placeholders)
│   └── week-17/
│       ├── RatesNoDispo_Reporte_Editorial.html               (2.241 líneas · BUGFIX aplicado)
│       └── Analisis_Rates_NoDispo_7d.xlsx                    (11 pestañas · Top 20)
│
└── mail/
    ├── Mail_CheckRates_W17.html                                (110 líneas · brand violeta)
    └── Mail_RatesNoDispo_W17.html                              (119 líneas · brand magenta)
```

**Total: 13 archivos en 7 carpetas**

---

## ✅ Próximo release

**Week 18 · lunes 5 de mayo de 2026** · primer release con datos completos en formato Etapa 2 nativo (HTML + xlsx generados desde dataset crudo W18 directamente).

Cuando recibas los datasets W18, el flujo será:

1. Procesar `Week18CheckRates.xlsx` y `Week18RatesNoDispo.xlsx` con scripts Etapa 2
2. Generar reportes editoriales W18 (rellenando templates)
3. Generar xlsx de análisis W18 (mismas 11 + 16 pestañas)
4. Crear mails W18 (a partir de templates o adaptando los W17)
5. Mover W17 al archivo del Hub · activar W18 como card principal
6. Commit + push + envío
