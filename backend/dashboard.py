import streamlit as st
import httpx
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Aetheris OS - Command Center", layout="wide")

st.title("🌿 Aetheris OS: Autonomous Living Building")
st.markdown("---")

# 1. Hardware Simulation Sidebar
# Allows judges to manually override real-world sensors to test autonomous logic
st.sidebar.header("🕹️ Hardware Simulator")
sim_mode = st.sidebar.toggle("Enable Manual Simulation")

if sim_mode:
    sim_cpu = st.sidebar.slider("Simulate CPU Load (%)", 0, 100, 50)
    sim_temp = st.sidebar.slider("Simulate Outdoor Temp (°F)", 20, 100, 57)
    sim_rain = st.sidebar.slider("Cistern Level (%)", 0, 100, 80)
else:
    # Pulling real telemetry from local machine sensors
    try:
        res = httpx.get("http://localhost:8000/system/circular-strategy", timeout=5.0).json()
        sim_cpu = res['server_state']['cpu_usage_percent']
        sim_temp = res['weather']['temp']
        sim_rain = 85  # Default sensor baseline
    except:
        sim_cpu, sim_temp, sim_rain = 20, 57, 85

# 2. Sustainability Metrics (Business Analytics Value Proposition)
st.subheader("📊 Environmental Impact")
col1, col2, col3 = st.columns(3)

# Based on 65W TDP "Thermal Crack"
saved_kwh = (sim_cpu / 100) * 0.065
co2_avoided = saved_kwh * 0.4 # kg CO2 per kWh grid displacement

with col1:
    st.metric("Energy Scavenged", f"{saved_kwh:.4f} kWh", delta="Circular Heat")
with col2:
    st.metric("CO2 Avoided", f"{co2_avoided:.4f} kg", delta="-15% vs Grid")
with col3:
    st.metric("Sustainability Score", f"{int(sim_cpu * 0.8 + sim_rain * 0.2)}/100")

# 3. Building Command & Neural Status
# High-level interaction layer for system overrides or sensory input
st.subheader("🧠 Aetheris Command & Neural Status")
command_input = st.text_input("Input sensory state (e.g., 'User shivering', 'Prioritize PCM Soak'):")

if command_input:
    with st.spinner("Processing neural trajectory..."):
        try:
            res = httpx.post("http://localhost:8000/voice/intent", 
                             params={"user_text": command_input}, timeout=15.0).json()
            
            with st.container(border=True):
                st.markdown(f"**Admin Input:** `{command_input}`")
                st.markdown(f"**Aetheris Reasoning:** {res['response']}")
            
            # Hardware simulation feedback
            if "shiver" in command_input.lower() or "cold" in command_input.lower():
                st.toast("Redirecting 65W Server Waste Heat to local zone...")
        except Exception as e:
            st.error(f"Command Error: {str(e)}")

# 4. Live Actuator Logic (Autonomous Physical Behavior)
st.subheader("⚙️ Live Actuator Status")
heat_demand = 70 - sim_temp
actuators = {
    "System": ["Hydra Loop", "Solar Thermal", "Window Blinds", "Radiant Floor"],
    "Intensity": [
        f"{min(100, sim_cpu + 10)}%", 
        "OFF" if sim_temp < 60 else "ON", 
        "CLOSED" if sim_temp < 50 else "OPEN", 
        f"{max(0, heat_demand * 2)}%"
    ],
    "Source": [
        "Server Waste Heat" if sim_cpu > 30 else "N/A", 
        "Passive", 
        "Passive", 
        "Hybrid (Server + Grid)" if sim_cpu > 40 else "Grid"
    ]
}
st.table(pd.DataFrame(actuators))

# 5. Predictive Intelligence
st.subheader("🗓️ 72-Hour Thermal Management Plan")
if st.button("Generate Fresh Predictive Plan"):
    with st.spinner("Gemini calculating deterministic thermal trajectories..."):
        try:
            plan_res = httpx.get("http://localhost:8000/plan/72h", timeout=60.0).json()
            st.markdown(plan_res['plan']['plan'])
        except Exception as e:
            st.error(f"Planning Error: {str(e)}")
