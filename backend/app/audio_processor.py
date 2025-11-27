"""
Audio preprocessing and pitch extraction using CREPE and Torchaudio
"""
import torch
import torchaudio
import torchcrepe
import numpy as np
import librosa
from pathlib import Path
from typing import Tuple, Optional
import soundfile as sf


class AudioProcessor:
    """Handles audio preprocessing and pitch extraction"""
    
    def __init__(self, target_sr: int = 16000):
        """
        Initialize the audio processor
        
        Args:
            target_sr: Target sample rate for processing
        """
        self.target_sr = target_sr
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"AudioProcessor initialized on device: {self.device}")
    
    def load_and_preprocess(self, audio_path: str) -> Tuple[torch.Tensor, int]:
        """
        Load and preprocess audio file
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Tuple of (audio tensor, sample rate)
        """
        # Load audio using torchaudio
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Resample to target sample rate
        if sample_rate != self.target_sr:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=self.target_sr
            )
            waveform = resampler(waveform)
        
        # Normalize audio
        waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-8)
        
        return waveform, self.target_sr
    
    def extract_pitch_with_crepe(self, audio_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract pitch/melody using CREPE pitch tracker
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Tuple of (time, frequency, confidence)
        """
        # Load and preprocess audio
        waveform, sr = self.load_and_preprocess(audio_path)
        
        # Move to device
        audio_tensor = waveform.to(self.device)
        
        # Extract pitch using CREPE
        # CREPE expects audio with shape (batch, samples)
        time, frequency, confidence, activation = torchcrepe.predict(
            audio_tensor,
            sr,
            hop_length=160,  # ~10ms hop for 16kHz
            fmin=50,         # Minimum frequency (Hz)
            fmax=800,        # Maximum frequency for humming (Hz)
            model='full',    # Use full CREPE model for best quality
            decoder=torchcrepe.decode.viterbi,  # Viterbi decoding for smooth pitch
            device=self.device
        )
        
        # Convert to numpy
        time = time.cpu().numpy()
        frequency = frequency.cpu().numpy().squeeze()
        confidence = confidence.cpu().numpy().squeeze()
        
        # Filter out low confidence predictions
        frequency = np.where(confidence > 0.5, frequency, 0)
        
        return time, frequency, confidence
    
    def pitch_to_midi(self, frequency: np.ndarray) -> np.ndarray:
        """
        Convert frequency (Hz) to MIDI note numbers
        
        Args:
            frequency: Array of frequencies in Hz
            
        Returns:
            Array of MIDI note numbers
        """
        # Avoid log of zero
        frequency = np.where(frequency > 0, frequency, 1)
        midi = 69 + 12 * np.log2(frequency / 440.0)
        # Set zero frequencies to zero MIDI notes
        midi = np.where(frequency > 1, midi, 0)
        return midi
    
    def extract_melody_features(self, audio_path: str) -> dict:
        """
        Extract comprehensive melody features from audio
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing melody features
        """
        # Extract pitch
        time, frequency, confidence = self.extract_pitch_with_crepe(audio_path)
        
        # Convert to MIDI
        midi_notes = self.pitch_to_midi(frequency)
        
        # Calculate statistics
        valid_freq = frequency[frequency > 0]
        
        if len(valid_freq) > 0:
            pitch_mean = np.mean(valid_freq)
            pitch_std = np.std(valid_freq)
            pitch_range = np.max(valid_freq) - np.min(valid_freq)
        else:
            pitch_mean = pitch_std = pitch_range = 0
        
        # Load audio for additional features
        waveform, sr = self.load_and_preprocess(audio_path)
        audio_np = waveform.squeeze().numpy()
        
        # Calculate tempo using librosa
        tempo, _ = librosa.beat.beat_track(y=audio_np, sr=sr)
        
        features = {
            'time': time.tolist(),
            'frequency': frequency.tolist(),
            'confidence': confidence.tolist(),
            'midi_notes': midi_notes.tolist(),
            'pitch_mean': float(pitch_mean),
            'pitch_std': float(pitch_std),
            'pitch_range': float(pitch_range),
            'tempo': float(tempo),
            'duration': float(len(audio_np) / sr),
            'avg_confidence': float(np.mean(confidence))
        }
        
        return features
    
    def create_melody_guide(self, audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Create a simplified melody guide audio file
        
        Args:
            audio_path: Input audio path
            output_path: Output path for the melody guide (optional)
            
        Returns:
            Path to the created melody guide file
        """
        # Extract pitch
        time, frequency, confidence = self.extract_pitch_with_crepe(audio_path)
        
        # Load original audio
        waveform, sr = self.load_and_preprocess(audio_path)
        audio_np = waveform.squeeze().numpy()
        
        # Create output path if not provided
        if output_path is None:
            input_path = Path(audio_path)
            output_path = input_path.parent / f"{input_path.stem}_melody.wav"
        
        # For now, save the cleaned version
        # In a production system, you might synthesize from the pitch contour
        sf.write(str(output_path), audio_np, sr)
        
        return str(output_path)

