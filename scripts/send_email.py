#!/usr/bin/env python3
"""
send_email.py · Generador semi-automático del email semanal · CheckRates

USO:
    python send_email.py <NUMERO_SEMANA>

EJEMPLO:
    python send_email.py 17

QUÉ HACE:
    1. Lee la plantilla email/CheckRates_Mail_Template.txt (y .html)
    2. Reemplaza {{WEEK_NUM}} con el número de semana
    3. Genera 3 archivos en email/output/:
        - checkrates_week_NN_mail.txt   (cuerpo plano para copiar/pegar)
        - checkrates_week_NN_mail.html  (cuerpo HTML para clientes que soporten)
        - checkrates_week_NN_link.txt   (link de Gmail compose pre-armado)
    4. Imprime instrucciones del paso a paso

POR QUÉ NO MANDA SOLO:
    Gmail vía SMTP requiere App Password + tokens. El approach semi-automático
    es más seguro y robusto: el script arma todo, vos revisás antes de mandar.

FLUJO TÍPICO:
    $ python send_email.py 17
    
    📧 Mail Week 17 generado.
    
    👉 PASO 1: Abrir el link del compose:
       https://mail.google.com/mail/?view=cm&...
       (También guardado en: email/output/checkrates_week_17_link.txt)
    
    👉 PASO 2: Pegar el cuerpo del mail (que se abre en una ventana nueva):
       email/output/checkrates_week_17_mail.txt
    
    👉 PASO 3: Revisar destinatarios y asunto, apretar Enviar.
"""

import sys
import os
import urllib.parse
from datetime import datetime

# ============================================================
# CONFIG — datos de envío (modificable)
# ============================================================

# Email de origen (visible en From cuando se envía)
FROM_EMAIL = 'federico.iglesias@pricetravel.com'

# Lista de destinatarios (To)
DESTINATARIOS = [
    'rafael.durand@pricetravel.com',
    'bellanira.hernandez@pricetravel.com',
    'maria.rico@pricetravel.com',
    'javier.parra@pricetravel.com',
    'alonso.mis@pricetravel.com',
    'daniela.madrigal@pricetravel.com',
    'ingrid.kuhnne@pricetravel.com',
    'david.gamboa@pricetravel.com',
    'hugo.ascencio@pricetravel.com',
    'ext.jesus.lizarraga@pricetravel.com',
]

# CC y BCC (vacíos por ahora — agregar si hace falta)
CC_LIST = []
BCC_LIST = []

# Asunto — {WEEK_NUM} se reemplaza
SUBJECT_TEMPLATE = 'Supply Optimization · Reporte CheckRates Week-{WEEK_NUM}'

# Link del hub (Netlify con login)
LINK_HUB = 'https://analytics-desk.netlify.app/'

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RELEASE_DIR = os.path.dirname(SCRIPT_DIR)
EMAIL_DIR = os.path.join(RELEASE_DIR, 'email')
TEMPLATE_TXT = os.path.join(EMAIL_DIR, 'CheckRates_Mail_Template.txt')
TEMPLATE_HTML = os.path.join(EMAIL_DIR, 'CheckRates_Mail_Template.html')
OUTPUT_DIR = os.path.join(EMAIL_DIR, 'output')


def render_template(week_num):
    """Lee las plantillas y reemplaza placeholders"""
    placeholders = {
        '{{WEEK_NUM}}': f'{week_num:02d}',
        '{{LINK_HUB}}': LINK_HUB,
    }
    
    # Plain text
    with open(TEMPLATE_TXT) as f:
        body_txt = f.read()
    for k, v in placeholders.items():
        body_txt = body_txt.replace(k, v)
    
    # HTML
    with open(TEMPLATE_HTML) as f:
        body_html = f.read()
    for k, v in placeholders.items():
        body_html = body_html.replace(k, v)
    
    return body_txt, body_html


def build_gmail_compose_link(subject, to_list, body_txt, cc_list=None, bcc_list=None):
    """Construye el link de Gmail compose pre-armado.
    
    Formato:
    https://mail.google.com/mail/?view=cm&fs=1&to=...&su=...&body=...
    """
    base = 'https://mail.google.com/mail/?view=cm&fs=1'
    params = {
        'to': ','.join(to_list),
        'su': subject,
        'body': body_txt,
    }
    if cc_list:
        params['cc'] = ','.join(cc_list)
    if bcc_list:
        params['bcc'] = ','.join(bcc_list)
    
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f'{base}&{query}'


