import uuid, os, psutil, platform, httpx, grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dotenv import load_dotenv
from numpy import dot
from numpy.linalg import norm

load_dotenv()

import vdss_pb2, vdss_pb2_grpc

app = FastAPI(title="Aetheris OS - The Living Machine")

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = mongo_client.aetheris
materials_collection = db.materials
system_logs = db.system_logs

LOCATION = {
    "lat": float(os.getenv("BUILDING_LAT", 37.7749)),
    "lon": float(os.getenv("BUILDING_LON", -122.4194)),
}

# ---------------------------------------------------------------------------
# DEMO / SIM HEAT (judge-wow)
# ---------------------------------------------------------------------------
DEMO_HEAT_WATTS = 0.0
DEMO_HEAT_DECAY_PER_SEC = 2.0
LAST_DEMO_TS = datetime.now(timezone.utc)

# ===========================================================================
# MODELS
# ===========================================================================

class LivingMachineState(BaseModel):
    """Complete system telemetry for Aetheris Living Machine"""

    # Phase 1: Bio-Sponge (Bryum argenteum moss layer)
    roof_moss_velocity_reduction: float = 60.0
    nitrogen_capture_rate: float = 0.0
    heavy_metal_filtration: float = 0.0

    # Phase 2: Vertical Spine (Gravity Highway)
    ph_level: float = 6.8
    tds_ppm: int = 45
    flow_rate: float = 2.4
    spine_oxygenation_level: float = 8.5

    # Phase 3: Foundation Reservoir (Thermal Battery)
    foundation_temp_celsius: float = 18.5
    thermal_capacity_used: float = 0.0
    is_saturated: bool = False
    seismic_dampener_status: str = "nominal"

    # Phase 4: Liquid Loop (Server Heat Sink)
    server_heat_output_watts: float = 0.0
    cooling_energy_reduction: float = 85.0
    copper_coil_efficiency: float = 92.0

    # Phase 5: Smart Glass Control
    smart_glass_opacity: int = 0
    solar_gain_watts: float = 0.0

    # Environmental Context
    outside_temp: Optional[float] = None
    weather_description: Optional[str] = None


class MaterialRequest(BaseModel):
    name: str
    description: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class WeatherForecast(BaseModel):
    timestamp: datetime
    temp: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    clouds: int


class DemoHeatRequest(BaseModel):
    watts: float = 80.0
    seconds: int = 45


# ===========================================================================
# HELPERS
# ===========================================================================

def get_embedding(text: str):
    """Generates 3072-dim vector using Gemini embedding model."""
    result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return result.embeddings[0].values


