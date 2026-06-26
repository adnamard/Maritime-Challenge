"""
Maritime Operations Performance Dashboard
Senior BI / Datathon-grade revision
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
# Fix: orjson circular import bug on some Windows Python 3.12 environments
pio.json.config.default_engine = "json"
 
 
# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Maritime Ops Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────
NAVY      = "#0F2044"
BLUE      = "#1A4B8C"
ACCENT    = "#E8501A"
LIGHT     = "#F4F7FB"   # page background
WHITE     = "#FFFFFF"   # cards / callouts
CHART_BG  = "#EDF1F7"   # plot area – visibly distinct from page & cards
MUTED     = "#64748B"
BORDER    = "#D1D9E6"
SUCCESS   = "#16A34A"
WARN      = "#D97706"

PLOTLY_TEMPLATE = "plotly_white"
CHART_COLORS    = [BLUE, ACCENT, "#3B82F6", "#10B981", "#F59E0B"]

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* ── Layout ── */
.main {{ background-color: {LIGHT}; }}
.block-container {{ padding: 1.5rem 2.5rem 3rem; max-width: 1400px; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {NAVY};
}}
[data-testid="stSidebar"] * {{
    color: #CBD5E1 !important;
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: {BLUE} !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: {WHITE} !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

/* ── Metric cards ── */
.kpi-card {{
    background: {WHITE};
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border-top: 4px solid {BLUE};
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}}
.kpi-label {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {MUTED};
    margin-bottom: 0.4rem;
}}
.kpi-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {NAVY};
    line-height: 1;
}}
.kpi-delta {{
    font-size: 0.8rem;
    margin-top: 0.3rem;
    color: {MUTED};
}}
.kpi-accent {{ border-top-color: {ACCENT}; }}

/* ── Section header ── */
.section-eyebrow {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {ACCENT};
    margin-bottom: 0.2rem;
}}
.section-title {{
    font-size: 1.35rem;
    font-weight: 700;
    color: {NAVY};
    margin-bottom: 0.25rem;
}}
.section-body {{
    font-size: 0.875rem;
    color: {MUTED};
    line-height: 1.6;
    margin-bottom: 0rem;
}}

/* ── Insight / callout ── */
.callout {{
    background: {WHITE};
    border-left: 4px solid {BLUE};
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 0;
}}
.callout-warn {{ border-left-color: {ACCENT}; }}
.callout-label {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {MUTED};
    margin-bottom: 0.35rem;
}}
.callout-text {{
    font-size: 0.88rem;
    color: {NAVY};
    line-height: 1.55;
}}

/* ── Divider ── */
.hr {{ border-top: 1px solid {BORDER}; margin: 2rem 0; }}

/* ── Finding badge ── */
.badge {{
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 4px;
}}
.badge-confirmed {{ background: #DCFCE7; color: #15803D; }}
.badge-null {{ background: #FEF9C3; color: #92400E; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("final_dataset.csv")
    df["date_id"] = pd.to_datetime(df["date_id"])
    # Ordered categorical for suez_period
    suez_order = ["Pre-Suez", "During-Suez", "Post-Suez", "Normal"]
    df["suez_period"] = pd.Categorical(df["suez_period"], categories=suez_order, ordered=True)
    return df


df = load_data()


# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='padding:1rem 0 0.5rem'><span style='color:{WHITE};font-size:1.1rem;font-weight:700'>🚢 Maritime Ops</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Filters")

    selected_region = st.multiselect(
        "Regional Hub",
        options=sorted(df["regional_hub"].unique()),
        default=sorted(df["regional_hub"].unique()),
    )
    selected_vessel = st.multiselect(
        "Vessel Category",
        options=sorted(df["vessel_category"].unique()),
        default=sorted(df["vessel_category"].unique()),
    )
    selected_year = st.multiselect(
        "Fiscal Year",
        options=sorted(df["fiscal_year"].unique()),
        default=sorted(df["fiscal_year"].unique()),
    )

    st.markdown("---")
    st.markdown(
"""
<div style="text-align:center; color:#64748B; font-size:0.82rem; line-height:1.7;">

Data: 2021–2024 • 15,000 Cargo Movements • 50 Global Terminals

<br>

Developed by <b>Dea Ramanda</b> |
Data Analyst • Machine Learning Enthusiast

<br>

<a href="https://github.com/adnamard" target="_blank">GitHub</a>
&nbsp;&nbsp;•&nbsp;&nbsp;
<a href="https://linkedin.com/in/adnamard" target="_blank">LinkedIn</a>

