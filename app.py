import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring & Slippage Predictor")
st.markdown("### Hybrid AHP-ANN Predictive Analytics for DPWH-NCR")

# ⚠️ PAALALA: Siguraduhin na ang link na ito ay tugma sa Ngrok mo sa Colab
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Project Details")
    budget = st.number_input("Contract Budget (PHP)", value=3000000.0)
    planned_dur = st.number_input("Total Duration (Days)", value=180)
    
    st.write("---")
    st.subheader("⏱️ Progress Tracker")
    target_day = st.number_input("Target Day (Planned)", value=60)
    actual_day = st.number_input("Actual Day (Current)", value=60)
    
    # Mathematical Slippage (Current Delay)
    current_delay = actual_day - target_day
    current_slip_dec = current_delay / planned_dur if planned_dur > 0 else 0

with col2:
    st.subheader("⚠️ Site Conditions")
    st.write("Rate the overall site risk (1=Low, 5=High):")
    risk_level = st.select_slider("Current Risk Intensity", options=[1, 2, 3, 4, 5], value=3)
    
    if current_delay > 0:
        st.warning(f"Project is {current_delay} days BEHIND schedule.")
    elif current_delay < 0:
        st.success(f"Project is {abs(current_delay)} days AHEAD of schedule.")
    else:
        st.info("Project is ON SCHEDULE.")

st.write("---")

if st.button("GENERATE PREDICTION REPORT", use_container_width=True):
    with st.spinner("AI is analyzing data..."):
        # STEP 1: Manual Normalization (Preno para hindi mag-100%)
        # Ginagawa nating 0.0 to 1.0 ang range para kay ANN
        norm_cost = budget / 50000000.0
        norm_dur = planned_dur / 1000.0
        norm_risk = risk_level / 5.0
        
        # STEP 2: Prepare the 26 inputs
        risk_inputs = [float(norm_risk)] * 18
        ahp_weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
        final_inputs = risk_inputs + ahp_weights + [float(norm_cost), float(norm_dur)]
        
        try:
            response = requests.post(API_URL, json={"inputs": final_inputs})
            if response.status_code == 200:
                ai_forecast_dec = response.json()['slippage']
                
                # TOTAL SLIPPAGE = (Current Status) + (AI Forecast for Future)
                total_slippage_dec = current_slip_dec + ai_forecast_dec
                final_res = total_slippage_dec * 100
                
                # Capping para realistic ang display sa dashboard
                if final_res > 100: final_res = 100.0
                if final_res < -100: final_res = -100.0

                st.metric("PREDICTED FINAL SLIPPAGE", f"{final_res:.2f}%")
                
                if final_res > 15:
                    st.error("🚨 **CRITICAL STATUS:** High probability of major delay.")
                elif final_res > 5:
                    st.warning("⚠️ **WATCH STATUS:** Moderate slippage predicted.")
                else:
                    st.success("✅ **STABLE STATUS:** Project performance is healthy.")
            else:
                st.error("API Error. Check if Colab is still running.")
        except Exception as e:
            st.error(f"Connection Error: {e}")