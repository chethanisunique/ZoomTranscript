import os
import shutil
import uuid
import subprocess
import whisper
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from transformers import pipeline
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Loading ---
# It's best practice to load models once when the application starts
try:
    logger.info("Loading Whisper model...")
    whisper_model = whisper.load_model("tiny")
    logger.info("Whisper model loaded successfully.")

    logger.info("Loading summarization model...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    logger.info("Summarization model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading models: {e}")
    # Exit if models can't be loaded
    raise RuntimeError("Could not load AI models") from e


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Zoom AI Worker API",
    description="API for transcribing and summarizing audio & video files.",
)

# Serve extracted audio files
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# --- CORS Configuration ---
# This allows the React frontend (running on a different port) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Functions ---

def extract_audio(input_path: str) -> str:
    """Extracts or converts audio to WAV using ffmpeg. Returns the audio file path."""
    ext = os.path.splitext(input_path)[1].lower()
    output_path = input_path  # default if already audio
    if ext in [".mp4", ".mov", ".mkv", ".webm"]:
        output_path = input_path + ".wav"
        cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-i", input_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            output_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def get_duration_sec(path: str) -> int:
    """Get media duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(float(result.stdout.strip()))
    except Exception:
        return 0
def transcribe_audio(audio_path: str) -> List[Dict]:
    """Transcribes audio and returns a list of segments with speaker and text."""
    logger.info(f"Transcribing audio file: {audio_path}")
    # Note: Speaker diarization is a complex feature not included in the original script.
    # For now, we'll label the speaker as "Speaker 1".
    # A more advanced implementation would use a diarization model.
    result = whisper_model.transcribe(audio_path, verbose=True)
    
    segments: List[Dict] = []
    for segment in result.get("segments", []):
        start_sec = float(segment["start"])
        end_sec = float(segment["end"])
        segments.append({
            "speaker": "Speaker",  # TODO: Replace with real diarization
            "text": segment["text"].strip(),
            "timestamp": f"{int(start_sec // 60):02d}:{int(start_sec % 60):02d}",
            "start": start_sec,
            "end": end_sec,
        })
        
    logger.info("Transcription complete.")
    return segments

def summarize_text(text: List[Dict]) -> dict:
    """Summarizes the transcribed text."""
    logger.info("Starting summarization...")
    full_transcript = " ".join([seg["text"] for seg in text])
    
    # The summarizer works best with text up to a certain length.
    # Truncate if necessary.
    max_input_length = 1024
    if len(full_transcript) > max_input_length * 4: # Heuristic for token length
        full_transcript = full_transcript[:max_input_length * 4]

    summary_result = summarizer(full_transcript, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    
    # The mock data has a more structured summary. We will create a simplified version.
    summary_data = {
        "overview": summary_result,
        "keyPoints": [point.strip() for point in summary_result.split('.') if point.strip()],
        "participants": ["Speaker"], # Placeholder
        "duration": "N/A",  # Placeholder
        "actionItems": [] # Placeholder
    }
    logger.info("Summarization complete.")
    return summary_data


# --- API Endpoint ---
@app.post("/process-file/")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload a Zoom recording (audio or video), transcribe it, and return a summary, speaker segments, duration, and an audio URL.
    """
    # Create a temporary directory to store the uploaded file
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file
        logger.info(f"Receiving file: {file.filename}")
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to {temp_file_path}")

        # Extract/convert audio if necessary
        audio_path = extract_audio(temp_file_path)

        # Duration
        duration_sec = get_duration_sec(audio_path)
        duration_display = f"{duration_sec//60}:{duration_sec%60:02d}" if duration_sec else "N/A"

        transcript_data = transcribe_audio(audio_path)
        summary_data = summarize_text(transcript_data)
        summary_data["duration"] = duration_display

        # Save audio copy to media directory for playback
        audio_filename = f"{uuid.uuid4()}.wav"
        media_path = os.path.join(MEDIA_DIR, audio_filename)
        shutil.copy(audio_path, media_path)
        audio_url = f"/media/{audio_filename}"

        return {
            "transcript": transcript_data,
            "summary": summary_data,
            "audioUrl": audio_url,
            "duration": duration_display,
        }
    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        # Clean up the temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            # Also remove extracted audio if it was generated inside temp_files
            extracted = temp_file_path + ".wav"
            if os.path.exists(extracted):
                os.remove(extracted)
        except Exception:
            pass
        logger.info("Processing finished and temporary file removed.")

# --- Root Endpoint for Health Check ---
@app.get("/")
def read_root():
    return {"status": "API is running"}
