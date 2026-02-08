import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import datetime
import io
import pytz 
import qrcode 

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Auto Finance", page_icon="🏦")

# --- UI DESIGN ---
st.title("🏦 PAWAN AUTO FINANCE")
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

# --- QUOTATION TYPE ---
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
    
    p_val = price if price else 0
    d_val = down if down else 0
    f_val = f_ch if f_ch else 0
    loan_amt = (p_val - d_val) + f_val
    pdf_labels = [("Vehicle Price", p_val), ("Down Payment", d_val), ("File Charges", f_val)]

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
        # QR Code Fixed Logic
        map_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(map_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)

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
        
        c.drawString(70, y, "Net Loan Amount"); c.drawRightString(520, y, f"Rs. {loan_amt:,.2f}")

        # QR Footer
        c.drawImage(qr_reader, 50, 110, width=60, height=60)
        c.setFont("Helvetica-Bold", 7); c.drawString(50, 102, "SCAN FOR ADDRESS")
        
        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Bold", 12); c.drawRightString(540, 85, "Authorized Signature")
        
        c.save()
        st.success("PDF Ready!")
        st.download_button("📥 Download PDF", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
