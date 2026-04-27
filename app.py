import streamlit as st
import requests

st.set_page_config(page_title="DPWH Monitoring Tool", layout="wide")
st.title("🏗️ Project Monitoring Tool")

API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

budget = st.number_input("Budget (PHP)", value=3000000.0)
duration = st.number_input("Duration (Days)", value=180)
target = st.number_input("Target Day", value=60)
actual = st.number_input("Actual Day", value=60)
risk = st.slider("Risk Level (1-5)", 1, 5, 3)

if st.button("RUN PREDICTION"):
    # MANUAL SCALING (Preno para hindi mag-100%)
    n_budget = budget / 50000000.0
    n_duration = duration / 1000.0
    n_risk = risk / 5.0
    
    # 26 Inputs
    inputs = ([float(n_risk)] * 18) + [0.154, 0.210, 0.098, 0.245, 0.143, 0.150] + [n_budget, n_duration]
    
    try:
        res = requests.post(API_URL, json={"inputs": inputs})
        if res.status_code == 200:
            val = res.json()['slippage']
            # Simple math: Actual delay % + AI predicted %
            total = ((actual - target) / duration) + val
            final = total * 100
            
            # Realistic Capping
            if final > 100: final = 100.0
            if final < -100: final = -100.0

            st.header(f"Slippage: {final:.2f}%")
            if final > 15: st.error("CRITICAL")
            else: st.success("STABLE")
    except:
        st.error("Check Colab/Ngrok.")