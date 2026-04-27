import streamlit as st
import requests

st.set_page_config(page_title="DPWH-NCR Slippage Predictor", layout="wide")

# Title and Branding
st.title("🏗️ Hybrid AHP-ANN Slippage Prediction System")
st.markdown("### Development of a Predictive Model for DPWH Road Construction Projects")
st.write("---")

API_URL = "https://willing-finch-fool.ngrok-free.dev/predict" 

# --- SIDEBAR: PROJECT OVERVIEW ---
with st.sidebar:
    st.header("Project Metadata")
    actual_cost = st.number_input("Contract Amount (PHP)", value=15000000.0, step=500000.0)
    actual_dur = st.number_input("Original Duration (Days)", value=180, step=10)
    
    # Hidden Auto-Normalization (Para tama ang results)
    norm_cost = actual_cost / 50000000  # Max cost in training data
    norm_dur = actual_dur / 1000        # Max duration in training data

# --- MAIN PANEL: RISK ASSESSMENT ---
st.subheader("📋 Risk Indicator Assessment")
st.info("Rate the following indicators based on site inspection and project evaluation (1 = Very Low, 5 = Very High)")

col1, col2 = st.columns(2)

with col1:
    st.write("**⚠️ Environmental & Site Risks**")
    r28 = st.select_slider("Risk 28: Weather Conditions", options=[1, 2, 3, 4, 5], value=3)
    r07 = st.select_slider("Risk 07: Site Accessibility", options=[1, 2, 3, 4, 5], value=2)
    r15 = st.select_slider("Risk 15: Right-of-Way (ROW) Issues", options=[1, 2, 3, 4, 5], value=1)
    # Pwede nating dagdagan dito yung iba pang Risks niyo...

with col2:
    st.write("**⚙️ Resource & Technical Risks**")
    r27 = st.select_slider("Risk 27: Equipment Breakdown", options=[1, 2, 3, 4, 5], value=2)
    r09 = st.select_slider("Risk 09: Labor Shortage", options=[1, 2, 3, 4, 5], value=3)
    r23 = st.select_slider("Risk 23: Material Delivery Delays", options=[1, 2, 3, 4, 5], value=2)

# --- PRE-SET AHP WEIGHTS (Based on your Research) ---
# Ito yung sinasabi mong hindi na dapat alam ng user
ahp_weights = [0.154, 0.210, 0.098, 0.245, 0.143, 0.150] 

if st.button("RUN PREDICTIVE ANALYSIS", use_container_width=True):
    # Dito natin bubuuin yung saktong 26 variables para sa AI
    # (Example order: 18 Risks + 6 Weights + Cost + Duration)
    # Gagamit muna tayo ng placeholder values (0.05) sa ibang risks na hindi natin nilagyan ng slider para gumana
    risk_inputs = [r28/5, r07/5, r15/5, r27/5, r09/5, r23/5] + ([0.05] * 12)
    final_inputs = risk_inputs + ahp_weights + [norm_cost, norm_dur]
    
    try:
        response = requests.post(API_URL, json={"inputs": final_inputs})
        if response.status_code == 200:
            res = response.json()['slippage'] * 100
            
            st.write("---")
            st.markdown(f"## Predicted Slippage: **{res:.2f}%**")
            
            if res > 15:
                st.error("🚨 **CRITICAL SLIPPAGE:** Project is significantly behind schedule.")
            elif res > 5:
                st.warning("⚠️ **MODERATE SLIPPAGE:** Needs close monitoring.")
            else:
                st.success("✅ **ON TRACK:** Project is within safe limits.")
        else:
            st.error("Error connecting to AI. Please check Colab.")
    except:
        st.error("The 'Brain' (Google Colab) is currently offline.")