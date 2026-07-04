#!/usr/bin/env python3
"""
commit_searchbox_fix.py — Commit del fix del searchbox CORP (W26) por Git Tree API.

Sube render_rnd_p1.py + assemble_unified.py al repo federicochurches/Price (main),
en un único tree atómico, siguiendo el patrón canónico del proyecto:
  GET refs/heads/main -> GET commit (base tree) -> POST blobs (base64)
  -> POST tree (base_tree) -> POST commit -> PATCH ref

USO (desde la raíz del repo C:\\Users\\federico.iglesias\\Price):
  python commit_searchbox_fix.py

Requiere el token de GitHub. Por defecto lo lee de text3.txt (el canónico del
proyecto). Si tenés el token en una env var, exportalo como GITHUB_TOKEN.
"""
import os, sys, json, base64, urllib.request, urllib.error

# ── Config ────────────────────────────────────────────────────────────────
OWNER  = 'federicochurches'
REPO   = 'Price'
BRANCH = 'main'
API    = f'https://api.github.com/repos/{OWNER}/{REPO}'

# Archivos a commitear: (ruta_local, ruta_en_repo)
FILES = [
    ('render_rnd_p1.py',   'render_rnd_p1.py'),
    ('assemble_unified.py', 'assemble_unified.py'),
]

COMMIT_MSG = ('fix: searchbox CORP/Destino/Pais trae universo completo (W26) · '
              'pools RND_CORP/DEST/PAIS_POOL sin cap + CAP reservado por dimension '
              'en _kpiSbBuildDD (hotel ya no monopoliza las sugerencias)')

# ── Token ─────────────────────────────────────────────────────────────────
def _get_token():
    tok = os.getenv('GITHUB_TOKEN', '').strip()
    if tok:
        return tok
    # Fallback: text3.txt (canónico del proyecto)
    for p in ('text3.txt', os.path.join('..', 'text3.txt')):
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                # tr -d '[:space:]' — sacar todo whitespace
                return ''.join(f.read().split())
    sys.exit('ERROR: no encontré el token. Exportá GITHUB_TOKEN o dejá text3.txt en la carpeta.')

TOKEN = _get_token()

def _req(method, url, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {TOKEN}')
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
    # Verificar que los archivos locales existen
    for local, _ in FILES:
        if not os.path.exists(local):
            sys.exit(f'ERROR: no encuentro {local} en el directorio actual. '
                     f'Corré el script desde la raíz del repo.')

    print(f'Repo: {OWNER}/{REPO} · branch {BRANCH}')

    # 1· HEAD SHA fresco
    ref = _req('GET', f'{API}/git/refs/heads/{BRANCH}')
    head_sha = ref['object']['sha']
    print(f'[1/6] HEAD actual: {head_sha[:10]}')

    # 2· commit base -> base tree
    base_commit = _req('GET', f'{API}/git/commits/{head_sha}')
    base_tree = base_commit['tree']['sha']
    print(f'[2/6] base tree: {base_tree[:10]}')

    # 3· blobs (base64) por archivo
    tree_items = []
    for local, repo_path in FILES:
        with open(local, 'rb') as f:
            content_b64 = base64.b64encode(f.read()).decode('ascii')
        blob = _req('POST', f'{API}/git/blobs',
                    {'content': content_b64, 'encoding': 'base64'})
        tree_items.append({'path': repo_path, 'mode': '100644',
                           'type': 'blob', 'sha': blob['sha']})
        print(f'[3/6] blob {repo_path}: {blob["sha"][:10]} ({len(content_b64)} b64 chars)')

    # 4· tree con base_tree (atómico, multi-archivo)
    tree = _req('POST', f'{API}/git/trees',
                {'base_tree': base_tree, 'tree': tree_items})
    print(f'[4/6] tree nuevo: {tree["sha"][:10]}')

    # 5· commit
    commit = _req('POST', f'{API}/git/commits',
                  {'message': COMMIT_MSG, 'tree': tree['sha'], 'parents': [head_sha]})
    print(f'[5/6] commit: {commit["sha"][:10]}')

    # 6· PATCH ref
    _req('PATCH', f'{API}/git/refs/heads/{BRANCH}',
         {'sha': commit['sha'], 'force': False})
    print(f'[6/6] ref actualizado -> {commit["sha"][:10]}')

    print('\n✔ Commit OK.')
    print(f'  https://github.com/{OWNER}/{REPO}/commit/{commit["sha"]}')
    print('\nVerificá el contenido real (no solo que el commit aparezca):')
    for _, repo_path in FILES:
        print(f'  curl -sI https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{repo_path}')

if __name__ == '__main__':
    main()
