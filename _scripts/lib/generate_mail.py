"""Genera Mail unificado CR + RND."""
from pathlib import Path

def generate_mail(week: int, periodo: str, cr_kpis: dict, rnd_kpis: dict, output_path: Path,
                  template_path: Path = None):
    """Genera Mail_WNN.html unificado · usa template con placeholders."""
    if template_path is None:
        template_path = Path(__file__).resolve().parent.parent / 'templates' / 'mail_template.html'
    
    template = template_path.read_text(encoding='utf-8')
    
    # CR: corp top
    cr_top = cr_kpis.get('top_corp')
    cr_top_corps = ', '.join(cr_top['Corporate'].head(3).tolist()) if cr_top is not None and len(cr_top) > 0 else 'N/A'
    
    # RND: corp top
    rnd_top = rnd_kpis.get('top_corp')
    has_corp = rnd_kpis['kpis'].get('has_corp', False)
    if has_corp and rnd_top is not None and len(rnd_top) > 0:
        rnd_top_corps = ', '.join(rnd_top['CorpName'].head(3).tolist())
    else:
        rnd_top_dest = rnd_kpis.get('top_dest')
        if rnd_top_dest is not None and len(rnd_top_dest) > 0:
            rnd_top_corps = ', '.join(rnd_top_dest['Destino'].head(3).tolist()) + ' (Top destinos)'
        else:
            rnd_top_corps = 'N/A'
    
    replacements = {
        '{{WEEK}}': str(week),
        '{{WEEK_PADDED}}': f'{week:02d}',
        '{{PERIODO}}': periodo,
        # CR
        '{{CR_TOTAL_HOT}}': f"{cr_kpis['kpis']['total_hot']:,}".replace(',', '.'),
        '{{CR_P80}}': f"{cr_kpis['kpis']['p80_count']:,}".replace(',', '.'),
        '{{CR_EFICACIA}}': f"{cr_kpis['kpis']['eficacia']:.2f}%",
        '{{CR_CR}}': f"{cr_kpis['kpis']['cr']:.2f}%",
        '{{CR_TOTAL_CK}}': f"{cr_kpis['kpis']['total_ck']/1e6:.2f}M",
        '{{CR_TOTAL_BKGS}}': f"{cr_kpis['kpis']['total_bkgs']:,}".replace(',', '.'),
        '{{CR_ZERO_BKGS}}': f"{cr_kpis['kpis']['zero_bkgs']:,}".replace(',', '.'),
        '{{CR_ZERO_PCT}}': f"{cr_kpis['kpis']['zero_bkgs_pct']:.1f}%",
        '{{CR_TOP_CORPS}}': cr_top_corps,
        '{{CR_SEV_SUPER}}': str(cr_kpis['severity_eficacia']['super'] + cr_kpis['severity_cr']['super']),
        '{{CR_SEV_CRITICA}}': str(cr_kpis['severity_eficacia']['critica'] + cr_kpis['severity_cr']['critica']),
        # RND
        '{{RND_TOTAL_HOT}}': f"{rnd_kpis['kpis']['total_hot']:,}".replace(',', '.'),
        '{{RND_P80}}': f"{rnd_kpis['kpis']['p80_count']:,}".replace(',', '.'),
        '{{RND_NODISPO}}': f"{rnd_kpis['kpis']['nodispo_pond']:.2f}%",
        '{{RND_TRAFICO}}': f"{rnd_kpis['kpis']['total_traf']/1e6:.1f}M",
        '{{RND_BKGS}}': f"{rnd_kpis['kpis']['total_bkgs']:,}".replace(',', '.'),
        '{{RND_GB}}': f"${rnd_kpis['kpis']['total_gb']/1e6:.2f}M",
        '{{RND_ZERO_BKGS}}': f"{rnd_kpis['kpis']['zero_bkgs']:,}".replace(',', '.'),
        '{{RND_ZERO_PCT}}': f"{rnd_kpis['kpis']['zero_bkgs_pct']:.1f}%",
        '{{RND_TOP_CORPS}}': rnd_top_corps,
        '{{RND_SEV_SUPER}}': str(rnd_kpis['severity']['super']),
        '{{RND_SEV_CRITICA}}': str(rnd_kpis['severity']['critica']),
    }
    
    html = template
    for key, val in replacements.items():
        html = html.replace(key, val)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    return output_path
