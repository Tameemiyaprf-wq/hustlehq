from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from zipfile import ZipFile
from datetime import date
import json

import pandas as pd
import calendar
import html
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="HustleHQ",
    page_icon="💼",
    layout="wide"
)

st.markdown(
    """
    <style>
    .hustlehq-mobile-note {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 12px 0 18px 0;
        color: #064E3B;
        font-size: 0.95rem;
        line-height: 1.45;
    }

    .hustlehq-action-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    .hustlehq-action-card h4 {
        margin-top: 0;
        margin-bottom: 6px;
        color: #0B1F33;
    }

    .hustlehq-action-card p {
        margin-bottom: 0;
        color: #475569;
        font-size: 0.95rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.65rem !important;
            line-height: 1.2 !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 12px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }

        button[kind="primary"], .stButton button {
            width: 100%;
            border-radius: 12px;
        }

        .stDownloadButton button {
            width: 100%;
            border-radius: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
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
CONTACT_FILE = DATA_FOLDER / "contact_records.csv"
PERSONAL_ACCOUNT_FILE = DATA_FOLDER / "personal_account_records.csv"
PERSONAL_SUBSCRIPTION_FILE = DATA_FOLDER / "personal_subscription_records.csv"
PERSONAL_SAVINGS_GOAL_FILE = DATA_FOLDER / "personal_savings_goal_records.csv"
PERSONAL_BUDGET_FILE = DATA_FOLDER / "personal_budget_records.csv"
PERSONAL_TRANSACTION_FILE = DATA_FOLDER / "personal_transaction_records.csv"



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



def load_contact_records():
    columns = [
        "date_added",
        "contact_name",
        "company_platform",
        "email_or_contact",
        "contact_type",
        "status",
        "expected_value",
        "last_contacted",
        "follow_up_date",
        "notes",
    ]

    if CONTACT_FILE.exists():
        records = pd.read_csv(CONTACT_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["expected_value"] = pd.to_numeric(records["expected_value"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_contact_records(records):
    records.to_csv(CONTACT_FILE, index=False)



def load_personal_account_records():
    columns = [
        "date_added",
        "provider",
        "account_name",
        "account_type",
        "balance",
        "credit_limit",
        "status",
        "notes",
        "last_updated",
    ]

    if PERSONAL_ACCOUNT_FILE.exists():
        records = pd.read_csv(PERSONAL_ACCOUNT_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["balance"] = pd.to_numeric(records["balance"], errors="coerce").fillna(0)
        records["credit_limit"] = pd.to_numeric(records["credit_limit"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_personal_account_records(records):
    records.to_csv(PERSONAL_ACCOUNT_FILE, index=False)


def load_personal_transaction_records():
    columns = [
        "date_added",
        "transaction_date",
        "transaction_type",
        "account",
        "category",
        "description",
        "amount",
        "status",
        "notes",
    ]

    if PERSONAL_TRANSACTION_FILE.exists():
        records = pd.read_csv(PERSONAL_TRANSACTION_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_personal_transaction_records(records):
    records.to_csv(PERSONAL_TRANSACTION_FILE, index=False)



def load_personal_budget_records():
    columns = [
        "date_added",
        "budget_month",
        "budget_year",
        "income_expected",
        "rent_housing",
        "groceries",
        "transport",
        "phone_internet",
        "personal_spending",
        "debt_repayment",
        "savings_contribution",
        "other_fixed_costs",
        "subscription_total",
        "total_planned_outgoing",
        "remaining_money",
        "status",
        "notes",
    ]

    if PERSONAL_BUDGET_FILE.exists():
        records = pd.read_csv(PERSONAL_BUDGET_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        money_columns = [
            "income_expected",
            "rent_housing",
            "groceries",
            "transport",
            "phone_internet",
            "personal_spending",
            "debt_repayment",
            "savings_contribution",
            "other_fixed_costs",
            "subscription_total",
            "total_planned_outgoing",
            "remaining_money",
        ]

        for column in money_columns:
            records[column] = pd.to_numeric(records[column], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_personal_budget_records(records):
    records.to_csv(PERSONAL_BUDGET_FILE, index=False)


def get_subscription_total_for_month(subscription_records, selected_year, selected_month):
    if subscription_records.empty:
        return 0

    records = subscription_records.copy()

    records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)
    records["next_payment_date_dt"] = pd.to_datetime(records["next_payment_date"], errors="coerce")

    month_records = records[
        (records["status"] == "Active")
        & (records["next_payment_date_dt"].dt.year == int(selected_year))
        & (records["next_payment_date_dt"].dt.month == int(selected_month))
    ].copy()

    if month_records.empty:
        return 0

    return month_records["amount"].sum()



def load_personal_savings_goal_records():
    columns = [
        "date_added",
        "goal_name",
        "target_amount",
        "current_amount",
        "linked_account",
        "deadline",
        "priority",
        "status",
        "notes",
    ]

    if PERSONAL_SAVINGS_GOAL_FILE.exists():
        records = pd.read_csv(PERSONAL_SAVINGS_GOAL_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["target_amount"] = pd.to_numeric(records["target_amount"], errors="coerce").fillna(0)
        records["current_amount"] = pd.to_numeric(records["current_amount"], errors="coerce").fillna(0)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_personal_savings_goal_records(records):
    records.to_csv(PERSONAL_SAVINGS_GOAL_FILE, index=False)


def calculate_goal_months_remaining(deadline_value):
    deadline_date = pd.to_datetime(deadline_value, errors="coerce")

    if pd.isna(deadline_date):
        return 0

    today = pd.Timestamp.today().normalize()

    if deadline_date <= today:
        return 0

    days_remaining = (deadline_date - today).days
    months_remaining = max(math.ceil(days_remaining / 30), 1)

    return months_remaining



def load_personal_subscription_records():
    columns = [
        "date_added",
        "subscription_name",
        "amount",
        "category",
        "paid_from_account",
        "next_payment_date",
        "payment_day",
        "colour",
        "status",
        "notes",
    ]

    if PERSONAL_SUBSCRIPTION_FILE.exists():
        records = pd.read_csv(PERSONAL_SUBSCRIPTION_FILE)

        for column in columns:
            if column not in records.columns:
                records[column] = ""

        records["amount"] = pd.to_numeric(records["amount"], errors="coerce").fillna(0)
        records["payment_day"] = pd.to_numeric(records["payment_day"], errors="coerce").fillna(0).astype(int)

        return records[columns]

    return pd.DataFrame(columns=columns)


def save_personal_subscription_records(records):
    records.to_csv(PERSONAL_SUBSCRIPTION_FILE, index=False)


def calculate_personal_net_worth(account_records):
    if account_records.empty:
        return {
            "current_cash": 0,
            "savings": 0,
            "investments": 0,
            "debts": 0,
            "net_worth": 0,
        }

    records = account_records.copy()
    records["balance"] = pd.to_numeric(records["balance"], errors="coerce").fillna(0)

    current_cash = records[
        records["account_type"].isin(["Current Account", "Digital Wallet", "Cash"])
    ]["balance"].sum()

    savings = records[
        records["account_type"] == "Savings Account"
    ]["balance"].sum()

    investments = records[
        records["account_type"].isin(["Investment", "Stocks & Shares ISA", "Lifetime ISA", "Pension"])
    ]["balance"].sum()

    debts = records[
        records["account_type"].isin(["Credit Card", "Loan/Debt"])
    ]["balance"].sum()

    net_worth = current_cash + savings + investments - debts

    return {
        "current_cash": current_cash,
        "savings": savings,
        "investments": investments,
        "debts": debts,
        "net_worth": net_worth,
    }


def get_subscription_colour_hex(colour_name):
    colour_map = {
        "Emerald": "#10B981",
        "Blue": "#3B82F6",
        "Purple": "#8B5CF6",
        "Pink": "#EC4899",
        "Amber": "#F59E0B",
        "Red": "#EF4444",
        "Slate": "#64748B",
    }

    return colour_map.get(colour_name, "#10B981")


def move_subscription_date_forward(current_date_value):
    current_date = pd.to_datetime(current_date_value, errors="coerce")

    if pd.isna(current_date):
        return str(pd.Timestamp.today().date())

    year = int(current_date.year)
    month = int(current_date.month)
    day = int(current_date.day)

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    last_day_next_month = calendar.monthrange(next_year, next_month)[1]
    safe_day = min(day, last_day_next_month)

    return str(date(next_year, next_month, safe_day))



def render_subscription_calendar(subscription_records, selected_year, selected_month):
    active_subscriptions = subscription_records[
        subscription_records["status"] == "Active"
    ].copy()

    if active_subscriptions.empty:
        return "<p>No active subscriptions to show on the calendar.</p>"

    active_subscriptions["next_payment_date_dt"] = pd.to_datetime(
        active_subscriptions["next_payment_date"],
        errors="coerce"
    )

    month_subscriptions = active_subscriptions[
        (active_subscriptions["next_payment_date_dt"].dt.year == selected_year)
        & (active_subscriptions["next_payment_date_dt"].dt.month == selected_month)
    ].copy()

    events_by_day = {}

    for _, row in month_subscriptions.iterrows():
        payment_date = row["next_payment_date_dt"]

        if pd.isna(payment_date):
            continue

        day = int(payment_date.day)

        if day not in events_by_day:
            events_by_day[day] = []

        events_by_day[day].append(
            {
                "name": str(row["subscription_name"]),
                "amount": float(row["amount"]),
                "colour": str(row["colour"]),
                "account": str(row["paid_from_account"]),
            }
        )

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(selected_year, selected_month)
    month_name = calendar.month_name[selected_month]

    html_output = f"""
    <style>
    .pf-calendar {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 8px;
        margin-top: 12px;
    }}

    .pf-calendar th {{
        text-align: center;
        color: #334155;
        font-size: 0.9rem;
        padding-bottom: 6px;
    }}

    .pf-calendar td {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        min-height: 88px;
        height: 88px;
        vertical-align: top;
        padding: 8px;
        width: 14.2%;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }}

    .pf-calendar .empty-day {{
        background: #F8FAFC;
        border: 1px solid #EEF2F7;
    }}

    .pf-day-number {{
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }}

    .pf-event {{
        border-radius: 999px;
        padding: 3px 7px;
        margin-top: 4px;
        color: white;
        font-size: 0.72rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .pf-glow {{
        animation: pfPulse 1.9s infinite;
    }}

    @keyframes pfPulse {{
        0% {{ box-shadow: 0 0 0 rgba(16, 185, 129, 0.0); }}
        50% {{ box-shadow: 0 0 18px rgba(16, 185, 129, 0.45); }}
        100% {{ box-shadow: 0 0 0 rgba(16, 185, 129, 0.0); }}
    }}

    @media (max-width: 768px) {{
        .pf-calendar {{
            border-spacing: 4px;
        }}

        .pf-calendar td {{
            min-height: 72px;
            height: 72px;
            padding: 5px;
        }}

        .pf-event {{
            font-size: 0.62rem;
            padding: 2px 5px;
        }}
    }}
    </style>

    <h3>{month_name} {selected_year}</h3>
    <table class="pf-calendar">
        <tr>
            <th>Mon</th>
            <th>Tue</th>
            <th>Wed</th>
            <th>Thu</th>
            <th>Fri</th>
            <th>Sat</th>
            <th>Sun</th>
        </tr>
    """

    for week in month_days:
        html_output += "<tr>"

        for day in week:
            if day == 0:
                html_output += '<td class="empty-day"></td>'
            else:
                day_events = events_by_day.get(day, [])
                glow_class = "pf-glow" if day_events else ""

                html_output += f'<td class="{glow_class}">'
                html_output += f'<div class="pf-day-number">{day}</div>'

                for event in day_events[:3]:
                    colour_hex = get_subscription_colour_hex(event["colour"])
                    safe_name = html.escape(event["name"])
                    safe_account = html.escape(event["account"])
                    amount = event["amount"]

                    html_output += (
                        f'<div class="pf-event" style="background:{colour_hex};">'
                        f'{safe_name} £{amount:,.2f}'
                        f'</div>'
                    )

                if len(day_events) > 3:
                    html_output += f'<div style="font-size:0.7rem;color:#64748B;margin-top:4px;">+{len(day_events) - 3} more</div>'

                html_output += "</td>"

        html_output += "</tr>"

    html_output += "</table>"

    return html_output



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
        "Mobile Quick Guide",
        "Add Income",
        "Import Income CSV",
        "Add Expense",
        "Import Expense CSV",
        "Recurring Expenses",
        "Project Tracker",
        "Client / Contact Tracker",
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


# =========================
st.markdown(
    """
    <style>
    .pf-dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08);
    }

    .pf-dashboard-card h4 {
        margin: 0 0 6px 0;
        color: #0B1F33;
        font-size: 1rem;
    }

    .pf-dashboard-card p {
        margin: 0;
        color: #64748B;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .pf-money-positive {
        color: #047857;
        font-weight: 800;
    }

    .pf-money-warning {
        color: #B45309;
        font-weight: 800;
    }

    .pf-money-danger {
        color: #B91C1C;
        font-weight: 800;
    }

    .pf-section-pill {
        display: inline-block;
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        border-radius: 999px;
        padding: 5px 11px;
        margin: 4px 5px 4px 0;
        font-size: 0.82rem;
        font-weight: 700;
    }

    @media (max-width: 768px) {
        .pf-dashboard-card {
            padding: 14px;
            border-radius: 15px;
        }

        .pf-section-pill {
            font-size: 0.76rem;
            padding: 4px 9px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# TOP APP SWITCHER
# =========================

if "active_app_section" not in st.session_state:
    st.session_state["active_app_section"] = "HustleHQ"

st.markdown(
    """
    <style>
    .hustlehq-top-switcher {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 12px 16px;
        margin-bottom: 18px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08);
    }

    .hustlehq-top-title {
        font-weight: 800;
        color: #0B1F33;
        font-size: 1.05rem;
        margin-bottom: 2px;
    }

    .hustlehq-top-subtitle {
        color: #64748B;
        font-size: 0.88rem;
    }

    @media (max-width: 768px) {
        .hustlehq-top-switcher {
            padding: 10px 12px;
            margin-bottom: 14px;
        }

        .hustlehq-top-title {
            font-size: 0.95rem;
        }

        .hustlehq-top-subtitle {
            font-size: 0.78rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

top_menu_col, top_label_col = st.columns([0.13, 0.87])

with top_menu_col:
    with st.popover("☰"):
        st.markdown("### Switch section")

        if st.button("💼 HustleHQ", use_container_width=True, key="switch_to_hustlehq"):
            st.session_state["active_app_section"] = "HustleHQ"
            st.rerun()

        if st.button("🏦 Personal Finance", use_container_width=True, key="switch_to_personal_finance"):
            st.session_state["active_app_section"] = "Personal Finance"
            st.rerun()

current_app_section = st.session_state.get("active_app_section", "HustleHQ")

with top_label_col:
    if current_app_section == "Personal Finance":
        st.markdown(
            """
            <div class="hustlehq-top-switcher">
                <div class="hustlehq-top-title">🏦 Personal Finance</div>
                <div class="hustlehq-top-subtitle">Personal accounts, savings, debt, net worth and subscriptions.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="hustlehq-top-switcher">
                <div class="hustlehq-top-title">💼 HustleHQ</div>
                <div class="hustlehq-top-subtitle">Side-hustle income, expenses, invoices, projects and tax records.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if current_app_section == "Personal Finance":
    page = "Personal Finance"

    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        div[data-testid="collapsedControl"] {
            display: none !important;
        }

        .block-container {
            max-width: 1400px;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



if page == "Personal Finance":
    st.title("Personal Finance")
    st.subheader("Personal money, debt, savings and subscription control centre")

    st.info(
        "This section is for personal finance tracking. Bank connections are not live yet. "
        "For now, update balances manually for providers like NatWest, Santander, Zopa, American Express, Trading 212, PayPal and AJ Bell Dodl. "
        "Later, this can be upgraded with Open Banking or platform integrations where available."
    )

    account_records = load_personal_account_records()
    subscription_records = load_personal_subscription_records()

    net_worth_data = calculate_personal_net_worth(account_records)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Current cash", f"£{net_worth_data['current_cash']:,.2f}")
    col2.metric("Savings", f"£{net_worth_data['savings']:,.2f}")
    col3.metric("Investments", f"£{net_worth_data['investments']:,.2f}")
    col4.metric("Debt", f"£{net_worth_data['debts']:,.2f}")
    col5.metric("Net worth", f"£{net_worth_data['net_worth']:,.2f}")

    st.markdown("---")

    personal_tabs = st.tabs(
        [
            "Dashboard",
            "Accounts",
            "Savings",
            "Savings Goals",
            "Debt Manager",
            "Subscriptions",
            "Bills Forecast",
            "Subscription Calendar",
            "Monthly Budget",
            "Transactions",
            "Import Transactions CSV",
        ]
    )

    bank_options = [
        "Santander",
        "NatWest",
        "Zopa",
        "American Express",
        "Trading 212",
        "PayPal",
        "AJ Bell Dodl",
        "Nationwide",
        "Lloyds",
        "Revolut",
        "Monzo",
        "Halifax",
        "Other",
    ]

    with personal_tabs[0]:
        st.markdown("### Personal finance dashboard")

        st.markdown(
            """
            <span class="pf-section-pill">Accounts</span>
            <span class="pf-section-pill">Savings</span>
            <span class="pf-section-pill">Debt</span>
            <span class="pf-section-pill">Subscriptions</span>
            <span class="pf-section-pill">Net worth</span>
            """,
            unsafe_allow_html=True,
        )

        if account_records.empty:
            st.warning("No personal accounts added yet. Go to the Accounts tab to add your bank, savings, credit card, ISA, pension and wallet balances.")
        else:
            display_accounts = account_records.copy()
            display_accounts["balance"] = pd.to_numeric(display_accounts["balance"], errors="coerce").fillna(0)
            display_accounts["credit_limit"] = pd.to_numeric(display_accounts["credit_limit"], errors="coerce").fillna(0)

            total_positive_assets = display_accounts[
                display_accounts["account_type"].isin(
                    [
                        "Current Account",
                        "Savings Account",
                        "Investment",
                        "Stocks & Shares ISA",
                        "Lifetime ISA",
                        "Pension",
                        "Digital Wallet",
                        "Cash",
                    ]
                )
            ]["balance"].sum()

            total_debt = display_accounts[
                display_accounts["account_type"].isin(["Credit Card", "Loan/Debt"])
            ]["balance"].sum()

            credit_cards = display_accounts[
                display_accounts["account_type"] == "Credit Card"
            ].copy()

            total_credit_limit = credit_cards["credit_limit"].sum() if not credit_cards.empty else 0
            total_credit_used = credit_cards["balance"].sum() if not credit_cards.empty else 0

            credit_utilisation = 0
            if total_credit_limit > 0:
                credit_utilisation = (total_credit_used / total_credit_limit) * 100

            dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)

            dash_col1.metric("Total assets", f"£{total_positive_assets:,.2f}")
            dash_col2.metric("Total debt", f"£{total_debt:,.2f}")
            dash_col3.metric("Credit used", f"{credit_utilisation:,.1f}%")
            dash_col4.metric("Accounts tracked", len(display_accounts))

            if credit_utilisation >= 75:
                st.error("Credit utilisation is high. Consider prioritising credit card repayment before adding new spending.")
            elif credit_utilisation >= 30:
                st.warning("Credit utilisation is moderate. Keep an eye on credit card balances.")
            elif total_credit_limit > 0:
                st.success("Credit utilisation is currently in a healthier range.")

            st.markdown("### Account type breakdown")

            account_type_summary = (
                display_accounts
                .groupby("account_type", as_index=False)["balance"]
                .sum()
                .sort_values("balance", ascending=False)
            )

            st.dataframe(account_type_summary, use_container_width=True)

            st.markdown("### Provider breakdown")

            provider_summary = (
                display_accounts
                .groupby("provider", as_index=False)["balance"]
                .sum()
                .sort_values("balance", ascending=False)
            )

            st.dataframe(provider_summary, use_container_width=True)

            st.markdown("### Accounts table")

            st.dataframe(
                display_accounts[
                    [
                        "provider",
                        "account_name",
                        "account_type",
                        "balance",
                        "credit_limit",
                        "status",
                        "last_updated",
                    ]
                ],
                use_container_width=True,
            )

        st.markdown("---")

        st.markdown("### Subscription control panel")

        if subscription_records.empty:
            st.warning("No subscriptions added yet. Go to the Subscriptions tab to add recurring personal payments.")
        else:
            subscription_records["amount"] = pd.to_numeric(subscription_records["amount"], errors="coerce").fillna(0)
            subscription_records["next_payment_date_dt"] = pd.to_datetime(
                subscription_records["next_payment_date"],
                errors="coerce"
            )

            active_subscriptions = subscription_records[
                subscription_records["status"] == "Active"
            ].copy()

            monthly_subscription_total = active_subscriptions["amount"].sum() if not active_subscriptions.empty else 0
            yearly_subscription_total = monthly_subscription_total * 12

            today = pd.Timestamp.today().normalize()

            due_soon = subscription_records[
                (subscription_records["status"] == "Active")
                & (subscription_records["next_payment_date_dt"] >= today)
                & (subscription_records["next_payment_date_dt"] <= today + pd.Timedelta(days=7))
            ].copy()

            overdue_subscriptions = subscription_records[
                (subscription_records["status"] == "Active")
                & (subscription_records["next_payment_date_dt"] < today)
            ].copy()

            sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)

            sub_col1.metric("Active subscriptions", len(active_subscriptions))
            sub_col2.metric("Monthly total", f"£{monthly_subscription_total:,.2f}")
            sub_col3.metric("Yearly total", f"£{yearly_subscription_total:,.2f}")
            sub_col4.metric("Due in 7 days", len(due_soon))

            if not overdue_subscriptions.empty:
                st.error(f"{len(overdue_subscriptions)} active subscription(s) have payment dates in the past. Update their next payment dates.")
            elif not due_soon.empty:
                st.warning(f"{len(due_soon)} subscription(s) are due within 7 days.")
            else:
                st.success("No active subscriptions due in the next 7 days.")

            if not due_soon.empty:
                st.markdown("### Subscriptions due soon")
                st.dataframe(
                    due_soon[
                        [
                            "subscription_name",
                            "amount",
                            "paid_from_account",
                            "next_payment_date",
                            "colour",
                            "category",
                        ]
                    ],
                    use_container_width=True,
                )

            st.markdown("### Subscription cost by payment account")

            subscription_account_summary = (
                active_subscriptions
                .groupby("paid_from_account", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            ) if not active_subscriptions.empty else pd.DataFrame(columns=["paid_from_account", "amount"])

            st.dataframe(subscription_account_summary, use_container_width=True)

            st.markdown("### Subscription cost by category")

            subscription_category_summary = (
                active_subscriptions
                .groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            ) if not active_subscriptions.empty else pd.DataFrame(columns=["category", "amount"])

            st.dataframe(subscription_category_summary, use_container_width=True)

        st.markdown("---")

        st.markdown("### What to update regularly")

        st.markdown(
            """
            <div class="pf-dashboard-card">
                <h4>Weekly money check</h4>
                <p>Update current account balances, credit card debt, PayPal balance and any new savings movements.</p>
            </div>
            <div class="pf-dashboard-card">
                <h4>Monthly subscription check</h4>
                <p>Check the subscription calendar before payments come out so you know which account needs money in it.</p>
            </div>
            <div class="pf-dashboard-card">
                <h4>Investment check</h4>
                <p>Update Trading 212 and AJ Bell Dodl balances manually until direct platform integrations are added.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


    with personal_tabs[1]:
        st.markdown("### Add personal account")

        with st.form("add_personal_account_form"):
            col_a, col_b = st.columns(2)

            with col_a:
                provider = st.selectbox("Bank/provider", bank_options)

                account_name = st.text_input(
                    "Account name",
                    placeholder="Example: NatWest Current, Amex Card, Zopa Smart Saver"
                )

                account_type = st.selectbox(
                    "Account type",
                    [
                        "Current Account",
                        "Savings Account",
                        "Credit Card",
                        "Loan/Debt",
                        "Investment",
                        "Stocks & Shares ISA",
                        "Lifetime ISA",
                        "Pension",
                        "Digital Wallet",
                        "Cash",
                    ]
                )

            with col_b:
                balance = st.number_input(
                    "Balance / amount owed (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0,
                    help="For current/savings accounts, enter the money you have. For credit cards/loans, enter the amount owed."
                )

                credit_limit = st.number_input(
                    "Credit limit (£)",
                    min_value=0.0,
                    step=50.0,
                    value=0.0,
                    help="Only needed for credit cards or overdraft-style accounts."
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Active",
                        "Closed",
                        "Paused",
                    ]
                )

            notes = st.text_area("Notes", placeholder="Example: Main spending account, emergency fund, card used for Plan It, etc.")

            submitted_account = st.form_submit_button("Save personal account")

        if submitted_account:
            if not account_name.strip():
                st.error("Add an account name before saving.")
            else:
                new_account = pd.DataFrame(
                    [
                        {
                            "date_added": str(pd.Timestamp.today().date()),
                            "provider": provider,
                            "account_name": account_name.strip(),
                            "account_type": account_type,
                            "balance": balance,
                            "credit_limit": credit_limit,
                            "status": status,
                            "notes": notes.strip(),
                            "last_updated": str(pd.Timestamp.today().date()),
                        }
                    ]
                )

                account_records = pd.concat([account_records, new_account], ignore_index=True)
                save_personal_account_records(account_records)

                st.success("Personal account saved.")
                st.rerun()

        st.markdown("### Account records")

        if account_records.empty:
            st.warning("No accounts saved yet.")
        else:
            st.dataframe(account_records, use_container_width=True)

            st.markdown("### Update account balance")

            update_options = [
                f"{index} - {row['provider']} - {row['account_name']} ({row['account_type']})"
                for index, row in account_records.iterrows()
            ]

            selected_account_update = st.selectbox(
                "Choose account to update",
                update_options,
                key="personal_account_update_select"
            )

            selected_update_index = int(selected_account_update.split(" - ")[0])
            selected_update_row = account_records.loc[selected_update_index]

            new_balance = st.number_input(
                "New balance / amount owed (£)",
                min_value=0.0,
                step=10.0,
                value=float(selected_update_row["balance"]),
                key="personal_account_new_balance"
            )

            if st.button("Update selected account balance"):
                account_records.loc[selected_update_index, "balance"] = new_balance
                account_records.loc[selected_update_index, "last_updated"] = str(pd.Timestamp.today().date())
                save_personal_account_records(account_records)

                st.success("Account balance updated.")
                st.rerun()

            st.markdown("### Delete account")

            selected_account_delete = st.selectbox(
                "Choose account to delete",
                update_options,
                key="personal_account_delete_select"
            )

            if st.button("Delete selected account"):
                selected_delete_index = int(selected_account_delete.split(" - ")[0])
                account_records = account_records.drop(index=selected_delete_index).reset_index(drop=True)
                save_personal_account_records(account_records)

                st.success("Account deleted.")
                st.rerun()

            st.download_button(
                "Download personal accounts CSV",
                data=account_records.to_csv(index=False).encode("utf-8"),
                file_name="hustlehq_personal_accounts.csv",
                mime="text/csv",
            )

    with personal_tabs[2]:
        st.markdown("### Savings tracker")

        savings_records = account_records[
            account_records["account_type"].isin(["Savings Account", "Lifetime ISA"])
        ].copy()

        if savings_records.empty:
            st.warning("No savings accounts or Lifetime ISA accounts added yet. Add them in the Accounts tab using account type: Savings Account or Lifetime ISA.")
        else:
            savings_records["balance"] = pd.to_numeric(savings_records["balance"], errors="coerce").fillna(0)

            total_savings = savings_records["balance"].sum()

            st.metric("Total savings", f"£{total_savings:,.2f}")

            st.dataframe(
                savings_records[
                    [
                        "provider",
                        "account_name",
                        "balance",
                        "status",
                        "last_updated",
                        "notes",
                    ]
                ],
                use_container_width=True,
            )

        st.info(
            "Savings goals will come in Part 2P. For Part 1P, this section focuses on recording how much is inside each savings account."
        )

    with personal_tabs[3]:
        st.markdown("### Savings Goals")
        st.subheader("Track emergency funds, move-out savings, ISA goals and personal targets")

        savings_goal_records = load_personal_savings_goal_records()

        savings_account_options = ["Manual / not linked"]

        if not account_records.empty:
            savings_like_accounts = account_records[
                account_records["account_type"].isin(
                    [
                        "Savings Account",
                        "Lifetime ISA",
                        "Stocks & Shares ISA",
                        "Investment",
                        "Pension",
                    ]
                )
            ].copy()

            if not savings_like_accounts.empty:
                savings_account_options += [
                    f"{row['provider']} - {row['account_name']}"
                    for _, row in savings_like_accounts.iterrows()
                ]

        st.markdown("### Add savings goal")

        with st.form("add_personal_savings_goal_form"):
            goal_col1, goal_col2 = st.columns(2)

            with goal_col1:
                goal_name = st.text_input(
                    "Goal name",
                    placeholder="Example: Emergency fund, Move-out fund, LISA deposit, Laptop fund"
                )

                target_amount = st.number_input(
                    "Target amount (£)",
                    min_value=0.0,
                    step=50.0,
                    value=0.0
                )

                current_amount = st.number_input(
                    "Current amount saved (£)",
                    min_value=0.0,
                    step=25.0,
                    value=0.0
                )

                linked_account = st.selectbox(
                    "Linked account",
                    savings_account_options
                )

            with goal_col2:
                deadline = st.date_input("Goal deadline")

                priority = st.selectbox(
                    "Priority",
                    [
                        "High",
                        "Medium",
                        "Low",
                    ]
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Active",
                        "Paused",
                        "Completed",
                        "Cancelled",
                    ]
                )

            notes = st.text_area("Goal notes")

            submitted_goal = st.form_submit_button("Save savings goal")

        if submitted_goal:
            if not goal_name.strip():
                st.error("Add a goal name before saving.")
            elif target_amount <= 0:
                st.error("Add a target amount above £0.")
            else:
                new_goal = pd.DataFrame(
                    [
                        {
                            "date_added": str(pd.Timestamp.today().date()),
                            "goal_name": goal_name.strip(),
                            "target_amount": target_amount,
                            "current_amount": current_amount,
                            "linked_account": linked_account,
                            "deadline": str(deadline),
                            "priority": priority,
                            "status": status,
                            "notes": notes.strip(),
                        }
                    ]
                )

                savings_goal_records = pd.concat(
                    [savings_goal_records, new_goal],
                    ignore_index=True
                )

                save_personal_savings_goal_records(savings_goal_records)

                st.success("Savings goal saved.")
                st.rerun()

        st.markdown("---")

        st.markdown("### Savings goal overview")

        if savings_goal_records.empty:
            st.warning("No savings goals saved yet.")
        else:
            savings_goal_records["target_amount"] = pd.to_numeric(
                savings_goal_records["target_amount"],
                errors="coerce"
            ).fillna(0)

            savings_goal_records["current_amount"] = pd.to_numeric(
                savings_goal_records["current_amount"],
                errors="coerce"
            ).fillna(0)

            active_goals = savings_goal_records[
                savings_goal_records["status"] == "Active"
            ].copy()

            total_target = active_goals["target_amount"].sum() if not active_goals.empty else 0
            total_saved = active_goals["current_amount"].sum() if not active_goals.empty else 0
            remaining_to_save = max(total_target - total_saved, 0)

            overall_progress = 0

            if total_target > 0:
                overall_progress = min((total_saved / total_target) * 100, 100)

            goal_metric1, goal_metric2, goal_metric3, goal_metric4 = st.columns(4)

            goal_metric1.metric("Active goals", len(active_goals))
            goal_metric2.metric("Total target", f"£{total_target:,.2f}")
            goal_metric3.metric("Saved so far", f"£{total_saved:,.2f}")
            goal_metric4.metric("Remaining", f"£{remaining_to_save:,.2f}")

            st.progress(overall_progress / 100)
            st.caption(f"Overall active-goal progress: {overall_progress:,.1f}%")

            display_goals = savings_goal_records.copy()

            display_goals["progress_%"] = display_goals.apply(
                lambda row: min((row["current_amount"] / row["target_amount"] * 100), 100) if row["target_amount"] > 0 else 0,
                axis=1
            )

            display_goals["remaining_amount"] = display_goals.apply(
                lambda row: max(row["target_amount"] - row["current_amount"], 0),
                axis=1
            )

            display_goals["months_remaining"] = display_goals["deadline"].apply(
                calculate_goal_months_remaining
            )

            display_goals["monthly_needed"] = display_goals.apply(
                lambda row: row["remaining_amount"] / row["months_remaining"] if row["months_remaining"] > 0 else row["remaining_amount"],
                axis=1
            )

            st.markdown("### Goal table")

            st.dataframe(
                display_goals[
                    [
                        "goal_name",
                        "target_amount",
                        "current_amount",
                        "remaining_amount",
                        "progress_%",
                        "monthly_needed",
                        "linked_account",
                        "deadline",
                        "priority",
                        "status",
                        "notes",
                    ]
                ],
                use_container_width=True,
            )

            st.markdown("### Emergency fund check")

            emergency_keywords = ["emergency", "buffer", "safety"]

            emergency_goals = display_goals[
                display_goals["goal_name"].astype(str).str.lower().apply(
                    lambda value: any(keyword in value for keyword in emergency_keywords)
                )
            ].copy()

            if emergency_goals.empty:
                st.info("No emergency fund goal found. Consider adding one called Emergency Fund or Safety Buffer.")
            else:
                emergency_saved = emergency_goals["current_amount"].sum()
                emergency_target = emergency_goals["target_amount"].sum()

                emergency_progress = 0

                if emergency_target > 0:
                    emergency_progress = min((emergency_saved / emergency_target) * 100, 100)

                st.metric("Emergency fund saved", f"£{emergency_saved:,.2f}")
                st.progress(emergency_progress / 100)
                st.caption(f"Emergency fund progress: {emergency_progress:,.1f}%")

            st.markdown("### Update savings goal progress")

            goal_options = [
                f"{index} - {row['goal_name']} - £{float(row['current_amount']):,.2f} / £{float(row['target_amount']):,.2f}"
                for index, row in savings_goal_records.iterrows()
            ]

            selected_goal_update = st.selectbox(
                "Choose goal to update",
                goal_options,
                key="personal_savings_goal_update_select"
            )

            selected_goal_index = int(selected_goal_update.split(" - ")[0])
            selected_goal_row = savings_goal_records.loc[selected_goal_index]

            updated_current_amount = st.number_input(
                "Updated current amount saved (£)",
                min_value=0.0,
                step=25.0,
                value=float(selected_goal_row["current_amount"]),
                key="personal_savings_goal_updated_amount"
            )

            if st.button("Update selected savings goal"):
                savings_goal_records.loc[selected_goal_index, "current_amount"] = updated_current_amount
                save_personal_savings_goal_records(savings_goal_records)

                st.success("Savings goal updated.")
                st.rerun()

            st.markdown("### Delete savings goal")

            selected_goal_delete = st.selectbox(
                "Choose goal to delete",
                goal_options,
                key="personal_savings_goal_delete_select"
            )

            if st.button("Delete selected savings goal"):
                selected_delete_index = int(selected_goal_delete.split(" - ")[0])
                savings_goal_records = savings_goal_records.drop(index=selected_delete_index).reset_index(drop=True)
                save_personal_savings_goal_records(savings_goal_records)

                st.success("Savings goal deleted.")
                st.rerun()

            st.download_button(
                "Download savings goals CSV",
                data=savings_goal_records.to_csv(index=False).encode("utf-8"),
                file_name="hustlehq_personal_savings_goals.csv",
                mime="text/csv",
            )

        st.markdown("---")

        st.info(
            "Use savings goals for money you are building up intentionally. "
            "Use the Accounts tab for the actual balance inside each account."
        )




    with personal_tabs[4]:
        st.markdown("### Debt Manager")
        st.subheader("Track credit cards, loans, repayments and available credit")

        if account_records.empty:
            st.warning("No personal accounts added yet. Add credit cards or loans in the Accounts tab first.")
        else:
            debt_records = account_records[
                account_records["account_type"].isin(["Credit Card", "Loan/Debt"])
            ].copy()

            if debt_records.empty:
                st.warning("No debt accounts found. Add a credit card or loan in the Accounts tab.")
                st.info("Use account type: Credit Card or Loan/Debt.")
            else:
                debt_records["balance"] = pd.to_numeric(
                    debt_records["balance"],
                    errors="coerce"
                ).fillna(0)

                debt_records["credit_limit"] = pd.to_numeric(
                    debt_records["credit_limit"],
                    errors="coerce"
                ).fillna(0)

                credit_card_records = debt_records[
                    debt_records["account_type"] == "Credit Card"
                ].copy()

                total_debt = debt_records["balance"].sum()
                total_credit_limit = credit_card_records["credit_limit"].sum() if not credit_card_records.empty else 0
                total_credit_used = credit_card_records["balance"].sum() if not credit_card_records.empty else 0
                available_credit = total_credit_limit - total_credit_used

                credit_utilisation = 0

                if total_credit_limit > 0:
                    credit_utilisation = (total_credit_used / total_credit_limit) * 100

                debt_col1, debt_col2, debt_col3, debt_col4 = st.columns(4)

                debt_col1.metric("Total debt", f"£{total_debt:,.2f}")
                debt_col2.metric("Credit used", f"£{total_credit_used:,.2f}")
                debt_col3.metric("Available credit", f"£{available_credit:,.2f}")
                debt_col4.metric("Credit utilisation", f"{credit_utilisation:,.1f}%")

                if credit_utilisation >= 90:
                    st.error("Credit utilisation is very high. This can make your finances feel tight and may affect your credit profile.")
                elif credit_utilisation >= 75:
                    st.error("Credit utilisation is high. Prioritise reducing credit card balances where possible.")
                elif credit_utilisation >= 30:
                    st.warning("Credit utilisation is moderate. Keep monitoring it and avoid relying on the card for normal spending.")
                elif total_credit_limit > 0:
                    st.success("Credit utilisation is currently in a healthier range.")

                st.markdown("### Debt accounts")

                debt_display = debt_records.copy()

                debt_display["available_credit"] = debt_display["credit_limit"] - debt_display["balance"]

                debt_display["utilisation_%"] = debt_display.apply(
                    lambda row: (row["balance"] / row["credit_limit"] * 100) if row["credit_limit"] > 0 and row["account_type"] == "Credit Card" else 0,
                    axis=1
                )

                st.dataframe(
                    debt_display[
                        [
                            "provider",
                            "account_name",
                            "account_type",
                            "balance",
                            "credit_limit",
                            "available_credit",
                            "utilisation_%",
                            "status",
                            "last_updated",
                            "notes",
                        ]
                    ],
                    use_container_width=True,
                )

                st.markdown("### Debt by provider")

                debt_by_provider = (
                    debt_records
                    .groupby("provider", as_index=False)["balance"]
                    .sum()
                    .sort_values("balance", ascending=False)
                )

                st.dataframe(debt_by_provider, use_container_width=True)

                st.markdown("### Repayment simulator")

                sim_col1, sim_col2 = st.columns(2)

                with sim_col1:
                    simulator_debt = st.number_input(
                        "Debt balance to simulate (£)",
                        min_value=0.0,
                        step=10.0,
                        value=float(total_debt)
                    )

                with sim_col2:
                    monthly_payment = st.number_input(
                        "Monthly repayment (£)",
                        min_value=0.0,
                        step=10.0,
                        value=50.0
                    )

                if simulator_debt > 0 and monthly_payment > 0:
                    months_to_clear = int((simulator_debt + monthly_payment - 0.01) // monthly_payment)
                    years_to_clear = months_to_clear / 12

                    sim_a, sim_b = st.columns(2)

                    sim_a.metric("Months to clear", months_to_clear)
                    sim_b.metric("Years to clear", f"{years_to_clear:,.1f}")

                    st.info(
                        "This is a simple repayment estimate and does not include interest, fees, Plan It instalment structures, "
                        "minimum-payment rules or new spending."
                    )
                else:
                    st.warning("Enter a debt balance and monthly payment above £0 to use the simulator.")

                st.markdown("### Log a debt repayment")

                debt_options = [
                    f"{index} - {row['provider']} - {row['account_name']} - £{float(row['balance']):,.2f}"
                    for index, row in account_records.iterrows()
                    if row["account_type"] in ["Credit Card", "Loan/Debt"]
                ]

                if not debt_options:
                    st.info("No debt accounts available for repayment logging.")
                else:
                    selected_debt = st.selectbox(
                        "Choose debt account",
                        debt_options,
                        key="personal_debt_repayment_select"
                    )

                    repayment_amount = st.number_input(
                        "Repayment amount (£)",
                        min_value=0.0,
                        step=10.0,
                        value=0.0,
                        key="personal_debt_repayment_amount"
                    )

                    if st.button("Apply repayment to selected debt"):
                        if repayment_amount <= 0:
                            st.error("Enter a repayment amount above £0.")
                        else:
                            selected_debt_index = int(selected_debt.split(" - ")[0])
                            current_balance = float(account_records.loc[selected_debt_index, "balance"])
                            new_balance = max(current_balance - repayment_amount, 0)

                            account_records.loc[selected_debt_index, "balance"] = new_balance
                            account_records.loc[selected_debt_index, "last_updated"] = str(pd.Timestamp.today().date())

                            save_personal_account_records(account_records)

                            st.success(
                                f"Repayment applied. New balance: £{new_balance:,.2f}."
                            )
                            st.rerun()

                st.markdown("### Debt management notes")

                st.write("- For credit cards, enter the amount owed as the balance.")
                st.write("- For American Express Plan It, you can either track the full Amex balance or create a separate Loan/Debt account called Amex Plan It.")
                st.write("- Use the repayment logger after you make a payment so your net worth updates.")
                st.write("- Keep credit limits updated so utilisation is accurate.")

                st.download_button(
                    "Download debt accounts CSV",
                    data=debt_display.to_csv(index=False).encode("utf-8"),
                    file_name="hustlehq_personal_debt_accounts.csv",
                    mime="text/csv",
                )




    with personal_tabs[5]:
        st.markdown("### Add subscription")

        account_options = []

        if not account_records.empty:
            account_options = [
                f"{row['provider']} - {row['account_name']}"
                for _, row in account_records.iterrows()
            ]

        fallback_account_options = [
            "Santander",
            "NatWest",
            "Zopa",
            "American Express",
            "Trading 212",
            "PayPal",
            "AJ Bell Dodl",
            "Nationwide",
            "Lloyds",
            "Revolut",
            "Monzo",
            "Halifax",
            "Other",
        ]

        paid_from_options = account_options if account_options else fallback_account_options

        with st.form("add_personal_subscription_form"):
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                subscription_name = st.text_input(
                    "Subscription name",
                    placeholder="Example: Spotify, Canva, iCloud, Gym, Netflix"
                )

                amount = st.number_input(
                    "Monthly amount (£)",
                    min_value=0.0,
                    step=1.0,
                    value=0.0
                )

                category = st.selectbox(
                    "Category",
                    [
                        "Entertainment",
                        "Phone/Internet",
                        "Software",
                        "Finance",
                        "Shopping",
                        "Health/Fitness",
                        "Transport",
                        "Education",
                        "Insurance",
                        "Other",
                    ]
                )

                paid_from_account = st.selectbox(
                    "Paid from account",
                    paid_from_options
                )

            with col_s2:
                next_payment_date = st.date_input("Next payment date")

                payment_day = int(next_payment_date.day)

                colour = st.selectbox(
                    "Calendar glow colour",
                    [
                        "Emerald",
                        "Blue",
                        "Purple",
                        "Pink",
                        "Amber",
                        "Red",
                        "Slate",
                    ]
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Active",
                        "Paused",
                        "Cancelled",
                    ]
                )

            notes = st.text_area("Subscription notes")

            submitted_subscription = st.form_submit_button("Save subscription")

        if submitted_subscription:
            if not subscription_name.strip():
                st.error("Add a subscription name before saving.")
            elif amount <= 0:
                st.error("Add an amount above £0.")
            else:
                new_subscription = pd.DataFrame(
                    [
                        {
                            "date_added": str(pd.Timestamp.today().date()),
                            "subscription_name": subscription_name.strip(),
                            "amount": amount,
                            "category": category,
                            "paid_from_account": paid_from_account,
                            "next_payment_date": str(next_payment_date),
                            "payment_day": payment_day,
                            "colour": colour,
                            "status": status,
                            "notes": notes.strip(),
                        }
                    ]
                )

                subscription_records = pd.concat([subscription_records, new_subscription], ignore_index=True)
                save_personal_subscription_records(subscription_records)

                st.success("Subscription saved.")
                st.rerun()

        st.markdown("### Subscription records")

        if subscription_records.empty:
            st.warning("No subscriptions saved yet.")
        else:
            subscription_records["amount"] = pd.to_numeric(subscription_records["amount"], errors="coerce").fillna(0)

            active_subscriptions = subscription_records[
                subscription_records["status"] == "Active"
            ].copy()

            active_total = active_subscriptions["amount"].sum() if not active_subscriptions.empty else 0

            col_sub_1, col_sub_2, col_sub_3 = st.columns(3)

            col_sub_1.metric("Subscriptions saved", len(subscription_records))
            col_sub_2.metric("Active subscriptions", len(active_subscriptions))
            col_sub_3.metric("Active monthly total", f"£{active_total:,.2f}")

            st.dataframe(subscription_records, use_container_width=True)

            st.markdown("### Update subscription status")

            subscription_options = [
                f"{index} - {row['subscription_name']} - £{float(row['amount']):,.2f}"
                for index, row in subscription_records.iterrows()
            ]

            selected_subscription_update = st.selectbox(
                "Choose subscription to update",
                subscription_options,
                key="personal_subscription_update_select"
            )

            new_subscription_status = st.selectbox(
                "New subscription status",
                [
                    "Active",
                    "Paused",
                    "Cancelled",
                ],
                key="personal_subscription_status_value"
            )

            if st.button("Update selected subscription status"):
                selected_subscription_index = int(selected_subscription_update.split(" - ")[0])
                subscription_records.loc[selected_subscription_index, "status"] = new_subscription_status
                save_personal_subscription_records(subscription_records)

                st.success("Subscription status updated.")
                st.rerun()

            st.markdown("### Delete subscription")

            selected_subscription_delete = st.selectbox(
                "Choose subscription to delete",
                subscription_options,
                key="personal_subscription_delete_select"
            )

            if st.button("Delete selected subscription"):
                selected_delete_index = int(selected_subscription_delete.split(" - ")[0])
                subscription_records = subscription_records.drop(index=selected_delete_index).reset_index(drop=True)
                save_personal_subscription_records(subscription_records)

                st.success("Subscription deleted.")
                st.rerun()

            st.download_button(
                "Download personal subscriptions CSV",
                data=subscription_records.to_csv(index=False).encode("utf-8"),
                file_name="hustlehq_personal_subscriptions.csv",
                mime="text/csv",
            )

    with personal_tabs[6]:
        st.markdown("### Bills Forecast")
        st.subheader("See what is coming out, when, and from which account")

        if subscription_records.empty:
            st.warning("No subscriptions saved yet. Add subscriptions first, then this forecast will show what is due.")
        else:
            forecast_records = subscription_records.copy()
            forecast_records["amount"] = pd.to_numeric(
                forecast_records["amount"],
                errors="coerce"
            ).fillna(0)

            forecast_records["next_payment_date_dt"] = pd.to_datetime(
                forecast_records["next_payment_date"],
                errors="coerce"
            )

            active_forecast = forecast_records[
                forecast_records["status"] == "Active"
            ].copy()

            if active_forecast.empty:
                st.warning("No active subscriptions found.")
            else:
                today = pd.Timestamp.today().normalize()

                active_forecast["days_until_payment"] = (
                    active_forecast["next_payment_date_dt"] - today
                ).dt.days

                overdue_bills = active_forecast[
                    active_forecast["days_until_payment"] < 0
                ].copy()

                due_7 = active_forecast[
                    (active_forecast["days_until_payment"] >= 0)
                    & (active_forecast["days_until_payment"] <= 7)
                ].copy()

                due_14 = active_forecast[
                    (active_forecast["days_until_payment"] >= 0)
                    & (active_forecast["days_until_payment"] <= 14)
                ].copy()

                due_30 = active_forecast[
                    (active_forecast["days_until_payment"] >= 0)
                    & (active_forecast["days_until_payment"] <= 30)
                ].copy()

                col_bill_1, col_bill_2, col_bill_3, col_bill_4 = st.columns(4)

                col_bill_1.metric("Overdue", len(overdue_bills))
                col_bill_2.metric("Due in 7 days", f"£{due_7['amount'].sum():,.2f}")
                col_bill_3.metric("Due in 14 days", f"£{due_14['amount'].sum():,.2f}")
                col_bill_4.metric("Due in 30 days", f"£{due_30['amount'].sum():,.2f}")

                if not overdue_bills.empty:
                    st.error(f"{len(overdue_bills)} subscription(s) have payment dates in the past. Update or mark them as paid.")
                    st.dataframe(
                        overdue_bills[
                            [
                                "subscription_name",
                                "amount",
                                "paid_from_account",
                                "next_payment_date",
                                "days_until_payment",
                                "category",
                            ]
                        ],
                        use_container_width=True,
                    )

                st.markdown("### Upcoming payments")

                upcoming_payments = active_forecast.sort_values(
                    "next_payment_date_dt",
                    ascending=True
                ).copy()

                st.dataframe(
                    upcoming_payments[
                        [
                            "subscription_name",
                            "amount",
                            "paid_from_account",
                            "next_payment_date",
                            "days_until_payment",
                            "category",
                            "colour",
                        ]
                    ],
                    use_container_width=True,
                )

                st.markdown("### Money needed by account")

                forecast_window = st.selectbox(
                    "Forecast window",
                    [
                        "Next 7 days",
                        "Next 14 days",
                        "Next 30 days",
                        "All active subscriptions",
                    ],
                    key="personal_bills_forecast_window"
                )

                if forecast_window == "Next 7 days":
                    account_forecast = due_7.copy()
                elif forecast_window == "Next 14 days":
                    account_forecast = due_14.copy()
                elif forecast_window == "Next 30 days":
                    account_forecast = due_30.copy()
                else:
                    account_forecast = active_forecast.copy()

                if account_forecast.empty:
                    st.info("No payments found for this forecast window.")
                else:
                    account_needed_summary = (
                        account_forecast
                        .groupby("paid_from_account", as_index=False)["amount"]
                        .sum()
                        .sort_values("amount", ascending=False)
                    )

                    account_needed_summary = account_needed_summary.rename(
                        columns={
                            "paid_from_account": "Account",
                            "amount": "Money needed",
                        }
                    )

                    st.dataframe(account_needed_summary, use_container_width=True)

                st.markdown("### Mark subscription as paid")

                payment_options = [
                    f"{index} - {row['subscription_name']} - £{float(row['amount']):,.2f} - {row['next_payment_date']}"
                    for index, row in subscription_records.iterrows()
                    if row["status"] == "Active"
                ]

                if not payment_options:
                    st.info("No active subscriptions available to mark as paid.")
                else:
                    selected_payment = st.selectbox(
                        "Choose subscription payment",
                        payment_options,
                        key="mark_subscription_paid_select"
                    )

                    selected_payment_index = int(selected_payment.split(" - ")[0])
                    selected_payment_row = subscription_records.loc[selected_payment_index]

                    st.write(
                        f"Selected: {selected_payment_row['subscription_name']} from {selected_payment_row['paid_from_account']}."
                    )

                    date_update_mode = st.radio(
                        "After marking as paid, update next payment date by:",
                        [
                            "Move forward by 1 month",
                            "Choose custom next payment date",
                        ],
                        key="subscription_date_update_mode"
                    )

                    custom_next_date = None

                    if date_update_mode == "Choose custom next payment date":
                        custom_next_date = st.date_input(
                            "Custom next payment date",
                            key="custom_next_subscription_date"
                        )

                    if st.button("Mark selected subscription as paid"):
                        if date_update_mode == "Move forward by 1 month":
                            new_next_payment_date = move_subscription_date_forward(
                                selected_payment_row["next_payment_date"]
                            )
                        else:
                            new_next_payment_date = str(custom_next_date)

                        subscription_records.loc[selected_payment_index, "next_payment_date"] = new_next_payment_date

                        try:
                            subscription_records.loc[selected_payment_index, "payment_day"] = int(
                                pd.to_datetime(new_next_payment_date).day
                            )
                        except Exception:
                            subscription_records.loc[selected_payment_index, "payment_day"] = 0

                        save_personal_subscription_records(subscription_records)

                        st.success(
                            f"Marked as paid. Next payment date updated to {new_next_payment_date}."
                        )
                        st.rerun()

                st.markdown("### Download bills forecast")

                bills_export = active_forecast[
                    [
                        "subscription_name",
                        "amount",
                        "paid_from_account",
                        "next_payment_date",
                        "days_until_payment",
                        "category",
                        "status",
                        "notes",
                    ]
                ].copy()

                st.download_button(
                    "Download bills forecast CSV",
                    data=bills_export.to_csv(index=False).encode("utf-8"),
                    file_name="hustlehq_personal_bills_forecast.csv",
                    mime="text/csv",
                )

        st.markdown("---")

        st.info(
            "Use this page before payday and before the start of each month. "
            "It shows which account needs money in it before subscriptions leave."
        )


    with personal_tabs[7]:
        st.markdown("### Subscription calendar")

        if subscription_records.empty:
            st.warning("Add subscriptions first, then they will appear on the calendar.")
        else:
            today = pd.Timestamp.today()

            cal_col1, cal_col2 = st.columns(2)

            with cal_col1:
                selected_month = st.selectbox(
                    "Month",
                    list(range(1, 13)),
                    index=int(today.month) - 1,
                    format_func=lambda month_number: calendar.month_name[month_number],
                )

            with cal_col2:
                selected_year = st.number_input(
                    "Year",
                    min_value=2020,
                    max_value=2100,
                    value=int(today.year),
                    step=1,
                )

            calendar_html = render_subscription_calendar(
                subscription_records,
                int(selected_year),
                int(selected_month),
            )

            st.markdown(calendar_html, unsafe_allow_html=True)

            st.markdown("### Payments in selected month")

            subscription_records["next_payment_date_dt"] = pd.to_datetime(
                subscription_records["next_payment_date"],
                errors="coerce"
            )

            selected_month_subscriptions = subscription_records[
                (subscription_records["next_payment_date_dt"].dt.year == int(selected_year))
                & (subscription_records["next_payment_date_dt"].dt.month == int(selected_month))
            ].copy()

            if selected_month_subscriptions.empty:
                st.info("No subscriptions found for the selected month.")
            else:
                selected_month_subscriptions["amount"] = pd.to_numeric(
                    selected_month_subscriptions["amount"],
                    errors="coerce"
                ).fillna(0)

                selected_month_total = selected_month_subscriptions[
                    selected_month_subscriptions["status"] == "Active"
                ]["amount"].sum()

                st.metric("Active subscription payments this month", f"£{selected_month_total:,.2f}")

                st.dataframe(
                    selected_month_subscriptions[
                        [
                            "subscription_name",
                            "amount",
                            "paid_from_account",
                            "next_payment_date",
                            "colour",
                            "status",
                            "category",
                        ]
                    ],
                    use_container_width=True,
                )

    with personal_tabs[8]:
        st.markdown("### Monthly Budget")
        st.subheader("Plan income, bills, debt repayments, savings and leftover money")

        budget_records = load_personal_budget_records()

        today = pd.Timestamp.today()

        month_options = list(range(1, 13))

        budget_col1, budget_col2 = st.columns(2)

        with budget_col1:
            selected_budget_month = st.selectbox(
                "Budget month",
                month_options,
                index=int(today.month) - 1,
                format_func=lambda month_number: calendar.month_name[month_number],
                key="personal_budget_month_select",
            )

        with budget_col2:
            selected_budget_year = st.number_input(
                "Budget year",
                min_value=2020,
                max_value=2100,
                value=int(today.year),
                step=1,
                key="personal_budget_year_select",
            )

        subscription_total_for_month = get_subscription_total_for_month(
            subscription_records,
            int(selected_budget_year),
            int(selected_budget_month),
        )

        st.info(
            f"Active subscriptions found for {calendar.month_name[int(selected_budget_month)]} "
            f"{int(selected_budget_year)}: £{subscription_total_for_month:,.2f}"
        )

        st.markdown("### Build monthly budget")

        with st.form("add_personal_monthly_budget_form"):
            income_expected = st.number_input(
                "Expected personal income this month (£)",
                min_value=0.0,
                step=50.0,
                value=0.0,
                help="Use expected take-home pay or money available for the month."
            )

            st.markdown("#### Essentials")

            essential_col1, essential_col2 = st.columns(2)

            with essential_col1:
                rent_housing = st.number_input(
                    "Rent / housing (£)",
                    min_value=0.0,
                    step=25.0,
                    value=0.0
                )

                groceries = st.number_input(
                    "Groceries / food (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

                transport = st.number_input(
                    "Transport (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

            with essential_col2:
                phone_internet = st.number_input(
                    "Phone / internet (£)",
                    min_value=0.0,
                    step=5.0,
                    value=0.0
                )

                personal_spending = st.number_input(
                    "Personal spending (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

                other_fixed_costs = st.number_input(
                    "Other fixed costs (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

            st.markdown("#### Financial priorities")

            priority_col1, priority_col2 = st.columns(2)

            with priority_col1:
                debt_repayment = st.number_input(
                    "Planned debt repayment (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

            with priority_col2:
                savings_contribution = st.number_input(
                    "Planned savings contribution (£)",
                    min_value=0.0,
                    step=10.0,
                    value=0.0
                )

            status = st.selectbox(
                "Budget status",
                [
                    "Draft",
                    "Active",
                    "Completed",
                    "Replaced",
                ]
            )

            notes = st.text_area(
                "Budget notes",
                placeholder="Example: payday timing, expected M&S income, debt payment plan, savings target."
            )

            submitted_budget = st.form_submit_button("Save monthly budget")

        total_planned_outgoing = (
            rent_housing
            + groceries
            + transport
            + phone_internet
            + personal_spending
            + other_fixed_costs
            + debt_repayment
            + savings_contribution
            + subscription_total_for_month
        )

        remaining_money = income_expected - total_planned_outgoing

        st.markdown("### Budget preview")

        preview_col1, preview_col2, preview_col3, preview_col4 = st.columns(4)

        preview_col1.metric("Expected income", f"£{income_expected:,.2f}")
        preview_col2.metric("Planned outgoing", f"£{total_planned_outgoing:,.2f}")
        preview_col3.metric("Subscriptions", f"£{subscription_total_for_month:,.2f}")
        preview_col4.metric("Remaining", f"£{remaining_money:,.2f}")

        if income_expected <= 0:
            st.warning("Add expected income to make the budget useful.")
        elif remaining_money < 0:
            st.error("This budget is negative. Planned costs are higher than expected income.")
        elif remaining_money < 50:
            st.warning("This budget leaves a very small buffer.")
        else:
            st.success("This budget leaves a positive buffer.")

        if submitted_budget:
            if income_expected <= 0:
                st.error("Add expected income before saving this budget.")
            else:
                new_budget = pd.DataFrame(
                    [
                        {
                            "date_added": str(pd.Timestamp.today().date()),
                            "budget_month": calendar.month_name[int(selected_budget_month)],
                            "budget_year": int(selected_budget_year),
                            "income_expected": income_expected,
                            "rent_housing": rent_housing,
                            "groceries": groceries,
                            "transport": transport,
                            "phone_internet": phone_internet,
                            "personal_spending": personal_spending,
                            "debt_repayment": debt_repayment,
                            "savings_contribution": savings_contribution,
                            "other_fixed_costs": other_fixed_costs,
                            "subscription_total": subscription_total_for_month,
                            "total_planned_outgoing": total_planned_outgoing,
                            "remaining_money": remaining_money,
                            "status": status,
                            "notes": notes.strip(),
                        }
                    ]
                )

                budget_records = pd.concat([budget_records, new_budget], ignore_index=True)
                save_personal_budget_records(budget_records)

                st.success("Monthly budget saved.")
                st.rerun()

        st.markdown("---")

        st.markdown("### Budget history")

        if budget_records.empty:
            st.warning("No monthly budgets saved yet.")
        else:
            budget_records["income_expected"] = pd.to_numeric(
                budget_records["income_expected"],
                errors="coerce"
            ).fillna(0)

            budget_records["total_planned_outgoing"] = pd.to_numeric(
                budget_records["total_planned_outgoing"],
                errors="coerce"
            ).fillna(0)

            budget_records["remaining_money"] = pd.to_numeric(
                budget_records["remaining_money"],
                errors="coerce"
            ).fillna(0)

            active_budgets = budget_records[
                budget_records["status"].isin(["Draft", "Active"])
            ].copy()

            hist_col1, hist_col2, hist_col3 = st.columns(3)

            hist_col1.metric("Budgets saved", len(budget_records))
            hist_col2.metric("Active/draft budgets", len(active_budgets))
            hist_col3.metric(
                "Latest remaining",
                f"£{budget_records.iloc[-1]['remaining_money']:,.2f}"
            )

            st.dataframe(budget_records, use_container_width=True)

            st.markdown("### Delete budget record")

            budget_delete_options = [
                f"{index} - {row['budget_month']} {row['budget_year']} - {row['status']} - Remaining £{float(row['remaining_money']):,.2f}"
                for index, row in budget_records.iterrows()
            ]

            selected_budget_delete = st.selectbox(
                "Choose budget to delete",
                budget_delete_options,
                key="personal_budget_delete_select"
            )

            if st.button("Delete selected budget"):
                selected_delete_index = int(selected_budget_delete.split(" - ")[0])
                budget_records = budget_records.drop(index=selected_delete_index).reset_index(drop=True)
                save_personal_budget_records(budget_records)

                st.success("Budget record deleted.")
                st.rerun()

            st.download_button(
                "Download monthly budgets CSV",
                data=budget_records.to_csv(index=False).encode("utf-8"),
                file_name="hustlehq_personal_monthly_budgets.csv",
                mime="text/csv",
            )

        st.markdown("---")

        st.info(
            "Use this tab before the month starts, then update it after payday or when subscriptions/debt repayments change."
        )




    with personal_tabs[9]:
        st.markdown("### Transactions")
        st.subheader("Track personal income, spending and transfers manually")

        transaction_records = load_personal_transaction_records()

        account_options = []

        if not account_records.empty:
            account_options = [
                f"{row['provider']} - {row['account_name']}"
                for _, row in account_records.iterrows()
            ]

        if not account_options:
            account_options = [
                "Santander",
                "NatWest",
                "Zopa",
                "American Express",
                "Trading 212",
                "PayPal",
                "AJ Bell Dodl",
                "Nationwide",
                "Lloyds",
                "Revolut",
                "Monzo",
                "Halifax",
                "Other",
            ]

        st.markdown("### Add transaction")

        with st.form("add_personal_transaction_form"):
            trans_col1, trans_col2 = st.columns(2)

            with trans_col1:
                transaction_date = st.date_input("Transaction date")

                transaction_type = st.selectbox(
                    "Transaction type",
                    [
                        "Expense",
                        "Income",
                        "Transfer",
                    ]
                )

                account = st.selectbox(
                    "Account",
                    account_options
                )

                category = st.selectbox(
                    "Category",
                    [
                        "Income",
                        "Food/Groceries",
                        "Transport",
                        "Subscriptions",
                        "Shopping",
                        "Debt Repayment",
                        "Savings Transfer",
                        "Entertainment",
                        "Health/Fitness",
                        "Education",
                        "Bills",
                        "Family/Friends",
                        "Beauty",
                        "Clothing",
                        "Investing",
                        "Other",
                    ]
                )

            with trans_col2:
                description = st.text_input(
                    "Description",
                    placeholder="Example: Tesco, Amex payment, M&S wages, Spotify"
                )

                amount = st.number_input(
                    "Amount (£)",
                    min_value=0.0,
                    step=1.0,
                    value=0.0
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Cleared",
                        "Pending",
                        "Planned",
                    ]
                )

            notes = st.text_area("Notes")

            submitted_transaction = st.form_submit_button("Save transaction")

        if submitted_transaction:
            if amount <= 0:
                st.error("Add an amount above £0.")
            elif not description.strip():
                st.error("Add a description before saving.")
            else:
                new_transaction = pd.DataFrame(
                    [
                        {
                            "date_added": str(pd.Timestamp.today().date()),
                            "transaction_date": str(transaction_date),
                            "transaction_type": transaction_type,
                            "account": account,
                            "category": category,
                            "description": description.strip(),
                            "amount": amount,
                            "status": status,
                            "notes": notes.strip(),
                        }
                    ]
                )

                transaction_records = pd.concat(
                    [transaction_records, new_transaction],
                    ignore_index=True
                )

                save_personal_transaction_records(transaction_records)

                st.success("Transaction saved.")
                st.rerun()

        st.markdown("---")

        st.markdown("### Transaction dashboard")

        if transaction_records.empty:
            st.warning("No personal transactions saved yet.")
        else:
            transaction_records["amount"] = pd.to_numeric(
                transaction_records["amount"],
                errors="coerce"
            ).fillna(0)

            transaction_records["transaction_date_dt"] = pd.to_datetime(
                transaction_records["transaction_date"],
                errors="coerce"
            )

            today = pd.Timestamp.today()

            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:
                selected_transaction_month = st.selectbox(
                    "Month",
                    list(range(1, 13)),
                    index=int(today.month) - 1,
                    format_func=lambda month_number: calendar.month_name[month_number],
                    key="personal_transaction_month_select",
                )

            with filter_col2:
                selected_transaction_year = st.number_input(
                    "Year",
                    min_value=2020,
                    max_value=2100,
                    value=int(today.year),
                    step=1,
                    key="personal_transaction_year_select",
                )

            month_transactions = transaction_records[
                (transaction_records["transaction_date_dt"].dt.year == int(selected_transaction_year))
                & (transaction_records["transaction_date_dt"].dt.month == int(selected_transaction_month))
            ].copy()

            if month_transactions.empty:
                st.info("No transactions found for the selected month.")
            else:
                month_income = month_transactions[
                    month_transactions["transaction_type"] == "Income"
                ]["amount"].sum()

                month_expenses = month_transactions[
                    month_transactions["transaction_type"] == "Expense"
                ]["amount"].sum()

                month_transfers = month_transactions[
                    month_transactions["transaction_type"] == "Transfer"
                ]["amount"].sum()

                month_net = month_income - month_expenses

                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                metric_col1.metric("Income", f"£{month_income:,.2f}")
                metric_col2.metric("Expenses", f"£{month_expenses:,.2f}")
                metric_col3.metric("Transfers", f"£{month_transfers:,.2f}")
                metric_col4.metric("Net", f"£{month_net:,.2f}")

                if month_net < 0:
                    st.error("You spent more than you logged as income for this month.")
                elif month_expenses > 0:
                    st.success("This month currently has a positive personal cash flow.")

                st.markdown("### Transactions for selected month")

                st.dataframe(
                    month_transactions[
                        [
                            "transaction_date",
                            "transaction_type",
                            "account",
                            "category",
                            "description",
                            "amount",
                            "status",
                            "notes",
                        ]
                    ],
                    use_container_width=True,
                )

                st.markdown("### Spending by category")

                spending_by_category = (
                    month_transactions[
                        month_transactions["transaction_type"] == "Expense"
                    ]
                    .groupby("category", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )

                if spending_by_category.empty:
                    st.info("No expense transactions found for this month.")
                else:
                    st.dataframe(spending_by_category, use_container_width=True)

                st.markdown("### Spending by account")

                spending_by_account = (
                    month_transactions[
                        month_transactions["transaction_type"] == "Expense"
                    ]
                    .groupby("account", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )

                if spending_by_account.empty:
                    st.info("No account spending found for this month.")
                else:
                    st.dataframe(spending_by_account, use_container_width=True)

                st.markdown("### Income by account")

                income_by_account = (
                    month_transactions[
                        month_transactions["transaction_type"] == "Income"
                    ]
                    .groupby("account", as_index=False)["amount"]
                    .sum()
                    .sort_values("amount", ascending=False)
                )

                if income_by_account.empty:
                    st.info("No income transactions found for this month.")
                else:
                    st.dataframe(income_by_account, use_container_width=True)

            st.markdown("---")

            st.markdown("### All transactions")

            st.dataframe(
                transaction_records[
                    [
                        "transaction_date",
                        "transaction_type",
                        "account",
                        "category",
                        "description",
                        "amount",
                        "status",
                        "notes",
                    ]
                ],
                use_container_width=True,
            )

            st.markdown("### Delete transaction")

            transaction_delete_options = [
                f"{index} - {row['transaction_date']} - {row['transaction_type']} - {row['description']} - £{float(row['amount']):,.2f}"
                for index, row in transaction_records.iterrows()
            ]

            selected_transaction_delete = st.selectbox(
                "Choose transaction to delete",
                transaction_delete_options,
                key="personal_transaction_delete_select"
            )

            if st.button("Delete selected transaction"):
                selected_delete_index = int(selected_transaction_delete.split(" - ")[0])
                transaction_records = transaction_records.drop(index=selected_delete_index).reset_index(drop=True)
                save_personal_transaction_records(transaction_records)

                st.success("Transaction deleted.")
                st.rerun()

            st.download_button(
                "Download personal transactions CSV",
                data=transaction_records.drop(columns=["transaction_date_dt"], errors="ignore").to_csv(index=False).encode("utf-8"),
                file_name="hustlehq_personal_transactions.csv",
                mime="text/csv",
            )

        st.markdown("---")

        st.info(
            "Use this tab for manual tracking until bank imports or Open Banking connections are added. "
            "For now, it does not automatically update your account balances."
        )




    with personal_tabs[10]:
        st.markdown("### Import Transactions CSV")
        st.subheader("Import personal spending, income and transfer records from CSV files")

        st.warning(
            "Use this for bank exports, PayPal exports, Monzo/Revolut CSVs, manual spreadsheets or copied transaction data. "
            "Always preview before saving."
        )

        uploaded_transaction_file = st.file_uploader(
            "Upload personal transaction CSV",
            type=["csv"],
            key="personal_transaction_csv_upload"
        )

        if uploaded_transaction_file is None:
            st.info("Upload a CSV file to begin.")
        else:
            try:
                imported_transactions_df = pd.read_csv(uploaded_transaction_file)

                if imported_transactions_df.empty:
                    st.error("The uploaded CSV is empty.")
                else:
                    st.markdown("### Uploaded file preview")
                    st.dataframe(imported_transactions_df.head(30), use_container_width=True)

                    csv_columns = imported_transactions_df.columns.tolist()
                    none_option = "None"

                    def guess_transaction_column(possible_names):
                        for possible_name in possible_names:
                            for column in csv_columns:
                                if possible_name.lower() in column.lower():
                                    return column
                        return csv_columns[0] if csv_columns else none_option

                    st.markdown("### Map your columns")

                    date_guess = guess_transaction_column(["date", "transaction date", "posted", "paid"])
                    description_guess = guess_transaction_column(["description", "merchant", "name", "details", "reference"])
                    amount_guess = guess_transaction_column(["amount", "value", "money", "paid", "debit", "credit"])
                    category_guess = guess_transaction_column(["category", "type"])
                    account_guess = guess_transaction_column(["account", "bank", "provider"])

                    map_col1, map_col2 = st.columns(2)

                    with map_col1:
                        date_column = st.selectbox(
                            "Date column",
                            csv_columns,
                            index=csv_columns.index(date_guess) if date_guess in csv_columns else 0
                        )

                        description_column = st.selectbox(
                            "Description column",
                            csv_columns,
                            index=csv_columns.index(description_guess) if description_guess in csv_columns else 0
                        )

                        amount_column = st.selectbox(
                            "Amount column",
                            csv_columns,
                            index=csv_columns.index(amount_guess) if amount_guess in csv_columns else 0
                        )

                    with map_col2:
                        category_column = st.selectbox(
                            "Category column",
                            [none_option] + csv_columns,
                            index=([none_option] + csv_columns).index(category_guess) if category_guess in csv_columns else 0
                        )

                        account_column = st.selectbox(
                            "Account column",
                            [none_option] + csv_columns,
                            index=([none_option] + csv_columns).index(account_guess) if account_guess in csv_columns else 0
                        )

                        status_column = st.selectbox(
                            "Status column",
                            [none_option] + csv_columns,
                            index=0
                        )

                    st.markdown("### Import settings")

                    account_options = []

                    account_records_for_import = load_personal_account_records()

                    if not account_records_for_import.empty:
                        account_options = [
                            f"{row['provider']} - {row['account_name']}"
                            for _, row in account_records_for_import.iterrows()
                        ]

                    if not account_options:
                        account_options = [
                            "Santander",
                            "NatWest",
                            "Zopa",
                            "American Express",
                            "Trading 212",
                            "PayPal",
                            "AJ Bell Dodl",
                            "Nationwide",
                            "Lloyds",
                            "Revolut",
                            "Monzo",
                            "Halifax",
                            "Other",
                        ]

                    default_account = st.selectbox(
                        "Default account if no account column is used",
                        account_options
                    )

                    default_category = st.selectbox(
                        "Default category if no category column is used",
                        [
                            "Food/Groceries",
                            "Transport",
                            "Subscriptions",
                            "Shopping",
                            "Debt Repayment",
                            "Savings Transfer",
                            "Entertainment",
                            "Health/Fitness",
                            "Education",
                            "Bills",
                            "Family/Friends",
                            "Beauty",
                            "Clothing",
                            "Investing",
                            "Income",
                            "Other",
                        ]
                    )

                    amount_style = st.radio(
                        "How should HustleHQ read the amount column?",
                        [
                            "Negative = expense, positive = income",
                            "All rows are expenses",
                            "All rows are income",
                        ],
                        key="personal_transaction_amount_style"
                    )

                    default_status = st.selectbox(
                        "Default transaction status",
                        [
                            "Cleared",
                            "Pending",
                            "Planned",
                        ]
                    )

                    add_import_tag = st.checkbox(
                        "Add CSV import tag to notes",
                        value=True
                    )

                    if st.button("Preview imported transactions"):
                        preview_df = imported_transactions_df.copy()

                        preview_df["_transaction_date"] = pd.to_datetime(
                            preview_df[date_column],
                            errors="coerce"
                        )

                        preview_df["_raw_amount"] = pd.to_numeric(
                            preview_df[amount_column],
                            errors="coerce"
                        ).fillna(0)

                        if amount_style == "Negative = expense, positive = income":
                            preview_df["_transaction_type"] = preview_df["_raw_amount"].apply(
                                lambda value: "Expense" if value < 0 else "Income"
                            )
                            preview_df["_amount"] = preview_df["_raw_amount"].abs()
                        elif amount_style == "All rows are expenses":
                            preview_df["_transaction_type"] = "Expense"
                            preview_df["_amount"] = preview_df["_raw_amount"].abs()
                        else:
                            preview_df["_transaction_type"] = "Income"
                            preview_df["_amount"] = preview_df["_raw_amount"].abs()

                        preview_df["_description"] = preview_df[description_column].astype(str)

                        if category_column != none_option:
                            preview_df["_category"] = preview_df[category_column].astype(str)
                        else:
                            preview_df["_category"] = default_category

                        if account_column != none_option:
                            preview_df["_account"] = preview_df[account_column].astype(str)
                        else:
                            preview_df["_account"] = default_account

                        if status_column != none_option:
                            preview_df["_status"] = preview_df[status_column].astype(str)
                        else:
                            preview_df["_status"] = default_status

                        preview_df["_notes"] = "Imported from personal transaction CSV"

                        if add_import_tag:
                            preview_df["_notes"] = preview_df["_notes"] + " | CSV import"

                        converted_transactions = pd.DataFrame(
                            {
                                "date_added": str(pd.Timestamp.today().date()),
                                "transaction_date": preview_df["_transaction_date"].dt.date.astype(str),
                                "transaction_type": preview_df["_transaction_type"],
                                "account": preview_df["_account"],
                                "category": preview_df["_category"],
                                "description": preview_df["_description"],
                                "amount": preview_df["_amount"],
                                "status": preview_df["_status"],
                                "notes": preview_df["_notes"],
                            }
                        )

                        converted_transactions = converted_transactions[
                            converted_transactions["amount"] > 0
                        ].copy()

                        converted_transactions = converted_transactions[
                            converted_transactions["transaction_date"].notna()
                        ].copy()

                        st.session_state["personal_transaction_import_preview"] = converted_transactions

                    if "personal_transaction_import_preview" in st.session_state:
                        converted_transactions = st.session_state["personal_transaction_import_preview"]

                        st.markdown("### Converted transaction preview")

                        if converted_transactions.empty:
                            st.error("No valid transactions found after conversion. Check your date and amount columns.")
                        else:
                            st.dataframe(converted_transactions, use_container_width=True)

                            import_income_total = converted_transactions[
                                converted_transactions["transaction_type"] == "Income"
                            ]["amount"].sum()

                            import_expense_total = converted_transactions[
                                converted_transactions["transaction_type"] == "Expense"
                            ]["amount"].sum()

                            import_transfer_total = converted_transactions[
                                converted_transactions["transaction_type"] == "Transfer"
                            ]["amount"].sum()

                            import_col1, import_col2, import_col3, import_col4 = st.columns(4)

                            import_col1.metric("Rows ready", len(converted_transactions))
                            import_col2.metric("Income", f"£{import_income_total:,.2f}")
                            import_col3.metric("Expenses", f"£{import_expense_total:,.2f}")
                            import_col4.metric("Transfers", f"£{import_transfer_total:,.2f}")

                            existing_transactions = load_personal_transaction_records()

                            duplicate_count = 0

                            if not existing_transactions.empty:
                                existing_keys = set(
                                    (
                                        existing_transactions["transaction_date"].astype(str)
                                        + "|"
                                        + existing_transactions["description"].astype(str)
                                        + "|"
                                        + existing_transactions["amount"].astype(str)
                                    ).tolist()
                                )

                                new_keys = (
                                    converted_transactions["transaction_date"].astype(str)
                                    + "|"
                                    + converted_transactions["description"].astype(str)
                                    + "|"
                                    + converted_transactions["amount"].astype(str)
                                ).tolist()

                                duplicate_count = sum(1 for key in new_keys if key in existing_keys)

                            if duplicate_count > 0:
                                st.warning(f"{duplicate_count} possible duplicate transaction(s) found based on date, description and amount.")

                            confirm_import = st.checkbox(
                                "I have checked the preview and want to save these personal transactions.",
                                key="confirm_personal_transaction_import"
                            )

                            if st.button("Save imported personal transactions"):
                                if not confirm_import:
                                    st.error("Tick the confirmation box before saving.")
                                else:
                                    updated_transactions = pd.concat(
                                        [existing_transactions, converted_transactions],
                                        ignore_index=True
                                    )

                                    save_personal_transaction_records(updated_transactions)

                                    st.success("Personal transactions imported successfully.")
                                    st.info("Go to Transactions or Dashboard to review the imported records.")

                                    del st.session_state["personal_transaction_import_preview"]

            except Exception as error:
                st.error("Personal transaction CSV import failed.")
                st.exception(error)

        st.markdown("---")

        st.markdown("### CSV import tips")

        st.write("- Bank CSVs often use negative numbers for spending and positive numbers for income.")
        st.write("- Use the amount-style option carefully before previewing.")
        st.write("- For PayPal, Revolut or Monzo exports, map their account/category columns where available.")
        st.write("- For credit card exports, use the card account as the default account.")
        st.write("- Imported transactions do not automatically change your account balances yet. That comes in a later Personal Finance part.")




    st.markdown("---")

    st.caption(
        "Personal Finance is separate from HustleHQ side-hustle records. "
        "Use this section for personal account balances, debt, savings and subscriptions."
    )



if page == "Mobile Quick Guide":
    st.title("Mobile Quick Guide")
    st.subheader("Use HustleHQ faster from your phone")

    st.markdown(
        """
        <div class="hustlehq-mobile-note">
        HustleHQ works best when you use quick entry pages on mobile and bigger review pages on laptop.
        Use your phone for adding income, expenses, receipts and quick checks. Use your laptop for exports,
        PDF reports, backups and tax-year reviews.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Best pages to use on your phone")

    st.markdown(
        """
        <div class="hustlehq-action-card">
            <h4>Add Income</h4>
            <p>Use this straight after a payment, Vinted sale, brand payment, transcription payout or client payment.</p>
        </div>
        <div class="hustlehq-action-card">
            <h4>Add Expense</h4>
            <p>Use this immediately after buying postage, packaging, software, stock, travel or supplies.</p>
        </div>
        <div class="hustlehq-action-card">
            <h4>Project Tracker</h4>
            <p>Use this to quickly log a new idea, paid task, app project, client job or side-hustle opportunity.</p>
        </div>
        <div class="hustlehq-action-card">
            <h4>Client / Contact Tracker</h4>
            <p>Use this after speaking to a brand, client, assistant, buyer, supplier or collaborator.</p>
        </div>
        <div class="hustlehq-action-card">
            <h4>Payment Chase</h4>
            <p>Use this when checking unpaid invoices or preparing a reminder message.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Best pages to use on laptop")

    laptop_pages = pd.DataFrame(
        [
            {"Page": "HMRC Export", "Best use": "Download structured tax-year records."},
            {"Page": "PDF Report", "Best use": "Create polished summaries."},
            {"Page": "Data Backup", "Best use": "Download full backups."},
            {"Page": "Restore Backup", "Best use": "Restore records carefully."},
            {"Page": "Tax-Year Summary", "Best use": "Review profit, expenses and evidence quality."},
            {"Page": "Import Income CSV", "Best use": "Upload platform exports or bank CSVs."},
            {"Page": "Import Expense CSV", "Best use": "Upload bank or receipt CSVs."},
        ]
    )

    st.dataframe(laptop_pages, use_container_width=True)

    st.markdown("### Mobile workflow")

    st.write("1. Add money in as soon as it arrives.")
    st.write("2. Add costs as soon as you pay them.")
    st.write("3. Upload/import CSVs weekly instead of typing everything manually.")
    st.write("4. Check the dashboard every few days.")
    st.write("5. Download a backup at least once a week.")
    st.write("6. Do serious tax/export checks on laptop.")

    st.markdown("### Phone shortcut tip")

    st.info(
        "Open the deployed app on your iPhone, tap Share, then Add to Home Screen. "
        "This makes HustleHQ feel more like a normal app."
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



elif page == "Client / Contact Tracker":
    st.title("Client / Contact Tracker")
    st.subheader("Track brands, clients, platforms and side-hustle contacts")

    contact_records = load_contact_records()

    st.markdown("### Add new contact")

    with st.form("add_contact_form"):
        col1, col2 = st.columns(2)

        with col1:
            contact_name = st.text_input(
                "Contact name",
                placeholder="Example: Sarah, Hiring Team, Brand Manager"
            )

            company_platform = st.text_input(
                "Company / platform",
                placeholder="Example: Vinted, Test Brand, Local Business"
            )

            email_or_contact = st.text_input(
                "Email / contact details",
                placeholder="Example: email, Instagram handle, website, phone"
            )

            contact_type = st.selectbox(
                "Contact type",
                [
                    "UGC Brand",
                    "Website Client",
                    "App Sales Lead",
                    "Transcription Platform",
                    "Digital Product Customer",
                    "Repeat Buyer",
                    "Supplier",
                    "Collaborator",
                    "Other",
                ]
            )

        with col2:
            status = st.selectbox(
                "Status",
                [
                    "Lead",
                    "Contacted",
                    "Waiting for reply",
                    "In discussion",
                    "Won / Active",
                    "Completed",
                    "Lost / No reply",
                    "Paused",
                ]
            )

            expected_value = st.number_input(
                "Expected value (£)",
                min_value=0.0,
                step=5.0,
                value=0.0
            )

            last_contacted = st.date_input("Last contacted date")
            follow_up_date = st.date_input("Follow-up date")

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Save contact")

    if submitted:
        if not contact_name.strip() and not company_platform.strip():
            st.error("Add at least a contact name or company/platform before saving.")
        else:
            new_contact = pd.DataFrame(
                [
                    {
                        "date_added": str(pd.Timestamp.today().date()),
                        "contact_name": contact_name.strip(),
                        "company_platform": company_platform.strip(),
                        "email_or_contact": email_or_contact.strip(),
                        "contact_type": contact_type,
                        "status": status,
                        "expected_value": expected_value,
                        "last_contacted": str(last_contacted),
                        "follow_up_date": str(follow_up_date),
                        "notes": notes.strip(),
                    }
                ]
            )

            contact_records = pd.concat([contact_records, new_contact], ignore_index=True)
            save_contact_records(contact_records)

            st.success("Contact saved successfully.")
            st.rerun()

    st.markdown("---")

    st.markdown("### Contact overview")

    if contact_records.empty:
        st.warning("No contacts saved yet.")
    else:
        contact_records["expected_value"] = pd.to_numeric(
            contact_records["expected_value"],
            errors="coerce"
        ).fillna(0)

        active_statuses = ["Lead", "Contacted", "Waiting for reply", "In discussion", "Won / Active"]
        active_contacts = contact_records[contact_records["status"].isin(active_statuses)].copy()

        total_expected_value = active_contacts["expected_value"].sum() if not active_contacts.empty else 0

        follow_up_dates = pd.to_datetime(active_contacts["follow_up_date"], errors="coerce") if not active_contacts.empty else pd.Series(dtype="datetime64[ns]")
        today = pd.Timestamp.today().normalize()

        follow_ups_due = int(((follow_up_dates >= today) & (follow_up_dates <= today + pd.Timedelta(days=7))).sum()) if not active_contacts.empty else 0
        overdue_follow_ups = int((follow_up_dates < today).sum()) if not active_contacts.empty else 0

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Contacts saved", len(contact_records))
        col2.metric("Active contacts", len(active_contacts))
        col3.metric("Active expected value", f"£{total_expected_value:,.2f}")
        col4.metric("Follow-ups due", follow_ups_due)

        alert1, alert2 = st.columns(2)

        if follow_ups_due > 0:
            alert1.warning(f"{follow_ups_due} follow-up(s) due within 7 days.")
        else:
            alert1.success("No follow-ups due within 7 days.")

        if overdue_follow_ups > 0:
            alert2.error(f"{overdue_follow_ups} follow-up(s) appear overdue.")
        else:
            alert2.success("No overdue follow-ups.")

        st.markdown("### Filter contacts")

        status_filter = st.selectbox(
            "Filter by status",
            ["All"] + sorted(contact_records["status"].dropna().unique().tolist())
        )

        type_filter = st.selectbox(
            "Filter by contact type",
            ["All"] + sorted(contact_records["contact_type"].dropna().unique().tolist())
        )

        filtered_contacts = contact_records.copy()

        if status_filter != "All":
            filtered_contacts = filtered_contacts[filtered_contacts["status"] == status_filter]

        if type_filter != "All":
            filtered_contacts = filtered_contacts[filtered_contacts["contact_type"] == type_filter]

        display_contacts = filtered_contacts.copy()
        display_contacts["expected_value"] = pd.to_numeric(
            display_contacts["expected_value"],
            errors="coerce"
        ).fillna(0)

        st.dataframe(display_contacts, use_container_width=True)

        st.download_button(
            "Download contacts CSV",
            data=contact_records.to_csv(index=False).encode("utf-8"),
            file_name="hustlehq_contacts.csv",
            mime="text/csv",
        )

        st.markdown("### Update contact status")

        update_options = [
            f"{index} - {row['contact_name']} - {row['company_platform']} ({row['status']})"
            for index, row in contact_records.iterrows()
        ]

        selected_update = st.selectbox(
            "Choose contact to update",
            update_options,
            key="contact_status_update_select"
        )

        new_status = st.selectbox(
            "New status",
            [
                "Lead",
                "Contacted",
                "Waiting for reply",
                "In discussion",
                "Won / Active",
                "Completed",
                "Lost / No reply",
                "Paused",
            ],
            key="contact_status_update_value"
        )

        if st.button("Update selected contact status"):
            selected_index = int(selected_update.split(" - ")[0])
            contact_records.loc[selected_index, "status"] = new_status
            contact_records.loc[selected_index, "last_contacted"] = str(pd.Timestamp.today().date())
            save_contact_records(contact_records)

            st.success("Contact status updated.")
            st.rerun()

        st.markdown("### Delete contact")

        delete_options = [
            f"{index} - {row['contact_name']} - {row['company_platform']}"
            for index, row in contact_records.iterrows()
        ]

        selected_delete = st.selectbox(
            "Choose contact to delete",
            delete_options,
            key="delete_contact_select"
        )

        if st.button("Delete selected contact"):
            selected_index = int(selected_delete.split(" - ")[0])
            contact_records = contact_records.drop(index=selected_index).reset_index(drop=True)
            save_contact_records(contact_records)

            st.success("Contact deleted.")
            st.rerun()

    st.markdown("---")

    st.markdown("### How to use this page")

    st.write("- Add contacts before they become paid projects or invoices.")
    st.write("- Use follow-up dates so leads do not go cold.")
    st.write("- Use expected value to estimate your pipeline.")
    st.write("- When a contact becomes actual work, add it to Project Tracker.")
    st.write("- When work is ready to bill, create an invoice from Invoice Draft.")



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
