import os
import shutil
import whisper
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
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
    description="API for transcribing and summarizing audio files.",
)

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
def transcribe_audio(audio_path: str) -> list:
    """Transcribes audio and returns a list of segments with speaker and text."""
    logger.info(f"Transcribing audio file: {audio_path}")
    # Note: Speaker diarization is a complex feature not included in the original script.
    # For now, we'll label the speaker as "Speaker 1".
    # A more advanced implementation would use a diarization model.
    result = whisper_model.transcribe(audio_path, verbose=True)
    
    segments = []
    for segment in result.get("segments", []):
        segments.append({
            "speaker": "Speaker", # Placeholder for speaker diarization
            "text": segment["text"],
            "timestamp": f"{int(segment['start'] // 60):02d}:{int(segment['start'] % 60):02d}"
        })
        
    logger.info("Transcription complete.")
    return segments

def summarize_text(text: list) -> dict:
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
        "duration": "N/A", # Placeholder
        "actionItems": [] # Placeholder
    }
    logger.info("Summarization complete.")
    return summary_data


# --- API Endpoint ---
@app.post("/process-audio/")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload an audio file, transcribe it, and return a summary.
    """
    # Create a temporary directory to store the uploaded file
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file
        logger.info(f"Receiving file: {file.filename}")
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to {temp_file_path}")

        # Process the audio file
        transcript_data = transcribe_audio(temp_file_path)
        summary_data = summarize_text(transcript_data)

        return {
            "transcript": transcript_data,
            "summary": summary_data
        }
    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")
        return {"error": f"An error occurred: {str(e)}"}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        logger.info("Processing finished and temporary file removed.")

# --- Root Endpoint for Health Check ---
@app.get("/")
def read_root():
    return {"status": "API is running"}
