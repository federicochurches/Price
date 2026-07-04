#!/usr/bin/env python3
"""
commit_supply_html.py — Sube el SUPPLY_W26.html regenerado (Carimundi + searchbox)
a reports/week-26/SUPPLY_W26.html por Git Tree API (obligatoria para archivos grandes).

USO (desde la raíz del repo C:\\Users\\federico.iglesias\\Price):
  python commit_supply_html.py

Busca el HTML en este orden:
  1) C:\\mnt\\user-data\\outputs\\SUPPLY_W26.html   (donde lo escribe assemble_unified)
  2) %USERPROFILE%\\Desktop\\SUPPLY_W26_VALIDAR.html (la copia que validaste)
  3) reports\\week-26\\SUPPLY_W26.html               (fallback)
O pasás la ruta como argumento:  python commit_supply_html.py "C:\\ruta\\al.html"

Token: env var GITHUB_TOKEN o text3.txt en la carpeta.
"""
import os, sys, json, base64, urllib.request, urllib.error

OWNER     = 'federicochurches'
REPO      = 'Price'
BRANCH    = 'main'
REPO_PATH = 'reports/week-26/SUPPLY_W26.html'   # ruta que sirve Netlify
API       = f'https://api.github.com/repos/{OWNER}/{REPO}'

COMMIT_MSG = ('fix: SUPPLY_W26 · searchbox CORP/Dest/Pais universo completo + '
              'ranking corp con MIN_TRAFICO=2000 (override W26 por baja de trafico)')

def _find_html():
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return sys.argv[1]
    home = os.path.expanduser('~')
    candidates = [
        r'C:\mnt\user-data\outputs\SUPPLY_W26.html',
        os.path.join(home, 'Desktop', 'SUPPLY_W26_VALIDAR.html'),
        os.path.join('reports', 'week-26', 'SUPPLY_W26.html'),
    ]
    found = [p for p in candidates if os.path.exists(p)]
    if not found:
        sys.exit('ERROR: no encontré el HTML. Pasá la ruta como argumento:\n'
                 '  python commit_supply_html.py "C:\\ruta\\al\\SUPPLY_W26.html"')
    if len(found) > 1:
        # elegir el más reciente entre los que existen
        found.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        print('Varios candidatos; uso el más reciente:')
        for p in found:
            import datetime
            print(f'   {p}  ({datetime.datetime.fromtimestamp(os.path.getmtime(p))})')
    return found[0]

def _get_token():
    tok = os.getenv('GITHUB_TOKEN', '').strip()
    if tok:
        return tok
    for p in ('text3.txt', os.path.join('..', 'text3.txt')):
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                return ''.join(f.read().split())
    sys.exit('ERROR: no encontré el token. Exportá GITHUB_TOKEN o dejá text3.txt.')

def _req(method, url, payload=None, token=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        sys.exit(f'ERROR HTTP {e.code} en {method} {url}\n{body}')

def main():
    html_path = _find_html()
    size_mb = os.path.getsize(html_path) / 1024 / 1024
    print(f'HTML a subir: {html_path}  ({size_mb:.2f} MB)')
    print(f'Destino en repo: {REPO_PATH}')
    token = _get_token()

    # 1· HEAD SHA fresco
    ref = _req('GET', f'{API}/git/refs/heads/{BRANCH}', token=token)
    head_sha = ref['object']['sha']
    print(f'[1/6] HEAD: {head_sha[:10]}')

    # 2· base tree
    base_commit = _req('GET', f'{API}/git/commits/{head_sha}', token=token)
    base_tree = base_commit['tree']['sha']
    print(f'[2/6] base tree: {base_tree[:10]}')

    # 3· blob (base64) del HTML
    with open(html_path, 'rb') as f:
        content_b64 = base64.b64encode(f.read()).decode('ascii')
    blob = _req('POST', f'{API}/git/blobs',
                {'content': content_b64, 'encoding': 'base64'}, token=token)
    print(f'[3/6] blob: {blob["sha"][:10]}  ({len(content_b64):,} b64 chars)')

    # 4· tree con base_tree
    tree = _req('POST', f'{API}/git/trees',
                {'base_tree': base_tree,
                 'tree': [{'path': REPO_PATH, 'mode': '100644',
                           'type': 'blob', 'sha': blob['sha']}]}, token=token)
    print(f'[4/6] tree: {tree["sha"][:10]}')

    # 5· commit
    commit = _req('POST', f'{API}/git/commits',
                  {'message': COMMIT_MSG, 'tree': tree['sha'],
                   'parents': [head_sha]}, token=token)
    print(f'[5/6] commit: {commit["sha"][:10]}')

    # 6· PATCH ref
    _req('PATCH', f'{API}/git/refs/heads/{BRANCH}',
         {'sha': commit['sha'], 'force': False}, token=token)
    print(f'[6/6] ref -> {commit["sha"][:10]}')

    print('\n✔ Commit OK.')
    print(f'  https://github.com/{OWNER}/{REPO}/commit/{commit["sha"]}')
    print('\nVERIFICAR EL CONTENIDO REAL (no solo que el commit aparezca):')
    print(f'  $h=(Invoke-WebRequest "https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{REPO_PATH}" -UseBasicParsing).Content')
    print( '  ($h | Select-String "Carimundi" -AllMatches).Matches.Count   # debe dar > 0')
    print( '  ($h | Select-String "RND_CORP_POOL" -AllMatches).Matches.Count # debe dar > 0')
    print('\nNetlify redeploya solo desde main; esperá 1-2 min y verificá en incógnito (cache CDN).')

if __name__ == '__main__':
    main()