</div>
""",
unsafe_allow_html=True
)


# ─────────────────────────────────────────
# FILTERED DATA
# ─────────────────────────────────────────
fdf = df[
    df["regional_hub"].isin(selected_region)
    & df["vessel_category"].isin(selected_vessel)
    & df["fiscal_year"].isin(selected_year)
].copy()


# ─────────────────────────────────────────
# HELPER: chart defaults
# ─────────────────────────────────────────
def style_fig(fig, height=320):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=8, r=16, t=40, b=8),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,   # sama dengan plot area — tidak ada "frame" putih
        font=dict(family="Inter", size=12, color=NAVY),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=NAVY, size=11),
        ),
        xaxis=dict(
            showgrid=True, gridcolor="#C8D3E3", gridwidth=1,
            linecolor="#A0AFCA", zerolinecolor="#A0AFCA",
            tickfont=dict(color=NAVY),
            title_font=dict(color=NAVY),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#C8D3E3", gridwidth=1,
            linecolor="#A0AFCA", zerolinecolor="#A0AFCA",
            tickfont=dict(color=NAVY),
            title_font=dict(color=NAVY),
        ),
        title_font=dict(color=NAVY, size=13, family="Inter"),
    )
    return fig


# ─────────────────────────────────────────
# ── HEADER
# ─────────────────────────────────────────
st.markdown(f"""
<div style="padding:1.5rem 0 1rem">
  <div class="section-eyebrow">Executive Operations Review · 2021–2024</div>
  <div style="font-size:1.9rem;font-weight:800;color:{NAVY};line-height:1.2">
    Maritime Operations<br>Performance Dashboard
  </div>
  <div class="section-body" style="margin-top:0.5rem;max-width:680px">
    Operational analysis across 50 terminals and 4 regional hubs.
    Covers the 2021 Suez Canal disruption and identifies bottlenecks
    on the path to a 15 % reduction in cargo movement time.
  </div>
</div>
<div class="hr"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# ── KPI ROW
# ─────────────────────────────────────────
median_dur   = fdf["move_duration"].median()
total_mvmt   = len(fdf)
n_terminals  = fdf["terminal_name"].nunique()
worst        = fdf.groupby("terminal_name")["move_duration"].median().max()
best         = fdf.groupby("terminal_name")["move_duration"].median().min()
perf_gap_pct = (worst - best) / best * 100

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card kpi-accent">
      <div class="kpi-label">Median Move Duration</div>
      <div class="kpi-value">{median_dur:.0f}</div>
      <div class="kpi-delta">minutes · all movements</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Total Movements</div>
      <div class="kpi-value">{total_mvmt:,}</div>
      <div class="kpi-delta">cargo moves analysed</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Terminals</div>
      <div class="kpi-value">{n_terminals}</div>
      <div class="kpi-delta">active terminals</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Terminal Performance Gap</div>
      <div class="kpi-value">{perf_gap_pct:.0f}%</div>
      <div class="kpi-delta">worst vs best terminal</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SECTION 1 – SUEZ DISRUPTION TIMELINE
# ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">Section 1 · External Shock</div>
<div class="section-title">Did the Suez Disruption Leave a Footprint?</div>
<div class="section-body">
  The Ever Given grounded on 23 March 2021, blocking the canal for six days.
  Movement duration is the primary signal of operational stress.
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([5, 5], gap="large")

