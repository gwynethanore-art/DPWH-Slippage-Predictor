import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring & Slippage Predictor")

# SIGURADUHIN NA TAMA ANG NGROK LINK MO DITO
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Project Schedule")
    budget = st.number_input("Contract Budget (PHP)", value=3000000.0)
    planned_dur = st.number_input("Original Duration (Days)", value=180)
    
    st.write("---")
    st.subheader("⏱️ Current Progress Tracker")
    target_day = st.number_input("Target Day (Where should we be?)", value=60)
    actual_day = st.number_input("Actual Day (Where are we today?)", value=60)
    
    # Linear delay math
    current_delay = actual_day - target_day
    # Gawing decimal ang current slippage (e.g., 10 days delay / 180 = 0.05)
    current_slip_dec = current_delay / planned_dur if planned_dur > 0 else 0

with col2:
    st.subheader("⚠️ Site Conditions")
    risk_level = st.select_slider("Current Risk Intensity", options=[1, 2, 3, 4, 5], value=3)
    
    if current_delay > 0:
        st.warning(f"Project is {current_delay} days BEHIND schedule.")
    elif current_delay < 0:
        st.success(f"Project is {abs(current_delay)} days AHEAD of schedule.")
    else:
        st.info("Project is exactly ON SCHEDULE.")

st.write("---")

if st.button("CALCULATE FINAL PREDICTION"):
    # STEP 1: NORMALIZATION (Preno para hindi mag-100% agad)
    norm_cost = budget / 50000000 
    norm_dur = planned_dur / 1000
    
    # STEP 2: Fill 26 inputs
    risk_inputs = [risk_level / 5] * 18
    weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
    final_inputs = risk_inputs + weights + [norm_cost, norm_dur]
    
    try:
        response = requests.post(API_URL, json={"inputs": final_inputs})
        if response.status_code == 200:
            # Kunin ang AI forecast (Decimal, e.g., 0.02)
            ai_forecast = response.json()['slippage']
            
            # TOTAL = Current + Future Forecast
            total_slippage_decimal = current_slip_dec + ai_forecast
            final_res = total_slippage_decimal * 100
            
            # Realistic capping
            if final_res > 100: final_res = 100.0
            if final_res < -100: final_res = -100.0

            st.metric("PREDICTED FINAL SLIPPAGE", f"{final_res:.2f}%")
            
            if final_res > 15:
                st.error("🚨 **CRITICAL STATUS:** High probability of major delay.")
            elif final_res > 5:
                st.warning("⚠️ **WATCH STATUS:** Moderate slippage predicted.")
            else:
                st.success("✅ **STABLE STATUS:** Project performance is healthy.")
    except:
        st.error("AI Server Offline. Check Colab/Ngrok.")