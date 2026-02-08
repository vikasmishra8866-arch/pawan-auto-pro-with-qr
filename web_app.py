import streamlit as st
import qrcode
from PIL import Image
import io

# --- 1. SUBSCRIPTION LOGIC ---
# Ye secret password aap payment ke baad customer ko denge
SECRET_ACCESS_KEY = "PAWAN786" 

if 'paid' not in st.session_state:
    st.session_state['paid'] = False

# --- 2. PAYMENT PAGE DESIGN ---
if not st.session_state['paid']:
    st.title("🏦 PAWAN AUTO FINANCE - PREMIUM")
    st.warning("⚠️ Access Restricted! Please complete payment to use the calculator.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Plan Details")
        st.write("✅ Unlimited PDF Quotations")
        st.write("✅ Vehicle Loan Option")
        st.write("✅ Validity: 1 Month")
        st.write("💰 **Amount: ₹499**")
        
        # UPI QR Link (Aapka UPI ID yahan daalein)
        upi_id = "yourname@upi" # <--- YAHAN APNA UPI ID DALO
        upi_url = f"upi://pay?pa={upi_id}&pn=Pawan%20Auto&am=499&cu=INR"
        
        qr = qrcode.make(upi_url)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        st.image(buf, caption="Scan to Pay ₹499", width=250)

    with col2:
        st.subheader("Activate Account")
        st.info("Payment ke baad screenshot 98XXXXXXXX par bhejein aur Access Key mangwayein.")
        
        key_input = st.text_input("Enter Access Key", type="password")
        if st.button("Activate Now"):
            if key_input == SECRET_ACCESS_KEY:
                st.session_state['paid'] = True
                st.success("Successfully Activated!")
                st.rerun()
            else:
                st.error("Wrong Access Key! Please contact Admin.")

# --- 3. ACTUAL APP CODE (After Payment) ---
else:
    st.sidebar.success("Premium Access: ACTIVE")
    if st.sidebar.button("Logout"):
        st.session_state['paid'] = False
        st.rerun()

    # --- Yahan se aapka purana Quotation wala pura code shuru hoga ---
    st.title("🏦 PAWAN AUTO FINANCE CALCULATOR")
    # ... (Baki purana code jo maine pehle diya tha wo yahan paste karein)
