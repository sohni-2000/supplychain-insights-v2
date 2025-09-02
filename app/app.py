# app/app.py — Supply Chain Insights (ASCII-only)

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Optional

# ------------------------------------------------------------------------------
# Page setup
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Supply Chain Insights", layout="wide")

# Project paths
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "outputs"
DATA = BASE / "data"

# Core artifacts
SEGMENTS_CSV = OUT / "customer_segments.csv"
PROFILE_CSV = OUT / "segment_profile.csv"
TRAIN_CSV = DATA / "train.csv"

# Optional EDA artifacts
EDA_CAT_CSV = OUT / "sales_by_category.csv"
EDA_REG_CSV = OUT / "sales_by_region.csv"
EDA_MTH_CSV = OUT / "sales_by_month.csv"

# Optional Prophet forecast artifact
FORECAST_CSV = OUT / "forecast_prophet.csv"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def fmt_mtime(p: Path) -> str:
    """Return human-readable modified time or 'missing'."""
    try:
        ts = datetime.fromtimestamp(p.stat().st_mtime)
        return ts.strftime("%a %b %d %H:%M:%S %Y")
    except FileNotFoundError:
        return "missing"

@st.cache_data(show_spinner=False)
def read_csv_if_exists(p: Path) -> Optional[pd.DataFrame]:
    if p.exists():
        try:
            return pd.read_csv(p)
        except Exception:
            return None
    return None

