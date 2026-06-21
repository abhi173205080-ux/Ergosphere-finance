import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import base64
import sqlite3
import os
from PIL import Image

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Ergosphere | Financial Oversight", layout="wide")

# ---------- DATABASE SETUP ----------
DB_NAME = "Ergosphere_finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  category TEXT,
                  amount REAL,
                  fixed BOOLEAN,
                  receipt TEXT,
                  month_year TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS incomes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  source TEXT,
                  amount REAL,
                  month_year TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budgets
                 (category TEXT PRIMARY KEY,
                  limit_amount REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS recurring
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  amount REAL,
                  frequency TEXT,
                  next_due TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  description TEXT,
                  amount REAL,
                  due_date TEXT,
                  paid BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS assets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  value REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS liabilities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  amount REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS investments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  amount REAL,
                  type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  target_amount REAL,
                  saved_so_far REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (category TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# ---------- HELPER FUNCTIONS ----------
def get_current_month():
    return datetime.now().strftime("%Y-%m")

def load_expenses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT date, category, amount, fixed, receipt FROM expenses WHERE month_year = ? ORDER BY id", 
                           conn, params=(get_current_month(),))
    conn.close()
    return df

def save_expense(date_val, category, amount, fixed, receipt):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (date, category, amount, fixed, receipt, month_year) VALUES (?,?,?,?,?,?)",
              (date_val, category, amount, fixed, receipt, get_current_month()))
    conn.commit()
    # Also save category
    c.execute("INSERT OR IGNORE INTO categories (category) VALUES (?)", (category,))
    conn.commit()
    conn.close()

def delete_expense(row_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = (SELECT id FROM expenses WHERE month_year = ? ORDER BY id LIMIT 1 OFFSET ?)",
              (get_current_month(), row_id))
    conn.commit()
    conn.close()

def load_categories():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT category FROM categories ORDER BY category", conn)
    conn.close()
    return df["category"].tolist() if not df.empty else []

def save_category(cat):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO categories (category) VALUES (?)", (cat,))
    conn.commit()
    conn.close()

def load_incomes():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT date, source, amount FROM incomes WHERE month_year = ?", conn, params=(get_current_month(),))
    conn.close()
    return df

def save_income(date_val, source, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO incomes (date, source, amount, month_year) VALUES (?,?,?,?)",
              (date_val, source, amount, get_current_month()))
    conn.commit()
    conn.close()

def load_budgets():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT category, limit_amount FROM budgets", conn)
    conn.close()
    return df

def save_budget(category, limit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO budgets (category, limit_amount) VALUES (?,?)", (category, limit))
    conn.commit()
    conn.close()

def load_recurring():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT category, amount, frequency, next_due FROM recurring", conn)
    conn.close()
    return df

def save_recurring(category, amount, frequency, next_due):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO recurring (category, amount, frequency, next_due) VALUES (?,?,?,?)",
              (category, amount, frequency, next_due))
    conn.commit()
    conn.close()

def load_bills():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT description, amount, due_date, paid FROM bills", conn)
    conn.close()
    return df

def save_bill(description, amount, due_date, paid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO bills (description, amount, due_date, paid) VALUES (?,?,?,?)",
              (description, amount, due_date, paid))
    conn.commit()
    conn.close()

