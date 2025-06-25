import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("error_analysis_per_measure_variable.csv")

# Calculation for both alignment and accompaniment errors
alignment_stats = df["alignment_error"].describe()
accompaniment_stats = df["accompaniment_error"].describe()

# Calculate absolute errors
df["abs_alignment_error"] = abs(df["alignment_error"])
df["abs_accompaniment_error"] = abs(df["accompaniment_error"])

# Save stats in a dataframe
stats_df = pd.DataFrame(
    {
        "Statistic": alignment_stats.index.tolist() + ["mean_absolute_error"],
        "Alignment Error": alignment_stats.values.tolist()
        + [df["abs_alignment_error"].mean()],
        "Accompaniment Error": accompaniment_stats.values.tolist()
        + [df["abs_accompaniment_error"].mean()],
    }
)

# Save statistics to CSV
stats_df.to_csv("error_statistics.csv", index=False)

plt.figure(figsize=(15, 10))

# Histogram of alignment errors
plt.subplot(2, 2, 1)
plt.hist(df["alignment_error"], bins=20, edgecolor="black")
plt.title("Histogram of Alignment Errors")
plt.xlabel("Alignment Error (seconds)")
plt.ylabel("Frequency")

# Histogram of accompaniment errors
plt.subplot(2, 2, 2)
plt.hist(df["accompaniment_error"], bins=20, edgecolor="black")
plt.title("Histogram of Accompaniment Errors")
plt.xlabel("Accompaniment Error (seconds)")
plt.ylabel("Frequency")

# Alignment error over measures (using positive and negative instances)
plt.subplot(2, 2, 3)
plt.plot(df["measure"], df["alignment_error"])
plt.title("Alignment Error Over Measures")
plt.xlabel("Measure")
plt.ylabel("Alignment Error (seconds)")
plt.axhline(y=0, color="r", linestyle="--")

# Accompaniment error over measures (using positive and negative instances)
plt.subplot(2, 2, 4)
plt.plot(df["measure"], df["accompaniment_error"])
plt.title("Accompaniment Error Over Measures")
plt.xlabel("Measure")
plt.ylabel("Accompaniment Error (seconds)")
plt.axhline(y=0, color="r", linestyle="--")

plt.tight_layout()
plt.savefig("error_analysis.png")
plt.show()

# Correlation between both
correlation = df["alignment_error"].corr(df["accompaniment_error"])
print(
    f"\nCorrelation between alignment error and accompaniment error: {correlation:.4f}"
)

# Identify measures with largest errors
worst_alignment = df.loc[df["abs_alignment_error"].idxmax()]
worst_accompaniment = df.loc[df["abs_accompaniment_error"].idxmax()]

print("\nMeasure with largest alignment error:")
print(worst_alignment[["measure", "alignment_error"]])

print("\nMeasure with largest accompaniment error:")
print(worst_accompaniment[["measure", "accompaniment_error"]])

df["alignment_error_diff"] = df["alignment_error"].diff()
df["accompaniment_error_diff"] = df["accompaniment_error"].diff()


# plot these progressions over time
plt.figure(figsize=(12, 6))
plt.plot(df["measure"][1:], df["alignment_error_diff"][1:], label="Alignment Error")
plt.plot(
    df["measure"][1:], df["accompaniment_error_diff"][1:], label="Accompaniment Error"
)
plt.title("Error Progression Over Measures")
plt.xlabel("Measure")
plt.ylabel("Error Difference (seconds)")
plt.legend()
plt.savefig("error_progression.png")
plt.show()
