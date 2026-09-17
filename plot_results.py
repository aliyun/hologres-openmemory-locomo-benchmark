#!/usr/bin/env python3
"""
Generate visualization charts for Hologres Open Memory LoCoMo benchmark results.

Generates 1 chart:
1. score_by_category.png — Bar chart showing Hologres Open Memory scores
   across all 4 question categories plus the Overall score.

Usage:
    python plot_results.py
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# Configuration
# ============================================================================

plt.style.use('seaborn-v0_8-whitegrid')

CATEGORY_NAMES = {1: "Multi-hop", 2: "Temporal", 3: "Open-domain", 4: "Single-hop"}
CATEGORY_ORDER = [1, 2, 3, 4]
DPI = 150

# Hologres Open Memory scores
HOLOGRES_DATA = {
    "Single-hop": 97.38,
    "Multi-hop": 96.81,
    "Temporal": 98.44,
    "Open-domain": 86.46,
    "Overall": 96.82,
}

CATEGORIES = ["Single-hop", "Temporal", "Multi-hop", "Open-domain"]

# Color palette
COLOR_CATEGORY = "#2563EB"   # Bold blue for category bars
COLOR_OVERALL = "#1E3A5F"    # Dark navy for the Overall bar


# ============================================================================
# Data Loading
# ============================================================================

def load_results(base_dir: str) -> list:
    """Load the single result file."""
    filepath = os.path.join(base_dir, "locomo_result.json")
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def calculate_category_scores(items: list) -> dict:
    """Calculate per-category accuracy."""
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


def calculate_overall_score(items: list) -> float:
    """Calculate overall accuracy."""
    if not items:
        return 0.0
    return sum(item["score"] for item in items) / len(items) * 100


# ============================================================================
# Chart: Score by Category (with Overall)
# ============================================================================

def plot_score_by_category(output_dir: str):
    """Bar chart showing Hologres Open Memory scores across categories and overall."""
    labels = CATEGORIES + ["Overall"]
    scores = [HOLOGRES_DATA[cat] for cat in CATEGORIES] + [HOLOGRES_DATA["Overall"]]
    colors = [COLOR_CATEGORY] * len(CATEGORIES) + [COLOR_OVERALL]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(labels, scores, color=colors, width=0.58,
                  edgecolor='white', linewidth=1.2)

    # Distinct styling for the Overall bar
    bars[-1].set_edgecolor(COLOR_OVERALL)
    bars[-1].set_linewidth(2)
    bars[-1].set_hatch('///')

    # Value labels on each bar
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f'{score:.2f}%', ha='center', va='bottom',
                fontsize=11, fontweight='bold')

    ax.set_ylabel('F1 Score (%)', fontsize=12)
    ax.set_title('Hologres Open Memory — Score by Question Category',
                 fontsize=14, fontweight='bold', pad=18)
    ax.set_ylim(80, 102)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.tick_params(axis='x', labelsize=11)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'score_by_category.png'),
                dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [1/1] score_by_category.png ✓")


# ============================================================================
# Main
# ============================================================================

def main():
    base_dir = str(Path(__file__).parent)
    output_dir = os.path.join(base_dir, 'images')
    os.makedirs(output_dir, exist_ok=True)

    print("Loading result file...")
    results = load_results(base_dir)
    print(f"  Loaded {len(results)} questions\n")

    print("Generating charts...")
    plot_score_by_category(output_dir)

    print(f"\nAll charts saved to: {output_dir}")


if __name__ == "__main__":
    main()
