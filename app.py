import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time
import os
import base64
import pytz 

# ==========================================
# 1. CONFIG & CORPORATE DARK THEME
# ==========================================
st.set_page_config(
    page_title="Testing Issue Tracker",
    page_icon="assets/Logo.svg", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# HELPER: BACA SVG JADI BASE64
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
            return base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    except:
        return ""

# ==========================================
# HELPER: GET CURRENT TIME (WIB / JAKARTA)
# ==========================================
def get_wib_time():
    tz = pytz.timezone('Asia/Jakarta')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M")

# ==========================================
# CSS STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, label, .stButton button, .stTextArea textarea, .stSelectbox div, .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0E1117;
        color: white;
        border: 1px solid #30363D;
        border-radius: 6px;
    }
    
    .stButton button {
        background-color: #0F52BA;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        border: none;
        height: 46px;
        margin-top: 0px;
    }
    .stButton button:hover {
        background-color: #0a3d8f;
    }

    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 1.5rem;
    }

    .empty-state {
        text-align: center;
        padding: 40px;
        color: #8b949e;
        border: 1px dashed #30363D;
        border-radius: 8px;
        background-color: #0d1117;
        font-size: 14px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'data_uat' not in st.session_state:
    st.session_state.data_uat = pd.DataFrame(
        columns=["Delete", "Status", "Time Found", "Issue Description", "Category", "Severity", "Time Resolved"]
    )

# --- SIDEBAR ---
with st.sidebar:
    st.header("Import Session")
    st.markdown("<p style='font-size: 12px; color: #8b949e; margin-top:-10px;'>Upload .xlsx file to resume.</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Select File", type=["xlsx"], label_visibility="collapsed")
    if uploaded_file:
        try:
            df_imported = pd.read_excel(uploaded_file)
            required_cols = ["Status", "Time Found", "Issue Description", "Category", "Severity", "Time Resolved"]
            if not all(col in df_imported.columns for col in required_cols):
                st.error("Invalid file format.")
            else:
                df_imported["Status"] = df_imported["Status"].apply(lambda x: True if x == "Closed" else False)
                df_imported.insert(0, "Delete", False)
                df_imported["Time Resolved"] = df_imported["Time Resolved"].fillna("")
                df_imported["Time Found"] = df_imported["Time Found"].astype(str)
                if st.button("Load Data", type="primary"):
                    st.session_state.data_uat = df_imported
                    st.rerun()
        except: pass

# ==========================================
# 3. HEADER AREA
# ==========================================
logo_b64 = get_base64_image("assets/Logo.svg")

st.markdown(f"""
<div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
    <img src="data:image/svg+xml;base64,{logo_b64}" width="48" style="margin-bottom: 0;">
    <div>
        <h3 style="margin: 0; font-weight: 700; font-size: 26px; color: #FFFFFF;">Testing Issue Tracker</h3>
        <p style="margin: 0; font-size: 14px; color: #8b949e; font-weight: 500;">Pertamina International Shipping • Internal Testing Phase</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. LOG NEW ISSUE
# ==========================================
with st.container(border=True):
    icon_new_b64 = get_base64_image("assets/NewIssue.svg")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <img src="data:image/svg+xml;base64,{icon_new_b64}" width="22" style="opacity: 0.9;">
        <span style="font-size: 18px; font-weight: 700; color: #E6E6E6;">Log New Issue</span>
    </div>
    """, unsafe_allow_html=True)
    
    input_desc = st.text_area("Issue Description", height=100, placeholder="Describe the technical issue clearly...")
    c1, c2, c3 = st.columns([3, 2, 1], gap="medium")
    
    with c1:
        category = st.selectbox("Category", ["Functional Bug", "UI/UX Defect", "Data Integrity", "Feature Request", "Performance", "Other"])
    with c2:
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    with c3:
        st.markdown("<div style='margin-top: 29px;'></div>", unsafe_allow_html=True) 
        btn_submit = st.button("Submit Issue", type="primary", use_container_width=True)

    if btn_submit and input_desc:
        current_time_wib = get_wib_time()
        new_row = {
            "Delete": False, "Status": False, 
            "Time Found": current_time_wib, 
            "Issue Description": input_desc, "Category": category, "Severity": severity, "Time Resolved": "" 
        }
        st.session_state.data_uat = pd.concat([st.session_state.data_uat, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()

# ==========================================
# 5. METRICS (FIXED SYNTAX)
# ==========================================
st.write("")
total = len(st.session_state.data_uat)
closed = len(st.session_state.data_uat[st.session_state.data_uat["Status"] == True])
open_s = total - closed
crit = len(st.session_state.data_uat[st.session_state.data_uat["Severity"].isin(["High", "Critical"])])

m1, m2, m3, m4 = st.columns(4)

with m1: 
    with st.container(border=True): 
        st.metric("Total Issues", total)

with m2: 
    with st.container(border=True): 
        st.metric("Pending", open_s)

with m3: 
    with st.container(border=True): 
        st.metric("Resolved", closed)

with m4: 
    with st.container(border=True): 
        st.metric("Critical / High", crit)

# ==========================================
# 6. TABLE LOG
# ==========================================
st.write("")
with st.container(border=True):
    icon_list_b64 = get_base64_image("assets/ListTable.svg")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
        <img src="data:image/svg+xml;base64,{icon_list_b64}" width="22" style="opacity: 0.9;">
        <span style="font-size: 18px; font-weight: 700; color: #E6E6E6;">Issue Log</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.data_uat.empty:
        st.markdown('<div class="empty-state">No issues logged yet. Start by submitting a new entry above.</div>', unsafe_allow_html=True)
    else:
        edited_df = st.data_editor(
            st.session_state.data_uat,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Delete": st.column_config.CheckboxColumn("Del", width="small"),
                "Status": st.column_config.CheckboxColumn("Done", width="small"),
                "Time Found": st.column_config.TextColumn("Time Found", disabled=True),
                "Issue Description": st.column_config.TextColumn("Description", width="large", required=True),
                "Category": st.column_config.SelectboxColumn("Category", width="medium", options=["Functional Bug", "UI/UX Defect", "Data Integrity", "Feature Request", "Performance"]),
                "Severity": st.column_config.SelectboxColumn("Severity", width="small", options=["Low", "Medium", "High", "Critical"]),
                "Time Resolved": st.column_config.TextColumn("Resolved At", disabled=True)
            },
            num_rows="fixed"
        )
        
        if not edited_df.equals(st.session_state.data_uat):
            df_active = edited_df[edited_df["Delete"] == False].copy()
            for idx, row in df_active.iterrows():
                if row["Status"] and not row["Time Resolved"]: 
                    df_active.at[idx, "Time Resolved"] = get_wib_time()
                elif not row["Status"] and row["Time Resolved"]: 
                    df_active.at[idx, "Time Resolved"] = ""
            st.session_state.data_uat = df_active
            st.rerun()

# ==========================================
# 7. EXPORT
# ==========================================
st.write("")
with st.container(border=True):
    c_ex1, c_ex2 = st.columns([4, 1])
    with c_ex1:
        icon_dl_b64 = get_base64_image("assets/Download.svg")
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="data:image/svg+xml;base64,{icon_dl_b64}" width="24" style="opacity: 0.9;">
            <div>
                <div style="font-weight: 700; color: #E6E6E6; font-size: 16px;">Export Data</div>
                <div style="font-size: 12px; color: #8b949e;">Download report (.xlsx) to resume later.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_ex2:
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        if not st.session_state.data_uat.empty:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                exp_df = st.session_state.data_uat.drop(columns=["Delete"]).copy()
                exp_df["Status"] = exp_df["Status"].apply(lambda x: "Closed" if x else "Open")
                exp_df.to_excel(writer, index=False, sheet_name='Logs')
                writer.sheets['Logs'].set_column('A:G', 20)
            st.download_button("Download Excel", data=buf.getvalue(), file_name=f"UAT_Log_{get_wib_time().replace(':','-').replace(' ', '_')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)