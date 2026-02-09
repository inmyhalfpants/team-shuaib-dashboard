import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(page_title="Team Shuaib Project Manager", layout="wide")
st.title("Team Shuaib Management System")

# --- FILE CONFIGURATION ---
# This must match your uploaded Excel file name exactly
EXCEL_FILE = "Team Shuaib Daily Status.xlsx"

@st.cache_data
def load_data():
    """
    Loads data from the Excel file.
    Includes error handling for missing tabs or columns.
    """
    if not os.path.exists(EXCEL_FILE):
        return None, None

    # -------------------------------------------
    # PART 1: LOAD PROJECT LEDGERS
    # -------------------------------------------
    projects = []
    
    # Helper function to load a sheet if it exists
    def get_sheet(sheet_name, type_name):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
            df['Type'] = type_name
            return df
        except:
            return None

    # 1. Load 3D Project Ledger
    df_3d = get_sheet("3D Project Ledger", "3D Project")
    if df_3d is not None: 
        projects.append(df_3d)

    # 2. Load Web Shell Ledger
    df_web = get_sheet("WEB-Shell--Project Ledger", "Web Shell")
    if df_web is not None:
        # Rename columns to match the master list
        df_web = df_web.rename(columns={'Web Shell update': 'Name of project', 'Jira Link': 'JIRA'})
        projects.append(df_web)

    # 3. Load Venue Specific Tabs
    venue_tabs = [
        ("LNOO Venues", "LNOO"), 
        ("PDA Venues", "PDA"), 
        ("Connected Camera Venuer", "Connected Cam")
    ]
    
    for sheet, v_type in venue_tabs:
        df_v = get_sheet(sheet, v_type)
        if df_v is not None:
            # Standardize column names
            if 'Project' in df_v.columns: 
                df_v = df_v.rename(columns={'Project': 'Name of project', 'Jira': 'JIRA'})
            projects.append(df_v)
    
    # Combine all ledgers
    if projects:
        master_ledger = pd.concat(projects, ignore_index=True)
    else:
        master_ledger = pd.DataFrame()
    
    # -------------------------------------------
    # PART 2: LOAD DAILY STATUS (2026 Tab)
    # -------------------------------------------
    daily_status = pd.DataFrame()
    
    try:
        # We read with header=None because the dates are in odd places
        df_daily = pd.read_excel(EXCEL_FILE, sheet_name="2026", header=None)
        
        # --- CRITICAL FIX FOR KEYERROR ---
        # The app expects 12 columns (Index 0 to 11). 
        # If the Excel sheet is empty or new, it might have fewer.
        # This loop adds empty columns until we have at least 12.
        while df_daily.shape[1] < 12:
            df_daily[df_daily.shape[1]] = "" 

        clean_rows = []
        current_date = None
        
        # Iterate through rows to find Dates and Data
        for index, row in df_daily.iterrows():
            val_0 = str(row[0])
            
            # 1. Detect Date (Example: "2026-02-09")
            if val_0.startswith('2026-'):
                current_date = val_0
                continue
            
            # 2. Detect Team Member Data
            # Column 2 usually has the Name
            member_name = str(row[2])
            
            # Filter out empty rows, headers, or notes
            if member_name != 'nan' and member_name != 'Member' and "Note:" not in val_0:
                clean_rows.append({
                    'Date': current_date,
                    'Member': member_name,
                    # We use safe checks to avoid crashing if cells are empty
                    'Attendance': str(row[3]) if str(row[3]) != 'nan' else '',
                    'Project': str(row[5]) if str(row[5]) != 'nan' else '',
                    'Morning': str(row[10]) if str(row[10]) != 'nan' else '',
                    'Evening': str(row[11]) if str(row[11]) != 'nan' else ''
                })
        
        daily_status = pd.DataFrame(clean_rows)
        
    except Exception as e:
        # If reading 2026 fails, we print the error to the logs but keep the app running
        print(f"Error loading daily status: {e}")
        daily_status = pd.DataFrame()

    return master_ledger, daily_status

# Load the data
ledger, status = load_data()

# --- APP LAYOUT ---
tab1, tab2 = st.tabs(["📊 Daily Dashboard", "🗂️ Project Master List"])

# --- TAB 1: DASHBOARD ---
with tab1:
    if status is not None and not status.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sort dates so the newest is first
            dates = sorted(status['Date'].unique(), reverse=True)
            sel_date = st.selectbox("Select Date", dates)
            
        with col2:
            # Filter by team member
            members = sorted(status['Member'].unique())
            sel_member = st.multiselect("Filter by Member", members)
        
        # Apply filters
        filtered_df = status[status['Date'] == sel_date]
        if sel_member:
            filtered_df = filtered_df[filtered_df['Member'].isin(sel_member)]
            
        st.dataframe(filtered_df, use_container_width=True)
        
    else:
        st.info("No Daily Status data found. Please check that your Excel file has a tab named '2026'.")

# --- TAB 2: MASTER LIST ---
with tab2:
    if ledger is not None and not ledger.empty:
        search = st.text_input("🔍 Search Projects (Name, JIRA, or Lead)")
        
        if search:
            # Search across all columns
            mask = ledger.apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)
            st.dataframe(ledger[mask], use_container_width=True)
        else:
            st.dataframe(ledger, use_container_width=True)
            
    else:
        st.warning("No Project Ledger data found. Please check your Excel tab names.")