import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="GitHub 热门仓库趋势分析看板",
    layout="wide"
)


@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "history", "repo_trend_history.csv")

    if not os.path.exists(file_path):
        st.error(f"数据文件不存在：{file_path}")
        st.stop()

    df = pd.read_csv(file_path)

    # 数值列处理
    numeric_cols = [
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "contributors_count",
        "hot_score"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 时间列处理
    time_cols = ["snapshot_date", "created_at", "updated_at", "pushed_at"]
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 缺失值处理
    if "language" in df.columns:
        df["language"] = df["language"].fillna("Unknown")
    else:
        df["language"] = "Unknown"

    if "contributors_count" in df.columns:
        df["contributors_count"] = df["contributors_count"].fillna(0)
    else:
        df["contributors_count"] = 0

    if "topics" in df.columns:
        df["topics"] = df["topics"].fillna("")
    else:
        df["topics"] = ""

    # 如果历史表里没有 hot_score，就现场补算
    if "hot_score" not in df.columns:
        df["hot_score"] = (
            df["stargazers_count"].fillna(0) * 0.6 +
            df["forks_count"].fillna(0) * 0.3 +
            df["contributors_count"].fillna(0) * 0.1
        )

    return df


def extract_all_topics(df):
    topic_set = set()

    for topics in df["topics"].fillna(""):
        for topic in str(topics).split(","):
            topic = topic.strip()
            if topic:
                topic_set.add(topic)

    return ["All"] + sorted(topic_set)


df = load_data()

# 只展示最新一天的数据
if "snapshot_date" in df.columns and not df["snapshot_date"].isna().all():
    latest_date = df["snapshot_date"].max()
    df = df[df["snapshot_date"] == latest_date].copy()

st.title("GitHub 热门仓库趋势分析看板")
st.markdown("基于 GitHub API、GitHub Actions 与 Streamlit 的热门仓库自动化分析系统")

if "snapshot_date" in df.columns and not df["snapshot_date"].isna().all():
    st.caption(f"当前展示数据日期：{df['snapshot_date'].max().strftime('%Y-%m-%d')}")

# -----------------------------
# 侧边栏筛选
# -----------------------------
st.sidebar.header("筛选条件")

language_list = ["All"] + sorted(df["language"].dropna().unique().tolist())
selected_language = st.sidebar.selectbox("选择主语言", language_list)

topic_list = extract_all_topics(df)
selected_topic = st.sidebar.selectbox("选择 Topic", topic_list)

min_stars = int(df["stargazers_count"].min()) if not df.empty else 0
max_stars = int(df["stargazers_count"].max()) if not df.empty else 0

selected_stars = st.sidebar.slider(
    "Stars 范围",
    min_stars,
    max_stars,
    (min_stars, max_stars)
)

# -----------------------------
# 数据过滤
# -----------------------------
filtered_df = df.copy()

if selected_language != "All":
    filtered_df = filtered_df[filtered_df["language"] == selected_language]

if selected_topic != "All":
    filtered_df = filtered_df[
        filtered_df["topics"].str.contains(selected_topic, case=False, na=False)
    ]

filtered_df = filtered_df[
    (filtered_df["stargazers_count"] >= selected_stars[0]) &
    (filtered_df["stargazers_count"] <= selected_stars[1])
]

if filtered_df.empty:
    st.warning("当前筛选条件下没有数据，请调整筛选条件。")
    st.stop()

# -----------------------------
# 顶部指标
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("仓库数量", len(filtered_df))
col2.metric("总 Stars", f"{int(filtered_df['stargazers_count'].sum()):,}")
col3.metric("总 Forks", f"{int(filtered_df['forks_count'].sum()):,}")
col4.metric("总 Contributors", f"{int(filtered_df['contributors_count'].sum()):,}")
col5.metric("平均热度评分", f"{filtered_df['hot_score'].mean():,.0f}")

st.divider()

# -----------------------------
# Top 10 热门仓库（按 Stars）
# -----------------------------
st.subheader("Top 10 热门仓库（按 Stars）")
top_stars_df = filtered_df.sort_values("stargazers_count", ascending=False).head(10)

fig1 = px.bar(
    top_stars_df,
    x="full_name",
    y="stargazers_count",
    title="Top 10 Repositories by Stars",
    text="stargazers_count",
    hover_data={
        "full_name": True,
        "stargazers_count": ":,",
        "forks_count": ":,",
        "contributors_count": ":,",
        "language": True,
        "topics": True
    }
)
fig1.update_layout(
    xaxis_title="Repository",
    yaxis_title="Stars"
)
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Top 10 热门仓库（按热度评分）
# -----------------------------
st.subheader("Top 10 热门仓库（按热度评分）")
top_hot_df = filtered_df.sort_values("hot_score", ascending=False).head(10)

fig_hot = px.bar(
    top_hot_df,
    x="full_name",
    y="hot_score",
    title="Top 10 Repositories by Hot Score",
    text="hot_score",
    hover_data={
        "full_name": True,
        "hot_score": ":,.0f",
        "stargazers_count": ":,",
        "forks_count": ":,",
        "contributors_count": ":,",
        "language": True
    }
)
fig_hot.update_layout(
    xaxis_title="Repository",
    yaxis_title="Hot Score"
)
fig_hot.update_traces(texttemplate="%{text:.0f}", textposition="outside")
st.plotly_chart(fig_hot, use_container_width=True)

# -----------------------------
# 主语言分布
# -----------------------------
st.subheader("主语言分布")
lang_df = (
    filtered_df["language"]
    .value_counts()
    .head(10)
    .reset_index()
)
lang_df.columns = ["language", "count"]

fig2 = px.pie(
    lang_df,
    names="language",
    values="count",
    title="Top Languages Distribution",
    hole=0.35
)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Top 10 仓库（按 Contributors）
# -----------------------------
st.subheader("Top 10 仓库（按 Contributors）")
top_contrib_df = filtered_df.sort_values("contributors_count", ascending=False).head(10)

fig3 = px.bar(
    top_contrib_df,
    x="full_name",
    y="contributors_count",
    title="Top 10 Repositories by Contributors Count",
    text="contributors_count",
    hover_data={
        "full_name": True,
        "contributors_count": ":,",
        "stargazers_count": ":,",
        "forks_count": ":,",
        "language": True
    }
)
fig3.update_layout(
    xaxis_title="Repository",
    yaxis_title="Contributors Count"
)
fig3.update_traces(textposition="outside")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Stars vs Forks
# -----------------------------
st.subheader("Stars vs Forks")
fig4 = px.scatter(
    filtered_df,
    x="stargazers_count",
    y="forks_count",
    size="contributors_count",
    color="language",
    hover_name="full_name",
    hover_data={
        "stargazers_count": ":,",
        "forks_count": ":,",
        "contributors_count": ":,",
        "hot_score": ":,.0f",
        "topics": True
    },
    title="Stars vs Forks"
)
fig4.update_layout(
    xaxis_title="Stars",
    yaxis_title="Forks"
)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# -----------------------------
# 明细表
# -----------------------------
st.subheader("仓库明细数据")

show_cols = [
    "full_name",
    "stargazers_count",
    "forks_count",
    "open_issues_count",
    "contributors_count",
    "hot_score",
    "language",
    "topics",
    "updated_at"
]

existing_cols = [col for col in show_cols if col in filtered_df.columns]
display_df = filtered_df[existing_cols].sort_values("hot_score", ascending=False).copy()

if "updated_at" in display_df.columns:
    display_df["updated_at"] = pd.to_datetime(display_df["updated_at"], errors="coerce")
    display_df["updated_at"] = display_df["updated_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

st.dataframe(display_df, use_container_width=True)