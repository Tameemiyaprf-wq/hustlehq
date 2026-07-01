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
APP_VERSION = "1.0.0"
APP_STAGE = "Phase 1 MVP"

DATA_FOLDER = Path("data")

if DATA_FOLDER.exists() and not DATA_FOLDER.is_dir():
    DATA_FOLDER.unlink()

DATA_FOLDER.mkdir(exist_ok=True)

INCOME_FILE = DATA_FOLDER / "income_records.csv"
EXPENSE_FILE = DATA_FOLDER / "expense_records.csv"
GOALS_FILE = DATA_FOLDER / "goals.json"
APP_SETTINGS_FILE = DATA_FOLDER / "app_settings.json"
PROJECT_FILE = DATA_FOLDER / "project_records.csv"
INVOICE_FILE = DATA_FOLDER / "invoice_records.csv"
RECURRING_EXPENSE_FILE = DATA_FOLDER / "recurring_expense_records.csv"


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

    # Force protection on so restored/old settings cannot accidentally disable login
    default_settings["password_protection"] = True
    save_app_settings(default_settings)

    return default_settings


def save_app_settings(settings):
    APP_SETTINGS_FILE.write_text(json.dumps(settings, indent=4), encoding="utf-8")


def logout_user():
    keys_to_clear = [
        "authenticated",
        "login_password_input",
        "unlock_hustlehq_button",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state["authenticated"] = False
    st.rerun()


def require_password():
    settings = load_app_settings()

    if st.session_state.get("authenticated", False) is True:
        return True

    st.title("HustleHQ Login")
    st.subheader("Enter your app password to continue")

    entered_password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password",
        key="login_password_input"
    )

    if st.button("Unlock HustleHQ", key="unlock_hustlehq_button"):
        correct_password = settings.get("app_password", "hustlehq123")

        if entered_password == correct_password:
            st.session_state["authenticated"] = True
            st.success("Access granted.")
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.info("Default password: hustlehq123. Change it in Settings after logging in.")

    return False


