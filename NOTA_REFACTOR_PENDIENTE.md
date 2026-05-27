# 🔧 REFACTOR P9 · Centralización CR/RND · CERRADO W22
**Fecha cierre:** 2026-05-26

## Estado: ✅ COMPLETADO

### Lo que se hizo

#### 1. `render_helpers.py` — funciones nuevas agregadas

| Función | Propósito |
|---|---|
| `KPI_TOP_N = 10` | **Constante única** para top visible — 1 línea para cambiar |
| `render_traf_wow_pill_pct(pct_delta)` | Pill WoW de tráfico expresado como % |
| `render_traf_wow_pill_abs(abs_delta)` | Pill WoW de tráfico expresado como delta absoluto |
| `render_traf_line_cr(cr_current, cr_prev)` | Línea "Tráfico: 746.111 ↑pill" para CR |
| `render_traf_line_rnd(trafico_current, trafico_prev)` | Línea "Tráfico: 12,2B ↑pill" para RND |
| `_resolve_label(r, t_key)` | Extrae (raw_lab, lab, corp_sub) según t_key — centraliza lógica de etiquetado |
| `build_kpi_tab_rows(df_t, t_key, cfg)` | Genera HTML de filas con `cfg` dict — el corazón del refactor |
| `build_kpi_tab_panel(df_t, t_key, cfg, spec)` | Construye `<div class="tab-panel">` completo |

#### 2. `render_cr_p1.py`
- Loop Eficacia reemplazado por dict `_EF_CFG` + llamada a `build_kpi_tab_panel()`
- Loop ConvRate reemplazado por dict `_CV_CFG` + llamada a `build_kpi_tab_panel()`
- `_cr_trafico_line()` delegada a `render_traf_line_cr()`
- Duplicado inline de traf_line en `render_kpi_card_eficacia` eliminado
- **−138 líneas** (791 → 653)

#### 3. `render_rnd_p1.py`
- Loop NoDispo reemplazado por dict `_ND_CFG` + llamada a `build_kpi_tab_panel()`
- Loop IPM reemplazado por dict `_IPM_CFG` + llamada a `build_kpi_tab_panel()`
- Ambas `_traf_line` inline reemplazadas por `render_traf_line_rnd()`
- **−80 líneas** (538 → 458)

### Criterio de éxito cumplido

Un cambio en `KPI_TOP_N` (hoy `10`) requiere modificar **1 sola línea** en `render_helpers.py`. ✅

### Nota de diseño — tabs "channel" y "canasta"

Los tabs `channel` (CR) y `canasta` (ambos) conservan su lógica ad-hoc porque:
- `channel` necesita split PP/TP con grid diferente (4 cols vs 6)
- `canasta` no tiene WoW por fila ni filtro de corpus

`build_kpi_tab_panel()` devuelve `''` si `t_key == 'channel'`, delegando al caller.

---
> P9 movido a HISTORIAL_SESIONES como bug cerrado.

