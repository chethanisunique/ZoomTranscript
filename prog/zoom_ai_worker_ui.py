import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
from transformers import pipeline
import pyperclip
import pygame
from ttkthemes import ThemedTk

sys.stdout.reconfigure(encoding='utf-8')

# Load Whisper Model
model = whisper.load_model("tiny")

# Load Summarization Model
summarizer = pipeline("summarization")

# Initialize Pygame for Audio Playback
pygame.mixer.init()

# Global Variables
selected_folder = ""
dark_mode = False

def browse_folder():
    global selected_folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder = folder_path
        folder_label.config(text=f"Selected: {selected_folder}")
        confirm_button.config(state=tk.NORMAL)

def confirm_selection():
    if selected_folder:
        messagebox.showinfo("Confirmation", f"Folder Selected:\n{selected_folder}")
        upload_button.config(state=tk.NORMAL)
    else:
        messagebox.showwarning("Warning", "Please select a folder first!")

def update_progress(value, text):
    progress_bar["value"] = value
    progress_label.config(text=f"Progress: {value}% - {text}")
    root.update_idletasks()

def transcribe_audio(audio_path):
    return model.transcribe(audio_path)["text"]

def summarize_text(text):
    return summarizer(text, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]

def process_zoom_recordings():
    if not selected_folder:
        messagebox.showerror("Error", "No folder selected! Please browse and select a folder.")
        return

    update_progress(10, "Initializing...")
    processed_folder = os.path.join(selected_folder, "Processed")
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)

    update_progress(20, "Scanning files...")
    all_files = os.listdir(selected_folder)
    audio_files = [f for f in all_files if f.endswith(('.m4a', '.wav', '.mp3'))]

    if not audio_files:
        messagebox.showerror("Error", "No audio files found! Please check your folder.")
        return

    update_progress(40, "Processing audio files...")
    transcripts = []
    for i, audio_file in enumerate(audio_files):
        audio_path = os.path.join(selected_folder, audio_file)
        transcript = transcribe_audio(audio_path)
        transcripts.append(transcript)
        with open(os.path.join(processed_folder, f"{audio_file}.txt"), "w", encoding="utf-8") as f:
            f.write(transcript)
        progress = 40 + int((i + 1) / len(audio_files) * 30)
        update_progress(progress, f"Transcribing {audio_file}...")

    update_progress(80, "Summarizing text...")
    full_transcript = " ".join(transcripts)
    summary = summarize_text(full_transcript)
    with open(os.path.join(processed_folder, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary)

    summary_textbox.config(state=tk.NORMAL)
    summary_textbox.delete(1.0, tk.END)
    summary_textbox.insert(tk.END, summary)
    summary_textbox.config(state=tk.DISABLED)

    update_progress(100, "Completed!")
    messagebox.showinfo("Success", "Process Completed!\nCheck the 'Processed' folder.")
    update_progress(0, "Ready")

def copy_summary():
    text = summary_textbox.get(1.0, tk.END).strip()
    pyperclip.copy(text)
    messagebox.showinfo("Copied", "Summary copied to clipboard!")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg="#2E2E2E")
        folder_label.config(bg="#2E2E2E", fg="white")
        progress_label.config(bg="#2E2E2E", fg="white")
        summary_textbox.config(bg="#3A3A3A", fg="white")
        theme_button.config(text="☀️ Light Mode")
    else:
        root.configure(bg="white")
        folder_label.config(bg="white", fg="black")
        progress_label.config(bg="white", fg="black")
        summary_textbox.config(bg="white", fg="black")
        theme_button.config(text="🌙 Dark Mode")

# Tkinter UI Setup
root = ThemedTk(theme="radiance")
root.title("Zoom AI Worker")
root.geometry("600x500")

browse_button = tk.Button(root, text="📂 Browse Folder", command=browse_folder, font=("Segoe UI", 12), relief=tk.RAISED, bd=3)
browse_button.pack(pady=10)

folder_label = tk.Label(root, text="No folder selected", font=("Segoe UI", 10))
folder_label.pack()

confirm_button = tk.Button(root, text="✅ Confirm Selection", command=confirm_selection, state=tk.DISABLED, font=("Segoe UI", 12), relief=tk.RAISED, bd=3)
confirm_button.pack(pady=5)

upload_button = tk.Button(root, text="▶️ Upload & Process", command=process_zoom_recordings, state=tk.DISABLED, font=("Segoe UI", 12), relief=tk.RAISED, bd=3)
upload_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

progress_label = tk.Label(root, text="Progress: 0% - Ready", font=("Segoe UI", 10))
progress_label.pack()

summary_textbox = tk.Text(root, height=10, width=60, state=tk.DISABLED, wrap=tk.WORD, font=("Segoe UI", 10))
summary_textbox.pack(pady=10)

copy_button = tk.Button(root, text="📋 Copy Summary", command=copy_summary, font=("Segoe UI", 12), relief=tk.RAISED, bd=3)
copy_button.pack(pady=5)

theme_button = tk.Button(root, text="🌙 Dark Mode", command=toggle_theme, font=("Segoe UI", 12), relief=tk.RAISED, bd=3)
theme_button.pack(pady=10)

root.mainloop()
