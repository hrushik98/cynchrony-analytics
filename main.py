"""
Cynchrony Analytics Dashboard - Streamlit Application

A real-time analytics dashboard for monitoring the Cynchrony Backend API.

Run with: streamlit run analytics_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

BACKEND_URL = st.secrets["ANALYTICS_BACKEND_URL"]
REFRESH_INTERVAL = int(st.secrets["DASHBOARD_REFRESH_INTERVAL"])

# Page configuration
st.set_page_config(
    page_title="Cynchrony Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    .success-rate-high {
        color: #10b981;
    }
    .success-rate-medium {
        color: #f59e0b;
    }
    .success-rate-low {
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)


def fetch_data(endpoint: str):
    """Fetch data from the analytics API."""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            st.error(f"Error fetching {endpoint}: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}. Make sure the server is running.")
        return None
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {str(e)}")
        return None


def format_number(num):
    """Format large numbers with K, M suffixes."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def get_success_rate_color(rate):
    """Get color based on success rate."""
    if rate >= 95:
        return "success-rate-high"
    elif rate >= 80:
        return "success-rate-medium"
    return "success-rate-low"


def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Cynchrony Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cynchrony.in/logo.png", width=150)
        st.markdown("---")
        st.markdown("### Settings")
        
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 10, 120, REFRESH_INTERVAL)
        
        st.markdown("---")
        st.markdown("### Quick Links")
        st.markdown(f"- [API Docs]({BACKEND_URL}/docs)")
        st.markdown(f"- [Health Check]({BACKEND_URL}/health)")
        
        st.markdown("---")
        st.markdown("### Backend Status")
        try:
            health = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if health.status_code == 200:
                st.success("✅ Backend Online")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")
        
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Fetch summary data
    summary = fetch_data("summary")
    
    if summary is None:
        st.warning("Unable to fetch analytics data. Please check the backend connection.")
        st.info(f"Trying to connect to: {BACKEND_URL}")
        return
    
    # Main Metrics Row
    st.markdown("### 📈 Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total API Calls",
            value=format_number(summary.get("total_api_calls", 0)),
            delta=None
        )
    
    with col2:
        success_rate = summary.get("success_rate", 100)
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Errors",
            value=format_number(summary.get("total_errors", 0)),
            delta=None
        )
    
    with col4:
        st.metric(
            label="AI Chat Calls",
            value=format_number(summary.get("ai_chat_calls", 0)),
            delta=None
        )
    
    with col5:
        st.metric(
            label="AI Generation",
            value=format_number(summary.get("ai_generation_calls", 0)),
            delta=None
        )
    
    st.markdown("---")
    
    # Processing Metrics Row
    st.markdown("### 🔧 Processing Operations")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            label="📄 PDF Processing",
            value=format_number(summary.get("pdf_processing", 0))
        )
    
    with col2:
        st.metric(
            label="🖼️ Image Processing",
            value=format_number(summary.get("image_processing", 0))
        )
    
    with col3:
        st.metric(
            label="🎬 Video Processing",
            value=format_number(summary.get("video_processing", 0))
        )
    
    with col4:
        st.metric(
            label="🎵 Audio Processing",
            value=format_number(summary.get("audio_processing", 0))
        )
    
    with col5:
        st.metric(
            label="💻 Code Executions",
            value=format_number(summary.get("code_executions", 0))
        )
    
    with col6:
        st.metric(
            label="📁 File Uploads",
            value=format_number(summary.get("file_uploads", 0))
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Category Breakdown")
        
        category_data = summary.get("category_breakdown", {})
        if category_data:
            df = pd.DataFrame([
                {"Category": k.replace("_", " ").title(), "Count": v}
                for k, v in category_data.items()
            ])
            df = df.sort_values("Count", ascending=True)
            
            fig = px.bar(
                df,
                x="Count",
                y="Category",
                orientation="h",
                color="Count",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Number of Calls",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available yet.")
    
    with col2:
        st.markdown("### 🎯 Top Endpoints")
        
        endpoints = fetch_data("endpoints")
        if endpoints:
            df = pd.DataFrame(endpoints[:10])
            if not df.empty:
                fig = px.bar(
                    df,
                    x="count",
                    y="endpoint",
                    orientation="h",
                    color="success_rate",
                    color_continuous_scale="RdYlGn",
                    labels={"count": "Calls", "endpoint": "Endpoint", "success_rate": "Success %"}
                )
                fig.update_layout(
                    height=400,
                    yaxis={"categoryorder": "total ascending"}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No endpoint data available yet.")
    
    st.markdown("---")
    
    # Hourly Stats
    st.markdown("### ⏰ Hourly Activity (Last 24 Hours)")
    
    hourly = fetch_data("hourly")
    if hourly:
        df = pd.DataFrame(hourly)
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["hour"],
                y=df["count"],
                mode="lines+markers",
                name="Total Calls",
                line=dict(color="#667eea", width=2),
                fill="tozeroy",
                fillcolor="rgba(102, 126, 234, 0.2)"
            ))
            
            fig.add_trace(go.Scatter(
                x=df["hour"],
                y=df["success_count"],
                mode="lines+markers",
                name="Successful",
                line=dict(color="#10b981", width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df["hour"],
                y=df["error_count"],
                mode="lines+markers",
                name="Errors",
                line=dict(color="#ef4444", width=2)
            ))
            
            fig.update_layout(
                height=300,
                xaxis_title="Hour",
                yaxis_title="Number of Calls",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hourly data available yet.")
    
    st.markdown("---")
    
    # Business Metrics Row
    st.markdown("### 💼 Business Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🔐 Auth Events",
            value=format_number(summary.get("authentication_events", 0))
        )
    
    with col2:
        st.metric(
            label="💳 Payment Events",
            value=format_number(summary.get("payment_events", 0))
        )
    
    with col3:
        st.metric(
            label="📝 Assessments",
            value=format_number(summary.get("assessment_events", 0))
        )
    
    with col4:
        st.metric(
            label="🎤 Interviews",
            value=format_number(summary.get("interview_events", 0))
        )
    
    with col5:
        st.metric(
            label="📄 Resume Ops",
            value=format_number(summary.get("resume_operations", 0))
        )
    
    st.markdown("---")
    
    # Recent Errors
    st.markdown("### ⚠️ Recent Errors")
    
    errors = fetch_data("errors")
    if errors:
        df = pd.DataFrame(errors[:20])
        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "endpoint": st.column_config.TextColumn("Endpoint", width="medium"),
                    "method": st.column_config.TextColumn("Method", width="small"),
                    "status_code": st.column_config.NumberColumn("Status", width="small"),
                    "error": st.column_config.TextColumn("Error Message", width="large"),
                    "timestamp": st.column_config.TextColumn("Timestamp", width="medium")
                }
            )
        else:
            st.success("🎉 No errors recorded!")
    else:
        st.success("🎉 No errors recorded!")
    
    st.markdown("---")
    
    # Daily Stats
    st.markdown("### 📅 Daily Statistics (Last 30 Days)")
    
    daily = fetch_data("daily")
    if daily:
        df = pd.DataFrame(daily)
        if not df.empty:
            df = df.sort_values("date")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df["date"],
                y=df["successful_calls"],
                name="Successful",
                marker_color="#10b981"
            ))
            
            fig.add_trace(go.Bar(
                x=df["date"],
                y=df["failed_calls"],
                name="Failed",
                marker_color="#ef4444"
            ))
            
            fig.update_layout(
                barmode="stack",
                height=300,
                xaxis_title="Date",
                yaxis_title="Number of Calls",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No daily data available yet.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
            Cynchrony Analytics Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            <br>
            Connected to: {BACKEND_URL}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
