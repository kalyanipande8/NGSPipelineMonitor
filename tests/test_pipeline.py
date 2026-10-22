import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.simulate_pipeline_runs import simulate_runs, summarize_detection, STAGES


def test_six_pipeline_stages_defined():
    assert len(STAGES) == 6


def test_simulated_runs_produce_failures():
    df = simulate_runs()
    assert df["failed"].sum() > 0


def test_detection_latency_is_usually_small():
    df = simulate_runs(poll_interval_min=5.0)
    failed = df[df["failed"]]
    assert failed["detection_latency_min"].median() <= 10.0


def test_most_failures_caught_within_10_minutes():
    df = simulate_runs()
    summary = summarize_detection(df)
    assert summary["pct_caught_within_10min"] >= 90.0


def test_unfailed_runs_have_no_detection_latency():
    df = simulate_runs()
    unfailed = df[~df["failed"]]
    assert unfailed["detection_latency_min"].isna().all()
