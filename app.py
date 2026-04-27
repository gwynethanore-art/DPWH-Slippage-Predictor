import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring & Slippage Forecaster")

# UPDATE MO ITO SA ACTIVE NGROK LINK MO
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Project Schedule")
    budget = st.number_input("Contract Budget (PHP)", value=3000000.0)
    planned_dur = st.number_input("Original Duration (Days)", value=180)
    
    st.write("---")
    st.subheader("⏱️ Current Progress Tracker")
    # Dito na papasok yung example mo na Day 50 vs 60, pero flexible kahit anong number
    target_day = st.number_input("Target Day (Where should we be today?)", value=0)
    actual_day = st.number_input("Actual Day (What day is it today?)", value=0)
    
    # Automatic Math for current delay
    current_delay = actual_day - target_day
    if planned_dur > 0:
        current_slippage_pct = (current_delay / planned_dur) * 100
    else:
        current_slippage_pct = 0

with col2:
    st.subheader("⚠️ Site Conditions (Risk Factors)")
    st.write("Rate the intensity of risks affecting the project today:")
    # 1 to 5 scale para user-friendly
    risk_level = st.select_slider("Current Risk Intensity (1=Low, 5=High)", options=[1, 2, 3, 4, 5], value=3)
    
    if current_delay > 0:
        st.warning(f"Project is currently {current_delay} days BEHIND schedule.")
    elif current_delay < 0:
        st.success(f"Project is {abs(current_delay)} days AHEAD of schedule.")

# --- CALCULATION LOGIC ---
if st.button("CALCULATE FINAL PREDICTION", use_container_width=True):
    # Hidden Logic para sa 26 inputs
    norm_cost = budget / 50000000 
    norm_dur = planned_dur / 1000
    risk_inputs = [risk_level / 5] * 18
    weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
    
    final_inputs = risk_inputs + weights + [norm_cost, norm_dur]
    
    try:
        response = requests.post(API_URL, json={"inputs": final_inputs})
        if response.status_code == 200:
            ai_forecast = response.json()['slippage'] * 100
            
            # TOTAL SLIPPAGE = Current Delay + Predicted Future Delay
            total_slippage = current_slippage_pct + ai_forecast
            
            # Limit results para hindi lumampas sa reality
            if total_slippage > 100: total_slippage = 100.0
            if total_slippage < -100: total_slippage = -100.0

            st.write("---")
            st.markdown(f"## Predicted Final Slippage: **{total_slippage:.2f}%**")
            
            if total_slippage > 15:
                st.error("🚨 **CRITICAL STATUS:** High probability of significant project delay.")
            elif total_slippage > 5:
                st.warning("⚠️ **WATCH STATUS:** Moderate slippage detected. Monitoring required.")
            else:
                st.success("✅ **STABLE STATUS:** Project is performing within acceptable limits.")
    except:
        st.error("AI is not responding. Make sure Google Colab and Ngrok are running.")