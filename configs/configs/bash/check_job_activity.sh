#!/usr/bin/env bash
#
# Usage: ./check_job_activity.sh <JOBID>
# Example: ./check_job_activity.sh 65389
#
# This script:
#   1) Checks if the job is running under the scheduler
#   2) Finds the PID(s) for that job
#   3) Reports CPU and GPU usage
#   4) Checks if the main training log is changing

set -euo pipefail

JOBID="${1:-}"

if [[ -z "$JOBID" ]]; then
  echo "Usage: $0 <JOBID>"
  exit 1
fi

echo "=== Checking job $JOBID ==="

########################################
# 1. Scheduler status
########################################

# Try both squeue (Slurm) and qstat (PBS/UGE) in case your site uses one of them
if command -v squeue >/dev/null 2>&1; then
  JOB_STATE=$(squeue -j "$JOBID" -h -o "%T" 2>/dev/null || true)
  if [[ -z "$JOB_STATE" ]]; then
    echo "Job $JOBID not in squeue (may be finished or failed)."
  else
    echo "Slurm state for job $JOBID: $JOB_STATE"
  fi
elif command -v qstat >/dev/null 2>&1; then
  JOB_STATE=$(qstat -f "$JOBID" 2>/dev/null | awk -F= '/job_state/ {gsub(/ /,"",$2); print $2}')
  if [[ -z "$JOB_STATE" ]]; then
    echo "Job $JOBID not in qstat (may be finished or failed)."
  else
    echo "PBS/UGE state for job $JOBID: $JOB_STATE"
  fi
else
  echo "Warning: Neither squeue nor qstat found; cannot query scheduler state."
fi

########################################
# 2. Find processes belonging to this job
########################################

echo
echo "=== Looking for processes with jobid $JOBID in their environment ==="

# This pattern works on many clusters where JOBID is in the environment.
# Adjust the grep if your site uses PBS_JOBID, SGE_TASK_ID, etc.
PIDS=$(ps -eo pid,user,cmd --no-headers \
  | grep "$JOBID" \
  | grep -v "grep" \
  | awk '{print $1}' \
  | sort -u)

if [[ -z "$PIDS" ]]; then
  echo "No running processes found that obviously belong to job $JOBID."
else
  echo "Found candidate PIDs for job $JOBID: $PIDS"
fi

########################################
# 3. CPU usage snapshot
########################################

if [[ -n "$PIDS" ]]; then
  echo
  echo "=== CPU usage for job processes (snapshot) ==="
  # ps -p ... -o ... will fail if too many PIDs in one go; so loop
  for PID in $PIDS; do
    if ps -p "$PID" > /dev/null 2>&1; then
      ps -p "$PID" -o pid,user,%cpu,%mem,etime,cmd --no-headers
    fi
  done
else
  echo
  echo "No PIDs to inspect for CPU usage."
fi

########################################
# 4. GPU usage snapshot (if NVIDIA GPUs present)
########################################

echo
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "=== GPU usage (nvidia-smi) ==="
  nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader 2>/dev/null \
    | awk -v pids="$PIDS" '
      BEGIN {
        split(pids, a, " ")
        for (i in a) used[a[i]] = 1
      }
      {
        pid=$1
        # csv may include commas; strip trailing commas from pid field
        sub(/,$/,"",pid)
        if (pid in used) print $0
      }'
else
  echo "nvidia-smi not found; skipping GPU check."
fi

########################################
# 5. Check if training log is changing
########################################

echo
echo "=== Log activity check ==="

# Adjust this to match your actual log naming convention.
# From your example: logs/xcep_train_<JOBID>.out and .err
OUT_LOG="logs/xcep_train_${JOBID}.out"
ERR_LOG="logs/xcep_train_${JOBID}.err"

for LOG in "$OUT_LOG" "$ERR_LOG"; do
  if [[ -f "$LOG" ]]; then
    echo "Checking log file: $LOG"
    SIZE1=$(stat -c%s "$LOG" 2>/dev/null || stat -f%z "$LOG" 2>/dev/null || echo 0)
    sleep 5
    SIZE2=$(stat -c%s "$LOG" 2>/dev/null || stat -f%z "$LOG" 2>/dev/null || echo 0)
    echo "  Size t0: $SIZE1 bytes"
    echo "  Size t1: $SIZE2 bytes"
    if [[ "$SIZE2" -gt "$SIZE1" ]]; then
      echo "  -> Log is growing: training is still writing output."
    else
      echo "  -> Log not growing over 5s window (could be idle, blocked, or in a long GPU op)."
    fi

    echo "  Last 5 lines:"
    tail -n 5 "$LOG" | sed 's/^/    /'
  else
    echo "Log file not found: $LOG"
  fi
done

########################################
# 6. Summary heuristic
########################################

echo
echo "=== Summary ==="

ACTIVE_CPU=0
for PID in $PIDS; do
  CPU=$(ps -p "$PID" -o %cpu --no-headers 2>/dev/null | tr -d ' ')
  if [[ -n "$CPU" ]]; then
    CPU_INT=${CPU%.*}
    if [[ "$CPU_INT" -gt 0 ]]; then
      ACTIVE_CPU=1
      break
    fi
  fi
done

LOG_GROWING=0
for LOG in "$OUT_LOG" "$ERR_LOG"; do
  if [[ -f "$LOG" ]]; then
    S1=$(stat -c%s "$LOG" 2>/dev/null || stat -f%z "$LOG" 2>/dev/null || echo 0)
    sleep 1
    S2=$(stat -c%s "$LOG" 2>/dev/null || stat -f%z "$LOG" 2>/dev/null || echo 0)
    if [[ "$S2" -gt "$S1" ]]; then
      LOG_GROWING=1
      break
    fi
  fi
done

if [[ -n "$PIDS" ]] && [[ "$ACTIVE_CPU" -eq 1 || "$LOG_GROWING" -eq 1 ]]; then
  echo "Conclusion: job $JOBID appears to be doing useful work (CPU and/or logs active)."
elif [[ -n "$PIDS" ]]; then
  echo "Conclusion: processes for job $JOBID exist but show no clear activity over this short window."
  echo "  They might be waiting on I/O, in a long GPU kernel, or stuck. Re-run in a few minutes to confirm."
else
  echo "Conclusion: no running processes found for job $JOBID; it has likely finished or failed."
fi
echo "=== End of check for job $JOBID ==="