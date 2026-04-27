import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide", page_icon="🏗️")
st.title("🏗️ Project Monitoring & Slippage Predictor")
st.markdown("### Hybrid AHP-ANN Predictive Analytics for DPWH-NCR")
st.write("---")

API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Project Profile")
    budget = st.number_input("Contract Budget (PHP)", value=0.0, step=100000.0)
    duration = st.number_input("Total Duration (Days)", value=0, step=1)
    st.write("---")
    st.subheader("⏱️ Current Progress")
    target_day = st.number_input("Target Day (Should be)", value=0)
    actual_day = st.number_input("Actual Day (Today)", value=0)

with col2:
    st.subheader("⚠️ Risk Assessment")
    risk_level = st.select_slider("Current Risk Intensity", options=[1, 2, 3, 4, 5], value=1)
    diff = target_day - actual_day
    if diff < 0:
        st.success(f"Current Status: Project is {abs(diff)} days ADVANCED.")
    elif diff > 0:
        st.warning(f"Current Status: Project is {diff} days BEHIND schedule.")
    else:
        st.info("Current Status: Project is ON SCHEDULE.")

st.write("---")

if st.button("GENERATE PREDICTION REPORT", use_container_width=True):
    if budget <= 0 or duration <= 0:
        st.error("Please provide valid Budget and Duration values.")
    else:
        with st.spinner("AI is analyzing data..."):
            n_budget = budget / 50000000.0
            n_duration = duration / 1000.0
            n_risk = risk_level / 5.0
            
            risk_inputs = [float(n_risk)] * 18
            ahp_weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
            final_inputs = risk_inputs + ahp_weights + [float(n_budget), float(n_duration)]
            
            try:
                response = requests.post(API_URL, json={"inputs": final_inputs}, timeout=15)
                if response.status_code == 200:
                    ai_forecast_dec = response.json()['slippage']
                    current_slip_dec = (target_day - actual_day) / duration if duration > 0 else 0
                    
                    # NEW CALIBRATION: Mas mabait sa Low Risk
                    if risk_level == 1:
                        multiplier = 0.02 if current_slip_dec <= 0 else 0.05
                    elif risk_level <= 3:
                        multiplier = 0.15
                    else:
                        multiplier = 0.80
                    
                    calibrated_ai = ai_forecast_dec * multiplier
                    total_slippage = (current_slip_dec + calibrated_ai) * 100
                    total_slippage = max(min(total_slippage, 100.0), -100.0)

                    st.write("---")
                    st.metric("PREDICTED FINAL SLIPPAGE", f"{total_slippage:.2f}%")
                    
                    if total_slippage > 15:
                        st.error("🚨 **CRITICAL STATUS:** High probability of major project delay.")
                    elif total_slippage > 5:
                        st.warning("⚠️ **WATCHLIST STATUS:** Moderate slippage predicted.")
                    elif total_slippage < 0:
                        st.success(f"🚀 **EXCELLENT:** Project is predicted to be ADVANCED by {abs(total_slippage):.2f}%.")
                    else:
                        st.success("✅ **STABLE STATUS:** Project performance is healthy.")
                else:
                    st.error("API Error: Check your Colab server.")
            except Exception as e:
                st.error("Connection Error: Update your Ngrok link.")

st.markdown("---")
st.caption("Developed for Research Purposes - PUP Civil Engineering 2026")