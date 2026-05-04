# 🚀 Cómo aplicar este paquete al repo

## Estructura del paquete (Nivel B + Mail v3.1 + Glosario nuevo + Catálogo v2)

```
.
├── README.md                          ← actualizado: glosario + catálogo Áreas Accountable v2
├── NIVEL_C_PENDIENTE.md               ← roadmap para Week 19
├── COMMIT_GUIDE.md                    ← este archivo
├── areas_catalogo.py                  ← catálogo de las 4 Áreas Accountable
├── index.html                         ← Hub Week 18 con cards activas
├── _email/week-18/Mail_W18.html       ← Mail v3.1 ejecutivo · catálogo Áreas Accountable
├── rates-nodispo/week-18/             (3 archivos)
└── checkrates/week-18/                (3 archivos)
```

## Aplicar al repo local

```bash
# Desde la raíz del clone local
cp -r W18_Package/* /path/to/Price/
cd /path/to/Price
git status
```

Esperado:
- `modified: README.md`
- `modified: index.html`
- `new file: NIVEL_C_PENDIENTE.md`
- `new file: areas_catalogo.py`
- `new file: rates-nodispo/week-18/...`
- `new file: checkrates/week-18/...`
- `new file: _email/week-18/Mail_W18.html`

## Verificar `.gitignore`

```bash
echo "_email/" >> .gitignore
git rm --cached -r _email/ 2>/dev/null || true
```

## Commit

```bash
git add .
git commit -m "feat: datos Week-18 · sistema bandas D + glosario RPM/GBM + catálogo Áreas Accountable v2 · 4-may-2026"
git push origin main
```

## Verificar en producción

1. Esperar 1-2 minutos a que GitHub Pages actualice
2. Visitar https://federicochurches.github.io/Price/
3. Verificar:
   - Cards Week 18 con metas correctas
   - Reportes editoriales accesibles desde links activos
   - Archivo muestra Week 17 active, Week 16 active, Week 15 disabled

## Enviar el mail

1. Abrir `_email/week-18/Mail_W18.html` en el navegador local
2. Revisar el bloque del glosario nuevo (es la primera vez que se introduce el cambio)
3. Verificar que las 4 áreas accountable estén correctas: Supply Optimization · Supply Optimization / TPS · Supply Comercial / Supply Optimization · Supply Comercial / Wholesale
4. Copiar asunto y cuerpo, pegar en compose Gmail/Outlook
5. Agregar 12 destinatarios en BCC (`destinatarios.md` local)
6. Verificar URLs de los reportes
7. Enviar

---

**Generado:** Mayo 2026 · post Week 18 v3.1 con catálogo Áreas Accountable v2
