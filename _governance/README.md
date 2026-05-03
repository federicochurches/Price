# 🏛 Governance · PRICE

Carpeta de gobernanza del proyecto. Acá vive todo lo que define el funcionamiento del sistema (prompts, checklists, decisiones).

## 📂 Contenido

| Archivo | Propósito |
|---|---|
| `PROMPT_MAESTRO.md` | Prompt completo que define el rol y las decisiones del proyecto. Se usa para configurar el system prompt en Claude Project. |
| `CHECKLIST_PROYECTO_CLAUDE.md` | Lista de archivos esperados en el proyecto Claude · sirve para validar el estado. |
| `CHANGELOG.md` | Histórico de versiones del prompt y decisiones consolidadas. |

---

## 🔄 Cuándo actualizar cada archivo

### `PROMPT_MAESTRO.md`
- Cada vez que se decide un cambio metodológico importante
- Bumpear versión + agregar entry en CHANGELOG
- Reemplazar el prompt del proyecto Claude con esta versión

### `CHECKLIST_PROYECTO_CLAUDE.md`
- Cuando se agregan/quitan archivos del proyecto Claude
- Cuando cambia el `Mail_W##` de referencia
- Para validar antes de cerrar una sesión

### `CHANGELOG.md`
- Cada cambio que afecte al prompt o al sistema
- Mantener orden cronológico inverso (más reciente arriba)

---

## 🎯 Cómo arrancar un chat W18+

1. Abrir chat nuevo dentro del proyecto PRICE
2. (Opcional) En el primer mensaje pedir: "Validá los archivos del proyecto contra el checklist"
3. Subir datasets crudos de la semana en cuestión + de la semana anterior
4. Subir reporte y excel de la semana anterior como referencia
5. Pedir el análisis y reportes nuevos

---

## 📚 Referencias

- **Repo:** https://github.com/federicochurches/Price
- **Hub público:** https://federicochurches.github.io/Price/
- **README del repo:** `/README.md`

---

**Última actualización:** Mayo 2026
