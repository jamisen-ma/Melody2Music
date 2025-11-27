// Melody2Music Frontend Application
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const audioFileInput = document.getElementById('audioFile');
const fileNameSpan = document.getElementById('fileName');
const recordBtn = document.getElementById('recordBtn');
const recordStatus = document.getElementById('recordStatus');
const generateBtn = document.getElementById('generateBtn');
const progressContainer = document.getElementById('progress');
const resultsSection = document.getElementById('results');
const resultAudio = document.getElementById('resultAudio');
const downloadBtn = document.getElementById('downloadBtn');
const featuresDiv = document.getElementById('features');

// Form inputs
const genreSelect = document.getElementById('genre');
const moodSelect = document.getElementById('mood');
const instrumentsInput = document.getElementById('instruments');
const durationInput = document.getElementById('duration');

// State
let selectedFile = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let currentAudioUrl = null;

// Event Listeners
audioFileInput.addEventListener('change', handleFileSelect);
recordBtn.addEventListener('click', toggleRecording);
generateBtn.addEventListener('click', generateMusic);
downloadBtn.addEventListener('click', downloadAudio);

// File Selection Handler
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        fileNameSpan.textContent = file.name;
        generateBtn.disabled = false;
    }
}

// Recording Functions
async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const fileName = `recording_${Date.now()}.wav`;
                selectedFile = new File([audioBlob], fileName, { type: 'audio/wav' });
                fileNameSpan.textContent = fileName;
                generateBtn.disabled = false;
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            recordBtn.textContent = '⏹️ Stop Recording';
            recordBtn.classList.add('recording');
            recordStatus.textContent = 'Recording...';
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.textContent = '🎤 Record Audio';
        recordBtn.classList.remove('recording');
        recordStatus.textContent = 'Recording saved!';
        setTimeout(() => {
            recordStatus.textContent = '';
        }, 3000);
    }
}

// Generate Music
async function generateMusic() {
    if (!selectedFile) {
        alert('Please select or record an audio file first.');
        return;
    }

    // Show progress
    generateBtn.disabled = true;
    progressContainer.style.display = 'block';
    resultsSection.style.display = 'none';

    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('genre', genreSelect.value);
    formData.append('mood', moodSelect.value);
    formData.append('instruments', instrumentsInput.value);
    
    if (durationInput.value) {
        formData.append('duration', durationInput.value);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-music`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate music');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error generating music:', error);
        alert(`Error: ${error.message}\n\nMake sure the backend server is running on ${API_BASE_URL}`);
    } finally {
        progressContainer.style.display = 'none';
        generateBtn.disabled = false;
    }
}

// Display Results
function displayResults(result) {
    // Set audio source
    currentAudioUrl = `${API_BASE_URL}${result.audio_url}`;
    resultAudio.src = currentAudioUrl;
    
    // Display melody features
    displayMelodyFeatures(result.melody_features);
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display Melody Features
function displayMelodyFeatures(features) {
    const featureItems = [
        {
            label: 'Duration',
            value: `${features.duration.toFixed(1)}s`
        },
        {
            label: 'Tempo',
            value: `${Math.round(features.tempo)} BPM`
        },
        {
            label: 'Avg Pitch',
            value: `${Math.round(features.pitch_mean)} Hz`
        },
        {
            label: 'Pitch Range',
            value: `${Math.round(features.pitch_range)} Hz`
        },
        {
            label: 'Confidence',
            value: `${(features.avg_confidence * 100).toFixed(0)}%`
        },
        {
            label: 'Pitch Std Dev',
            value: `${Math.round(features.pitch_std)} Hz`
        }
    ];

    featuresDiv.innerHTML = featureItems.map(item => `
        <div class="feature-item">
            <div class="feature-label">${item.label}</div>
            <div class="feature-value">${item.value}</div>
        </div>
    `).join('');
}

// Download Audio
function downloadAudio() {
    if (currentAudioUrl) {
        const link = document.createElement('a');
        link.href = currentAudioUrl;
        link.download = `melody2music_${Date.now()}.wav`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const health = await response.json();
        console.log('Backend health:', health);
        
        if (!health.audio_processor || !health.music_generator) {
            console.warn('Backend services not fully initialized');
        }
    } catch (error) {
        console.error('Backend not reachable:', error);
        console.log(`Please make sure the backend is running on ${API_BASE_URL}`);
    }
}

// Initialize
checkBackendHealth();

