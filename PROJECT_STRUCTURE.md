# Project Structure

```
Melody2Music/
│
├── README.md                      # Main project documentation
├── QUICKSTART.md                  # Quick setup guide
├── PROJECT_STRUCTURE.md           # This file
├── .gitignore                     # Git ignore rules
│
├── backend/                       # Python FastAPI backend
│   ├── requirements.txt           # Python dependencies
│   ├── run.sh                     # Startup script (executable)
│   ├── test_api.py               # API testing script
│   │
│   ├── app/                       # Application code
│   │   ├── __init__.py           # Package initialization
│   │   ├── main.py               # FastAPI app & endpoints
│   │   ├── audio_processor.py    # CREPE pitch extraction
│   │   ├── music_generator.py    # MusicGen wrapper
│   │   └── config.py             # Configuration settings
│   │
│   ├── uploads/                   # Temporary uploaded files
│   │   └── .gitkeep
│   │
│   ├── outputs/                   # Generated audio files
│   │   └── .gitkeep
│   │
│   └── venv/                      # Virtual environment (created on setup)
│
└── frontend/                      # Web frontend
    ├── public/                    # Static files
    │   ├── index.html            # Main HTML page
    │   ├── style.css             # Styling
    │   └── app.js                # Frontend JavaScript
    │
    └── src/                       # Source files (if using React/build tools)
```

## Key Files

### Backend

#### `app/main.py`
- FastAPI application initialization
- API endpoints:
  - `POST /api/generate-music` - Complete pipeline
  - `POST /api/extract-melody` - Melody extraction only
  - `POST /api/generate-text-only` - Text-only generation
  - `GET /api/download/{filename}` - Download files
  - `GET /health` - Health check
- CORS middleware configuration
- Model initialization

#### `app/audio_processor.py`
- `AudioProcessor` class
- Audio loading and preprocessing (Torchaudio)
- CREPE pitch extraction
- Melody feature analysis
- Frequency to MIDI conversion
- Tempo detection (Librosa)

#### `app/music_generator.py`
- `MusicGenerator` class
- MusicGen model loading and management
- Text-conditioned generation
- Melody-conditioned generation
- Audio saving and post-processing
- Style prompt construction

#### `app/config.py`
- Configuration constants
- Environment variable loading
- Directory management
- Model parameters

### Frontend

#### `public/index.html`
- Main UI structure
- Upload/record interface
- Style customization form
- Audio player
- Feature display

#### `public/style.css`
- Modern, gradient design
- Responsive layout
- Form styling
- Progress indicators
- Audio player styling

#### `public/app.js`
- File upload handling
- Audio recording (Web Audio API)
- API communication
- Results display
- Feature visualization

## Data Flow

```
User Input (Humming)
        ↓
[Frontend: Upload/Record]
        ↓
[API: POST /api/generate-music]
        ↓
[AudioProcessor]
    ├── Load & preprocess audio
    ├── Extract pitch with CREPE
    └── Calculate features
        ↓
[MusicGenerator]
    ├── Load melody audio
    ├── Create style prompt
    └── Generate with MusicGen
        ↓
[Save & Return]
        ↓
[Frontend: Play/Download]
```

## API Request/Response Flow

### Request
```
POST /api/generate-music
Content-Type: multipart/form-data

file: [audio file]
genre: "pop"
mood: "upbeat"
instruments: "piano"
duration: 10.0 (optional)
```

### Response
```json
{
  "message": "Music generated successfully",
  "audio_url": "/api/download/xxx.wav",
  "melody_features": {
    "time": [...],
    "frequency": [...],
    "midi_notes": [...],
    "pitch_mean": 220.5,
    "pitch_std": 45.2,
    "pitch_range": 180.3,
    "tempo": 120.0,
    "duration": 10.2,
    "avg_confidence": 0.85
  }
}
```

## Dependencies

### Core ML Libraries
- **PyTorch**: Deep learning framework
- **Torchaudio**: Audio processing
- **torchcrepe**: CREPE pitch tracker
- **transformers**: Hugging Face model hub
- **audiocraft**: Meta's MusicGen

### Audio Processing
- **librosa**: Audio analysis
- **soundfile**: Audio I/O
- **numpy**: Numerical computing
- **scipy**: Scientific computing

### Web Framework
- **FastAPI**: Modern async web framework
- **uvicorn**: ASGI server
- **python-multipart**: File upload handling
- **pydantic**: Data validation

## Model Downloads

On first run, the following models are automatically downloaded:

1. **MusicGen Melody Model** (~1.5 GB)
   - From: `facebook/musicgen-melody`
   - Used for: Melody-conditioned music generation

2. **CREPE Model** (~100 MB)
   - Included in torchcrepe
   - Used for: Pitch extraction

Models are cached in `~/.cache/huggingface/` by default.

## Environment Variables

Optional configuration via environment variables:

- `MODEL_SIZE`: MusicGen model size (small/medium/large/melody)
- `TARGET_SAMPLE_RATE`: Audio processing sample rate (16000)
- `HOST`: Server host (0.0.0.0)
- `PORT`: Server port (8000)
- `DEVICE`: Force device (cuda/cpu, auto if empty)

## Development

### Adding New Endpoints

1. Add route in `app/main.py`
2. Use existing processors (`audio_processor`, `music_generator`)
3. Return appropriate Pydantic models
4. Update frontend `app.js` if needed

### Modifying Audio Processing

Edit `app/audio_processor.py`:
- Adjust CREPE parameters in `extract_pitch_with_crepe()`
- Add new feature extraction in `extract_melody_features()`
- Modify preprocessing in `load_and_preprocess()`

### Changing Generation Settings

Edit `app/music_generator.py`:
- Adjust generation parameters in `generate_with_melody()`
- Modify style prompts in `get_style_prompt()`
- Change audio post-processing in `save_audio()`

## Testing

### Manual Testing
1. Use the web interface
2. Upload test audio files
3. Try different style combinations

### API Testing
```bash
python backend/test_api.py [optional_audio_file.wav]
```

### cURL Testing
```bash
curl -X POST http://localhost:8000/api/generate-music \
  -F "file=@test.wav" \
  -F "genre=jazz" \
  -F "mood=relaxed" \
  -F "instruments=saxophone"
```

## Deployment Considerations

### For Production
- Add authentication/authorization
- Implement rate limiting
- Use production ASGI server (gunicorn + uvicorn workers)
- Set up reverse proxy (nginx)
- Configure CORS properly (specific origins)
- Add request validation and file size limits
- Implement cleanup job for old files
- Use cloud storage for audio files
- Consider GPU instance for performance

### Docker (Future)
```dockerfile
# Example Dockerfile structure
FROM python:3.12
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## Performance Optimization

- **GPU**: 5-10x faster generation
- **Model Size**: Smaller models (small/medium) are faster
- **Duration**: Longer output takes more time
- **Batch Processing**: Process multiple requests efficiently
- **Caching**: Cache frequently used prompts

## Troubleshooting

See [QUICKSTART.md](QUICKSTART.md) and [README.md](README.md) for common issues and solutions.

