import uuid, os, psutil, platform, httpx, grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
import vdss_pb2, vdss_pb2_grpc # Ensure these are in your path

app = FastAPI(title="Aetheris OS - Intelligence Layer")
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = mongo_client.aetheris
materials_collection = db.materials

LOCATION = {"lat": float(os.getenv("BUILDING_LAT", 37.7749)), "lon": float(os.getenv("BUILDING_LON", -122.4194))}

class WeatherForecast(BaseModel):
    timestamp: datetime
    temp: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    clouds: int

def get_server_thermal_state() -> Dict:
    cpu_percent = psutil.cpu_percent(interval=1)
    estimated_heat_watts = (cpu_percent / 100) * 65 # Your 65W TDP "Crack"
    return {
        "cpu_usage_percent": cpu_percent,
        "estimated_heat_output_watts": estimated_heat_watts,
        "thermal_state": "high" if cpu_percent > 70 else "medium" if cpu_percent > 40 else "low"
    }

async def get_weather_forecast() -> List[WeatherForecast]:
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": LOCATION["lat"], "lon": LOCATION["lon"], "appid": os.getenv("OPENWEATHER_API_KEY"), "units": "imperial"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    return [WeatherForecast(timestamp=datetime.fromtimestamp(i["dt"], tz=timezone.utc), temp=i["main"]["temp"],
                            feels_like=i["main"]["feels_like"], humidity=i["main"]["humidity"],
                            description=i["weather"][0]["description"], wind_speed=i["wind"]["speed"],
                            clouds=i["clouds"]["all"]) for i in data["list"][:40]]

@app.get("/plan/72h")
async def predictive_plan():
    forecasts = await get_weather_forecast()
    summary = "\n".join([f"- {f.timestamp.strftime('%a %I%p')}: {f.temp:.0f}F, {f.description}" for f in forecasts])
    
    prompt = f"""You are Aetheris OS. Use this 5-day weather: {summary}
    STRICT OUTPUT FORMAT for each 6-hour block:
    1. OUTDOOR: [Temp] | [Condition]
    2. ACTUATORS: Hydra Loop: [Int%] | Radiant Floor: [Int%] | Blinds: [OPEN/CLOSED]
    3. REASONING: 1 sentence explaining the PCM soak or Grid offset.
    RULES: BLINDS logic: Close if < 50F and overcast. Open only for PCM soak if sun is present."""

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt,
        config={'temperature': 0.0, 'top_p': 0.1} # Forces consistency
    )
    return {"plan": {"plan": response.text}}

@app.post("/voice/intent")
async def voice_intent(user_text: str):
    thermal = get_server_thermal_state()
    prompt = f"User says: '{user_text}'. As Aetheris OS, respond in 2 sentences acknowledging their need and explaining how you're using the server's {thermal['estimated_heat_output_watts']:.1f}W to help."
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return {"response": response.text}

@app.get("/system/circular-strategy")
async def circular_strategy():
    thermal = get_server_thermal_state()
    forecasts = await get_weather_forecast()
    return {"server_state": thermal, "weather": forecasts[0].model_dump() if forecasts else None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
