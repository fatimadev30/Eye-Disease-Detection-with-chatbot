import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import require_login, check_admin_access
from db.database import get_connection

require_login()
if not check_admin_access():
    st.error("Access Denied. Administrator privileges required.")
    st.stop()

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    
    .header-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        font-size: 36px;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .header-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        color: #64748B;
        margin-bottom: 30px;
    }
    
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        font-family: 'DM Sans', sans-serif;
        border: 1px solid #e2e8f0;
    }
    .custom-table thead {
        background-color: #f8fafc;
        border-bottom: 2px solid #e2e8f0;
    }
    .custom-table th {
        text-align: left;
        padding: 16px 20px;
        font-size: 13px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .custom-table td {
        padding: 16px 20px;
        font-size: 14px;
        color: #1e293b;
        border-bottom: 1px solid #f1f5f9;
        font-weight: 500;
    }
    .custom-table tbody tr {
        transition: background-color 0.2s ease;
    }
    .custom-table tbody tr:hover {
        background-color: #f0fdfa;
    }
    .custom-table tbody tr:last-child td {
        border-bottom: none;
    }
    .admin-badge {
        color: #0D9488;
        font-weight: 700;
    }
    .target-badge {
        color: #3B82F6;
        font-weight: 700;
        background-color: #EFF6FF;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
    }
    
    .empty-state {
        background: white;
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        font-family: 'DM Sans', sans-serif;
    }
    .empty-state i {
        font-size: 48px;
        color: #94A3B8;
        margin-bottom: 16px;
    }
    .empty-state h3 {
        margin: 0 0 8px 0;
        color: #1E293B;
        font-size: 18px;
        font-weight: 700;
    }
    .empty-state p {
        margin: 0;
        color: #64748B;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<div class="header-title">📜 Audit Logs</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Record of administrative actions.</div>', unsafe_allow_html=True)

conn = get_connection()
query = '''
    SELECT a.timestamp, u1.username as admin_username, a.action, a.target_user_id, u2.username as target_username
    FROM audit_logs a
    JOIN users u1 ON a.admin_id = u1.id
    LEFT JOIN users u2 ON a.target_user_id = u2.id
    ORDER BY a.timestamp DESC
'''
logs_df = pd.read_sql_query(query, conn)
conn.close()

if logs_df.empty:
    st.markdown("""
    <div class="empty-state">
        <i class="fa-solid fa-clipboard-list"></i>
        <h3>No Audit Logs Found</h3>
        <p>There are currently no administrative actions recorded in the system.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    table_html = '<table class="custom-table">'
    table_html += '<thead><tr><th>Time</th><th>User / Admin</th><th>Action</th><th>Target User</th></tr></thead><tbody>'
    
     # Convert database records into table rows
    for _, row in logs_df.iterrows():
        date_str = pd.to_datetime(row['timestamp']).strftime('%b %d, %Y • %I:%M %p')
            # target user information
        if pd.notna(row['target_username']):
            target_val = f"@{row['target_username']} (ID: {row['target_user_id']})"
        else:
            target_val = f"ID: {row['target_user_id']}" if pd.notna(row['target_user_id']) else "N/A"
            
        table_html += f"""<tr>
    <td style="color: #64748B;">{date_str}</td>
    <td><span class="admin-badge">@{row['admin_username']}</span></td>
    <td>{row['action']}</td>
    <td><span class="target-badge">{target_val}</span></td>
</tr>"""
        
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)
