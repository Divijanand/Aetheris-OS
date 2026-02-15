# 🚀 Aetheris OS - Setup Without Docker

If you don't have Docker installed, you can still run Aetheris OS using cloud-hosted databases.

## Alternative Setup (No Docker Required)

### 1. Use MongoDB Atlas (Free)

Instead of local MongoDB, use free cloud MongoDB:

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Create free cluster
3. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
4. Update `.env`:
```
   MONGO_URI=mongodb+srv://your-connection-string-here
```

### 2. Skip Actian VectorAI (Simplified Mode)

The system can run without Actian by using MongoDB for storage only:

Update `backend/main.py` - comment out Actian-related code (search for `grpc.aio.insecure_channel`)

**Note:** Semantic search will be slower but still functional.

### 3. Install Python Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux  
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure API Keys

Edit `backend/.env`:
```
GEMINI_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
MONGO_URI=your_mongodb_atlas_uri
```

### 5. Run Application
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Dashboard
streamlit run dashboard.py
```

## Troubleshooting

**"ModuleNotFoundError"**: Run `pip install -r requirements.txt`
**"Connection refused"**: Check if MongoDB Atlas URI is correct
**"API key invalid"**: Verify keys in `.env` file

Still stuck? Open an issue: https://github.com/YOUR_USERNAME/aetheris-os/issues
