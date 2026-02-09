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
    "Final Assets prepration and Public VV
