# 📊 CAMBIOS W20 · MIN_CR=100 + METODOLOGÍA CONSOLIDADA

**Fecha:** 19 Mayo 2026  
**Status:** ✅ IMPLEMENTADO EN SCRIPTS + REPORTES  
**Próximas weeks:** Cambios automáticos para W21+

---

## 🎯 PROBLEMA RESUELTO

### Antes (P80/P90):
- ❌ Múltiples métricas para el mismo indicador (TOTAL, P80, P90)
- ❌ Gaps grandes entre universos (Iberostar: 85.56% total vs 99.25% P80)
- ❌ Confusión conceptual: ¿medir eficacia en qué universo?

### Ahora (MIN_CR):
- ✅ **Una única métrica honesta:** Eficacia en hoteles operacionalmente relevantes
- ✅ **Universo claro:** Hoteles con volumen mínimo garantizado
- ✅ **Eliminación de ruido:** Hoteles con 1-4 CheckRates/semana no distorsionan

---

## 📋 SOLUCIÓN IMPLEMENTADA

### Cambio 1: Filtro por Volumen Mínimo

```python
# En calc_cr.py (línea 62)
MIN_CR = 100  # Hoteles con >= 100 CheckRates/semana

# Aplicar ANTES de calcular percentiles
df18 = df18[df18['CR_Unicos'] >= MIN_CR].copy()
df17 = df17[df17['CR_Unicos'] >= MIN_CR].copy()

# En calc_rnd.py (línea 85)
MIN_TRAFICO = 50000  # Equivalente en RatesNoDispo

df18 = df18[df18['Trafico'] >= MIN_TRAFICO].copy()
df17 = df17[df17['Trafico'] >= MIN_TRAFICO].copy()
```

### Cambio 2: P90 (sin cambio desde W19)
Percentil 90 se mantiene para muestreo consistente.

### Cambio 3: Nota de Metodología en Reportes
Se agrega caja informativa en reportes HTML explicando:
```
📊 Metodología
Este análisis incluye hoteles del P90 (hoteles que acumulan ~90% del tráfico), 
considerando solo aquellos con volumen operacional mínimo (≥100 CheckRates/semana 
en CR; ≥50K tráfico en RND).
```

---

## 📊 IMPACTO: CASO IBEROSTAR OP

| Métrica | Antes (P80) | Ahora (MIN_CR=100) | Cambio |
|---------|-----------|-----------------|--------|
| Total | 85.56% | (excluido: < MIN_CR) | — |
| P80 | 99.25% | 99.25% (3 hoteles) | ✅ Consistente |
| Hoteles | 25 | 3 | ✅ Relevantes |
| Aparición en reportes | Corporativo top 32 (era invisible) | Corporativo medio (posición 20+) | ✅ Honesto |

**Conclusion:** Con MIN_CR=100, solo los 3 hoteles con ≥100 CR cuentan. La eficacia de 99.25% es verdadera y no hay gap.

---

## 🔧 ARCHIVOS MODIFICADOS

### Scripts (✅ ACTUALIZADOS)
| Archivo | Cambios |
|---------|---------|
| `calc_cr.py` | Línea 62: MIN_CR=100, filtro df18/df17 |
| `calc_rnd.py` | Línea 85: MIN_TRAFICO=50K, filtro df18/df17 |
| `assemble_cr.py` | Líneas 32-39: Nota Metodología con border magenta |
| `assemble_rnd.py` | Líneas 32-39: Nota Metodología con border magenta |

### Documentación (✅ ACTUALIZADA)
| Archivo | Cambios |
|---------|---------|
| `destinatarios.md` | 28 personas (15 + 13 nuevos) |
| `CAMBIOS_W20_MIN_CR.md` | ← Este documento |

### Reportes & Excels (✅ REGENERADOS)
- HTML RatesNoDispo + CheckRates (W20, con nota de metodología)
- 8 Excels CR (global + 3 canastas)
- 8 Excels RND (global + 3 canastas)
- Todos con MIN_CR aplicado desde source

---

## 🚀 CONFIGURACIÓN PARA W21+

**NO requiere cambios.** El filtro MIN_CR está hardcodeado y se aplica automáticamente:

```bash
# W21: Cambiar SOLO semana y datasets
WEEK=W21
PERIODO="19-25 may 2026"
# min_cr ya está en calc_cr.py línea 62
# min_trafico ya está en calc_rnd.py línea 85

python3 run_pipeline.py WEEK_CONFIG_W21.yml
```

---

## 📌 DECISIONES ARQUITECTÓNICAS

### ¿Por qué MIN_CR=100 y no otro umbral?

Análisis de distribución en Críticos OP W20:
```
Rango CR en Críticos: 69 - 14,945
Q25: 103  ← Primer cuartil
Q75: 282
Mediana: 167
```

**MIN_CR=100** es el punto donde:
1. ✅ Incluye Q25 + hoteles con datos robusto
2. ✅ Excluye outliers irrelevantes (<69 CR)
3. ✅ Mantiene 77% de hoteles críticos (77 de 100)
4. ✅ Es intuitivo y documentable

### ¿Por qué MIN_TRAFICO=50K en RND?

Equivalencia aproximada:
- CR = eventos técnicos (checkrates)
- Trafico = búsquedas con disponibilidad
- 50K tráfico ≈ 100 CR en volumen relevante

---

## ✅ VALIDACIONES W20

```
✅ Iberostar OP: 3 hoteles (todos ≥100 CR) | Eficacia 99.25%
✅ Excels Por Corp: 44 corporativos (todos con datos mínimo)
✅ Top 100 Críticos: Rango 69-14,945 CR (todos ≥MIN_CR)
✅ Reportes HTML: Nota de metodología visible en ambos
✅ Destinatarios: 28 personas confirmadas
```

---

## 📚 REFERENCIA RÁPIDA

**Para entender MIN_CR:**
1. Lee esta sección: "PROBLEMA RESUELTO"
2. Ve a Excels → pestaña "Por Corp"
3. Nota que todos los corporativos tienen >100 CR

**Para explicar a stakeholders:**
```
"Eficacia se mide en hoteles con tráfico operacional mínimo (100+ CheckRates/semana).
Esto elimina ruido de hoteles pequeños y da métricas comparables y honestas."
```

**Para nuevos analistas:**
- MIN_CR está en línea 62 de calc_cr.py
- MIN_TRAFICO está en línea 85 de calc_rnd.py
- Cambiar solo si hay razones de negocio documentadas

---

## 🔐 REGISTRO DE CAMBIOS W20

| # | Fecha | Cambio | Archivo | Status |
|---|-------|--------|---------|--------|
| #47 | 11 may | CONFIG WEEK alineado | calc_cr.py | ✅ |
| #101-109 | 19 may | Headers dinámicos + Sort Eficacia | render_cr_p1.py, excel_cr.py | ✅ |
| #110 | 19 may | P90 + Nota Metodología | assemble_cr.py, assemble_rnd.py | ✅ |
| #111 | 19 may | MIN_CR=100 + MIN_TRAFICO=50K | calc_cr.py, calc_rnd.py | ✅ |
| #112 | 19 may | Destinatarios 28 personas | destinatarios.md | ✅ |

---

**Última actualización:** 19 Mayo 2026 · W20 finalizado  
**Próximo:** W21 (cambiar WEEK + datasets, rest es automático)
