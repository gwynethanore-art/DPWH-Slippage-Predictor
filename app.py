import streamlit as st
import requests

# Page Setup
st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide", page_icon="🏗️")

st.title("🏗️ Project Monitoring & Slippage Predictor")
st.markdown("### Hybrid AHP-ANN Predictive Analytics for DPWH-NCR")
st.write("---")

# ⚠️ PAALALA: Palitan ang URL na ito base sa Ngrok link mula sa Colab mo!
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

# Layout para sa Inputs
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
    st.info("Rate the site conditions based on AHP intensity (1 = Low Risk, 5 = High Risk)")
    risk_level = st.select_slider("Current Risk Intensity", options=[1, 2, 3, 4, 5], value=1)
    
    # Simple logic display for current status
    current_delay = actual_day - target_day
    if current_delay > 0:
        st.warning(f"Current Status: Project is {current_delay} days BEHIND schedule.")
    elif current_delay < 0:
        st.success(f"Current Status: Project is {abs(current_delay)} days ADVANCED.")
    else:
        st.info("Current Status: Project is ON SCHEDULE.")

st.write("---")

# Prediction Trigger
if st.button("GENERATE PREDICTION REPORT", use_container_width=True):
    if budget <= 0 or duration <= 0:
        st.error("Please provide valid Budget and Duration values.")
    else:
        with st.spinner("AI is analyzing historical data and risks..."):
            # 1. Normalization (Manual Scaling para iwas 100% error)
            n_budget = budget / 50000000.0
            n_duration = duration / 1000.0
            n_risk = risk_level / 5.0
            
            # 2. Prepare 26 Inputs (18 Risk Nodes + 6 AHP Weights + 2 Physical Constraints)
            risk_inputs = [float(n_risk)] * 18
            ahp_weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
            final_inputs = risk_inputs + ahp_weights + [float(n_budget), float(n_duration)]
            
            try:
                # 3. Request to Google Colab API
                response = requests.post(API_URL, json={"inputs": final_inputs}, timeout=15)
                
                if response.status_code == 200:
                    ai_forecast_dec = response.json()['slippage']
                    
                    # 4. CALCULATION LOGIC
                    # Math: (Actual - Target) / Duration
                    current_slip_dec = (actual_day - target_day) / duration if duration > 0 else 0
                    
                    # CALIBRATION: Binabawasan ang "bias" ng AI base sa Risk Level
                    if risk_level == 1 and actual_day <= target_day:
                        calibrated_ai = ai_forecast_dec * 0.05  # 5% influence lang
                    elif risk_level <= 3:
                        calibrated_ai = ai_forecast_dec * 0.25  # 25% influence
                    else:
                        calibrated_ai = ai_forecast_dec * 1.0   # Full influence pag high risk
                    
                    # Final Formula
                    total_slippage = (current_slip_dec + calibrated_ai) * 100
                    
                    # Hard Caps for realism
                    total_slippage = max(min(total_slippage, 100.0), -100.0)

                    # 5. Display Results
                    st.write("---")
                    st.metric("PREDICTED FINAL SLIPPAGE", f"{total_slippage:.2f}%")
                    
                    if total_slippage > 15:
                        st.error("🚨 **CRITICAL STATUS:** High probability of major project delay.")
                        st.markdown("Immediate intervention required per DPWH D.O. 193.")
                    elif total_slippage > 5:
                        st.warning("⚠️ **WATCHLIST STATUS:** Moderate slippage predicted.")
                        st.markdown("Close monitoring is recommended.")
                    elif total_slippage < 0:
                        st.success(f"🚀 **EXCELLENT:** Project is predicted to be ADVANCED by {abs(total_slippage):.2f}%.")
                        st.markdown("Current efficiency suggests project completion ahead of schedule.")
                    else:
                        st.success("✅ **STABLE STATUS:** Project performance is healthy.")
                        st.markdown("No significant slippage predicted.")
                else:
                    st.error(f"API Error: {response.json().get('error', 'Check model file in Colab')}")
            except Exception as e:
                st.error(f"Connection Error: Ensure your Ngrok link is updated and Colab is running.")

st.markdown("---")
st.caption("Developed for Research Purposes - PUP Civil Engineering 2026")