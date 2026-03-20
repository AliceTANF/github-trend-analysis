import os
import ast
import pandas as pd
import matplotlib.pyplot as plt



def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "enriched_repos.csv")
    df = pd.read_csv(file_path)
    return df, base_dir


def clean_data(df):
    df = df.copy()

    # 数值列处理
    numeric_cols = ["stargazers_count", "forks_count", "open_issues_count", "contributors_count"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 时间列处理
    time_cols = ["created_at", "updated_at", "pushed_at"]
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # 缺失值处理
    df["language"] = df["language"].fillna("Unknown")
    df["contributors_count"] = df["contributors_count"].fillna(0)

    return df


def plot_top_stars(df, output_dir):
    top_df = df.sort_values("stargazers_count", ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    plt.bar(top_df["full_name"], top_df["stargazers_count"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Top 10 Repositories by Stars")
    plt.xlabel("Repository")
    plt.ylabel("Stars")
    plt.tight_layout()

    file_path = os.path.join(output_dir, "top10_stars.png")
    plt.savefig(file_path)
    plt.close()


def plot_language_distribution(df, output_dir):
    lang_df = df["language"].value_counts().head(10)

    plt.figure(figsize=(8, 8))
    plt.pie(lang_df.values, labels=lang_df.index, autopct="%1.1f%%")
    plt.title("Top Languages Distribution")
    plt.tight_layout()

    file_path = os.path.join(output_dir, "language_distribution.png")
    plt.savefig(file_path)
    plt.close()


def plot_top_contributors(df, output_dir):
    top_df = df.sort_values("contributors_count", ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    plt.bar(top_df["full_name"], top_df["contributors_count"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Top 10 Repositories by Contributors Count")
    plt.xlabel("Repository")
    plt.ylabel("Contributors Count")
    plt.tight_layout()

    file_path = os.path.join(output_dir, "top10_contributors.png")
    plt.savefig(file_path)
    plt.close()


def plot_stars_vs_forks(df, output_dir):
    plt.figure(figsize=(10, 6))
    plt.scatter(df["stargazers_count"], df["forks_count"])
    plt.title("Stars vs Forks")
    plt.xlabel("Stars")
    plt.ylabel("Forks")
    plt.tight_layout()

    file_path = os.path.join(output_dir, "stars_vs_forks.png")
    plt.savefig(file_path)
    plt.close()


def main():
    df, base_dir = load_data()
    df = clean_data(df)

    output_dir = os.path.join(base_dir, "data", "plots")
    os.makedirs(output_dir, exist_ok=True)

    plot_top_stars(df, output_dir)
    plot_language_distribution(df, output_dir)
    plot_top_contributors(df, output_dir)
    plot_stars_vs_forks(df, output_dir)

    print("图表已生成：", output_dir)


if __name__ == "__main__":
    main()