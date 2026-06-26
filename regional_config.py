"""
regional_config.py · Catálogo de regiones para Excels regionales
W26+ · Filtro sobre pickle global (P80 calculado sobre universo completo)

4 regiones:
  Mexico  → Destinos México
  US      → Destinos US
  CALA    → Caribe y América Latina (excl. México)
  Global  → Worldwide (Europa, Asia, Medio Oriente, Oceanía, África, Canadá)

MIN_TRAFICO_REGIONAL: umbral permisivo vs el global (50K) para capturar
hoteles relevantes a nivel regional que no pasan el corte del universo completo.
"""

MIN_TRAFICO_REGIONAL = 10_000  # vs 50K global

REGIONES = {
    'Mexico': {
        'label':  'Destinos México',
        'file':   'Mexico',
        'paises': [
            'México',
        ],
    },
    'US': {
        'label':  'Destinos US',
        'file':   'US',
        'paises': [
            'Estados Unidos de América',
            'Puerto Rico',
            'Guam',
            'Islas Marianas del Norte',
        ],
    },
    'CALA': {
        'label':  'Destinos CALA',
        'file':   'CALA',
        'paises': [
            # Caribe
            'Anguila',
            'Antigua y Barbuda',
            'Aruba',
            'Bahamas',
            'Barbados',
            'Cuba',
            'Curazao',
            'Islas Caimán',
            'Jamaica',
            'República Dominicana',
            'San Cristóbal y Nieves',
            'Santa Lucía',
            'Sint Maarten',
            # América Central
            'Belice',
            'Costa Rica',
            'El Salvador',
            'Guatemala',
            'Honduras',
            'Nicaragua',
            'Panamá',
            # América del Sur
            'Argentina',
            'Bolivia',
            'Brasil',
            'Chile',
            'Colombia',
            'Ecuador',
            'Guyana',
            'Paraguay',
            'Perú',
            'Uruguay',
            'Venezuela',
        ],
    },
    'Global': {
        'label':  'Destinos Global',
        'file':   'Global',
        'paises': [
            # Europa Occidental
            'Alemania',
            'Austria',
            'Bélgica',
            'Croacia (Hrvatska)',
            'Dinamarca',
            'España',
            'Estonia',
            'Finlandia',
            'Francia',
            'Gran Bretaña (UK)',
            'Grecia',
            'Hungría',
            'Irlanda',
            'Italia',
            'Letonia',
            'Lituania',
            'Luxemburgo',
            'Malta',
            'Mónaco',
            'Países Bajos',
            'Polonia',
            'Portugal',
            'República Checa',
            'Rumania',
            'Serbia',
            'Eslovaquia',
            'Eslovenia',
            'Bulgaria',
            'Chipre',
            'Macedonia',
            'Montenegro',
            'Bosnia y Herzegovina',
            'Albania',
            'Ucrania',
            # Europa del Este / Asia Central
            'Georgia',
            'Kazajistán',
            'Kirguistán',
            'Azerbaiyán',
            # Medio Oriente
            'Arabia Saudita',
            'Catar',
            'Emiratos Árabes Unidos',
            'Israel',
            'Jordania',
            # África
            'Angola',
            'Cabo Verde',
            'Egipto',
            'Kenia',
            'Mauricio',
            'Marruecos',
            'Tanzania',
            'Zambia',
            # Asia
            'Bangladés',
            'Camboya',
            'China',
            'Corea (Sur)',
            'Filipinas',
            'India',
            'Indonesia',
            'Japón',
            'Laos',
            'Malasia',
            'Maldivas',
            'Singapur',
            'Sri Lanka',
            'Tailandia',
            'Turquía',
            'Vietnam',
            # Oceanía
            'Australia',
            'Nueva Zelanda (Aotearoa)',
            # Norte
            'Canadá',
            # Otros / Territorios
            'Åland',
        ],
    },
}

# Validación: todos los países deben estar en exactamente una región
def get_all_paises():
    all_p = []
    for r in REGIONES.values():
        all_p.extend(r['paises'])
    return all_p

def get_region_for_pais(pais):
    for key, r in REGIONES.items():
        if pais in r['paises']:
            return key
    return None  # países sin región asignada → no aparecen en ningún regional
