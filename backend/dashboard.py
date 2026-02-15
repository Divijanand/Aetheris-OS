import streamlit as st
import httpx
import pandas as pd
import time
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Aetheris OS - Command Center", layout="wide")
st.title("🌿 Aetheris OS: The Living Machine")
st.caption("Nyra Phase 1–5 • Circular thermal infrastructure • Real-time telemetry")
st.markdown("---")

# ---------------------------------------------------------------------------
# Sidebar: Judge demo controls + manual simulation
# ---------------------------------------------------------------------------
st.sidebar.header("🎬 Judge Demo Controls")

colA, colB = st.sidebar.columns(2)
with colA:
    if st.button("🔥 Heat Spike (80W)"):
        try:
            httpx.post(f"{BACKEND}/demo/heat", json={"watts": 80, "seconds": 45}, timeout=5.0)
            st.sidebar.success("Heat spike engaged")
        except Exception as e:
            st.sidebar.error(f"Demo heat error: {e}")

with colB:
    if st.button("🧊 Reset Heat"):
        try:
            httpx.post(f"{BACKEND}/demo/reset", timeout=5.0)
            st.sidebar.success("Heat reset")
        except Exception as e:
            st.sidebar.error(f"Demo reset error: {e}")

auto_refresh = st.sidebar.toggle("Auto-refresh (2s)", value=True)

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Hardware Simulator")
sim_mode = st.sidebar.toggle("Manual Simulation")

if sim_mode:
    sim_cpu = st.sidebar.slider("Simulate CPU Load (%)", 0, 100, 50)
    sim_temp = st.sidebar.slider("Simulate Outdoor Temp (°F)", 20, 100, 57)
    sim_rain = st.sidebar.slider("Cistern Level (%)", 0, 100, 80)
else:
    try:
        r = httpx.get(f"{BACKEND}/system/circular-strategy", timeout=5.0)
        r.raise_for_status()
        res = r.json()
        sim_cpu = res["server_state"]["cpu_usage_percent"]
        sim_temp = res.get("weather", {}).get("temp") or 57
        sim_rain = 85
        st.sidebar.success("Live telemetry ✅")
    except Exception:
        sim_cpu, sim_temp, sim_rain = 20, 57, 85
        st.sidebar.warning("Fallback values (backend not ready)")

# ---------------------------------------------------------------------------
# Environmental Impact (demo-friendly scoring)
# ---------------------------------------------------------------------------
st.subheader("📊 Environmental Impact")

saved_kwh = (sim_cpu / 100) * 0.25  # demo-friendly scaling
co2_avoided = saved_kwh * 0.4
heat_demand = max(0, 70 - sim_temp)
sustainability_score = int(
    min(
        100,
        (sim_cpu * 0.45) + (saved_kwh * 250) + (heat_demand * 0.4) + (sim_rain * 0.05),
    )
)

c1, c2, c3 = st.columns(3)
c1.metric("Energy Scavenged", f"{saved_kwh:.4f} kWh", delta="↑ Circular Heat")
c2.metric("CO₂ Avoided", f"{co2_avoided:.4f} kg", delta="↓ vs Grid HVAC")
c3.metric("Sustainability Score", f"{sustainability_score}/100")

st.markdown("---")

# ---------------------------------------------------------------------------
# Nyra Phase 1–5 System Status
# ---------------------------------------------------------------------------
st.subheader("🏗️ Living Machine System Status (Nyra Phase 1–5)")

machine_status = None
state = None
server_state = None

try:
    r = httpx.get(f"{BACKEND}/system/living-machine/status", timeout=5.0)
    r.raise_for_status()
    machine_status = r.json()
    state = machine_status["living_machine_state"]
    server_state = machine_status["server_state"]
except Exception as e:
    st.error(f"Backend status error: {e}")

