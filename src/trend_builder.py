import os
import glob
import pandas as pd
from datetime import datetime


def extract_snapshot_date(filename):
    """
    从文件名中提取日期
    例如: enriched_repos_llm_2026-03-19.csv -> 2026-03-19
    """
    base_name = os.path.basename(filename)
    date_str = base_name.replace(".csv", "").split("_")[-1]
    return date_str


def build_history_table():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    snapshot_dir = os.path.join(base_dir, "data", "snapshots")
    history_dir = os.path.join(base_dir, "data", "history")

    os.makedirs(snapshot_dir, exist_ok=True)
    os.makedirs(history_dir, exist_ok=True)

    file_pattern = os.path.join(snapshot_dir, "enriched_repos_*.csv")
    snapshot_files = sorted(glob.glob(file_pattern))

    if not snapshot_files:
        print("没有找到任何快照文件，请先运行 extract.py")
        return

    all_data = []

    for file_path in snapshot_files:
        try:
            df = pd.read_csv(file_path)
            snapshot_date = extract_snapshot_date(file_path)
            df["snapshot_date"] = snapshot_date
            all_data.append(df)
            print(f"已读取: {file_path}")
        except Exception as e:
            print(f"读取失败: {file_path}, 错误: {e}")

    if not all_data:
        print("没有可合并的数据")
        return

    history_df = pd.concat(all_data, ignore_index=True)

    # 保留核心字段
    keep_cols = [
        "snapshot_date",
        "id",
        "name",
        "full_name",
        "html_url",
        "description",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "contributors_count",
        "hot_score",
        "language",
        "topics",
        "created_at",
        "updated_at",
        "pushed_at"
    ]

    existing_cols = [col for col in keep_cols if col in history_df.columns]
    history_df = history_df[existing_cols]

    # 去重：同一天同一个仓库只保留一条
    history_df = history_df.drop_duplicates(subset=["snapshot_date", "full_name"])

    # 排序
    history_df = history_df.sort_values(by=["full_name", "snapshot_date"])

    history_file = os.path.join(history_dir, "repo_trend_history.csv")
    history_df.to_csv(history_file, index=False, encoding="utf-8-sig")

    print(f"历史趋势总表已生成: {history_file}")
    print(f"总记录数: {len(history_df)}")


if __name__ == "__main__":
    build_history_table()