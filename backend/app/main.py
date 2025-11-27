"""
FastAPI backend for Melody2Music system
Handles audio upload, melody extraction, and music generation
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil
import uuid
from typing import Optional
import os

from .audio_processor import AudioProcessor
from .music_generator import MusicGenerator, get_style_prompt


# Initialize FastAPI app
app = FastAPI(
    title="Melody2Music API",
    description="Convert humming to instrumental music using CREPE and MusicGen",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors (lazy loading for efficiency)
audio_processor = None
music_generator = None

# Directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# Pydantic models
class GenerationRequest(BaseModel):
    genre: str = "pop"
    mood: str = "upbeat"
    instruments: str = "piano and guitar"
    duration: Optional[float] = None


class MelodyFeaturesResponse(BaseModel):
    features: dict
    message: str


class GenerationResponse(BaseModel):
    message: str
    audio_url: str
    melody_features: dict


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global audio_processor, music_generator
    
    print("Initializing Melody2Music backend...")
    audio_processor = AudioProcessor(target_sr=16000)
    
    # Use melody model for conditioning
    music_generator = MusicGenerator(model_size='melody')
    print("Backend initialization complete!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Melody2Music API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "audio_processor": audio_processor is not None,
        "music_generator": music_generator is not None
    }


@app.post("/api/extract-melody", response_model=MelodyFeaturesResponse)
async def extract_melody(file: UploadFile = File(...)):
    """
    Extract melody features from uploaded humming audio
    
    Args:
        file: Audio file (wav, mp3, etc.)
        
    Returns:
        Extracted melody features including pitch, tempo, etc.
    """
    if audio_processor is None:
        raise HTTPException(status_code=503, detail="Audio processor not initialized")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    input_path = UPLOAD_DIR / f"{file_id}{file_extension}"
    
    try:
        # Save uploaded file
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract melody features
        features = audio_processor.extract_melody_features(str(input_path))
        
        return MelodyFeaturesResponse(
            features=features,
            message="Melody features extracted successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting melody: {str(e)}")
    
    finally:
        # Cleanup
        if input_path.exists():
            input_path.unlink()


@app.post("/api/generate-music", response_model=GenerationResponse)
async def generate_music(
    file: UploadFile = File(...),
    genre: str = Form("pop"),
    mood: str = Form("upbeat"),
    instruments: str = Form("piano"),
    duration: Optional[float] = Form(None)
):
    """
    Complete pipeline: Upload humming, extract melody, generate music
    
    Args:
        file: Audio file with humming
        genre: Musical genre (pop, jazz, classical, etc.)
        mood: Mood/emotion (happy, sad, energetic, etc.)
        instruments: Desired instruments
        duration: Duration in seconds (optional)
        
    Returns:
        Generated music file and melody features
    """
    if audio_processor is None or music_generator is None:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Generate unique ID for this request
    request_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    input_path = UPLOAD_DIR / f"{request_id}_input{file_extension}"
    output_path = OUTPUT_DIR / f"{request_id}_output"
    
    try:
        # Save uploaded file
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing request {request_id}")
        print(f"Genre: {genre}, Mood: {mood}, Instruments: {instruments}")
        
        # Extract melody features
        features = audio_processor.extract_melody_features(str(input_path))
        print(f"Melody features extracted. Confidence: {features['avg_confidence']:.2f}")
        
        # Create style prompt
        style_prompt = get_style_prompt(genre, mood, instruments)
        print(f"Style prompt: {style_prompt}")
        
        # Generate music
        generated_file = music_generator.generate_complete_track(
            melody_path=str(input_path),
            style_description=style_prompt,
            output_path=str(output_path),
            duration=duration,
            temperature=1.0,
            cfg_coef=3.0
        )
        
        return GenerationResponse(
            message="Music generated successfully",
            audio_url=f"/api/download/{request_id}_output.wav",
            melody_features=features
        )
    
    except Exception as e:
        print(f"Error generating music: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")
    
    finally:
        # Cleanup input file
        if input_path.exists():
            input_path.unlink()


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download generated audio file
    
    Args:
        filename: Name of the file to download
        
    Returns:
        Audio file
    """
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=filename
    )


@app.delete("/api/cleanup/{request_id}")
async def cleanup_files(request_id: str):
    """
    Cleanup files associated with a request
    
    Args:
        request_id: Request ID
        
    Returns:
        Cleanup status
    """
    cleaned = []
    
    # Find and remove associated files
    for pattern in [f"{request_id}_*", f"*{request_id}*"]:
        for directory in [UPLOAD_DIR, OUTPUT_DIR]:
            for file_path in directory.glob(pattern):
                try:
                    file_path.unlink()
                    cleaned.append(str(file_path.name))
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    return {
        "message": "Cleanup completed",
        "files_removed": cleaned
    }


@app.post("/api/generate-text-only")
async def generate_from_text(
    description: str = Form(...),
    duration: float = Form(10.0)
):
    """
    Generate music from text description only (no melody conditioning)
    
    Args:
        description: Text description of desired music
        duration: Duration in seconds
        
    Returns:
        Generated music file
    """
    if music_generator is None:
        raise HTTPException(status_code=503, detail="Music generator not initialized")
    
    request_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{request_id}_text_gen"
    
    try:
        # Generate music
        audio = music_generator.generate_from_description(
            description=description,
            duration=duration
        )
        
        # Save audio
        generated_file = music_generator.save_audio(audio, str(output_path))
        
        return {
            "message": "Music generated successfully",
            "audio_url": f"/api/download/{request_id}_text_gen.wav"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

