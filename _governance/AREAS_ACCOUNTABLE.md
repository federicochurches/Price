# Catálogo de Áreas Accountable · v2

Vigente desde **Week 18** (mayo 2026). Reemplaza catálogo v1 que tenía 11 áreas distintas y se consolidó a 4.

---

## Las 4 Áreas

| Área | Cobertura · qué accionar |
|---|---|
| **Supply Optimization** | Diagnóstico técnico interno · escalamiento Súper Críticos de Eficacia y %NoDispo · saneamiento severity · BI/dashboards · monitoreo de cohortes |
| **Supply Optimization / TPS** | Diagnóstico Sin Conversión (BKGS=0) · mapping/paridad/inventario · auditoría connectivity Third Party · resolución de errors técnicos en checkrates |
| **Supply Comercial / Supply Optimization** | Casos críticos de alto volumen que requieren escalamiento KAM · cohorte Sin Conversión estructural (proyectos trimestrales) · revisión de cuentas estratégicas |
| **Supply Comercial / Wholesale** | RPM/GBM/ConvRate por canasta · pricing · SLAs corporativos · auditoría comercial canales · negociación contractual con corp |

---

## Mapeo desde catálogo v1 (lo que quedó deprecado)

| v1 (deprecado) | v2 |
|---|---|
| Tech / Connectivity | → Supply Optimization |
| Supply / BI | → Supply Optimization |
| Tech / Account Mgmt | → Supply Optimization / TPS |
| Comercial / Connectivity | → Supply Optimization / TPS |
| Supply / Tech / KAM | → Supply Comercial / Supply Optimization |
| Supply / KAM | → Supply Comercial / Supply Optimization |
| Supply / Tech | → Supply Comercial / Supply Optimization |
| Pricing / Producto | → Supply Comercial / Wholesale |
| Pricing / Supply | → Supply Comercial / Wholesale |
| Producto / Pricing | → Supply Comercial / Wholesale |
| Comercial / KAM | → Supply Comercial / Wholesale |
| Comercial / Legal | → Supply Comercial / Wholesale |

---

## Implementación

`_scripts/areas_catalogo.py` contiene la lista canónica + función `map_v1_to_v2()` para transición.

Todo el Plan de Acción (global y por canasta) usa SOLO estas 4 áreas. Cualquier label nuevo que aparezca en un brief externo debe mapearse antes de incluirlo.