def build_short_gmail_link(subject, to_list, cc_list=None, bcc_list=None):
    """Versión corta del link Gmail compose (sin body).
    
    El body lo pegamos manualmente desde el archivo .txt.
    Ventaja: no hay riesgo de exceder el límite de URL.
    """
    base = 'https://mail.google.com/mail/?view=cm&fs=1'
    params = {
        'to': ','.join(to_list),
        'su': subject,
    }
    if cc_list:
        params['cc'] = ','.join(cc_list)
    if bcc_list:
        params['bcc'] = ','.join(bcc_list)
    
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f'{base}&{query}'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    try:
        week_num = int(sys.argv[1])
    except ValueError:
        print('❌ El número de semana debe ser un entero')
        sys.exit(1)
    
    if not 1 <= week_num <= 53:
        print('❌ Número de semana fuera de rango (1-53)')
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"  📧 CheckRates · Week {week_num} · Generación de email")
    print(f"{'='*70}\n")
    
    # Render del cuerpo
    body_txt, body_html = render_template(week_num)
    subject = SUBJECT_TEMPLATE.format(WEEK_NUM=f'{week_num:02d}')
    
    # Crear carpeta output si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Guardar cuerpo plano
    out_txt = os.path.join(OUTPUT_DIR, f'checkrates_week_{week_num:02d}_mail.txt')
    with open(out_txt, 'w') as f:
        f.write(body_txt)
    print(f"   📄 Cuerpo plano: {out_txt}")
    
    # Guardar cuerpo HTML
    out_html = os.path.join(OUTPUT_DIR, f'checkrates_week_{week_num:02d}_mail.html')
    with open(out_html, 'w') as f:
        f.write(body_html)
    print(f"   📄 Cuerpo HTML:  {out_html}")
    
    # Generar link Gmail compose con body completo
    full_link = build_gmail_compose_link(subject, DESTINATARIOS, body_txt, CC_LIST, BCC_LIST)
    
    # Generar link Gmail compose corto (sin body, por si el largo excede el límite del navegador)
    short_link = build_short_gmail_link(subject, DESTINATARIOS, CC_LIST, BCC_LIST)
    
    # Guardar ambos links
    out_links = os.path.join(OUTPUT_DIR, f'checkrates_week_{week_num:02d}_links.txt')
    with open(out_links, 'w') as f:
        f.write(f"# Gmail Compose links · CheckRates Week {week_num}\n")
        f.write(f"# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## OPCIÓN A · Link completo (asunto + destinatarios + cuerpo)\n")
        f.write(f"# Si el navegador lo abre OK, no hay que hacer nada más\n\n")
        f.write(f"{full_link}\n\n")
        f.write(f"## OPCIÓN B · Link corto (solo asunto + destinatarios)\n")
        f.write(f"# Usar si el link de arriba es muy largo y el navegador lo trunca\n")
        f.write(f"# Después pegar el cuerpo desde checkrates_week_{week_num:02d}_mail.txt\n\n")
        f.write(f"{short_link}\n")
    print(f"   🔗 Links Gmail: {out_links}")
    
    # ============================================================
    # Resumen e instrucciones
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  ✅ Mail listo para enviar")
    print(f"{'='*70}\n")
    
    print(f"   Asunto:        {subject}")
    print(f"   De:            {FROM_EMAIL}")
    print(f"   Destinatarios: {len(DESTINATARIOS)} ({', '.join(d.split('@')[0] for d in DESTINATARIOS[:3])}, ...)")
    print(f"   Link en mail:  {LINK_HUB}")
    
    print(f"\n📋 PASOS A SEGUIR:\n")
    print(f"   1. Asegurate de estar logueado en Gmail con la cuenta:")
    print(f"      → {FROM_EMAIL}\n")
    print(f"   2. Abrí este link en el navegador:")
    print(f"      → cat {out_links}")
    print(f"      Copiá el primer URL (OPCIÓN A) y pegalo en el navegador.\n")
    print(f"   3. Si Gmail abre vacío o falta el cuerpo, usá la OPCIÓN B:")
    print(f"      → Copiá el cuerpo desde {out_txt}")
    print(f"      → Pegalo en el cuerpo del mail de Gmail\n")
    print(f"   4. Revisá destinatarios y asunto, apretá Enviar.\n")
    
    # Tamaño del link
    link_size = len(full_link)
    if link_size > 2000:
        print(f"   ⚠ El link completo tiene {link_size} chars (límite navegadores: ~2000)")
        print(f"     Recomendado usar OPCIÓN B y pegar el cuerpo manual.\n")


if __name__ == '__main__':
    main()
