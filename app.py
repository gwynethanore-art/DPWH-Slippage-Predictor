import streamlit as st
import requests

# Page setup para mukhang professional dashboard
st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring & Slippage Predictor")
st.markdown("### Hybrid AHP-ANN Predictive Analytics for DPWH-NCR")

# ⚠️ PALITAN MO ITO NG FRESH NGROK LINK MULA SA COLAB MO
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

# --- INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Project Details")
    budget = st.number_input("Contract Budget (PHP)", value=3000000.0, step=100000.0)
    planned_dur = st.number_input("Total Duration (Days)", value=180, step=1)
    
    st.write("---")
    st.subheader("⏱️ Progress Tracker")
    # Dito papasok yung logic mo na Day 50 vs Day 60 (Example)
    target_day = st.number_input("Target Day (Where should we be today?)", value=60)
    actual_day = st.number_input("Actual Day (What day is it today?)", value=60)
    
    # Simple Math: Actual Delay Ratio
    current_delay_days = actual_day - target_day
    current_slip_dec = current_delay_days / planned_dur if planned_dur > 0 else 0

with col2:
    st.subheader("⚠️ Site Conditions")
    st.write("Rate the overall site risk (1=Low, 5=High):")
    risk_level = st.select_slider("Current Risk Intensity", options=[1, 2, 3, 4, 5], value=3)
    
    if current_delay_days > 0:
        st.warning(f"Project is {current_delay_days} days BEHIND schedule.")
    elif current_delay_days < 0:
        st.success(f"Project is {abs(current_delay_days)} days AHEAD of schedule.")
    else:
        st.info("Project is currently ON SCHEDULE.")

st.write("---")

# --- CALCULATION ---
if st.button("GENERATE PREDICTION REPORT", use_container_width=True):
    with st.spinner("AI is analyzing data..."):
        # 1. Fill 18 Risks + 6 AHP Weights + Budget + Duration (Total 26)
        # Ginagawa nating float ang Risk at Budget para mabasa ng Scaler sa Colab
        risk_inputs = [float(risk_level)] * 18
        ahp_weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150]
        
        # RAW INPUTS ang ise-send natin (Budget at Duration) dahil may Scaler.pkl ka sa Colab
        final_inputs = risk_inputs + ahp_weights + [float(budget), float(planned_dur)]
        
        try:
            response = requests.post(API_URL, json={"inputs": final_inputs})
            if response.status_code == 200:
                # Kunin ang AI Future Forecast (Decimal value ito, e.g. 0.05)
                ai_forecast_dec = response.json()['slippage']
                
                # FINAL LOGIC: Current Delay + Predicted Future Delay
                total_slippage_dec = current_slip_dec + ai_forecast_dec
                final_percentage = total_slippage_dec * 100
                
                # Safety caps para hindi mag-milyon ang display
                if final_percentage > 100: final_percentage = 100.0
                if final_percentage < -100: final_percentage = -100.0

                # --- DISPLAY RESULTS ---
                st.metric("PREDICTED FINAL SLIPPAGE", f"{final_percentage:.2f}%")
                
                if final_percentage > 15:
                    st.error("🚨 **CRITICAL:** Project performance is unsatisfactory. Catch-up plan required.")
                elif final_percentage > 5:
                    st.warning("⚠️ **WATCH:** Moderate slippage detected. Increased site supervision needed.")
                else:
                    st.success("✅ **STABLE:** Project is within manageable performance limits.")
            else:
                st.error(f"Server Error: {response.status_code}. Check if Colab is still running.")
        except Exception as e:
            st.error(f"Connection Error: {e}. Make sure Ngrok is active.")