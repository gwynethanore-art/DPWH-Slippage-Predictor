import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring Tool")

# SIGURADUHIN NA TAMA ANG NGROK LINK MO
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

# INPUTS - Ginawa nating 0 ang default para ikaw ang mag-input
budget = st.number_input("Budget (PHP)", value=0.0)
duration = st.number_input("Duration (Days)", value=0)
target = st.number_input("Target Day (Should be)", value=0)
actual = st.number_input("Actual Day (Today)", value=0)
risk = st.slider("Risk Level (1-5)", 1, 5, 1)

if st.button("RUN PREDICTION"):
    # VALIDATION: Para hindi mag-error kung nakalimutan mag-input
    if budget == 0 or duration == 0:
        st.warning("Pakilagay po ang Budget at Duration.")
    else:
        # MANUAL SCALING (Para safe sa 100% error)
        n_budget = budget / 50000000.0
        n_duration = duration / 1000.0
        n_risk = risk / 5.0
        
        # 26 Inputs (18 risks + 6 weights + cost + duration)
        inputs = ([float(n_risk)] * 18) + [0.154, 0.210, 0.098, 0.245, 0.143, 0.150] + [n_budget, n_duration]
        
        try:
            res = requests.post(API_URL, json={"inputs": inputs})
            if res.status_code == 200:
                val = res.json()['slippage']
                # Math: Current Delay % + AI Forecast %
                current_slip = (actual - target) / duration
                total = (current_slip + val) * 100
                
                # LIMITS
                if total > 100: total = 100.0
                if total < -100: total = -100.0

                st.write("---")
                st.header(f"Final Slippage: {total:.2f}%")
                
                if total > 15:
                    st.error("🚨 STATUS: CRITICAL")
                elif total > 5:
                    st.warning("⚠️ STATUS: WATCHLIST")
                else:
                    st.success("✅ STATUS: STABLE")
            else:
                st.error("May mali sa API. Check Colab.")
        except Exception as e:
            st.error(f"Connection Error: {e}")