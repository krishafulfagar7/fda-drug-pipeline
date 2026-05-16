import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

CSV_PATH = "/Users/krishafulfagar/AI-Powered-FDA-Drug-Scraper/data/clean_approvals.csv"

df = pd.read_csv(CSV_PATH)
df["year"] = pd.to_datetime(df["Date of Approval"], format="mixed", errors="coerce").dt.year
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

COLORS = {"bg": "#0a0e1a", "card": "#111827", "border": "#1e2d45", "accent": "#00c9ff", "accent2": "#7b61ff", "text": "#e2e8f0", "muted": "#64748b"}
CHART_COLORS = ["#00c9ff","#7b61ff","#f43f5e","#10b981","#f59e0b","#3b82f6","#ec4899","#14b8a6","#8b5cf6","#ef4444","#06b6d4","#84cc16","#f97316","#a855f7","#22c55e"]
PLOTLY_LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="monospace", color="#e2e8f0", size=12), margin=dict(l=20,r=20,t=40,b=20), legend=dict(bgcolor="rgba(0,0,0,0)"), xaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45"), yaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45"))

app = Dash(__name__)
app.layout = html.Div(style={"background":"#0a0e1a","minHeight":"100vh","padding":"32px","fontFamily":"monospace","color":"#e2e8f0"}, children=[
    html.H1("FDA Drug Approval Dashboard", style={"fontWeight":"800","fontSize":"2rem","marginBottom":"8px"}),
    html.P(f"Analyzing {len(df):,} FDA-approved drugs · openFDA + LLM Classification", style={"color":"#64748b","marginBottom":"32px"}),
    html.Div(style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"16px","marginBottom":"24px"}, children=[
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","borderLeft":"3px solid #00c9ff"}, children=[
            html.Div(id="stat-total", style={"fontSize":"2rem","fontWeight":"800","color":"#00c9ff"}, children=f"{len(df):,}"),
            html.Div("TOTAL APPROVALS", style={"fontSize":"0.65rem","color":"#64748b","letterSpacing":"0.15em","marginTop":"6px"}),
        ]),
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","borderLeft":"3px solid #7b61ff"}, children=[
            html.Div(id="stat-companies", style={"fontSize":"2rem","fontWeight":"800","color":"#7b61ff"}, children=f"{df['Company'].nunique():,}"),
            html.Div("UNIQUE COMPANIES", style={"fontSize":"0.65rem","color":"#64748b","letterSpacing":"0.15em","marginTop":"6px"}),
        ]),
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","borderLeft":"3px solid #10b981"}, children=[
            html.Div(id="stat-years", style={"fontSize":"2rem","fontWeight":"800","color":"#10b981"}, children=str(df["year"].nunique())),
            html.Div("YEARS OF DATA", style={"fontSize":"0.65rem","color":"#64748b","letterSpacing":"0.15em","marginTop":"6px"}),
        ]),
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","borderLeft":"3px solid #f59e0b"}, children=[
            html.Div(id="stat-disease", style={"fontSize":"1.1rem","fontWeight":"800","color":"#f59e0b"}, children=df["disease_type"].mode()[0]),
            html.Div("TOP DISEASE AREA", style={"fontSize":"0.65rem","color":"#64748b","letterSpacing":"0.15em","marginTop":"6px"}),
        ]),
    ]),
    html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","marginBottom":"16px"}, children=[
        html.P("FILTER BY YEAR", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"12px"}),
        dcc.RangeSlider(id="year-slider", min=df["year"].min(), max=df["year"].max(), step=1, value=[df["year"].min(), df["year"].max()],
            marks={int(y): {"label":str(int(y)),"style":{"color":"#64748b","fontSize":"0.7rem"}} for y in sorted(df["year"].unique())}),
    ]),
    html.Div(style={"display":"grid","gridTemplateColumns":"2fr 1fr","gap":"16px","marginBottom":"16px"}, children=[
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px"}, children=[
            html.P("APPROVALS OVER TIME", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"8px"}),
            dcc.Graph(id="timeline-chart", style={"height":"260px"}, config={"displayModeBar":False}),
        ]),
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px"}, children=[
            html.P("DRUG TYPE BREAKDOWN", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"8px"}),
            dcc.Graph(id="drug-type-pie", style={"height":"260px"}, config={"displayModeBar":False}),
        ]),
    ]),
    html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"16px","marginBottom":"16px"}, children=[
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px"}, children=[
            html.P("APPROVALS BY DISEASE AREA", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"8px"}),
            dcc.Graph(id="disease-bar", style={"height":"320px"}, config={"displayModeBar":False}),
        ]),
        html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px"}, children=[
            html.P("TOP 10 COMPANIES BY APPROVALS", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"8px"}),
            dcc.Graph(id="company-bar", style={"height":"320px"}, config={"displayModeBar":False}),
        ]),
    ]),
    html.Div(style={"background":"#111827","border":"1px solid #1e2d45","borderRadius":"12px","padding":"20px","marginBottom":"16px"}, children=[
        html.P("DISEASE AREA × DRUG TYPE MATRIX", style={"color":"#64748b","fontSize":"0.65rem","letterSpacing":"0.15em","marginBottom":"8px"}),
        dcc.Graph(id="heatmap", style={"height":"320px"}, config={"displayModeBar":False}),
    ]),
    html.P("Data: openFDA Drug Applications API · Classification: LLaMA 3.3 via Groq", style={"color":"#2d3f5a","fontSize":"0.65rem","textAlign":"center","marginTop":"16px"}),
])

