import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

// = os.getenv("GITHUB_TOKEN")
TOKEN = os.getenv("GH_API_TOKEN") or os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def search_trending_repos(topic="llm", per_page=20, page=1):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"topic:{topic}",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
        "page": page
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()["items"]

    rows = []
    for repo in data:
        rows.append({
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "html_url": repo["html_url"],
            "description": repo["description"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "pushed_at": repo["pushed_at"],
            "stargazers_count": repo["stargazers_count"],
            "forks_count": repo["forks_count"],
            "open_issues_count": repo["open_issues_count"],
            "language": repo["language"],
            "topics": ",".join(repo.get("topics", []))
        })

    return pd.DataFrame(rows)


def get_contributors_count(full_name):
    url = f"https://api.github.com/repos/{full_name}/contributors"
    params = {"per_page": 100}

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"获取 contributors 失败: {full_name}, 状态码: {resp.status_code}")
        return None

    data = resp.json()
    return len(data)


def get_languages_detail(full_name):
    url = f"https://api.github.com/repos/{full_name}/languages"

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"获取 languages 失败: {full_name}, 状态码: {resp.status_code}")
        return None

    data = resp.json()
    return data


def enrich_repo_data(df):
    contributors_list = []
    languages_list = []

    for _, row in df.iterrows():
        full_name = row["full_name"]
        print(f"正在处理: {full_name}")

        contributors_count = get_contributors_count(full_name)
        languages_detail = get_languages_detail(full_name)

        contributors_list.append(contributors_count)
        languages_list.append(str(languages_detail))

    df["contributors_count"] = contributors_list
    df["languages_detail"] = languages_list

    return df


def add_hot_score(df):
    df = df.copy()

    df["contributors_count"] = pd.to_numeric(df["contributors_count"], errors="coerce").fillna(0)

    df["hot_score"] = (
        df["stargazers_count"] * 0.6 +
        df["forks_count"] * 0.3 +
        df["contributors_count"] * 0.1
    )

    return df


def save_daily_snapshot(df, topic="llm"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    snapshot_dir = os.path.join(base_dir, "data", "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)

    today_str = datetime.today().strftime("%Y-%m-%d")
    file_path = os.path.join(snapshot_dir, f"enriched_repos_{topic}_{today_str}.csv")

    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"每日快照已保存: {file_path}")

    return file_path


def run_daily_collection(topic="llm", per_page=20):
    df = search_trending_repos(topic=topic, per_page=per_page, page=1)
    print(df.head())

    df = enrich_repo_data(df)
    df = add_hot_score(df)

    save_daily_snapshot(df, topic=topic)


if __name__ == "__main__":
    run_daily_collection(topic="llm", per_page=20)