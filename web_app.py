import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import datetime
import io
import pytz 
import qrcode 

# --- CONFIGURATION ---
MY_UPI_ID = "9696159863@ibl" # Aapki UPI ID set kar di gayi hai
SECRET_ACCESS_KEY = "PAWAN786" # Payment ke baad ye password customer ko dena hai

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Auto Finance - Premium", page_icon="🏦")

# Session State for Payment Lock
if 'paid' not in st.session_state:
    st.session_state['paid'] = False

# --- 1. PAYMENT LOCK SCREEN ---
if not st.session_state['paid']:
    st.title("🏦 PAWAN AUTO FINANCE - PREMIUM")
    st.warning("⚠️ Access Restricted! Please complete your payment to unlock the calculator.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plan: Monthly Premium")
        st.write("💰 **Amount: ₹499**")
        st.write("✅ Unlimited PDF Quotations")
        st.write("✅ Vehicle Purchase & Loan Options")
        
        # UPI QR Generation
        upi_url = f"upi://pay?pa={MY_UPI_ID}&pn=Pawan%20Auto%20Finance&am=499&cu=INR"
        qr = qrcode.make(upi_url)
        qr_buf = io.BytesIO()
        qr.save(qr_buf, format='PNG')
        st.image(qr_buf, caption="Scan to Pay ₹499", width=250)

    with col2:
        st.subheader("How to Activate?")
        st.write("1. Scan the QR code and pay ₹499.")
        st.write("2. Send the payment screenshot to **Vikas Mishra**.")
        st.write("3. Enter the **Access Key** you received below:")
        
        key_input = st.text_input("Enter Access Key", type="password", placeholder="Type key here...")
        if st.button("Unlock Calculator Now"):
            if key_input == SECRET_ACCESS_KEY:
                st.session_state['paid'] = True
                st.success("✅ Access Granted!")
                st.rerun()
            else:
                st.error("❌ Invalid Access Key! Please contact Admin.")

# --- 2. MAIN APP CONTENT (Unlocked after payment) ---
else:
    st.sidebar.success("✅ Premium Access: Active")
    if st.sidebar.button("Logout"):
        st.session_state['paid'] = False
        st.rerun()

    st.title("🏦 PAWAN AUTO FINANCE")
    st.markdown(f"**Managed by: Vikas Mishra**") 
    st.write(f"📅 {current_time}")

    st.markdown("---")
    service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

    # Input Section
    cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
    veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

    col1, col2 = st.columns(2)

    if service_mode == "Vehicle Purchase":
        with col1:
            price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Enter Price...")
            down = st.number_input("Down Payment (Rs)", value=None, placeholder="Enter Down...")
        with col2:
            f_ch = st.number_input("File Charges (Rs)", value=None, placeholder="Enter Charges...")
            roi = st.number_input("Interest Rate (%)", value=18.0)
        
        loan_amt = (price if price else 0) - (down if down else 0) + (f_ch if f_ch else 0)
        pdf_labels = [("Vehicle Price", price if price else 0), ("Down Payment", down if down else 0), ("File Charges", f_ch if f_ch else 0)]

    else: # Loan on Vehicle
        with col1:
            l_amt = st.number_input("Loan Amount (Rs)", value=None, placeholder="Enter Loan...")
            hp_ch = st.number_input("HP Charges (Rs)", value=None, placeholder="0.0")
        with col2:
            trans_ch = st.number_input("Transfer Charges (Rs)", value=None, placeholder="0.0")
            roi = st.number_input("Interest Rate (%)", value=18.0)
        
        loan_amt = (l_amt if l_amt else 0) + (hp_ch if hp_ch else 0) + (trans_ch if trans_ch else 0)
        pdf_labels = [("Loan Amount", l_amt if l_amt else 0), ("HP Charges", hp_ch if hp_ch else 0), ("Transfer Charges", trans_ch if trans_ch else 0)]

    # --- LIVE PREVIEW ---
    if loan_amt > 0:
        st.markdown("---")
        st.subheader("📊 Live EMI Preview")
        all_tenures = [5, 10, 12, 15, 18, 24, 30, 36]
        for i in range(0, len(all_tenures), 4):
            cols = st.columns(4)
            for m, col in zip(all_tenures[i:i+4], cols):
                r = roi / (12 * 100)
                emi_val = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
                col.metric(f"{m} Mo", f"₹{emi_val:,.0f}")

    # --- PDF GENERATION ---
    if st.button("Generate Premium PDF Quotation"):
        if not cust_name or not veh_name or loan_amt == 0:
            st.error("Please fill all details!")
        else:
            # Map QR for PDF (Shop Location)
            map_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
            qr_map = qrcode.make(map_link)
            map_buf = io.BytesIO()
            qr_map.save(map_buf, format='PNG')
            map_buf.seek(0)
            map_qr_reader = ImageReader(map_buf)

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Header
            c.setFillColor(colors.HexColor("#1e3d59"))
            c.rect(0, 750, 600, 100, fill=1)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 30)
            c.drawCentredString(300, 795, "PAWAN AUTO FINANCE")
            
            # Body
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 720, f"CUSTOMER: {cust_name.upper()}")
            c.drawString(50, 700, f"VEHICLE: {veh_name.upper()}")
            
            y = 650
            for label, val in pdf_labels:
                c.drawString(70, y, label)
                c.drawRightString(520, y, f"Rs. {val:,.2f}")
                y -= 25
            
            c.drawString(70, y, "Net Loan Amount"); c.drawRight
