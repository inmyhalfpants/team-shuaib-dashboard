import streamlit as st
import pandas as pd
import os
import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Team Shuaib Project Manager", layout="wide")
st.title("Team Shuaib Management System")

# --- CONFIGURATION ---
EXCEL_FILE = "Team Shuaib Daily Status.xlsx"

# --- DROPDOWN OPTIONS ---
ATTENDANCE_OPTIONS = ["In", "Out", "WFH"]
STATUS_OPTIONS = ["In Process", "QA", "Hold", "Blocked due to IT issues", "Assigned", "Completed"]

# Reformatted list to prevent syntax errors
TASK_KEYWORDS = [
    "File Setup/Cad Placement",
    "Refrence collection/ Asset check",
    "Site Setup/Exterior Modeling",
    "Massing/Bowl Modeling",
    "Exterior Modeling",
    "Bowl Detailing , Vomitory, Aisles",
    "Concourse Area",
    "Premium Facade",
    "Railclone set/ Railing Placement",
    "Site Modeling",
    "Field/ Court/ Stage setup",
    "Detailing",
    "Stadium self QA and refinement",
    "Texturing",
    "Chair Modeling",
    "Roof Modeling",
    "Texturing & Lighting",
    "Chair QC",
    "ScoreBoard Modeling",
    "Chair Railcone set",
    "Refinement",
    "QC Comments",
    "Spline Extracting/Spline Naming",
    "Site Texturing/Lighting",
    "Seat Node Generate",
    "Finalize QC & Refinment",
    "Chair Placement",
    "Refinement and shoot Test renders",
    "Aerial Level Adjustment",
    "Data Model",
    "Test Render QA/Refinments",
    "Self QA & QC changes",
    "Data Model/Json/Price Map",
    "Shoot Beta renders",
    "Json/Price Map",
    "AMVV Beauty And site testing",
    "Beta Assets Deliver",
    "AMVV Chair Break",
    "AMVV Data Model",
    "Raster file prepration",
    "AMVV Chair naming and random color",
    "AMVV Test renders",
    "Vecor File preration/Test renders",
    "WireColor Competes and Json",
    "Internal QA/Client comments",
    "Final render shoot for STG",
    "Shoot final renders",
    "AMVV test render QC",
    "Grouping and Bounds",
    "Final Assets prepration and Public VV Delivery",
    "AMVV Final render shoot",
    "CMS/4D",
    "AMVV asset prepration and Assets Delivery",
    "Assets Combine and QC Comments",
    "STG assets Uploading and STG",
    "Internal QA",
    "STG QA",
    "Bowl Change",
    "Structure Change",
    "Score Board Design",
    "Railing Change",
    "Seat Type Change",
    "Branding 3D Logo",
    "Banner",
    "Rafter / Country Flag's",
    "Team Logo",
    "Price Map",
    "Manifest - Row name update /Seat /Section number",
    "Rollover - VR Position change",
    "Level Altering - Level add/remove /update",
    "Lighting Changes (Day/Evening/Night)",
    "Field Change",
    "Premium Space Layout",
    "Furniture",
    "Config Change - adding Multiple Config",
    "Web-Shell changes"
]

