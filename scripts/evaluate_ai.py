"""Print reproducible baseline metrics; run as ``python -m scripts.evaluate_ai``."""

from __future__ import annotations

import argparse
import json

from ai_service.evaluation import evaluate_baselines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", help="Optional evaluation_cases.json path")
    parser.add_argument("--k", type=int, default=3, help="Ranking cutoff")
    args = parser.parse_args()
    print(json.dumps(evaluate_baselines(args.cases, k=args.k), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
