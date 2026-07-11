import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import require_login, check_admin_access
from db.database import get_connection

# Page setup
require_login()
if not check_admin_access():
    st.error("Access Denied. Administrator privileges required.")
    st.stop()

# ----------------- DATA FETCHING -----------------
def get_dashboard_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Metrics
    metrics = {
        "total_users": cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='user'").fetchone()['count'],
        "total_predictions": cursor.execute("SELECT COUNT(*) as count FROM predictions").fetchone()['count'],
        "total_chats": cursor.execute("SELECT COUNT(*) as count FROM chat_history").fetchone()['count'],
        "avg_conf": cursor.execute("SELECT AVG(confidence) as avg FROM predictions").fetchone()['avg']
    }
    
    # Chart 1: Distribution (Diseases)
    pred_dist = pd.read_sql_query("SELECT predicted_class, COUNT(*) as count FROM predictions GROUP BY predicted_class", conn)
    
    # Chart 2: Timeline (Total Predictions)
    timeline_df = pd.read_sql_query("""
        SELECT DATE(timestamp) as date, COUNT(*) as count 
        FROM predictions 
        GROUP BY DATE(timestamp) 
        ORDER BY date ASC
    """, conn)
    
    # Table: Recent Activity
    recent_activity = pd.read_sql_query("""
        SELECT u.username, p.predicted_class, p.confidence, p.timestamp 
        FROM predictions p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.timestamp DESC LIMIT 5
    """, conn)
    
    conn.close()
    return metrics, pred_dist, timeline_df, recent_activity

metrics, pred_dist, timeline_df, recent_activity = get_dashboard_data()

# ----------------- HEADER -----------------
st.markdown("<h1 style='color: #0F172A; font-family: DM Sans, sans-serif; font-size: 36px; font-weight: 800; margin-bottom: 0;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-family: DM Sans, sans-serif; margin-bottom: 30px;'>Overview of platform metrics and user activity.</p>", unsafe_allow_html=True)

# ----------------- METRICS CARDS WITH OUTLINE -----------------
col1, col2, col3, col4 = st.columns(4)

def metric_card(col, title, value):
    col.markdown(f"""
        <div style="
            background: white; 
            padding: 24px 15px; 
            border-radius: 16px; 
            border: 1.5px solid #E2E8F0; 
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            text-align: center;
            font-family: 'DM Sans', sans-serif;
        ">
            <p style="margin: 0; color: #64748B; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
            <h2 style="margin: 10px 0 0 0; color: #0F172A; font-size: 32px; font-weight: 800;">{value}</h2>
        </div>
    """, unsafe_allow_html=True)

avg_conf_pct = f"{metrics['avg_conf'] * 100:.1f}%" if metrics['avg_conf'] else "0%"

metric_card(col1, "Total Users", metrics['total_users'])
metric_card(col2, "Total Scans", metrics['total_predictions'])
metric_card(col3, "AI Chats", metrics['total_chats'])
metric_card(col4, "Avg Confidence", avg_conf_pct)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- CHARTS SECTION -----------------
c1, c2 = st.columns([1, 1])

with c1:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0; font-size: 18px; color: #1e293b;'>Disease Distribution</h3>", unsafe_allow_html=True)
        if not pred_dist.empty:
            fig_pie = px.pie(
                pred_dist, 
                values='count', 
                names='predicted_class',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No prediction data.")

with c2:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0; font-size: 18px; color: #1e293b;'>Prediction Frequency</h3>", unsafe_allow_html=True)
        if not timeline_df.empty:
            fig_line = px.line(
                timeline_df, 
                x='date', 
                y='count',
                markers=True,
                color_discrete_sequence=['#0D9488']
            )
            fig_line.update_layout(
                xaxis_title=None, yaxis_title=None,
                margin=dict(t=10, b=10, l=0, r=0), height=300,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_line.update_xaxes(showgrid=False)
            fig_line.update_yaxes(gridcolor='#f1f5f9')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No timeline data.")

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- RECENT SCANS TABLE -----------------
st.markdown("<h3 style='color: #1E293B; font-size: 20px; margin-bottom: 15px;'>Recent Scans</h3>", unsafe_allow_html=True)
if not recent_activity.empty:
    recent_activity['confidence'] = (recent_activity['confidence'] * 100).round(1).astype(str) + '%'
    
    table_css = """
    <style>
    .custom-table { width: 100%; border-collapse: collapse; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'DM Sans', sans-serif; border: 1px solid #e2e8f0; }
    .custom-table thead { background: #f8fafc; border-bottom: 2px solid #e2e8f0; }
    .custom-table th { text-align: left; padding: 16px 20px; font-size: 13px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .custom-table td { padding: 16px 20px; font-size: 14px; color: #1e293b; border-bottom: 1px solid #f1f5f9; font-weight: 500; }
    .custom-table tr:hover { background: #f0fdfa; }
    .diag-badge { padding: 4px 12px; border-radius: 100px; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .bg-cnv { background: #FEE2E2; color: #DC2626; }
    .bg-dme { background: #FEF3C7; color: #D97706; }
    .bg-drusen { background: #E0F2FE; color: #0284C7; }
    .bg-normal { background: #DCFCE7; color: #16A34A; }
    </style>
    """
    
    table_html = table_css + '<table class="custom-table"><thead><tr><th>User</th><th>Diagnosis</th><th>Confidence</th><th>Time</th></tr></thead><tbody>'
    
    for _, row in recent_activity.iterrows():
        cls_lower = row['predicted_class'].lower()
        badge_bg = f"bg-{cls_lower}" if cls_lower in ["cnv", "dme", "drusen", "normal"] else "bg-normal"
        date_str = pd.to_datetime(row['timestamp']).strftime('%b %d, %Y • %I:%M %p')
        
        table_html += f"""<tr>
            <td><span style="color: #0D9488; font-weight: 700;">@{row['username']}</span></td>
            <td><span class="diag-badge {badge_bg}">{row['predicted_class']}</span></td>
            <td>{row['confidence']}</td>
            <td style="color: #64748B;">{date_str}</td>
        </tr>"""
    
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)
else:
    st.info("No recent scans found.")

st.markdown("<br><br>", unsafe_allow_html=True)
