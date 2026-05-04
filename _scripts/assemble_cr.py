"""Ensambla reporte CR W18 final."""
from pathlib import Path

WK = 'W18'
MES = 'Mayo 2026'
VOL = '18'
N_HOT = '32.086'

p1 = Path('/home/claude/part1_cr.html').read_text(encoding='utf-8')
p2 = Path('/home/claude/part2_cr.html').read_text(encoding='utf-8')
p3 = Path('/home/claude/part3_cr.html').read_text(encoding='utf-8')

def replace_placeholders(s):
    return (s.replace('{{WEEK_NUM}}', WK)
             .replace('{{MES_AÑO}}', MES)
             .replace('{{VOL_NUM}}', VOL))

p1 = replace_placeholders(p1)
p2 = replace_placeholders(p2)
p3 = replace_placeholders(p3)

footer_html = f'''<footer style="margin:60px 0 30px;padding:25px 0;border-top:1px solid var(--ink-soft);display:flex;justify-content:space-between;flex-wrap:wrap;gap:15px;font-family:'Geist',sans-serif;font-size:11px;color:var(--ink-muted);letter-spacing:.02em;">
<span>Supply CheckRates · {WK} · {MES} · Vol. {VOL}</span>
<span>PriceTravel · Supply Optimization · {N_HOT} hoteles analizados</span>
</footer>'''

# Insertar footer antes de </body>
if p3.rstrip().endswith('</html>'):
    idx = p3.rfind('</body>')
    p3_body = p3[:idx]
    p3_close = p3[idx:]
else:
    p3_body = p3
    p3_close = '</body>\n</html>'

final = (
    '<!DOCTYPE html>\n<html lang="es">\n'
    + p1
    + '\n'
    + p2
    + '\n'
    + p3_body
    + '\n'
    + footer_html
    + '\n'
    + p3_close
)

out = Path('/mnt/user-data/outputs/Supply_CheckRates_W18.html')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(final, encoding='utf-8')
print(f'Reporte CR W18 escrito: {len(final):,} chars en {out}')
