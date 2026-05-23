"""Ensambla reporte RND WNN final — lee semana y hoteles del pickle."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle
from pathlib import Path

# ── Leer semana y métricas del pickle ─────────────────────────────────────
with open(os.getenv('PICKLE_RND', 'rnd_w20_data.pkl'),'rb') as _f:
    _D = pickle.load(_f)

WK  = f'W{_D.get("VOL_NUM", "19")}'
MES = _D.get('MES_AÑO', 'Mayo 2026')
VOL = _D.get('VOL_NUM', '19')
N_HOTELES = f'{len(_D["g_hotel"]):,}'.replace(',', '.')

p1 = Path('./part1_rnd.html').read_text(encoding='utf-8')
p2 = Path('./part2_rnd.html').read_text(encoding='utf-8')
p3 = Path('./part3_rnd.html').read_text(encoding='utf-8')

def replace_placeholders(s):
    return (s.replace('{{WEEK_NUM}}', WK)
             .replace('{{MES_AÑO}}', MES)
             .replace('{{VOL_NUM}}', VOL))

p1 = replace_placeholders(p1)
p2 = replace_placeholders(p2)
p3 = replace_placeholders(p3)

# El footer viene del template (asset_rnd_footer.html)
# No se genera footer adicional aquí

# Nota de metodología sobre P90
NOTA_METODOLOGIA = '''
<div style="background:#F2EDE0;border-left:4px solid #EA0074;padding:16px;margin:32px 0;font-size:12px;color:#333;">
<div style="font-weight:700;font-size:13px;color:#EA0074;margin-bottom:8px;">📊 Metodología</div>
<p style="margin:0;line-height:1.6;">
Este análisis incluye hoteles del <strong>P90</strong> (hoteles que acumulan ~90% del tráfico de disponibilidad), 
para una evaluación más completa de proveedores y corporativos. 
Las métricas reflejan desempeño en el segmento más relevante para Supply Optimization.
</p>
</div>
'''

final = (
    '<!DOCTYPE html>\n<html lang="es">\n'
    + p1 + '\n'
    + NOTA_METODOLOGIA + '\n'
    + p2 + '\n'
    + p3
)

out = Path('/mnt/user-data/outputs') / f'RatesNoDispo_Reporte_Editorial.html'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(final, encoding='utf-8')
print(f'Reporte RND {WK} escrito: {len(final):,} chars en {out}')
