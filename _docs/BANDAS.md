# Sistema de Bandas · Vigente desde Week 18

Las bandas dividen los hoteles del P80 en 5 niveles de severidad por cada métrica. Las bandas se calibraron en Week 18 para reflejar la métrica RPM como **Gross Booking USD por millón** (antes era reservas/M).

---

## % de No Disponibilidad (RND)

| Banda | Rango | Color |
|---|---|---|
| Exitosa | < 3% | `#4FC3F4` cyan |
| Aceptable | 3 – 5% | `#5C469C` violet |
| Revisar | 5 – 20% | `#A86A1D` ámbar |
| Crítica | 20 – 60% | `#C0392B` rojo |
| Súper Crítica | > 60% | `#161616` negro |

**Target global:** < 3% (banda Exitosa)

---

## RPM (GBM USD/M) (RND)

> RPM = Gross Booking USD por millón de búsquedas = `gb_usd / Trafico × 1.000.000`

| Banda | Rango | Color |
|---|---|---|
| Exitosa | ≥ $1500 | `#4FC3F4` cyan |
| Aceptable | $650 – $1500 | `#5C469C` violet |
| Revisar | $200 – $650 | `#A86A1D` ámbar |
| Crítica | < $200 | `#C0392B` rojo |
| Sin Conversión | BKGS = 0 | `#8A8377` muted (cohorte aparte) |

**Target global:** ≥ $650 (banda Aceptable o mejor)

> **Bug fix Week 18:** Antes la función `banda_rpm()` usaba thresholds 1/2.5/4 (cuando la métrica era reservas/M). Cualquier valor RPM > 4 caía en Exitosa, dando lecturas incorrectas. Corregido a thresholds 200/650/1500 USD/M consistentes con la métrica actual.

---

## Eficacia (CR)

| Banda | Rango | Color |
|---|---|---|
| Exitosa | ≥ 97% | `#4FC3F4` cyan |
| Aceptable | 93 – 97% | `#5C469C` violet |
| Revisar | 85 – 93% | `#A86A1D` ámbar |
| Crítica | 60 – 85% | `#C0392B` rojo |
| Súper Crítica | < 60% | `#161616` negro |

**Target global:** ≥ 97% (banda Exitosa)

---

## Conv Rate (CR)

| Banda | Rango | Color |
|---|---|---|
| Exitosa | ≥ 2,5% | `#4FC3F4` cyan |
| Aceptable | 1,5 – 2,5% | `#5C469C` violet |
| Revisar | 0,8 – 1,5% | `#A86A1D` ámbar |
| Crítica | < 0,8% | `#C0392B` rojo |
| Sin Conversión | BKGS = 0 | `#8A8377` muted (cohorte aparte) |

**Target global:** ≥ 2,5% (banda Exitosa)

---

## Sistema D · "Sin Conversión" como cohorte aparte

Sin Conversión NO es la peor banda — es una **cohorte estructural separada**. Los hoteles con `BKGS=0` requieren diagnóstico técnico/contractual (mapping, paridad, inventario) y NO entran en la severity normal.

**Por qué:** antes el ~60% de hoteles caía en "Súper Crítica" porque tenían BKGS=0, saturando la severity. Ahora Severity se aplica solo a los procesables (BKGS > 0) y Sin Conversión queda como un canal de remediación distinto.

---

## Implementación

Las bandas viven en `_scripts/engine.py` en estas funciones:
- `banda_nodispo(pct)` 
- `banda_rpm(rpm, bkgs)` — métrica GBM USD/M
- `banda_eficacia(ef)`
- `banda_convrate(cv, bkgs)`

Cualquier cambio de threshold debe propagarse a:
1. `engine.py` (función)
2. `excel_cr.py` y `excel_rnd.py` (etiquetas de Severity)
3. `template_severity.py` (rangos visibles en HTML)
4. Templates HTML (rangos en cards Severity)
