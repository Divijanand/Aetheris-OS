# 🏗️ Aetheris OS - Living Building Intelligence Layer

An AI-powered semantic intelligence system for predictive building management.

## 🎯 What It Does

Aetheris OS gives your building a **semantic memory** - it understands concepts, not just keywords. The system can:

- **Understand Materials**: "liquid based heat management" → Hydra Cooling Loop (74.5% match)
- **Semantic Search**: Find systems by concept, not exact wording
- **Weather Prediction**: Generate 72-hour thermal management plans
- **Self-Awareness**: The building "knows" its own components and their purposes

## 🧠 Architecture
┌─────────────────────────────────────────────────────────┐
│                    AETHERIS OS                          │
│              Intelligence Layer v1.0                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Gemini AI  │  │  Actian      │  │  MongoDB    │  │
│  │  3072-dim    │→ │  VectorAI    │→ │  Metadata   │  │
│  │  Embeddings  │  │  Similarity  │  │  Storage    │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│         ↓                   ↓                ↓          │
│  ┌─────────────────────────────────────────────────┐  │
│  │           FastAPI REST Endpoints                 │  │
│  │  /materials/upsert  |  /materials/search         │  │
│  │  /weather/forecast  |  /plan/72h                 │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📊 System Stats

- **Materials Indexed**: 5 building systems
- **Semantic Accuracy**: 62-78% similarity matching
- **Vector Dimensions**: 3,072
- **Response Time**: ~2-3 seconds per query
- **API Calls**: Unlimited (self-hosted)

## 🚀 Quick Start

### 1. Start Services
```bash
cd ~/aetheris-os
docker compose up -d
```

### 2. Activate Environment
```bash
cd backend
source venv/bin/activate
```

### 3. Run Server
```bash
python main.py
```

### 4. Test Semantic Search
```powershell
$searchBody = @{query="cooling water system"; top_k=3} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/materials/search" -Method Post -Body $searchBody -ContentType "application/json"
```

## 🌤️ Weather Integration

Get AI-generated thermal management plans:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/plan/72h" -Method Get
```

The system analyzes 72-hour weather forecasts and recommends:
- Which systems to activate/deactivate
- Intensity levels (0-100%)
- Reasoning based on temperature, humidity, cloud cover

## 📦 Indexed Systems

1. **Smart Tint Glazing** - Electrochromic glass for thermal management
2. **Hydra Cooling Loop** - Liquid cooling using Foundation Cistern
3. **Living Water Filter** - Biological filtration for Active Gutter
4. **Solar Thermal Collector** - Rooftop panels for passive heating

## 🧪 Semantic Intelligence Examples

Query: "heat control for windows" → **Smart Tint Glazing** (72.4%)
Query: "liquid based heat management" → **Hydra Cooling Loop** (74.5%)
Query: "biological water cleaning" → **Living Water Filter** (74.4%)

## 🔧 Tech Stack

- **AI**: Google Gemini (text-embedding-004, gemini-2.0-flash-exp)
- **Vector DB**: Actian VectorAI (HNSW index, FAISS driver)
- **Metadata**: MongoDB
- **API**: FastAPI + Uvicorn
- **Weather**: OpenWeatherMap API

## 📁 Project Structure
```
aetheris-os/
├── backend/
│   ├── main.py              # Core application
│   ├── vdss.proto           # gRPC protocol
│   ├── .env                 # API keys (gitignored)
│   └── venv/                # Python environment
├── docker-compose.yml       # Container orchestration
└── README.md               # This file
```

## 🔑 Environment Variables

Create `backend/.env`:
```
GEMINI_API_KEY=your_gemini_key
OPENWEATHER_API_KEY=your_weather_key
ACTIAN_HOST=127.0.0.1
ACTIAN_PORT=50051
MONGO_URI=mongodb://localhost:27017
BUILDING_LAT=37.7749
BUILDING_LON=-122.4194
```

## 🎯 Future Enhancements

- [ ] Real-time sensor integration
- [ ] Multi-building coordination
- [ ] Energy cost optimization
- [ ] Occupancy-based adjustments
- [ ] Historical pattern learning

## 📝 License

Built with ❤️ for the Living Machine
