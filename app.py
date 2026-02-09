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
TASK_KEYWORDS = [
    "File Setup/Cad Placement", "Refrence collection/ Asset check", "Site Setup/Exterior Modeling",
    "Massing/Bowl Modeling", "Exterior Modeling", "Bowl Detailing , Vomitory, Aisles",
    "Concourse Area", "Premium Facade", "Railclone set/ Railing Placement",
    "Site Modeling", "Field/ Court/ Stage setup", "Detailing", "Stadium self QA and refinement",
    "Texturing", "Chair Modeling", "Roof Modeling", "Texturing & Lighting", "Chair QC",
    "ScoreBoard Modeling", "Chair Railcone set", "Refinement", "QC Comments",
    "Spline Extracting/Spline Naming", "Site Texturing/Lighting", "Seat Node Generate",
    "Finalize QC & Refinment", "Chair Placement", "Refinement and shoot Test renders",
    "Aerial Level Adjustment", "Data Model", "Test Render QA/Refinments",
    "Self QA & QC changes", "Data Model/Json/Price Map", "Shoot Beta renders",
    "Json/Price Map", "AMVV Beauty And site testing", "Beta Assets Deliver",
    "AMVV Chair Break", "AMVV Data Model", "Raster file prepration",
    "AMVV Chair naming and random color", "AMVV Test renders", 
    "Vecor File preration/Test renders", "WireColor Competes and Json",
    "Internal QA/Client comments", "Final render shoot for STG", "Shoot final renders",
    "AMVV test render QC", "Grouping and Bounds", 
    "Final Assets prepration and Public VV Delivery", "AMVV Final render shoot",
    "CMS/4D", "AMVV asset prepration and Assets Delivery", 
    "Assets Combine and QC Comments", "STG assets Uploading and STG", "Internal QA",
    "STG QA", "Bowl Change", "Structure Change", "Score Board Design",
    "Railing Change", "Seat Type Change", "Branding 3D Logo", "Banner",
    "Rafter / Country Flag's", "Team Logo", "Price Map", 
    "Manifest - Row name update /Seat /Section number", 
    "Rollover - VR Position change", "Level Altering - Level add/remove /update",
    "Lighting Changes (Day/Evening/Night)", "Field Change", "Premium Space Layout",
    "Furniture", "Config Change - adding Multiple Config", "Web-Shell changes"
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
    for sheet, ptype in [
        ("3D Project Ledger", "3D"), 
        ("WEB-Shell--Project Ledger", "Web"),
        ("LNOO Venues", "L
