#!/usr/bin/env bash
# Real integration test for monitor.sh: writes stage status files
# simulating a pipeline run with one failing stage, runs monitor_once
# directly (sourced, not the infinite daemon), and asserts a real
# alert was written to the alert log.
set -euo pipefail

TEST_DIR=$(mktemp -d)
export STATUS_DIR="${TEST_DIR}/run_status"
export ALERT_LOG="${STATUS_DIR}/alerts.log"
mkdir -p "${STATUS_DIR}"

echo 0 > "${STATUS_DIR}/fastqc.status"
echo 0 > "${STATUS_DIR}/trim.status"
echo 1 > "${STATUS_DIR}/align.status"   # real injected failure

source "$(dirname "$0")/../monitor.sh"
monitor_once

if grep -q "FAILURE detected in stage 'align'" "${ALERT_LOG}"; then
  echo "PASS: monitor.sh correctly detected the align-stage failure"
  rm -rf "${TEST_DIR}"
  exit 0
else
  echo "FAIL: no alert found in ${ALERT_LOG}"
  cat "${ALERT_LOG}" 2>&1 || true
  rm -rf "${TEST_DIR}"
  exit 1
fi