with col_left:
    # Bar: median by suez_period (ordered)
    suez_agg = (
        fdf.groupby("suez_period", observed=True)["move_duration"]
        .median()
        .reset_index()
        .sort_values("suez_period")
    )
    suez_agg["color"] = suez_agg["suez_period"].apply(
        lambda x: ACCENT if x == "During-Suez" else BLUE
    )
    fig = go.Figure(go.Bar(
        x=suez_agg["suez_period"].astype(str),
        y=suez_agg["move_duration"],
        marker_color=suez_agg["color"],
        text=suez_agg["move_duration"].round(0).astype(int),
        textposition="outside",
        textfont=dict(size=12, color=NAVY, family="Inter"),
    ))
    during_val = suez_agg.loc[suez_agg["suez_period"] == "During-Suez", "move_duration"].values
    normal_val = suez_agg.loc[suez_agg["suez_period"] == "Normal", "move_duration"].values
    if len(during_val) and len(normal_val):
        uplift = (during_val[0] - normal_val[0]) / normal_val[0] * 100
        fig.add_annotation(
            x="During-Suez", y=during_val[0] + 20,
            text=f"+{uplift:.1f}% vs Normal",
            showarrow=False,
            font=dict(color=ACCENT, size=11, family="Inter"),
        )
    fig.update_layout(
        title="Median Move Duration by Disruption Phase",
        yaxis_title="Minutes (median)",
        yaxis_range=[0, (suez_agg["move_duration"].max() * 1.2)],
        xaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(style_fig(fig, 300), use_container_width=True)

    st.markdown(f"""
    <div class="callout callout-warn" style="margin-top:0">
      <div class="callout-label">⚠ Caveat — small sample</div>
      <div class="callout-text">
        Only <strong>78 records</strong> fall in the During-Suez window.
        Treat the uplift figure as directional, not statistically precise.
        Hypothesis H7 is <span class="badge badge-confirmed">Confirmed directionally</span>
      </div>
    </div>""", unsafe_allow_html=True)

with col_right:
    # Line chart: monthly trend with vline
    monthly = (
        fdf.groupby(["fiscal_year", "month"])["move_duration"]
        .median()
        .reset_index()
    )
    monthly["period"] = pd.to_datetime(
        monthly["fiscal_year"].astype(str) + "-" + monthly["month"].astype(str)
    )
    monthly = monthly.sort_values("period")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["period"],
        y=monthly["move_duration"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=5, color=BLUE),
        name="Median Duration",
    ))
    suez_ts = pd.Timestamp("2021-03-23").timestamp() * 1000
    fig.add_vline(
        x=suez_ts,
        line_dash="dash",
        line_color=ACCENT,
    )
    fig.add_annotation(
        x=suez_ts,
        y=1,
        yref="paper",
        text="Ever Given grounds",
        showarrow=False,
        xanchor="left",
        font=dict(color=ACCENT, size=11, family="Inter"),
    )
    fig.update_layout(
        title="Monthly Median Move Duration (2021–2024)",
        yaxis_title="Minutes (median)",
        xaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(style_fig(fig, 300), use_container_width=True)

    st.markdown(f"""
    <div class="callout" style="margin-top:0">
      <div class="callout-label">Key Reading</div>
      <div class="callout-text">
        Duration is broadly stable across 2021–2024, suggesting operations
        absorbed the disruption without lasting structural change.
        This limits the disruption's strategic weight and shifts focus
        to persistent terminal-level inefficiencies.
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SECTION 2 – REGIONAL EXPOSURE
# ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">Section 2 · Geographic Exposure</div>
<div class="section-title">Which Regions Felt It Most?</div>
<div class="section-body">
  EMEA sits closest to the Suez Canal. Hypothesis H6 predicts it absorbs
  the largest disruption impact.
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([5, 5], gap="large")

with col_left:
    region_agg = (
        fdf.groupby(["regional_hub", "suez_period"], observed=True)["move_duration"]
        .median()
        .reset_index()
        .sort_values("suez_period")
    )
    fig = px.bar(
        region_agg,
        x="regional_hub",
        y="move_duration",
        color="suez_period",
        barmode="group",
        color_discrete_sequence=CHART_COLORS,
        labels={"move_duration": "Median Minutes", "regional_hub": "", "suez_period": "Period"},
        title="Median Move Duration by Region & Phase",
    )
    fig.update_layout(legend_title="")
    st.plotly_chart(style_fig(fig, 340), use_container_width=True)

with col_right:
    # Compute lift: During-Suez vs Pre-Suez per region
    pivot = (
        fdf.groupby(["regional_hub", "suez_period"], observed=True)["move_duration"]
        .median()
        .unstack("suez_period")
        .reset_index()
    )
    if "During-Suez" in pivot.columns and "Pre-Suez" in pivot.columns:
        pivot["disruption_lift"] = (
            (pivot["During-Suez"] - pivot["Pre-Suez"]) / pivot["Pre-Suez"] * 100
        )
        pivot_sorted = pivot.sort_values("disruption_lift", ascending=True)
        fig2 = go.Figure(go.Bar(
            x=pivot_sorted["disruption_lift"],
            y=pivot_sorted["regional_hub"],
            orientation="h",
            marker_color=[ACCENT if v > 0 else SUCCESS for v in pivot_sorted["disruption_lift"]],
            text=[f"{v:+.1f}%" for v in pivot_sorted["disruption_lift"]],
            textposition="outside",
            textfont=dict(color=NAVY, size=12, family="Inter"),
        ))
        max_abs = max(abs(pivot_sorted["disruption_lift"].max()), abs(pivot_sorted["disruption_lift"].min()))
        fig2.update_layout(
            title="Disruption Impact: During vs Pre-Suez (%)",
            xaxis_title="% change in median duration",
            xaxis_range=[-(max_abs * 1.4), max_abs * 1.4],
            yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(style_fig(fig2, 340), use_container_width=True)
    else:
        st.info("Insufficient data for disruption lift chart with current filters.")

st.markdown(f"""
<div class="callout callout-warn" style="max-width:100%">
  <div class="callout-label">Finding · H6 <span class="badge badge-confirmed">Confirmed</span></div>
  <div class="callout-text">
    AMER and EMEA show the largest During-Suez lifts. However, the effect is transient —
    Post-Suez durations fall <em>below</em> pre-crisis levels in all regions,
    suggesting adaptive re-routing provided a temporary efficiency gain after the blockage cleared.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SECTION 3 – TERMINAL BOTTLENECKS (highest executive value)
# ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">Section 3 · Operational Bottlenecks</div>
<div class="section-title">Where Are the Persistent Delays?</div>
<div class="section-body">
  Terminal identity is the strongest differentiator in this dataset.
  The gap between the slowest and fastest terminal is <strong>30 %</strong>.
  Closing even half of that gap delivers the target 15 % reduction.
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([5, 5], gap="large")

with col_left:
    # Top 10 worst with benchmark line
    term_med = (
        fdf.groupby("terminal_name")["move_duration"]
        .median()
        .reset_index()
        .sort_values("move_duration", ascending=False)
    )
    top10_worst = term_med.head(10)
    overall_median = fdf["move_duration"].median()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10_worst["move_duration"],
        y=top10_worst["terminal_name"],
        orientation="h",
        marker_color=ACCENT,
        text=top10_worst["move_duration"].round(0).astype(int),
        textposition="outside",
        textfont=dict(color=NAVY, size=12, family="Inter"),
    ))
    fig.add_shape(
        type="line",
        x0=overall_median, x1=overall_median,
        y0=0, y1=1,
        yref="paper",
        line=dict(color=BLUE, dash="dot", width=1.5),
    )
    fig.add_annotation(
        x=overall_median,
        y=0.98,
        yref="paper",
        text=f"Fleet avg {overall_median:.0f}",
        showarrow=False,
        xanchor="right",
        font=dict(color=BLUE, size=11, family="Inter"),
    )
    fig.update_layout(
        title="10 Slowest Terminals · Median Move Duration",
        xaxis_title="Minutes",
        xaxis_range=[0, top10_worst["move_duration"].max() * 1.18],
        yaxis_title="",
        showlegend=False,
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style_fig(fig, 360), use_container_width=True)

