"""
Music generation using Meta's MusicGen model
"""
import torch
import torchaudio
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from pathlib import Path
from typing import Optional, List
import numpy as np


class MusicGenerator:
    """Handles music generation with MusicGen"""
    
    def __init__(self, model_size: str = 'medium'):
        """
        Initialize MusicGen model
        
        Args:
            model_size: Size of the model ('small', 'medium', 'large', 'melody')
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading MusicGen model ({model_size}) on device: {self.device}")
        
        # Load MusicGen model
        # For melody conditioning, use 'melody' model
        if model_size == 'melody':
            self.model = MusicGen.get_pretrained('facebook/musicgen-melody')
        else:
            self.model = MusicGen.get_pretrained(f'facebook/musicgen-{model_size}')
        
        self.model.to(self.device)
        print("MusicGen model loaded successfully")
    
    def generate_from_description(
        self,
        description: str,
        duration: float = 10.0,
        temperature: float = 1.0,
        top_k: int = 250,
        top_p: float = 0.0,
        cfg_coef: float = 3.0
    ) -> torch.Tensor:
        """
        Generate music from text description only
        
        Args:
            description: Text description of the desired music
            duration: Duration in seconds
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            cfg_coef: Classifier-free guidance coefficient
            
        Returns:
            Generated audio tensor
        """
        # Set generation parameters
        self.model.set_generation_params(
            duration=duration,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            cfg_coef=cfg_coef
        )
        
        # Generate music
        with torch.no_grad():
            wav = self.model.generate([description])
        
        return wav.cpu()
    
    def generate_with_melody(
        self,
        description: str,
        melody_path: str,
        duration: float = 10.0,
        temperature: float = 1.0,
        top_k: int = 250,
        cfg_coef: float = 3.0
    ) -> torch.Tensor:
        """
        Generate music conditioned on both text and melody
        
        Args:
            description: Text description of the desired music style
            melody_path: Path to the melody/humming audio file
            duration: Duration in seconds
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            cfg_coef: Classifier-free guidance coefficient
            
        Returns:
            Generated audio tensor
        """
        # Load melody audio
        melody, sr = torchaudio.load(melody_path)
        
        # Ensure mono
        if melody.shape[0] > 1:
            melody = torch.mean(melody, dim=0, keepdim=True)
        
        # Resample if necessary (MusicGen expects 32kHz)
        if sr != self.model.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.model.sample_rate)
            melody = resampler(melody)
        
        melody = melody.to(self.device)
        
        # Set generation parameters
        self.model.set_generation_params(
            duration=duration,
            temperature=temperature,
            top_k=top_k,
            cfg_coef=cfg_coef
        )
        
        # Generate music conditioned on melody
        with torch.no_grad():
            wav = self.model.generate_with_chroma(
                descriptions=[description],
                melody_wavs=melody[None],
                melody_sample_rate=self.model.sample_rate,
                progress=False
            )
        
        return wav.cpu()
    
    def save_audio(
        self,
        audio: torch.Tensor,
        output_path: str,
        sample_rate: Optional[int] = None
    ) -> str:
        """
        Save generated audio to file
        
        Args:
            audio: Audio tensor to save
            output_path: Output file path (without extension)
            sample_rate: Sample rate (uses model's if not provided)
            
        Returns:
            Path to saved audio file
        """
        if sample_rate is None:
            sample_rate = self.model.sample_rate
        
        # Ensure audio is 2D (channels, samples)
        if audio.dim() == 3:
            audio = audio.squeeze(0)
        
        # Use audiocraft's audio_write which handles normalization
        output_path = Path(output_path)
        audio_write(
            str(output_path.with_suffix('')),  # Without extension
            audio,
            sample_rate,
            strategy="loudness",
            loudness_compressor=True
        )
        
        return str(output_path.with_suffix('.wav'))
    
    def generate_complete_track(
        self,
        melody_path: str,
        style_description: str,
        output_path: str,
        duration: Optional[float] = None,
        temperature: float = 1.0,
        cfg_coef: float = 3.0
    ) -> str:
        """
        Complete pipeline: generate music from humming with style
        
        Args:
            melody_path: Path to humming/melody audio
            style_description: Description of desired musical style
            output_path: Output path for generated music
            duration: Duration in seconds (uses melody duration if None)
            temperature: Sampling temperature
            cfg_coef: Guidance coefficient
            
        Returns:
            Path to generated audio file
        """
        # Get melody duration if not specified
        if duration is None:
            melody, sr = torchaudio.load(melody_path)
            duration = melody.shape[1] / sr
            duration = min(duration, 30.0)  # Cap at 30 seconds
        
        # Generate music
        print(f"Generating music with style: '{style_description}'")
        print(f"Duration: {duration:.1f}s")
        
        audio = self.generate_with_melody(
            description=style_description,
            melody_path=melody_path,
            duration=duration,
            temperature=temperature,
            cfg_coef=cfg_coef
        )
        
        # Save audio
        output_file = self.save_audio(audio, output_path)
        print(f"Music saved to: {output_file}")
        
        return output_file


def get_style_prompt(genre: str, mood: str = "", instruments: str = "") -> str:
    """
    Create a detailed style prompt for MusicGen
    
    Args:
        genre: Musical genre (e.g., 'pop', 'jazz', 'classical')
        mood: Mood/emotion (e.g., 'happy', 'melancholic', 'energetic')
        instruments: Instrument preferences (e.g., 'piano', 'guitar', 'orchestra')
        
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    if genre:
        prompt_parts.append(genre)
    
    if mood:
        prompt_parts.append(mood)
    
    if instruments:
        prompt_parts.append(f"with {instruments}")
    
    # Add some defaults if nothing specified
    if not prompt_parts:
        prompt_parts = ["melodic", "instrumental"]
    
    return " ".join(prompt_parts)

