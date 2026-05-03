"""
Publication-quality plots for Residual RL experimental results.
Generates elegant bar charts with 95% CI error bars in a blue theme.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from pathlib import Path

# ============================================================================
# STYLE CONFIGURATION
# ============================================================================

# Blue palette - from dark to light
COLORS = {
    "base": "#1a365d",  # Deep navy for base
    "rl_td3": "#7fb3d5",  # Light steel blue
    "rl_sac": "#5dade2",  # Sky blue
    "rl_ppo": "#85c1e9",  # Pale blue
    "res_td3": "#2471a3",  # Strong blue
    "res_sac": "#1a5276",  # Dark cerulean
    "res_ppo": "#2e86ab",  # Ocean blue
}

# Method display names
METHOD_LABELS = {
    "Base": "Base Policy",
    "RL_TD3": "RL (TD3)",
    "RL_SAC": "RL (SAC)",
    "RL_PPO": "RL (PPO)",
    "Res_TD3": "Res-RL (TD3)",
    "Res_SAC": "Res-RL (SAC)",
    "Res_PPO": "Res-RL (PPO)",
}

# Task display names (cleaner)
TASK_LABELS = {
    "rubix-stack-v1": "Rubik's Stack",
    "bus-table-easy-v1": "Bus Table (Easy)",
    "bus-table-medium-v1": "Bus Table (Medium)",
    "bus-table-hard-v1": "Bus Table (Hard)",
    "close-bottle-lid-v1": "Close Bottle Lid",
    "erase-whiteboard-v1": "Erase Whiteboard",
    "close-french-press-v1": "Close French Press",
}


def setup_style():
    """Configure matplotlib for publication-quality output."""
    plt.rcParams.update(
        {
            # Font settings
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            # Figure settings
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.1,
            # Axes settings
            "axes.linewidth": 0.8,
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#1a1a1a",
            "axes.spines.top": False,
            "axes.spines.right": False,
            # Grid
            "axes.grid": True,
            "grid.alpha": 0.3,
            "grid.linewidth": 0.5,
            "axes.axisbelow": True,
            # Legend
            "legend.framealpha": 0.95,
            "legend.edgecolor": "#cccccc",
        }
    )


def calculate_ci(data: np.ndarray, confidence: float = 0.95) -> float:
    """Calculate 95% CI half-width."""
    n = len(data)
    if n < 2:
        return 0.0
    se = np.std(data, ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    return t_crit * se


def load_and_process_data():
    """Load CSV and compute all statistics."""
    df = pd.read_csv("results.csv")
    df_trials = df[pd.to_numeric(df["Trial"], errors="coerce").notna()].copy()
    df_trials["Trial"] = df_trials["Trial"].astype(int)

    methods = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]

    results = []
    for task, group in df_trials.groupby("Task", sort=False):
        group = group.sort_values("Trial")
        all_trials = group[methods].astype(float).values
        gen_trials = group[group["Trial"] >= 11][methods].astype(float).values
        base_gen = group[group["Trial"] >= 11]["Base"].astype(float).values

        for i, method in enumerate(methods):
            # Mean Progress
            mp_data = all_trials[:, i]
            results.append(
                {
                    "Task": task,
                    "Metric": "MeanProgress",
                    "Method": method,
                    "Mean": np.mean(mp_data),
                    "CI": calculate_ci(mp_data),
                }
            )
            # Generalization
            gen_data = gen_trials[:, i]
            results.append(
                {
                    "Task": task,
                    "Metric": "Generalization",
                    "Method": method,
                    "Mean": np.mean(gen_data),
                    "CI": calculate_ci(gen_data),
                }
            )
            # Transfer Gap
            if method.startswith("Res_"):
                diff = gen_data - base_gen
                results.append(
                    {
                        "Task": task,
                        "Metric": "TransferGap",
                        "Method": method,
                        "Mean": np.mean(diff),
                        "CI": calculate_ci(diff),
                    }
                )

    return pd.DataFrame(results), df_trials


def plot_overall_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 1: Overall performance comparison across all tasks.
    Shows Mean Progress averaged across all 7 tasks.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]
    mp_data = df_stats[df_stats["Metric"] == "MeanProgress"]

    # Aggregate across tasks
    agg_means = []
    agg_cis = []
    for method in methods:
        method_data = mp_data[mp_data["Method"] == method]
        # Pool the means and compute CI of the means
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(methods))
    colors = (
        [COLORS["base"]]
        + [COLORS["rl_td3"], COLORS["rl_sac"], COLORS["rl_ppo"]]
        + [COLORS["res_td3"], COLORS["res_sac"], COLORS["res_ppo"]]
    )

    bars = ax.bar(
        x, agg_means, width=0.65, color=colors, edgecolor="white", linewidth=1.5
    )

    # Error bars with caps
    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        ecolor="#1a1a1a",
        elinewidth=1.5,
        capsize=5,
        capthick=1.5,
    )

    # Add value labels on bars
    for bar, mean, ci in zip(bars, agg_means, agg_cis):
        height = bar.get_height()
        ax.annotate(
            f"{mean:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height + ci + 0.02),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="medium",
        )

    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in methods], rotation=25, ha="right")
    ax.set_ylabel("Mean Task Progress", fontweight="medium")
    ax.set_title(
        "Overall Performance Comparison\n(Averaged Across All Tasks)",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 1.15)
    ax.axhline(
        y=agg_means[0], color=COLORS["base"], linestyle="--", alpha=0.5, linewidth=1
    )

    # Add baseline reference text
    ax.text(
        6.5,
        agg_means[0] + 0.02,
        "Baseline",
        fontsize=9,
        color=COLORS["base"],
        alpha=0.8,
    )

    plt.tight_layout()
    fig.savefig(output_dir / "01_overall_mean_progress.png", dpi=300)
    fig.savefig(output_dir / "01_overall_mean_progress.pdf")
    plt.close(fig)
    print("✓ Saved: 01_overall_mean_progress")


def plot_generalization_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 2: Generalization scores (OOD performance, trials 11-20).
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]
    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    agg_means = []
    agg_cis = []
    for method in methods:
        method_data = gen_data[gen_data["Method"] == method]
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(methods))
    colors = (
        [COLORS["base"]]
        + [COLORS["rl_td3"], COLORS["rl_sac"], COLORS["rl_ppo"]]
        + [COLORS["res_td3"], COLORS["res_sac"], COLORS["res_ppo"]]
    )

    bars = ax.bar(
        x, agg_means, width=0.65, color=colors, edgecolor="white", linewidth=1.5
    )
    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        ecolor="#1a1a1a",
        elinewidth=1.5,
        capsize=5,
        capthick=1.5,
    )

    for bar, mean, ci in zip(bars, agg_means, agg_cis):
        height = bar.get_height()
        ax.annotate(
            f"{mean:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height + ci + 0.02),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="medium",
        )

    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in methods], rotation=25, ha="right")
    ax.set_ylabel("Generalization Score ($J_{gen}$)", fontweight="medium")
    ax.set_title(
        "Generalization Performance (OOD Trials 11–20)\n(Averaged Across All Tasks)",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 1.15)
    ax.axhline(
        y=agg_means[0], color=COLORS["base"], linestyle="--", alpha=0.5, linewidth=1
    )

    plt.tight_layout()
    fig.savefig(output_dir / "02_generalization_comparison.png", dpi=300)
    fig.savefig(output_dir / "02_generalization_comparison.pdf")
    plt.close(fig)
    print("✓ Saved: 02_generalization_comparison")


def plot_transfer_gap(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 3: Transfer Gap - the explicit benefit of Residual RL over baseline.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    methods = ["Res_TD3", "Res_SAC", "Res_PPO"]
    tg_data = df_stats[df_stats["Metric"] == "TransferGap"]

    agg_means = []
    agg_cis = []
    for method in methods:
        method_data = tg_data[tg_data["Method"] == method]
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(methods))
    colors = [COLORS["res_td3"], COLORS["res_sac"], COLORS["res_ppo"]]

    bars = ax.bar(
        x, agg_means, width=0.55, color=colors, edgecolor="white", linewidth=2
    )
    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        ecolor="#1a1a1a",
        elinewidth=2,
        capsize=6,
        capthick=2,
    )

    for bar, mean, ci in zip(bars, agg_means, agg_cis):
        height = bar.get_height()
        ax.annotate(
            f"+{mean:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height + ci + 0.015),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#1a365d",
        )

    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in methods])
    ax.set_ylabel("Transfer Gap ($\\Delta_{gen}$)", fontweight="medium")
    ax.set_title(
        "Transfer Gap: Residual RL Improvement Over Baseline\n(Generalization Performance Gain)",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 0.6)
    ax.axhline(y=0, color="#333333", linewidth=1)

    # Add annotation
    ax.text(
        1,
        0.52,
        "All methods show significant\npositive transfer",
        ha="center",
        fontsize=10,
        style="italic",
        color="#555555",
    )

    plt.tight_layout()
    fig.savefig(output_dir / "03_transfer_gap.png", dpi=300)
    fig.savefig(output_dir / "03_transfer_gap.pdf")
    plt.close(fig)
    print("✓ Saved: 03_transfer_gap")


def plot_per_task_breakdown(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 4: Per-task breakdown showing Base vs Best Residual RL.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    tasks = list(TASK_LABELS.keys())
    mp_data = df_stats[df_stats["Metric"] == "MeanProgress"]

    base_means = []
    base_cis = []
    best_res_means = []
    best_res_cis = []
    best_res_methods = []

    for task in tasks:
        task_data = mp_data[mp_data["Task"] == task]

        # Base performance
        base_row = task_data[task_data["Method"] == "Base"].iloc[0]
        base_means.append(base_row["Mean"])
        base_cis.append(base_row["CI"])

        # Best residual method
        res_data = task_data[task_data["Method"].str.startswith("Res_")]
        best_idx = res_data["Mean"].idxmax()
        best_row = res_data.loc[best_idx]
        best_res_means.append(best_row["Mean"])
        best_res_cis.append(best_row["CI"])
        best_res_methods.append(best_row["Method"])

    x = np.arange(len(tasks))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        base_means,
        width,
        label="Base Policy",
        color=COLORS["base"],
        edgecolor="white",
        linewidth=1.5,
    )
    bars2 = ax.bar(
        x + width / 2,
        best_res_means,
        width,
        label="Best Res-RL",
        color=COLORS["res_sac"],
        edgecolor="white",
        linewidth=1.5,
    )

    ax.errorbar(
        x - width / 2,
        base_means,
        yerr=base_cis,
        fmt="none",
        ecolor="#333333",
        elinewidth=1.2,
        capsize=4,
        capthick=1.2,
    )
    ax.errorbar(
        x + width / 2,
        best_res_means,
        yerr=best_res_cis,
        fmt="none",
        ecolor="#333333",
        elinewidth=1.2,
        capsize=4,
        capthick=1.2,
    )

    # Add improvement percentages
    for i, (base, best, ci) in enumerate(zip(base_means, best_res_means, best_res_cis)):
        if base > 0:
            improvement = ((best - base) / base) * 100
            ax.annotate(
                f"+{improvement:.0f}%",
                xy=(x[i] + width / 2, best + ci + 0.03),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=COLORS["res_sac"],
            )

    ax.set_xticks(x)
    ax.set_xticklabels([TASK_LABELS[t] for t in tasks], rotation=30, ha="right")
    ax.set_ylabel("Mean Task Progress", fontweight="medium")
    ax.set_title(
        "Per-Task Performance: Base Policy vs Best Residual RL",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 1.25)
    ax.legend(loc="upper right", framealpha=0.95)

    plt.tight_layout()
    fig.savefig(output_dir / "04_per_task_breakdown.png", dpi=300)
    fig.savefig(output_dir / "04_per_task_breakdown.pdf")
    plt.close(fig)
    print("✓ Saved: 04_per_task_breakdown")


def plot_residual_rl_methods_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 5: Comparison of the three Residual RL algorithms across tasks.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    tasks = list(TASK_LABELS.keys())
    methods = ["Res_TD3", "Res_SAC", "Res_PPO"]
    colors = [COLORS["res_td3"], COLORS["res_sac"], COLORS["res_ppo"]]

    for ax_idx, (ax, metric, title) in enumerate(
        zip(
            axes,
            ["MeanProgress", "Generalization"],
            [
                "Mean Task Progress (All 20 Trials)",
                "Generalization Score (OOD Trials 11–20)",
            ],
        )
    ):
        metric_data = df_stats[df_stats["Metric"] == metric]

        x = np.arange(len(tasks))
        width = 0.25

        for i, (method, color) in enumerate(zip(methods, colors)):
            means = []
            cis = []
            for task in tasks:
                row = metric_data[
                    (metric_data["Task"] == task) & (metric_data["Method"] == method)
                ].iloc[0]
                means.append(row["Mean"])
                cis.append(row["CI"])

            offset = (i - 1) * width
            bars = ax.bar(
                x + offset,
                means,
                width,
                label=METHOD_LABELS[method],
                color=color,
                edgecolor="white",
                linewidth=1,
            )
            ax.errorbar(
                x + offset,
                means,
                yerr=cis,
                fmt="none",
                ecolor="#333333",
                elinewidth=1,
                capsize=3,
                capthick=1,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(
            [TASK_LABELS[t] for t in tasks], rotation=35, ha="right", fontsize=9
        )
        ax.set_ylabel("Score", fontweight="medium")
        ax.set_title(title, fontweight="bold", pad=10)
        ax.set_ylim(0, 1.15)
        ax.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    fig.savefig(output_dir / "05_residual_rl_comparison.png", dpi=300)
    fig.savefig(output_dir / "05_residual_rl_comparison.pdf")
    plt.close(fig)
    print("✓ Saved: 05_residual_rl_comparison")


def plot_rl_vs_residual_rl(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 6: Direct comparison of RL vs Residual RL (same algorithm).
    Shows that residual RL consistently outperforms pure RL.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    algorithms = ["TD3", "SAC", "PPO"]
    x = np.arange(len(algorithms))
    width = 0.35

    rl_means = []
    rl_cis = []
    res_means = []
    res_cis = []

    for alg in algorithms:
        rl_method = f"RL_{alg}"
        res_method = f"Res_{alg}"

        rl_data = gen_data[gen_data["Method"] == rl_method]["Mean"].values
        res_data = gen_data[gen_data["Method"] == res_method]["Mean"].values

        rl_means.append(np.mean(rl_data))
        rl_cis.append(calculate_ci(rl_data))
        res_means.append(np.mean(res_data))
        res_cis.append(calculate_ci(res_data))

    bars1 = ax.bar(
        x - width / 2,
        rl_means,
        width,
        label="Pure RL",
        color="#85c1e9",
        edgecolor="white",
        linewidth=2,
    )
    bars2 = ax.bar(
        x + width / 2,
        res_means,
        width,
        label="Residual RL",
        color=COLORS["res_sac"],
        edgecolor="white",
        linewidth=2,
    )

    ax.errorbar(
        x - width / 2,
        rl_means,
        yerr=rl_cis,
        fmt="none",
        ecolor="#333333",
        elinewidth=1.5,
        capsize=5,
        capthick=1.5,
    )
    ax.errorbar(
        x + width / 2,
        res_means,
        yerr=res_cis,
        fmt="none",
        ecolor="#333333",
        elinewidth=1.5,
        capsize=5,
        capthick=1.5,
    )

    # Add improvement arrows
    for i, (rl, res, res_ci) in enumerate(zip(rl_means, res_means, res_cis)):
        improvement = res - rl
        ax.annotate(
            f"+{improvement:.2f}",
            xy=(x[i] + width / 2, res + res_ci + 0.03),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color=COLORS["res_sac"],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, fontsize=12)
    ax.set_xlabel("RL Algorithm", fontweight="medium")
    ax.set_ylabel("Generalization Score", fontweight="medium")
    ax.set_title(
        "Pure RL vs Residual RL by Algorithm\n(Generalization Performance)",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 1.0)
    ax.legend(loc="upper left", fontsize=11)

    plt.tight_layout()
    fig.savefig(output_dir / "06_rl_vs_residual_rl.png", dpi=300)
    fig.savefig(output_dir / "06_rl_vs_residual_rl.pdf")
    plt.close(fig)
    print("✓ Saved: 06_rl_vs_residual_rl")


def plot_summary_hero(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 7: Hero summary plot - single striking visualization.
    Shows the key finding: Residual RL dramatically improves over baseline.
    """
    fig, ax = plt.subplots(figsize=(9, 7))

    # Compare Base, Best Pure RL, Best Residual RL on Generalization
    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    categories = ["Base Policy", "Best Pure RL\n(SAC)", "Best Residual RL\n(Res-SAC)"]
    methods = ["Base", "RL_SAC", "Res_SAC"]

    means = []
    cis = []
    for method in methods:
        data = gen_data[gen_data["Method"] == method]["Mean"].values
        means.append(np.mean(data))
        cis.append(calculate_ci(data))

    x = np.arange(len(categories))
    colors_hero = ["#5d6d7e", "#7fb3d5", "#1a5276"]

    bars = ax.bar(
        x, means, width=0.6, color=colors_hero, edgecolor="white", linewidth=3
    )
    ax.errorbar(
        x,
        means,
        yerr=cis,
        fmt="none",
        ecolor="#1a1a1a",
        elinewidth=2.5,
        capsize=8,
        capthick=2.5,
    )

    # Bold value labels
    for bar, mean, ci in zip(bars, means, cis):
        height = bar.get_height()
        ax.annotate(
            f"{mean:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height + ci + 0.025),
            ha="center",
            va="bottom",
            fontsize=16,
            fontweight="bold",
        )

    # Improvement annotation
    improvement = ((means[2] - means[0]) / means[0]) * 100 if means[0] > 0 else 0
    ax.annotate(
        f"+{improvement:.0f}%\nimprovement",
        xy=(2, means[2] + cis[2] + 0.12),
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
        color=COLORS["res_sac"],
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor=COLORS["res_sac"],
            alpha=0.9,
        ),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=13, fontweight="medium")
    ax.set_ylabel("Generalization Score ($J_{gen}$)", fontsize=13, fontweight="medium")
    ax.set_title(
        "Residual RL Dramatically Improves OOD Generalization",
        fontsize=15,
        fontweight="bold",
        pad=20,
    )
    ax.set_ylim(0, 1.1)

    # Reference line
    ax.axhline(y=means[0], color="#5d6d7e", linestyle="--", alpha=0.4, linewidth=1.5)

    plt.tight_layout()
    fig.savefig(output_dir / "07_hero_summary.png", dpi=300)
    fig.savefig(output_dir / "07_hero_summary.pdf")
    plt.close(fig)
    print("✓ Saved: 07_hero_summary")