async def get_weather_forecast() -> List[WeatherForecast]:
    """Fetch 72-hour weather forecast (OpenWeather 3h blocks -> 24 blocks ~= 72h)."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": LOCATION["lat"],
        "lon": LOCATION["lon"],
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "imperial",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()

    forecasts: List[WeatherForecast] = []
    for item in data.get("list", [])[:24]:
        forecasts.append(
            WeatherForecast(
                timestamp=datetime.fromtimestamp(item["dt"], tz=timezone.utc),
                temp=item["main"]["temp"],
                feels_like=item["main"]["feels_like"],
                humidity=item["main"]["humidity"],
                description=item["weather"][0]["description"],
                wind_speed=item["wind"]["speed"],
                clouds=item["clouds"]["all"],
            )
        )
    return forecasts


def _apply_demo_decay() -> None:
    """Decay DEMO_HEAT_WATTS over time so the spike feels temporary."""
    global DEMO_HEAT_WATTS, LAST_DEMO_TS
    now = datetime.now(timezone.utc)
    dt = (now - LAST_DEMO_TS).total_seconds()
    LAST_DEMO_TS = now
    if dt <= 0:
        return
    DEMO_HEAT_WATTS = max(0.0, DEMO_HEAT_WATTS - (DEMO_HEAT_DECAY_PER_SEC * dt))


def _smart_glass_opacity(temp_c: float) -> int:
    """
    Nyra Phase 5:
    - >= 24°C => 100%
    - <= 22°C => 0%
    - 22–24°C => ramp
    """
    if temp_c >= 24.0:
        return 100
    if temp_c <= 22.0:
        return 0
    return int(((temp_c - 22.0) / (24.0 - 22.0)) * 100)


def get_server_thermal_state() -> Dict:
    """Monitor server thermal output for Liquid Loop integration."""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_temp = None

    if platform.system() == "Linux":
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps and temps["coretemp"]:
                cpu_temp = temps["coretemp"][0].current
            elif "cpu_thermal" in temps and temps["cpu_thermal"]:
                cpu_temp = temps["cpu_thermal"][0].current
        except Exception:
            pass

    memory = psutil.virtual_memory()

    _apply_demo_decay()
    base_heat = (cpu_percent / 100) * 65.0
    estimated_heat_watts = base_heat + DEMO_HEAT_WATTS

    # Phase 4: 85% cooling energy reduction (demo math)
    traditional_cooling_watts = estimated_heat_watts / 0.15
    energy_saved = traditional_cooling_watts * 0.85

    return {
        "cpu_usage_percent": cpu_percent,
        "cpu_temp_celsius": cpu_temp,
        "memory_percent": memory.percent,
        "server_heat_output_watts": estimated_heat_watts,
        "traditional_cooling_watts": traditional_cooling_watts,
        "energy_saved_watts": energy_saved,
        "cooling_efficiency": "85% reduction vs grid AC",
        "demo_heat_watts": DEMO_HEAT_WATTS,
    }


def interpret_state(state: LivingMachineState) -> str:
    """Nyra's feedback loop interpretation."""
    if state.is_saturated:
        return (
            "🚨 CRITICAL: Foundation thermal battery saturated (24°C). "
            "Smart Glass engaged at 100% opacity to reduce solar gain. "
            "Consider activating supplemental heat dissipation or reducing compute."
        )
    if state.thermal_capacity_used > 75:
        return (
            "⚠️ WARNING: Thermal capacity above 75%. "
            "Prepare for Smart Glass ramp-up if temperature continues rising."
        )
    if state.server_heat_output_watts < 30:
        return (
            "✅ NOMINAL: Low server load. Foundation reservoir absorbing minimal heat. "
            "System in passive monitoring mode."
        )
    return (
        "✅ ACTIVE: Server heat being captured by Liquid Loop. "
        "Foundation thermal battery within optimal range. Circular heat strategy engaged."
    )


# ===========================================================================
# SYSTEM ENDPOINTS (Nyra Phase 1–5)
# ===========================================================================

@app.get("/system/living-machine/status")
async def get_living_machine_status():
    """Get complete Living Machine telemetry (Phase 1–5)."""

    # Weather
    forecasts = await get_weather_forecast()
    current_weather = forecasts[0] if forecasts else None

    # Server
    server_state = get_server_thermal_state()

    # Foundation thermal model (demo-friendly scaling)
    foundation_temp = 18.5 + (server_state["server_heat_output_watts"] * 0.08)
    thermal_capacity = ((foundation_temp - 18.5) / (24.0 - 18.5)) * 100
    thermal_capacity = max(0.0, min(100.0, thermal_capacity))

    # Smart Glass (Nyra Phase 5)
    opacity = _smart_glass_opacity(foundation_temp)

    # Solar gain estimate (simple demo)
    solar_gain = 0.0
    if current_weather:
        # more clouds => less solar gain; keep within reasonable demo bounds
        solar_gain = 1000.0 * (1.0 - (current_weather.clouds / 100.0))

    state = LivingMachineState(
        # Phase 1
        roof_moss_velocity_reduction=60.0,
        nitrogen_capture_rate=3.2,
        heavy_metal_filtration=72.0,

        # Phase 2
        ph_level=6.8,
        tds_ppm=45,
        flow_rate=2.4,
        spine_oxygenation_level=8.5,

        # Phase 3
        foundation_temp_celsius=foundation_temp,
        thermal_capacity_used=thermal_capacity,
        is_saturated=foundation_temp >= 24.0,
        seismic_dampener_status="nominal",

        # Phase 4
        server_heat_output_watts=server_state["server_heat_output_watts"],
        cooling_energy_reduction=85.0,
        copper_coil_efficiency=92.0,

        # Phase 5
        smart_glass_opacity=opacity,
        solar_gain_watts=solar_gain,

        # Environment
        outside_temp=current_weather.temp if current_weather else None,
        weather_description=current_weather.description if current_weather else None,
    )

    # Log
    await system_logs.insert_one(
        {
            **state.model_dump(),
            "timestamp": datetime.now(timezone.utc),
            "server_state": server_state,
        }
    )

    return {
        "living_machine_state": state,
        "server_state": server_state,
        "interpretation": interpret_state(state),
    }


