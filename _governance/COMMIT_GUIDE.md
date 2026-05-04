# 🚀 Cómo aplicar este paquete al repo

## 1. Estructura del paquete

Este paquete contiene la estructura exacta que va al repo de GitHub. Tiene:

```
.
├── README.md                       ← README del repo (actualizar)
├── NIVEL_C_PENDIENTE.md            ← NUEVO archivo · documenta deuda técnica
├── index.html                      ← Hub actualizado con cards W18
├── _email/week-18/Mail_W18.html    ← NUEVO · mail ejecutivo (no se publica · solo local)
├── rates-nodispo/week-18/          ← NUEVA carpeta
│   ├── RatesNoDispo_Reporte_Editorial.html
│   ├── Analisis_Rates_NoDispo_7d.xlsx
│   └── Dataset_RatesNoDispo_W18.xlsx
└── checkrates/week-18/             ← NUEVA carpeta
    ├── CheckRates_Reporte_Editorial.html
    ├── Analisis_Checkrates_7d.xlsx
    └── Dataset_CheckRates_W18.xlsx
```

## 2. Aplicar al repo local

Desde la raíz de tu clone local de `Price`:

```bash
# 1. Copiar los archivos del ZIP descomprimido a la raíz del repo
#    (sobrescribe README.md, index.html y agrega las carpetas nuevas)
cp -r W18_Package/* /path/to/Price/

# 2. Verificar status
cd /path/to/Price
git status
```

Deberías ver:
- `modified: README.md`
- `modified: index.html`
- `new file: NIVEL_C_PENDIENTE.md`
- `new file: rates-nodispo/week-18/...` (3 archivos)
- `new file: checkrates/week-18/...` (3 archivos)
- `new file: _email/week-18/Mail_W18.html`

## 3. Verificar `.gitignore`

Asegurate de que `_email/` esté en `.gitignore` (no se publica). Si no está:

```bash
echo "_email/" >> .gitignore
git rm --cached -r _email/ 2>/dev/null || true
```

> **IMPORTANTE:** El mail tiene datos de los destinatarios y no debe publicarse. Mantenerlo siempre local.

## 4. Commit

```bash
git add .
git commit -m "feat: datos Week-18 · RatesNoDispo + CheckRates · sistema bandas D · 4-may-2026"
git push origin main
```

## 5. Verificar en producción

Una vez pusheado:

1. Esperar 1-2 minutos a que GitHub Pages actualice
2. Visitar https://federicochurches.github.io/Price/
3. Verificar que:
   - Las cards muestran Week 18
   - Los meta de cada card son correctos (%NoDispo 3,01% para RND · Eficacia 94,36% para CR)
   - Los links activos funcionan
   - El archivo muestra Week 17 activa, Week 16 activa, Week 15 disabled

## 6. Enviar el mail

1. Abrir `_email/week-18/Mail_W18.html` en el navegador local
2. Seguir las instrucciones del recuadro amarillo (copiar asunto, copiar cuerpo)
3. Pegar en Gmail/Outlook
4. Agregar 12 destinatarios en CCO (ver `destinatarios.md` local)
5. Verificar que las URLs de los reportes funcionan (deben apuntar a `https://federicochurches.github.io/Price/...week-18/...`)
6. Enviar

---

**Generado:** Mayo 2026 · post W18