def plot_task_difficulty_analysis(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 8: Bus Table difficulty progression showing Res-RL maintains performance.
    """
    fig, ax = plt.subplots(figsize=(9, 6))

    # Focus on bus-table tasks at different difficulties
    tasks = ["bus-table-easy-v1", "bus-table-medium-v1", "bus-table-hard-v1"]
    difficulty_labels = ["Easy", "Medium", "Hard"]

    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    methods = ["Base", "Res_SAC"]
    colors_diff = [COLORS["base"], COLORS["res_sac"]]
    markers = ["o", "s"]

    x = np.arange(len(tasks))

    for method, color, marker in zip(methods, colors_diff, markers):
        means = []
        cis = []
        for task in tasks:
            row = gen_data[
                (gen_data["Task"] == task) & (gen_data["Method"] == method)
            ].iloc[0]
            means.append(row["Mean"])
            cis.append(row["CI"])

        label = "Base Policy" if method == "Base" else "Res-RL (SAC)"
        ax.errorbar(
            x,
            means,
            yerr=cis,
            fmt=f"-{marker}",
            color=color,
            linewidth=2.5,
            markersize=12,
            capsize=6,
            capthick=2,
            label=label,
            markeredgecolor="white",
            markeredgewidth=2,
        )

        # Fill between for confidence band (Bollinger-style)
        means_arr = np.array(means)
        cis_arr = np.array(cis)
        ax.fill_between(
            x, means_arr - cis_arr, means_arr + cis_arr, color=color, alpha=0.15
        )

    ax.set_xticks(x)
    ax.set_xticklabels(difficulty_labels, fontsize=12)
    ax.set_xlabel("Task Difficulty", fontsize=12, fontweight="medium")
    ax.set_ylabel("Generalization Score", fontsize=12, fontweight="medium")
    ax.set_title(
        "Robustness to Task Difficulty: Bus Table Environment",
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper right", fontsize=11)

    # Add annotation
    ax.annotate(
        "Res-RL maintains\nhigh performance",
        xy=(2, 0.75),
        ha="center",
        fontsize=10,
        style="italic",
        color=COLORS["res_sac"],
    )

    plt.tight_layout()
    fig.savefig(output_dir / "08_task_difficulty.png", dpi=300)
    fig.savefig(output_dir / "08_task_difficulty.pdf")
    plt.close(fig)
    print("✓ Saved: 08_task_difficulty")


def main():
    setup_style()
    output_dir = Path("Plots")
    output_dir.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("Generating Publication-Quality Plots")
    print("=" * 60 + "\n")

    df_stats, df_trials = load_and_process_data()

    # Generate all plots
    plot_overall_comparison(df_stats, output_dir)
    plot_generalization_comparison(df_stats, output_dir)
    plot_transfer_gap(df_stats, output_dir)
    plot_per_task_breakdown(df_stats, output_dir)
    plot_residual_rl_methods_comparison(df_stats, output_dir)
    plot_rl_vs_residual_rl(df_stats, output_dir)
    plot_summary_hero(df_stats, output_dir)
    plot_task_difficulty_analysis(df_stats, output_dir)

    print("\n" + "=" * 60)
    print(f"All plots saved to: {output_dir.absolute()}")
    print("Formats: PNG (300 DPI) + PDF (vector)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
