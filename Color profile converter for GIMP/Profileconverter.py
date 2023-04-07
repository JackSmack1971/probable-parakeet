import os
import threading
import tkinter as tk
import tkinter.filedialog as fd
from queue import Queue
import logging
from pathlib import Path
import concurrent.futures
import subprocess
import time
from tkinter import ttk


# Define the default paths to the GIMP executable and the color profiles
default_gimp_path = "path/to/gimp/executable"
default_profiles = {
    "CMYK": {"path": "path/to/GRACoL2006_Coated1v2.icc", "black_point_compensation": 0, "rendering_intent": 2},
    "sRGB": {"path": "path/to/sRGB.icc", "black_point_compensation": 0, "rendering_intent": 0},
    "AdobeRGB": {"path": "path/to/AdobeRGB1998.icc", "black_point_compensation": 0, "rendering_intent": 0}
} 

# Set up logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, filename='color_conversion_tool.log') 

# Define the batch processing function
def batch_process(file_path, output_dir, gimp_path, profile_data, progress_var):
    icc_path = profile_data["path"]
    black_point_compensation = profile_data["black_point_compensation"]
    rendering_intent = profile_data["rendering_intent"] 

    # Construct the output file path
    filename = os.path.basename(file_path)
    profile_name = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, profile_name, filename) 

    # Run the GIMP command to perform the color conversion
    gimp_command = [gimp_path, "-i", "-b",
                    '(python-fu-color-conversion "{}" "{}" "{}" {} {})'.format(
                        file_path, output_path, icc_path, black_point_compensation, rendering_intent),
                    "-b", "(gimp-quit 0)"]
    try:
        subprocess.run(gimp_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f'Color conversion of {file_path} completed successfully.')
        progress_var.step(1)
    except subprocess.CalledProcessError as error:
        logging.error(f'Error occurred while processing {file_path}: {error}')
        print(f'Error occurred while processing {file_path}: {error}') 

# Define the worker function for multithreading
def worker():
    while True:
        file_path, output_dir, gimp_path, profile_data, progress_var = q.get()
        batch_process(file_path, output_dir, gimp_path, profile_data, progress_var)
        q.task_done() 

# Define the GUI functions
def browse_input_folder():
    folder = fd.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(tk.END, folder) 

def browse_output_folder():
    folder = fd.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(tk.END, folder) 

def browse_gimp_path():
    path = fd.askopenfilename(filetypes=[("GIMP Executable", "gimp*")])
    gimp_path_entry.delete(0, tk.END)
    gimp_path_entry.insert(tk.END, path) 

def browse_profile(profile_name):
    path = fd.askopenfilename(filetypes=[("ICC Profile", "*.icc")])
    profile_entry_dict[profile_name].delete(0, tk.END) 

def process_files(): input_dir = input_folder_entry.get() output_dir = output_folder_entry.get() 

# Validate input and output directories
if not os.path.isdir(input_dir):
    logging.error(f'Invalid input directory')
    print('Invalid input directory')
    return
if not os.path.exists(output_dir):
    try:
        os.makedirs(output_dir)
    except Exception as e:
        logging.error(f'Error creating output directory: {e}')
        print('Error creating output directory')
        return 

# Create the subfolders for each color profile
for profile_name in default_profiles:
    profile_dir = os.path.join(output_dir, profile_name)
    if not os.path.exists(profile_dir):
        try:
            os.makedirs(profile_dir)
        except Exception as e:
            logging.error(f'Error creating {profile_name} profile directory: {e}')
            print(f'Error creating {profile_name} profile directory')
            return 

file_list = []
for file_name in os.listdir(input_dir):
    if file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png") or file_name.endswith(".gif"):
        file_path = os.path.join(input_dir, file_name)
        file_list.append(file_path) 

# Set batch size and number of threads
batch_size = int(batch_size_entry.get())
num_threads = int(num_threads_entry.get()) 

# Set up progress bar
total_files = len(file_list) * len(default_profiles)
progress_var = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_var.grid(row=8+len(default_profiles), column=0, columnspan=3, padx=5, pady=5, sticky=tk.W) 

# Process files
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    for file_path in file_list:
        for profile_name, profile_data in default_profiles.items():
            if os.path.splitext(os.path.basename(file_path))[0] == profile_name:
                executor.submit(batch_process, file_path, os.path.join(output_dir, profile_name), gimp_path_entry.get(), profile_data, progress_var)
                break 

root = tk.Tk() root.title("Color Conversion Tool") 

input_folder_entry = tk.Entry(root, width=50) input_folder_entry.grid(row=0, column=0, padx=5, pady=5) 

browse_input_button = tk.Button(root, text="Browse Input Folder", command=browse_input_folder) browse_input_button.grid(row=0, column=1, padx=5, pady=5) 

output_folder_entry = tk.Entry(root, width=50) output_folder_entry.grid(row=1, column=0, padx=5, pady=5) 

browse_output_button = tk.Button(root, text="Browse Output Folder", command=browse_output_folder) browse_output_button.grid(row=1, column=1, padx=5, pady=5) 

gimp_path_entry = tk.Entry(root, width=50) gimp_path_entry.insert(tk.END, default_gimp_path) gimp_path_entry.grid(row=2, column=0, padx=5, pady=5) 

browse_gimp_button = tk.Button(root, text="Browse GIMP Path", command=browse_gimp_path) browse_gimp_button.grid(row=2, column=1, padx=5, pady=5) 

batch_size_label = tk.Label(root, text="Batch Size:") batch_size_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W) 

batch_size_entry = tk.Entry(root, width=10) batch_size_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W) batch_size_entry.insert(tk.END, "10") 

num_threads_label = tk.Label(root, text="Number of Threads:") num_threads_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W) 

num_threads_entry = tk.Entry(root, width=10) num_threads_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W) num_threads_entry.insert(tk.END, "4") 

profile_entry_dict = {} for i, profile_name in enumerate(default_profiles): label = tk.Label(root, text=profile_name + " Profile:") label.grid(row=5+i, column=0, padx=5, pady=5, sticky=tk.W) 

profile_entry_dict[profile_name] = tk.Entry(root, width=50)
profile_entry_dict[profile_name].insert(tk.END, default_profiles[profile_name]["path"])
profile_entry_dict[profile_name].grid(row=5+i, column=1, padx=5, pady=5, sticky=tk.W) 

browse_button = tk.Button(root, text="Browse", command=lambda profile_name=profile_name: browse_profile(profile_name))
browse_button.grid(row=5+i, column=2, padx=5, pady=5) 

process_button = tk.Button(root, text="Process Files", command=process_files) process_button.grid(row=8+len(default_profiles), column=0, padx=5, pady=5, sticky=tk.W) 

status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W) status_bar.grid(row=9+len(default_profiles), column=0, columnspan=3, sticky=tk.W+tk.E) 

q = Queue(maxsize=0) 

root.mainloop()
