import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(page_title="Team Shuaib Project Manager", layout="wide")
st.title("Team Shuaib Management System")

# FILE NAME CONFIGURATION
# Make sure your Excel file in the folder is named EXACTLY this:
EXCEL_FILE = "Team Shuaib Daily Status.xlsx"

@st.cache_data
def load_ledger_data():
    """Loads and combines projects from different Excel Tabs."""
    if not os.path.exists(EXCEL_FILE):
        return pd.DataFrame()

    projects = []
    
    # 1. Load 3D Project Ledger
    try:
        df_3d = pd.read_excel(EXCEL_FILE, sheet_name="3D Project Ledger")
        df_3d['Type'] = '3D Project'
        projects.append(df_3d)
    except ValueError:
        pass # Sheet might not exist, skip it

    # 2. Load Web Shell Ledger
    try:
        df_web = pd.read_excel(EXCEL_FILE, sheet_name="WEB-Shell--Project Ledger")
        df_web['Type'] = 'Web Shell'
        df_web = df_web.rename(columns={'Web Shell update': 'Name of project', 'Jira Link': 'JIRA'})
        projects.append(df_web)
    except ValueError:
        pass

    # 3. Load Venue Specific Tabs
    # Check your Excel tabs! These names must match the tabs at the bottom of your Excel.
    venue_tabs = [
        ("LNOO Venues", "LNOO"),
        ("PDA Venues", "PDA"),
        ("Connected Camera Venuer", "Connected Cam")
    ]
    
    for sheet, v_type in venue_tabs:
        try:
            df_v = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
            df_v['Type'] = v_type
            if 'Project' in df_v.columns:
                df_v = df_v.rename(columns={'Project': 'Name of project', 'Jira': 'JIRA'})
            projects.append(df_v)
        except ValueError:
            pass

    if projects:
        master_df = pd.concat(projects, ignore_index=True)
        # Keep only useful columns
        cols_to_keep = ['Name of project', 'Type', 'Team Lead', 'Scope', 'JIRA', 'Comments', 'Status', 'prod url']
        valid_cols = [c for c in cols_to_keep if c in master_df.columns]
        return master_df[valid_cols]
    
    return pd.DataFrame()

@st.cache_data
def load_daily_status():
    """Parses the '2026' tab from the Excel file."""
    if not os.path.exists(EXCEL_FILE):
        return pd.DataFrame()
    
    try:
        # We read the '2026' sheet. Header=None because the dates are in weird places.
        df = pd.read_excel(EXCEL_FILE, sheet_name="2026", header=None)
    except ValueError:
        st.error("Could not find a tab named '2026' in your Excel file.")
        return pd.DataFrame()
    
    clean_rows = []
    current_date = None
    
    for index, row in df.iterrows():
        val_0 = str(row[0])
        
        # Detect Date (looks for '2026-')
        if val_0.startswith('2026-'):
            current_date = val_0
            continue 
            
        # Parse Rows
        team_lead = str(row[1])
        member = str(row[2])
        status = str(row[3])
        
        if member != 'nan' and member != 'Member' and "Note:" not in val_0:
            clean_rows.append({
                'Date': current_date,
                'Team Lead': team_lead if team_lead != 'nan' else '',
                'Member': member,
                'Attendance': status if status != 'nan' else '',
                'Project': str(row[5]) if str(row[5]) != 'nan' else '',
                'Morning Update': str(row[10]) if str(row[10]) != 'nan' else '',
                'Evening Update': str(row[11]) if str(row[11]) != 'nan' else ''
            })
            
    return pd.DataFrame(clean_rows)

# --- Application Layout ---

tab1, tab2 = st.tabs(["📊 Daily Dashboard", "🗂️ Project Master List"])

with tab1:
    st.header("Daily Status Log")
    df_status = load_daily_status()
    
    if not df_status.empty:
        col1, col2 = st.columns(2)
        with col1:
            # Sort dates newest first
            dates = sorted(df_status['Date'].unique(), reverse=True)
            selected_date = st.selectbox("Select Date", dates)
        with col2:
            members = sorted(df_status['Member'].unique())
            selected_member = st.multiselect("Filter by Member", members)
        
        filtered_df = df_status[df_status['Date'] == selected_date]
        if selected_member:
            filtered_df = filtered_df[filtered_df['Member'].isin(selected_member)]
            
        st.dataframe(filtered_df, use_container_width=True)
        
        st.subheader("Attendance Overview")
        st.bar_chart(filtered_df['Attendance'].value_counts())
    else:
        st.info("Upload 'Team Shuaib Daily Status.xlsx' to see data.")

with tab2:
    st.header("Unified Project Ledger")
    df_ledger = load_ledger_data()
    
    if not df_ledger.empty:
        search_term = st.text_input("🔍 Search Projects (Name, JIRA, or Lead)")
        if search_term:
            mask = df_ledger.apply(lambda x: x.astype(str).str.contains(search_term, case=False).any(), axis=1)
            display_df = df_ledger[mask]
        else:
            display_df = df_ledger
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Ledger data not found. Check Excel tab names.")