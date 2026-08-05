#!/usr/bin/env python3
"""
Generate visualization charts for Hologres Open Memory LoCoMo benchmark results.

Generates 5 charts:
1. overall_score_comparison.png — Bar chart comparing Overall scores
2. score_by_category.png — Grouped bar chart by question type
3. radar_chart.png — Radar/spider chart across 4 categories
4. run_stability.png — Per-run Overall scores for Hologres Open Memory
5. category_breakdown_heatmap.png — Heatmap of per-run category scores

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
NUM_RUNS = 5
DPI = 150

# Color palette — professional and distinct
COLORS = {
    "Hologres Open Memory": "#2563EB",  # Bold blue
    "Zep": "#F97316",                   # Orange
    "MemoryLake": "#F59E0B",            # Amber
    "EverMemOS": "#10B981",             # Emerald
    "Mem0": "#8B5CF6",                  # Violet
    "ByteRover 2.0": "#EC4899",         # Pink
    "Honcho": "#14B8A6",                # Teal
    "MemOS": "#A855F7",                 # Purple
}

# Comparison data (from README), sorted by Overall descending
COMPARISON_DATA = {
    "Hologres Open Memory": {
        "Single-hop": 95.46, "Multi-hop": 96.74,
        "Temporal": 97.45, "Open-domain": 81.46, "Overall": 95.23
    },
    "Zep": {
        "Single-hop": 96.4, "Multi-hop": 94.0,
        "Temporal": 95.6, "Open-domain": 79.2, "Overall": 94.7
    },
    "MemoryLake": {
        "Single-hop": 96.79, "Multi-hop": 91.84,
        "Temporal": 91.28, "Open-domain": 85.42, "Overall": 94.03
    },
    "EverMemOS": {
        "Single-hop": 96.67, "Multi-hop": 91.84,
        "Temporal": 89.72, "Open-domain": 76.04, "Overall": 93.05
    },
    "Mem0": {
        "Single-hop": 94.6, "Multi-hop": 95.4,
        "Temporal": 92.5, "Open-domain": 82.3, "Overall": 92.5
    },
    "ByteRover 2.0": {
        "Single-hop": 95.4, "Multi-hop": 85.1,
        "Temporal": 94.4, "Open-domain": 77.2, "Overall": 92.2
    },
    "Honcho": {
        "Single-hop": 84.0, "Multi-hop": 88.2,
        "Temporal": 77.1, "Open-domain": 93.2, "Overall": 89.9
    },
    "MemOS": {
        "Single-hop": 92.51, "Multi-hop": 88.65,
        "Temporal": 85.05, "Open-domain": 69.79, "Overall": 88.83
    },
}

# All 8 systems, sorted by Overall descending
SYSTEMS = list(COMPARISON_DATA.keys())
# Subsets to keep grouped charts readable
SYSTEMS_TOP5 = SYSTEMS[:5]  # category grouped bar chart
SYSTEMS_TOP4 = SYSTEMS[:4]  # radar chart
CATEGORIES = ["Single-hop", "Temporal", "Multi-hop", "Open-domain"]


# ============================================================================
# Data Loading
# ============================================================================

def load_results(base_dir: str) -> list:
    """Load all 5 result files."""
    runs = []
    for i in range(1, NUM_RUNS + 1):
        filepath = os.path.join(base_dir, f"locomo_result_{i}.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        runs.append(data)
    return runs


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
# Chart 1: Overall Score Comparison
# ============================================================================

def plot_overall_comparison(output_dir: str):
    """Bar chart comparing Overall scores of all 8 systems."""
    fig, ax = plt.subplots(figsize=(12, 6))

    systems = SYSTEMS
    scores = [COMPARISON_DATA[s]["Overall"] for s in systems]
    colors = [COLORS[s] for s in systems]

    bars = ax.bar(systems, scores, color=colors, width=0.65, edgecolor='white', linewidth=0.8)

    # Highlight Hologres bar
    bars[0].set_edgecolor('#1E40AF')
    bars[0].set_linewidth(2)

    # Add value labels on bars
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f'{score:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('Overall F1 Score (%)', fontsize=11)
    ax.set_title('Overall Score Comparison — LoCoMo Benchmark', fontsize=13, fontweight='bold', pad=15)
    ax.set_ylim(84, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.tick_params(axis='x', labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'overall_score_comparison.png'), dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [1/5] overall_score_comparison.png ✓")


# ============================================================================
# Chart 2: Score by Category (Grouped Bar Chart)
# ============================================================================

def plot_score_by_category(output_dir: str):
    """Grouped bar chart showing scores by question type for the top 5 systems."""
    fig, ax = plt.subplots(figsize=(12, 6))

    systems = SYSTEMS_TOP5
    x = np.arange(len(CATEGORIES))
    width = 0.16
    n = len(systems)

    for i, system in enumerate(systems):
        scores = [COMPARISON_DATA[system][cat] for cat in CATEGORIES]
        offset = (i - (n - 1) / 2) * width
        bars = ax.bar(x + offset, scores, width, label=system,
                      color=COLORS[system], edgecolor='white', linewidth=0.5)
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f'{score:.1f}', ha='center', va='bottom', fontsize=7)

    ax.set_xlabel('Question Category', fontsize=11)
    ax.set_ylabel('F1 Score (%)', fontsize=11)
    ax.set_title('Score by Question Category — Top 5 Systems', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(CATEGORIES, fontsize=10)
    ax.set_ylim(65, 102)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax.legend(fontsize=9, loc='lower left', ncol=2)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'score_by_category.png'), dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [2/5] score_by_category.png ✓")


# ============================================================================
# Chart 3: Radar Chart
# ============================================================================

def plot_radar_chart(output_dir: str):
    """Radar/spider chart comparing the top 4 systems across 4 categories."""
    categories = CATEGORIES
    num_vars = len(categories)

    # Compute angles
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    for system in SYSTEMS_TOP4:
        values = [COMPARISON_DATA[system][cat] for cat in categories]
        values += values[:1]  # Close the polygon
        ax.plot(angles, values, 'o-', linewidth=2, label=system, color=COLORS[system], markersize=6)
        ax.fill(angles, values, alpha=0.1, color=COLORS[system])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(60, 100)
    ax.set_yticks([70, 80, 90, 100])
    ax.set_yticklabels(['70%', '80%', '90%', '100%'], fontsize=9)
    ax.set_title('Multi-Dimensional Comparison — Radar Chart', fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='lower right', bbox_to_anchor=(1.15, -0.05), fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'radar_chart.png'), dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [3/5] radar_chart.png ✓")


# ============================================================================
# Chart 4: Run Stability
# ============================================================================

def plot_run_stability(runs: list, output_dir: str):
    """Line chart showing Overall score for each of the 5 runs."""
    fig, ax = plt.subplots(figsize=(8, 5))

    run_overalls = []
    for run_data in runs:
        overall = calculate_overall_score(run_data)
        run_overalls.append(overall)

    run_labels = [f'Run {i+1}' for i in range(NUM_RUNS)]
    x = np.arange(1, NUM_RUNS + 1)
    avg = np.mean(run_overalls)

    # Plot line with markers
    ax.plot(x, run_overalls, 'o-', color=COLORS["Hologres Open Memory"],
            linewidth=2.5, markersize=10, markerfacecolor='white',
            markeredgecolor=COLORS["Hologres Open Memory"], markeredgewidth=2.5)

    # Average horizontal line
    ax.axhline(y=avg, color='#EF4444', linestyle='--', linewidth=1.5, label=f'Average: {avg:.2f}%')

    # Annotate each point
    for i, score in enumerate(run_overalls):
        ax.annotate(f'{score:.2f}%', (x[i], score),
                    textcoords="offset points", xytext=(0, 12),
                    ha='center', fontsize=9, fontweight='bold')

    ax.set_xlabel('Run', fontsize=11)
    ax.set_ylabel('Overall F1 Score (%)', fontsize=11)
    ax.set_title('Hologres Open Memory — Run Stability', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(run_labels, fontsize=10)
    ax.set_ylim(94.0, 96.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    ax.legend(fontsize=10, loc='lower right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'run_stability.png'), dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [4/5] run_stability.png ✓")


# ============================================================================
# Chart 5: Category Breakdown Heatmap
# ============================================================================

def plot_category_heatmap(runs: list, output_dir: str):
    """Heatmap showing per-run scores for each category."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Build data matrix: rows=runs, columns=categories
    data = []
    for run_data in runs:
        cat_scores = calculate_category_scores(run_data)
        row = [cat_scores[cat] if cat_scores[cat] is not None else 0 for cat in CATEGORY_ORDER]
        data.append(row)

    data = np.array(data)
    run_labels = [f'Run {i+1}' for i in range(NUM_RUNS)]
    cat_labels = [CATEGORY_NAMES[c] for c in CATEGORY_ORDER]

    # Create heatmap
    im = ax.imshow(data, cmap='YlGnBu', aspect='auto', vmin=75, vmax=100)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('F1 Score (%)', fontsize=10)

    # Set ticks
    ax.set_xticks(np.arange(len(cat_labels)))
    ax.set_yticks(np.arange(len(run_labels)))
    ax.set_xticklabels(cat_labels, fontsize=10)
    ax.set_yticklabels(run_labels, fontsize=10)

    # Add text annotations in cells
    for i in range(len(run_labels)):
        for j in range(len(cat_labels)):
            val = data[i, j]
            text_color = 'white' if val > 92 else 'black'
            ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                    fontsize=10, fontweight='bold', color=text_color)

    ax.set_title('Hologres Open Memory — Per-Run Category Scores', fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'category_breakdown_heatmap.png'), dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [5/5] category_breakdown_heatmap.png ✓")


# ============================================================================
# Main
# ============================================================================

def main():
    base_dir = str(Path(__file__).parent)
    output_dir = os.path.join(base_dir, 'images')
    os.makedirs(output_dir, exist_ok=True)

    print("Loading result files...")
    runs = load_results(base_dir)
    print(f"  Loaded {len(runs)} runs, {len(runs[0])} questions per run\n")

    print("Generating charts...")
    plot_overall_comparison(output_dir)
    plot_score_by_category(output_dir)
    plot_radar_chart(output_dir)
    plot_run_stability(runs, output_dir)
    plot_category_heatmap(runs, output_dir)

    print(f"\nAll charts saved to: {output_dir}")


if __name__ == "__main__":
    main()
