"""
template_seguimiento.py · Bloque de seguimiento del Plan de Acción
Lee plan_seguimiento_W(N-1).md y renderiza los items OPEN como carryover.
"""
import os, re

def render_seguimiento_block(seguimiento_file, accent_color='#EA0074'):
    """
    Lee el archivo de seguimiento y renderiza items OPEN como carryover.
    Si no existe el archivo, retorna string vacío.
    """
    if not os.path.exists(seguimiento_file):
        return ''

    with open(seguimiento_file, encoding='utf-8') as f:
        content = f.read()

    open_match = re.search(r'## OPEN\n(.*?)(?=## CERRADO|## NOTAS|## PENDIENTE|$)', content, re.DOTALL)
    if not open_match:
        return ''

    items = [l.strip() for l in open_match.group(1).split('\n')
             if l.strip().startswith('-') and not l.strip().startswith('#')]
    if not items:
        return ''

    def parse_item(line):
        cluster_m = re.search(r'\[(QW|MP|ES)\]', line)
        report_m  = re.search(r'\[(CR|RND|AMBOS)\]', line)
        cluster = cluster_m.group(1) if cluster_m else 'MP'
        report  = report_m.group(1)  if report_m  else 'AMBOS'
        text = re.sub(r'\[.*?\]', '', line).lstrip('- ').strip()
        week_m = re.search(r'abierto (W\d+)', text)
        week_open = week_m.group(1) if week_m else ''
        text_clean = re.sub(r' — abierto W\d+', '', text).strip()
        return cluster, report, text_clean, week_open

    cluster_cfg = {
        'QW': {'bg':'#E0F0E2','color':'#2F6C34','label':'Quick Win'},
        'MP': {'bg':'#FFF4E0','color':'#A86A1D','label':'Mid Priority'},
        'ES': {'bg':'#EDE8F7','color':'#5C469C','label':'Estratégica'},
    }
    report_cfg = {
        'CR':    {'bg':'#EDE8F7','color':'#5C469C'},
        'RND':   {'bg':'#FCE4F1','color':'#EA0074'},
        'AMBOS': {'bg':'#F2EEE6','color':'#8A8377'},
    }

    rows_html = ''
    for item in items:
        cluster, report, text, week_open = parse_item(item)
        cc = cluster_cfg.get(cluster, cluster_cfg['MP'])
        rc = report_cfg.get(report, report_cfg['AMBOS'])

        # Badge "desde WNN"
        carry_badge = (
            f'<span style="display:inline-block;font-size:9px;font-weight:700;'
            f'letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;'
            f'border-radius:2px;background:#F2EDE0;color:#8A8377;margin-left:6px;">'
            f'desde {week_open}</span>'
        ) if week_open else ''

        rows_html += f'''
<div class="action-row {cluster.lower()}" style="border-left-color:#C9C1B0 !important;opacity:0.85;">
  <div style="display:flex;flex-direction:column;gap:4px;">
    <div class="action-owner-badge" style="background:#F2EDE0;color:#8A8377;border:1px solid var(--rule);">CARRYOVER</div>
    <span style="font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
    padding:2px 6px;border-radius:2px;background:{cc["bg"]};color:{cc["color"]};text-align:center;">{cc["label"]}</span>
    <span style="font-size:9px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
    padding:2px 6px;border-radius:2px;background:{rc["bg"]};color:{rc["color"]};text-align:center;">{report}</span>
  </div>
  <div class="accion" style="color:var(--ink-soft);">{text}{carry_badge}</div>
</div>'''

    n = len(items)
    sep = f'''<div style="display:flex;align-items:center;gap:12px;margin:32px 0 16px;">
  <div style="flex:1;height:1px;background:var(--rule);"></div>
  <span style="font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-muted);white-space:nowrap;">📋 Carryover · {n} item{"s" if n!=1 else ""} pendiente{"s" if n!=1 else ""} de semanas anteriores</span>
  <div style="flex:1;height:1px;background:var(--rule);"></div>
</div>'''

    return sep + f'<div class="action-grid">{rows_html}</div>'


def generar_archivo_seguimiento(plan_items, week_label, output_path):
    """
    Genera plan_seguimiento_WNN.md.
    ES y MP → ## OPEN (persisten automáticamente)
    QW → ## PENDIENTE_QW (revisión manual)
    """
    es_mp = [i for i in plan_items if i["cluster"] in ("ES", "MP")]
    qw    = [i for i in plan_items if i["cluster"] == "QW"]

    def fmt(items):
        return "\n".join(
            f'- [{i["cluster"]}] [{i["report"]}] {i["text"]} — abierto {week_label}'
            for i in items
        ) or "# (vacío)"

    content = f"""# Plan de Seguimiento · {week_label}
# ─────────────────────────────────────────────────────────────────────────────
# INSTRUCCIONES:
#   · ## OPEN      → aparece como CARRYOVER en el reporte de la próxima semana
#   · ## CERRADO   → se ignora
#   · ES y MP persisten automáticamente · QW requieren revisión manual
# ─────────────────────────────────────────────────────────────────────────────

## OPEN
# ES (Estratégicas) y MP (Mid Priority) — persisten automáticamente
{fmt(es_mp)}

## PENDIENTE_QW
# Quick Wins — mover a OPEN si siguen abiertos, o a CERRADO si se resolvieron
{fmt(qw)}

## CERRADO
# (items resueltos)

## NOTAS
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path
