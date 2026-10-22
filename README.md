# NGSPipelineMonitor

A real Linux/Bash monitoring daemon tracking run status and errors
across 6 NGS pipeline stages, with automated Slack alerting, plus a
statistical simulation measuring detection latency across 500 runs.

> Developed a Linux-based Bash monitoring tool tracking run status and
> errors across 6 NGS pipeline stages (fastqc, trim, align, sort,
> variant_call, annotate), with automated Slack alerting on failure.
> Across 500 statistically simulated pipeline runs (61 with injected
> failures), 100% of failures were detected within 10 minutes (mean
> detection latency 3.15 minutes), including realistic webhook-retry
> delays.

## What's real vs. synthetic — read this first

**Real:** `monitor.sh` is a genuine, executable Bash monitoring script
— it polls real per-stage status files, detects non-zero exit codes,
and fires a real `curl`-based Slack webhook POST (logged locally when
no webhook URL is configured). `tests/test_monitor_sh.sh` is a real
bash integration test: it writes real stage status files with an
injected failure, runs the monitor's detection logic directly, and
asserts a real alert line was written — this actually runs and passes
in this environment. `Dockerfile` containerizes the monitor for
deployment alongside a real pipeline.

**Synthetic:** there is no real NGS pipeline or Slack workspace
connected in this environment. The headline "100% caught within 10
minutes, 3.15 min mean latency" statistic comes from
`src/simulate_pipeline_runs.py`, a Python simulation of 500 pipeline
runs (because a single bash integration test can't establish a
percentage across hundreds of runs) — each run has a real chance of a
randomly-timed stage failure, a real poll-interval-bounded detection
delay, and a real simulated webhook-retry delay (8% per-cycle chance
of transient delivery failure, compounding realistically rather than
guaranteeing instant delivery).

## Results (real, from `run_all.py` + the bash integration test)

```
Bash integration test: PASS (correctly detected an injected align-stage failure)

Python statistical simulation (500 runs, 61 failures):
  Mean detection latency: 3.15 min
  Failures caught within 10 min: 100.0%
```

`tests/test_pipeline.py` (5 tests, all passing) checks the 6 stages
are defined, simulated runs produce real failures, median detection
latency stays low, >=90% are caught within 10 minutes, and unfailed
runs correctly report no detection latency.

## Usage

```bash
pip install -r requirements.txt
bash tests/test_monitor_sh.sh    # real bash integration test
python3 run_all.py               # statistical detection-latency simulation
python3 -m pytest tests/test_pipeline.py -v
docker build -t ngs-monitor .    # containerize the real monitor
```

## Project structure

```
monitor.sh                    # real bash pipeline-stage monitor + Slack alerting
Dockerfile                    # containerizes monitor.sh
src/simulate_pipeline_runs.py # 500-run statistical detection-latency simulation
run_all.py
tests/
  test_monitor_sh.sh          # real bash integration test
  test_pipeline.py            # pytest suite for the statistical simulation
```

## Tech stack

Bash, Docker, Linux (real monitor + container), Python/pandas/numpy
(statistical simulation), pytest.

## Limitations

- No real NGS pipeline or Slack workspace is connected; the webhook
  call in `monitor.sh` is real code but untested against a live
  Slack endpoint.
- The 100%/3.15-min headline figures come from the Python statistical
  model, not from running 500 real pipeline executions.
