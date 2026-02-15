#!/bin/bash

echo "🏗️  Aetheris OS - Easy Setup"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "🔑 Creating .env file..."
    cat > .env << EOF
GEMINI_API_KEY=your_gemini_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
ACTIAN_HOST=127.0.0.1
ACTIAN_PORT=50051
MONGO_URI=mongodb://localhost:27017
BUILDING_LAT=37.7749
BUILDING_LON=-122.4194
EOF
    echo "⚠️  Please edit backend/.env and add your API keys!"
    echo "   Get Gemini key: https://aistudio.google.com/"
    echo "   Get Weather key: https://openweathermap.org/api"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
cd ..
docker compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: cd backend && source venv/bin/activate"
echo "3. Run: python main.py"
echo "4. In new terminal: streamlit run dashboard.py"
