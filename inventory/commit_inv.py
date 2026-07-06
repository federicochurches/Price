import base64, json, urllib.request, glob, os

TOKEN_PATH = '../text3.txt'
REPO = 'federicochurches/Price'

html_files = glob.glob('week-*/INVENTORY_W*.html')
if not html_files:
    print("No se encontro INVENTORY_W*.html")
    exit(1)

html_files.sort(reverse=True)
html_path = html_files[0]
week_folder = html_path.split(os.sep)[0]
week_num = week_folder.replace('week-', '')
week_tag = 'W' + week_num

json_hbw   = week_folder + '/hotel_by_week_' + week_tag + '.json'
json_hist  = week_folder + '/hist_dim_' + week_tag + '.json'
json_cdest = week_folder + '/corp_dest_' + week_tag + '.json'

print('Semana: ' + week_tag)
print('HTML:   ' + html_path)

TOKEN = open(TOKEN_PATH).read().strip()
H = {'Authorization': 'token ' + TOKEN, 'Content-Type': 'application/json'}

def get(url):
    req = urllib.request.Request(url, headers={'Authorization': 'token ' + TOKEN})
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=H)
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

def patch(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=H, method='PATCH')
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

def blob(path):
    if not os.path.exists(path):
        print('  (no existe) ' + path)
        return None
    mb = round(os.path.getsize(path)/1024/1024, 2)
    print('Subiendo ' + path + ' (' + str(mb) + ' MB)...')
    with open(path, 'rb') as f: c = base64.b64encode(f.read()).decode()
    return post('https://api.github.com/repos/' + REPO + '/git/blobs', {'content': c, 'encoding': 'base64'})['sha']

base = 'https://api.github.com/repos/' + REPO
head = get(base + '/git/ref/heads/main')['object']['sha']
tree_sha = get(base + '/git/commits/' + head)['tree']['sha']

tree_items = []

html_sha = blob(html_path)
if html_sha:
    tree_items.append({'path': 'inventory/' + week_folder + '/INVENTORY_' + week_tag + '.html', 'mode': '100644', 'type': 'blob', 'sha': html_sha})

for jpath, jname in [(json_hbw, 'hotel_by_week_'), (json_hist, 'hist_dim_'), (json_cdest, 'corp_dest_')]:
    sha = blob(jpath)
    if sha:
        tree_items.append({'path': 'inventory/' + week_folder + '/' + jname + week_tag + '.json', 'mode': '100644', 'type': 'blob', 'sha': sha})

if not tree_items:
    print('Nada que commitear')
    exit(1)

new_tree = post(base + '/git/trees', {'base_tree': tree_sha, 'tree': tree_items})['sha']
msg = 'feat(inventory): INVENTORY_' + week_tag + ' actualizado'
new_commit = post(base + '/git/commits', {'message': msg, 'tree': new_tree, 'parents': [head]})['sha']
result = patch(base + '/git/refs/heads/main', {'sha': new_commit})
print('Commiteado: ' + result['object']['sha'])
print('URL: https://analytics-desk.netlify.app/inventory/' + week_folder + '/inventory_' + week_tag.lower())
