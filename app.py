from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from zipfile import ZipFile
from datetime import date
import json

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="HustleHQ",
    page_icon="💼",
    layout="wide"
)


# =========================
# HUSTLEHQ POLISH CSS
# =========================

st.markdown(
    """
    <style>
    .stApp {
        background: #F8FAFC;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1F33 0%, #071827 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #0B1F33;
        font-weight: 800;
    }

    h2, h3 {
        color: #102A43;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0px 6px 18px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    .hustlehq-hero {
        background: linear-gradient(135deg, #0B1F33 0%, #064E3B 100%);
        padding: 28px;
        border-radius: 22px;
        margin-bottom: 24px;
        color: white;
    }

    .hustlehq-hero h2 {
        color: white;
        margin-bottom: 4px;
    }

    .hustlehq-hero p {
        color: #D1FAE5;
        margin-bottom: 0px;
    }

    .hustlehq-card {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #E5E7EB;
        box-shadow: 0px 8px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

sample_income = pd.DataFrame(
    {
        "stream": [
            "Vinted",
            "Legal Transcription",
            "Etsy / Digital Products",
            "UGC Deals",
            "YouTube",
        ],
        "amount": [250, 180, 90, 320, 45],
    }
)

sample_expenses = pd.DataFrame(
    {
        "category": [
            "Stock",
            "Postage",
            "Packaging",
            "Software",
            "Courses / Learning",
        ],
        "amount": [110, 35, 20, 28, 45],
    }
)
DATA_FOLDER = Path("data")

if DATA_FOLDER.exists() and not DATA_FOLDER.is_dir():
    DATA_FOLDER.unlink()

DATA_FOLDER.mkdir(exist_ok=True)

INCOME_FILE = DATA_FOLDER / "income_records.csv"
EXPENSE_FILE = DATA_FOLDER / "expense_records.csv"
GOALS_FILE = DATA_FOLDER / "goals.json"
APP_SETTINGS_FILE = DATA_FOLDER / "app_settings.json"


def load_income_records():
    columns = [
        "date",
        "income_stream",
        "platform",
        "description",
        "gross_income",
        "fees",
        "net_income",
        "paid_status",
        "evidence_link",
        "notes",
    ]

    if INCOME_FILE.exists():
        records = pd.read_csv(INCOME_FILE)

        if "stream" in records.columns and "income_stream" not in records.columns:
            records = records.rename(columns={"stream": "income_stream"})
    else:
        records = pd.DataFrame(columns=columns)

    for column in columns:
        if column not in records.columns:
            records[column] = ""

    if not records.empty:
        records["date"] = pd.to_datetime(records["date"], errors="coerce")
        records["gross_income"] = pd.to_numeric(records["gross_income"], errors="coerce").fillna(0)
        records["fees"] = pd.to_numeric(records["fees"], errors="coerce").fillna(0)
        records["net_income"] = pd.to_numeric(records["net_income"], errors="coerce").fillna(0)

    return records[columns]


def save_income_record(record):
    records = load_income_records()
    new_row = pd.DataFrame([record])
    records = pd.concat([records, new_row], ignore_index=True)
    records.to_csv(INCOME_FILE, index=False)
def load_expense_records():
    columns = [
        "date",
        "expense_category",
        "linked_stream",
        "description",
        "amount",
        "receipt_link",
        "notes",
    ]

    if EXPENSE_FILE.exists():
        records = pd.read_csv(EXPENSE_FILE)
    else:
        records = pd.DataFrame(columns=columns)

    for column in columns:
        if column not in records.columns:
            records[column] = ""

    if not records.empty:
        records["date"] = pd.to_datetime(records["date"], errors="coerce")
        records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)

    return records[columns]


def save_expense_record(record):
    records = load_expense_records()
    new_row = pd.DataFrame([record])
    records = pd.concat([records, new_row], ignore_index=True)
    records.to_csv(EXPENSE_FILE, index=False)

    def overwrite_income_records(records):
     records.to_csv(INCOME_FILE, index=False)

def load_goal_settings():
    default_goals = {
        "debt_target": 1000.0,
        "savings_target": 2000.0,
        "monthly_income_goal": 500.0,
        "emergency_buffer_goal": 500.0,
        "priority_goal": "Clear debt first",
    }

    if GOALS_FILE.exists():
        try:
            saved_goals = json.loads(GOALS_FILE.read_text(encoding="utf-8"))
            default_goals.update(saved_goals)
        except json.JSONDecodeError:
            pass

    return default_goals


def save_goal_settings(goals):
    GOALS_FILE.write_text(json.dumps(goals, indent=4), encoding="utf-8")


def add_income_status_columns(income_records):
    records = income_records.copy()

    if records.empty:
        records["record_status"] = []
        records["review_reason"] = []
        return records

    statuses = []
    reasons = []

    for _, row in records.iterrows():
        description = str(row.get("description", "")).strip()
        evidence_link = str(row.get("evidence_link", "")).strip()
        paid_status = str(row.get("paid_status", "")).strip()
        gross_income = float(row.get("gross_income", 0))
        net_income = float(row.get("net_income", 0))

        if description == "" or gross_income <= 0:
            statuses.append("Needs review")
            reasons.append("Missing description or income amount is zero")
        elif paid_status != "Paid":
            statuses.append("Pending payment")
            reasons.append("Income is not fully marked as paid")
        elif evidence_link == "":
            statuses.append("Missing evidence")
            reasons.append("No evidence link or screenshot name added")
        elif net_income < 0:
            statuses.append("Needs review")
            reasons.append("Net income is negative")
        else:
            statuses.append("Complete")
            reasons.append("Record looks complete")

    records["record_status"] = statuses
    records["review_reason"] = reasons

    return records


def add_expense_status_columns(expense_records):
    records = expense_records.copy()

    if records.empty:
        records["record_status"] = []
        records["review_reason"] = []
        return records

    statuses = []
    reasons = []

    for _, row in records.iterrows():
        description = str(row.get("description", "")).strip()
        receipt_link = str(row.get("receipt_link", "")).strip()
        amount = float(row.get("amount", 0))

        if description == "" or amount <= 0:
            statuses.append("Needs review")
            reasons.append("Missing description or expense amount is zero")
        elif receipt_link == "":
            statuses.append("Missing receipt")
            reasons.append("No receipt link or screenshot name added")
        else:
            statuses.append("Complete")
            reasons.append("Record looks complete")

    records["record_status"] = statuses
    records["review_reason"] = reasons

    return records


def load_app_settings():
    default_settings = {
        "app_password": "hustlehq123",
        "password_protection": True,
    }

    if APP_SETTINGS_FILE.exists():
        try:
            saved_settings = json.loads(APP_SETTINGS_FILE.read_text(encoding="utf-8"))
            default_settings.update(saved_settings)
        except json.JSONDecodeError:
            pass

    return default_settings


def save_app_settings(settings):
    APP_SETTINGS_FILE.write_text(json.dumps(settings, indent=4), encoding="utf-8")


def require_password():
    settings = load_app_settings()

    if not settings.get("password_protection", True):
        return True

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    st.title("HustleHQ Login")
    st.subheader("Enter your app password to continue")

    entered_password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    if st.button("Unlock HustleHQ"):
        if entered_password == settings.get("app_password", "hustlehq123"):
            st.session_state["authenticated"] = True
            st.success("Access granted.")
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.info("Default password: hustlehq123. Change it in Settings after logging in.")

    return False



def logout_user():
    st.session_state["authenticated"] = False
    st.rerun()


def render_sidebar_summary():
    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()
    app_settings = load_app_settings()

    if income_records.empty:
        sidebar_income = 0
    else:
        sidebar_income = income_records["net_income"].sum()

    if expense_records.empty:
        sidebar_expenses = 0
    else:
        sidebar_expenses = expense_records["amount"].sum()

    sidebar_profit = sidebar_income - sidebar_expenses
    priority_goal = goals.get("priority_goal", "Clear debt first")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick snapshot")
    st.sidebar.metric("Income", f"£{sidebar_income:,.2f}")
    st.sidebar.metric("Expenses", f"£{sidebar_expenses:,.2f}")
    st.sidebar.metric("Profit", f"£{sidebar_profit:,.2f}")
    st.sidebar.markdown(f"**Priority:** {priority_goal}")

    if app_settings.get("password_protection", True):
        st.sidebar.success("Password protection active")
    else:
        st.sidebar.warning("Password protection off")

    if st.sidebar.button("Log out"):
        logout_user()

    st.sidebar.markdown("---")
    st.sidebar.caption("HustleHQ Phase 1 MVP")


st.sidebar.markdown("## 💼 HustleHQ")
st.sidebar.markdown("Side-Hustle Finance Command Centre")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Income",
        "Add Expense",
        "Evidence Centre",
        "HMRC Export",
        "Weekly Review",
        "Data Backup",
        "Restore Backup",
        "PDF Report",
        "Settings",
    ]
)

render_sidebar_summary()



# =========================
# PART 22 STYLE READABILITY FIX
# =========================

st.markdown(
    """
    <style>
    /* Main app text */
    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div {
        color: #0B1F33;
    }

    /* Sidebar stays white */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: white !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0px 6px 18px rgba(15, 23, 42, 0.08);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0B1F33 !important;
        font-weight: 800 !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #0B1F33 !important;
    }

    /* Dataframes and normal page text */
    .main,
    .main *,
    section.main *,
    div[data-testid="stAppViewContainer"] * {
        color: #0B1F33;
    }

    /* Keep alerts readable */
    div[data-testid="stAlert"] * {
        color: inherit !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# =========================
# FINAL HUSTLEHQ MOCKUP THEME
# =========================

st.markdown(
    """
    <style>
    /* Overall app background */
    .stApp {
        background: #F8FAFC !important;
        color: #0B1F33 !important;
    }

    /* Main readable text */
    .main,
    .main p,
    .main span,
    .main label,
    .main div,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] p,
    div[data-testid="stAppViewContainer"] span,
    div[data-testid="stAppViewContainer"] label {
        color: #0B1F33 !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #0B1F33 !important;
        font-weight: 800 !important;
    }

    h1 {
        font-size: 42px !important;
        letter-spacing: -0.03em !important;
    }

    h2, h3 {
        letter-spacing: -0.02em !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071827 0%, #0B1F33 55%, #064E3B 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMetric"] * {
        color: #FFFFFF !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: 0px 10px 28px rgba(15, 23, 42, 0.08) !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0B1F33 !important;
        font-weight: 900 !important;
        font-size: 32px !important;
    }

    /* Download buttons and normal buttons */
    div.stButton > button,
    div.stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #047857 0%, #065F46 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.1rem !important;
        font-weight: 800 !important;
        box-shadow: 0px 8px 18px rgba(4, 120, 87, 0.24) !important;
    }

    div.stButton > button *,
    div.stDownloadButton > button *,
    button[kind="primary"] *,
    button[kind="secondary"] *,
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="baseButton-primary"] *,
    [data-testid="stDownloadButton"] button *,
    [data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    [data-testid="stDownloadButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    div.stButton > button:focus,
    div.stDownloadButton > button:focus,
    [data-testid="stDownloadButton"] button:focus,
    [data-testid="stFormSubmitButton"] button:focus {
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0px 0px 0px 3px rgba(16, 185, 129, 0.25) !important;
    }

    /* Inputs */
    input,
    textarea,
    select,
    div[data-baseweb="select"] *,
    div[data-baseweb="input"] *,
    div[data-baseweb="textarea"] * {
        color: #0B1F33 !important;
    }

    input,
    textarea {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #0B1F33 !important;
        font-weight: 700 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #047857 !important;
        border-bottom-color: #047857 !important;
    }

    /* Alerts stay readable */
    div[data-testid="stAlert"] {
        border-radius: 14px !important;
        font-weight: 650 !important;
    }

    div[data-testid="stAlert"] * {
        color: inherit !important;
    }

    /* Data tables */
    div[data-testid="stDataFrame"] {
        background: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        overflow: hidden !important;
    }

    /* Horizontal spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }

    /* Make disabled-looking text readable */
    .stMarkdown,
    .stMarkdown *,
    .stText,
    .stText * {
        color: #0B1F33 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# =========================
# STREAMLIT TOP BAR READABILITY FIX
# =========================

st.markdown(
    """
    <style>
    /* Streamlit top header bar */
    header[data-testid="stHeader"] {
        background-color: #0B1F33 !important;
        color: #FFFFFF !important;
    }

    header[data-testid="stHeader"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Deploy button and menu in top-right */
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a,
    header[data-testid="stHeader"] span,
    header[data-testid="stHeader"] div {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    header[data-testid="stHeader"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    /* Top-left collapse/expand arrows */
    button[data-testid="collapsedControl"] {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    button[data-testid="collapsedControl"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    /* Make toolbar buttons easier to see */
    [data-testid="stToolbar"] {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    [data-testid="stToolbar"] * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# =========================
# FORM CONTROL READABILITY FIX
# =========================

st.markdown(
    """
    <style>
    /* Main input fields */
    input,
    textarea {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
    }

    /* Number input containers */
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Number input plus/minus buttons */
    div[data-testid="stNumberInput"] button {
        background-color: #E2E8F0 !important;
        color: #0B1F33 !important;
        border: 1px solid #CBD5E1 !important;
    }

    div[data-testid="stNumberInput"] button * {
        color: #0B1F33 !important;
        fill: #0B1F33 !important;
    }

    /* Select box outer container */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
    }

    /* Select box visible selected value */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] input {
        color: #0B1F33 !important;
    }

    div[data-baseweb="select"] svg {
        fill: #0B1F33 !important;
        color: #0B1F33 !important;
    }

    /* Dropdown menu options */
    ul[role="listbox"],
    ul[role="listbox"] li,
    div[role="listbox"],
    div[role="option"] {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
    }

    div[role="option"] *,
    li[role="option"] * {
        color: #0B1F33 !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover {
        background-color: #ECFDF5 !important;
        color: #0B1F33 !important;
    }

    /* Date input */
    div[data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Password field */
    input[type="password"] {
        background-color: #FFFFFF !important;
        color: #0B1F33 !important;
    }

    /* Labels stay dark and readable */
    label,
    label *,
    div[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] * {
        color: #0B1F33 !important;
        font-weight: 650 !important;
    }

    /* Form submit buttons stay emerald */
    [data-testid="stFormSubmitButton"] button,
    div.stButton > button,
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #047857 0%, #065F46 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
    }

    [data-testid="stFormSubmitButton"] button *,
    div.stButton > button *,
    div.stDownloadButton > button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if page == "Dashboard":
    st.title("Dashboard")
    st.subheader("Your side-hustle finance command centre")

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()

    if income_records.empty:
        total_gross_income = 0
        total_income = 0
        evidence_missing_income = 0
        pending_income = 0
    else:
        total_gross_income = income_records["gross_income"].sum()
        total_income = income_records["net_income"].sum()
        evidence_missing_income = income_records["evidence_link"].fillna("").eq("").sum()
        pending_income = income_records[income_records["paid_status"] != "Paid"]["net_income"].sum()

    if expense_records.empty:
        total_expenses = 0
        evidence_missing_expenses = 0
    else:
        total_expenses = expense_records["amount"].sum()
        evidence_missing_expenses = expense_records["receipt_link"].fillna("").eq("").sum()

    true_profit = total_income - total_expenses
    total_missing_evidence = evidence_missing_income + evidence_missing_expenses

    st.markdown("### Financial snapshot")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Gross income", f"£{total_gross_income:,.2f}")
    col2.metric("Net income", f"£{total_income:,.2f}")
    col3.metric("Expenses", f"£{total_expenses:,.2f}")
    col4.metric("True profit", f"£{true_profit:,.2f}")

    st.markdown("### Status checks")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        if true_profit > 0:
            st.success(f"Profitable: £{true_profit:,.2f} profit recorded.")
        elif true_profit == 0:
            st.warning("Breaking even. Add more income or reduce costs.")
        else:
            st.error(f"Loss position: £{abs(true_profit):,.2f} more spent than earned.")

    with status_col2:
        if total_gross_income >= 1000:
            st.warning("Trading allowance alert: gross income is over £1,000.")
        elif total_gross_income >= 750:
            st.warning("Gross income is approaching the £1,000 trading allowance threshold.")
        else:
            st.success("Gross income is currently below £1,000.")

    with status_col3:
        if total_missing_evidence > 0:
            st.warning(f"{total_missing_evidence} records need evidence.")
        else:
            st.success("Evidence records look complete.")

    if pending_income > 0:
        st.info(f"You have £{pending_income:,.2f} marked as pending or part-paid.")

    st.markdown("### Goal progress")

    debt_target = float(goals.get("debt_target", 1000))
    savings_target = float(goals.get("savings_target", 2000))
    monthly_income_goal = float(goals.get("monthly_income_goal", 500))
    emergency_buffer_goal = float(goals.get("emergency_buffer_goal", 500))
    priority_goal = goals.get("priority_goal", "Clear debt first")

    goal_col1, goal_col2, goal_col3, goal_col4 = st.columns(4)

    goal_col1.metric("Debt target", f"£{debt_target:,.2f}")
    goal_col2.metric("Savings target", f"£{savings_target:,.2f}")
    goal_col3.metric("Emergency buffer", f"£{emergency_buffer_goal:,.2f}")
    goal_col4.metric("Priority", priority_goal)

    debt_progress = min(true_profit / debt_target, 1) if debt_target > 0 else 0
    savings_progress = min(true_profit / savings_target, 1) if savings_target > 0 else 0
    buffer_progress = min(true_profit / emergency_buffer_goal, 1) if emergency_buffer_goal > 0 else 0
    monthly_progress = min(total_income / monthly_income_goal, 1) if monthly_income_goal > 0 else 0

    st.write("Debt target progress")
    st.progress(debt_progress)

    st.write("Savings target progress")
    st.progress(savings_progress)

    st.write("Emergency buffer progress")
    st.progress(buffer_progress)

    st.write("Monthly income goal progress")
    st.progress(monthly_progress)

    st.markdown("### Income by stream")

    if income_records.empty:
        st.info("No saved income records yet. Go to Add Income and save your first record.")
    else:
        income_by_stream = (
            income_records
            .groupby("income_stream")["net_income"]
            .sum()
            .reset_index()
            .sort_values("net_income", ascending=False)
        )

        income_chart = px.pie(
            income_by_stream,
            names="income_stream",
            values="net_income",
            hole=0.45,
        )

        st.plotly_chart(income_chart, use_container_width=True)

    st.markdown("### Expenses by category")

    if expense_records.empty:
        st.info("No saved expense records yet. Go to Add Expense and save your first expense.")
    else:
        expense_by_category = (
            expense_records
            .groupby("expense_category")["amount"]
            .sum()
            .reset_index()
            .sort_values("amount", ascending=False)
        )

        expense_chart = px.bar(
            expense_by_category,
            x="expense_category",
            y="amount",
            text_auto=True,
        )

        st.plotly_chart(expense_chart, use_container_width=True)

    st.markdown("### Monthly trend")

    monthly_income = pd.DataFrame()
    monthly_expenses = pd.DataFrame()

    if not income_records.empty:
        dated_income = income_records.dropna(subset=["date"]).copy()

        if not dated_income.empty:
            dated_income["month"] = dated_income["date"].dt.to_period("M").astype(str)
            monthly_income = (
                dated_income
                .groupby("month")["net_income"]
                .sum()
                .reset_index()
                .rename(columns={"net_income": "income"})
            )

    if not expense_records.empty:
        dated_expenses = expense_records.dropna(subset=["date"]).copy()

        if not dated_expenses.empty:
            dated_expenses["month"] = dated_expenses["date"].dt.to_period("M").astype(str)
            monthly_expenses = (
                dated_expenses
                .groupby("month")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "expenses"})
            )

    if monthly_income.empty and monthly_expenses.empty:
        st.info("Monthly trend will appear once your records include dates.")
    else:
        monthly_trend = pd.merge(
            monthly_income,
            monthly_expenses,
            on="month",
            how="outer"
        ).fillna(0)

        monthly_trend["profit"] = monthly_trend["income"] - monthly_trend["expenses"]
        monthly_trend = monthly_trend.sort_values("month")

        trend_chart = px.line(
            monthly_trend,
            x="month",
            y=["income", "expenses", "profit"],
            markers=True,
        )

        st.plotly_chart(trend_chart, use_container_width=True)

    st.markdown("### Dashboard recommendations")

    if income_records.empty and expense_records.empty:
        st.info("Add income and expense records to generate recommendations.")
    else:
        if true_profit > 0:
            st.success("Main recommendation: protect your profit. Do not scale expenses faster than income.")

            if not income_records.empty:
                best_income_stream = (
                    income_records
                    .groupby("income_stream")["net_income"]
                    .sum()
                    .reset_index()
                    .sort_values("net_income", ascending=False)
                    .iloc[0]["income_stream"]
                )

                st.write(f"Best income stream to focus on: **{best_income_stream}**")

            if not expense_records.empty:
                biggest_expense_category = (
                    expense_records
                    .groupby("expense_category")["amount"]
                    .sum()
                    .reset_index()
                    .sort_values("amount", ascending=False)
                    .iloc[0]["expense_category"]
                )

                st.write(f"Biggest cost area to monitor: **{biggest_expense_category}**")

        elif true_profit == 0:
            st.warning("Main recommendation: aim for your first positive profit week.")
        else:
            st.error("Main recommendation: pause new spending until your income catches up.")

    st.markdown("### Saved income records")

    if income_records.empty:
        st.warning("No income records saved yet.")
    else:
        st.dataframe(income_records, use_container_width=True)

    st.markdown("### Saved expense records")

    if expense_records.empty:
        st.warning("No expense records saved yet.")
    else:
        st.dataframe(expense_records, use_container_width=True)


elif page == "Add Income":
    st.title("Add Income")
    st.subheader("Add, edit and delete income records")

    income_stream_options = [
        "Vinted",
        "Legal Transcription",
        "YouTube",
        "Substack",
        "Etsy / Digital Products",
        "UGC Deals",
        "App Sales",
        "Website Builds",
        "Client Work",
        "Other",
    ]

    platform_options = [
        "Vinted",
        "TranscribeMe",
        "YouTube",
        "Substack",
        "Etsy",
        "Stripe",
        "PayPal",
        "Bank Transfer",
        "Cash",
        "Other",
    ]

    paid_status_options = ["Paid", "Pending", "Part-paid"]

    add_tab, edit_tab = st.tabs(["Add new income", "Edit or delete income"])

    with add_tab:
        with st.form("income_form"):
            income_date = st.date_input(
                "Date received / expected",
                value=date.today()
            )

            income_stream = st.selectbox(
                "Income stream",
                income_stream_options
            )

            platform = st.selectbox(
                "Platform",
                platform_options
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Sold black dress"
            )

            gross_income = st.number_input(
                "Gross income (£)",
                min_value=0.0,
                step=1.0
            )

            fees = st.number_input(
                "Platform/payment fees (£)",
                min_value=0.0,
                step=0.5
            )

            paid_status = st.selectbox(
                "Paid status",
                paid_status_options
            )

            evidence_link = st.text_input(
                "Evidence link / screenshot name",
                placeholder="Example: vinted_sale_001"
            )

            notes = st.text_area(
                "Notes",
                placeholder="Example: Bought for £8, sold for £25"
            )

            net_income = gross_income - fees

            st.info(f"Net income calculated: £{net_income:,.2f}")

            submitted = st.form_submit_button("Save income record")

        if submitted:
            record = {
                "date": income_date.isoformat(),
                "income_stream": income_stream,
                "platform": platform,
                "description": description,
                "gross_income": gross_income,
                "fees": fees,
                "net_income": net_income,
                "paid_status": paid_status,
                "evidence_link": evidence_link,
                "notes": notes,
            }

            save_income_record(record)

            st.success("Income record saved successfully.")
            st.balloons()

    with edit_tab:
        st.write("### Saved income records")

        income_records = load_income_records()

        if income_records.empty:
            st.warning("No income records saved yet.")
        else:
            st.dataframe(income_records, use_container_width=True)

            st.write("### Choose income record")

            income_options = {}

            for index, row in income_records.iterrows():
                income_name = row.get("income_stream", "Unknown")
                description_text = row.get("description", "")
                amount = float(row.get("net_income", 0))
                label = f"{index} | {income_name} | {description_text} | £{amount:,.2f}"
                income_options[label] = index

            selected_income_label = st.selectbox(
                "Choose an income record",
                list(income_options.keys())
            )

            selected_index = income_options[selected_income_label]
            selected_row = income_records.loc[selected_index]

            selected_date = selected_row.get("date")

            if pd.isna(selected_date):
                selected_date_value = date.today()
            else:
                selected_date_value = pd.to_datetime(selected_date).date()

            current_income_stream = selected_row.get("income_stream", "Other")
            current_platform = selected_row.get("platform", "Other")
            current_paid_status = selected_row.get("paid_status", "Paid")

            if current_income_stream not in income_stream_options:
                current_income_stream = "Other"

            if current_platform not in platform_options:
                current_platform = "Other"

            if current_paid_status not in paid_status_options:
                current_paid_status = "Paid"

            with st.form("edit_income_form"):
                edited_date = st.date_input(
                    "Edit date",
                    value=selected_date_value
                )

                edited_income_stream = st.selectbox(
                    "Edit income stream",
                    income_stream_options,
                    index=income_stream_options.index(current_income_stream)
                )

                edited_platform = st.selectbox(
                    "Edit platform",
                    platform_options,
                    index=platform_options.index(current_platform)
                )

                edited_description = st.text_input(
                    "Edit description",
                    value=str(selected_row.get("description", ""))
                )

                edited_gross_income = st.number_input(
                    "Edit gross income (£)",
                    min_value=0.0,
                    step=1.0,
                    value=float(selected_row.get("gross_income", 0))
                )

                edited_fees = st.number_input(
                    "Edit fees (£)",
                    min_value=0.0,
                    step=0.5,
                    value=float(selected_row.get("fees", 0))
                )

                edited_paid_status = st.selectbox(
                    "Edit paid status",
                    paid_status_options,
                    index=paid_status_options.index(current_paid_status)
                )

                edited_evidence_link = st.text_input(
                    "Edit evidence link",
                    value=str(selected_row.get("evidence_link", ""))
                )

                edited_notes = st.text_area(
                    "Edit notes",
                    value=str(selected_row.get("notes", ""))
                )

                edited_net_income = edited_gross_income - edited_fees

                st.info(f"Updated net income: £{edited_net_income:,.2f}")

                update_submitted = st.form_submit_button("Update income record")

            if update_submitted:
                income_records.loc[selected_index, "date"] = edited_date.isoformat()
                income_records.loc[selected_index, "income_stream"] = edited_income_stream
                income_records.loc[selected_index, "platform"] = edited_platform
                income_records.loc[selected_index, "description"] = edited_description
                income_records.loc[selected_index, "gross_income"] = edited_gross_income
                income_records.loc[selected_index, "fees"] = edited_fees
                income_records.loc[selected_index, "net_income"] = edited_net_income
                income_records.loc[selected_index, "paid_status"] = edited_paid_status
                income_records.loc[selected_index, "evidence_link"] = edited_evidence_link
                income_records.loc[selected_index, "notes"] = edited_notes

                income_records.to_csv(INCOME_FILE, index=False)

                st.success("Income record updated successfully.")
                st.rerun()

            st.write("### Delete income record")

            if st.button("Delete selected income record"):
                income_records = income_records.drop(index=selected_index).reset_index(drop=True)
                income_records.to_csv(INCOME_FILE, index=False)

                st.success("Income record deleted successfully.")
                st.rerun()


elif page == "Add Expense":
    st.title("Add Expense")
    st.subheader("Add, edit and delete expense records")

    expense_category_options = [
        "Stock",
        "Postage",
        "Packaging",
        "Platform Fees",
        "Software",
        "Equipment",
        "Travel",
        "Courses / Learning",
        "Subscriptions",
        "Marketing",
        "Other",
    ]

    linked_stream_options = [
        "Vinted",
        "Legal Transcription",
        "YouTube",
        "Substack",
        "Etsy / Digital Products",
        "UGC Deals",
        "App Sales",
        "Website Builds",
        "Client Work",
        "Other",
    ]

    add_tab, edit_tab = st.tabs(["Add new expense", "Edit or delete expense"])

    with add_tab:
        with st.form("expense_form"):
            expense_date = st.date_input(
                "Date paid / incurred",
                value=date.today()
            )

            expense_category = st.selectbox(
                "Expense category",
                expense_category_options
            )

            linked_stream = st.selectbox(
                "Linked income stream",
                linked_stream_options
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Postage for Vinted parcel"
            )

            amount = st.number_input(
                "Amount (£)",
                min_value=0.0,
                step=0.5
            )

            receipt_link = st.text_input(
                "Receipt link / screenshot name",
                placeholder="Example: royalmail_receipt_001"
            )

            notes = st.text_area(
                "Notes",
                placeholder="Example: Postage cost linked to black dress sale"
            )

            submitted = st.form_submit_button("Save expense record")

        if submitted:
            record = {
                "date": expense_date.isoformat(),
                "expense_category": expense_category,
                "linked_stream": linked_stream,
                "description": description,
                "amount": amount,
                "receipt_link": receipt_link,
                "notes": notes,
            }

            save_expense_record(record)

            st.success("Expense record saved successfully.")
            st.balloons()

    with edit_tab:
        st.write("### Saved expense records")

        expense_records = load_expense_records()

        if expense_records.empty:
            st.warning("No expense records saved yet.")
        else:
            st.dataframe(expense_records, use_container_width=True)

            st.write("### Choose expense record")

            expense_options = {}

            for index, row in expense_records.iterrows():
                category_name = row.get("expense_category", "Unknown")
                description_text = row.get("description", "")
                amount = float(row.get("amount", 0))
                label = f"{index} | {category_name} | {description_text} | £{amount:,.2f}"
                expense_options[label] = index

            selected_expense_label = st.selectbox(
                "Choose an expense record",
                list(expense_options.keys())
            )

            selected_index = expense_options[selected_expense_label]
            selected_row = expense_records.loc[selected_index]

            selected_date = selected_row.get("date")

            if pd.isna(selected_date):
                selected_date_value = date.today()
            else:
                selected_date_value = pd.to_datetime(selected_date).date()

            current_category = selected_row.get("expense_category", "Other")
            current_stream = selected_row.get("linked_stream", "Other")

            if current_category not in expense_category_options:
                current_category = "Other"

            if current_stream not in linked_stream_options:
                current_stream = "Other"

            with st.form("edit_expense_form"):
                edited_date = st.date_input(
                    "Edit date",
                    value=selected_date_value
                )

                edited_expense_category = st.selectbox(
                    "Edit expense category",
                    expense_category_options,
                    index=expense_category_options.index(current_category)
                )

                edited_linked_stream = st.selectbox(
                    "Edit linked income stream",
                    linked_stream_options,
                    index=linked_stream_options.index(current_stream)
                )

                edited_description = st.text_input(
                    "Edit description",
                    value=str(selected_row.get("description", ""))
                )

                edited_amount = st.number_input(
                    "Edit amount (£)",
                    min_value=0.0,
                    step=0.5,
                    value=float(selected_row.get("amount", 0))
                )

                edited_receipt_link = st.text_input(
                    "Edit receipt link",
                    value=str(selected_row.get("receipt_link", ""))
                )

                edited_notes = st.text_area(
                    "Edit notes",
                    value=str(selected_row.get("notes", ""))
                )

                update_submitted = st.form_submit_button("Update expense record")

            if update_submitted:
                expense_records.loc[selected_index, "date"] = edited_date.isoformat()
                expense_records.loc[selected_index, "expense_category"] = edited_expense_category
                expense_records.loc[selected_index, "linked_stream"] = edited_linked_stream
                expense_records.loc[selected_index, "description"] = edited_description
                expense_records.loc[selected_index, "amount"] = edited_amount
                expense_records.loc[selected_index, "receipt_link"] = edited_receipt_link
                expense_records.loc[selected_index, "notes"] = edited_notes

                expense_records.to_csv(EXPENSE_FILE, index=False)

                st.success("Expense record updated successfully.")
                st.rerun()

            st.write("### Delete expense record")

            if st.button("Delete selected expense record"):
                expense_records = expense_records.drop(index=selected_index).reset_index(drop=True)
                expense_records.to_csv(EXPENSE_FILE, index=False)

                st.success("Expense record deleted successfully.")
                st.rerun()


elif page == "Evidence Centre":
    st.title("Evidence Centre")
    st.subheader("Review missing evidence, unpaid income and records that need attention")

    income_records = load_income_records()
    expense_records = load_expense_records()

    income_review = add_income_status_columns(income_records)
    expense_review = add_expense_status_columns(expense_records)

    st.markdown("### Review summary")

    income_problem_count = 0
    expense_problem_count = 0
    complete_income_count = 0
    complete_expense_count = 0

    if not income_review.empty:
        income_problem_count = len(income_review[income_review["record_status"] != "Complete"])
        complete_income_count = len(income_review[income_review["record_status"] == "Complete"])

    if not expense_review.empty:
        expense_problem_count = len(expense_review[expense_review["record_status"] != "Complete"])
        complete_expense_count = len(expense_review[expense_review["record_status"] == "Complete"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Income issues", income_problem_count)
    col2.metric("Expense issues", expense_problem_count)
    col3.metric("Complete income records", complete_income_count)
    col4.metric("Complete expense records", complete_expense_count)

    st.markdown("---")

    st.markdown("### Income record status")

    if income_review.empty:
        st.info("No income records saved yet.")
    else:
        income_status_summary = (
            income_review
            .groupby("record_status")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        st.dataframe(income_status_summary, use_container_width=True)

        income_filter = st.selectbox(
            "Filter income records by status",
            [
                "All",
                "Complete",
                "Missing evidence",
                "Pending payment",
                "Needs review",
            ]
        )

        filtered_income_review = income_review.copy()

        if income_filter != "All":
            filtered_income_review = filtered_income_review[
                filtered_income_review["record_status"] == income_filter
            ]

        st.dataframe(filtered_income_review, use_container_width=True)

        if income_problem_count == 0:
            st.success("All income records look complete.")
        else:
            st.warning("Some income records need attention before export or tax review.")

    st.markdown("---")

    st.markdown("### Expense record status")

    if expense_review.empty:
        st.info("No expense records saved yet.")
    else:
        expense_status_summary = (
            expense_review
            .groupby("record_status")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        st.dataframe(expense_status_summary, use_container_width=True)

        expense_filter = st.selectbox(
            "Filter expense records by status",
            [
                "All",
                "Complete",
                "Missing receipt",
                "Needs review",
            ]
        )

        filtered_expense_review = expense_review.copy()

        if expense_filter != "All":
            filtered_expense_review = filtered_expense_review[
                filtered_expense_review["record_status"] == expense_filter
            ]

        st.dataframe(filtered_expense_review, use_container_width=True)

        if expense_problem_count == 0:
            st.success("All expense records look complete.")
        else:
            st.warning("Some expense records need receipts or review before export.")

    st.markdown("---")

    st.markdown("### What these labels mean")

    st.write("**Complete** — record has the main details and evidence/receipt.")
    st.write("**Missing evidence** — income record has no screenshot, payout proof or evidence link.")
    st.write("**Missing receipt** — expense record has no receipt link or screenshot name.")
    st.write("**Pending payment** — income is marked as Pending or Part-paid.")
    st.write("**Needs review** — amount or description needs checking.")


elif page == "HMRC Export":
    st.title("HMRC Export")
    st.subheader("Create a bookkeeping report pack for your side-hustle records")

    st.warning(
        "This app helps organise records. It does not file anything to HMRC and it is not tax advice."
    )

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()

    tax_year = st.selectbox(
        "Select report period",
        [
            "2026/27",
            "2025/26",
            "2024/25",
            "All records",
        ]
    )

    filtered_income = income_records.copy()
    filtered_expenses = expense_records.copy()

    if tax_year != "All records":
        start_year = int(tax_year.split("/")[0])
        tax_start = pd.Timestamp(start_year, 4, 6)
        tax_end = pd.Timestamp(start_year + 1, 4, 5)

        if not filtered_income.empty:
            filtered_income = filtered_income[
                (filtered_income["date"] >= tax_start) &
                (filtered_income["date"] <= tax_end)
            ]

        if not filtered_expenses.empty:
            filtered_expenses = filtered_expenses[
                (filtered_expenses["date"] >= tax_start) &
                (filtered_expenses["date"] <= tax_end)
            ]

    if filtered_income.empty:
        gross_income = 0
        fees = 0
        net_income = 0
        income_count = 0
        pending_income = 0
    else:
        gross_income = filtered_income["gross_income"].sum()
        fees = filtered_income["fees"].sum()
        net_income = filtered_income["net_income"].sum()
        income_count = len(filtered_income)
        pending_income = filtered_income[filtered_income["paid_status"] != "Paid"]["net_income"].sum()

    if filtered_expenses.empty:
        total_expenses = 0
        expense_count = 0
    else:
        total_expenses = filtered_expenses["amount"].sum()
        expense_count = len(filtered_expenses)

    true_profit = net_income - total_expenses

    income_review = add_income_status_columns(filtered_income)
    expense_review = add_expense_status_columns(filtered_expenses)

    if income_review.empty:
        income_issues = pd.DataFrame()
        income_issue_count = 0
        complete_income_count = 0
    else:
        income_issues = income_review[income_review["record_status"] != "Complete"]
        income_issue_count = len(income_issues)
        complete_income_count = len(income_review[income_review["record_status"] == "Complete"])

    if expense_review.empty:
        expense_issues = pd.DataFrame()
        expense_issue_count = 0
        complete_expense_count = 0
    else:
        expense_issues = expense_review[expense_review["record_status"] != "Complete"]
        expense_issue_count = len(expense_issues)
        complete_expense_count = len(expense_review[expense_review["record_status"] == "Complete"])

    st.markdown("### Report summary")

    summary = pd.DataFrame(
        {
            "Metric": [
                "Selected period",
                "Gross income",
                "Platform/payment fees",
                "Net income",
                "Tracked expenses",
                "True profit before tax",
                "Pending or part-paid income",
                "Income records",
                "Expense records",
                "Complete income records",
                "Complete expense records",
                "Income records needing review",
                "Expense records needing review",
                "Debt target",
                "Savings target",
                "Emergency buffer goal",
                "Monthly income goal",
                "Priority goal",
            ],
            "Amount / Count": [
                tax_year,
                f"£{gross_income:,.2f}",
                f"£{fees:,.2f}",
                f"£{net_income:,.2f}",
                f"£{total_expenses:,.2f}",
                f"£{true_profit:,.2f}",
                f"£{pending_income:,.2f}",
                income_count,
                expense_count,
                complete_income_count,
                complete_expense_count,
                income_issue_count,
                expense_issue_count,
                f"£{float(goals.get('debt_target', 0)):,.2f}",
                f"£{float(goals.get('savings_target', 0)):,.2f}",
                f"£{float(goals.get('emergency_buffer_goal', 0)):,.2f}",
                f"£{float(goals.get('monthly_income_goal', 0)):,.2f}",
                goals.get("priority_goal", ""),
            ],
        }
    )

    st.dataframe(summary, use_container_width=True)

    st.markdown("### Profit by side hustle")

    if filtered_income.empty:
        profit_by_stream = pd.DataFrame(
            columns=["side_hustle", "income", "expenses", "profit"]
        )
        st.info("No income records found for this period.")
    else:
        income_by_stream = (
            filtered_income
            .groupby("income_stream")["net_income"]
            .sum()
            .reset_index()
            .rename(columns={"income_stream": "side_hustle", "net_income": "income"})
        )

        if filtered_expenses.empty:
            expense_by_stream = pd.DataFrame(
                {
                    "side_hustle": income_by_stream["side_hustle"],
                    "expenses": 0,
                }
            )
        else:
            expense_by_stream = (
                filtered_expenses
                .groupby("linked_stream")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"linked_stream": "side_hustle", "amount": "expenses"})
            )

        profit_by_stream = pd.merge(
            income_by_stream,
            expense_by_stream,
            on="side_hustle",
            how="outer"
        ).fillna(0)

        profit_by_stream["profit"] = profit_by_stream["income"] - profit_by_stream["expenses"]
        profit_by_stream = profit_by_stream.sort_values("profit", ascending=False)

        st.dataframe(profit_by_stream, use_container_width=True)

    st.markdown("### Record review")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Income issues", income_issue_count)

        if income_issue_count > 0:
            st.warning("Income records need review before relying on this report.")
            st.dataframe(income_issues, use_container_width=True)
        else:
            st.success("No income review issues found for this period.")

    with col2:
        st.metric("Expense issues", expense_issue_count)

        if expense_issue_count > 0:
            st.warning("Expense records need review before relying on this report.")
            st.dataframe(expense_issues, use_container_width=True)
        else:
            st.success("No expense review issues found for this period.")

    st.markdown("### Download report pack")

    safe_tax_year = tax_year.replace("/", "-").replace(" ", "_").lower()

    goal_settings = pd.DataFrame(
        {
            "Setting": [
                "Debt target",
                "Savings target",
                "Emergency buffer goal",
                "Monthly income goal",
                "Priority goal",
            ],
            "Value": [
                goals.get("debt_target", 0),
                goals.get("savings_target", 0),
                goals.get("emergency_buffer_goal", 0),
                goals.get("monthly_income_goal", 0),
                goals.get("priority_goal", ""),
            ],
        }
    )

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(
            f"hustlehq_summary_{safe_tax_year}.csv",
            summary.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_income_records_{safe_tax_year}.csv",
            filtered_income.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_expense_records_{safe_tax_year}.csv",
            filtered_expenses.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_profit_by_side_hustle_{safe_tax_year}.csv",
            profit_by_stream.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_income_review_issues_{safe_tax_year}.csv",
            income_issues.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_expense_review_issues_{safe_tax_year}.csv",
            expense_issues.to_csv(index=False)
        )

        zip_file.writestr(
            f"hustlehq_goal_settings_{safe_tax_year}.csv",
            goal_settings.to_csv(index=False)
        )

    st.download_button(
        "Download full report pack ZIP",
        data=zip_buffer.getvalue(),
        file_name=f"hustlehq_report_pack_{safe_tax_year}.zip",
        mime="application/zip",
    )

    st.markdown("### Individual downloads")

    st.download_button(
        "Download summary CSV",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name=f"hustlehq_summary_{safe_tax_year}.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download income records CSV",
        data=filtered_income.to_csv(index=False).encode("utf-8"),
        file_name=f"hustlehq_income_records_{safe_tax_year}.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download expense records CSV",
        data=filtered_expenses.to_csv(index=False).encode("utf-8"),
        file_name=f"hustlehq_expense_records_{safe_tax_year}.csv",
        mime="text/csv",
    )

    st.markdown("### Export checks")

    if income_count == 0 and expense_count == 0:
        st.warning("No records found for this selected period.")
    else:
        st.success("Report pack generated for the selected period.")

    if income_issue_count > 0 or expense_issue_count > 0:
        st.warning("The report pack includes review issue files. Check those before using the records.")
    else:
        st.success("No review issues detected for this selected period.")

    if tax_year != "All records":
        st.info("UK tax years usually run from 6 April to 5 April. This app filters using that date range.")
elif page == "Weekly Review":
    st.title("Weekly Review")
    st.subheader("Review what made money, what cost money and what is worth focusing on next")

    income_records = load_income_records()
    expense_records = load_expense_records()

    if income_records.empty:
        total_income = 0
    else:
        total_income = income_records["net_income"].sum()

    if expense_records.empty:
        total_expenses = 0
    else:
        total_expenses = expense_records["amount"].sum()

    true_profit = total_income - total_expenses

    col1, col2, col3 = st.columns(3)

    col1.metric("Total net income", f"£{total_income:,.2f}")
    col2.metric("Total expenses", f"£{total_expenses:,.2f}")
    col3.metric("Current profit", f"£{true_profit:,.2f}")

    st.markdown("### Profit by side hustle")

    if income_records.empty:
        st.info("Add income records to calculate profit by side hustle.")
    else:
        income_by_stream = (
            income_records
            .groupby("income_stream")["net_income"]
            .sum()
            .reset_index()
            .rename(columns={"income_stream": "side_hustle", "net_income": "income"})
        )

        if expense_records.empty:
            expense_by_stream = pd.DataFrame(
                {
                    "side_hustle": income_by_stream["side_hustle"],
                    "expenses": 0,
                }
            )
        else:
            expense_by_stream = (
                expense_records
                .groupby("linked_stream")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"linked_stream": "side_hustle", "amount": "expenses"})
            )

        profit_by_stream = pd.merge(
            income_by_stream,
            expense_by_stream,
            on="side_hustle",
            how="outer"
        ).fillna(0)

        profit_by_stream["profit"] = profit_by_stream["income"] - profit_by_stream["expenses"]

        profit_by_stream = profit_by_stream.sort_values("profit", ascending=False)

        st.dataframe(profit_by_stream, use_container_width=True)

        profit_chart = px.bar(
            profit_by_stream,
            x="side_hustle",
            y="profit",
            text_auto=True,
            title="Profit by side hustle"
        )

        st.plotly_chart(profit_chart, use_container_width=True)

        best_side_hustle = profit_by_stream.iloc[0]["side_hustle"]
        best_profit = profit_by_stream.iloc[0]["profit"]

        worst_side_hustle = profit_by_stream.iloc[-1]["side_hustle"]
        worst_profit = profit_by_stream.iloc[-1]["profit"]

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"Best performer: {best_side_hustle} with £{best_profit:,.2f} profit.")

        with col2:
            if worst_profit < 0:
                st.error(f"Weakest performer: {worst_side_hustle} is currently at £{worst_profit:,.2f}.")
            else:
                st.warning(f"Lowest performer: {worst_side_hustle} with £{worst_profit:,.2f} profit.")

        st.markdown("### Focus recommendation")

        if best_profit > 0:
            st.write(f"Your strongest current focus should be: **{best_side_hustle}**.")
            st.write("Put more time into the side hustle already proving it can produce profit.")

        if worst_profit < 0:
            st.write(f"Review **{worst_side_hustle}** before spending more money on it.")
            st.write("It is currently costing more than it has made.")

        if total_income > 0:
            profit_margin = (true_profit / total_income) * 100
        else:
            profit_margin = 0

        st.metric("Overall profit margin", f"{profit_margin:,.1f}%")

        if profit_margin >= 70:
            st.success("Very strong margin. Your costs are low compared with income.")
        elif profit_margin >= 30:
            st.warning("Decent margin. Keep watching costs as income grows.")
        elif profit_margin > 0:
            st.warning("Thin margin. You are profitable, but costs may be eating too much income.")
        else:
            st.error("Negative margin. Expenses are currently higher than income.")

    st.markdown("---")

    st.markdown("### Income performance")

    if income_records.empty:
        st.info("No income records yet. Add income first.")
    else:
        income_summary = (
            income_records
            .groupby("income_stream")["net_income"]
            .sum()
            .reset_index()
            .sort_values("net_income", ascending=False)
        )

        st.dataframe(income_summary, use_container_width=True)

        best_stream = income_summary.iloc[0]["income_stream"]
        best_amount = income_summary.iloc[0]["net_income"]

        st.success(f"Your strongest income stream by income is {best_stream}, with £{best_amount:,.2f} recorded.")

    st.markdown("### Expense performance")

    if expense_records.empty:
        st.info("No expense records yet.")
    else:
        expense_summary = (
            expense_records
            .groupby("expense_category")["amount"]
            .sum()
            .reset_index()
            .sort_values("amount", ascending=False)
        )

        st.dataframe(expense_summary, use_container_width=True)

        biggest_category = expense_summary.iloc[0]["expense_category"]
        biggest_amount = expense_summary.iloc[0]["amount"]

        st.warning(f"Your biggest cost category is {biggest_category}, with £{biggest_amount:,.2f} recorded.")

    st.markdown("### Action recommendations")

    if income_records.empty and expense_records.empty:
        st.info("Add at least one income record and one expense record to generate recommendations.")

    elif true_profit > 0:
        st.success("You are currently profitable. Your next move is to increase the income stream with the strongest return.")

    elif true_profit == 0:
        st.warning("You are breaking even. The next goal is to increase income or reduce unnecessary costs.")

    else:
        st.error("You are currently spending more than you are earning. Review costs before scaling.")
elif page == "Restore Backup":
    st.title("Restore Backup")
    st.subheader("Restore HustleHQ records from a backup ZIP")

    st.warning(
        "This page can replace your current income records, expense records, goal settings and app settings. "
        "Only restore a backup file you trust."
    )

    st.markdown("### Upload backup ZIP")

    uploaded_backup = st.file_uploader(
        "Upload your full HustleHQ backup ZIP",
        type=["zip"]
    )

    confirm_restore = st.checkbox(
        "I understand this will replace my current app data with the uploaded backup."
    )

    if uploaded_backup is not None:
        st.info("Backup file uploaded. Tick the confirmation box, then click restore.")

        if st.button("Restore from backup ZIP"):
            if not confirm_restore:
                st.error("Tick the confirmation box before restoring.")
            else:
                restored_items = []

                try:
                    with ZipFile(uploaded_backup, "r") as zip_file:
                        zip_names = zip_file.namelist()

                        if "hustlehq_income_records_backup.csv" in zip_names:
                            income_data = zip_file.read("hustlehq_income_records_backup.csv")
                            INCOME_FILE.write_bytes(income_data)
                            restored_items.append("Income records")

                        if "hustlehq_expense_records_backup.csv" in zip_names:
                            expense_data = zip_file.read("hustlehq_expense_records_backup.csv")
                            EXPENSE_FILE.write_bytes(expense_data)
                            restored_items.append("Expense records")

                        if "goals.json" in zip_names:
                            goals_data = zip_file.read("goals.json").decode("utf-8")
                            GOALS_FILE.write_text(goals_data, encoding="utf-8")
                            restored_items.append("Goal settings")

                        elif "hustlehq_goal_settings_backup.csv" in zip_names:
                            goals_csv = pd.read_csv(zip_file.open("hustlehq_goal_settings_backup.csv"))
                            restored_goals = {}

                            if "Setting" in goals_csv.columns and "Value" in goals_csv.columns:
                                for _, row in goals_csv.iterrows():
                                    key = str(row["Setting"])
                                    value = row["Value"]

                                    try:
                                        value = float(value)
                                    except (ValueError, TypeError):
                                        value = str(value)

                                    restored_goals[key] = value

                                save_goal_settings(restored_goals)
                                restored_items.append("Goal settings")

                        if "app_settings.json" in zip_names:
                            app_settings_data = zip_file.read("app_settings.json").decode("utf-8")
                            APP_SETTINGS_FILE.write_text(app_settings_data, encoding="utf-8")
                            restored_items.append("App/password settings")

                        elif "hustlehq_app_settings_backup.csv" in zip_names:
                            app_settings_csv = pd.read_csv(zip_file.open("hustlehq_app_settings_backup.csv"))
                            restored_app_settings = {}

                            if "Setting" in app_settings_csv.columns and "Value" in app_settings_csv.columns:
                                for _, row in app_settings_csv.iterrows():
                                    key = str(row["Setting"])
                                    value = row["Value"]

                                    if str(value).lower() == "true":
                                        value = True
                                    elif str(value).lower() == "false":
                                        value = False
                                    else:
                                        value = str(value)

                                    restored_app_settings[key] = value

                                save_app_settings(restored_app_settings)
                                restored_items.append("App/password settings")

                    if restored_items:
                        st.success("Backup restored successfully.")
                        st.write("Restored:")
                        for item in restored_items:
                            st.write(f"- {item}")

                        st.info("Refresh the app to reload the restored records.")
                    else:
                        st.warning("No recognised HustleHQ backup files were found inside this ZIP.")

                except Exception as error:
                    st.error("Restore failed.")
                    st.exception(error)

    st.markdown("---")

    st.markdown("### Restore checklist")

    st.write("- Use backups downloaded from the Data Backup page.")
    st.write("- Restoring replaces the current app records.")
    st.write("- Refresh the app after restoring.")
    st.write("- Download a fresh backup after checking the restored data.")

    st.markdown("### Safer option")

    st.info(
        "Before restoring, download a current backup from the Data Backup page. "
        "That gives you a fallback if you upload the wrong ZIP."
    )



elif page == "PDF Report":
    st.title("PDF Report")
    st.subheader("Generate a clean PDF summary of your HustleHQ records")

    st.warning(
        "This PDF is for personal bookkeeping and review. It does not file anything to HMRC and it is not tax advice."
    )

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()

    report_period = st.selectbox(
        "Select report period",
        [
            "2026/27",
            "2025/26",
            "2024/25",
            "All records",
        ],
        key="pdf_report_period"
    )

    filtered_income = income_records.copy()
    filtered_expenses = expense_records.copy()

    if report_period != "All records":
        start_year = int(report_period.split("/")[0])
        tax_start = pd.Timestamp(start_year, 4, 6)
        tax_end = pd.Timestamp(start_year + 1, 4, 5)

        if not filtered_income.empty:
            filtered_income = filtered_income[
                (filtered_income["date"] >= tax_start) &
                (filtered_income["date"] <= tax_end)
            ]

        if not filtered_expenses.empty:
            filtered_expenses = filtered_expenses[
                (filtered_expenses["date"] >= tax_start) &
                (filtered_expenses["date"] <= tax_end)
            ]

    if filtered_income.empty:
        gross_income = 0
        fees = 0
        net_income = 0
        pending_income = 0
        income_count = 0
    else:
        gross_income = filtered_income["gross_income"].sum()
        fees = filtered_income["fees"].sum()
        net_income = filtered_income["net_income"].sum()
        pending_income = filtered_income[filtered_income["paid_status"] != "Paid"]["net_income"].sum()
        income_count = len(filtered_income)

    if filtered_expenses.empty:
        total_expenses = 0
        expense_count = 0
    else:
        total_expenses = filtered_expenses["amount"].sum()
        expense_count = len(filtered_expenses)

    true_profit = net_income - total_expenses

    income_review = add_income_status_columns(filtered_income)
    expense_review = add_expense_status_columns(filtered_expenses)

    if income_review.empty:
        income_issues = pd.DataFrame()
        income_issue_count = 0
    else:
        income_issues = income_review[income_review["record_status"] != "Complete"]
        income_issue_count = len(income_issues)

    if expense_review.empty:
        expense_issues = pd.DataFrame()
        expense_issue_count = 0
    else:
        expense_issues = expense_review[expense_review["record_status"] != "Complete"]
        expense_issue_count = len(expense_issues)

    if filtered_income.empty:
        profit_by_stream = pd.DataFrame(
            columns=["side_hustle", "income", "expenses", "profit"]
        )
    else:
        income_by_stream = (
            filtered_income
            .groupby("income_stream")["net_income"]
            .sum()
            .reset_index()
            .rename(columns={"income_stream": "side_hustle", "net_income": "income"})
        )

        if filtered_expenses.empty:
            expense_by_stream = pd.DataFrame(
                {
                    "side_hustle": income_by_stream["side_hustle"],
                    "expenses": 0,
                }
            )
        else:
            expense_by_stream = (
                filtered_expenses
                .groupby("linked_stream")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"linked_stream": "side_hustle", "amount": "expenses"})
            )

        profit_by_stream = pd.merge(
            income_by_stream,
            expense_by_stream,
            on="side_hustle",
            how="outer"
        ).fillna(0)

        profit_by_stream["profit"] = profit_by_stream["income"] - profit_by_stream["expenses"]
        profit_by_stream = profit_by_stream.sort_values("profit", ascending=False)

    summary = pd.DataFrame(
        {
            "Metric": [
                "Report period",
                "Gross income",
                "Platform/payment fees",
                "Net income",
                "Tracked expenses",
                "True profit before tax",
                "Pending or part-paid income",
                "Income records",
                "Expense records",
                "Income records needing review",
                "Expense records needing review",
                "Debt target",
                "Savings target",
                "Emergency buffer goal",
                "Monthly income goal",
                "Priority goal",
            ],
            "Value": [
                report_period,
                f"GBP {gross_income:,.2f}",
                f"GBP {fees:,.2f}",
                f"GBP {net_income:,.2f}",
                f"GBP {total_expenses:,.2f}",
                f"GBP {true_profit:,.2f}",
                f"GBP {pending_income:,.2f}",
                income_count,
                expense_count,
                income_issue_count,
                expense_issue_count,
                f"GBP {float(goals.get('debt_target', 0)):,.2f}",
                f"GBP {float(goals.get('savings_target', 0)):,.2f}",
                f"GBP {float(goals.get('emergency_buffer_goal', 0)):,.2f}",
                f"GBP {float(goals.get('monthly_income_goal', 0)):,.2f}",
                goals.get("priority_goal", ""),
            ],
        }
    )

    st.markdown("### PDF report preview")
    st.dataframe(summary, use_container_width=True)

    st.markdown("### Profit by side hustle preview")

    if profit_by_stream.empty:
        st.info("No profit-by-side-hustle data for this period yet.")
    else:
        st.dataframe(profit_by_stream, use_container_width=True)

    def draw_text_line(pdf, text_value, x, y, size=10, bold=False):
        font_name = "Helvetica-Bold" if bold else "Helvetica"
        pdf.setFont(font_name, size)
        pdf.drawString(x, y, str(text_value))

    def draw_wrapped_text(pdf, text_value, x, y, max_chars=95, size=9):
        words = str(text_value).split()
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()

            if len(test_line) <= max_chars:
                line = test_line
            else:
                draw_text_line(pdf, line, x, y, size=size)
                y -= 5 * mm
                line = word

        if line:
            draw_text_line(pdf, line, x, y, size=size)
            y -= 5 * mm

        return y

    def start_new_page(pdf):
        pdf.showPage()
        return A4[1] - 22 * mm

    def build_pdf_report():
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        page_width, page_height = A4
        left = 18 * mm
        right = page_width - 18 * mm
        y = page_height - 22 * mm

        pdf.setTitle("HustleHQ PDF Report")

        draw_text_line(pdf, "HustleHQ", left, y, size=22, bold=True)
        y -= 9 * mm

        draw_text_line(pdf, "Side-Hustle Finance Report", left, y, size=14, bold=True)
        y -= 8 * mm

        draw_text_line(pdf, f"Report period: {report_period}", left, y, size=10)
        y -= 6 * mm

        draw_text_line(pdf, "This report is for personal bookkeeping and review. It is not tax advice.", left, y, size=9)
        y -= 10 * mm

        draw_text_line(pdf, "Financial Summary", left, y, size=14, bold=True)
        y -= 7 * mm

        for _, row in summary.iterrows():
            if y < 25 * mm:
                y = start_new_page(pdf)

            draw_text_line(pdf, f"{row['Metric']}: {row['Value']}", left, y, size=9)
            y -= 5 * mm

        y -= 5 * mm

        if y < 35 * mm:
            y = start_new_page(pdf)

        draw_text_line(pdf, "Profit by Side Hustle", left, y, size=14, bold=True)
        y -= 7 * mm

        if profit_by_stream.empty:
            draw_text_line(pdf, "No side-hustle profit data available for this period.", left, y, size=9)
            y -= 6 * mm
        else:
            for _, row in profit_by_stream.iterrows():
                if y < 25 * mm:
                    y = start_new_page(pdf)

                line = (
                    f"{row['side_hustle']} | "
                    f"Income: GBP {float(row['income']):,.2f} | "
                    f"Expenses: GBP {float(row['expenses']):,.2f} | "
                    f"Profit: GBP {float(row['profit']):,.2f}"
                )

                y = draw_wrapped_text(pdf, line, left, y, max_chars=95, size=9)

        y -= 5 * mm

        if y < 35 * mm:
            y = start_new_page(pdf)

        draw_text_line(pdf, "Record Review Issues", left, y, size=14, bold=True)
        y -= 7 * mm

        if income_issues.empty and expense_issues.empty:
            draw_text_line(pdf, "No income or expense review issues found for this period.", left, y, size=9)
            y -= 6 * mm
        else:
            if not income_issues.empty:
                draw_text_line(pdf, "Income Issues", left, y, size=11, bold=True)
                y -= 6 * mm

                for _, row in income_issues.head(10).iterrows():
                    if y < 25 * mm:
                        y = start_new_page(pdf)

                    line = (
                        f"{row.get('income_stream', '')} | "
                        f"{row.get('description', '')} | "
                        f"{row.get('record_status', '')} | "
                        f"{row.get('review_reason', '')}"
                    )

                    y = draw_wrapped_text(pdf, line, left, y, max_chars=95, size=8)

            if not expense_issues.empty:
                if y < 35 * mm:
                    y = start_new_page(pdf)

                draw_text_line(pdf, "Expense Issues", left, y, size=11, bold=True)
                y -= 6 * mm

                for _, row in expense_issues.head(10).iterrows():
                    if y < 25 * mm:
                        y = start_new_page(pdf)

                    line = (
                        f"{row.get('expense_category', '')} | "
                        f"{row.get('description', '')} | "
                        f"{row.get('record_status', '')} | "
                        f"{row.get('review_reason', '')}"
                    )

                    y = draw_wrapped_text(pdf, line, left, y, max_chars=95, size=8)

        y -= 5 * mm

        if y < 35 * mm:
            y = start_new_page(pdf)

        draw_text_line(pdf, "Recommended Next Actions", left, y, size=14, bold=True)
        y -= 7 * mm

        if true_profit > 0:
            y = draw_wrapped_text(
                pdf,
                "You are currently profitable. Protect your profit and focus on the side hustle with the strongest return.",
                left,
                y,
                size=9
            )
        elif true_profit == 0:
            y = draw_wrapped_text(
                pdf,
                "You are currently breaking even. Your next target is to push profit above zero.",
                left,
                y,
                size=9
            )
        else:
            y = draw_wrapped_text(
                pdf,
                "You are currently in a loss position. Review expenses before scaling any side hustle further.",
                left,
                y,
                size=9
            )

        if income_issue_count > 0 or expense_issue_count > 0:
            y = draw_wrapped_text(
                pdf,
                "Review missing evidence, missing receipts and pending payment records before relying on this report.",
                left,
                y,
                size=9
            )

        pdf.save()
        buffer.seek(0)

        return buffer.getvalue()

    pdf_bytes = build_pdf_report()

    safe_period = report_period.replace("/", "-").replace(" ", "_").lower()

    st.download_button(
        "Download PDF report",
        data=pdf_bytes,
        file_name=f"hustlehq_pdf_report_{safe_period}.pdf",
        mime="application/pdf",
    )

    st.markdown("### PDF report checks")

    if income_count == 0 and expense_count == 0:
        st.warning("No records found for this selected period.")
    else:
        st.success("PDF report is ready to download.")

    if income_issue_count > 0 or expense_issue_count > 0:
        st.warning("This PDF includes record issues. Check the Evidence Centre before relying on it.")
    else:
        st.success("No record issues detected for this selected period.")


elif page == "Data Backup":
    st.title("Data Backup")
    st.subheader("Download and protect your HustleHQ records")

    st.warning(
        "Keep backups of your CSV, goal and app settings files. This app stores data locally on your laptop inside the data folder."
    )

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()
    app_settings = load_app_settings()

    st.markdown("### Backup summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Income records", len(income_records))
    col2.metric("Expense records", len(expense_records))
    col3.metric("Saved goal settings", len(goals))
    col4.metric("App settings", len(app_settings))

    st.markdown("### Full backup ZIP")

    backup_buffer = BytesIO()

    with ZipFile(backup_buffer, "w") as zip_file:
        zip_file.writestr(
            "hustlehq_income_records_backup.csv",
            income_records.to_csv(index=False)
        )

        zip_file.writestr(
            "hustlehq_expense_records_backup.csv",
            expense_records.to_csv(index=False)
        )

        goal_settings_df = pd.DataFrame(
            {
                "Setting": list(goals.keys()),
                "Value": list(goals.values()),
            }
        )

        zip_file.writestr(
            "hustlehq_goal_settings_backup.csv",
            goal_settings_df.to_csv(index=False)
        )

        app_settings_df = pd.DataFrame(
            {
                "Setting": list(app_settings.keys()),
                "Value": list(app_settings.values()),
            }
        )

        zip_file.writestr(
            "hustlehq_app_settings_backup.csv",
            app_settings_df.to_csv(index=False)
        )

        if GOALS_FILE.exists():
            zip_file.writestr(
                "goals.json",
                GOALS_FILE.read_text(encoding="utf-8")
            )

        if APP_SETTINGS_FILE.exists():
            zip_file.writestr(
                "app_settings.json",
                APP_SETTINGS_FILE.read_text(encoding="utf-8")
            )

        zip_file.writestr(
            "README.txt",
            "HustleHQ backup pack. Keep these files safe. To restore manually, copy the CSV/JSON files back into the data folder."
        )

    st.download_button(
        "Download full HustleHQ backup ZIP",
        data=backup_buffer.getvalue(),
        file_name="hustlehq_full_backup.zip",
        mime="application/zip",
    )

    st.markdown("### Individual downloads")

    st.download_button(
        "Download income records backup",
        data=income_records.to_csv(index=False).encode("utf-8"),
        file_name="hustlehq_income_records_backup.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download expense records backup",
        data=expense_records.to_csv(index=False).encode("utf-8"),
        file_name="hustlehq_expense_records_backup.csv",
        mime="text/csv",
    )

    goal_settings_df = pd.DataFrame(
        {
            "Setting": list(goals.keys()),
            "Value": list(goals.values()),
        }
    )

    st.download_button(
        "Download goal settings backup",
        data=goal_settings_df.to_csv(index=False).encode("utf-8"),
        file_name="hustlehq_goal_settings_backup.csv",
        mime="text/csv",
    )

    app_settings_df = pd.DataFrame(
        {
            "Setting": list(app_settings.keys()),
            "Value": list(app_settings.values()),
        }
    )

    st.download_button(
        "Download app settings backup",
        data=app_settings_df.to_csv(index=False).encode("utf-8"),
        file_name="hustlehq_app_settings_backup.csv",
        mime="text/csv",
    )

    st.markdown("### Backup checks")

    if income_records.empty and expense_records.empty:
        st.warning("You do not have income or expense records backed up yet.")
    else:
        st.success("Your finance records are included in the backup.")

    if APP_SETTINGS_FILE.exists():
        st.success("Your password/app settings are included in the backup.")
    else:
        st.warning("No app settings file found yet. Save password settings first if needed.")

    st.markdown("### Restore note")

    st.info(
        "For now, restoring is manual: put the backup CSV or JSON files back into the data folder. Automatic restore can be added later."
    )


elif page == "Settings":
    st.title("Settings")
    st.subheader("Set and save your side-hustle goals and app preferences")

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()
    app_settings = load_app_settings()

    if income_records.empty:
        total_income = 0
    else:
        total_income = income_records["net_income"].sum()

    if expense_records.empty:
        total_expenses = 0
    else:
        total_expenses = expense_records["amount"].sum()

    true_profit = total_income - total_expenses

    st.markdown("### Saved goal settings")

    with st.form("goal_settings_form"):
        debt_target = st.number_input(
            "Debt target to clear (£)",
            min_value=0.0,
            step=50.0,
            value=float(goals.get("debt_target", 1000.0))
        )

        savings_target = st.number_input(
            "Savings target (£)",
            min_value=0.0,
            step=50.0,
            value=float(goals.get("savings_target", 2000.0))
        )

        monthly_income_goal = st.number_input(
            "Monthly side-hustle income goal (£)",
            min_value=0.0,
            step=50.0,
            value=float(goals.get("monthly_income_goal", 500.0))
        )

        emergency_buffer_goal = st.number_input(
            "Emergency buffer goal (£)",
            min_value=0.0,
            step=50.0,
            value=float(goals.get("emergency_buffer_goal", 500.0))
        )

        priority_options = [
            "Clear debt first",
            "Build emergency buffer",
            "Save for moving out",
            "Scale side hustles",
            "Build portfolio income",
        ]

        saved_priority = goals.get("priority_goal", "Clear debt first")

        if saved_priority not in priority_options:
            saved_priority = "Clear debt first"

        priority_goal = st.selectbox(
            "Priority goal",
            priority_options,
            index=priority_options.index(saved_priority)
        )

        submitted = st.form_submit_button("Save goal settings")

    if submitted:
        new_goals = {
            "debt_target": debt_target,
            "savings_target": savings_target,
            "monthly_income_goal": monthly_income_goal,
            "emergency_buffer_goal": emergency_buffer_goal,
            "priority_goal": priority_goal,
        }

        save_goal_settings(new_goals)

        st.success("Goal settings saved successfully.")
        st.rerun()

    st.markdown("---")

    st.markdown("### Password protection")

    with st.form("password_settings_form"):
        password_protection = st.checkbox(
            "Enable password protection",
            value=bool(app_settings.get("password_protection", True))
        )

        new_password = st.text_input(
            "App password",
            value=str(app_settings.get("app_password", "hustlehq123")),
            type="password"
        )

        password_submitted = st.form_submit_button("Save password settings")

    if password_submitted:
        new_app_settings = {
            "app_password": new_password,
            "password_protection": password_protection,
        }

        save_app_settings(new_app_settings)

        st.success("Password settings saved successfully. They will apply when the app reloads.")

    if app_settings.get("password_protection", True):
        st.success("Password protection is currently active.")
    else:
        st.warning("Password protection is currently turned off.")

    st.markdown("---")

    st.markdown("### Current goal progress")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total income recorded", f"£{total_income:,.2f}")
    col2.metric("Total expenses recorded", f"£{total_expenses:,.2f}")
    col3.metric("Current profit", f"£{true_profit:,.2f}")

    debt_progress = min(true_profit / float(goals.get("debt_target", 1000)), 1) if float(goals.get("debt_target", 1000)) > 0 else 0
    savings_progress = min(true_profit / float(goals.get("savings_target", 2000)), 1) if float(goals.get("savings_target", 2000)) > 0 else 0
    buffer_progress = min(true_profit / float(goals.get("emergency_buffer_goal", 500)), 1) if float(goals.get("emergency_buffer_goal", 500)) > 0 else 0
    monthly_progress = min(total_income / float(goals.get("monthly_income_goal", 500)), 1) if float(goals.get("monthly_income_goal", 500)) > 0 else 0

    st.write("Debt target progress")
    st.progress(debt_progress)

    st.write("Savings target progress")
    st.progress(savings_progress)

    st.write("Emergency buffer progress")
    st.progress(buffer_progress)

    st.write("Monthly income goal progress")
    st.progress(monthly_progress)

    st.markdown("### Cash sprint tracker")

    if true_profit > 0:
        debt_gap = max(float(goals.get("debt_target", 1000)) - true_profit, 0)
        savings_gap = max(float(goals.get("savings_target", 2000)) - true_profit, 0)
        buffer_gap = max(float(goals.get("emergency_buffer_goal", 500)) - true_profit, 0)

        st.write(f"Debt gap remaining: **£{debt_gap:,.2f}**")
        st.write(f"Savings gap remaining: **£{savings_gap:,.2f}**")
        st.write(f"Emergency buffer gap remaining: **£{buffer_gap:,.2f}**")
    else:
        st.warning("Current profit is zero or negative, so goal gaps cannot move yet.")

    average_sale_profit = st.number_input(
        "Average profit per sale/job (£)",
        min_value=1.0,
        step=1.0,
        value=20.0
    )

    selected_target = st.selectbox(
        "Sprint target to calculate",
        [
            "Debt target",
            "Savings target",
            "Emergency buffer",
            "Monthly income goal",
        ]
    )

    if selected_target == "Debt target":
        sprint_gap = max(float(goals.get("debt_target", 1000)) - true_profit, 0)
    elif selected_target == "Savings target":
        sprint_gap = max(float(goals.get("savings_target", 2000)) - true_profit, 0)
    elif selected_target == "Emergency buffer":
        sprint_gap = max(float(goals.get("emergency_buffer_goal", 500)) - true_profit, 0)
    else:
        sprint_gap = max(float(goals.get("monthly_income_goal", 500)) - total_income, 0)

    required_sales = int((sprint_gap + average_sale_profit - 1) // average_sale_profit)

    st.info(
        f"To hit your selected sprint target, you need roughly {required_sales} sales/jobs at £{average_sale_profit:,.2f} profit each."
    )

    st.markdown("### Current app status")

    st.write("- Income tracking: active")
    st.write("- Expense tracking: active")
    st.write("- Delete buttons: active")
    st.write("- Evidence Centre: active")
    st.write("- HMRC Export: active")
    st.write("- Weekly Review: active")
    st.write("- Date tracking: active")
    st.write("- Monthly trend charts: active")
    st.write("- Saved goal tracking: active")
    st.write("- Password protection: active")
