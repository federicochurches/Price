"""Ensambla reporte CR WNN final — lee semana y hoteles del pickle."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── Leer semana y métricas del pickle ─────────────────────────────────────
with open(os.getenv('PICKLE_CR', 'cr_w20_data.pkl'),'rb') as _f:
    _D = pickle.load(_f)

WK  = f'W{_D.get("VOL_NUM", "19")}'
MES = _D.get('MES_AÑO', 'Mayo 2026')
VOL = _D.get('VOL_NUM', '19')
N_HOTELES = f'{len(_D["g_hotel"]):,}'.replace(',', '.')

p1 = Path('./part1_cr.html').read_text(encoding='utf-8')
p2 = Path('./part2_cr.html').read_text(encoding='utf-8')
p3 = Path('./part3_cr.html').read_text(encoding='utf-8')

# ── Resolver {{SHARED_HEAD}} — inyectar CSS/JS compartido ─────────────────
shared_head_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'asset_shared_head.html'
if shared_head_path.exists() and '{{SHARED_HEAD}}' in p1:
    shared_head = shared_head_path.read_text(encoding='utf-8')
    p1 = p1.replace('{{SHARED_HEAD}}', shared_head)

def replace_placeholders(s):
    return (s.replace('{{WEEK_NUM}}', WK)
             .replace('{{MES_AÑO}}', MES)
             .replace('{{VOL_NUM}}', VOL))

p1 = replace_placeholders(p1)
p2 = replace_placeholders(p2)
p3 = replace_placeholders(p3)

final = (
    '<!DOCTYPE html>\n<html lang="es">\n'
    + p1 + '\n'
    + p2 + '\n'
    + p3
)

out = Path('/mnt/user-data/outputs') / f'CheckRates_Reporte_Editorial.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(final, encoding='utf-8')
print(f'Reporte CR {WK} escrito: {len(final):,} chars en {out}')