@app.get("/system/circular-strategy")
async def circular_strategy_compat():
    """
    Backward-compatible endpoint for older dashboard calls.
    Mirrors the old structure but sources from the new Living Machine status.
    """
    status = await get_living_machine_status()
    lm: LivingMachineState = status["living_machine_state"]

    return {
        "server_state": status["server_state"],
        "weather": {
            "temp": lm.outside_temp,
            "description": lm.weather_description,
        },
        "living_machine_state": lm,
        "interpretation": status["interpretation"],
    }


@app.post("/system/adapt")
async def run_adaptation(state: LivingMachineState):
    """
    Nyra's Automated Feedback Loop
    Triggers Smart-Glass if foundation hits max thermal capacity
    """

    if state.foundation_temp_celsius >= 24.0:
        state.is_saturated = True
        state.smart_glass_opacity = 100
        action = (
            "CRITICAL: Thermal saturation reached. Engaging Smart-Glass opacity "
            "at 100% to reduce solar gain."
        )

        alert_prompt = f"""AETHERIS ALERT: Foundation reservoir has reached thermal capacity (24°C).

System Response:
- Smart Glass: 100% opacity activated
- Solar Gain Reduction: Estimated {state.solar_gain_watts}W blocked
- Recommendation: Consider opening thermal vent or reducing server workload

Provide a brief operational recommendation."""

        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=alert_prompt,
            )
            action += f"\n\nAI Recommendation: {response.text}"
        except Exception as e:
            action += f"\n\nAI Recommendation unavailable: {str(e)}"

    else:
        # Use Nyra ramp (22–24°C) if foundation temp is provided properly.
        # If only thermal_capacity_used is provided, keep original proportional fallback.
        state.smart_glass_opacity = _smart_glass_opacity(state.foundation_temp_celsius)
        action = (
            f"NOMINAL: Foundation at {state.foundation_temp_celsius:.1f}°C "
            f"({state.thermal_capacity_used:.1f}% capacity). "
            f"Smart-Glass at {state.smart_glass_opacity}%."
        )

    await system_logs.insert_one(
        {
            **state.model_dump(),
            "timestamp": datetime.now(timezone.utc),
            "action_taken": action,
        }
    )

    return {
        "action": action,
        "state": state,
        "phase_1_status": "Bio-Sponge active - 60% velocity reduction",
        "phase_2_status": f"Spine flow: {state.flow_rate}L/min, pH: {state.ph_level}",
        "phase_3_status": f"Foundation: {state.foundation_temp_celsius:.1f}°C",
        "phase_4_status": f"Liquid Loop: {state.cooling_energy_reduction}% cooling reduction",
    }


# ===========================================================================
# DEMO ENDPOINTS (judge button)
# ===========================================================================

@app.post("/demo/heat")
async def demo_heat(req: DemoHeatRequest):
    """Add simulated compute heat so the system visibly reacts."""
    global DEMO_HEAT_WATTS, DEMO_HEAT_DECAY_PER_SEC
    DEMO_HEAT_WATTS = max(0.0, float(req.watts))
    DEMO_HEAT_DECAY_PER_SEC = max(0.5, DEMO_HEAT_WATTS / max(10, int(req.seconds)))
    return {
        "status": "ok",
        "demo_heat_watts": DEMO_HEAT_WATTS,
        "decay_watts_per_sec": DEMO_HEAT_DECAY_PER_SEC,
    }


