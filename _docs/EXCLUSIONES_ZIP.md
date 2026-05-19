# 🚫 Archivos que NUNCA deben ir en el ZIP del proyecto

**Actualizado:** 12 mayo 2026

## Archivos explícitamente excluidos

### `_TEMPLATE_Hub.html`
- **Por qué:** Vive SOLO en GitHub bajo `_template/`, nunca en el proyecto Claude
- **Tamaño:** 35 KB · no se necesita para el pipeline
- **Acción:** Si aparece, eliminarlo inmediatamente
- **En ZIP:** Explícitamente excluido con `-x "_TEMPLATE_Hub.html"`

## Cómo generar ZIP limpio

```bash
cd /mnt/project && zip -r Proyecto_PRICE_Claude_W20_COMPLETO.zip . \
  -x "*.pyc" "__pycache__/*" ".git/*" "_TEMPLATE_Hub.html"
```

**⚠️ NO OLVIDAR:** La flag `-x "_TEMPLATE_Hub.html"` al final del comando zip

## Verificar que no está en ZIP

```bash
unzip -l Proyecto_PRICE_Claude_W20_COMPLETO.zip | grep -i "_TEMPLATE_Hub"
# No debe devolver nada (silencio = correcto)
```

