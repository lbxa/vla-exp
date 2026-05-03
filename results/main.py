import pandas as pd
import numpy as np
from scipy import stats


def calculate_ci(data: np.ndarray, confidence: float = 0.95) -> float:
    """Calculate 95% CI half-width (error bar)."""
    n = len(data)
    if n < 2:
        return np.nan
    se = np.std(data, ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    return t_crit * se


def main():
    # Read CSV
    df = pd.read_csv("results.csv")

    # Filter to trial rows only (Trial column is numeric)
    df_trials = df[pd.to_numeric(df["Trial"], errors="coerce").notna()].copy()
    df_trials["Trial"] = df_trials["Trial"].astype(int)

    methods = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]
    res_methods = ["Res_TD3", "Res_SAC", "Res_PPO"]

    results = []

    # Group by task
    for task, group in df_trials.groupby("Task", sort=False):
        group = group.sort_values("Trial")

        # Mean Progress: all 20 trials
        all_trials = group[methods].astype(float).values

        # Generalization: trials 11-20
        gen_trials = group[group["Trial"] >= 11][methods].astype(float).values
        base_gen = group[group["Trial"] >= 11]["Base"].astype(float).values

        for i, method in enumerate(methods):
            # Mean Progress
            mp_data = all_trials[:, i]
            mp_mean = np.mean(mp_data)
            mp_ci = calculate_ci(mp_data)
            results.append(
                {
                    "Task": task,
                    "Metric": "MeanProgress",
                    "Method": method,
                    "Mean": mp_mean,
                    "CI_95": mp_ci,
                }
            )

            # Generalization
            gen_data = gen_trials[:, i]
            gen_mean = np.mean(gen_data)
            gen_ci = calculate_ci(gen_data)
            results.append(
                {
                    "Task": task,
                    "Metric": "Generalization",
                    "Method": method,
                    "Mean": gen_mean,
                    "CI_95": gen_ci,
                }
            )

            # Transfer Gap (only for Res_* methods)
            if method in res_methods:
                # Paired difference: Res_i - Base_i for trials 11-20
                diff = gen_data - base_gen
                tg_mean = np.mean(diff)
                tg_ci = calculate_ci(diff)
                results.append(
                    {
                        "Task": task,
                        "Metric": "TransferGap",
                        "Method": method,
                        "Mean": tg_mean,
                        "CI_95": tg_ci,
                    }
                )

    # Create output dataframe
    results_df = pd.DataFrame(results)

    # Write to CSV
    results_df.to_csv("results_with_ci.csv", index=False)

    # Print formatted tables to console
    print("=" * 80)
    print("95% CONFIDENCE INTERVALS FOR EXPERIMENTAL RESULTS")
    print("=" * 80)

    for task in df_trials["Task"].unique():
        print(f"\n{'=' * 80}")
        print(f"TASK: {task}")
        print("=" * 80)

        task_results = results_df[results_df["Task"] == task]

        # Mean Progress
        print("\n--- Mean Progress (all 20 trials) ---")
        mp = task_results[task_results["Metric"] == "MeanProgress"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in mp.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

        # Generalization
        print("\n--- Generalization (trials 11-20) ---")
        gen = task_results[task_results["Metric"] == "Generalization"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in gen.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

        # Transfer Gap
        print("\n--- Transfer Gap (Res - Base, trials 11-20) ---")
        tg = task_results[task_results["Metric"] == "TransferGap"]
        print(f"{'Method':<12} {'Mean':>10} {'± CI_95':>12}")
        print("-" * 36)
        for _, row in tg.iterrows():
            print(f"{row['Method']:<12} {row['Mean']:>10.4f} {row['CI_95']:>12.4f}")

    print(f"\n{'=' * 80}")
    print(f"Results saved to: results_with_ci.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()
