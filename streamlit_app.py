import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FDA Drug Approval Dashboard", page_icon="💊", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/clean_approvals.csv")
    df["year"] = pd.to_datetime(df["Date of Approval"], format="mixed", errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

st.title("💊 FDA Drug Approval Intelligence")
st.caption(f"Analyzing {len(df):,} FDA-approved drugs · openFDA API + LLaMA 3.3 Classification")

st.sidebar.header("Filters")
years = sorted(df["year"].unique())
year_range = st.sidebar.select_slider("Year Range", options=years, value=(min(years), max(years)))
drug_types = ["All"] + sorted(df["drug_type"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Drug Type", drug_types)

f = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
if selected_type != "All":
    f = f[f["drug_type"] == selected_type]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Approvals", f"{len(f):,}")
col2.metric("Unique Companies", f"{f['Company'].nunique():,}")
col3.metric("Drug Types", f"{f['drug_type'].nunique()}")
col4.metric("Top Disease Area", f["disease_type"].mode()[0] if len(f) > 0 else "N/A")

st.divider()

col_a, col_b = st.columns([2, 1])
with col_a:
    st.subheader("Approvals Over Time")
    tl = f.groupby("year").size().reset_index(name="count")
    st.plotly_chart(px.area(tl, x="year", y="count", color_discrete_sequence=["#00c9ff"]), use_container_width=True)

with col_b:
    st.subheader("Drug Type Breakdown")
    dc = f["drug_type"].value_counts().head(8)
    st.plotly_chart(px.pie(values=dc.values, names=dc.index, hole=0.55), use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.subheader("Approvals by Disease Area")
    dis = f["disease_type"].value_counts().reset_index()
    dis.columns = ["disease", "count"]
    st.plotly_chart(px.bar(dis, x="count", y="disease", orientation="h", color="count", color_continuous_scale=["#1e2d45","#00c9ff"]), use_container_width=True)

with col_d:
    st.subheader("Top 10 Companies")
    co = f["Company"].value_counts().head(10).reset_index()
    co.columns = ["company", "count"]
    st.plotly_chart(px.bar(co, x="count", y="company", orientation="h", color="count", color_continuous_scale=["#1e2d45","#7b61ff"]), use_container_width=True)

st.subheader("Disease Area × Drug Type Matrix")
heat = f.groupby(["disease_type","drug_type"]).size().unstack(fill_value=0)
st.plotly_chart(px.imshow(heat, color_continuous_scale=["#0a0e1a","#1e3a5f","#00c9ff"], aspect="auto"), use_container_width=True)

st.caption("Data: openFDA · Classification: LLaMA 3.3 via Groq")
