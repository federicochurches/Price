import re
src = open('render_cr_p1.py', encoding='utf-8').read()
# Insertar print de debug en _build_bk_card_tabs_json
old = "    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')\n    if not _os.path.exists(bk_path):"
new = "    bk_path = _os.getenv('PICKLE_BK', f'bk_w{VOL_NUM}_data.pkl')\n    import sys as _sys; print('DEBUG BK: bk_path=' + str(bk_path) + ' exists=' + str(_os.path.exists(bk_path)), file=_sys.stderr)\n    if not _os.path.exists(bk_path):"
src = src.replace(old, new, 1)
open('render_cr_p1.py', 'w', encoding='utf-8').write(src)
print('Debug agregado')
