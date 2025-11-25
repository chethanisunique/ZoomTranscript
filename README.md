# Transcription Studio: AI-Powered Meeting Assistant

Transcription Studio is a full-stack web application that leverages AI to transcribe and summarize audio recordings from meetings. Simply upload a Zoom recording (or any `.m4a` file), and the application will provide a full, speaker-segmented transcript and a concise, AI-generated summary.

This project combines a modern React frontend with a powerful Python backend, making it a comprehensive example of integrating AI services into a web application.

## Features

- **File Upload**: A sleek, drag-and-drop interface for uploading audio files.
- **AI Transcription**: Utilizes OpenAI's Whisper model to generate accurate, time-stamped transcripts.
- **AI Summarization**: Employs a `transformers`-based model to produce a structured summary, including an overview and key points.
- **Dual-Server Architecture**: A React/Vite frontend communicates with a Python/FastAPI backend.
- **Easy Setup**: Includes a batch script to automate backend setup and execution.

## Technology Stack

**Frontend:**
- **Framework**: React (with Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks

**Backend:**
- **Framework**: FastAPI
- **Language**: Python
- **AI Models**:
  - `openai-whisper` for transcription
  - `transformers` (with `facebook/bart-large-cnn`) for summarization

## Getting Started

To run this project locally, you will need Python, Node.js, and FFmpeg installed on your system.

### 1. Install FFmpeg

The backend requires FFmpeg to process audio files. You can install it using `winget` (on Windows) or by following the manual installation guide [here](https://www.gyan.dev/ffmpeg/builds/).

### 2. Set Up the Backend

Navigate to the project root directory in your terminal and run the provided batch script:

```bash
cd d:\Zoom_project
run_backend.bat
```

This script will automatically:
1. Create and activate a Python virtual environment (`venv`).
2. Install all required dependencies from `requirements.txt`.
3. Start the FastAPI server at `http://localhost:8000`.

### 3. Set Up the Frontend

Open a **new terminal** and navigate to the `Frontend` directory:

```bash
cd d:\Zoom_project\Frontend
```

Install the necessary Node.js packages:

```bash
npm install
```

Then, start the development server:

```bash
npm run dev
```

The application will open in your browser, typically at `http://localhost:5173`.

## How to Use

1. Launch the application by starting both the backend and frontend servers.
2. Open the web interface in your browser.
3. Drag and drop your audio file onto the upload area or click to browse.
4. Wait for the processing to complete.
5. View the full transcript and the AI-generated summary in their respective tabs.
