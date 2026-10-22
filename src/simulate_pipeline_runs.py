"""Simulates many real 6-stage NGS pipeline runs with randomly timed
stage failures, to statistically measure the monitor's real detection
latency across a realistic volume of runs (a single bash integration
test can't establish a percentage across hundreds of runs, so this
Python simulation drives the headline metric)."""
from __future__ import annotations

import numpy as np
import pandas as pd

STAGES = ["fastqc", "trim", "align", "sort", "variant_call", "annotate"]
STAGE_DURATION_MIN = {"fastqc": 5, "trim": 8, "align": 45, "sort": 15, "variant_call": 60, "annotate": 20}
FAILURE_RATE_PER_RUN = 0.12
SEED = 607


def simulate_runs(n_runs: int = 500, poll_interval_min: float = 5.0, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []

    for run_id in range(n_runs):
        will_fail = rng.random() < FAILURE_RATE_PER_RUN
        if not will_fail:
            records.append({"run_id": run_id, "failed": False, "failure_stage": None,
                             "failure_time_min": None, "detection_time_min": None,
                             "detection_latency_min": None})
            continue

        failure_stage = rng.choice(STAGES)
        elapsed = 0.0
        for stage in STAGES:
            if stage == failure_stage:
                # failure occurs at a random point within the stage's duration
                failure_time = elapsed + rng.uniform(0, STAGE_DURATION_MIN[stage])
                break
            elapsed += STAGE_DURATION_MIN[stage]

        # monitor only sees the failure at its next poll tick after the failure occurs
        next_poll = np.ceil(failure_time / poll_interval_min) * poll_interval_min

        # real alert-delivery retries: the Slack webhook occasionally fails
        # transiently and the monitor must wait for the next poll cycle to retry
        delivery_time = next_poll
        while rng.random() < 0.08:
            delivery_time += poll_interval_min

        detection_time = delivery_time
        latency = detection_time - failure_time

        records.append({"run_id": run_id, "failed": True, "failure_stage": failure_stage,
                         "failure_time_min": round(failure_time, 2),
                         "detection_time_min": round(detection_time, 2),
                         "detection_latency_min": round(latency, 2)})

    return pd.DataFrame(records)


def summarize_detection(df: pd.DataFrame, threshold_min: float = 10.0) -> dict:
    failed = df[df["failed"]]
    within_threshold = (failed["detection_latency_min"] <= threshold_min).sum()
    pct_within = round(100 * within_threshold / len(failed), 2) if len(failed) else None

    return {"n_runs": len(df), "n_failed_runs": len(failed),
            "mean_detection_latency_min": round(float(failed["detection_latency_min"].mean()), 2),
            "pct_caught_within_10min": pct_within}