with col_right:
    # Distribution: box per terminal top10 vs bottom10 — replaced with scatter of all terminals
    term_med["quartile"] = pd.qcut(term_med["move_duration"], 4,
                                    labels=["Q1 Best", "Q2", "Q3", "Q4 Worst"])
    term_med["color"] = term_med["quartile"].map({
        "Q1 Best": SUCCESS, "Q2": BLUE, "Q3": WARN, "Q4 Worst": ACCENT
    })

    fig2 = go.Figure()
    for q, color in [("Q1 Best", SUCCESS), ("Q2", BLUE), ("Q3", WARN), ("Q4 Worst", ACCENT)]:
        subset = term_med[term_med["quartile"] == q]
        fig2.add_trace(go.Box(
            y=subset["move_duration"],
            name=q,
            marker_color=color,
            boxmean=True,
            showlegend=True,
        ))
    fig2.update_layout(
        title="Terminal Performance Distribution by Quartile",
        yaxis_title="Median Move Duration (min)",
        showlegend=True,
    )
    st.plotly_chart(style_fig(fig2, 360), use_container_width=True)

st.markdown(f"""
<div class="callout callout-warn" style="max-width:100%">
  <div class="callout-label">Strategic Implication · H4 <span class="badge badge-confirmed">Confirmed</span></div>
  <div class="callout-text">
    Q4 terminals average <strong>~535 min</strong> vs <strong>~460 min</strong> for Q1.
    Reallocating cargo from the bottom decile to Q1 terminals — or initiating
    targeted operational reviews at Q4 terminals — is the single highest-leverage intervention
    available. No other variable in the dataset approaches this explanatory power.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SECTION 4 – FACTORS WITH LIMITED IMPACT
# ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">Section 4 · Hypothesis Validation</div>
<div class="section-title">What Doesn't Drive Delays?</div>
<div class="section-body">
  Ruling out false leads is as valuable as confirming real ones.
  None of the vessel or operational variables below produced
  a meaningful effect on move duration.
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    vc_agg = (
        fdf.groupby("vessel_category")["move_duration"]
        .median()
        .reset_index()
        .sort_values("move_duration")
    )
    fig = px.bar(
        vc_agg,
        x="move_duration",
        y="vessel_category",
        orientation="h",
        color_discrete_sequence=[BLUE],
        title="Vessel Category",
        labels={"move_duration": "Median (min)", "vessel_category": ""},
        text="move_duration",
    )
    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(color=NAVY, size=12, family="Inter"),
    )
    fig.update_layout(
        showlegend=False,
        xaxis_range=[0, vc_agg["move_duration"].max() * 1.2],
    )
    st.plotly_chart(style_fig(fig, 260), use_container_width=True)
    st.markdown(f"""
    <div class="callout">
      <div class="callout-label">H2 <span class="badge badge-null">Not Confirmed</span></div>
      <div class="callout-text">Range ≈ 25 min across four categories. Not operationally significant.</div>
    </div>""", unsafe_allow_html=True)

with col2:
    ab_order = ["New (<5yr)", "Modern (5-15yr)", "Mature (16-30yr)", "Old (>30yr)"]
    ab_agg = (
        fdf.groupby("age_bucket")["move_duration"]
        .median()
        .reindex(ab_order)
        .reset_index()
    )
    fig = px.bar(
        ab_agg,
        x="move_duration",
        y="age_bucket",
        orientation="h",
        color_discrete_sequence=[BLUE],
        title="Vessel Age Bucket",
        labels={"move_duration": "Median (min)", "age_bucket": ""},
        text="move_duration",
    )
    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(color=NAVY, size=12, family="Inter"),
    )
    fig.update_layout(
        showlegend=False,
        xaxis_range=[0, ab_agg["move_duration"].max() * 1.2],
    )
    st.plotly_chart(style_fig(fig, 260), use_container_width=True)
    st.markdown(f"""
    <div class="callout">
      <div class="callout-label">H1 <span class="badge badge-null">Not Confirmed</span></div>
      <div class="callout-text">Vessel age shows no consistent directional relationship with duration.</div>
    </div>""", unsafe_allow_html=True)

with col3:
    shift_agg = (
        fdf.groupby("shift")["move_duration"]
        .median()
        .reset_index()
    )
    fig = px.bar(
        shift_agg,
        x="move_duration",
        y="shift",
        orientation="h",
        color_discrete_sequence=[BLUE],
        title="Shift Schedule",
        labels={"move_duration": "Median (min)", "shift": ""},
        text="move_duration",
    )
    fig.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(color=NAVY, size=12, family="Inter"),
    )
    fig.update_layout(
        showlegend=False,
        xaxis_range=[0, shift_agg["move_duration"].max() * 1.2],
    )
    st.plotly_chart(style_fig(fig, 260), use_container_width=True)
    st.markdown(f"""
    <div class="callout">
      <div class="callout-label">H5 <span class="badge badge-null">Not Confirmed</span></div>
      <div class="callout-text">Night shift is marginally <em>faster</em> than day — contrary to the hypothesis.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SECTION 5 – OPTIMISATION ROADMAP
# ─────────────────────────────────────────
st.markdown("""
<div class="section-eyebrow">Section 5 · Path to 15 % Reduction</div>
<div class="section-title">Optimisation Roadmap</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(f"""
    <div class="callout callout-warn">
      <div class="callout-label">🔴 Immediate · Terminal Reallocation</div>
      <div class="callout-text">
        Audit the 10 worst terminals. Quantify whether delays stem from
        infrastructure, staffing, or process. Even a 10 % reduction at
        these terminals moves the fleet median by ≈4 %.
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="callout">
      <div class="callout-label">🟡 Near-Term · EMEA Contingency Plans</div>
      <div class="callout-text">
        EMEA absorbs the sharpest disruption spikes. Pre-approved alternative
        routing protocols and buffer capacity agreements can cut peak-event
        duration increases by an estimated 5–8 %.
      </div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="callout">
      <div class="callout-label">🟢 Ongoing · Duration as a Risk KPI</div>
      <div class="callout-text">
        Move duration is a leading indicator that spiked before downstream
        congestion was visible. Embed it in weekly operations reviews as
        an early-warning metric.
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# RAW DATA EXPLORER
# ─────────────────────────────────────────
with st.expander("📋 Raw Data Explorer", expanded=False):
    st.dataframe(
        fdf.sort_values("move_duration", ascending=False),
        use_container_width=True,
        height=400,
    )
    st.caption(f"{len(fdf):,} records shown · sorted by move duration descending")
