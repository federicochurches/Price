#!/usr/bin/env python3
"""
check_html.py — auditoría del SUPPLY_WNN.html generado.

Cuatro chequeos, pensados para cazar las clases de problema que se acumularon
en el pipeline (duplicación de data, código/handlers huérfanos, drift de tamaño):

  1. COMPOSICIÓN  — peso de cada `var NAME = {...}` / `[...]` top-level, ordenado.
  2. DUPLICADOS   — blobs (arrays/objetos) byte-idénticos emitidos más de una vez
                    (esto cazaría CR_HOTELS y los _sb 4×). Reporta bytes redundantes.
  3. PRESUPUESTO  — tamaño total + delta vs el build anterior (baseline en disco).
  4. HUÉRFANOS    — IDs que el JS hace getElementById('X') pero no existen como
                    id="X" en el DOM · handlers onclick="fn(" sin `function fn`.

Uso:  python check_html.py [ruta_html]   (default: reports/week-24/SUPPLY_W24.html)
      --update-baseline   guarda el tamaño actual como nuevo baseline
Pensado para engancharse al final de assemble_unified.py (o correr suelto).
"""
import sys, os, re, json, hashlib

DUP_MIN_BYTES   = 4096     # umbral para reportar un blob como duplicado
COMP_MIN_BYTES  = 4096     # umbral para listar un var en composición
BASELINE_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.html_budget.json')


# ── helper: balance-match de {} / [] con conciencia de strings ────────────────
def _match_span(s, start):
    """start apunta al '{' o '['. Devuelve idx del cierre balanceado."""
    depth = 0; i = start; instr = False; esc = False; q = ''
    while i < len(s):
        c = s[i]
        if instr:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: instr = False
        else:
            if c in '"\'': instr = True; q = c
            elif c in '{[': depth += 1
            elif c in '}]':
                depth -= 1
                if depth == 0: return i
        i += 1
    return -1


def find_top_vars(html):
    """Encuentra `var NAME = {` / `var NAME = [` y devuelve [(name, raw_str), ...]."""
    out = []
    for m in re.finditer(r'\bvar\s+([A-Za-z_$][\w$]*)\s*=\s*([{\[])', html):
        name = m.group(1)
        start = m.end() - 1
        end = _match_span(html, start)
        if end > start:
            out.append((name, html[start:end + 1]))
    return out


# ── 1 + 2: composición y duplicados ───────────────────────────────────────────
def _walk_blobs(obj, path, acc, depth, maxdepth):
    """Recolecta (path, md5, bytes) de arrays/objetos grandes hasta maxdepth."""
    try:
        ser = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        return
    b = len(ser.encode('utf-8'))
    if isinstance(obj, (list, dict)) and b >= DUP_MIN_BYTES:
        acc.append((path, hashlib.md5(ser.encode('utf-8')).hexdigest(), b))
    if depth >= maxdepth:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_blobs(v, f'{path}.{k}', acc, depth + 1, maxdepth)
    elif isinstance(obj, list) and len(obj) <= 8:   # no explotar listas largas
        for idx, v in enumerate(obj):
            _walk_blobs(v, f'{path}[{idx}]', acc, depth + 1, maxdepth)


def analyze(html):
    vars_ = find_top_vars(html)
    # dedup por nombre: quedarse con la aparición más grande (los vars de data son únicos)
    by_name = {}
    for name, raw in vars_:
        if len(raw) > len(by_name.get(name, '')):
            by_name[name] = raw

    comp = []          # (name, bytes, parseable)
    blobs = []         # (path, md5, bytes)
    for name, raw in by_name.items():
        nbytes = len(raw.encode('utf-8'))
        parsed = None
        try:
            parsed = json.loads(raw)
        except Exception:
            pass
        comp.append((name, nbytes, parsed is not None))
        if parsed is not None:
            _walk_blobs(parsed, name, blobs, 0, 2)
    comp.sort(key=lambda x: -x[1])

    # agrupar blobs por md5 → duplicados
    groups = {}
    for path, h, b in blobs:
        groups.setdefault(h, []).append((path, b))
    dups = []
    for h, items in groups.items():
        if len(items) >= 2:
            bytes_each = items[0][1]
            redundant = bytes_each * (len(items) - 1)
            dups.append((redundant, bytes_each, len(items), [p for p, _ in items]))
    dups.sort(key=lambda x: -x[0])
    return comp, dups