def monthly_actuals_from_train(train_df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Build monthly actuals (ds,y) from raw orders."""
    if train_df is None or train_df.empty:
        return None

    # detect date and sales columns
    date_col = None
    for c in train_df.columns:
        lc = c.lower().strip()
        if lc in ("order date", "order_date", "date"):
            date_col = c
            break

    sales_col = None
    for c in train_df.columns:
        lc = c.lower().strip()
        if lc in ("sales", "revenue", "amount"):
            sales_col = c
            break

    if date_col is None or sales_col is None:
        return None

    tmp = train_df[[date_col, sales_col]].copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    tmp["ds"] = tmp[date_col].dt.to_period("M").dt.to_timestamp()
    m = tmp.groupby("ds", as_index=False)[sales_col].sum().rename(columns={sales_col: "y"})
    return m

def forecast_band_from_prophet(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Return Prophet-style forecast (ds,yhat,yhat_lower,yhat_upper) if valid."""
    need = ["ds", "yhat", "yhat_lower", "yhat_upper"]
    if df is None or df.empty or not all(c in df.columns for c in need):
        return None
    f = df.copy()
    f["ds"] = pd.to_datetime(f["ds"], errors="coerce")
    f = f.dropna(subset=["ds"])
    return f[need]

def simple_rolling_forecast(m_actuals: pd.DataFrame, months: int = 3) -> pd.DataFrame:
    """Fallback forecast: mean of last 6 months with +/-5% bounds."""
    tail = m_actuals.dropna(subset=["y"]).tail(6)
    baseline = float(tail["y"].mean()) if not tail.empty else float(m_actuals["y"].mean())
    start = m_actuals["ds"].max()
    future_idx = pd.date_range(start=start + pd.offsets.MonthBegin(), periods=months, freq="MS")
    out = pd.DataFrame({
        "ds": future_idx,
        "yhat": baseline,
        "yhat_lower": baseline * 0.95,
        "yhat_upper": baseline * 1.05,
    })
    return out

def file_tile(p: Path, label: str, key_prefix: str):
    """Neat file card for the right panel."""
    with st.container(border=True):
        st.caption(label)
        st.code(str(p).replace("\\", "/"))
        st.caption(fmt_mtime(p))
        if p.exists():
            st.download_button(
                "Download",
                data=p.read_bytes(),
                file_name=p.name,
                mime="text/csv",
                use_container_width=True,
                key=f"{key_prefix}-dl",
            )
        else:
            st.button("Missing", disabled=True, use_container_width=True, key=f"{key_prefix}-missing")

# ------------------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------------------
cust = read_csv_if_exists(SEGMENTS_CSV)
profile = read_csv_if_exists(PROFILE_CSV)
train = read_csv_if_exists(TRAIN_CSV)

eda_cat = read_csv_if_exists(EDA_CAT_CSV)
eda_reg = read_csv_if_exists(EDA_REG_CSV)
eda_mth = read_csv_if_exists(EDA_MTH_CSV)

forecast_raw = read_csv_if_exists(FORECAST_CSV)
forecast_df = forecast_band_from_prophet(forecast_raw)

monthly_actuals = eda_mth if eda_mth is not None else monthly_actuals_from_train(train)

# ------------------------------------------------------------------------------
# Layout: main vs right panel
# ------------------------------------------------------------------------------
left, right = st.columns([7, 3], gap="large")

with right:
    st.markdown("### Project files")
    if st.button("Reload data", use_container_width=True, key="reload-right"):
        st.cache_data.clear()
        st.rerun()

    file_tile(SEGMENTS_CSV, "Customer segments", "seg")
    file_tile(PROFILE_CSV, "Segment profiles", "prof")
    file_tile(TRAIN_CSV, "Raw orders (train.csv)", "train")
    file_tile(EDA_CAT_CSV, "EDA: sales by category", "eda-cat")
    file_tile(EDA_REG_CSV, "EDA: sales by region", "eda-reg")
    file_tile(EDA_MTH_CSV, "EDA: sales by month", "eda-mth")
    file_tile(FORECAST_CSV, "Forecast (Prophet)", "fc-prophet")

with left:
    st.title("Supply Chain Insights")

    tab_overview, tab_customers, tab_profiles, tab_eda, tab_forecast, tab_help = st.tabs(
        ["Overview", "Customers", "Profiles", "EDA", "Forecasting", "Help"]
    )

    # ---------------------------- Overview ----------------------------
    with tab_overview:
        c1, c2, c3 = st.columns(3)
        n_customers = None if cust is None else len(cust)
        total_sales = None
        total_orders = None

        if cust is not None:
            ts_col = next((c for c in cust.columns if c.lower() in ("total_sales", "sales")), None)
            if ts_col:
                total_sales = float(cust[ts_col].sum())
            oc_col = next((c for c in cust.columns if c.lower() in ("order_count", "orders")), None)
            if oc_col:
                total_orders = int(cust[oc_col].sum())

        c1.metric("Customers", "-" if n_customers is None else n_customers)
        c2.metric("Total Sales", "-" if total_sales is None else f"{total_sales:,.0f}")
        c3.metric("Orders", "-" if total_orders is None else f"{total_orders:,}")

        st.divider()
        st.subheader("Customer Share by Segment")

        if cust is None or cust.empty:
            st.info("Place outputs/customer_segments.csv to show this chart.")
        else:
            seg_col = next((c for c in cust.columns if c.lower() in ("segment", "label")), None)
            if seg_col is None:
                st.warning("Could not find a segment column in customer_segments.csv")
            else:
                seg_counts = cust.groupby(seg_col, as_index=False).size().rename(columns={"size": "customers"})
                fig = px.bar(seg_counts, x=seg_col, y="customers", title="Customer Share by Segment")
                st.plotly_chart(fig, use_container_width=True)

    # ---------------------------- Customers (with filters) ----------------------------
    with tab_customers:
        st.subheader("Explore Customers")
        if cust is None or cust.empty:
            st.info("Place outputs/customer_segments.csv to enable this tab.")
        else:
            df = cust.copy()

            seg_col = next((c for c in df.columns if c.lower() in ("segment", "label")), None)
            id_col = next((c for c in df.columns if c.lower() in ("customer_id", "customer id", "id")), None)
            last_order_col = next((c for c in df.columns if c.lower() in ("last_order", "last order", "order_date", "order date")), None)
            rec_col = next((c for c in df.columns if c.lower() in ("recency_days", "recency", "days_since")), None)

            c1f, c2f, c3f, c4f = st.columns([1.2, 1.4, 1.4, 1.4])

            # Segment selector
            if seg_col:
                seg_opts = ["All"] + sorted([str(x) for x in df[seg_col].dropna().unique()])
                seg_choice = c1f.selectbox("Segment", seg_opts, index=0)
            else:
                seg_choice = "All"
                c1f.write("")

            # Recency slider
            if rec_col and pd.api.types.is_numeric_dtype(df[rec_col]):
                rmin = int(max(0, df[rec_col].min()))
                rmax = int(max(rmin, df[rec_col].max()))
                rec_range = c2f.slider("Recency (days)", rmin, rmax, (rmin, rmax))
            else:
                rec_range = (None, None)
                c2f.write("")

            # Sales range
            sales_col = next((c for c in df.columns if c.lower() in ("total_sales", "sales")), None)
            if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
                smin = float(df[sales_col].min())
                smax = float(df[sales_col].max())
                sales_range = c3f.slider("Total sales filter", float(smin), float(smax), (float(smin), float(smax)))
            else:
                sales_range = (None, None)
                c3f.write("")

            # Search
            search_id = c4f.text_input("Search Customer ID")

            # Apply filters
            if seg_choice != "All" and seg_col:
                df = df[df[seg_col].astype(str) == seg_choice]
            if rec_range[0] is not None and rec_col:
                df = df[(df[rec_col] >= rec_range[0]) & (df[rec_col] <= rec_range[1])]
            if sales_range[0] is not None and sales_col:
                df = df[(df[sales_col] >= sales_range[0]) & (df[sales_col] <= sales_range[1])]
            if search_id.strip() and id_col:
                df = df[df[id_col].astype(str).str.contains(search_id.strip(), case=False, na=False)]

            if last_order_col:
                try:
                    df[last_order_col] = pd.to_datetime(df[last_order_col], errors="coerce").dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

            st.dataframe(df, use_container_width=True, height=520)

    # ---------------------------- Profiles ----------------------------
    with tab_profiles:
        st.subheader("Segment Profiles")
        if profile is None or profile.empty:
            st.info("Place outputs/segment_profile.csv to enable this tab.")
        else:
            st.dataframe(profile, use_container_width=True, height=520)

    # ---------------------------- EDA (interactive) ----------------------------
    with tab_eda:
        st.subheader("Exploratory Analysis")

        mode = st.radio("View", ["By Category", "By Region", "Monthly"], horizontal=True)

        # CATEGORY
        if mode == "By Category":
            cat = eda_cat
            if cat is None and train is not None and not train.empty:
                cat_col = next((c for c in train.columns if c.lower() == "category"), None)
                sal_col = next((c for c in train.columns if c.lower() in ("sales", "revenue", "amount")), None)
                if cat_col and sal_col:
                    tmp = train[[cat_col, sal_col]].copy()
                    cat = tmp.groupby(cat_col, as_index=False)[sal_col].sum().rename(
                        columns={sal_col: "total_sales", cat_col: "category"}
                    )
            if cat is None or cat.empty:
                st.info("Provide sales_by_category.csv or a train.csv with Category and Sales.")
            else:
                ccol = "category" if "category" in cat.columns else next((c for c in cat.columns if c.lower()=="category"), cat.columns[0])
                scol = "total_sales" if "total_sales" in cat.columns else next((c for c in cat.columns if c.lower() in ("total_sales","sales","revenue")), cat.columns[1])
                opts = ["All"] + sorted([str(x) for x in cat[ccol].dropna().unique()])
                pick = st.selectbox("Category filter", opts, index=0, key="eda_cat_pick")
                plot_df = cat if pick == "All" else cat[cat[ccol].astype(str) == pick]
                fig = px.bar(plot_df, x=ccol, y=scol, title="Total Sales by Category")
                st.plotly_chart(fig, use_container_width=True)

        # REGION
        if mode == "By Region":
            reg = eda_reg
            if reg is None and train is not None and not train.empty:
                reg_col = next((c for c in train.columns if c.lower() == "region"), None)
                sal_col = next((c for c in train.columns if c.lower() in ("sales", "revenue", "amount")), None)
                if reg_col and sal_col:
                    tmp = train[[reg_col, sal_col]].copy()
                    reg = tmp.groupby(reg_col, as_index=False)[sal_col].sum().rename(
                        columns={sal_col: "total_sales", reg_col: "region"}
                    )
            if reg is None or reg.empty:
                st.info("Provide sales_by_region.csv or a train.csv with Region and Sales.")
            else:
                rcol = "region" if "region" in reg.columns else next((c for c in reg.columns if c.lower()=="region"), reg.columns[0])
                scol = "total_sales" if "total_sales" in reg.columns else next((c for c in reg.columns if c.lower() in ("total_sales","sales","revenue")), reg.columns[1])
                opts = ["All"] + sorted([str(x) for x in reg[rcol].dropna().unique()])
                pick = st.selectbox("Region filter", opts, index=0, key="eda_reg_pick")
                plot_df = reg if pick == "All" else reg[reg[rcol].astype(str) == pick]
                fig = px.bar(plot_df, x=rcol, y=scol, title="Total Sales by Region")
                st.plotly_chart(fig, use_container_width=True)

        # MONTHLY
        if mode == "Monthly":
            m = eda_mth if eda_mth is not None else monthly_actuals_from_train(train)
            if m is None or m.empty:
                st.info("Provide sales_by_month.csv or a train.csv with Order Date and Sales.")
            else:
                dfm = m.copy()
                if "ds" not in dfm.columns:
                    if len(dfm.columns) >= 2:
                        dfm.columns = ["ds", "y"] + list(dfm.columns[2:])
                dfm["ds"] = pd.to_datetime(dfm["ds"], errors="coerce")
                dfm = dfm.dropna(subset=["ds"]).sort_values("ds")

                min_d, max_d = dfm["ds"].min().date(), dfm["ds"].max().date()
                dr = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="eda_date_range")
                if isinstance(dr, tuple) and len(dr) == 2:
                    dfm = dfm[(dfm["ds"] >= pd.to_datetime(dr[0])) & (dfm["ds"] <= pd.to_datetime(dr[1]))]

                fig = px.line(dfm, x="ds", y="y", markers=True, title="Monthly Sales")
                st.plotly_chart(fig, use_container_width=True)

    # ---------------------------- Forecasting (interactive) ----------------------------
    with tab_forecast:
        st.subheader("Monthly sales: actuals and forecast")

        colA, colB = st.columns([1, 1])
        horizon = colA.slider("Horizon (months, fallback forecast)", 1, 12, 3, key="fc_horizon")
        show_band = colB.checkbox("Show forecast band", value=True, key="fc_band")

        fig = None
        # Actuals
        if monthly_actuals is not None and not monthly_actuals.empty:
            dfm = monthly_actuals.copy()
            dfm["ds"] = pd.to_datetime(dfm["ds"], errors="coerce")
            dfm = dfm.dropna(subset=["ds"]).sort_values("ds")
            fig = px.line(dfm, x="ds", y="y", title="", markers=True)
            fig.update_traces(name="Actuals", showlegend=True)

        # Forecast (Prophet if available; else simple rolling)
        f = forecast_df
        if f is None and monthly_actuals is not None and not monthly_actuals.empty:
            f = simple_rolling_forecast(monthly_actuals, months=horizon)

        if f is not None and not f.empty:
            f = f.copy()
            f["ds"] = pd.to_datetime(f["ds"], errors="coerce")
            f = f.dropna(subset=["ds"]).sort_values("ds")

            f_line = px.line(f, x="ds", y="yhat", markers=True)
            f_line.update_traces(line_color="red", name="Forecast")
            if fig is None:
                fig = f_line
            else:
                for tr in f_line.data:
                    fig.add_trace(tr)

            if show_band and all(c in f.columns for c in ["yhat_lower", "yhat_upper"]):
                lo = px.line(f, x="ds", y="yhat_lower"); lo.update_traces(showlegend=True, name="Forecast band", line=dict(width=0))
                hi = px.line(f, x="ds", y="yhat_upper"); hi.update_traces(showlegend=False, line=dict(width=0))
                for tr in lo.data + hi.data:
                    fig.add_trace(tr)

        if fig is None:
            st.info("Provide monthly actuals and/or forecast to see the chart.")
        else:
            st.plotly_chart(fig, use_container_width=True, height=520)

    # ---------------------------- Help ----------------------------
    with tab_help:
        st.subheader("How this dashboard works")
        help_lines = [
            "**Inputs**",
            "- outputs/customer_segments.csv - per-customer features and segment labels",
            "- outputs/segment_profile.csv - per-segment rollups",
            "- data/train.csv - raw orders for EDA and monthly actuals",
            "- outputs/forecast_prophet.csv - optional forecast (Prophet)",
            "",
            "**Typical notebook pipeline**",
            "cust.to_csv('outputs/customer_segments.csv', index=False)",
            "profile.to_csv('outputs/segment_profile.csv', index=False)",
            "sales_by_category.to_csv('outputs/sales_by_category.csv', index=False)",
            "sales_by_region.to_csv('outputs/sales_by_region.csv', index=False)",
            "sales_by_month.to_csv('outputs/sales_by_month.csv', index=False)",
            "forecast[['ds','yhat','yhat_lower','yhat_upper']].to_csv('outputs/forecast_prophet.csv', index=False)",
            "",
            "**Refresh**",
            "- Click Reload data in the right panel.",
            "- If still stale: menu -> Clear cache, then Rerun.",
        ]
        st.markdown("\n".join(help_lines))