import streamlit as st
import pandas as pd
from datetime import timedelta, datetime, date
import calendar

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Invoice Simulator", layout="wide")

# --- SIDEBAR (Left Panel) ---
with st.sidebar:
    st.title("Settings")
    
    bill_type = st.selectbox("Bill Type", [
        "List Bill - Group", "List Bill - Individual", 
        "Self Bill", "Individual direct"
    ])
    
    premium = st.number_input("Monthly Premium ($)", min_value=0.0, value=100.00)
    
    freq = st.selectbox("Invoicing Frequency", ["Weekly", "Monthly"])
    modality = st.selectbox("Modality", ["Monthly", "Weekly", "Biweekly"])
    start_date = st.date_input("Start Date", date(2026, 1, 1))
    
    num_invoices = st.slider("Invoices to show", 1, 52, 12)
    
    submit_button = st.button("Generate Invoices", use_container_width=True)
    
    st.markdown("---")
    st.caption("Created by Dwaipayan Sinha") # Your initials in small font

# --- MAIN PANEL ---
st.title("Invoicing period and current due amount")

if submit_button:
    # 1. Calculation Logic for Modal Amounts
    annual_premium = premium * 12
    if modality == "Weekly":
        modal_amount = round(annual_premium / 52, 2)
    elif modality == "Biweekly":
        modal_amount = round(annual_premium / 26, 2)
    else: # Monthly
        modal_amount = round(premium, 2)

    invoices = []
    current_start = datetime.combine(start_date, datetime.min.time())
    # This is the "Anchor Date" for Biweekly/Weekly payments
    anchor_date = current_start 

    # 2. Generation Loop
    for i in range(1, num_invoices + 1):
        if freq == "Weekly":
            current_end = current_start + timedelta(days=6)
        else: # Monthly Frequency
            last_day = calendar.monthrange(current_start.year, current_start.month)[1]
            current_end = current_start.replace(day=last_day)
        
        due_amount = 0.00
        
        # --- FIXED LOGIC ENGINE ---
        
        # Case A: Modality is Monthly (Trigger on the 1st of the month)
        if modality == "Monthly":
            temp_date = current_start
            while temp_date <= current_end:
                if temp_date.day == 1:
                    due_amount = modal_amount
                    break
                temp_date += timedelta(days=1)
        
        # Case B: Modality is Weekly or Biweekly
        # We check if any "Payment Due Date" falls within the current invoicing period
        else:
            days_step = 7 if modality == "Weekly" else 14
            
            # Start from the anchor and jump forward until we reach or pass the current period
            check_date = anchor_date
            while check_date <= current_end:
                if current_start <= check_date <= current_end:
                    due_amount += modal_amount
                check_date += timedelta(days=days_step)

        invoices.append({
            "Inv #": i,
            "Period": f"{current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}",
            "Due ($)": f"{due_amount:.2f}"
        })
        current_start = current_end + timedelta(days=1)

    # 3. Display Results
    col1, col2 = st.columns([2, 1]) # Keep boxes narrow
    with col1:
        st.info(f"Results for **{bill_type}**")
        df = pd.DataFrame(invoices)
        st.dataframe(df, height=400, use_container_width=True, hide_index=True)
else:
    st.write("Click 'Generate Invoices' on the left.")