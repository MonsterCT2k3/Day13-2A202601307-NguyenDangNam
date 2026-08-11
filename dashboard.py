import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import yaml
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Day 13 AI Observability Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .status-pass {
        color: #16A34A;
        font-weight: 600;
    }
    .status-fail {
        color: #DC2626;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Path definitions
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "dashboard.yaml"
DEFAULT_LOGS_PATH = BASE_DIR / "data" / "logs.jsonl"

@st.cache_data(ttl=5)
def load_config():
    if not CONFIG_PATH.exists():
        st.error(f"Config file not found at {CONFIG_PATH}")
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("dashboard", {})

@st.cache_data(ttl=2)
def load_logs(file_path):
    path = Path(file_path)
    if not path.exists():
        return pd.DataFrame()
    
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                records.append(data)
            except json.JSONDecodeError:
                continue
                
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame(records)
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df

# Header section
config = load_config()
title = config.get("title", "Day 13 AI Observability")
st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">System Metrics, Latency, Traffic, Cost, Tokens & Quality Dashboard</div>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("⚙️ Settings & Controls")
log_file = st.sidebar.text_input("Log file path", value=str(DEFAULT_LOGS_PATH))

time_range_min = st.sidebar.slider(
    "Time Range (minutes)",
    min_value=5,
    max_value=180,
    value=config.get("time_range_minutes", 60),
    step=5
)

refresh_rate = st.sidebar.number_input(
    "Refresh Rate (seconds)",
    min_value=5,
    max_value=60,
    value=config.get("refresh_seconds", 30),
    step=5
)

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

if auto_refresh:
    time.sleep(0.01) # Yield control briefly
    st.markdown(f"""
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {refresh_rate * 1000});
        </script>
    """, unsafe_allow_html=True)

if st.sidebar.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.rerun()

# Load log data
df = load_logs(log_file)

if df.empty or "ts" not in df.columns:
    st.warning(f"No log data found or log file empty at `{log_file}`.")
    st.stop()

# Time filtering
max_ts = df["ts"].max()
min_ts = max_ts - timedelta(minutes=time_range_min)
df_filtered = df[df["ts"] >= min_ts].copy()

st.sidebar.markdown(f"**Data Window:** {min_ts.strftime('%H:%M:%S')} - {max_ts.strftime('%H:%M:%S')} UTC")
st.sidebar.markdown(f"**Total Events in Window:** `{len(df_filtered)}`")

# Helper function to check thresholds
def render_threshold_badge(current_val, operator, threshold_val, unit=""):
    passed = False
    if operator == "lte":
        passed = current_val <= threshold_val
        symbol = "≤"
    elif operator == "gte":
        passed = current_val >= threshold_val
        symbol = "≥"
        
    badge_class = "status-pass" if passed else "status-fail"
    status_text = "PASS" if passed else "ALERT / THRESHOLD BREACH"
    st.markdown(
        f'<span class="{badge_class}">[{status_text}] Target: {symbol} {threshold_val} {unit} (Actual: {current_val:.2f})</span>',
        unsafe_allow_html=True
    )

panels = {p["id"]: p for p in config.get("panels", [])}

# Layout: 2 Columns x 3 Rows for 6 panels
col1, col2 = st.columns(2)

# --- PANEL 1: LATENCY PERCENTILES ---
with col1:
    st.subheader("1. Latency Percentiles (ms)")
    panel_config = panels.get("latency", {})
    df_lat = df_filtered[df_filtered["event"] == "response_sent"].dropna(subset=["latency_ms"]).copy()
    
    if not df_lat.empty:
        p50 = df_lat["latency_ms"].quantile(0.50)
        p95 = df_lat["latency_ms"].quantile(0.95)
        p99 = df_lat["latency_ms"].quantile(0.99)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("P50 Latency", f"{p50:.1f} ms")
        m2.metric("P95 Latency", f"{p95:.1f} ms")
        m3.metric("P99 Latency", f"{p99:.1f} ms")
        
        thresh = panel_config.get("threshold", {})
        render_threshold_badge(p95, thresh.get("operator", "lte"), thresh.get("value", 3000), "ms")
        
        # Time series chart
        df_lat["minute"] = df_lat["ts"].dt.floor("1min")
        lat_grouped = df_lat.groupby("minute")["latency_ms"].agg(
            P50=lambda x: x.quantile(0.50),
            P95=lambda x: x.quantile(0.95),
            P99=lambda x: x.quantile(0.99)
        ).reset_index()
        
        fig = px.line(lat_grouped, x="minute", y=["P50", "P95", "P99"], 
                      labels={"value": "Latency (ms)", "minute": "Time"},
                      color_discrete_sequence=["#3B82F6", "#F59E0B", "#EF4444"])
        fig.add_hline(y=thresh.get("value", 3000), line_dash="dash", line_color="red", annotation_text="P95 Limit (3000ms)")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No response_sent events found.")

# --- PANEL 2: REQUEST TRAFFIC ---
with col2:
    st.subheader("2. Request Traffic (req/min)")
    panel_config = panels.get("traffic", {})
    df_req = df_filtered[df_filtered["event"] == "request_received"].copy()
    
    if not df_req.empty:
        total_requests = len(df_req)
        df_req["minute"] = df_req["ts"].dt.floor("1min")
        traffic_grouped = df_req.groupby("minute").size().reset_index(name="requests_per_minute")
        avg_rate = traffic_grouped["requests_per_minute"].mean()
        max_rate = traffic_grouped["requests_per_minute"].max()
        
        m1, m2 = st.columns(2)
        m1.metric("Total Requests", f"{total_requests}")
        m2.metric("Avg Traffic Rate", f"{avg_rate:.1f} req/min")
        
        thresh = panel_config.get("threshold", {})
        render_threshold_badge(avg_rate, thresh.get("operator", "gte"), thresh.get("value", 1), "req/min")
        
        fig = px.bar(traffic_grouped, x="minute", y="requests_per_minute",
                     labels={"requests_per_minute": "Requests / min", "minute": "Time"},
                     color_discrete_sequence=["#10B981"])
        fig.add_hline(y=thresh.get("value", 1), line_dash="dash", line_color="green", annotation_text="Min Target (1 req/min)")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No request_received events found.")

# Row 2
col3, col4 = st.columns(2)

# --- PANEL 3: ERRORS ---
with col3:
    st.subheader("3. Error Rate & Breakdown")
    panel_config = panels.get("errors", {})
    df_err_events = df_filtered[df_filtered["event"].isin(["request_received", "request_failed"])].copy()
    
    total_received = len(df_filtered[df_filtered["event"] == "request_received"])
    total_failed = len(df_filtered[df_filtered["event"] == "request_failed"])
    
    err_rate_pct = (total_failed / total_received * 100) if total_received > 0 else 0.0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Requests Received", f"{total_received}")
    m2.metric("Failed Requests", f"{total_failed}")
    m3.metric("Error Rate", f"{err_rate_pct:.2f}%")
    
    thresh = panel_config.get("threshold", {})
    render_threshold_badge(err_rate_pct, thresh.get("operator", "lte"), thresh.get("value", 2), "%")
    
    df_failed = df_filtered[df_filtered["event"] == "request_failed"]
    if not df_failed.empty and "error_type" in df_failed.columns:
        err_counts = df_failed["error_type"].value_counts().reset_index()
        err_counts.columns = ["error_type", "count"]
        fig = px.pie(err_counts, values="count", names="error_type", title="Error Breakdown by Type",
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Zero errors recorded in current window!")

# --- PANEL 4: COST OVER TIME ---
with col4:
    st.subheader("4. Cost Over Time (USD)")
    panel_config = panels.get("cost", {})
    df_cost = df_filtered[df_filtered["event"] == "response_sent"].dropna(subset=["cost_usd"]).copy()
    
    if not df_cost.empty:
        total_cost = df_cost["cost_usd"].sum()
        df_cost["minute"] = df_cost["ts"].dt.floor("1min")
        cost_grouped = df_cost.groupby("minute")["cost_usd"].sum().reset_index()
        
        m1, m2 = st.columns(2)
        m1.metric("Total Window Cost", f"${total_cost:.4f}")
        m2.metric("Avg Cost / Min", f"${cost_grouped['cost_usd'].mean():.4f}")
        
        thresh = panel_config.get("threshold", {})
        render_threshold_badge(total_cost, thresh.get("operator", "lte"), thresh.get("value", 2.5), "USD")
        
        fig = px.line(cost_grouped, x="minute", y="cost_usd",
                      labels={"cost_usd": "Cost ($)", "minute": "Time"},
                      color_discrete_sequence=["#8B5CF6"])
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost data available.")

# Row 3
col5, col6 = st.columns(2)

# --- PANEL 5: TOKENS ---
with col5:
    st.subheader("5. Token Usage (In / Out)")
    panel_config = panels.get("tokens", {})
    df_tok = df_filtered[df_filtered["event"] == "response_sent"].copy()
    
    if not df_tok.empty and ("tokens_in" in df_tok.columns or "tokens_out" in df_tok.columns):
        tok_in = df_tok["tokens_in"].sum() if "tokens_in" in df_tok.columns else 0
        tok_out = df_tok["tokens_out"].sum() if "tokens_out" in df_tok.columns else 0
        total_tokens = tok_in + tok_out
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Tokens In", f"{tok_in:,}")
        m2.metric("Tokens Out", f"{tok_out:,}")
        m3.metric("Total Tokens", f"{total_tokens:,}")
        
        thresh = panel_config.get("threshold", {})
        render_threshold_badge(total_tokens, thresh.get("operator", "lte"), thresh.get("value", 50000), "tokens")
        
        df_tok["minute"] = df_tok["ts"].dt.floor("1min")
        tok_grouped = df_tok.groupby("minute")[["tokens_in", "tokens_out"]].sum().reset_index()
        
        fig = px.bar(tok_grouped, x="minute", y=["tokens_in", "tokens_out"],
                     labels={"value": "Token Count", "minute": "Time", "variable": "Type"},
                     barmode="group",
                     color_discrete_sequence=["#6366F1", "#EC4899"])
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No token usage data available.")

# --- PANEL 6: QUALITY PROXY ---
with col6:
    st.subheader("6. Quality Proxy Score")
    panel_config = panels.get("quality", {})
    df_qual = df_filtered[df_filtered["event"] == "response_sent"].dropna(subset=["quality_score"]).copy()
    
    if not df_qual.empty:
        mean_quality = df_qual["quality_score"].mean()
        min_quality = df_qual["quality_score"].min()
        
        m1, m2 = st.columns(2)
        m1.metric("Mean Quality Score", f"{mean_quality:.2f}")
        m2.metric("Min Quality Score", f"{min_quality:.2f}")
        
        thresh = panel_config.get("threshold", {})
        render_threshold_badge(mean_quality, thresh.get("operator", "gte"), thresh.get("value", 0.75), "score")
        
        df_qual["minute"] = df_qual["ts"].dt.floor("1min")
        qual_grouped = df_qual.groupby("minute")["quality_score"].mean().reset_index()
        
        fig = px.line(qual_grouped, x="minute", y="quality_score",
                      labels={"quality_score": "Mean Quality Score", "minute": "Time"},
                      color_discrete_sequence=["#06B6D4"])
        fig.add_hline(y=thresh.get("value", 0.75), line_dash="dash", line_color="teal", annotation_text="Min Quality (0.75)")
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), yaxis_range=[0, 1.05])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No quality score data available.")

# Footer
st.markdown("---")
st.caption("Day 13 Observability Dashboard — Streamlit Implementation for AI Lab Observability.")
