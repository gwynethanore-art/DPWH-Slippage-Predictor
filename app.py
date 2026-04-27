import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring & Slippage Predictor")

# SIGURADUHIN NA TAMA ANG NGROK LINK MO MULA SA COLAB
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Project Details")
    budget = st.number_input("Contract Budget (PHP)", value=3000000.0)
    planned_dur = st.number_input("Total Duration (Days)", value=180)
    
    st.write("---")
    st.subheader("⏱️ Progress Tracker")
    target_day = st.number_input("Target Day (Should be)", value=60)
    actual_day = st.number_input("Actual Day (Today)", value=60)
    
    # Simple Math for Current Delay
    current_delay = actual_day - target_day
    current_slip_dec = current_delay / planned_dur if planned_dur > 0 else 0

with col2:
    st.subheader("⚠️ Site Risks")
    risk_level = st.select_slider("Current Risk Intensity (1-5)", options=[1, 2, 3, 4, 5], value=3)
    
    if current_delay > 0:
        st.warning(f"Project is {current_delay} days BEHIND schedule.")
    elif current_delay < 0:
        st.success(f"Project is {abs(current_delay)} days AHEAD of schedule.")
    else:
        st.info("Project is ON SCHEDULE.")

st.write("---")

if st.button("RUN PREDICTION"):
    # PINAKAMADALING FIX: 
    # Huwag nang mag-divide dito dahil may scaler.pkl ka na sa Colab.
    # I-send ang RAW numbers (3M, 180, etc.)
    
    risk_inputs = [float(risk_level)] * 18 # Gawing float para sa Scaler
    weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
    
    # Raw values ang dulo (budget at planned_dur)
    final_inputs = risk_inputs + weights + [float(budget), float(planned_dur)]
    
    try:
        response = requests.post(API_URL, json={"inputs": final_inputs})
        if response.status_code == 200:
            ai_forecast = response.json()['slippage']
            
            # Formula: (Actual Delay Ratio) + (AI Forecast Ratio)
            total_slippage = (current_slip_dec + ai_forecast) * 100
            
            # Simple guardrails
            if total_slippage > 100: total_slippage = 100.0
            if total_slippage < -100: total_slippage = -100.0

            st.metric("PREDICTED FINAL SLIPPAGE", f"{total_slippage:.2f}%")
            
            if total_slippage > 15:
                st.error("🚨 **CRITICAL:** High chance of major delay.")
            elif total_slippage > 5:
                st.warning("⚠️ **WATCH:** Moderate delay predicted.")
            else:
                st.success("✅ **STABLE:** Project is on track.")
    except Exception as e:
        st.error(f"Error: {e}")