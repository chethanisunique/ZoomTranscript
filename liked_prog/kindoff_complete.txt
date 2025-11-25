# zoom_ai_worker_ui.py
import sys
import os
import torch
import whisper
import subprocess
import json
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QTabWidget, QTextEdit, QHBoxLayout, QLineEdit, QScrollArea, QGroupBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from transformers import pipeline

sys.stdout.reconfigure(encoding='utf-8')

summarizer = pipeline("summarization")
model = whisper.load_model("tiny")

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3"

class ZoomAIWorker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoom AI Worker")
        self.resize(1000, 800)

        self.layout = QVBoxLayout(self)

        self.select_button = QPushButton("Select Zoom Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything about the meeting…")
        self.chat_input.returnPressed.connect(self.answer_query)
        self.layout.addWidget(self.chat_input)

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.layout.addWidget(self.chat_output)

        self.transcripts = {}
        self.summaries = {}

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Zoom Folder")
        if folder:
            self.process_selected_folder(folder)

    def process_selected_folder(self, folder):
        self.transcripts = {}
        self.summaries = {}

        full_audio = None
        for file in os.listdir(folder):
            if file.endswith(".m4a"):
                full_audio = os.path.join(folder, file)
                break

        if not full_audio:
            self.chat_output.setText("No full audio file found in main folder.")
            return

        full_transcript = model.transcribe(full_audio)['text']
        full_summary = summarizer(full_transcript, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        self.transcripts['Full Meeting'] = full_transcript
        self.summaries['Full Meeting'] = full_summary

        self.build_full_tab(full_transcript, full_summary)

        speaker_folder = os.path.join(folder, "Audio Record")
        if not os.path.exists(speaker_folder):
            self.chat_output.append("No 'Audio Record' folder found.")
            return

        self.build_speaker_tab(speaker_folder)

    def build_full_tab(self, transcript, summary):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("📄 Full Meeting Transcript"))
        text_box = QTextEdit(transcript)
        layout.addWidget(text_box)
        layout.addWidget(QLabel("📝 Summary"))
        summary_box = QTextEdit(summary)
        layout.addWidget(summary_box)
        self.tabs.addTab(tab, "Full Meeting")

    def build_speaker_tab(self, speaker_folder):
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        vbox = QVBoxLayout(scroll_content)

        for file in os.listdir(speaker_folder):
            if file.endswith(".m4a"):
                speaker_name = os.path.splitext(file)[0]
                path = os.path.join(speaker_folder, file)
                transcript = model.transcribe(path)['text']
                summary = summarizer(transcript, max_length=100, min_length=25, do_sample=False)[0]['summary_text']
                self.transcripts[speaker_name] = transcript
                self.summaries[speaker_name] = summary

                group = QGroupBox(f"🗣️ {speaker_name}")
                group_layout = QVBoxLayout()
                group_layout.addWidget(QLabel("Transcript:"))
                text_box = QTextEdit(transcript)
                group_layout.addWidget(text_box)
                group_layout.addWidget(QLabel("Summary:"))
                summary_box = QTextEdit(summary)
                group_layout.addWidget(summary_box)

                play_btn = QPushButton("🔊 Play Audio")
                play_btn.clicked.connect(lambda _, p=path: QDesktopServices.openUrl(QUrl.fromLocalFile(p)))
                group_layout.addWidget(play_btn)

                group.setLayout(group_layout)
                vbox.addWidget(group)

        scroll.setWidget(scroll_content)
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "Speaker-wise Summary")

    def answer_query(self):
        query = self.chat_input.text().strip()
        self.chat_input.clear()
        context = ""
        for name, text in self.transcripts.items():
            context += f"Transcript of {name}:\n{text}\n\n"

        prompt = f"You are a helpful assistant. Answer the question based on the following meeting transcript context.\n\n{context}\n\nUser: {query}\nAssistant:"

        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": LLM_MODEL, "prompt": prompt, "stream": False}
            )
            if response.status_code == 200:
                reply = response.json().get("response", "(No response)")
                self.chat_output.append(f"You: {query}\nAI: {reply}\n")
            else:
                self.chat_output.append("Error from LLM API.")
        except Exception as e:
            self.chat_output.append(f"Failed to contact Ollama: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    win = ZoomAIWorker()
    win.show()
    sys.exit(app.exec())
