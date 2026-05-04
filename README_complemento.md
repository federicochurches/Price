# Complemento Week 18 · Mail Flujo Sistémico

## Archivos a actualizar en el proyecto Claude

1. **Playbook_Mail_Semanal.md** → reemplaza la versión W17
2. **render_mail_v3.py** → versión con URL Netlify, marcadores DRAFT_BODY y bloque credenciales
3. **CHECKLIST_PROYECTO_CLAUDE.md** → reemplaza versión vieja
4. **Mail_W18.html** → versión final con credenciales y URLs Netlify
5. **_governance/MAIL_DRAFT_FLUJO.md** → NUEVO · documentación flujo Gmail MCP

## Cambios principales

### `render_mail_v3.py`
- URL_BASE cambió de `federicochurches.github.io/Price` a `analytics-desk.netlify.app`
- Bloque amarillo con credenciales del hub (`pricetravel` / `supply2026`)
- Marcadores `<!-- DRAFT_BODY_START -->` y `<!-- DRAFT_BODY_END -->` para extraer body fácil

### `Playbook_Mail_Semanal.md`
- Workflow actualizado al flujo Gmail MCP
- Comando único: `Generá el draft del mail Week NN`
- Tiempo bajó de 10-15 min → 5 min

### `_governance/MAIL_DRAFT_FLUJO.md` (nuevo)
- Spec técnica del flujo del draft
- Variantes del comando
- Pre-requisitos antes de pedir el draft
- Manejo de fallos (HTML que se "limpia")

## Para el próximo Week 19

Solo decir: `Generá el draft del mail Week 19`

Claude lee `Mail_W19.html`, extrae body entre marcadores, llama Gmail:create_draft con BCC + credenciales inyectadas, devuelve Draft ID.
