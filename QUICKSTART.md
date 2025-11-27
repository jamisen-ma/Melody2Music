# 🚀 Quickstart Guide

Get Melody2Music up and running in 5 minutes!

## Prerequisites

- Python 3.12+ installed
- ~2GB free disk space for models
- Optional: CUDA GPU for faster processing

## Step 1: Setup Backend (2 minutes)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this will download models on first run)
pip install -r requirements.txt
```

## Step 2: Start Backend Server (1 minute)

### Option A: Using the startup script
```bash
./run.sh
```

### Option B: Manual start
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for the message: **"Backend initialization complete!"**

This may take a minute on first run as models are downloaded.

## Step 3: Open Frontend (1 minute)

Open `frontend/public/index.html` in your web browser, or:

```bash
cd frontend/public
python -m http.server 3000
```

Then open: **http://localhost:3000**

## Step 4: Generate Music! (1 minute)

1. Click **"🎤 Record Audio"** and hum a melody (or upload an audio file)
2. Choose your preferred **genre**, **mood**, and **instruments**
3. Click **"✨ Generate Music"**
4. Wait 15-30 seconds
5. Listen to your AI-generated music! 🎵

## Test with cURL

```bash
# Test the API directly
curl -X POST http://localhost:8000/api/generate-music \
  -F "file=@your_humming.wav" \
  -F "genre=pop" \
  -F "mood=upbeat" \
  -F "instruments=piano" \
  -o output.wav
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "CUDA out of memory"
The system will automatically fall back to CPU. For CPU-only:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Backend not responding
Check if it's running:
```bash
curl http://localhost:8000/health
```

### Port already in use
Change the port:
```bash
uvicorn app.main:app --port 8001
```

Then update `API_BASE_URL` in `frontend/public/app.js`

## Example Inputs

Good humming practices:
- Clear, steady humming (no words)
- 3-15 seconds duration
- Comfortable pitch range
- Minimal background noise
- Record in a quiet environment

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Explore the `/docs` endpoint for all API features
- Try different genre/mood combinations
- Experiment with longer melodies

## Support

Having issues? Check:
1. Python version: `python --version` (should be 3.12+)
2. Backend logs for error messages
3. Browser console for frontend errors

---

Happy music making! 🎵✨