# ── 4: huérfanos ──────────────────────────────────────────────────────────────
def orphans(html):
    # IDs literales que el JS busca
    ref_ids = set(re.findall(r'getElementById\(\s*[\'"]([^\'"]+)[\'"]\s*\)', html))
    present_ids = set(re.findall(r'\bid\s*=\s*[\'"]([^\'"]+)[\'"]', html))
    missing_ids = sorted(i for i in ref_ids if i not in present_ids)

    # handlers onclick="fn(" cuya función no está definida
    onclick_fns = set(re.findall(r'onclick\s*=\s*[\'"]\s*([A-Za-z_$][\w$]*)\s*\(', html))
    defined = set(re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(', html))
    defined |= set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*=\s*function\b', html))
    defined |= set(re.findall(r'\bvar\s+([A-Za-z_$][\w$]*)\s*=', html))
    undefined_handlers = sorted(f for f in onclick_fns if f not in defined)
    return missing_ids, undefined_handlers, len(ref_ids), len(onclick_fns)


# ── presupuesto ───────────────────────────────────────────────────────────────
def budget(total, comp, update):
    base = None
    if os.path.exists(BASELINE_PATH):
        try: base = json.load(open(BASELINE_PATH))
        except Exception: base = None
    delta_total = (total - base['total']) if base else None
    if update or base is None:
        json.dump({'total': total, 'vars': {n: b for n, b, _ in comp}},
                  open(BASELINE_PATH, 'w'), indent=2)
    return base, delta_total


def fmt(b):
    return f'{b/1024/1024:.2f}MB' if b >= 1024*1024 else f'{b/1024:.0f}KB'


def report(path, update=False):
    """Imprime el reporte de auditoría sobre el HTML en `path`. No lanza —
    pensado para engancharse al final del pipeline sin romper el build."""
    if not os.path.exists(path):
        print(f'[check_html] ✗ no existe: {path}'); return
    html = open(path, encoding='utf-8').read()
    total = len(html.encode('utf-8'))
    comp, dups = analyze(html)
    base, delta_total = budget(total, comp, update)
    missing_ids, undef_handlers, n_ref, n_onclick = orphans(html)

    print(f'\n═══ check_html · {os.path.basename(path)} ═══')

    # 3. presupuesto
    line = f'\n[PRESUPUESTO] total: {fmt(total)} ({total:,} bytes)'
    if delta_total is not None:
        sign = '+' if delta_total >= 0 else '−'
        line += f'  ·  Δ vs baseline: {sign}{fmt(abs(delta_total))}'
    else:
        line += '  ·  (baseline creado)'
    print(line)

    # 1. composición
    print(f'\n[COMPOSICIÓN] vars top-level ≥ {COMP_MIN_BYTES//1024}KB:')
    for name, b, ok in comp:
        if b < COMP_MIN_BYTES: continue
        pct = 100*b/total
        flag = '' if ok else '  (no-JSON, sin chequeo de dups)'
        print(f'   {fmt(b):>9}  {pct:4.1f}%  {name}{flag}')

    # 2. duplicados
    print('\n[DUPLICADOS] blobs byte-idénticos emitidos ≥2 veces:')
    if not dups:
        print('   ✓ ninguno')
    else:
        total_red = sum(d[0] for d in dups)
        for redundant, each, count, paths in dups[:20]:
            print(f'   {fmt(redundant):>9} redundantes · {count}× {fmt(each)} c/u')
            for p in paths[:6]:
                print(f'              {p}')
            if len(paths) > 6:
                print(f'              … (+{len(paths)-6} más)')
        print(f'   → recuperable deduplicando: ~{fmt(total_red)}')

    # 4. huérfanos
    print(f'\n[HUÉRFANOS] (candidatos a revisar — los IDs dinámicos no se chequean)')
    print(f'   getElementById literales: {n_ref} · onclick handlers: {n_onclick}')
    if missing_ids:
        print(f'   IDs buscados por JS y AUSENTES en el DOM ({len(missing_ids)}):')
        for i in missing_ids[:25]:
            print(f'      · {i}')
        if len(missing_ids) > 25: print(f'      … (+{len(missing_ids)-25} más)')
    else:
        print('   ✓ ningún getElementById literal sin elemento')
    if undef_handlers:
        print(f'   onclick → función NO definida ({len(undef_handlers)}):')
        for f in undef_handlers[:25]:
            print(f'      · {f}')
    else:
        print('   ✓ ningún onclick sin función definida')
    print()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    update = '--update-baseline' in sys.argv
    path = args[0] if args else 'reports/week-24/SUPPLY_W24.html'
    report(path, update=update)


if __name__ == '__main__':
    main()
