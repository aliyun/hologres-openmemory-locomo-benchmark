#!/usr/bin/env python3
"""
Calculate LoCoMo benchmark scores for Hologres Open Memory.

Reads a single locomo_result.json file and computes:
- Per-category scores (correct / total / percentage)
- Overall score

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


def load_results(base_dir: str) -> list[dict]:
    """Load the single locomo_result.json file."""
    filepath = os.path.join(base_dir, "locomo_result.json")
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def calculate_category_scores(items: list[dict]) -> dict[int, tuple]:
    """Calculate per-category accuracy for a list of items.

    Returns a dict mapping category -> (correct, total, percentage).
    """
    cat_correct = {}
    cat_total = {}

    for item in items:
        cat = item["category"]
        cat_correct[cat] = cat_correct.get(cat, 0) + item["score"]
        cat_total[cat] = cat_total.get(cat, 0) + 1

    scores = {}
    for cat in CATEGORY_ORDER:
        if cat in cat_total and cat_total[cat] > 0:
            correct = cat_correct[cat]
            total = cat_total[cat]
            scores[cat] = (correct, total, correct / total * 100)
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

    # Load results
    print("Loading result file...")
    items = load_results(str(base_dir))
    print(f"  Loaded {len(items)} questions")

    # =========================================================================
    # Per-Category Scores
    # =========================================================================
    print_header("CATEGORY SCORES")

    cat_scores = calculate_category_scores(items)

    header = f"{'Category':<14} {'Correct':>8} {'Total':>8} {'Score':>10}"
    print(header)
    print("-" * len(header))

    for cat in CATEGORY_ORDER:
        if cat_scores[cat] is not None:
            correct, total, pct = cat_scores[cat]
            print(f"  {CATEGORY_NAMES[cat]:<12} {correct:>8.0f} {total:>8} {pct:>9.2f}%")
        else:
            print(f"  {CATEGORY_NAMES[cat]:<12} {'N/A':>8} {'N/A':>8} {'N/A':>10}")

    # =========================================================================
    # Overall Score
    # =========================================================================
    overall = calculate_overall_score(items)

    print_header("OVERALL SCORE")

    total_correct = sum(item["score"] for item in items)
    total_items = len(items)
    print(f"  Correct:  {total_correct:.0f} / {total_items}")
    print(f"  Score:    {overall:.2f}%")
    print()


if __name__ == "__main__":
    main()
