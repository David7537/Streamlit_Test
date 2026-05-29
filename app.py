import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #1a1d2e; border-right: 1px solid #2d3055; }
.metric-card {
    background: linear-gradient(135deg, #1e2235 0%, #252840 100%);
    border: 1px solid #3a3f6e;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #7c83fd; margin: 4px 0; }
.metric-label { font-size: 0.8rem; color: #9299b8; text-transform: uppercase; letter-spacing: 1px; }
.metric-delta { font-size: 0.85rem; color: #4ade80; margin-top: 4px; }
section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #c5c9e0;
    margin-bottom: 12px;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label { color: #9299b8 !important; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#7c83fd", "#f7768e", "#9ece6a", "#e0af68", "#bb9af7", "#7dcfff", "#73daca"]
BG      = "#1a1d2e"
PAPER   = "#1e2235"
GRID    = "#2d3055"
TEXT    = "#c5c9e0"

PLOT_LAYOUT = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=BG,
    font_color=TEXT,
    font_family="Inter, sans-serif",
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color=TEXT),
    margin=dict(l=40, r=20, t=40, b=40),
)

# ── Data ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("sellers.xlsx")
    df.columns = [c.strip() for c in df.columns]
    df["FULL NAME"] = df["NAME"] + " " + df["LASTNAME"]
    return df

df = load_data()

# ── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    all_regions = sorted(df["REGION"].unique())
    sel_regions = st.multiselect(
        "Region",
        options=all_regions,
        default=all_regions,
        placeholder="Select regions…",
    )

    income_min, income_max = int(df["INCOME"].min()), int(df["INCOME"].max())
    income_range = st.slider(
        "Income Range",
        min_value=income_min,
        max_value=income_max,
        value=(income_min, income_max),
        step=100,
    )

    units_min, units_max = int(df["SOLD UNITS"].min()), int(df["SOLD UNITS"].max())
    units_range = st.slider(
        "Units Sold Range",
        min_value=units_min,
        max_value=units_max,
        value=(units_min, units_max),
    )

    st.markdown("---")
    st.markdown("## Vendor Lookup")
    vendor_options = ["— Select —"] + sorted(df["FULL NAME"].unique())
    sel_vendor = st.selectbox("Vendor", vendor_options)

    st.markdown("---")
    sort_col = st.selectbox(
        "Sort table by",
        ["TOTAL SALES", "SOLD UNITS", "SALES AVERAGE", "INCOME", "NAME"],
    )
    sort_asc = st.toggle("Ascending", value=False)

# ── Apply filters ────────────────────────────────────────────────────────────
filtered = df[
    (df["REGION"].isin(sel_regions)) &
    (df["INCOME"].between(*income_range)) &
    (df["SOLD UNITS"].between(*units_range))
].sort_values(sort_col, ascending=sort_asc)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# Sales Performance Dashboard")
st.markdown(f"<span style='color:#9299b8;font-size:0.9rem;'>Showing **{len(filtered)}** of **{len(df)}** sellers</span>", unsafe_allow_html=True)
st.markdown("---")

# ── KPI cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, delta=None):
    delta_html = f"<div class='metric-delta'>↑ {delta}</div>" if delta else ""
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value'>{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

kpi(k1, "Total Sellers",    f"{len(filtered)}")
kpi(k2, "Total Units Sold", f"{filtered['SOLD UNITS'].sum():,}")
kpi(k3, "Total Sales",      f"${filtered['TOTAL SALES'].sum():,.0f}")
kpi(k4, "Avg Sales/Seller", f"${filtered['TOTAL SALES'].mean():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
tab_overview, tab_region, tab_vendor, tab_table = st.tabs([
    " Overview", " By Region", " Vendor Detail", " Data Table"
])

# ── TAB 1: Overview charts ────────────────────────────────────────────────────
with tab_overview:
    c1, c2 = st.columns(2)

    # Units sold bar
    with c1:
        fig = px.bar(
            filtered.head(20), x="NAME", y="SOLD UNITS",
            color="REGION", color_discrete_sequence=PALETTE,
            title="Units Sold per Seller (Top 20)",
            labels={"NAME": "Seller", "SOLD UNITS": "Units"},
        )
        fig.update_layout(**PLOT_LAYOUT)
        fig.update_xaxes(tickangle=-45, gridcolor=GRID)
        fig.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig, use_container_width=True)

    # Total Sales scatter
    with c2:
        fig2 = px.scatter(
            filtered, x="SOLD UNITS", y="TOTAL SALES",
            color="REGION", size="INCOME",
            hover_data=["FULL NAME", "INCOME"],
            color_discrete_sequence=PALETTE,
            title="Units Sold vs Total Sales",
            labels={"SOLD UNITS": "Units Sold", "TOTAL SALES": "Total Sales ($)"},
        )
        fig2.update_layout(**PLOT_LAYOUT)
        fig2.update_xaxes(gridcolor=GRID)
        fig2.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig2, use_container_width=True)

    # Sales Average distribution
    fig3 = px.histogram(
        filtered, x="SALES AVERAGE", nbins=20,
        color="REGION", color_discrete_sequence=PALETTE,
        barmode="overlay", opacity=0.75,
        title="Sales Average Distribution",
        labels={"SALES AVERAGE": "Sales Average"},
    )
    fig3.update_layout(**PLOT_LAYOUT)
    fig3.update_xaxes(gridcolor=GRID)
    fig3.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: Region view ────────────────────────────────────────────────────────
with tab_region:
    region_agg = (
        filtered.groupby("REGION")
        .agg(
            Sellers=("ID", "count"),
            Units=("SOLD UNITS", "sum"),
            Total_Sales=("TOTAL SALES", "sum"),
            Avg_Sales=("SALES AVERAGE", "mean"),
            Avg_Income=("INCOME", "mean"),
        )
        .reset_index()
    )

    rc1, rc2 = st.columns(2)

    with rc1:
        fig_pie = px.pie(
            region_agg, names="REGION", values="Total_Sales",
            color_discrete_sequence=PALETTE,
            title="Total Sales Share by Region",
            hole=0.45,
        )
        fig_pie.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    with rc2:
        fig_grp = go.Figure()
        metrics = {"Units Sold": "Units", "Total Sales ($)": "Total_Sales", "Avg Income": "Avg_Income"}
        colors = PALETTE[:3]
        for i, (lbl, col) in enumerate(metrics.items()):
            fig_grp.add_trace(go.Bar(
                name=lbl,
                x=region_agg["REGION"],
                y=region_agg[col],
                marker_color=colors[i],
            ))
        fig_grp.update_layout(
            barmode="group",
            title="Region Comparison",
            **PLOT_LAYOUT,
        )
        fig_grp.update_xaxes(gridcolor=GRID)
        fig_grp.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig_grp, use_container_width=True)

    # Box plots per region
    fig_box = px.box(
        filtered, x="REGION", y="TOTAL SALES",
        color="REGION", color_discrete_sequence=PALETTE,
        title="Total Sales Distribution by Region",
        points="all",
    )
    fig_box.update_layout(**PLOT_LAYOUT)
    fig_box.update_xaxes(gridcolor=GRID)
    fig_box.update_yaxes(gridcolor=GRID)
    st.plotly_chart(fig_box, use_container_width=True)

    # Region summary table
    st.markdown("#### Region Summary")
    fmt = region_agg.copy()
    fmt["Total_Sales"] = fmt["Total_Sales"].map("${:,.0f}".format)
    fmt["Avg_Sales"]   = fmt["Avg_Sales"].map("{:.2%}".format)
    fmt["Avg_Income"]  = fmt["Avg_Income"].map("${:,.0f}".format)
    fmt.columns        = ["Region", "Sellers", "Units Sold", "Total Sales", "Avg Sales %", "Avg Income"]
    st.dataframe(fmt, use_container_width=True, hide_index=True)

# ── TAB 3: Vendor detail ──────────────────────────────────────────────────────
with tab_vendor:
    if sel_vendor == "— Select —":
        st.info(" Select a vendor from the sidebar to view their profile.")
    else:
        vrow = df[df["FULL NAME"] == sel_vendor].iloc[0]
        vregion_df = df[df["REGION"] == vrow["REGION"]]

        st.markdown(f"## {vrow['NAME']} {vrow['LASTNAME']}")
        st.markdown(f"<span style='background:#3a3f6e;padding:4px 12px;border-radius:20px;font-size:0.85rem;color:#c5c9e0;'>🗺️ {vrow['REGION']}</span> &nbsp; <span style='background:#2d4a3e;padding:4px 12px;border-radius:20px;font-size:0.85rem;color:#c5c9e0;'>🆔 {vrow['ID']}</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        vc1, vc2, vc3, vc4 = st.columns(4)
        kpi(vc1, "Income",       f"${vrow['INCOME']:,}")
        kpi(vc2, "Units Sold",   f"{vrow['SOLD UNITS']:,}")
        kpi(vc3, "Total Sales",  f"${vrow['TOTAL SALES']:,}")
        kpi(vc4, "Sales Avg",    f"{vrow['SALES AVERAGE']:.2%}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### How this vendor ranks in their region")

        metrics_rank = ["SOLD UNITS", "TOTAL SALES", "SALES AVERAGE", "INCOME"]
        labels_rank  = ["Units Sold", "Total Sales", "Sales Average", "Income"]

        fig_rank = make_subplots(rows=1, cols=4, subplot_titles=labels_rank)
        for i, (col, lbl) in enumerate(zip(metrics_rank, labels_rank), 1):
            sorted_region = vregion_df.sort_values(col)
            colors_bar = [
                "#7c83fd" if n == sel_vendor else "#2d3055"
                for n in sorted_region["FULL NAME"]
            ]
            fig_rank.add_trace(
                go.Bar(
                    x=sorted_region["FULL NAME"],
                    y=sorted_region[col],
                    marker_color=colors_bar,
                    showlegend=False,
                    name=lbl,
                ),
                row=1, col=i,
            )

        fig_rank.update_layout(height=380, **PLOT_LAYOUT)
        for ax in fig_rank.layout:
            if ax.startswith("xaxis"):
                fig_rank.layout[ax].update(showticklabels=False, gridcolor=GRID)
            if ax.startswith("yaxis"):
                fig_rank.layout[ax].update(gridcolor=GRID)
        st.plotly_chart(fig_rank, use_container_width=True)

        # Percentile badges
        st.markdown("#### Percentile within region")
        p1, p2, p3, p4 = st.columns(4)
        for col_p, label_p, pcol in zip(metrics_rank, labels_rank, [p1, p2, p3, p4]):
            pct = (vregion_df[col_p] <= vrow[col_p]).mean() * 100
            color = "#4ade80" if pct >= 70 else ("#e0af68" if pct >= 40 else "#f7768e")
            pcol.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label_p}</div>
                <div class='metric-value' style='color:{color}'>{pct:.0f}th</div>
                <div style='font-size:0.75rem;color:#9299b8;margin-top:2px;'>percentile</div>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 4: Data Table ─────────────────────────────────────────────────────────
with tab_table:
    st.markdown(f"#### Filtered Dataset — {len(filtered)} rows")

    display_cols = ["REGION", "ID", "FULL NAME", "INCOME", "SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"]
    show_df = filtered[display_cols].copy()
    show_df["INCOME"]        = show_df["INCOME"].map("${:,}".format)
    show_df["TOTAL SALES"]   = show_df["TOTAL SALES"].map("${:,}".format)
    show_df["SALES AVERAGE"] = show_df["SALES AVERAGE"].map("{:.2%}".format)

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "REGION":        st.column_config.TextColumn("Region"),
            "ID":            st.column_config.NumberColumn("ID"),
            "FULL NAME":     st.column_config.TextColumn("Name"),
            "INCOME":        st.column_config.TextColumn("Income"),
            "SOLD UNITS":    st.column_config.NumberColumn("Units Sold"),
            "TOTAL SALES":   st.column_config.TextColumn("Total Sales"),
            "SALES AVERAGE": st.column_config.TextColumn("Sales Avg"),
        },
    )

    # Download button
    csv = filtered.drop(columns=["FULL NAME"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download filtered data as CSV",
        data=csv,
        file_name="sellers_filtered.csv",
        mime="text/csv",
    )
