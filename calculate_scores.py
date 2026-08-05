#!/usr/bin/env python3
"""
Calculate LoCoMo benchmark scores for Hologres Open Memory.

Reads all 5 locomo_result_*.json files and computes:
- Per-category scores for each run
- Overall averages across all runs

Usage:
    python calculate_scores.py
"""

import json
import os
from pathlib import Path

# Category mapping
CATEGORY_NAMES = {
    1: "Multi-hop",
    2: "Temporal",
    3: "Open-domain",
    4: "Single-hop",
}

CATEGORY_ORDER = [1, 2, 3, 4]
NUM_RUNS = 5


def load_results(base_dir: str) -> list[list[dict]]:
    """Load all result files and return list of runs."""
    runs = []
    for i in range(1, NUM_RUNS + 1):
        filepath = os.path.join(base_dir, f"locomo_result_{i}.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        runs.append(data)
    return runs


def calculate_category_scores(items: list[dict]) -> dict[int, float]:
    """Calculate per-category accuracy for a list of items."""
    cat_correct = {}
    cat_total = {}

    for item in items:
        cat = item["category"]
        cat_correct[cat] = cat_correct.get(cat, 0) + item["score"]
        cat_total[cat] = cat_total.get(cat, 0) + 1

    scores = {}
    for cat in CATEGORY_ORDER:
        if cat in cat_total and cat_total[cat] > 0:
            scores[cat] = cat_correct[cat] / cat_total[cat] * 100
        else:
            scores[cat] = None

    return scores


def calculate_overall_score(items: list[dict]) -> float:
    """Calculate overall accuracy for a list of items."""
    if not items:
        return 0.0
    return sum(item["score"] for item in items) / len(items) * 100


def print_separator(width: int = 90):
    """Print a horizontal separator."""
    print("=" * width)


def print_header(title: str, width: int = 90):
    """Print a section header."""
    print()
    print_separator(width)
    print(f"  {title}")
    print_separator(width)
    print()


def format_score(score, width=9):
    """Format a score value for display."""
    if score is None:
        return f"{'N/A':>{width}}"
    return f"{score:>{width}.2f}%"


def main():
    base_dir = Path(__file__).parent

    # Load all runs
    print("Loading result files...")
    runs = load_results(str(base_dir))
    print(f"  Loaded {len(runs)} runs, {len(runs[0])} questions per run")

    # =========================================================================
    # Per-Run Category Scores
    # =========================================================================
    print_header("PER-RUN CATEGORY SCORES")

    run_scores = []  # List of (cat_scores_dict, overall)

    header = f"{'Run':<8}"
    for cat in CATEGORY_ORDER:
        header += f" {CATEGORY_NAMES[cat]:>12}"
    header += f" {'Overall':>10}"
    print(header)
    print("-" * len(header))

    for run_idx, run_data in enumerate(runs):
        cat_scores = calculate_category_scores(run_data)
        overall = calculate_overall_score(run_data)
        run_scores.append((cat_scores, overall))

        row = f"Run {run_idx + 1:<4}"
        for cat in CATEGORY_ORDER:
            row += f" {format_score(cat_scores[cat], 12)}"
        row += f" {overall:>9.2f}%"
        print(row)

    # Calculate averages
    print("-" * len(header))
    avg_row = f"{'Average':<8}"
    avg_cat_scores = {}
    for cat in CATEGORY_ORDER:
        values = [s[0][cat] for s in run_scores if s[0][cat] is not None]
        avg = sum(values) / len(values) if values else None
        avg_cat_scores[cat] = avg
        avg_row += f" {format_score(avg, 12)}"

    avg_overall = sum(s[1] for s in run_scores) / len(run_scores)
    avg_row += f" {avg_overall:>9.2f}%"
    print(avg_row)

    # =========================================================================
    # Summary Statistics
    # =========================================================================
    print_header("SUMMARY")

    print(f"  Overall Score (5-run average):  {avg_overall:.2f}%")
    print(f"  Best Single Run:                {max(s[1] for s in run_scores):.2f}%")
    print(f"  Worst Single Run:               {min(s[1] for s in run_scores):.2f}%")
    print(f"  Score Range:                    {max(s[1] for s in run_scores) - min(s[1] for s in run_scores):.2f}%")
    print()
    print("  Per-Category Averages:")
    for cat in CATEGORY_ORDER:
        if avg_cat_scores[cat] is not None:
            print(f"    {CATEGORY_NAMES[cat]:<12}  {avg_cat_scores[cat]:.2f}%")
    print()


if __name__ == "__main__":
    main()
