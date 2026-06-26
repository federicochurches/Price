"""
accounts_config.py · Catálogo de cuentas para Excels por cuenta
W26+ · Filtro sobre pickle global por CorpName exacto

Global Accounts: cadenas hoteleras internacionales (9 corps)
Cuentas Estratégicas: cuentas clave de PriceTravel (24 corps)
"""

GLOBAL_ACCOUNTS = {
    'label': 'Global Accounts',
    'file':  'GlobalAccounts',
    'corps': [
        'Accor',
        'Best Western',
        'CHOICE',
        'Hilton',
        'Hyatt',
        'IHG',
        'Marriott',
        'Oyo Rooms',
        'Wyndham',
    ],
}

CUENTAS_ESTRATEGICAS = {
    'label': 'Cuentas Estratégicas',
    'file':  'Estrategicas',
    'corps': [
        'Hyatt Inclusive Collection',
        'Barcelo',
        'Iberostar',
        'RIU',
        'Karisma',
        'Melia',
        'Royalton Hotels & Resorts',
        'GRUPO POSADAS',
        'NH',
        'PAM Hotels',
        'Krystal',
        'Emporio',
        'Park Royal',
        'Las Brisas',
        'Oasis',
        'Palace',
        'Presidente Intercontinental',
        'Sandos',
        'Villa Group',
        'Velas Resorts',
        'Palladium Hotel Group',
        'Mision',
        'Ocean by H10',
        'Bahia Principe',
    ],
}

# Lista canónica de grupos a generar
ACCOUNT_GROUPS = [GLOBAL_ACCOUNTS, CUENTAS_ESTRATEGICAS]
