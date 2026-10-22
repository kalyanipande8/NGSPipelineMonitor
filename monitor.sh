#!/usr/bin/env bash
# Real Linux pipeline monitor: polls per-stage status files for a
# 6-stage NGS pipeline (fastqc, trim, align, sort, variant_call,
# annotate) and fires a Slack alert the first time any stage's status
# file reports a non-zero exit code. Designed to run as a background
# daemon (e.g. inside the Docker container built from Dockerfile)
# alongside the actual pipeline.
set -euo pipefail

STAGES=(fastqc trim align sort variant_call annotate)
STATUS_DIR="${STATUS_DIR:-./run_status}"
POLL_INTERVAL_SEC="${POLL_INTERVAL_SEC:-5}"
ALERTED_FILE="${STATUS_DIR}/.alerted"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
ALERT_LOG="${ALERT_LOG:-${STATUS_DIR}/alerts.log}"

send_alert() {
  local stage="$1"
  local message="NGS pipeline FAILURE detected in stage '${stage}' at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "${message}" >> "${ALERT_LOG}"
  if [[ -n "${SLACK_WEBHOOK_URL}" ]]; then
    curl -s -X POST -H 'Content-type: application/json' \
      --data "{\"text\": \"${message}\"}" "${SLACK_WEBHOOK_URL}" > /dev/null || true
  fi
}

monitor_once() {
  for stage in "${STAGES[@]}"; do
    status_file="${STATUS_DIR}/${stage}.status"
    if [[ -f "${status_file}" ]]; then
      exit_code=$(cat "${status_file}")
      alert_marker="${ALERTED_FILE}.${stage}"
      if [[ "${exit_code}" != "0" && ! -f "${alert_marker}" ]]; then
        send_alert "${stage}"
        touch "${alert_marker}"
      fi
    fi
  done
}

main() {
  mkdir -p "${STATUS_DIR}"
  : > "${ALERT_LOG}"
  echo "NGSPipelineMonitor watching ${STATUS_DIR} every ${POLL_INTERVAL_SEC}s"
  while true; do
    monitor_once
    sleep "${POLL_INTERVAL_SEC}"
  done
}

# Allow sourcing this script for tests without starting the infinite loop.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main
fi
