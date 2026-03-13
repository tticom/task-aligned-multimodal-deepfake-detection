#!/bin/bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  update-from-repo.sh [--target fakeav|faceforensics|all] [--with-bash]

Examples:
  ./update-from-repo.sh --target fakeav
  ./update-from-repo.sh --target faceforensics
  ./update-from-repo.sh --target all --with-bash
EOF
}

TARGET="fakeav"
WITH_BASH="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"; shift 2 ;;
    --with-bash)
      WITH_BASH="true"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "ERROR: unknown arg: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ "$TARGET" != "fakeav" && "$TARGET" != "faceforensics" && "$TARGET" != "all" ]]; then
  echo "ERROR: --target must be fakeav, faceforensics, or all" >&2
  exit 2
fi

SRC_ROOT="$HOME/localscratch/fakeav_exception"
DST_ROOT="$HOME/sharedscratch"
DST_FAKEAV="$DST_ROOT/fakeav_xception"
DST_FF="$DST_ROOT/faceforensics"

[[ -d "$SRC_ROOT" ]] || { echo "ERROR: source repo not found: $SRC_ROOT" >&2; exit 1; }
mkdir -p "$DST_FAKEAV" "$DST_FF"

copy_tree_by_name() {
  local src_base="$1"   # e.g. $SRC_ROOT/scripts
  local dst_base="$2"   # e.g. $DST_FAKEAV/scripts
  local name_glob="$3"  # e.g. "*.py" or "*.yaml"

  if [[ ! -d "$src_base" ]]; then
    echo "SKIP: no directory: $src_base"
    return 0
  fi

  while IFS= read -r -d '' f; do
    local rel="${f#"$src_base/"}"
    local dst_dir="$dst_base/$(dirname "$rel")"
    mkdir -p "$dst_dir"
    cp -a "$f" "$dst_dir/"
  done < <(find "$src_base" -type f -name "$name_glob" -print0)

  echo "OK: copied $name_glob from $src_base -> $dst_base (recursive)"
}

copy_glob_flat() {
  local src_dir="$1"
  local pattern="$2"
  local dst_dir="$3"

  mkdir -p "$dst_dir"
  shopt -s nullglob
  local files=( "$src_dir"/$pattern )
  shopt -u nullglob

  if (( ${#files[@]} == 0 )); then
    echo "SKIP: no matches: $src_dir/$pattern"
    return 0
  fi

  cp -a "${files[@]}" "$dst_dir/"
  echo "OK: copied ${#files[@]} file(s) -> $dst_dir/"
}

sync_project() {
  local project="$1"         # "fakeav" | "faceforensics"
  local src_project="$2"     # e.g. $SRC_ROOT or $SRC_ROOT/faceforensics
  local dst_project="$3"     # e.g. $DST_FAKEAV or $DST_FF

  echo "=== Sync: $project ==="
  copy_glob_flat "$src_project/slurm" "*.slurm" "$dst_project/slurm"
  copy_tree_by_name "$src_project/scripts" "$dst_project/scripts" "*.py"
  copy_tree_by_name "$src_project/configs" "$dst_project/configs" "*.yaml"
}

if [[ "$TARGET" == "fakeav" || "$TARGET" == "all" ]]; then
  sync_project "fakeav" "$SRC_ROOT" "$DST_FAKEAV"
fi

if [[ "$TARGET" == "faceforensics" || "$TARGET" == "all" ]]; then
  if [[ -d "$SRC_ROOT/faceforensics" ]]; then
    sync_project "faceforensics" "$SRC_ROOT/faceforensics" "$DST_FF"
  else
    echo "SKIP: no faceforensics directory at $SRC_ROOT/faceforensics"
  fi
fi

if [[ "$WITH_BASH" == "true" ]]; then
  if [[ -d "$SRC_ROOT/configs/bash" ]]; then
    shopt -s nullglob
    bash_scripts=( "$SRC_ROOT/configs/bash/"*.sh )
    shopt -u nullglob
    if (( ${#bash_scripts[@]} > 0 )); then
      for f in "${bash_scripts[@]}"; do
        cp -a "$f" "$DST_ROOT/"
        chmod 0755 "$DST_ROOT/$(basename "$f")"
      done
      echo "OK: copied ${#bash_scripts[@]} bash helper(s) -> $DST_ROOT/ (0755)"
    else
      echo "SKIP: no matches: $SRC_ROOT/configs/bash/*.sh"
    fi
  else
    echo "SKIP: no configs/bash directory at $SRC_ROOT/configs/bash"
  fi
fi

echo "DONE"