@app.callback(
    Output("stat-total","children"), Output("stat-companies","children"),
    Output("stat-years","children"), Output("stat-disease","children"),
    Output("timeline-chart","figure"), Output("drug-type-pie","figure"),
    Output("disease-bar","figure"), Output("company-bar","figure"),
    Output("heatmap","figure"),
    Input("year-slider","value"),
)
def update_all(year_range):
    f = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    if len(f) == 0:
        empty = go.Figure()
        empty.update_layout(**PLOTLY_LAYOUT)
        return "0","0","0","N/A",empty,empty,empty,empty,empty

    tl = f.groupby("year").size().reset_index(name="count")
    fig_tl = go.Figure(go.Scatter(x=tl["year"], y=tl["count"], mode="lines+markers",
        line=dict(color="#00c9ff",width=2), marker=dict(color="#00c9ff",size=7),
        fill="tozeroy", fillcolor="rgba(0,201,255,0.08)"))
    fig_tl.update_layout(**PLOTLY_LAYOUT)

    dc = f["drug_type"].value_counts().head(8)
    fig_pie = go.Figure(go.Pie(labels=dc.index, values=dc.values, hole=0.55,
        marker=dict(colors=CHART_COLORS), textfont=dict(size=10)))
    fig_pie.update_layout(**PLOTLY_LAYOUT)

    dis = f["disease_type"].value_counts().reset_index()
    dis.columns = ["disease","count"]
    fig_dis = go.Figure(go.Bar(x=dis["count"], y=dis["disease"], orientation="h",
        marker=dict(color=dis["count"], colorscale=[[0,"#1e2d45"],[1,"#00c9ff"]])))
    fig_dis.update_layout(**PLOTLY_LAYOUT, yaxis=dict(autorange="reversed",gridcolor="#1e2d45"))

    co = f["Company"].value_counts().head(10).reset_index()
    co.columns = ["company","count"]
    fig_co = go.Figure(go.Bar(x=co["count"], y=co["company"], orientation="h",
        marker=dict(color=co["count"], colorscale=[[0,"#1e2d45"],[1,"#7b61ff"]])))
    fig_co.update_layout(**PLOTLY_LAYOUT, yaxis=dict(autorange="reversed",gridcolor="#1e2d45"))

    heat = f.groupby(["disease_type","drug_type"]).size().unstack(fill_value=0)
    fig_heat = go.Figure(go.Heatmap(z=heat.values, x=heat.columns.tolist(), y=heat.index.tolist(),
        colorscale=[[0,"#0a0e1a"],[0.5,"#1e3a5f"],[1,"#00c9ff"]], showscale=True))
    fig_heat.update_layout(**PLOTLY_LAYOUT)

    return (f"{len(f):,}", f"{f['Company'].nunique():,}", str(year_range[1]-year_range[0]+1),
            f["disease_type"].mode()[0], fig_tl, fig_pie, fig_dis, fig_co, fig_heat)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
