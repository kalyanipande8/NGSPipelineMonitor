import json
import os

from src.simulate_pipeline_runs import simulate_runs, summarize_detection


def main():
    df = simulate_runs()
    summary = summarize_detection(df)

    os.makedirs("results", exist_ok=True)
    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
