#!/bin/bash
set -euo pipefail

# Usage examples:
#   bash scripts/run_fakeav_audio_pipeline.sh
#   bash scripts/run_fakeav_audio_pipeline.sh --shards 100
#   bash scripts/run_fakeav_audio_pipeline.sh --shards 100 --max-parallel 20

SHARDS=100
MAX_PARALLEL=""   # e.g. 20 -> --array=0-99%20

usage() {
  cat >&2 <<'EOF'
Usage:
  run_fakeav_audio_pipeline.sh [--shards N] [--max-parallel N]

Options:
  --shards N         Number of array shards (default: 100)
  --max-parallel N   Max concurrent tasks (adds %N to --array)
EOF
}

need_value() {
  local opt="$1"
  if [[ $# -lt 2 ]] || [[ -z "${2:-}" ]] || [[ "${2:-}" == --* ]]; then
    echo "ERROR: $opt requires a value" >&2
    usage
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --shards)
      need_value "$1" "${2:-}"
      SHARDS="$2"
      shift 2
      ;;
    --max-parallel)
      need_value "$1" "${2:-}"
      MAX_PARALLEL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if ! [[ "$SHARDS" =~ ^[0-9]+$ ]] || (( SHARDS <= 0 )); then
  echo "ERROR: --shards must be a positive integer" >&2
  exit 2
fi

if [[ -n "$MAX_PARALLEL" ]]; then
  if ! [[ "$MAX_PARALLEL" =~ ^[0-9]+$ ]] || (( MAX_PARALLEL <= 0 )); then
    echo "ERROR: --max-parallel must be a positive integer" >&2
    exit 2
  fi
fi

ARRAY_MAX=$((SHARDS - 1))
ARRAY_SPEC="0-${ARRAY_MAX}"
if [[ -n "$MAX_PARALLEL" ]]; then
  ARRAY_SPEC="${ARRAY_SPEC}%${MAX_PARALLEL}"
fi

echo "Submitting manifest + leak audit..."
jid1=$(sbatch --parsable slurm/fakeav_prepare_audio_manifest.slurm)
echo "jid1=$jid1"

echo "Submitting audio array: --array=${ARRAY_SPEC}"
jid2=$(sbatch --parsable --dependency=afterok:"$jid1" --array="$ARRAY_SPEC" slurm/fakeav_prepare_audio_array.slurm)
echo "jid2=$jid2"

echo "Submitting outputs audit..."
jid3=$(sbatch --parsable --dependency=afterok:"$jid2" slurm/fakeav_prepare_audio_audit_outputs.slurm)
echo "jid3=$jid3"

echo "Pipeline submitted:"
echo "  manifest/leak audit: $jid1"
echo "  audio array:         $jid2"
echo "  outputs audit:       $jid3"