@app.post("/demo/reset")
async def demo_reset():
    """Reset demo heat to zero."""
    global DEMO_HEAT_WATTS
    DEMO_HEAT_WATTS = 0.0
    return {"status": "ok", "demo_heat_watts": DEMO_HEAT_WATTS}


# ===========================================================================
# MATERIALS (Vector Search)
# ===========================================================================

@app.post("/materials/upsert")
async def upsert_material(request: MaterialRequest):
    """Index building materials for semantic search."""
    try:
        vector_data = get_embedding(request.description)
        material_id = str(uuid.uuid4())

        material_doc = {
            "_id": material_id,
            "name": request.name,
            "description": request.description,
            "created_at": datetime.now(timezone.utc),
            "vector_stored": False,
        }
        await materials_collection.insert_one(material_doc)

        channel = grpc.aio.insecure_channel(
            f'{os.getenv("ACTIAN_HOST")}:{os.getenv("ACTIAN_PORT")}'
        )
        stub = vdss_pb2_grpc.VDSSServiceStub(channel)

        upsert_req = vdss_pb2.UpsertVectorRequest(
            collection_name="materials",
            vector_id=vdss_pb2.VectorIdentifier(uuid=material_id),
            vector=vdss_pb2.Vector(data=vector_data, dimension=3072),
        )

        await stub.UpsertVector(upsert_req)
        await channel.close()

        await materials_collection.update_one(
            {"_id": material_id},
            {"$set": {"vector_stored": True}},
        )

        return {"status": "success", "name": request.name, "id": material_id}

    except Exception as e:
        if "material_id" in locals():
            await materials_collection.delete_one({"_id": material_id})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/materials/search")
