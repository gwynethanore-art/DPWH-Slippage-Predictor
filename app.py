import streamlit as st
import requests

st.set_page_config(page_title="DPWH Project Tool", layout="centered")
st.title("🏗️ Project Planning & Monitoring Tool")

# ILAGAY ANG PINAKABAGONG NGROK LINK DITO
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

# --- INPUT SECTION ---
st.subheader("Project Parameters")
col1, col2 = st.columns(2)
with col1:
    actual_cost = st.number_input("Contract Amount (PHP)", value=5000000.0)
with col2:
    actual_duration = st.number_input("Contract Duration (Days)", value=180)

st.write("---")
st.subheader("Risk & Monitoring Profile")

# ISANG SLIDER LANG PARA SA LAHAT NG RISKS
overall_risk = st.select_slider(
    "How would you rate the site's overall risk level?",
    options=["Very Low", "Low", "Average", "High", "Critical"],
    value="Average"
)

# I-convert ang text sa number (0.2 to 1.0)
risk_map = {"Very Low": 0.2, "Low": 0.4, "Average": 0.6, "High": 0.8, "Critical": 1.0}
normalized_risk = risk_map[overall_risk]

if st.button("PREDICT SLIPPAGE", use_container_width=True):
    # 1. Automatic Normalization (I-adjust base sa max values ng training data niyo)
    # Halimbawa: kung 50M ang max cost sa training, i-divide sa 50,000,000
    norm_cost = actual_cost / 50000000 
    norm_duration = actual_duration / 1000
    
    # 2. Binuo ang 26 inputs sa background:
    # 18 Risks (Pare-parehong score base sa slider)
    risk_inputs = [normalized_risk] * 18
    # 6 AHP Weights (Average values mula sa CSV niyo)
    ahp_weights = [0.15, 0.20, 0.10, 0.25, 0.15, 0.15]
    
    # Pagsasama-samahin lahat (Total: 26)
    final_inputs = risk_inputs + ahp_weights + [norm_cost, norm_duration]
    
    try:
        response = requests.post(API_URL, json={"inputs": final_inputs})
        if response.status_code == 200:
            res = response.json()['slippage'] * 100
            
            # THE "SENSE" OF THE MODEL:
            st.metric("PREDICTED FINAL SLIPPAGE", f"{res:.2f}%")
            
            if res > 15:
                st.error("⚠️ CRITICAL: It is not recommended to start the project with these parameters. Re-evaluate the duration.")
            else:
                st.success("✅ FEASIBLE: The project timeline is realistic for this budget.")
        else:
            st.error("AI is not responding. Check Colab.")
    except:
        st.error("Connection failed.")