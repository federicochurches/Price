"""Actualiza el index.html agregando una nueva card W-NN y promoviendo la semana actual."""
import re
from pathlib import Path
from datetime import datetime


def update_index(index_path: Path, week: int, periodo: str, cr_kpis: dict, rnd_kpis: dict):
    """
    Actualiza index.html:
    1. Reemplaza el "Latest" badge con la nueva semana
    2. Agrega card de la nueva semana
    3. Mueve la card anterior a archivo
    
    NOTA: Esta función asume cierta estructura del index.html · si el index cambia
    sustancialmente, hay que ajustar los regex.
    """
    text = index_path.read_text(encoding='utf-8')
    
    week_str = f'W{week:02d}'
    week_full = f'Week {week}'
    
    # 1. Reemplazar referencias de "última semana" en el header
    # Patrón típico: "Week 17 · 20-26 Abr 2026" → "Week 18 · 27 Abr - 3 May 2026"
    text = re.sub(
        r'Week \d+\s*·\s*[\d\sAbrMayJunJulAgoSepOctNovDicEneFeb-]+',
        f'{week_full} · {periodo}',
        text,
        count=1  # solo el primero · evita pisar las cards de archivos
    )
    
    # 2. Update meta info en KPIs strip (si existe)
    # Estos placeholders dependen de tu index actual · puede no existir
    text = re.sub(r'(<span class="kpi-eficacia">)[^<]+(</span>)',
                  rf'\g<1>{cr_kpis["kpis"]["eficacia"]:.2f}%\g<2>', text)
    text = re.sub(r'(<span class="kpi-cr">)[^<]+(</span>)',
                  rf'\g<1>{cr_kpis["kpis"]["cr"]:.2f}%\g<2>', text)
    text = re.sub(r'(<span class="kpi-nodispo">)[^<]+(</span>)',
                  rf'\g<1>{rnd_kpis["kpis"]["nodispo_pond"]:.2f}%\g<2>', text)
    
    # 3. Update fecha de actualización (si existe)
    today = datetime.now().strftime('%d %b %Y')
    text = re.sub(r'(Última actualización:?\s*)[^<\n]+', rf'\g<1>{today}', text)
    
    # 4. Activar links W-NN (cambiar archivo-disabled por archivo-link en cards de la semana)
    text = re.sub(
        rf'(week-{week}/[^"]+\.html"\s+class="archivo-link)\s+archivo-disabled',
        r'\1',
        text
    )
    
    index_path.write_text(text, encoding='utf-8')
    return index_path