async def search_materials(request: SearchRequest):
    """Semantic material search (cosine similarity demo)."""
    try:
        query_vector = get_embedding(request.query)
        all_materials = await materials_collection.find({"vector_stored": True}).to_list(length=1000)

        def cosine_similarity(a, b):
            return dot(a, b) / (norm(a) * norm(b))

        scored_materials = []
        for material in all_materials:
            # NOTE: For true speed, store embeddings once and retrieve them.
            material_embedding = get_embedding(material["description"])
            score = cosine_similarity(query_vector, material_embedding)

            scored_materials.append(
                {
                    "id": material["_id"],
                    "name": material["name"],
                    "description": material["description"],
                    "score": float(score),
                }
            )

        scored_materials.sort(key=lambda x: x["score"], reverse=True)
        return {"query": request.query, "matches": scored_materials[: request.top_k]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/materials/list")
async def list_materials():
    """List all materials."""
    materials = await materials_collection.find().to_list(length=100)
    return {"count": len(materials), "materials": materials}


# ===========================================================================
# WEATHER + PLANNING
# ===========================================================================

@app.get("/weather/forecast")
async def get_forecast():
    """72-hour weather forecast."""
    try:
        forecasts = await get_weather_forecast()
        return {
            "location": LOCATION,
            "forecast_hours": len(forecasts) * 3,
            "forecasts": [f.model_dump() for f in forecasts],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@app.get("/plan/72h")
async def predictive_plan():
    """
    Generate AI-powered 72-hour thermal management plan.
    Includes safe fallback so demo never hard-fails if Gemini is down.
    """
    machine_status = await get_living_machine_status()
    state: LivingMachineState = machine_status["living_machine_state"]
    forecasts = await get_weather_forecast()

    prompt = f"""You are Aetheris OS managing a Living Machine building system.

CURRENT STATE:
Phase 1 (Bio-Sponge): {state.roof_moss_velocity_reduction}% runoff velocity reduction
Phase 2 (Spine): pH {state.ph_level}, TDS {state.tds_ppm}ppm, Flow {state.flow_rate}L/min
Phase 3 (Foundation): {state.foundation_temp_celsius:.2f}°C ({state.thermal_capacity_used:.1f}% capacity)
Phase 4 (Liquid Loop): {state.server_heat_output_watts:.1f}W server heat, {state.cooling_energy_reduction}% cooling reduction
Phase 5 (Smart Glass): {state.smart_glass_opacity}% opacity

WEATHER FORECAST (Next 24h):
{chr(10).join([f"- {f.timestamp.strftime('%a %I%p UTC')}: {f.temp:.0f}°F, {f.description}" for f in forecasts[:8]])}

TASK: Generate a 72-hour operational plan focusing on:
1. PCM Soak Strategy (when to absorb vs release thermal energy)
2. Grid Offset Optimization (minimize HVAC load)
3. Smart Glass activation timing
4. Server workload scheduling (run compute when heat is beneficial)

Return:
- Bullet plan
- 3-step action checklist
"""

    fallback_plan = f"""
### Fallback Plan (AI temporarily unavailable)

**Goal:** Keep foundation below **24°C**, maximize reuse of server heat, minimize grid HVAC.

**Next 24h**
- If outside temp < 60°F: route waste heat to radiant zones first, then to foundation reservoir.
- Keep Smart Glass at 0–30% unless foundation exceeds 75% capacity.
- Schedule heavy compute during the coldest window (night / early morning).

**24–72h**
- If forecast warms (solar gain increases): reduce compute at peak sun hours and pre-charge thermal battery earlier.
- If foundation > 75% capacity: begin heat shedding (venting / loop diversion) before reaching 24°C.
- Maintain minimum spine flow + pH monitoring to avoid stagnation.

**3-step checklist**
1. Check foundation capacity (%): {state.thermal_capacity_used:.0f}%
2. If capacity > 75%: increase Smart Glass opacity + reduce compute peak hours
3. If outside temp < 60°F: run compute and direct heat to comfort/hot-water zones
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        plan_text = response.text
        plan_source = "gemini"
    except Exception as e:
        plan_text = fallback_plan + f"\n\n**Error:** {str(e)}"
        plan_source = "fallback"

    return {
        "status": "Living Machine operational",
        "plan_source": plan_source,
        "current_state": state,
        "plan": plan_text,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ===========================================================================
# VOICE INTENT (FIXED)
# ===========================================================================

@app.post("/voice/intent")
async def process_voice_intent(user_text: str):
    """Natural language command processing"""
    try:
        print(f"🔵 VOICE INTENT: {user_text}")

        # Get current system state
        machine_status = await get_living_machine_status()
        print("✅ Got machine status")

        state_model: LivingMachineState = machine_status["living_machine_state"]
        print(f"✅ Got state model: {state_model}")

        # Convert once -> safe dict usage everywhere below
        state = state_model.model_dump()
        print("✅ Dumped state to dict")

        # Format outside temp safely
        outside_temp = state.get("outside_temp")
        outside_temp_str = f"{outside_temp:.0f}°F" if outside_temp is not None else "N/A"
        print(f"✅ Formatted temp: {outside_temp_str}")

        prompt = f"""You are Aetheris OS, the AI managing a Living Building system.

CURRENT SYSTEM STATE:
- Foundation Temperature: {state['foundation_temp_celsius']:.1f}°C ({state['thermal_capacity_used']:.1f}% capacity)
- Server Heat Output: {state['server_heat_output_watts']:.1f}W
- Smart Glass Opacity: {state['smart_glass_opacity']}%
- Outside Temperature: {outside_temp_str}
- System Status: {'SATURATED' if state['is_saturated'] else 'NOMINAL'}

USER INPUT: "{user_text}"

TASK: Respond as the building AI explaining what action you're taking. Be conversational and specific. Reference actual systems by name. Keep response to 2-3 sentences maximum."""

        print("✅ Calling Gemini...")
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        print("✅ Got Gemini response")

        return {
            "user_input": user_text,
            "response": response.text,
            "state_snapshot": state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        print(f"❌ VOICE INTENT ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice intent error: {str(e)}")


# ===========================================================================
# SERVER ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
