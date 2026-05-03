# ✅ Checklist · Archivos del proyecto Claude · PRICE

**Última actualización:** 1 mayo 2026 · post W17

---

## 📁 Archivos esperados en el proyecto Claude

Total esperado: **9 archivos**

### Configuración / governance (1)

| Estado | Archivo | Versión esperada | Tamaño aprox |
|---|---|---|---|
| ✅ | `README.md` | v2 con bandas D + estructura real del repo | ~9 KB |

### Templates (3)

| Estado | Archivo | Versión esperada | Tamaño aprox |
|---|---|---|---|
| ✅ | `_TEMPLATE_RatesNoDispo_Reporte.html` | post W17 con placeholders | ~351 KB |
| ✅ | `_TEMPLATE_CheckRates_Reporte.html` | post W17 con placeholders | ~327 KB |
| ✅ | `_TEMPLATE_Hub.html` | versión actual del hub | ~33 KB |

### Guías editoriales (2)

| Estado | Archivo | Versión esperada | Tamaño aprox |
|---|---|---|---|
| ✅ | `GUIA_EDITORIAL_RatesNoDispo.html` | v3 con sección 8 (Excel 12 pestañas) | ~16 KB |
| ✅ | `GUIA_EDITORIAL_CheckRates.html` | v3 con sección 8 (Excel 14 pestañas) + Channel agrupado | ~11 KB |

### Operacionales (3)

| Estado | Archivo | Versión esperada | Tamaño aprox |
|---|---|---|---|
| ✅ | `Mail_W17.html` | borrador W17 (referencia para futuras semanas) | ~14 KB |
| ✅ | `Playbook_Mail_Semanal.md` | workflow operativo | ~5 KB |
| ✅ | `destinatarios.md` | lista 12 destinatarios BCC | ~1 KB |

---

## ❌ Archivos que NO deben estar en el proyecto

Estos archivos viven solo en el repo GitHub, NO en el proyecto Claude:

### Reportes editoriales (live en GitHub)
- ❌ `RatesNoDispo_Reporte_Editorial.html` (cualquier semana)
- ❌ `CheckRates_Reporte_Editorial.html` (cualquier semana)

### Análisis Excel (live en GitHub)
- ❌ `Analisis_Rates_NoDispo_7d.xlsx` (cualquier semana)
- ❌ `Analisis_Checkrates_7d.xlsx` (cualquier semana)

### Datasets crudos (live en GitHub)
- ❌ `Week-NN-Rates-NoDispo.xlsx` o variantes
- ❌ `data_set_checkrates_WNN.xlsx` o variantes

### Versiones intermedias (limpiar siempre)
- ❌ Cualquier archivo con sufijos `_v1`, `_v2`, `_FIX`, `_OLD`, `_BACKUP`, `_W##` cuando la versión final ya existe sin sufijo

---

## 🔄 Cuándo subir archivos en el chat (no al proyecto)

En cada sesión semanal subís puntualmente:

### Para empezar análisis W18+
- ✅ Dataset crudo de la semana actual (RND + CR)
- ✅ Dataset crudo de la semana anterior (para comparar deltas)
- ✅ Reporte editorial de la semana anterior (referencia estructural)
- ✅ Excel de análisis de la semana anterior (referencia)

Estos archivos viven solo en la conversación · cuando termines la sesión podés borrar el chat sin perder nada (los datasets quedan en el repo Git).

---

## 🆕 Cuándo agregar archivos nuevos al proyecto Claude

Solo agregar archivos al proyecto Claude cuando:

- Sea documentación que se consulta cada semana (guías editoriales, README)
- Sea un template reutilizable (templates de reportes, hub)
- Sea workflow operativo (playbook, destinatarios)
- Sea referencia vigente del último mail enviado (Mail_W##.html)

**No agregar:**
- Reportes generados (van al repo Git)
- Datasets de una semana específica (van al repo Git)
- Versiones intermedias de fixes (van al repo Git si son finales, sino se descartan)

---

## 🔍 Cómo validar el estado del proyecto

Cada vez que arranques un chat nuevo, en mi primer mensaje yo debería ver exactamente estos 9 archivos. Si veo más o menos, te aviso.

Para forzar verificación, podés mandarme:
> "Validá los archivos del proyecto contra el checklist."

Y yo te respondo:
- ✅ Si están los 9 esperados
- ⚠ Si falta alguno o hay archivos extra
- ⚠ Si las versiones no coinciden con las esperadas

---

## 📋 Mantenimiento del checklist

Este checklist se actualiza cuando:
1. Se agregan nuevos templates al sistema (ej. nuevo tipo de reporte)
2. Se actualizan las guías editoriales (subir versión)
3. Se cambia el `Mail_W##` de referencia (cada vez que se manda uno nuevo)
4. Se agregan archivos operacionales nuevos

**Ubicación del checklist:** `_governance/CHECKLIST_PROYECTO_CLAUDE.md` en el repo `Price/`

---

**Última actualización:** Mayo 2026 · post W17