def load_project_records():
    columns = [
        "date_added",
        "project_name",
        "client_name",
        "side_hustle",
        "status",
        "expected_income",
        "deadline",
        "notes",
    ]

    if PROJECT_FILE.exists():
        records = pd.read_csv(PROJECT_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["expected_income"] = pd.to_numeric(records["expected_income"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_project_records(records):
    records.to_csv(PROJECT_FILE, index=False)



def load_invoice_records():
    columns = [
        "invoice_date",
        "invoice_number",
        "client_name",
        "client_email",
        "side_hustle",
        "service_description",
        "amount",
        "due_date",
        "status",
        "payment_notes",
    ]

    if INVOICE_FILE.exists():
        records = pd.read_csv(INVOICE_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_invoice_records(records):
    records.to_csv(INVOICE_FILE, index=False)



def get_uk_tax_year(date_value):
    date_value = pd.to_datetime(date_value, errors="coerce")

    if pd.isna(date_value):
        return "Unknown"

    year = date_value.year
    tax_year_start = pd.Timestamp(year=year, month=4, day=6)

    if date_value >= tax_year_start:
        return f"{year}/{str(year + 1)[-2:]}"
    else:
        return f"{year - 1}/{str(year)[-2:]}"


def add_tax_year_column(records):
    records = records.copy()

    if "date" not in records.columns:
        records["tax_year"] = "Unknown"
        return records

    records["date"] = pd.to_datetime(records["date"], errors="coerce")
    records["tax_year"] = records["date"].apply(get_uk_tax_year)

    return records



def load_recurring_expense_records():
    columns = [
        "date_added",
        "expense_name",
        "expense_category",
        "amount",
        "frequency",
        "next_due_date",
        "status",
        "notes",
    ]

    if RECURRING_EXPENSE_FILE.exists():
        records = pd.read_csv(RECURRING_EXPENSE_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_recurring_expense_records(records):
    records.to_csv(RECURRING_EXPENSE_FILE, index=False)


def estimate_monthly_recurring_cost(amount, frequency):
    if frequency == "Weekly":
        return amount * 52 / 12
    elif frequency == "Fortnightly":
        return amount * 26 / 12
    elif frequency == "Monthly":
        return amount
    elif frequency == "Quarterly":
        return amount / 3
    elif frequency == "Yearly":
        return amount / 12
    else:
        return amount



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

    if st.sidebar.button("Log out", key="sidebar_logout_button"):
        logout_user()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Version {APP_VERSION} • {APP_STAGE}")


if not require_password():
    st.stop()


st.sidebar.markdown("## 💼 HustleHQ")
st.sidebar.markdown("Side-Hustle Finance Command Centre")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Income",
        "Import Income CSV",
        "Add Expense",
        "Import Expense CSV",
        "Recurring Expenses",
        "Project Tracker",
        "Invoice Draft",
        "Invoice History",
        "Payment Chase",
        "Convert Invoice to Income",
        "Evidence Centre",
        "HMRC Export",
        "Tax-Year Summary",
        "Tax Set-Aside Calculator",
        "Weekly Review",
        "Monthly Insights",
        "Data Backup",
        "Restore Backup",
        "PDF Report",
        "Security Status",
        "Release Notes",
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


elif page == "Import Income CSV":
    st.title("Import Income CSV")
    st.subheader("Upload income records from a CSV file")

    st.warning(
        "Use this page to import income records from platform exports, bank CSVs or manual spreadsheets. "
        "Always check the preview before saving imported records."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="income_csv_upload"
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin.")
    else:
        try:
            imported_df = pd.read_csv(uploaded_file)

            if imported_df.empty:
                st.error("The uploaded CSV is empty.")
            else:
                st.markdown("### Uploaded file preview")
                st.dataframe(imported_df.head(20), use_container_width=True)

                st.markdown("### Map your columns")

                csv_columns = imported_df.columns.tolist()
                none_option = "None"

                def guess_column(possible_names):
                    for possible_name in possible_names:
                        for column in csv_columns:
                            if possible_name.lower() in column.lower():
                                return column
                    return csv_columns[0] if csv_columns else none_option

                date_column = st.selectbox(
                    "Date column",
                    csv_columns,
                    index=csv_columns.index(guess_column(["date", "sold", "payment"])) if guess_column(["date", "sold", "payment"]) in csv_columns else 0
                )

                stream_column = st.selectbox(
                    "Income stream / platform column",
                    [none_option] + csv_columns,
                    index=0
                )

                description_column = st.selectbox(
                    "Description/item/client column",
                    [none_option] + csv_columns,
                    index=([none_option] + csv_columns).index(guess_column(["description", "item", "title", "client", "service"])) if guess_column(["description", "item", "title", "client", "service"]) in csv_columns else 0
                )

                gross_column = st.selectbox(
                    "Gross income / amount column",
                    csv_columns,
                    index=csv_columns.index(guess_column(["gross", "amount", "total", "sale", "price"])) if guess_column(["gross", "amount", "total", "sale", "price"]) in csv_columns else 0
                )

                fee_column = st.selectbox(
                    "Fee column",
                    [none_option] + csv_columns,
                    index=0
                )

                status_column = st.selectbox(
                    "Payment status column",
                    [none_option] + csv_columns,
                    index=0
                )

                evidence_column = st.selectbox(
                    "Evidence/reference column",
                    [none_option] + csv_columns,
                    index=0
                )

                default_stream = st.selectbox(
                    "Default income stream if no platform column is used",
                    [
                        "Vinted",
                        "Legal Transcription",
                        "YouTube",
                        "Substack",
                        "Etsy/Digital Products",
                        "UGC Deals",
                        "App Sales",
                        "Website Builds",
                        "Client Work",
                        "Other",
                    ]
                )

                st.markdown("### Import settings")

                import_status_default = st.selectbox(
                    "Default payment status",
                    [
                        "Paid",
                        "Pending",
                        "Unpaid",
                        "Cancelled",
                    ]
                )

                add_import_tag = st.checkbox(
                    "Add CSV import tag to evidence",
                    value=True
                )

                if st.button("Preview converted income records"):
                    preview_records = imported_df.copy()

                    preview_records["_date"] = pd.to_datetime(preview_records[date_column], errors="coerce")
                    preview_records["_gross_income"] = pd.to_numeric(preview_records[gross_column], errors="coerce").fillna(0)

                    if fee_column != none_option:
                        preview_records["_platform_fee"] = pd.to_numeric(preview_records[fee_column], errors="coerce").fillna(0)
                    else:
                        preview_records["_platform_fee"] = 0

                    preview_records["_net_income"] = preview_records["_gross_income"] - preview_records["_platform_fee"]

                    if stream_column != none_option:
                        preview_records["_income_stream"] = preview_records[stream_column].astype(str)
                    else:
                        preview_records["_income_stream"] = default_stream

                    if description_column != none_option:
                        preview_records["_description"] = preview_records[description_column].astype(str)
                    else:
                        preview_records["_description"] = "Imported income record"

                    if status_column != none_option:
                        preview_records["_payment_status"] = preview_records[status_column].astype(str)
                    else:
                        preview_records["_payment_status"] = import_status_default

                    if evidence_column != none_option:
                        preview_records["_evidence"] = preview_records[evidence_column].astype(str)
                    else:
                        preview_records["_evidence"] = "Imported from CSV"

                    if add_import_tag:
                        preview_records["_evidence"] = preview_records["_evidence"] + " | CSV import"

                    converted_records = pd.DataFrame(
                        {
                            "date": preview_records["_date"].dt.date.astype(str),
                            "income_stream": preview_records["_income_stream"],
                            "description": preview_records["_description"],
                            "gross_income": preview_records["_gross_income"],
                            "platform_fee": preview_records["_platform_fee"],
                            "net_income": preview_records["_net_income"],
                            "payment_status": preview_records["_payment_status"],
                            "evidence": preview_records["_evidence"],
                        }
                    )

                    converted_records = converted_records[
                        converted_records["gross_income"] > 0
                    ].copy()

                    st.session_state["income_import_preview"] = converted_records

                if "income_import_preview" in st.session_state:
                    converted_records = st.session_state["income_import_preview"]

                    st.markdown("### Converted income preview")

                    if converted_records.empty:
                        st.error("No valid income records found after conversion. Check your amount column.")
                    else:
                        st.dataframe(converted_records, use_container_width=True)

                        total_import_income = converted_records["net_income"].sum()

                        col1, col2 = st.columns(2)
                        col1.metric("Records ready to import", len(converted_records))
                        col2.metric("Net income ready to import", f"£{total_import_income:,.2f}")

                        existing_income = load_income_records()

                        duplicate_count = 0

                        if not existing_income.empty and "evidence" in existing_income.columns:
                            existing_evidence = existing_income["evidence"].astype(str).tolist()

                            for evidence_value in converted_records["evidence"].astype(str).tolist():
                                if evidence_value in existing_evidence:
                                    duplicate_count += 1

                        if duplicate_count > 0:
                            st.warning(f"{duplicate_count} possible duplicate record(s) found based on evidence/reference text.")

                        confirm_import = st.checkbox(
                            "I have checked the preview and want to save these income records."
                        )

                        if st.button("Save imported income records"):
                            if not confirm_import:
                                st.error("Tick the confirmation box before saving.")
                            else:
                                updated_income = pd.concat(
                                    [existing_income, converted_records],
                                    ignore_index=True
                                )

                                save_income_records(updated_income)

                                st.success("Imported income records saved successfully.")
                                st.info("Go to Dashboard, Add Income or Tax-Year Summary to review the imported records.")

                                del st.session_state["income_import_preview"]

        except Exception as error:
            st.error("CSV import failed.")
            st.exception(error)

    st.markdown("---")

    st.markdown("### CSV import tips")

    st.write("- Your CSV should have at least a date column and an amount column.")
    st.write("- Use the mapping dropdowns to tell HustleHQ which columns mean what.")
    st.write("- Preview before saving.")
    st.write("- Imported records are added to your main income records.")
    st.write("- Keep your original platform export as backup evidence.")



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


elif page == "Project Tracker":
    st.title("Project Tracker")
    st.subheader("Track side-hustle projects before they become income")

    project_records = load_project_records()

    st.markdown("### Add new project")

    with st.form("add_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_name = st.text_input("Project name")
            client_name = st.text_input("Client/platform name")
            side_hustle = st.selectbox(
                "Side hustle category",
                [
                    "Vinted",
                    "Legal Transcription",
                    "YouTube",
                    "Substack",
                    "Etsy/Digital Products",
                    "UGC Deals",
                    "App Sales",
                    "Website Builds",
                    "Client Work",
                    "Other",
                ]
            )

        with col2:
            status = st.selectbox(
                "Project status",
                [
                    "Idea",
                    "In progress",
                    "Waiting for client",
                    "Completed - unpaid",
                    "Completed - paid",
                    "Cancelled",
                ]
            )

            expected_income = st.number_input(
                "Expected income (£)",
                min_value=0.0,
                step=5.0,
                value=0.0
            )

            deadline = st.date_input("Deadline")

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save project")

    if submitted:
        if not project_name.strip():
            st.error("Add a project name before saving.")
        else:
            new_project = pd.DataFrame(
                [
                    {
                        "date_added": str(pd.Timestamp.today().date()),
                        "project_name": project_name.strip(),
                        "client_name": client_name.strip(),
                        "side_hustle": side_hustle,
                        "status": status,
                        "expected_income": expected_income,
                        "deadline": str(deadline),
                        "notes": notes.strip(),
                    }
                ]
            )

            project_records = pd.concat([project_records, new_project], ignore_index=True)
            save_project_records(project_records)

            st.success("Project saved successfully.")
            st.rerun()

    st.markdown("---")

    st.markdown("### Project overview")

    if project_records.empty:
        st.warning("No projects saved yet.")
    else:
        project_records["expected_income"] = pd.to_numeric(
            project_records["expected_income"],
            errors="coerce"
        ).fillna(0)

        active_projects = project_records[
            ~project_records["status"].isin(["Completed - paid", "Cancelled"])
        ]

        unpaid_completed = project_records[
            project_records["status"] == "Completed - unpaid"
        ]

        total_expected_income = active_projects["expected_income"].sum()
        unpaid_expected_income = unpaid_completed["expected_income"].sum()

        deadline_dates = pd.to_datetime(active_projects["deadline"], errors="coerce")
        today = pd.Timestamp.today().normalize()
        overdue_count = int((deadline_dates < today).sum())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total projects", len(project_records))
        col2.metric("Active projects", len(active_projects))
        col3.metric("Expected active income", f"£{total_expected_income:,.2f}")
        col4.metric("Overdue projects", overdue_count)

        if unpaid_expected_income > 0:
            st.info(f"Completed but unpaid expected income: **£{unpaid_expected_income:,.2f}**")

        st.markdown("### Filter projects")

        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + sorted(project_records["status"].dropna().unique().tolist())
        )

        hustle_filter = st.selectbox(
            "Filter by side hustle",
            ["All"] + sorted(project_records["side_hustle"].dropna().unique().tolist())
        )

        filtered_projects = project_records.copy()

        if status_filter != "All":
            filtered_projects = filtered_projects[filtered_projects["status"] == status_filter]

        if hustle_filter != "All":
            filtered_projects = filtered_projects[filtered_projects["side_hustle"] == hustle_filter]

        st.dataframe(filtered_projects, use_container_width=True)

        st.download_button(
            "Download project tracker CSV",
            data=project_records.to_csv(index=False).encode("utf-8"),
            file_name="hustlehq_project_tracker.csv",
            mime="text/csv",
        )

        st.markdown("### Delete a project")

        delete_options = [
            f"{index} - {row['project_name']} ({row['status']})"
            for index, row in project_records.iterrows()
        ]

        selected_delete = st.selectbox(
            "Choose project to delete",
            delete_options
        )

        if st.button("Delete selected project"):
            selected_index = int(selected_delete.split(" - ")[0])
            project_records = project_records.drop(index=selected_index).reset_index(drop=True)
            save_project_records(project_records)

            st.success("Project deleted.")
            st.rerun()

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Add projects before they become paid income.")
    st.write("- Mark completed unpaid work so you know what money is still expected.")
    st.write("- Once payment arrives, add the payment on the Add Income page.")
    st.write("- Keep this page as your side-hustle pipeline tracker.")



elif page == "Invoice Draft":
    st.title("Invoice Draft")
    st.subheader("Create a clean invoice draft for side-hustle work")

    st.warning(
        "This creates an invoice draft for your records/client communication. "
        "It is not official tax advice and does not file anything to HMRC."
    )

    st.markdown("### Invoice details")

    with st.form("invoice_draft_form"):
        col1, col2 = st.columns(2)

        with col1:
            invoice_number = st.text_input(
                "Invoice number",
                value=f"HHQ-{pd.Timestamp.today().strftime('%Y%m%d')}"
            )

            your_name = st.text_input(
                "Your name / business name",
                value="Tami"
            )

            client_name = st.text_input("Client/platform name")

            client_email = st.text_input("Client email or contact")

        with col2:
            invoice_date = st.date_input("Invoice date")
            due_date = st.date_input("Payment due date")

            side_hustle = st.selectbox(
                "Side hustle category",
                [
                    "UGC Deals",
                    "Website Builds",
                    "Client Work",
                    "App Sales",
                    "Legal Transcription",
                    "Etsy/Digital Products",
                    "Substack",
                    "YouTube",
                    "Vinted",
                    "Other",
                ]
            )

            amount = st.number_input(
                "Invoice amount (£)",
                min_value=0.0,
                step=5.0,
                value=0.0
            )

        service_description = st.text_area(
            "Service / project description",
            placeholder="Example: UGC video package, website build, transcription job, app setup, content package..."
        )

        payment_notes = st.text_area(
            "Payment details / notes",
            placeholder="Example: Bank transfer details, payment reference, due date reminder, agreed terms..."
        )

        submitted = st.form_submit_button("Generate invoice draft")

    if submitted:
        if not client_name.strip():
            st.error("Add a client/platform name before generating the invoice.")
        elif amount <= 0:
            st.error("Add an invoice amount above £0.")
        elif not service_description.strip():
            st.error("Add a service or project description.")
        else:
            st.success("Invoice draft generated.")

            invoice_text = f"""
INVOICE

Invoice number: {invoice_number}
Invoice date: {invoice_date}
Payment due date: {due_date}

From:
{your_name}

To:
{client_name}
{client_email}

Side-hustle category:
{side_hustle}

Service / project description:
{service_description}

Amount due:
£{amount:,.2f}

Payment details / notes:
{payment_notes}

Thank you.
"""

            st.markdown("### Invoice preview")

            st.text_area(
                "Preview",
                value=invoice_text,
                height=420
            )

            st.download_button(
                "Download invoice text file",
                data=invoice_text.encode("utf-8"),
                file_name=f"{invoice_number}_invoice_draft.txt",
                mime="text/plain",
            )

            st.markdown("### Download PDF invoice")

            invoice_pdf_buffer = BytesIO()

            pdf = canvas.Canvas(invoice_pdf_buffer, pagesize=A4)
            width, height = A4

            x_margin = 22 * mm
            y_position = [height - 25 * mm]

            def pdf_line(text_value, size=10, bold=False, gap=7):
                if y_position[0] < 25 * mm:
                    pdf.showPage()
                    y_position[0] = height - 25 * mm

                font_name = "Helvetica-Bold" if bold else "Helvetica"
                pdf.setFont(font_name, size)

                safe_text = str(text_value).replace("£", "GBP ")
                pdf.drawString(x_margin, y_position[0], safe_text)
                y_position[0] -= gap * mm

            def pdf_wrapped(text_value, size=10, gap=5):
                safe_text = str(text_value).replace("£", "GBP ")
                words = safe_text.split()
                line = ""

                for word in words:
                    test_line = f"{line} {word}".strip()

                    if len(test_line) > 85:
                        pdf_line(line, size=size, gap=gap)
                        line = word
                    else:
                        line = test_line

                if line:
                    pdf_line(line, size=size, gap=gap)

            pdf_line("INVOICE", size=20, bold=True, gap=10)
            pdf_line(f"Invoice number: {invoice_number}", bold=True)
            pdf_line(f"Invoice date: {invoice_date}")
            pdf_line(f"Payment due date: {due_date}")
            pdf_line("")

            pdf_line("From:", bold=True)
            pdf_wrapped(your_name)
            pdf_line("")

            pdf_line("To:", bold=True)
            pdf_wrapped(client_name)
            if client_email.strip():
                pdf_wrapped(client_email)
            pdf_line("")

            pdf_line("Side-hustle category:", bold=True)
            pdf_wrapped(side_hustle)
            pdf_line("")

            pdf_line("Service / project description:", bold=True)
            pdf_wrapped(service_description)
            pdf_line("")

            pdf_line("Amount due:", bold=True)
            pdf_line(f"GBP {amount:,.2f}", size=14, bold=True)
            pdf_line("")

            pdf_line("Payment details / notes:", bold=True)
            pdf_wrapped(payment_notes if payment_notes.strip() else "No payment notes added.")
            pdf_line("")

            pdf_line("Thank you.", bold=True)

            pdf.save()

            st.download_button(
                "Download invoice PDF",
                data=invoice_pdf_buffer.getvalue(),
                file_name=f"{invoice_number}_invoice_draft.pdf",
                mime="application/pdf",
            )

            st.markdown("### Save invoice to history")

            invoice_status = st.selectbox(
                "Invoice status",
                [
                    "Draft",
                    "Sent",
                    "Awaiting payment",
                    "Paid",
                    "Overdue",
                    "Cancelled",
                ],
                key="invoice_draft_status"
            )

            if st.button("Save invoice to Invoice History", key="save_invoice_to_history"):
                invoice_records = load_invoice_records()

                new_invoice_record = pd.DataFrame(
                    [
                        {
                            "invoice_date": str(invoice_date),
                            "invoice_number": invoice_number,
                            "client_name": client_name.strip(),
                            "client_email": client_email.strip(),
                            "side_hustle": side_hustle,
                            "service_description": service_description.strip(),
                            "amount": amount,
                            "due_date": str(due_date),
                            "status": invoice_status,
                            "payment_notes": payment_notes.strip(),
                        }
                    ]
                )

                invoice_records = pd.concat([invoice_records, new_invoice_record], ignore_index=True)
                save_invoice_records(invoice_records)

                st.success("Invoice saved to Invoice History.")


    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Use this when a side-hustle project is ready to bill.")
    st.write("- Save the PDF/text invoice for your records.")
    st.write("- When payment arrives, log the money on the Add Income page.")
    st.write("- Keep invoice copies as supporting evidence.")



elif page == "Invoice History":
    st.title("Invoice History")
    st.subheader("Track invoice drafts, sent invoices and outstanding payments")

    invoice_records = load_invoice_records()

    if invoice_records.empty:
        st.warning("No invoices saved yet. Create one on the Invoice Draft page first.")
    else:
        invoice_records["amount"] = pd.to_numeric(invoice_records["amount"], errors="coerce").fillna(0)
        invoice_records["due_date"] = pd.to_datetime(invoice_records["due_date"], errors="coerce")
        today = pd.Timestamp.today().normalize()

        unpaid_statuses = ["Draft", "Sent", "Awaiting payment", "Overdue"]
        unpaid_invoices = invoice_records[invoice_records["status"].isin(unpaid_statuses)]
        paid_invoices = invoice_records[invoice_records["status"] == "Paid"]

        overdue_count = int(
            (
                invoice_records["due_date"].notna()
                & (invoice_records["due_date"] < today)
                & invoice_records["status"].isin(["Sent", "Awaiting payment", "Overdue"])
            ).sum()
        )

        total_invoiced = invoice_records["amount"].sum()
        total_paid = paid_invoices["amount"].sum()
        total_outstanding = unpaid_invoices["amount"].sum()

        st.markdown("### Invoice summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Invoices saved", len(invoice_records))
        col2.metric("Total invoiced", f"£{total_invoiced:,.2f}")
        col3.metric("Paid invoices", f"£{total_paid:,.2f}")
        col4.metric("Outstanding", f"£{total_outstanding:,.2f}")

        if overdue_count > 0:
            st.error(f"You have {overdue_count} overdue invoice(s).")
        else:
            st.success("No overdue invoices detected.")

        st.markdown("### Filter invoices")

        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + sorted(invoice_records["status"].dropna().unique().tolist())
        )

        hustle_filter = st.selectbox(
            "Filter by side hustle",
            ["All"] + sorted(invoice_records["side_hustle"].dropna().unique().tolist())
        )

        filtered_invoices = invoice_records.copy()

        if status_filter != "All":
            filtered_invoices = filtered_invoices[filtered_invoices["status"] == status_filter]

        if hustle_filter != "All":
            filtered_invoices = filtered_invoices[filtered_invoices["side_hustle"] == hustle_filter]

        display_invoices = filtered_invoices.copy()
        display_invoices["amount"] = display_invoices["amount"].map(lambda value: f"£{value:,.2f}")

        st.dataframe(display_invoices, use_container_width=True)

        st.download_button(
            "Download invoice history CSV",
            data=invoice_records.to_csv(index=False).encode("utf-8"),
            file_name="hustlehq_invoice_history.csv",
            mime="text/csv",
        )

        st.markdown("### Update invoice status")

        update_options = [
            f"{index} - {row['invoice_number']} - {row['client_name']} ({row['status']})"
            for index, row in invoice_records.iterrows()
        ]

        selected_update = st.selectbox(
            "Choose invoice to update",
            update_options,
            key="invoice_status_update_select"
        )

        new_status = st.selectbox(
            "New status",
            [
                "Draft",
                "Sent",
                "Awaiting payment",
                "Paid",
                "Overdue",
                "Cancelled",
            ],
            key="invoice_status_update_value"
        )

        if st.button("Update selected invoice status"):
            selected_index = int(selected_update.split(" - ")[0])
            invoice_records.loc[selected_index, "status"] = new_status
            save_invoice_records(invoice_records)

            st.success("Invoice status updated.")
            st.rerun()

        st.markdown("### Delete invoice")

        delete_options = [
            f"{index} - {row['invoice_number']} - {row['client_name']}"
            for index, row in invoice_records.iterrows()
        ]

        selected_delete = st.selectbox(
            "Choose invoice to delete",
            delete_options,
            key="delete_invoice_select"
        )

        if st.button("Delete selected invoice"):
            selected_index = int(selected_delete.split(" - ")[0])
            invoice_records = invoice_records.drop(index=selected_index).reset_index(drop=True)
            save_invoice_records(invoice_records)

            st.success("Invoice deleted.")
            st.rerun()

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Save invoice drafts from the Invoice Draft page.")
    st.write("- Mark invoices as Sent, Awaiting payment, Paid, Overdue or Cancelled.")
    st.write("- When an invoice is paid, also add the payment on the Add Income page.")
    st.write("- Use this page to track money you are owed.")



elif page == "Payment Chase":
    st.title("Payment Chase")
    st.subheader("Create professional follow-up messages for unpaid invoices")

    invoice_records = load_invoice_records()

    if invoice_records.empty:
        st.warning("No invoices saved yet. Create and save invoices first.")
    else:
        invoice_records["amount"] = pd.to_numeric(invoice_records["amount"], errors="coerce").fillna(0)

        unpaid_statuses = ["Draft", "Sent", "Awaiting payment", "Overdue"]
        unpaid_invoices = invoice_records[invoice_records["status"].isin(unpaid_statuses)].copy()

        if unpaid_invoices.empty:
            st.success("No unpaid invoices found.")
        else:
            st.markdown("### Choose unpaid invoice")

            invoice_options = [
                f"{index} - {row['invoice_number']} - {row['client_name']} - £{row['amount']:,.2f} - {row['status']}"
                for index, row in unpaid_invoices.iterrows()
            ]

            selected_invoice = st.selectbox(
                "Invoice to chase",
                invoice_options
            )

            selected_index = int(selected_invoice.split(" - ")[0])
            invoice = invoice_records.loc[selected_index]

            invoice_number = invoice["invoice_number"]
            client_name = invoice["client_name"]
            client_email = invoice["client_email"]
            amount = float(invoice["amount"])
            due_date = invoice["due_date"]
            service_description = invoice["service_description"]
            status = invoice["status"]

            col1, col2, col3 = st.columns(3)

            col1.metric("Invoice", invoice_number)
            col2.metric("Amount", f"£{amount:,.2f}")
            col3.metric("Status", status)

            st.write(f"**Client:** {client_name}")
            st.write(f"**Due date:** {due_date}")
            st.write(f"**Service:** {service_description}")

            st.markdown("### Message type")

            chase_type = st.selectbox(
                "Choose follow-up style",
                [
                    "Polite reminder",
                    "Overdue reminder",
                    "Final firm reminder",
                ]
            )

            your_name = st.text_input(
                "Sign-off name",
                value="Tami"
            )

            if chase_type == "Polite reminder":
                subject = f"Reminder: Invoice {invoice_number}"
                message = f"""Hi {client_name},

I hope you're well.

Just a quick reminder that invoice {invoice_number} for £{amount:,.2f} is due on {due_date}.

This relates to:
{service_description}

Please let me know once payment has been made, or if you need anything else from me.

Kind regards,
{your_name}
"""

            elif chase_type == "Overdue reminder":
                subject = f"Overdue invoice: {invoice_number}"
                message = f"""Hi {client_name},

I hope you're well.

I'm following up because invoice {invoice_number} for £{amount:,.2f} appears to now be overdue.

This relates to:
{service_description}

Please could you confirm when payment will be made?

Kind regards,
{your_name}
"""

            else:
                subject = f"Final payment reminder: Invoice {invoice_number}"
                message = f"""Hi {client_name},

I hope you're well.

I'm following up again regarding invoice {invoice_number} for £{amount:,.2f}, which remains unpaid.

This relates to:
{service_description}

Please arrange payment as soon as possible or confirm the expected payment date.

Kind regards,
{your_name}
"""

            st.markdown("### Subject line")

            st.text_input(
                "Copy subject",
                value=subject
            )

            st.markdown("### Message")

            st.text_area(
                "Copy message",
                value=message,
                height=320
            )

            st.download_button(
                "Download chase message as text file",
                data=message.encode("utf-8"),
                file_name=f"{invoice_number}_payment_chase.txt",
                mime="text/plain",
            )

            st.markdown("### Update invoice status after chasing")

            if st.button("Mark selected invoice as Awaiting payment"):
                invoice_records.loc[selected_index, "status"] = "Awaiting payment"
                save_invoice_records(invoice_records)
                st.success("Invoice marked as Awaiting payment.")
                st.rerun()

            if st.button("Mark selected invoice as Overdue"):
                invoice_records.loc[selected_index, "status"] = "Overdue"
                save_invoice_records(invoice_records)
                st.success("Invoice marked as Overdue.")
                st.rerun()

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Use this page after saving invoices in Invoice History.")
    st.write("- Start with a polite reminder if the due date is close.")
    st.write("- Use overdue reminders only when payment is late.")
    st.write("- Keep the tone professional and factual.")
    st.write("- When payment arrives, update the invoice to Paid and add the income on Add Income.")



elif page == "Convert Invoice to Income":
    st.title("Convert Invoice to Income")
    st.subheader("Turn paid invoices into income records without retyping everything")

    invoice_records = load_invoice_records()
    income_records = load_income_records()

    if invoice_records.empty:
        st.warning("No invoices saved yet. Create and save invoices first.")
    else:
        invoice_records["amount"] = pd.to_numeric(invoice_records["amount"], errors="coerce").fillna(0)

        paid_invoices = invoice_records[invoice_records["status"] == "Paid"].copy()

        if paid_invoices.empty:
            st.warning("No paid invoices found yet. Mark an invoice as Paid in Invoice History first.")
        else:
            st.markdown("### Choose paid invoice")

            invoice_options = [
                f"{index} - {row['invoice_number']} - {row['client_name']} - £{row['amount']:,.2f}"
                for index, row in paid_invoices.iterrows()
            ]

            selected_invoice = st.selectbox(
                "Paid invoice to convert",
                invoice_options
            )

            selected_index = int(selected_invoice.split(" - ")[0])
            invoice = invoice_records.loc[selected_index]

            invoice_number = str(invoice["invoice_number"])
            client_name = str(invoice["client_name"])
            side_hustle = str(invoice["side_hustle"])
            amount = float(invoice["amount"])
            service_description = str(invoice["service_description"])
            payment_notes = str(invoice["payment_notes"])
            invoice_date = str(invoice["invoice_date"])

            st.markdown("### Invoice selected")

            col1, col2, col3 = st.columns(3)

            col1.metric("Invoice", invoice_number)
            col2.metric("Client", client_name)
            col3.metric("Amount", f"£{amount:,.2f}")

            st.write(f"**Side hustle:** {side_hustle}")
            st.write(f"**Service:** {service_description}")

            st.markdown("### Income record details")

            income_date = st.date_input("Income received date")

            platform_fee = st.number_input(
                "Platform/payment fee (£)",
                min_value=0.0,
                step=1.0,
                value=0.0
            )

            evidence_note = st.text_input(
                "Evidence note",
                value=f"Invoice {invoice_number} paid by {client_name}"
            )

            duplicate_found = False

            if not income_records.empty and "evidence" in income_records.columns:
                duplicate_found = income_records["evidence"].astype(str).str.contains(invoice_number, case=False, na=False).any()

            if duplicate_found:
                st.warning("This invoice number already appears in your income evidence. Check before converting again.")

            if st.button("Convert selected invoice to income"):
                gross_income = amount
                net_income = gross_income - platform_fee

                new_income = pd.DataFrame(
                    [
                        {
                            "date": str(income_date),
                            "income_stream": side_hustle,
                            "description": f"Invoice payment from {client_name}: {service_description}",
                            "gross_income": gross_income,
                            "platform_fee": platform_fee,
                            "net_income": net_income,
                            "payment_status": "Paid",
                            "evidence": evidence_note,
                        }
                    ]
                )

                income_records = pd.concat([income_records, new_income], ignore_index=True)
                save_income_records(income_records)

                st.success("Invoice converted to income successfully.")
                st.info("Go to Dashboard or Add Income to review the new income record.")

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- First create an invoice on Invoice Draft.")
    st.write("- Save it to Invoice History.")
    st.write("- Mark it as Paid once payment arrives.")
    st.write("- Then use this page to create the income record automatically.")
    st.write("- After conversion, the income will appear on your Dashboard and exports.")



elif page == "Import Expense CSV":
    st.title("Import Expense CSV")
    st.subheader("Upload expense records from a CSV file")

    st.warning(
        "Use this page to import expense records from bank exports, platform fee reports, receipt trackers or manual spreadsheets. "
        "Always check the preview before saving imported expenses."
    )

    uploaded_file = st.file_uploader(
        "Upload expense CSV file",
        type=["csv"],
        key="expense_csv_upload"
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin.")
    else:
        try:
            imported_df = pd.read_csv(uploaded_file)

            if imported_df.empty:
                st.error("The uploaded CSV is empty.")
            else:
                st.markdown("### Uploaded file preview")
                st.dataframe(imported_df.head(20), use_container_width=True)

                st.markdown("### Map your columns")

                csv_columns = imported_df.columns.tolist()
                none_option = "None"

                def guess_column(possible_names):
                    for possible_name in possible_names:
                        for column in csv_columns:
                            if possible_name.lower() in column.lower():
                                return column
                    return csv_columns[0] if csv_columns else none_option

                date_guess = guess_column(["date", "transaction", "purchased", "paid"])
                description_guess = guess_column(["description", "merchant", "supplier", "item", "notes"])
                amount_guess = guess_column(["amount", "cost", "total", "price", "debit"])
                category_guess = guess_column(["category", "type"])

                date_column = st.selectbox(
                    "Date column",
                    csv_columns,
                    index=csv_columns.index(date_guess) if date_guess in csv_columns else 0
                )

                description_column = st.selectbox(
                    "Description/supplier column",
                    csv_columns,
                    index=csv_columns.index(description_guess) if description_guess in csv_columns else 0
                )

                amount_column = st.selectbox(
                    "Expense amount column",
                    csv_columns,
                    index=csv_columns.index(amount_guess) if amount_guess in csv_columns else 0
                )

                category_column = st.selectbox(
                    "Expense category column",
                    [none_option] + csv_columns,
                    index=([none_option] + csv_columns).index(category_guess) if category_guess in csv_columns else 0
                )

                receipt_column = st.selectbox(
                    "Receipt/evidence/reference column",
                    [none_option] + csv_columns,
                    index=0
                )

                default_category = st.selectbox(
                    "Default expense category if no category column is used",
                    [
                        "Postage",
                        "Packaging",
                        "Platform Fees",
                        "Software",
                        "Equipment",
                        "Travel",
                        "Marketing",
                        "Stock/Inventory",
                        "Subscriptions",
                        "Other",
                    ]
                )

                add_import_tag = st.checkbox(
                    "Add CSV import tag to receipt/evidence",
                    value=True
                )

                make_amounts_positive = st.checkbox(
                    "Convert negative bank amounts into positive expense values",
                    value=True
                )

                if st.button("Preview converted expense records"):
                    preview_records = imported_df.copy()

                    preview_records["_date"] = pd.to_datetime(preview_records[date_column], errors="coerce")
                    preview_records["_amount"] = pd.to_numeric(preview_records[amount_column], errors="coerce").fillna(0)

                    if make_amounts_positive:
                        preview_records["_amount"] = preview_records["_amount"].abs()

                    if category_column != none_option:
                        preview_records["_expense_category"] = preview_records[category_column].astype(str)
                    else:
                        preview_records["_expense_category"] = default_category

                    preview_records["_description"] = preview_records[description_column].astype(str)

                    if receipt_column != none_option:
                        preview_records["_receipt"] = preview_records[receipt_column].astype(str)
                    else:
                        preview_records["_receipt"] = "Imported from CSV"

                    if add_import_tag:
                        preview_records["_receipt"] = preview_records["_receipt"] + " | CSV import"

                    converted_records = pd.DataFrame(
                        {
                            "date": preview_records["_date"].dt.date.astype(str),
                            "expense_category": preview_records["_expense_category"],
                            "description": preview_records["_description"],
                            "amount": preview_records["_amount"],
                            "receipt": preview_records["_receipt"],
                        }
                    )

                    converted_records = converted_records[
                        converted_records["amount"] > 0
                    ].copy()

                    st.session_state["expense_import_preview"] = converted_records

                if "expense_import_preview" in st.session_state:
                    converted_records = st.session_state["expense_import_preview"]

                    st.markdown("### Converted expense preview")

                    if converted_records.empty:
                        st.error("No valid expense records found after conversion. Check your amount column.")
                    else:
                        st.dataframe(converted_records, use_container_width=True)

                        total_import_expenses = converted_records["amount"].sum()

                        col1, col2 = st.columns(2)
                        col1.metric("Records ready to import", len(converted_records))
                        col2.metric("Expenses ready to import", f"£{total_import_expenses:,.2f}")

                        existing_expenses = load_expense_records()

                        duplicate_count = 0

                        if not existing_expenses.empty:
                            existing_receipts = []

                            if "receipt" in existing_expenses.columns:
                                existing_receipts = existing_expenses["receipt"].astype(str).tolist()
                            elif "evidence" in existing_expenses.columns:
                                existing_receipts = existing_expenses["evidence"].astype(str).tolist()

                            for receipt_value in converted_records["receipt"].astype(str).tolist():
                                if receipt_value in existing_receipts:
                                    duplicate_count += 1

                        if duplicate_count > 0:
                            st.warning(f"{duplicate_count} possible duplicate expense record(s) found based on receipt/reference text.")

                        confirm_import = st.checkbox(
                            "I have checked the preview and want to save these expense records."
                        )

                        if st.button("Save imported expense records"):
                            if not confirm_import:
                                st.error("Tick the confirmation box before saving.")
                            else:
                                updated_expenses = pd.concat(
                                    [existing_expenses, converted_records],
                                    ignore_index=True
                                )

                                save_expense_records(updated_expenses)

                                st.success("Imported expense records saved successfully.")
                                st.info("Go to Dashboard, Add Expense or Tax-Year Summary to review the imported records.")

                                del st.session_state["expense_import_preview"]

        except Exception as error:
            st.error("CSV import failed.")
            st.exception(error)

    st.markdown("---")

    st.markdown("### CSV import tips")

    st.write("- Your CSV should have at least a date column, description column and amount column.")
    st.write("- Bank exports may show expenses as negative numbers. Use the checkbox to convert them into positive expenses.")
    st.write("- Preview before saving.")
    st.write("- Imported records are added to your main expense records.")
    st.write("- Keep the original receipt, bank export or platform report as evidence.")



elif page == "Recurring Expenses":
    st.title("Recurring Expenses")
    st.subheader("Track regular side-hustle costs and subscriptions")

    recurring_expenses = load_recurring_expense_records()

    st.markdown("### Add recurring expense")

    with st.form("add_recurring_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            expense_name = st.text_input(
                "Expense name",
                placeholder="Example: Canva Pro, domain name, phone bill, software subscription"
            )

            expense_category = st.selectbox(
                "Expense category",
                [
                    "Software",
                    "Subscriptions",
                    "Postage",
                    "Packaging",
                    "Platform Fees",
                    "Equipment",
                    "Travel",
                    "Marketing",
                    "Stock/Inventory",
                    "Phone/Internet",
                    "Other",
                ]
            )

            amount = st.number_input(
                "Amount (£)",
                min_value=0.0,
                step=1.0,
                value=0.0
            )

        with col2:
            frequency = st.selectbox(
                "Frequency",
                [
                    "Weekly",
                    "Fortnightly",
                    "Monthly",
                    "Quarterly",
                    "Yearly",
                    "One-off reminder",
                ]
            )

            next_due_date = st.date_input("Next due date")

            status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Paused",
                    "Cancelled",
                ]
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save recurring expense")

    if submitted:
        if not expense_name.strip():
            st.error("Add an expense name before saving.")
        elif amount <= 0:
            st.error("Add an amount above £0.")
        else:
            new_recurring_expense = pd.DataFrame(
                [
                    {
                        "date_added": str(pd.Timestamp.today().date()),
                        "expense_name": expense_name.strip(),
                        "expense_category": expense_category,
                        "amount": amount,
                        "frequency": frequency,
                        "next_due_date": str(next_due_date),
                        "status": status,
                        "notes": notes.strip(),
                    }
                ]
            )

            recurring_expenses = pd.concat(
                [recurring_expenses, new_recurring_expense],
                ignore_index=True
            )

            save_recurring_expense_records(recurring_expenses)

            st.success("Recurring expense saved successfully.")
            st.rerun()

    st.markdown("---")

    st.markdown("### Recurring expense overview")

    if recurring_expenses.empty:
        st.warning("No recurring expenses saved yet.")
    else:
        recurring_expenses["amount"] = pd.to_numeric(
            recurring_expenses["amount"],
            errors="coerce"
        ).fillna(0)

        active_expenses = recurring_expenses[
            recurring_expenses["status"] == "Active"
        ].copy()

        if not active_expenses.empty:
            active_expenses["estimated_monthly_cost"] = active_expenses.apply(
                lambda row: estimate_monthly_recurring_cost(row["amount"], row["frequency"]),
                axis=1
            )
        else:
            active_expenses["estimated_monthly_cost"] = []

        estimated_monthly_total = active_expenses["estimated_monthly_cost"].sum() if not active_expenses.empty else 0
        estimated_yearly_total = estimated_monthly_total * 12

        next_due_dates = pd.to_datetime(active_expenses["next_due_date"], errors="coerce") if not active_expenses.empty else pd.Series(dtype="datetime64[ns]")
        today = pd.Timestamp.today().normalize()
        due_soon_count = int(((next_due_dates >= today) & (next_due_dates <= today + pd.Timedelta(days=7))).sum()) if not active_expenses.empty else 0
        overdue_count = int((next_due_dates < today).sum()) if not active_expenses.empty else 0

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Recurring expenses", len(recurring_expenses))
        col2.metric("Active expenses", len(active_expenses))
        col3.metric("Est. monthly cost", f"£{estimated_monthly_total:,.2f}")
        col4.metric("Est. yearly cost", f"£{estimated_yearly_total:,.2f}")

        alert1, alert2 = st.columns(2)

        if due_soon_count > 0:
            alert1.warning(f"{due_soon_count} active recurring expense(s) due within 7 days.")
        else:
            alert1.success("No active recurring expenses due within 7 days.")

        if overdue_count > 0:
            alert2.error(f"{overdue_count} active recurring expense(s) appear overdue.")
        else:
            alert2.success("No active recurring expenses appear overdue.")

        st.markdown("### Filter recurring expenses")

        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + sorted(recurring_expenses["status"].dropna().unique().tolist())
        )

        category_filter = st.selectbox(
            "Filter by category",
            ["All"] + sorted(recurring_expenses["expense_category"].dropna().unique().tolist())
        )

        filtered_expenses = recurring_expenses.copy()

        if status_filter != "All":
            filtered_expenses = filtered_expenses[filtered_expenses["status"] == status_filter]

        if category_filter != "All":
            filtered_expenses = filtered_expenses[filtered_expenses["expense_category"] == category_filter]

        display_expenses = filtered_expenses.copy()

        display_expenses["amount"] = pd.to_numeric(
            display_expenses["amount"],
            errors="coerce"
        ).fillna(0)

        display_expenses["estimated_monthly_cost"] = display_expenses.apply(
            lambda row: estimate_monthly_recurring_cost(row["amount"], row["frequency"]),
            axis=1
        )

        st.dataframe(display_expenses, use_container_width=True)

        st.download_button(
            "Download recurring expenses CSV",
            data=recurring_expenses.to_csv(index=False).encode("utf-8"),
            file_name="hustlehq_recurring_expenses.csv",
            mime="text/csv",
        )

        st.markdown("### Convert recurring expense to actual expense")

        convert_options = [
            f"{index} - {row['expense_name']} - £{float(row['amount']):,.2f} ({row['frequency']})"
            for index, row in recurring_expenses.iterrows()
        ]

        selected_convert = st.selectbox(
            "Choose recurring expense to log now",
            convert_options,
            key="recurring_expense_convert_select"
        )

        if st.button("Log selected recurring expense as actual expense"):
            selected_index = int(selected_convert.split(" - ")[0])
            selected_row = recurring_expenses.loc[selected_index]

            expense_records = load_expense_records()

            new_expense = pd.DataFrame(
                [
                    {
                        "date": str(pd.Timestamp.today().date()),
                        "expense_category": selected_row["expense_category"],
                        "description": f"Recurring expense: {selected_row['expense_name']}",
                        "amount": float(selected_row["amount"]),
                        "receipt": f"Recurring expense log | {selected_row['expense_name']}",
                    }
                ]
            )

            expense_records = pd.concat([expense_records, new_expense], ignore_index=True)
            save_expense_records(expense_records)

            st.success("Recurring expense logged as an actual expense.")
            st.info("Go to Dashboard or Add Expense to review it.")

        st.markdown("### Delete recurring expense")

        delete_options = [
            f"{index} - {row['expense_name']} ({row['status']})"
            for index, row in recurring_expenses.iterrows()
        ]

        selected_delete = st.selectbox(
            "Choose recurring expense to delete",
            delete_options,
            key="delete_recurring_expense_select"
        )

        if st.button("Delete selected recurring expense"):
            selected_index = int(selected_delete.split(" - ")[0])
            recurring_expenses = recurring_expenses.drop(index=selected_index).reset_index(drop=True)
            save_recurring_expense_records(recurring_expenses)

            st.success("Recurring expense deleted.")
            st.rerun()

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Add regular costs like Canva, domains, subscriptions, packaging suppliers or software.")
    st.write("- Use monthly and yearly estimates to see how much your side hustles really cost.")
    st.write("- Convert a recurring expense into an actual expense when it is paid.")
    st.write("- Keep cancelled expenses recorded if you want history, or delete them if not needed.")



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
elif page == "Tax-Year Summary":
    st.title("Tax-Year Summary")
    st.subheader("Review income, expenses and profit by UK tax year")

    st.warning(
        "This page helps organise your records by UK tax year. It does not calculate your official tax bill and is not tax advice."
    )

    income_records = load_income_records()
    expense_records = load_expense_records()

    if income_records.empty and expense_records.empty:
        st.warning("No income or expense records yet. Add records first to generate a tax-year summary.")
    else:
        if not income_records.empty:
            income_records = add_tax_year_column(income_records)
            income_records["net_income"] = pd.to_numeric(income_records["net_income"], errors="coerce").fillna(0)

        if not expense_records.empty:
            expense_records = add_tax_year_column(expense_records)
            expense_records["amount"] = pd.to_numeric(expense_records["amount"], errors="coerce").fillna(0)

        tax_years = []

        if not income_records.empty:
            tax_years.extend(income_records["tax_year"].dropna().unique().tolist())

        if not expense_records.empty:
            tax_years.extend(expense_records["tax_year"].dropna().unique().tolist())

        tax_years = sorted(list(set(tax_years)))

        if "Unknown" in tax_years:
            tax_years.remove("Unknown")
            tax_years.append("Unknown")

        selected_tax_year = st.selectbox(
            "Select tax year",
            tax_years
        )

        selected_income = pd.DataFrame()
        selected_expenses = pd.DataFrame()

        if not income_records.empty:
            selected_income = income_records[income_records["tax_year"] == selected_tax_year].copy()

        if not expense_records.empty:
            selected_expenses = expense_records[expense_records["tax_year"] == selected_tax_year].copy()

        total_income = selected_income["net_income"].sum() if not selected_income.empty else 0
        total_expenses = selected_expenses["amount"].sum() if not selected_expenses.empty else 0
        profit = total_income - total_expenses

        st.markdown("### Selected tax-year summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Tax year", selected_tax_year)
        col2.metric("Income", f"£{total_income:,.2f}")
        col3.metric("Expenses", f"£{total_expenses:,.2f}")
        col4.metric("Profit", f"£{profit:,.2f}")

        st.markdown("### Trading allowance reference")

        trading_allowance = 1000

        if total_income <= trading_allowance:
            st.info(
                f"Recorded income for this tax year is £{total_income:,.2f}, which is at or below the £1,000 trading allowance reference point."
            )
        else:
            excess = total_income - trading_allowance
            st.warning(
                f"Recorded income is £{total_income:,.2f}, which is £{excess:,.2f} above the £1,000 trading allowance reference point. "
                "Check HMRC guidance or speak to a tax professional if unsure."
            )

        st.markdown("### Income by side hustle")

        if selected_income.empty:
            st.warning("No income records found for this tax year.")
        else:
            income_by_stream = selected_income.groupby("income_stream", as_index=False)["net_income"].sum()
            income_by_stream = income_by_stream.rename(
                columns={
                    "income_stream": "Side Hustle",
                    "net_income": "Net Income",
                }
            )
            income_by_stream = income_by_stream.sort_values("Net Income", ascending=False)

            st.dataframe(income_by_stream, use_container_width=True)
            st.bar_chart(income_by_stream.set_index("Side Hustle")["Net Income"])

        st.markdown("### Expenses by category/description")

        if selected_expenses.empty:
            st.warning("No expense records found for this tax year.")
        else:
            if "expense_category" in selected_expenses.columns:
                expense_group_column = "expense_category"
            elif "category" in selected_expenses.columns:
                expense_group_column = "category"
            else:
                expense_group_column = "description"

            expenses_by_group = selected_expenses.groupby(expense_group_column, as_index=False)["amount"].sum()
            expenses_by_group = expenses_by_group.rename(
                columns={
                    expense_group_column: "Expense Group",
                    "amount": "Amount",
                }
            )
            expenses_by_group = expenses_by_group.sort_values("Amount", ascending=False)

            st.dataframe(expenses_by_group, use_container_width=True)
            st.bar_chart(expenses_by_group.set_index("Expense Group")["Amount"])

        st.markdown("### Full tax-year record tables")

        with st.expander("View income records for selected tax year"):
            if selected_income.empty:
                st.write("No income records.")
            else:
                st.dataframe(selected_income, use_container_width=True)

        with st.expander("View expense records for selected tax year"):
            if selected_expenses.empty:
                st.write("No expense records.")
            else:
                st.dataframe(selected_expenses, use_container_width=True)

        st.markdown("### Download tax-year summary")

        summary_rows = [
            {
                "Tax Year": selected_tax_year,
                "Total Income": total_income,
                "Total Expenses": total_expenses,
                "Profit": profit,
                "Trading Allowance Reference": trading_allowance,
                "Income Above Trading Allowance Reference": max(total_income - trading_allowance, 0),
            }
        ]

        tax_year_summary_df = pd.DataFrame(summary_rows)

        st.download_button(
            "Download selected tax-year summary CSV",
            data=tax_year_summary_df.to_csv(index=False).encode("utf-8"),
            file_name=f"hustlehq_tax_year_summary_{selected_tax_year.replace('/', '_')}.csv",
            mime="text/csv",
        )

        st.markdown("### Record quality checks")

        missing_income_evidence = 0
        missing_expense_receipts = 0

        if not selected_income.empty and "evidence" in selected_income.columns:
            missing_income_evidence = selected_income["evidence"].astype(str).str.strip().isin(["", "nan", "None"]).sum()

        if not selected_expenses.empty:
            if "receipt" in selected_expenses.columns:
                missing_expense_receipts = selected_expenses["receipt"].astype(str).str.strip().isin(["", "nan", "None"]).sum()
            elif "evidence" in selected_expenses.columns:
                missing_expense_receipts = selected_expenses["evidence"].astype(str).str.strip().isin(["", "nan", "None"]).sum()

        check1, check2 = st.columns(2)

        if missing_income_evidence == 0:
            check1.success("Income evidence check: no missing evidence detected.")
        else:
            check1.warning(f"Income evidence check: {missing_income_evidence} record(s) may be missing evidence.")

        if missing_expense_receipts == 0:
            check2.success("Expense receipt check: no missing receipts detected.")
        else:
            check2.warning(f"Expense receipt check: {missing_expense_receipts} record(s) may be missing receipt/evidence details.")

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Use this page to review income and expenses by UK tax year.")
    st.write("- Download the tax-year summary CSV before doing self-assessment prep.")
    st.write("- Keep receipts, invoices, platform statements and bank evidence.")
    st.write("- Use HMRC Export for the fuller record pack.")
    st.write("- This page is for organisation, not official tax filing.")



elif page == "Tax Set-Aside Calculator":
    st.title("Tax Set-Aside Calculator")
    st.subheader("Estimate how much side-hustle profit to reserve")

    st.warning(
        "This is a planning calculator only. It does not calculate your official tax bill and is not tax advice."
    )

    income_records = load_income_records()
    expense_records = load_expense_records()

    if income_records.empty and expense_records.empty:
        st.warning("No income or expense records yet. Add records first to calculate a set-aside amount.")
    else:
        if not income_records.empty:
            income_records = add_tax_year_column(income_records)
            income_records["net_income"] = pd.to_numeric(income_records["net_income"], errors="coerce").fillna(0)

        if not expense_records.empty:
            expense_records = add_tax_year_column(expense_records)
            expense_records["amount"] = pd.to_numeric(expense_records["amount"], errors="coerce").fillna(0)

        tax_years = []

        if not income_records.empty:
            tax_years.extend(income_records["tax_year"].dropna().unique().tolist())

        if not expense_records.empty:
            tax_years.extend(expense_records["tax_year"].dropna().unique().tolist())

        tax_years = sorted(list(set(tax_years)))

        if "Unknown" in tax_years:
            tax_years.remove("Unknown")
            tax_years.append("Unknown")

        selected_tax_year = st.selectbox(
            "Select tax year",
            tax_years,
            key="set_aside_tax_year"
        )

        selected_income = pd.DataFrame()
        selected_expenses = pd.DataFrame()

        if not income_records.empty:
            selected_income = income_records[income_records["tax_year"] == selected_tax_year].copy()

        if not expense_records.empty:
            selected_expenses = expense_records[expense_records["tax_year"] == selected_tax_year].copy()

        total_income = selected_income["net_income"].sum() if not selected_income.empty else 0
        total_expenses = selected_expenses["amount"].sum() if not selected_expenses.empty else 0
        profit = total_income - total_expenses

        st.markdown("### Current tax-year position")

        col1, col2, col3 = st.columns(3)

        col1.metric("Income", f"£{total_income:,.2f}")
        col2.metric("Expenses", f"£{total_expenses:,.2f}")
        col3.metric("Profit", f"£{profit:,.2f}")

        st.markdown("### Set-aside settings")

        set_aside_percentage = st.slider(
            "Percentage of profit to set aside",
            min_value=0,
            max_value=50,
            value=25,
            step=1
        )

        already_reserved = st.number_input(
            "Amount already reserved (£)",
            min_value=0.0,
            step=10.0,
            value=0.0
        )

        if profit <= 0:
            suggested_set_aside = 0
        else:
            suggested_set_aside = profit * (set_aside_percentage / 100)

        remaining_to_reserve = max(suggested_set_aside - already_reserved, 0)

        st.markdown("### Suggested reserve")

        col4, col5, col6 = st.columns(3)

        col4.metric("Set-aside percentage", f"{set_aside_percentage}%")
        col5.metric("Suggested reserve", f"£{suggested_set_aside:,.2f}")
        col6.metric("Still to reserve", f"£{remaining_to_reserve:,.2f}")

        if profit <= 0:
            st.info("Your selected tax-year profit is zero or negative, so this calculator suggests no set-aside yet.")
        elif already_reserved >= suggested_set_aside:
            st.success("You have reserved enough based on this chosen percentage.")
        else:
            st.warning(f"You may want to reserve another £{remaining_to_reserve:,.2f} based on your chosen percentage.")

        st.markdown("### Reserve plan")

        weekly_reserve = remaining_to_reserve / 4 if remaining_to_reserve > 0 else 0
        monthly_reserve = remaining_to_reserve

        col7, col8 = st.columns(2)

        col7.metric("Reserve over 4 weeks", f"£{weekly_reserve:,.2f}/week")
        col8.metric("Reserve this month", f"£{monthly_reserve:,.2f}")

        st.markdown("### Side-hustle contribution")

        if selected_income.empty:
            st.warning("No income records found for this tax year.")
        else:
            income_by_stream = selected_income.groupby("income_stream", as_index=False)["net_income"].sum()
            income_by_stream = income_by_stream.rename(
                columns={
                    "income_stream": "Side Hustle",
                    "net_income": "Net Income",
                }
            )

            income_by_stream["Suggested Set-Aside"] = income_by_stream["Net Income"] * (set_aside_percentage / 100)
            income_by_stream = income_by_stream.sort_values("Net Income", ascending=False)

            st.dataframe(income_by_stream, use_container_width=True)

        st.markdown("### Download set-aside summary")

        summary_df = pd.DataFrame(
            [
                {
                    "Tax Year": selected_tax_year,
                    "Total Income": total_income,
                    "Total Expenses": total_expenses,
                    "Profit": profit,
                    "Set Aside Percentage": set_aside_percentage,
                    "Suggested Reserve": suggested_set_aside,
                    "Already Reserved": already_reserved,
                    "Remaining To Reserve": remaining_to_reserve,
                    "Weekly Reserve Over 4 Weeks": weekly_reserve,
                }
            ]
        )

        st.download_button(
            "Download set-aside summary CSV",
            data=summary_df.to_csv(index=False).encode("utf-8"),
            file_name=f"hustlehq_tax_set_aside_{selected_tax_year.replace('/', '_')}.csv",
            mime="text/csv",
        )

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Use this as a conservative planning tool.")
    st.write("- Choose your own set-aside percentage.")
    st.write("- Keep the reserved money separate from spending money.")
    st.write("- Check HMRC guidance or speak to a tax professional before filing anything.")
    st.write("- Use Tax-Year Summary and HMRC Export for fuller record checking.")



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


elif page == "Monthly Insights":
    st.title("Monthly Insights")
    st.subheader("Track monthly income, expenses, profit and side-hustle consistency")

    income_records = load_income_records()
    expense_records = load_expense_records()
    goals = load_goal_settings()

    monthly_income_goal = float(goals.get("monthly_income_goal", 500.0))

    if income_records.empty and expense_records.empty:
        st.warning("No income or expense records yet. Add records first to generate monthly insights.")
    else:
        income_monthly = pd.DataFrame()
        expense_monthly = pd.DataFrame()

        if not income_records.empty:
            income_records["date"] = pd.to_datetime(income_records["date"], errors="coerce")
            income_records["month"] = income_records["date"].dt.to_period("M").astype(str)

            income_monthly = income_records.groupby("month", as_index=False)["net_income"].sum()
            income_monthly = income_monthly.rename(columns={"net_income": "Income"})

        if not expense_records.empty:
            expense_records["date"] = pd.to_datetime(expense_records["date"], errors="coerce")
            expense_records["month"] = expense_records["date"].dt.to_period("M").astype(str)

            expense_monthly = expense_records.groupby("month", as_index=False)["amount"].sum()
            expense_monthly = expense_monthly.rename(columns={"amount": "Expenses"})

        if not income_monthly.empty and not expense_monthly.empty:
            monthly_summary = pd.merge(income_monthly, expense_monthly, on="month", how="outer")
        elif not income_monthly.empty:
            monthly_summary = income_monthly.copy()
            monthly_summary["Expenses"] = 0
        else:
            monthly_summary = expense_monthly.copy()
            monthly_summary["Income"] = 0

        monthly_summary["Income"] = monthly_summary["Income"].fillna(0)
        monthly_summary["Expenses"] = monthly_summary["Expenses"].fillna(0)
        monthly_summary["Profit"] = monthly_summary["Income"] - monthly_summary["Expenses"]
        monthly_summary = monthly_summary.sort_values("month")

        st.markdown("### Monthly performance summary")

        total_months = len(monthly_summary)
        average_monthly_income = monthly_summary["Income"].mean()
        average_monthly_expenses = monthly_summary["Expenses"].mean()
        average_monthly_profit = monthly_summary["Profit"].mean()

        best_month_row = monthly_summary.loc[monthly_summary["Profit"].idxmax()]
        worst_month_row = monthly_summary.loc[monthly_summary["Profit"].idxmin()]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Months tracked", total_months)
        col2.metric("Avg monthly income", f"£{average_monthly_income:,.2f}")
        col3.metric("Avg monthly expenses", f"£{average_monthly_expenses:,.2f}")
        col4.metric("Avg monthly profit", f"£{average_monthly_profit:,.2f}")

        col5, col6 = st.columns(2)

        col5.success(f"Best month: {best_month_row['month']} — £{best_month_row['Profit']:,.2f} profit")
        col6.warning(f"Worst month: {worst_month_row['month']} — £{worst_month_row['Profit']:,.2f} profit")

        st.markdown("### Monthly income vs expenses")

        chart_data = monthly_summary.set_index("month")[["Income", "Expenses", "Profit"]]
        st.bar_chart(chart_data)

        st.markdown("### Monthly goal progress")

        selected_month = st.selectbox(
            "Select month",
            monthly_summary["month"].tolist()
        )

        selected_month_data = monthly_summary[monthly_summary["month"] == selected_month].iloc[0]

        selected_income = selected_month_data["Income"]
        selected_expenses = selected_month_data["Expenses"]
        selected_profit = selected_month_data["Profit"]

        col7, col8, col9 = st.columns(3)

        col7.metric("Selected month income", f"£{selected_income:,.2f}")
        col8.metric("Selected month expenses", f"£{selected_expenses:,.2f}")
        col9.metric("Selected month profit", f"£{selected_profit:,.2f}")

        if monthly_income_goal > 0:
            goal_progress = min(selected_income / monthly_income_goal, 1)
            st.write(f"Monthly income goal: **£{monthly_income_goal:,.2f}**")
            st.progress(goal_progress)

            goal_gap = max(monthly_income_goal - selected_income, 0)

            if goal_gap == 0:
                st.success("This month hit or passed your monthly income goal.")
            else:
                st.info(f"You need **£{goal_gap:,.2f}** more income to hit this month's goal.")

        st.markdown("### Profit by side hustle for selected month")

        if not income_records.empty:
            selected_income_records = income_records[income_records["month"] == selected_month].copy()

            if selected_income_records.empty:
                st.warning("No income records found for this selected month.")
            else:
                stream_summary = selected_income_records.groupby("income_stream", as_index=False)["net_income"].sum()
                stream_summary = stream_summary.rename(columns={"income_stream": "Side Hustle", "net_income": "Net Income"})
                stream_summary = stream_summary.sort_values("Net Income", ascending=False)

                st.dataframe(stream_summary, use_container_width=True)

                st.bar_chart(stream_summary.set_index("Side Hustle")["Net Income"])
        else:
            st.warning("No income records available for side-hustle breakdown.")

        st.markdown("### Monthly summary table")

        display_summary = monthly_summary.copy()
        display_summary["Income"] = display_summary["Income"].map(lambda value: f"£{value:,.2f}")
        display_summary["Expenses"] = display_summary["Expenses"].map(lambda value: f"£{value:,.2f}")
        display_summary["Profit"] = display_summary["Profit"].map(lambda value: f"£{value:,.2f}")

        st.dataframe(display_summary, use_container_width=True)

        st.download_button(
            "Download monthly summary CSV",
            data=monthly_summary.to_csv(index=False).encode("utf-8"),
            file_name="hustlehq_monthly_summary.csv",
            mime="text/csv",
        )

        st.markdown("### Monthly insight notes")

        if average_monthly_profit > 0:
            st.success("Your average monthly profit is positive.")
        elif average_monthly_profit == 0:
            st.warning("Your average monthly profit is currently zero.")
        else:
            st.error("Your average monthly profit is negative. Review expenses or low-profit streams.")

        if average_monthly_income >= monthly_income_goal:
            st.success("Your average monthly income is meeting your saved monthly income goal.")
        else:
            st.info("Your average monthly income is below your saved monthly income goal.")



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


elif page == "Security Status":
    st.title("Security Status")
    st.subheader("Review HustleHQ access protection and safe usage")

    app_settings = load_app_settings()

    st.markdown("### Current protection status")

    password_enabled = app_settings.get("password_protection", True)
    session_authenticated = st.session_state.get("authenticated", False)

    col1, col2, col3 = st.columns(3)

    if password_enabled:
        col1.success("Password protection: ON")
    else:
        col1.error("Password protection: OFF")

    if session_authenticated:
        col2.success("Current session: Logged in")
    else:
        col2.warning("Current session: Not logged in")

    if APP_SETTINGS_FILE.exists():
        col3.success("App settings file: Found")
    else:
        col3.warning("App settings file: Missing")

    st.markdown("### Login controls")

    st.write("Use the sidebar **Log out** button when you finish using HustleHQ.")

    if st.button("Log out now", key="security_status_logout_button"):
        logout_user()

    st.markdown("### Password checklist")

    st.write("- Change the default password from hustlehq123.")
    st.write("- Do not share your Streamlit app link with people you do not trust.")
    st.write("- Do not store highly sensitive financial data online until database security is upgraded.")
    st.write("- Download backups regularly.")
    st.write("- Use Restore Backup only with ZIP files downloaded from your own HustleHQ app.")
    st.write("- Keep your GitHub repository private if you do not want others viewing the source code.")

    st.markdown("### Online deployment note")

    st.warning(
        "This app currently uses local CSV and JSON files for storage. On Streamlit Cloud, this is suitable for demos and light use, "
        "but it is not the same as a proper encrypted database-backed production app."
    )

    st.markdown("### Current security level")

    st.info(
        "Current level: basic password gate. This is better than having the app fully open, but it is not bank-grade authentication."
    )

    st.markdown("### Recommended future upgrades")

    st.write("- Add proper user accounts")
    st.write("- Add a database")
    st.write("- Store passwords securely instead of plain text")
    st.write("- Add environment secrets")
    st.write("- Add private user-specific cloud storage")
    st.write("- Add automatic backup versioning")



elif page == "Release Notes":
    st.title("Release Notes")
    st.subheader("HustleHQ app version and feature history")

    st.markdown("### Current version")

    col1, col2 = st.columns(2)

    col1.metric("Version", APP_VERSION)
    col2.metric("Stage", APP_STAGE)

    st.success("HustleHQ Phase 1 MVP is built, deployed and usable.")

    st.markdown("### Version 1.0.0 features")

    st.write("- Dashboard with income, expenses and profit overview")
    st.write("- Add, edit and delete income records")
    st.write("- Add, edit and delete expense records")
    st.write("- Date tracking and tax-year filtering")
    st.write("- Evidence Centre with missing evidence checks")
    st.write("- HMRC-style CSV export pack")
    st.write("- PDF report generator")
    st.write("- Weekly Review page")
    st.write("- Profit by side hustle analysis")
    st.write("- Saved goal settings")
    st.write("- Cash sprint tracker")
    st.write("- Data Backup page")
    st.write("- Restore Backup page")
    st.write("- Local password protection")
    st.write("- GitHub repo setup")
    st.write("- Streamlit Cloud deployment")

    st.markdown("### What this app is for")

    st.info(
        "HustleHQ helps track personal side-hustle income, expenses, profit, evidence and export records. "
        "It is designed to make your side-hustle records cleaner and easier to review."
    )

    st.markdown("### What this app is not")

    st.warning(
        "This app does not file anything to HMRC, does not calculate official tax liability, "
        "and is not professional tax advice."
    )

    st.markdown("### Suggested next upgrades")

    st.write("- Add a proper database instead of local CSV files")
    st.write("- Add login accounts for multiple users")
    st.write("- Add cloud-safe storage")
    st.write("- Add automatic monthly summaries")
    st.write("- Add charts for income consistency")
    st.write("- Add client/project-level tracking")
    st.write("- Add invoice-style exports")
    st.write("- Add mobile layout polish")

    st.markdown("### Deployment status")

    st.success("Local app: working")
    st.success("GitHub repo: connected")
    st.success("Streamlit deployment: working")

    st.markdown("### Recommended usage")

    st.write("- Keep downloading backups regularly")
    st.write("- Avoid storing highly sensitive financial data online until database security is upgraded")
    st.write("- Use the online version mainly for demos, testing and light tracking")
    st.write("- Use backups before major edits or upgrades")



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