def update_bill_paid(description, paid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE bills SET paid = ? WHERE description = ?", (paid, description))
    conn.commit()
    conn.close()

def load_assets():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT name, value FROM assets", conn)
    conn.close()
    return df

def save_asset(name, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO assets (name, value) VALUES (?,?)", (name, value))
    conn.commit()
    conn.close()

def load_liabilities():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT name, amount FROM liabilities", conn)
    conn.close()
    return df

def save_liability(name, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO liabilities (name, amount) VALUES (?,?)", (name, amount))
    conn.commit()
    conn.close()

def load_investments():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT name, amount, type FROM investments", conn)
    conn.close()
    return df

def save_investment(name, amount, type_val):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO investments (name, amount, type) VALUES (?,?,?)", (name, amount, type_val))
    conn.commit()
    conn.close()

def load_goals():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT name, target_amount, saved_so_far FROM goals", conn)
    conn.close()
    return df

def save_goal(name, target, saved):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO goals (name, target_amount, saved_so_far) VALUES (?,?,?)", (name, target, saved))
    conn.commit()
    conn.close()

def update_goal_saved(name, new_saved):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE goals SET saved_so_far = ? WHERE name = ?", (new_saved, name))
    conn.commit()
    conn.close()

def delete_goal(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE name = ?", (name,))
    conn.commit()
    conn.close()

# ---------- SEED SAMPLE DATA (ON FIRST RUN) ----------
def seed_sample_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if expenses table is empty
    c.execute("SELECT COUNT(*) FROM expenses")
    count = c.fetchone()[0]
    if count == 0:
        sample_data = [
            ("2026-06-20", "Milk", 100, 0, None),
            ("2026-06-21", "Home Loan EMI", 32000, 1, None),
            ("2026-06-21", "School Fees", 12500, 1, None),
            ("2026-06-21", "Car Loan EMI", 14500, 1, None),
            ("2026-06-22", "Groceries", 8500, 0, None),
            ("2026-06-22", "Personal Loan EMI", 6200, 1, None),
            ("2026-06-22", "Electricity Bill", 4500, 1, None),
            ("2026-06-23", "Maid & Cook Salary", 700, 1, None),
            ("2026-06-23", "Petrol / Fuel", 5000, 0, None),
            ("2026-06-24", "Health Insurance", 2500, 1, None),
            ("2026-06-24", "Broadband & OTT", 1200, 1, None),
            ("2026-06-25", "Society Maintenance", 3000, 1, None),
        ]
        month = get_current_month()
        for date_val, category, amount, fixed, receipt in sample_data:
            c.execute("INSERT INTO expenses (date, category, amount, fixed, receipt, month_year) VALUES (?,?,?,?,?,?)",
                      (date_val, category, amount, fixed, receipt, month))
            # Also save each category
            c.execute("INSERT OR IGNORE INTO categories (category) VALUES (?)", (category,))
        conn.commit()
    conn.close()

# ---------- INITIALIZE DATABASE AND SEED ----------
init_db()
seed_sample_data()

# ---------- TOP COLORED WELCOME BOX WITH LOGO ----------
logo_path = "Copilot_20260620_220455.png"  # change to your actual filename
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        logo_b64 = base64.b64encode(img_file.read()).decode()
    img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width:80px; height:80px; object-fit:contain; border-radius:50%; border:3px solid white; box-shadow:0 4px 10px rgba(0,0,0,0.2);">'
else:
    img_tag = '<div style="background:white; border-radius:50%; width:80px; height:80px; display:flex; align-items:center; justify-content:center; font-size:40px; font-weight:bold; color:#667eea; box-shadow:0 4px 10px rgba(0,0,0,0.2);">⚡</div>'

st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 20px;
    ">
        {img_tag}
        <div>
            <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: 1px;">
                Welcome to Ergosphere
            </h1>
            <p style="color: rgba(255,255,255,0.95); margin: 5px 0 0 0; font-size: 1.2rem; font-weight: 300;">
                Your absolute financial oversight dashboard
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR IMAGE (Father's Day) ----------
image_file = "233.png"  # change to your actual file name
if os.path.exists(image_file):
    st.sidebar.image(image_file, width=200, caption="❤️ For Dad")
else:
    st.sidebar.markdown("❤️ **For Dad**")

st.sidebar.markdown("---")

# ---------- SIDEBAR: CURRENCY SETTING ----------
if "currency" not in st.session_state:
    st.session_state.currency = "₹"
currency_symbol = st.sidebar.selectbox("Currency", ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"])
st.session_state.currency = currency_symbol.split()[0]

st.sidebar.markdown("---")

# ---------- LOAD DATA FROM DATABASE ----------
if "first_load" not in st.session_state:
    st.session_state.expenses_df = load_expenses()
    st.session_state.incomes_df = load_incomes()
    st.session_state.categories_list = load_categories()
    st.session_state.budgets_df = load_budgets()
    st.session_state.recurring_df = load_recurring()
    st.session_state.bills_df = load_bills()
    st.session_state.assets_df = load_assets()
    st.session_state.liabilities_df = load_liabilities()
    st.session_state.investments_df = load_investments()
    st.session_state.goals_df = load_goals()
    st.session_state.income_total = st.session_state.incomes_df["amount"].sum() if not st.session_state.incomes_df.empty else 0
    st.session_state.first_load = True

# ---------- SIDEBAR: ADD EXPENSE ----------
st.sidebar.header("➕ Add Expense")

category_options = ["New"] + st.session_state.categories_list
category = st.sidebar.selectbox("Category (saved)", category_options)
if category == "New":
    category = st.sidebar.text_input("New category name", "Milk")
    if category and category != "New":
        save_category(category.strip().title())
        st.session_state.categories_list = load_categories()

amount = st.sidebar.number_input(f"Amount ({st.session_state.currency})", min_value=0.0, step=10.0)
is_fixed = st.sidebar.checkbox("Fixed expense?")
receipt_file = st.sidebar.file_uploader("Attach receipt", type=["png", "jpg", "jpeg", "jfif"])

if st.sidebar.button("Add Expense"):
    if amount > 0:
        receipt_b64 = None
        if receipt_file:
            receipt_b64 = base64.b64encode(receipt_file.read()).decode()
        save_expense(date.today().isoformat(), category.strip().title(), amount, is_fixed, receipt_b64)
        st.session_state.expenses_df = load_expenses()
        st.sidebar.success(f"Added {st.session_state.currency}{amount} to {category}")
        st.rerun()
    else:
        st.sidebar.error("Amount must be > 0")

st.sidebar.markdown("---")
st.sidebar.header("💰 Income")
income_source = st.sidebar.text_input("Source", "Salary")
income_amt = st.sidebar.number_input(f"Amount ({st.session_state.currency})", min_value=0.0, step=1000.0, key="income_amt")
if st.sidebar.button("Add Income"):
    if income_amt > 0:
        save_income(date.today().isoformat(), income_source, income_amt)
        st.session_state.incomes_df = load_incomes()
        st.session_state.income_total = st.session_state.incomes_df["amount"].sum() if not st.session_state.incomes_df.empty else 0
        st.sidebar.success(f"Added {st.session_state.currency}{income_amt} from {income_source}")
        st.rerun()
    else:
        st.sidebar.error("Amount > 0")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Apply Recurring"):
    today = date.today()
    for idx, row in st.session_state.recurring_df.iterrows():
        next_due = datetime.strptime(row["next_due"], "%Y-%m-%d").date()
        if next_due <= today:
            save_expense(today.isoformat(), row["category"], row["amount"], True, None)
            if row["frequency"] == "Monthly":
                new_due = next_due + timedelta(days=30)
            elif row["frequency"] == "Weekly":
                new_due = next_due + timedelta(days=7)
            else:
                new_due = next_due + timedelta(days=365)
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE recurring SET next_due = ? WHERE category = ? AND amount = ?", 
                      (new_due.strftime("%Y-%m-%d"), row["category"], row["amount"]))
            conn.commit()
            conn.close()
    st.session_state.expenses_df = load_expenses()
    st.sidebar.success("Recurring expenses added!")
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Reset All Data", width='stretch'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses")
    c.execute("DELETE FROM incomes")
    c.execute("DELETE FROM categories")
    c.execute("DELETE FROM budgets")
    c.execute("DELETE FROM recurring")
    c.execute("DELETE FROM bills")
    c.execute("DELETE FROM assets")
    c.execute("DELETE FROM liabilities")
    c.execute("DELETE FROM investments")
    c.execute("DELETE FROM goals")
    conn.commit()
    conn.close()
    for key in list(st.session_state.keys()):
        if key != "currency":
            del st.session_state[key]
    st.rerun()

# ---------- COMPUTE FINANCIAL METRICS ----------
total_expenses = st.session_state.expenses_df["amount"].sum() if not st.session_state.expenses_df.empty else 0
total_income = st.session_state.income_total
savings = total_income - total_expenses
savings_rate = (savings / total_income * 100) if total_income > 0 else 0

# ---------- MAIN TABS ----------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Ledger", "📊 Dashboard", "🎯 Budgets & Goals", "🔄 Recurring & Bills", "💰 Net Worth", "📁 Import/Export"])

# ----- TAB 1: LEDGER (Fully Editable) -----
with tab1:
    st.subheader("Expense Ledger")

    def replace_expenses_for_month(expenses_df, month):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE month_year = ?", (month,))
        for _, row in expenses_df.iterrows():
            fixed = 1 if row["fixed"] else 0
            receipt = row.get("receipt", None)
            c.execute("INSERT INTO expenses (date, category, amount, fixed, receipt, month_year) VALUES (?,?,?,?,?,?)",
                      (row["date"], row["category"], row["amount"], fixed, receipt, month))
            c.execute("INSERT OR IGNORE INTO categories (category) VALUES (?)", (row["category"],))
        conn.commit()
        conn.close()

    if st.session_state.expenses_df.empty:
        st.info("No expenses yet. Add some using the sidebar.")
    else:
        edit_df = st.session_state.expenses_df.copy()
        edit_df["fixed"] = edit_df["fixed"].astype(bool)

        edited_df = st.data_editor(
            edit_df,
            column_config={
                "date": "Date",
                "category": "Category",
                "amount": st.column_config.NumberColumn("Amount", step=10),
                "fixed": st.column_config.CheckboxColumn("Fixed"),
                "receipt": st.column_config.TextColumn("Receipt", disabled=True)
            },
            num_rows="dynamic",
            width='stretch',
            key="ledger_editor"
        )

        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 Save Changes"):
                month = get_current_month()
                replace_expenses_for_month(edited_df, month)
                st.session_state.expenses_df = load_expenses()
                st.success("Changes saved successfully!")
                st.rerun()
        with col_reset:
            if st.button("↩️ Undo Changes"):
                st.session_state.expenses_df = load_expenses()
                st.warning("Changes discarded.")
                st.rerun()

# ----- TAB 2: DASHBOARD -----
with tab2:
    if st.session_state.expenses_df.empty:
        st.info("Add expenses to see charts.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Expenses", f"{st.session_state.currency}{total_expenses:,.0f}")
        col2.metric("Total Income", f"{st.session_state.currency}{total_income:,.0f}" if total_income else "Not set")
        col3.metric("Savings Rate", f"{savings_rate:.1f}%")
        # Calculate runway
        if total_expenses > 0 and total_income > 0:
            first_date = datetime.strptime(st.session_state.expenses_df["date"].min(), "%Y-%m-%d").date()
            days_so_far = max(1, (date.today() - first_date).days)
            daily_spend = total_expenses / days_so_far
            runway = int((total_income - total_expenses) / daily_spend) if daily_spend > 0 else "∞"
        else:
            runway = "∞"
        col4.metric("Runway (days)", str(runway))
        
        # Bar chart
        cat_sum = st.session_state.expenses_df.groupby("category")["amount"].sum().reset_index()
        fig_bar = px.bar(cat_sum, x="category", y="amount", title="Spending by Category",
                         color="amount", color_continuous_scale="Viridis", text_auto=True)
        st.plotly_chart(fig_bar, width='stretch')
        
        # Pie chart
        fig_pie = px.pie(cat_sum, values="amount", names="category", title="Expense Distribution",
                         hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, width='stretch')
        
        # Forecast chart
        if not st.session_state.expenses_df.empty:
            first_date = datetime.strptime(st.session_state.expenses_df["date"].min(), "%Y-%m-%d").date()
            days_so_far = max(1, (date.today() - first_date).days)
            daily_avg = total_expenses / days_so_far
            days = list(range(31))
            balance = [total_income - total_expenses + daily_avg * i for i in days]
            fig_forecast = px.line(x=days, y=balance, title="Projected Balance (Next 30 Days)",
                                   labels={"x": "Days", "y": f"Balance ({st.session_state.currency})"})
            st.plotly_chart(fig_forecast, width='stretch')
        
        # Right/Wrong path
        if savings_rate >= 20:
            st.success(f"🟢 RIGHT PATH – Savings rate {savings_rate:.1f}% > 20% benchmark")
        else:
            st.error(f"🔴 DEVIATING – Savings rate {savings_rate:.1f}% < 20% benchmark")

# ----- TAB 3: BUDGETS & GOALS -----
with tab3:
    st.subheader("Envelope Budgeting")
    for cat in st.session_state.categories_list:
        col1, col2 = st.columns([2,1])
        with col1:
            current_spent = st.session_state.expenses_df[st.session_state.expenses_df["category"]==cat]["amount"].sum() if not st.session_state.expenses_df.empty else 0
            budget_row = st.session_state.budgets_df[st.session_state.budgets_df["category"]==cat] if not st.session_state.budgets_df.empty else pd.DataFrame()
            budget = budget_row["limit_amount"].iloc[0] if not budget_row.empty else 0
            if budget > 0:
                percent = min(100, (current_spent / budget) * 100)
                st.progress(percent/100, text=f"{cat}: {st.session_state.currency}{current_spent:,.0f} / {st.session_state.currency}{budget:,.0f}")
                if current_spent > budget:
                    st.warning(f"⚠️ Overspent on {cat} by {st.session_state.currency}{current_spent-budget:,.0f}")
        with col2:
            new_budget = st.number_input(f"Budget {cat}", value=float(budget), step=500.0, key=f"budget_{cat}")
            if new_budget != budget:
                save_budget(cat, new_budget)
                st.session_state.budgets_df = load_budgets()
                st.rerun()
    
    st.markdown("---")
    st.subheader("🎯 Savings Goals")
    with st.form("goal_form"):
        goal_name = st.text_input("Goal name", placeholder="e.g., Vacation")
        goal_target = st.number_input("Target amount", min_value=0.0, step=1000.0)
        goal_saved = st.number_input("Already saved", min_value=0.0, step=500.0)
        if st.form_submit_button("Add Goal"):
            if goal_name:
                save_goal(goal_name, goal_target, goal_saved)
                st.session_state.goals_df = load_goals()
                st.success("Goal added!")
                st.rerun()
    
    for idx, row in st.session_state.goals_df.iterrows():
        progress = (row["saved_so_far"] / row["target_amount"]) * 100 if row["target_amount"] > 0 else 0
        st.progress(min(100, progress)/100, text=f"{row['name']}: {st.session_state.currency}{row['saved_so_far']:,.0f} / {st.session_state.currency}{row['target_amount']:,.0f}")
        new_saved = st.number_input(f"Update {row['name']}", value=row["saved_so_far"], step=500, key=f"goal_update_{idx}")
        if new_saved != row["saved_so_far"]:
            update_goal_saved(row["name"], new_saved)
            st.session_state.goals_df = load_goals()
            st.rerun()
        if st.button(f"Delete {row['name']}", key=f"del_goal_{idx}"):
            delete_goal(row["name"])
            st.session_state.goals_df = load_goals()
            st.rerun()

# ----- TAB 4: RECURRING & BILLS -----
with tab4:
    st.subheader("Recurring Expenses")
    with st.form("recurring_form"):
        rec_cat = st.text_input("Category")
        rec_amt = st.number_input("Amount", min_value=0.0)
        rec_freq = st.selectbox("Frequency", ["Monthly", "Weekly", "Yearly"])
        next_due = st.date_input("Next due date")
        if st.form_submit_button("Add Recurring"):
            if rec_cat and rec_amt > 0:
                save_recurring(rec_cat, rec_amt, rec_freq, next_due.strftime("%Y-%m-%d"))
                st.session_state.recurring_df = load_recurring()
                st.success("Recurring added!")
                st.rerun()
    st.dataframe(st.session_state.recurring_df, width='stretch')
    
    st.markdown("---")
    st.subheader("📅 Bill Reminders")
    with st.form("bill_form"):
        bill_desc = st.text_input("Bill description")
        bill_amt = st.number_input("Bill amount", min_value=0.0)
        bill_due = st.date_input("Due date")
        if st.form_submit_button("Add Bill"):
            if bill_desc and bill_amt > 0:
                save_bill(bill_desc, bill_amt, bill_due.strftime("%Y-%m-%d"), False)
                st.session_state.bills_df = load_bills()
                st.success("Bill added!")
                st.rerun()
    
    for idx, row in st.session_state.bills_df.iterrows():
        due_date = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
        col1, col2, col3 = st.columns([3,1,1])
        col1.write(f"{row['description']} – {st.session_state.currency}{row['amount']:,.0f} due {due_date}")
        if due_date < date.today() and not row["paid"]:
            col2.warning("⚠️ Overdue")
        paid = col3.checkbox("Paid", value=row["paid"], key=f"bill_{idx}")
        if paid != row["paid"]:
            update_bill_paid(row["description"], paid)
            st.session_state.bills_df = load_bills()
            st.rerun()

# ----- TAB 5: NET WORTH -----
with tab5:
    st.subheader("Assets")
    with st.form("asset_form"):
        asset_name = st.text_input("Asset name")
        asset_value = st.number_input("Value", min_value=0.0)
        if st.form_submit_button("Add Asset"):
            if asset_name:
                save_asset(asset_name, asset_value)
                st.session_state.assets_df = load_assets()
                st.rerun()
    st.dataframe(st.session_state.assets_df, width='stretch')
    
    st.subheader("Liabilities")
    with st.form("liability_form"):
        liab_name = st.text_input("Liability name")
        liab_amount = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Add Liability"):
            if liab_name:
                save_liability(liab_name, liab_amount)
                st.session_state.liabilities_df = load_liabilities()
                st.rerun()
    st.dataframe(st.session_state.liabilities_df, width='stretch')
    
    total_assets = st.session_state.assets_df["value"].sum() if not st.session_state.assets_df.empty else 0
    total_liab = st.session_state.liabilities_df["amount"].sum() if not st.session_state.liabilities_df.empty else 0
    net_worth = total_assets - total_liab
    st.metric("Net Worth", f"{st.session_state.currency}{net_worth:,.0f}")
    
    st.subheader("📈 Investments")
    with st.form("investment_form"):
        inv_name = st.text_input("Investment name")
        inv_amt = st.number_input("Amount", min_value=0.0)
        inv_type = st.selectbox("Type", ["Stocks", "Mutual Funds", "Crypto", "PPF", "Real Estate"])
        if st.form_submit_button("Add Investment"):
            if inv_name:
                save_investment(inv_name, inv_amt, inv_type)
                st.session_state.investments_df = load_investments()
                st.rerun()
    st.dataframe(st.session_state.investments_df, width='stretch')

# ----- TAB 6: IMPORT/EXPORT -----
with tab6:
    st.subheader("Export Data")
    if st.button("Download Expenses CSV"):
        csv = st.session_state.expenses_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="Ergosphere_expenses.csv">Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    st.subheader("Import from CSV")
    uploaded_file = st.file_uploader("Upload CSV (Date,Category,Amount,Fixed)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        required = ["Date", "Category", "Amount"]
        if all(col in df.columns for col in required):
            for _, row in df.iterrows():
                save_expense(row["Date"], row["Category"], row["Amount"], row.get("Fixed", False), None)
            st.session_state.expenses_df = load_expenses()
            st.success("Import successful!")
            st.rerun()
        else:
            st.error("Missing required columns: Date, Category, Amount")

# ---------- SIDEBAR FOOTER ----------
st.sidebar.markdown("---")
st.sidebar.info("⚡ **Ergosphere** – Financial Oversight")
st.sidebar.caption("Data persists in SQLite database")