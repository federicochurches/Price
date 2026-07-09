"""
promote_to_repo.py — Promueve archivos validados de Price_stage/ al repo real Price/

Compara STAGE vs REPO por hash SHA256 y solo copia archivos:
  - NUEVOS en stage (no existen todavía en el repo)
  - MODIFICADOS (hash distinto entre stage y repo)

No borra nada del repo que falte en stage (evita accidentes de sincronización).
Ignora: .git, __pycache__, pickles (*.pkl), datasets crudos sueltos en la raíz
(Dataset_*.xlsx — gitignored, no deben promoverse).

Uso:
    python promote_to_repo.py --stage "C:/Users/federico.iglesias/Price_stage" --repo "C:/Users/federico.iglesias/Price"

Solo ver qué cambiaría, sin copiar nada:
    python promote_to_repo.py --stage ... --repo ... --dry-run
"""
import argparse
import hashlib
import shutil
from pathlib import Path

IGNORE_DIRS = {".git", "__pycache__", ".idea", "node_modules"}
IGNORE_SUFFIXES = {".pkl"}


def sha256(path: Path, chunk: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def should_ignore(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(p in IGNORE_DIRS for p in parts):
        return True
    if rel_path.suffix in IGNORE_SUFFIXES:
        return True
    # Datasets crudos (gitignored) — a cualquier profundidad, no solo en la raíz.
    # Antes solo se chequeaba len(parts)==1, lo que dejó pasar Dataset_*.xlsx
    # copiados dentro de checkrates/week-NN/ y rates-nodispo/week-NN/ (20
    # archivos, 201MB, terminaron commiteados en el repo real — ver W28-security-review).
    if rel_path.name.startswith("Dataset_") and rel_path.suffix == ".xlsx":
        return True
    if rel_path.name.startswith("detalleHoteles_") and rel_path.suffix == ".xlsx":
        return True
    if rel_path.name.lower() == "datahoteles_contratos.xlsx":
        return True
    if rel_path.name.startswith("~$"):
        return True
    return False


def scan(root: Path) -> dict:
    files = {}
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root)
            if should_ignore(rel):
                continue
            files[rel] = p
    return files


def classify(rel_path: Path) -> str:
    """Clasifica un archivo como Inventory o Supply según su ruta relativa."""
    parts = rel_path.parts
    if parts and parts[0] == "inventory":
        return "Inventory"
    return "Supply"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, help="Carpeta de trabajo (Price_stage), sin .git")
    ap.add_argument("--repo", required=True, help="Carpeta del repo git real (Price)")
    ap.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se copiaría, sin copiar")
    args = ap.parse_args()

    stage_root = Path(args.stage)
    repo_root = Path(args.repo)

    if not stage_root.exists():
        print(f"ERROR: no existe la carpeta stage: {stage_root}")
        return
    if not repo_root.exists():
        print(f"ERROR: no existe la carpeta repo: {repo_root}")
        return

    stage_files = scan(stage_root)

    to_copy = []
    for rel, stage_path in stage_files.items():
        repo_path = repo_root / rel
        if not repo_path.exists():
            to_copy.append((rel, "NUEVO"))
        elif sha256(stage_path) != sha256(repo_path):
            to_copy.append((rel, "MODIFICADO"))

    if not to_copy:
        print("Nada para promover — stage y repo están sincronizados.")
        return

    grouped = {"Supply": [], "Inventory": []}
    for rel, status in to_copy:
        grouped[classify(rel)].append((rel, status))

    print(f"\n{len(to_copy)} archivo(s) a promover de STAGE -> REPO:\n")
    for group_name in ("Supply", "Inventory"):
        items = grouped[group_name]
        if not items:
            continue
        print(f"  == {group_name} ({len(items)}) ==")
        for rel, status in sorted(items, key=lambda x: str(x[0])):
            print(f"    [{status:10}] {rel}")
        print()

    if args.dry_run:
        print("(dry-run: no se copio nada)")
        return

    confirm = input(f"Confirmar copia de estos {len(to_copy)} archivo(s) al repo? (s/n): ").strip().lower()
    if confirm != "s":
        print("Cancelado.")
        return

    for rel, _status in to_copy:
        src = stage_root / rel
        dst = repo_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    print(f"\nOK: {len(to_copy)} archivo(s) promovidos. Ahora corre git status / git add en el repo.")


if __name__ == "__main__":
    main()