if state:
    capacity = float(state["thermal_capacity_used"])
    temp_c = float(state["foundation_temp_celsius"])
    opacity = int(state["smart_glass_opacity"])
    watts = float(state["server_heat_output_watts"])

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Phase 3: Foundation Temp", f"{temp_c:.1f}°C", delta=f"{capacity:.0f}% capacity")
    g2.metric(
        "Phase 4: Server Heat Captured",
        f"{watts:.1f} W",
        delta=f"{state['cooling_energy_reduction']:.0f}% cooling reduction",
    )
    g3.metric("Phase 5: Smart Glass Opacity", f"{opacity}%", delta="Active" if opacity > 0 else "Passive")
    g4.metric(
        "Outside Temp",
        f"{state['outside_temp']:.0f}°F" if state.get("outside_temp") else "N/A",
        delta=state.get("weather_description", ""),
    )

    st.progress(min(100, int(capacity)) / 100)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("### Phase 1: Bio-Sponge")
        st.write(f"Runoff velocity reduction: **{state['roof_moss_velocity_reduction']}%**")
        st.write(f"N capture: **{state['nitrogen_capture_rate']} mg/L**")
        st.write(f"Heavy metal filtration: **{state['heavy_metal_filtration']}%**")

    with p2:
        st.markdown("### Phase 2: Vertical Spine")
        st.write(f"pH: **{state['ph_level']}**")
        st.write(f"TDS: **{state['tds_ppm']} ppm**")
        st.write(f"Flow: **{state['flow_rate']} L/min**")
        st.write(f"O₂: **{state['spine_oxygenation_level']} mg/L**")

    with p3:
        st.markdown("### Phase 3–5: Feedback Loop")
        st.write(f"Saturated: **{state['is_saturated']}** (24°C trigger)")
        st.write(f"Seismic dampeners: **{state['seismic_dampener_status']}**")
        st.write(f"Solar gain (est): **{state['solar_gain_watts']:.0f} W**")

    st.markdown("## 🔄 Circular Heat Flow (Live)")
    flow_cols = st.columns(5)
    flow_cols[0].markdown("**Servers**\n\n🔥 heat output")
    flow_cols[1].markdown("➡️\n\n**Copper Coils**\n\n(Phase 4)")
    flow_cols[2].markdown("➡️\n\n**Foundation Reservoir**\n\n(Phase 3)")
    flow_cols[3].markdown("➡️\n\n**Radiant / Hot Water**\n\n(useful heat)")
    flow_cols[4].markdown("↩️\n\n**Smart Glass**\n\n(Phase 5)")

    with st.expander("🔍 System Interpretation"):
        st.info(machine_status.get("interpretation", "No interpretation provided."))

st.markdown("---")

# ---------------------------------------------------------------------------
# Natural language command (if your /voice/intent exists)
# ---------------------------------------------------------------------------
st.subheader("🧠 Aetheris Command & Neural Status")
command_input = st.text_input("Input sensory state (e.g., 'User shivering', 'Prioritize PCM Soak'):")

if command_input:
    with st.spinner("Thinking..."):
        try:
            r = httpx.post(f"{BACKEND}/voice/intent", params={"user_text": command_input}, timeout=15.0)
            r.raise_for_status()
            res = r.json()
            with st.container(border=True):
                st.markdown(f"**Input:** `{command_input}`")
                st.markdown(f"**Aetheris Response:** {res.get('response', 'No response')}")
        except Exception as e:
            st.error(f"Command error: {e}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Predictive plan (safe fallback supported by backend)
# ---------------------------------------------------------------------------
st.subheader("🗓️ 72-Hour Thermal Management Plan")

if st.button("Generate Fresh Predictive Plan"):
    with st.spinner("Generating plan..."):
        try:
            r = httpx.get(f"{BACKEND}/plan/72h", timeout=60.0)
            r.raise_for_status()
            plan_res = r.json()

            if plan_res.get("plan_source") != "gemini":
                st.warning("AI planning unavailable, showing fallback plan.")

            with st.container(border=True):
                st.markdown(plan_res.get("plan", "No plan generated."))
        except Exception as e:
            st.error(f"Planning error: {e}")

# ---------------------------------------------------------------------------
# Auto refresh (makes demo feel alive)
# ---------------------------------------------------------------------------
if auto_refresh:
    time.sleep(2)
    st.rerun()

st.markdown("---")
st.caption("Aetheris OS v1.0 - The Living Machine | Built for a sustainable future")
