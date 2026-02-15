# 🏗️ Aetheris OS - Autonomous Living Building System

An AI-powered circular engineering system that treats server waste heat as a building resource, enabling predictive thermal management and semantic intelligence.

![Aetheris OS Dashboard](https://img.shields.io/badge/Status-Operational-green) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- **Semantic Material Search**: Understand building systems by concept, not keywords (60-78% accuracy)
- **Circular Heat Management**: Server heat → building resource (not waste)
- **72-Hour Predictive Planning**: AI-generated thermal strategies based on weather
- **Natural Language Control**: "User shivering" → AI responds with heating strategy
- **Real-time Monitoring**: Server thermals, weather, system status

## 🎯 What Makes This Special

Traditional "smart buildings" waste datacenter heat through cooling systems. Aetheris OS integrates the AI server into the building's thermal ecosystem:

- Server generates heat during AI computations
- Heat is captured by Hydra Cooling Loop
- Routed to space heating, hot water, or thermal storage
- AI schedules heavy compute when heat is beneficial

**Result**: AI infrastructure becomes part of the solution, not the problem.

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    AETHERIS OS                          │
├─────────────────────────────────────────────────────────┤
│  Streamlit Dashboard ──→ FastAPI Backend               │
│       ↓                        ↓                         │
│  User Intent    ──→    Gemini AI (3072-dim vectors)    │
│                              ↓                           │
│              Actian VectorAI + MongoDB                  │
│                              ↓                           │
│          Circular Strategy Generation                   │
└─────────────────────────────────────────────────────────┘
```

## 📦 Tech Stack

- **AI**: Google Gemini (text-embedding-004, gemini-2.0-flash)
- **Vector DB**: Actian VectorAI (HNSW index)
- **Metadata**: MongoDB
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Weather**: OpenWeatherMap API
- **Deployment**: Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Divijanand/Aetheris-OS.git
cd aetheris-os
```

### 2. Set Up Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys

Create `backend/.env`:
```env
GEMINI_API_KEY=your_API_key_here
OPENWEATHER_API_KEY=f58be8b80cfd96af86e0eed56e6136fe
ACTIAN_HOST=127.0.0.1
ACTIAN_PORT=50051
MONGO_URI=mongodb://localhost:27017
BUILDING_LAT=37.7749
BUILDING_LON=-122.4194
```

**Get API Keys:**
- Gemini: https://aistudio.google.com/ (Free $300 credits)
- OpenWeather: https://openweathermap.org/api (Free tier)

### 4. Start Services
```bash
# Start Docker containers
docker compose up -d

# Verify containers are running
docker ps
```

### 5. Start Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

Backend runs on: http://localhost:8000

### 6. Start Dashboard (New Terminal)
```bash
cd backend
source venv/bin/activate
streamlit run dashboard.py
```

Dashboard runs on: http://localhost:8501

## 🎮 Usage Examples

### Natural Language Control
```
Input: "User is cold"
→ AI activates radiant floor heating, routes server heat to space heating

Input: "Prioritize hot water"
→ AI redirects thermal flow to Foundation Cistern heat exchanger
```

### Semantic Material Search
```
Query: "liquid cooling systems"
→ Finds: Hydra Cooling Loop (74.5% match)

Query: "passive solar heating"  
→ Finds: Solar Thermal Collector (78% match)
```

### Weather-Based Planning
```
GET /plan/72h
→ Returns hour-by-hour thermal management strategy for next 3 days
```

## 📊 API Endpoints

### Materials Management
- `POST /materials/upsert` - Index new building system
- `POST /materials/search` - Semantic search
- `GET /materials/list` - List all systems

### Thermal Management  
- `GET /system/thermal` - Current server thermal state
- `GET /system/circular-strategy` - AI circular engineering plan
- `POST /compute/schedule` - Schedule compute tasks

### Weather & Planning
- `GET /weather/forecast` - 72-hour weather forecast
- `GET /plan/72h` - AI-generated thermal plan

## 🔧 Development

### Add New Building Systems
```python
# Use the dashboard or API
POST http://localhost:8000/materials/upsert
{
  "name": "Green Roof System",
  "description": "Living vegetation roof for insulation and stormwater"
}
```

### Run Tests
```bash
cd backend
pytest
```

### Check Logs
```bash
# Backend logs
tail -f backend/logs/aetheris.log

# Docker logs
docker logs aetheris-os-actian-1
docker logs aetheris-os-mongo-1
```

## 📈 Performance Metrics

- **Semantic Accuracy**: 60-78% concept matching
- **API Response Time**: ~2-3 seconds per query
- **Vector Dimensions**: 3,072
- **Indexed Systems**: 13+ building components
- **Cost**: ~$0.10/day on Google Cloud free credits

## 🌍 Environmental Impact

Current system (low server load):
- Energy Scavenged: 0.3 kWh
- CO2 Avoided: 0.1 kg
- Sustainability Score: 17/100

*Scales with server workload and building size*

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Google Gemini for semantic AI
- Actian VectorAI for high-performance vector search
- OpenWeatherMap for weather data
- SFSU CS Department for support

## 📧 Contact

**Divij Anand** - Computer Science & Business Analytics, SFSU
**Nyra Oeun**   - Interior Design & Architecture, SFSU
Project Link: https://github.com/Divijanand/Aetheris-OS.git

---

*Built with ❤️ for a sustainable future*
