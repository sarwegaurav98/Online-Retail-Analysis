"""
UCI Online Retail – Streamlit Analytics Dashboard
Run: streamlit run dashboard.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Online Retail Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark-mode friendly Plotly template ────────────────────────────────────────
TEMPLATE = "plotly_dark"

def fig_layout(fig, height=400, **kwargs):
    """Apply consistent dark-mode layout to any figure."""
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E0E0"),
        margin=dict(l=10, r=10, t=40, b=10),
        **kwargs
    )
    return fig

# ── Load data ──────────────────────────────────────────────────────────────────
OUTPUT = os.path.join(os.path.dirname(__file__), "output")

@st.cache_data
def load_data():
    monthly  = pd.read_csv(f"{OUTPUT}/monthly_revenue.csv")
    country  = pd.read_csv(f"{OUTPUT}/country_revenue.csv")
    top10    = pd.read_csv(f"{OUTPUT}/top10_products.csv")
    rfm      = pd.read_csv(f"{OUTPUT}/rfm_segments.csv")
    cohort   = pd.read_csv(f"{OUTPUT}/cohort_retention.csv")
    ret_prod = pd.read_csv(f"{OUTPUT}/returns_by_product.csv")
    ret_ctry = pd.read_csv(f"{OUTPUT}/returns_by_country.csv")
    ret_sum  = pd.read_csv(f"{OUTPUT}/returns_summary.csv")
    pareto   = pd.read_csv(f"{OUTPUT}/pareto_customers.csv")
    churn    = pd.read_csv(f"{OUTPUT}/churn_summary.csv")
    log      = pd.read_csv(f"{OUTPUT}/data_quality_log.csv")
    return monthly, country, top10, rfm, cohort, ret_prod, ret_ctry, ret_sum, pareto, churn, log

(monthly, country, top10, rfm, cohort,
 ret_prod, ret_ctry, ret_sum, pareto, churn, log) = load_data()

# RFM segment summary
rfm_seg = (rfm.groupby("Segment")
              .agg(Customers=("CustomerID","count"),
                   Total_Revenue=("Monetary","sum"),
                   Avg_Recency=("Recency","mean"),
                   Avg_Frequency=("Frequency","mean"))
              .reset_index()
              .sort_values("Total_Revenue", ascending=False)
              .round(2))
rfm_seg["Revenue_Share_Pct"] = (
    rfm_seg["Total_Revenue"] / rfm_seg["Total_Revenue"].sum() * 100
).round(1)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Online Retail")
    st.markdown("**UCI Dataset · Dec 2010 – Dec 2011**")
    st.divider()
    page = st.radio("Navigate", [
        "📊 Executive Summary",
        "📈 Revenue & Seasonality",
        "🌍 Country Analysis",
        "👥 Customer Segmentation",
        "🔄 Cohort Retention",
        "↩️ Returns Analysis",
        "🧹 Data Quality",
    ])
    st.divider()
    st.caption("Data: UCI ML Repository · Online Retail")

# ── Segment colour palette ─────────────────────────────────────────────────────
SEG_COLORS = {
    "Champions":           "#2ECC71",
    "Loyal Customers":     "#3498DB",
    "At Risk":             "#E67E22",
    "Lost":                "#E74C3C",
    "New Customers":       "#9B59B6",
    "Potential Loyalists": "#1ABC9C",
    "Others":              "#95A5A6",
}

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 – EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary")
    st.markdown("**UCI Online Retail Dataset** · Dec 2010 – Dec 2011 · 541,909 raw transactions")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Revenue",    "£10,253,975")
    c2.metric("Total Orders",     "19,776")
    c3.metric("Avg Order Value",  "£518.51")
    c4.metric("Unique Customers", "4,334")
    c5.metric("Return Rate",      "7.76%")
    c6.metric("Churn Rate",       "33.4%")
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Monthly Revenue Trend")
        fig = px.bar(monthly, x="YearMonth", y="Revenue",
                     color_discrete_sequence=["#3498DB"],
                     labels={"YearMonth": "Month", "Revenue": "Revenue (£)"},
                     text_auto=".3s")
        fig.add_trace(go.Scatter(
            x=monthly["YearMonth"], y=monthly["AOV"],
            mode="lines+markers", name="AOV (£)", yaxis="y2",
            line=dict(color="#E74C3C", width=2), marker=dict(size=6)
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", title="AOV (£)",
                        showgrid=False, color="#E74C3C"),
            yaxis_title="Revenue (£)", showlegend=True,
            legend=dict(orientation="h", y=1.08)
        )
        fig_layout(fig, height=370)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue by Segment")
        fig2 = px.pie(rfm_seg, values="Total_Revenue", names="Segment",
                      color="Segment", color_discrete_map=SEG_COLORS, hole=0.45)
        fig2.update_traces(textposition="inside", textinfo="percent+label",
                           textfont_size=11)
        fig2.update_layout(showlegend=False)
        fig_layout(fig2, height=370)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Top 10 Products by Revenue")
        fig3 = px.bar(top10.sort_values("Revenue"), x="Revenue", y="Description",
                      orientation="h", color_discrete_sequence=["#2ECC71"],
                      labels={"Revenue": "Revenue (£)", "Description": ""},
                      text_auto=".3s")
        fig3.update_layout(yaxis=dict(tickfont=dict(size=10)))
        fig_layout(fig3, height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Revenue by Country (Top 10)")
        top_ctry = country.head(10).sort_values("Revenue")
        fig4 = px.bar(top_ctry, x="Revenue", y="Country", orientation="h",
                      color="Revenue", color_continuous_scale="Blues",
                      text_auto=".3s",
                      labels={"Revenue": "Revenue (£)", "Country": ""})
        fig4.update_coloraxes(showscale=False)
        fig_layout(fig4, height=380)
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 – REVENUE & SEASONALITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Revenue & Seasonality":
    st.title("📈 Revenue Performance & Seasonality")

    st.subheader("Monthly Revenue, Orders & AOV")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=monthly["YearMonth"], y=monthly["Revenue"],
                name="Revenue (£)", marker_color="#3498DB")
    fig.add_scatter(x=monthly["YearMonth"], y=monthly["Orders"],
                    mode="lines+markers", name="Orders",
                    line=dict(color="#E74C3C", width=2.5),
                    marker=dict(size=8), secondary_y=True)
    fig.update_yaxes(title_text="Revenue (£)", secondary_y=False, gridcolor="#444")
    fig.update_yaxes(title_text="Orders", secondary_y=True, showgrid=False,
                     tickfont=dict(color="#E74C3C"))
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    fig_layout(fig, height=400)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Month-over-Month Growth (%)")
        mom = monthly.dropna(subset=["MoM_Growth_Pct"]).copy()
        mom["color"] = mom["MoM_Growth_Pct"].apply(
            lambda x: "#2ECC71" if x >= 0 else "#E74C3C"
        )
        fig2 = go.Figure(go.Bar(
            x=mom["YearMonth"], y=mom["MoM_Growth_Pct"],
            marker_color=mom["color"],
            text=[f"{v:.1f}%" for v in mom["MoM_Growth_Pct"]],
            textposition="outside"
        ))
        fig2.update_layout(yaxis_title="MoM Growth (%)", showlegend=False)
        fig_layout(fig2, height=360)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Monthly Detail Table")
        disp = monthly[["YearMonth","Revenue","Orders","Units","AOV","MoM_Growth_Pct"]].copy()
        disp.columns = ["Month","Revenue (£)","Orders","Units","AOV (£)","MoM %"]
        disp["Revenue (£)"] = disp["Revenue (£)"].map("£{:,.0f}".format)
        disp["AOV (£)"]     = disp["AOV (£)"].map("£{:,.2f}".format)
        disp["MoM %"]       = disp["MoM %"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=380)

    st.subheader("🔑 Seasonality Highlights")
    hi1, hi2, hi3 = st.columns(3)
    hi1.info("📈 **Peak:** Nov 2011 – £1,453,263 (2,751 orders)")
    hi2.warning("📉 **Trough:** Feb 2011 – £507,998 (1,093 orders)")
    hi3.success("🗓️ **Sep–Nov** = ~36% of annual revenue")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 – COUNTRY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Country Analysis":
    st.title("🌍 Country Revenue Analysis")

    n_countries = st.slider("Show top N countries", 5, 38, 15)
    top_n = country.head(n_countries).copy()
    log_scale = st.checkbox("Log scale (better for non-UK comparison)", value=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Revenue – Top {n_countries} Countries")
        fig = px.bar(top_n.sort_values("Revenue"), x="Revenue", y="Country",
                     orientation="h",
                     color="Revenue", color_continuous_scale="Blues",
                     text_auto=".3s",
                     labels={"Revenue": "Revenue (£)", "Country": ""},
                     log_x=log_scale)
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, height=max(380, n_countries * 28))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue Share (Top 5 + Others)")
        # Group into top 5 + Others for a readable pie
        top5 = top_n.head(5).copy()
        others_rev = top_n.iloc[5:]["Revenue"].sum()
        if others_rev > 0:
            import numpy as np
            others_row = pd.DataFrame([{"Country": "Others", "Revenue": others_rev}])
            pie_df = pd.concat([top5[["Country","Revenue"]], others_row], ignore_index=True)
        else:
            pie_df = top5[["Country","Revenue"]]
        fig2 = px.pie(pie_df, values="Revenue", names="Country",
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig2.update_traces(textposition="inside", textinfo="percent+label",
                           textfont_size=12, pull=[0.05] + [0]*len(pie_df))
        fig2.update_layout(showlegend=True,
                           legend=dict(orientation="v", x=1, y=0.5))
        fig_layout(fig2, height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader(f"Country Revenue Table (Top {n_countries})")
    disp = top_n[["Country","Revenue","Orders","Units","Revenue_Share_Pct"]].copy()
    disp.columns = ["Country","Revenue (£)","Orders","Units","Share %"]
    disp["Revenue (£)"] = disp["Revenue (£)"].map("£{:,.0f}".format)
    disp["Share %"]     = disp["Share %"].map("{:.2f}%".format)
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.info("🇬🇧 **UK = 85.1%** of revenue (£8.7M). "
            "Netherlands 2.8%, EIRE 2.7%, Germany 2.0%, France 1.8%.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 – CUSTOMER SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customer Segmentation":
    st.title("👥 RFM Customer Segmentation")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", "4,334")
    col2.metric("Champions",       "956  (22%)")
    col3.metric("Churned (>90d)",  "1,449  (33.4%)")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Segment Overview", "Pareto Analysis", "Individual RFM"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Revenue by Segment")
            fig = px.bar(rfm_seg, x="Segment", y="Total_Revenue",
                         color="Segment", color_discrete_map=SEG_COLORS,
                         text_auto=".3s",
                         labels={"Total_Revenue": "Total Revenue (£)", "Segment": ""})
            fig.update_layout(showlegend=False, xaxis_tickangle=-20)
            fig_layout(fig, height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Recency vs Frequency (bubble = revenue)")
            fig2 = px.scatter(rfm_seg, x="Avg_Recency", y="Avg_Frequency",
                              size="Total_Revenue", color="Segment",
                              color_discrete_map=SEG_COLORS,
                              hover_data=["Customers", "Total_Revenue"],
                              size_max=60,
                              labels={"Avg_Recency": "Avg Recency (days)",
                                      "Avg_Frequency": "Avg Frequency (orders)"})
            fig_layout(fig2, height=380)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Segment Summary")
        seg_disp = rfm_seg.copy()
        seg_disp["Total_Revenue"]  = seg_disp["Total_Revenue"].map("£{:,.0f}".format)
        seg_disp["Avg_Recency"]    = seg_disp["Avg_Recency"].map("{:.0f} days".format)
        seg_disp["Avg_Frequency"]  = seg_disp["Avg_Frequency"].map("{:.1f}".format)
        seg_disp["Revenue_Share_Pct"] = seg_disp["Revenue_Share_Pct"].map("{:.1f}%".format)
        seg_disp.columns = ["Segment", "Customers", "Total Revenue",
                            "Avg Recency", "Avg Frequency", "Rev Share %"]
        st.dataframe(seg_disp, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Pareto Curve – Cumulative Revenue vs Customer %")
        fig3 = px.line(pareto, x="Customer_Pct", y="Cumulative_Revenue_Pct",
                       color_discrete_sequence=["#3498DB"],
                       labels={"Customer_Pct": "Cumulative Customer %",
                               "Cumulative_Revenue_Pct": "Cumulative Revenue %"})
        fig3.add_hline(y=80, line_dash="dash", line_color="#E74C3C",
                       annotation_text="80% Revenue", annotation_position="right")
        fig3.add_vline(x=26.1, line_dash="dash", line_color="#2ECC71",
                       annotation_text="26.1% of customers",
                       annotation_position="top right")
        fig_layout(fig3, height=440)
        st.plotly_chart(fig3, use_container_width=True)
        st.success("**Top 26.1% of customers generate 80% of revenue** — classic Pareto concentration.")

    with tab3:
        st.subheader("Individual Customer RFM Scores")
        seg_filter = st.multiselect("Filter by Segment",
                                    options=sorted(rfm["Segment"].unique()),
                                    default=sorted(rfm["Segment"].unique()))
        rfm_filtered = rfm[rfm["Segment"].isin(seg_filter)]
        st.dataframe(
            rfm_filtered[["CustomerID","Recency","Frequency","Monetary",
                           "R_Score","F_Score","M_Score","RFM_Score","Segment"]]
            .head(500).reset_index(drop=True),
            use_container_width=True, hide_index=True
        )
        st.caption(f"Showing up to 500 of {len(rfm_filtered):,} filtered customers")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 – COHORT RETENTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Cohort Retention":
    st.title("🔄 Cohort Retention Analysis")

    churn_vals = {r["Metric"]: r["Value"] for _, r in churn.iterrows()}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",    str(int(float(churn_vals.get("Total Customers", 4334)))))
    c2.metric("Churned (>90 days)", f"{int(float(churn_vals.get('Churned (>90 days)', 1449)))}  ({churn_vals.get('Churn Rate (%)', 33.4)}%)")
    c3.metric("Active (≤90 days)",  str(int(float(churn_vals.get("Active (<=90 days)", 2885)))))
    c4.metric("Snapshot Date",      str(churn_vals.get("Snapshot Date", "2011-12-10")))
    st.divider()

    st.subheader("Monthly Cohort Retention Heatmap (%)")
    month_cols = [c for c in cohort.columns if c.startswith("Month_")]
    cohort_plot = cohort.set_index("CohortMonth")[month_cols].astype(float)
    cohort_plot.columns = [f"+{c.replace('Month_','')}" for c in month_cols]

    fig = px.imshow(cohort_plot,
                    color_continuous_scale="RdYlGn",
                    aspect="auto", zmin=0, zmax=100,
                    text_auto=".1f",
                    labels=dict(x="Months since first purchase",
                                y="Cohort Month", color="Retention %"))
    fig.update_traces(textfont_size=11)
    fig.update_coloraxes(colorbar_title="Retention %")
    fig_layout(fig, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Month-1 Retention by Cohort")
    month1 = cohort[["CohortMonth","Month_1"]].dropna().copy()
    month1.columns = ["Cohort","Month 1 Retention %"]
    fig2 = px.bar(month1, x="Cohort", y="Month 1 Retention %",
                  color="Month 1 Retention %",
                  color_continuous_scale="Blues",
                  text_auto=".1f")
    fig2.update_coloraxes(showscale=False)
    fig_layout(fig2, height=340)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.info("📌 **Dec 2010 cohort** best retention: **36.5%** at month 1")
    col2.warning("📉 Later cohorts: month-1 drops to **~17%**")
    col3.success("🔁 **Overall avg month-1: ~21%**")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 – RETURNS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "↩️ Returns Analysis":
    st.title("↩️ Returns & Revenue Lost")

    ret_vals = {r["Metric"]: r["Value"] for _, r in ret_sum.iterrows()}
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Return Transactions", f"{int(float(ret_vals.get('Total Return Transactions', 10624))):,}")
    c2.metric("Units Returned",      f"{int(float(ret_vals.get('Total Units Returned', 484531))):,}")
    c3.metric("Revenue Lost",        f"£{float(ret_vals.get('Total Revenue Lost (£)', 896812)):,.0f}")
    c4.metric("Forward Revenue",     f"£{float(ret_vals.get('Total Forward Revenue (£)', 10666684)):,.0f}")
    c5.metric("Return Rate",         f"{float(ret_vals.get('Return Rate (%)', 7.76)):.2f}%")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue Lost by Country (Top 15)")
        top_ret = ret_ctry.head(15).sort_values("Revenue_Lost")
        fig = px.bar(top_ret, x="Revenue_Lost", y="Country", orientation="h",
                     color="Revenue_Lost", color_continuous_scale="Reds",
                     text_auto=".3s",
                     labels={"Revenue_Lost": "Revenue Lost (£)", "Country": ""})
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, height=440)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 15 Products by Revenue Lost")
        top_rp = ret_prod.sort_values("Revenue_Lost", ascending=False).head(15)
        fig2 = px.bar(top_rp.sort_values("Revenue_Lost"), x="Revenue_Lost",
                      y="Description", orientation="h",
                      color="Revenue_Lost", color_continuous_scale="Oranges",
                      text_auto=".3s",
                      labels={"Revenue_Lost": "Revenue Lost (£)", "Description": ""})
        fig2.update_coloraxes(showscale=False)
        fig2.update_layout(yaxis=dict(tickfont=dict(size=10)))
        fig_layout(fig2, height=440)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Return Volume vs Revenue Lost by Country")
    # Exclude UK outlier for a readable chart; add a toggle
    exclude_uk = st.checkbox("Exclude UK (outlier) for better readability", value=True)
    scatter_df = ret_ctry[ret_ctry["Country"] != "United Kingdom"] if exclude_uk else ret_ctry
    fig3 = px.scatter(scatter_df,
                      x="Return_Transactions", y="Revenue_Lost",
                      size="Units_Returned", color="Country",
                      hover_name="Country",
                      size_max=50,
                      labels={"Return_Transactions": "Return Transactions",
                              "Revenue_Lost": "Revenue Lost (£)"})
    fig3.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="white")))
    fig_layout(fig3, height=420)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 – DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧹 Data Quality":
    st.title("🧹 Data Cleaning Log")
    st.markdown("Every row-removal step logged with counts and percentage dropped.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Raw Rows",     "541,909")
    c2.metric("Rows Removed", f"{int(log['rows_dropped'].sum()):,}")
    c3.metric("Cleaned Rows", "391,283")
    st.divider()

    st.subheader("Rows Dropped per Cleaning Step")
    fig = px.bar(log, x="rows_dropped", y="step", orientation="h",
                 color="pct_dropped", color_continuous_scale="Reds",
                 text_auto=True,
                 labels={"rows_dropped": "Rows Dropped",
                         "step": "Step", "pct_dropped": "% Dropped"})
    fig.update_coloraxes(colorbar_title="% Dropped")
    fig.update_layout(yaxis=dict(tickfont=dict(size=11)))
    fig_layout(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detailed Cleaning Log")
    log_disp = log.copy()
    log_disp.columns = ["Step","Rows Before","Rows After","Rows Dropped","% Dropped","Description"]
    st.dataframe(log_disp, use_container_width=True, hide_index=True)

    st.subheader("Key Issues Found")
    issues = [
        ("Missing CustomerID",           "135,080 rows (24.9%) – excluded from RFM/cohort only"),
        ("Return invoices (starts 'C')",  "9,288 rows – moved to returns analysis"),
        ("Missing Description",           "1,454 rows – dropped"),
        ("Non-product codes",             "2,241 rows – POST, M, DOT, AMAZONFEE, etc."),
        ("Zero/negative UnitPrice",       "1,051 rows – dropped"),
        ("Exact duplicates",              "5,221 rows – deduplicated"),
    ]
    for title, detail in issues:
        st.markdown(f"- **{title}:** {detail}")
