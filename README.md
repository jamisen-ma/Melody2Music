# 🎵 Melody2Music: Humming-to-Song Generation System

Transform your humming into beautiful instrumental music using state-of-the-art AI models.

## Overview

Melody2Music is a complete system that converts a user's humming into a fully-produced instrumental track. It combines audio preprocessing, pitch tracking with CREPE, and generative audio synthesis with Meta's MusicGen to create melody-conditioned music.

## Features

- **Audio Preprocessing**: Clean and normalize input audio using Torchaudio
- **Pitch Tracking**: Extract melody using CREPE (Convolutional Representation for Pitch Estimation)
- **Music Generation**: Generate instrumental tracks conditioned on extracted melody using MusicGen
- **Style Control**: Customize genre, mood, and instrumentation via text prompts
- **FastAPI Backend**: RESTful API for audio processing and music generation
- **Modern Web UI**: Upload audio files or record directly in browser
- **Real-time Processing**: Fast inference with GPU support

## Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI**: Modern, fast web framework for building APIs
- **PyTorch & Torchaudio**: Audio processing and model inference
- **CREPE (torchcrepe)**: State-of-the-art pitch tracking
- **MusicGen (audiocraft)**: Meta's music generation model
- **Librosa**: Additional audio analysis features

### Frontend
- **HTML5/CSS3/JavaScript**: Modern, responsive web interface
- **Web Audio API**: In-browser audio recording

## Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Optional: CUDA-capable GPU for faster processing

### Setup

1. **Clone the repository**
```bash
cd Melody2Music
```

2. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

Note: First installation will download MusicGen models (~1.5GB for melody model)

4. **Create necessary directories**
```bash
mkdir -p uploads outputs
```

## Usage

### Starting the Backend

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Opening the Frontend

Simply open `frontend/public/index.html` in a web browser, or serve it with a simple HTTP server:

```bash
cd frontend/public
python -m http.server 3000
```

Then navigate to `http://localhost:3000`

### Using the Application

1. **Upload or Record Audio**
   - Click "Choose an audio file" to upload a recording
   - Or click "Record Audio" to record directly in browser
   - Supported formats: WAV, MP3, OGG, etc.

2. **Customize Style**
   - Select genre (Pop, Jazz, Classical, etc.)
   - Choose mood (Upbeat, Melancholic, Energetic, etc.)
   - Specify instruments (e.g., "piano and guitar")
   - Set duration (optional, defaults to input length)

3. **Generate Music**
   - Click "Generate Music"
   - Wait for processing (typically 10-30 seconds)
   - Listen to your generated track!

4. **Download**
   - Click "Download" to save the generated audio

## API Endpoints

### `POST /api/generate-music`
Complete pipeline: upload humming, extract melody, generate music

**Parameters:**
- `file`: Audio file (multipart/form-data)
- `genre`: Musical genre (string)
- `mood`: Mood/emotion (string)
- `instruments`: Desired instruments (string)
- `duration`: Duration in seconds (optional, float)

**Response:**
```json
{
  "message": "Music generated successfully",
  "audio_url": "/api/download/xxx_output.wav",
  "melody_features": {
    "duration": 5.2,
    "tempo": 120,
    "pitch_mean": 220.5,
    "pitch_range": 150.3,
    "avg_confidence": 0.85
  }
}
```

### `POST /api/extract-melody`
Extract melody features from audio without generation

### `POST /api/generate-text-only`
Generate music from text description only (no melody conditioning)

### `GET /api/download/{filename}`
Download generated audio file

### `GET /health`
Check backend service status

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (HTML/JS)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│        FastAPI Backend              │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │   Audio Processor Module     │  │
│  │  - Load & preprocess audio   │  │
│  │  - CREPE pitch extraction    │  │
│  │  - Feature analysis          │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Music Generator Module     │  │
│  │  - MusicGen model loading    │  │
│  │  - Melody conditioning       │  │
│  │  - Style-guided generation   │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## How It Works

1. **Audio Upload**: User uploads or records humming audio
2. **Preprocessing**: Audio is converted to mono, resampled to 16kHz, and normalized
3. **Pitch Extraction**: CREPE model extracts pitch contour (fundamental frequency over time)
4. **Feature Analysis**: Calculate tempo, pitch statistics, and confidence scores
5. **Style Prompt**: Combine user preferences into a text prompt for MusicGen
6. **Music Generation**: MusicGen generates audio conditioned on:
   - The extracted melody/pitch contour
   - The style description text prompt
7. **Post-processing**: Normalize and save the generated audio
8. **Delivery**: Return audio file and analysis to user

## Model Details

### CREPE (Pitch Tracking)
- Convolutional neural network for pitch estimation
- Trained on diverse musical datasets
- Outputs pitch confidence scores
- Viterbi decoding for temporal smoothness

### MusicGen (Music Generation)
- Meta's transformer-based music generation model
- Trained on 20,000 hours of licensed music
- Supports melody conditioning via chromagram
- Text-guided style control
- 32kHz stereo output

## Performance

- **Pitch Extraction**: ~0.5-1 second for 10s audio
- **Music Generation**: ~10-30 seconds for 10s output (with GPU)
- **Total Pipeline**: ~15-40 seconds end-to-end

GPU acceleration significantly improves generation speed (5-10x faster).

## Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.12+)
- First run downloads models automatically, may take a few minutes

### CUDA/GPU errors
- Install PyTorch with CUDA support: Visit [pytorch.org](https://pytorch.org)
- Or use CPU-only (slower): Models will automatically fall back to CPU

### Poor melody extraction
- Ensure clean, clear humming (minimal background noise)
- Hum steadily in a comfortable vocal range
- Avoid very short audio (less than 2 seconds)

### Low-quality output
- Try different genre/mood/instrument combinations
- Use longer, clearer input audio
- Adjust temperature parameter for more variation

## Future Improvements

- [ ] Support for longer audio generation (>30s)
- [ ] Multi-track generation (bass, drums, melody)
- [ ] Real-time streaming generation
- [ ] User authentication and history
- [ ] Fine-tuned models on specific genres
- [ ] MIDI export functionality
- [ ] Mobile app

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is for educational and research purposes. Please check the licenses for:
- MusicGen/AudioCraft: [AudioCraft License](https://github.com/facebookresearch/audiocraft)
- CREPE: [CREPE License](https://github.com/maxrmorrison/torchcrepe)

## Acknowledgments

- Meta AI for MusicGen/AudioCraft
- Kim et al. for CREPE pitch tracker
- FastAPI and PyTorch communities

## Contact

Built with ❤️ using Python, Torchaudio, CREPE, MusicGen, and FastAPI

---

**Note**: This system requires significant computational resources. For production use, consider cloud deployment with GPU instances.

