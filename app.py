import streamlit as st
import datetime
import pandas as pd
from supabase import create_client, Client
from pdf_generator import create_invoice_pdf

# Page configuration
st.set_page_config(page_title="Dispatch Invoice Generator", page_icon="🚚", layout="wide")

# Supabase Initialization
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Failed to connect to Supabase. Check your secrets settings.")
    st.stop()

st.title("🚚 Dispatch Invoice Generator")

# Navigation Tabs
tab1, tab2 = st.tabs(["📝 Generate New Invoice", "📊 Past Invoices"])

with tab1:
    st.subheader("Create Invoice Details")
    
    col1, col2 = st.columns(2)
    with col1:
        inv_num = st.text_input("Invoice Number", value=f"INV-{datetime.date.today().year}-{st.session_state.get('inv_cnt', 101):03d}")
        carrier_name = st.text_input("Carrier / Billed To Name", value="Dashing Transport Services")
        inv_date = st.date_input("Invoice Date", datetime.date.today())
        
        st.markdown("### 📍 Pickup & Drop Info")
        booking_date = st.date_input("1. Booking Date", datetime.date.today())
        pickup_date = st.date_input("2. Pickup Date", datetime.date.today())
        pickup_loc = st.text_input("3. Pickup Location", value="Timberville, VA")
        drop_date = st.date_input("4. Drop Date", datetime.date.today() + datetime.timedelta(days=1))
        drop_loc = st.text_input("5. Drop Location", value="Douglas, GA")

    with col2:
        st.markdown("### 🤝 Broker & Financial Info")
        broker_name = st.text_input("6. Broker Name", value="CH Robinson")
        broker_contact = st.text_input("7. Broker Contact", value="555-0199 / broker@logistics.com")
        
        load_amount = st.number_input("Gross Load Amount ($)", min_value=0.0, value=1150.00, step=50.0)
        percentage = st.number_input("8. Dispatch Fee Percentage (%)", min_value=0.0, max_value=100.0, value=6.0, step=0.5)
        
        # Calculation
        dispatch_fee = round(load_amount * (percentage / 100.0), 2)
        
        st.markdown("---")
        st.metric(label="Calculated Dispatch Fee", value=f"${dispatch_fee:,.2f}")
    
    if st.button("Generate & Save Invoice", type="primary"):
        invoice_payload = {
            "invoice_number": inv_num,
            "invoice_date": str(inv_date),
            "carrier_name": carrier_name,
            "booking_date": str(booking_date),
            "pickup_date": str(pickup_date),
            "pickup_location": pickup_loc,
            "drop_date": str(drop_date),
            "drop_location": drop_loc,
            "broker_name": broker_name,
            "broker_contact": broker_contact,
            "load_amount": load_amount,
            "percentage": percentage,
            "dispatch_fee": dispatch_fee
        }
        
        # Insert into Supabase
        try:
            res = supabase.table("invoices").insert(invoice_payload).execute()
            st.success(f"Invoice {inv_num} saved to Supabase database successfully!")
            
            # Generate PDF
            pdf_bytes = create_invoice_pdf(invoice_payload)
            
            st.download_button(
                label="📥 Download Invoice PDF",
                data=pdf_bytes,
                file_name=f"{inv_num}.pdf",
                mime="application/pdf"
            )
        except Exception as err:
            st.error(f"Error saving invoice: {err}")

with tab2:
    st.subheader("Invoice History")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
        
    try:
        response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
        records = response.data
        
        if records:
            df = pd.DataFrame(records)
            
            # Clean dataframe for display
            display_cols = [
                'invoice_number', 'invoice_date', 'carrier_name', 
                'broker_name', 'load_amount', 'percentage', 'dispatch_fee',
                'booking_date', 'pickup_date', 'pickup_location', 'drop_date', 'drop_location'
            ]
            
            st.dataframe(df[display_cols], use_container_width=True)
            
            # CSV Download option
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Export History as CSV",
                csv,
                "invoice_history.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("No saved invoices found.")
    except Exception as e:
        st.error(f"Failed to fetch records: {e}")
