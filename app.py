import streamlit as st
import requests

st.set_page_config(page_title="Slippage Predictor", page_icon="🏗️")
st.title("🏗️ Construction Slippage Predictor")
st.write("ANN-Based Prediction for DPWH NCR Projects")

# PAALALA: Siguraduhin na ang link na ito ay tugma sa lumabas sa Colab mo
API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

st.subheader("Project Data Input")

# Ginawa nating dalawang column para malinis tignan sa dashboard
col1, col2 = st.columns(2)

with col1:
    amt = st.number_input("Contract Amount (PHP)", value=1000000.0)
    dur = st.number_input("Original Duration (Days)", value=180)
    elapsed = st.number_input("Actual Days Elapsed", value=90)

with col2:
    prog = st.slider("Current Physical Progress (%)", 0, 100, 50)
    # Placeholder para sa iba pang 22 inputs na kailangan ng model mo
    other_inputs = [0.0] * 22 

if st.button("RUN PREDICTION"):
    # Pinagsasama ang mga inputs para mabuo ang 26 values na kailangan ng scaler
    data_to_send = [amt, dur, elapsed, prog/100] + other_inputs
    
    try:
        with st.spinner('Calculating...'):
            # Tinatawagan nito ang Google Colab via Ngrok link
            response = requests.post(API_URL, json={"inputs": data_to_send})
            
            if response.status_code == 200:
                result = response.json()['slippage']
                st.metric("Predicted Slippage", f"{result:.2f} %")
                
                # Kulay ng babala depende sa taas ng slippage
                if result > 15:
                    st.error("⚠️ High Risk: Significant delay predicted.")
                else:
                    st.success("✅ Manageable: Project is on track.")
            else:
                st.error("Error: Check if Google Colab is still running.")
    except Exception as e:
        st.error("Connection Failed. Siguraduhing tama ang Ngrok URL mo.")
        
        