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
MY_UPI_ID = "9696159863@ibl" 
MY_WHATSAPP = "919696159863" # International format (91 prefix)
SECRET_ACCESS_KEY = "PAWAN786" 

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Auto Finance - Premium", page_icon="🏦", layout="centered")

# Session State for Payment Lock
if 'paid' not in st.session_state:
    st.session_state['paid'] = False

# --- 1. PAYMENT LOCK SCREEN ---
if not st.session_state['paid']:
    st.title("🏦 PAWAN AUTO FINANCE")
    st.subheader("🔐 Premium Portal Access")
    st.error("Aapka Access expired hai ya aap naye user hain. Kripya payment karein.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("💰 **Amount: ₹499 / Month**")
        # UPI QR Generation
        upi_url = f"upi://pay?pa={MY_UPI_ID}&pn=Pawan%20Auto%20Finance&am=499&cu=INR"
        qr = qrcode.make(upi_url)
        qr_buf = io.BytesIO()
        qr.save(qr_buf, format='PNG')
        st.image(qr_buf, caption="Scan and Pay ₹499", width=230)

    with col2:
        st.subheader("Activation Steps:")
        st.write("1️⃣ QR Scan karke ₹499 pay karein.")
        st.write("2️⃣ Niche diye gaye button par click karke screenshot bhejein.")
        
        # WhatsApp Link
        msg = "Sir, maine ₹499 pay kar diye hain. Please mujhe Access Key bhej dijiye."
        wa_url = f"https://wa.me/{MY_WHATSAPP}?text={msg.replace(' ', '%20')}"
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;">
                    ✅ WhatsApp Screenshot & Get Key
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.write("3️⃣ Key milne ke baad yahan dalein:")
        key_input = st.text_input("Enter Access Key", type="password", placeholder="Yahan Key bharein...")
        if st.button("Unlock Calculator Now 🚀"):
            if key_input == SECRET_ACCESS_KEY:
                st.session_state['paid'] = True
                st.success("Access Granted! Loading...")
                st.rerun()
            else:
                st.error("Galat Key! Kripya sahi key dalein.")

# --- 2. MAIN APP CONTENT (Unlocked) ---
else:
    st.sidebar.success("✅ Premium Active")
    if st.sidebar.button("Logout"):
        st.session_state['paid'] = False
        st.rerun()

    st.title("🏦 PAWAN AUTO FINANCE")
    st.markdown(f"**Managed by: Vikas Mishra** | 📅 {current_time}")

    st.markdown("---")
    service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

    cust_name = st.text_input("Customer Name", placeholder="Type Name...")
    veh_name = st.text_input("Vehicle Name", placeholder="Type Vehicle...")

    col1, col2 = st.columns(2)

    if service_mode == "Vehicle Purchase":
        with col1:
            price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="0.0")
            down = st.number_input("Down Payment (Rs)", value=None, placeholder="0.0")
        with col2:
            f_ch = st.number_input("File Charges (Rs)", value=None, placeholder="0.0")
            roi = st.number_input("Interest Rate (%)", value=18.0)
        
        loan_amt = (price if price else 0) - (down if down else 0) + (f_ch if f_ch else 0)
        pdf_labels = [("Vehicle Price", price if price else 0), ("Down Payment", down if down else 0), ("File Charges", f_ch if f_ch else 0)]

    else:
        with col1:
            l_amt = st.number_input("Loan Amount (Rs)", value=None, placeholder="0.0")
            hp_ch = st.number_input("HP Charges (Rs)", value=None, placeholder="0.0")
        with col2:
            trans_ch = st.number_input("Transfer Charges (Rs)", value=None, placeholder="0.0")
            roi = st.number_input("Interest Rate (%)", value=18.0)
        
        loan_amt = (l_amt if l_amt else 0) + (hp_ch if hp_ch else 0) + (trans_ch if trans_ch else 0)
        pdf_labels = [("Loan Amount", l_amt if l_amt else 0), ("HP Charges", hp_ch if hp_ch else 0), ("Transfer Charges", trans_ch if trans_ch else 0)]

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

    if st.button("Generate Premium PDF Quotation"):
        if not cust_name or not veh_name or loan_amt == 0:
            st.error("Pura details bharein!")
        else:
            map_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
            qr_map = qrcode.make(map_link)
            map_buf = io.BytesIO()
            qr_map.save(map_buf, format='PNG')
            map_buf.seek(0)
            map_qr_reader = ImageReader(map_buf)

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFillColor(colors.HexColor("#1e3d59"))
            c.rect(0, 750, 600, 100, fill=1)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 30)
            c.drawCentredString(300, 795, "PAWAN AUTO FINANCE")
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 720, f"CUSTOMER: {cust_name.upper()}")
            c.drawString(50, 700, f"VEHICLE: {veh_name.upper()}")
            y = 650
            for label, val in pdf_labels:
                c.drawString(70, y, label)
                c.drawRightString(520, y, f"Rs. {val:,.2f}")
                y -= 25
            c.drawString(70, y, "Net Loan Amount"); c.drawRightString(520, y, f"Rs. {loan_amt:,.2f}")
            c.drawImage(map_qr_reader, 50, 110, width=60, height=60)
            c.setFont("Helvetica-Bold", 7); c.drawString(50, 102, "SCAN FOR ADDRESS")
            c.line(50, 100, 540, 100)
            c.setFont("Helvetica-Bold", 12); c.drawRightString(540, 85, "Authorized Signature")
            c.save()
            st.success("PDF Ready!")
            st.download_button("📥 Download PDF", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
