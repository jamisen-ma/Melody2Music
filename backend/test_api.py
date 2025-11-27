"""
Simple test script for Melody2Music API
"""
import requests
import time
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def test_health():
    """Test if the backend is running"""
    print("Testing backend health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   - Audio processor: {data['audio_processor']}")
            print(f"   - Music generator: {data['music_generator']}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print(f"   Start it with: cd backend && ./run.sh")
        return False


def test_text_generation():
    """Test text-only music generation"""
    print("\nTesting text-only generation...")
    
    data = {
        "description": "upbeat electronic music with synthesizers",
        "duration": 5.0
    }
    
    print(f"Generating: '{data['description']}'")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-text-only",
            data=data
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful! (took {elapsed:.1f}s)")
            print(f"   - Audio URL: {result['audio_url']}")
            
            # Download the file
            audio_url = f"{API_BASE_URL}{result['audio_url']}"
            audio_response = requests.get(audio_url)
            
            if audio_response.status_code == 200:
                output_file = Path("test_output.wav")
                output_file.write_bytes(audio_response.content)
                print(f"   - Saved to: {output_file.absolute()}")
                return True
            else:
                print(f"❌ Could not download audio: {audio_response.status_code}")
                return False
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_melody_generation(audio_file: str = None):
    """Test melody-conditioned generation"""
    if not audio_file:
        print("\n⚠️  Skipping melody generation test (no audio file provided)")
        print("   To test: python test_api.py path/to/your/humming.wav")
        return None
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print(f"\nTesting melody-conditioned generation with: {audio_file}")
    
    files = {
        'file': open(audio_path, 'rb')
    }
    
    data = {
        'genre': 'pop',
        'mood': 'upbeat',
        'instruments': 'piano and guitar'
    }
    
    print(f"Style: {data['genre']}, {data['mood']}, {data['instruments']}")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-music",
            files=files,
            data=data
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful! (took {elapsed:.1f}s)")
            print(f"   - Audio URL: {result['audio_url']}")
            
            # Show melody features
            features = result['melody_features']
            print(f"   - Duration: {features['duration']:.1f}s")
            print(f"   - Tempo: {features['tempo']:.0f} BPM")
            print(f"   - Avg Pitch: {features['pitch_mean']:.1f} Hz")
            print(f"   - Confidence: {features['avg_confidence']:.2f}")
            
            # Download the file
            audio_url = f"{API_BASE_URL}{result['audio_url']}"
            audio_response = requests.get(audio_url)
            
            if audio_response.status_code == 200:
                output_file = Path("test_melody_output.wav")
                output_file.write_bytes(audio_response.content)
                print(f"   - Saved to: {output_file.absolute()}")
                return True
            else:
                print(f"❌ Could not download audio: {audio_response.status_code}")
                return False
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        files['file'].close()


def main():
    import sys
    
    print("=" * 60)
    print("Melody2Music API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running. Exiting.")
        return
    
    # Test 2: Text-only generation
    test_text_generation()
    
    # Test 3: Melody-conditioned generation (if file provided)
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    test_melody_generation(audio_file)
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