@st.cache_data
def load_data():
    if not os.path.exists(EXCEL_FILE):
        return None, None

    # --- 1. LOAD MASTER LEDGER (For Jira Links) ---
    projects = []
    
    def get_sheet(name, type_name):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=name)
            df['Type'] = type_name
            return df
        except: return None

    # Load and combine ledgers
    sheets_to_load = [
        ("3D Project Ledger", "3D"), 
        ("WEB-Shell--Project Ledger", "Web"),
        ("LNOO Venues", "LNOO"), 
        ("PDA Venues", "PDA"), 
        ("Connected Camera Venuer", "Cam")
    ]
    
    for sheet, ptype in sheets_to_load:
        df = get_sheet(sheet, ptype)
        if df is not None:
            # Normalize Jira Column Name
            if 'Jira Link' in df.columns: df = df.rename(columns={'Jira Link': 'JIRA'})
            if 'Jira' in df.columns: df = df.rename(columns={'Jira': 'JIRA'})
            if 'Web Shell update' in df.columns: df = df.rename(columns={'Web Shell update': 'Name of project'})
            if 'Project' in df.columns: df = df.rename(columns={'Project': 'Name of project'})
            projects.append(df)
            
    master_ledger = pd.concat(projects, ignore_index=True) if projects else pd.DataFrame()

    # --- 2. LOAD DAILY STATUS (2026) ---
    try:
        # Read raw data
        df_daily = pd.read_excel(EXCEL_FILE, sheet_name="2026", header=None)
        
        # Ensure enough columns exist (we need at least 12 for the parsing logic)
        while df_daily.shape[1] < 12:
            df_daily[df_daily.shape[1]] = "" 

        clean_rows = []
        current_date = None
        
        for index, row in df_daily.iterrows():
            val_0 = str(row[0])
            
            # Detect Date
            if val_0.startswith('2026-'):
                current_date = val_0.split(' ')[0] # Remove time
                continue
            
            # Parse Rows
            # 0:Date, 1:Lead, 2:Member, 3:Attendance, 4:Archive, 5:Project/Jira, 6:Status, 8:Morning/Task
            member_name = str(row[2])
            if member_name != 'nan' and member_name != 'Member' and "Note:" not in val_0:
                
                # Try to find Jira Link
                project_name = str(row[5]) if str(row[5]) != 'nan' else ''
                jira_link = ""
                if not master_ledger.empty and project_name:
                    match = master_ledger[master_ledger['Name of project'].astype(str).str.contains(project_name, regex=False, case=False)]
                    if not match.empty:
                        jira_link = match.iloc[0]['JIRA'] if 'JIRA' in match.columns else ""

                clean_rows.append({
                    'Date': pd.to_datetime(current_date).date(), 
                    'Team Lead': str(row[1]) if str(row[1]) != 'nan' else '',
                    'Member': member_name,
                    'Attendance': str(row[3]) if str(row[3]) != 'nan' else 'Out',
                    'Project Archive': str(row[4]) if str(row[4]) != 'nan' else '',
                    'Project Name': project_name,
                    'Jira Link': jira_link if jira_link else project_name, 
                    'Project Status': str(row[6]) if str(row[6]) != 'nan' else 'In Process',
                    'Task Category': 'File Setup/Cad Placement', # Default
                    'Hours': 0.0,
                    'Comments': str(row[8]) if str(row[8]) != 'nan' else ''
                })
                
        daily_status = pd.DataFrame(clean_rows)
        
    except Exception as e:
        print(f"Error: {e}")
        daily_status = pd.DataFrame()

    return master_ledger, daily_status

ledger, status = load_data()

# --- APP LAYOUT ---
tab1, tab2 = st.tabs(["📊 Daily Dashboard", "🗂️ Project Master List"])

with tab1:
    if status is not None and not status.empty:
        # Minimal Filter Bar
        col1, col2 = st.columns([1, 3])
        with col1:
            dates = sorted(status['Date'].unique(), reverse=True)
            sel_date = st.selectbox("Select Date", dates)
        with col2:
            st.info("💡 Tip: Click on any cell in 'Attendance', 'Status', or 'Task Log' to change it.")
        
        # Filter Data
        filtered_df = status[status['Date'] == sel_date]

        # --- INTERACTIVE DATA EDITOR ---
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", disabled=True),
                "Team Lead": st.column_config.TextColumn("Team Lead", disabled=True),
                "Member": st.column_config.TextColumn("Member", disabled=True),
                
                # --- DROPDOWNS ---
                "Attendance": st.column_config.SelectboxColumn(
                    "Attendance",
                    options=ATTENDANCE_OPTIONS,
                    required=True,
                    width="small"
                ),
                "Project Status": st.column_config.SelectboxColumn(
                    "Project Status",
                    options=STATUS_OPTIONS,
                    required=True,
                    width="medium"
                ),
                "Task Category": st.column_config.SelectboxColumn(
                    "Task Log",
                    options=TASK_KEYWORDS,
                    width="large",
                    required=True
                ),
                # -----------------
                
                "Hours": st.column_config.NumberColumn("Hrs", min_value=0, max_value=24, step=0.5),
                "Project Archive": st.column_config.TextColumn("Project Archive"),
                "Jira Link": st.column_config.LinkColumn("Jira Link", display_text="Open Jira"),
                "Comments": st.column_config.TextColumn("Comments", width="large"),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            disabled=False 
        )
        
        # Download Button
        if st.button("Download Updated Sheet"):
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button("Click to Download CSV", csv, "updated_status.csv", "text/csv")
        
    else:
        st.info("No Daily Status data found.")

with tab2:
    if ledger is not None and not ledger.empty:
        search = st.text_input("🔍 Search Projects")
        if search:
            mask = ledger.apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)
            st.dataframe(ledger[mask], use_container_width=True)
        else:
            st.dataframe(ledger, use_container_width=True)
    else:
        st.warning("No Project Ledger data found.")
