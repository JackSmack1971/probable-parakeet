import tkinter as tk
from tkinter import filedialog

def browse_audio():
    audio_path = filedialog.askopenfilename(title="Select audio file", filetypes=[("Audio files", "*.wav;*.mp3")])
    audio_entry.delete(0, tk.END)
    audio_entry.insert(tk.END, audio_path)

def browse_model():
    model_path = filedialog.askopenfilename(title="Select model file", filetypes=[("Model files", "*.pt")])
    model_entry.delete(0, tk.END)
    model_entry.insert(tk.END, model_path)

def browse_output():
    output_folder = filedialog.askdirectory(title="Select output folder")
    output_entry.delete(0, tk.END)
    output_entry.insert(tk.END, output_folder)

def start_transcription():
    # Get the input values from the GUI
    audio_file = audio_entry.get()
    model_file = model_entry.get()
    output_folder = output_entry.get()
    output_format = format_var.get()

    # Call the main function from the original script with the appropriate arguments
    # You may need to modify the original script to accept input arguments directly
    transcribe(audio_file, model_file, output_folder, output_format)

# Initialize main window
window = tk.Tk()
window.title("Whisper Audio Transcription")

# Create and place labels, entries, and buttons
audio_label = tk.Label(window, text="Audio file:")
audio_label.grid(row=0, column=0, sticky="w")
audio_entry = tk.Entry(window, width=40)
audio_entry.grid(row=0, column=1)
audio_button = tk.Button(window, text="Browse", command=browse_audio)
audio_button.grid(row=0, column=2)

model_label = tk.Label(window, text="Model file:")
model_label.grid(row=1, column=0, sticky="w")
model_entry = tk.Entry(window, width=40)
model_entry.grid(row=1, column=1)
model_button = tk.Button(window, text="Browse", command=browse_model)
model_button.grid(row=1, column=2)

output_label = tk.Label(window, text="Output folder:")
output_label.grid(row=2, column=0, sticky="w")
output_entry = tk.Entry(window, width=40)
output_entry.grid(row=2, column=1)
output_button = tk.Button(window, text="Browse", command=browse_output)
output_button.grid(row=2, column=2)

format_label = tk.Label(window, text="Output format:")
format_label.grid(row=3, column=0, sticky="w")
format_var = tk.StringVar(window)
format_var.set("json")
format_menu = tk.OptionMenu(window, format_var, "json", "text", "csv")
format_menu.grid(row=3, column=1)

transcribe_button = tk.Button(window, text="Start Transcription", command=start_transcription)
transcribe_button.grid(row=4, column=0, columnspan=3)

# Start the main event loop
window.mainloop()
