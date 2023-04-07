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
from tkinter import messagebox
from PIL import Image 

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
def batch_process(file_path, output_dir, gimp_path, profile_data, output_format, q):
    icc_path = profile_data["path"]
    black_point_compensation = profile_data["black_point_compensation"]
    rendering_intent = profile_data["rendering_intent"] 

    # Construct the output file path
    filename = os.path.basename(file_path)
    profile_name, _ = os.path.splitext(filename)
    output_path = os.path.join(output_dir, profile_name + output_format) 

    # Run the GIMP command to perform the color conversion
    gimp_command = [gimp_path, "-i", "-b",
                    '(python-fu-color-conversion "{}" "{}" "{}" {} {})'.format(
                        file_path, output_path, icc_path, black_point_compensation, rendering_intent),
                    "-b", "(gimp-quit 0)"]
    try:
        subprocess.run(gimp_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f'Color conversion of {file_path} completed successfully.')
    except subprocess.CalledProcessError as error:
        logging.error(f'Error occurred while processing {file_path}: {error}')
    except Exception as e:
        logging.error(f'Error occurred while processing {file_path}: {e}')
    finally:
        q.task_done()


# Define the worker function for multithreading
def worker(q):
    while True:
        task = q.get()
        if task is None:
            break
        file_path, output_dir, gimp_path, profile_data, output_format = task
        batch_process(file_path, output_dir, gimp_path, profile_data, output_format, q)


class ColorConversionTool(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Color Conversion Tool") 

        self.input_folder_entry = tk.Entry(self.master, width=50)
        self.input_folder_entry.grid(row=0, column=0, padx=5, pady=5) 

        self.create_widgets()
        self.q = Queue()
        self.preview_image = None 

    def browse_input_folder(self):
        folder = fd.askdirectory()
        if folder:
            self.input_folder_entry.delete(0, tk.END)
            self.input_folder_entry.insert(tk.END, folder) 

    def browse_output_folder(self):
        folder = fd.askdirectory()
        if folder:
            self.output_folder_entry.delete(0        , tk.END)
        self.output_folder_entry.insert(tk.END, folder) 

def browse_gimp_path(self):
    path = fd.askopenfilename(filetypes=[("GIMP Executable", "gimp*")])
    if path:
        self.gimp_path_entry.delete(0, tk.END)
        self.gimp_path_entry.insert(tk.END, path) 

def browse_profile(self, profile_name):
    path = fd.askopenfilename(filetypes=[("ICC Profile", "*.icc")])
    if path:
        self.profile_entry_dict[profile_name].delete(0, tk.END)
        self.profile_entry_dict[profile_name].insert(tk.END, path) 

def validate_input(self):
    input_dir = self.input_folder_entry.get()
    output_dir = self.output_folder_entry.get()
    if not os.path.isdir(input_dir):
        logging.error(f'Invalid input directory')
        self.status_bar.config(text='Invalid input directory')
        return False
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            logging.error(f'Error creating output directory: {e}')
            self.status_bar.config(text='Error creating output directory')
            return False
    gimp_path = self.gimp_path_entry.get()
    if not os.path.isfile(gimp_path):
        logging.error(f'Invalid GIMP executable path')
        self.status_bar.config(text='Invalid GIMP executable path')
        return False
    return True 

def process_files(self):
    if not self.validate_input():
        return
    input_dir = self.input_folder_entry.get()
    output_dir = self.output_folder_entry.get()
    batch_size = int(self.batch_size_entry.get())
    num_threads = int(self.num_threads_entry.get())
    output_format = self.output_format_var.get() 

    # Set up progress bar
    total_files = len(self.file_list) * len(default_profiles)
    self.progress_var["maximum"] = total_files
    self.progress_var["value"] = 0 

    # Set up the worker threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(self.q,))
        t.start()
        threads.append(t) 

    # Process files
    for file_path in self.file_list:
        for profile_name, profile_data in default_profiles.items():
            profile_dir = os.path.join(output_dir, profile_name)
            os.makedirs(profile_dir, exist_ok=True)
            if os.path.splitext(os.path.basename(file_path))[0] == profile_name:
                self.q.put((file_path, profile_dir, self.gimp_path_entry.get(), profile_data, output_format)) 

    # Block until all tasks are done
    self.q.join() 

    # Stop the worker threads
    for _ in range(num_threads):
        self.q.put(None)
    for t in threads:
        t.join() 

    self.status_bar.config(text='Processing complete') 

def select_files(self):
    input_dir = self.input_folder_entry.get()
    self.file_list = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith((".jpg", ".jpeg", ".png", ".gif")):
            file_path = os.path.join(input_dir, file_name)
            self.file_list.append(file_path) 

def preview_conversion(self):
    if not self.validate_input():
        return 

    # Get the first file in the list
    file_path = self.file_list[0] if self.file_list else None
    if not file_path:
        messagebox.showerror("Error", "No valid image files found in the input directory.")
        return 

    # Perform a color conversion on the selected file
    profile_name = self.preview_profile_var.get()
    profile 

    data = default_profiles[profile_name]
    output_dir = os.path.join(self.input_folder_entry.get(), "preview")
    os.makedirs(output_dir, exist_ok=True) 

    preview_output_format = ".png"
    batch_process(file_path, output_dir, self.gimp_path_entry.get(), profile_data, preview_output_format, self.q) 

    # Load and display the preview image
    preview_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + preview_output_format)
    try:
        self.preview_image = Image.open(preview_file_path)
        self.preview_image.show()
    except Exception as e:
        logging.error(f'Error displaying preview image: {e}')
        self.status_bar.config(text='Error displaying preview image') 

def create_widgets(self):
    input_folder_label = tk.Label(self.master, text="Input Folder:")
    input_folder_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
    input_folder_button = tk.Button(self.master, text="Browse", command=self.browse_input_folder)
    input_folder_button.grid(row=0, column=2, padx=5, pady=5) 

    self.output_folder_entry = tk.Entry(self.master, width=50)
    self.output_folder_entry.grid(row=1, column=1, padx=5, pady=5)
    output_folder_label = tk.Label(self.master, text="Output Folder:")
    output_folder_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    output_folder_button = tk.Button(self.master, text="Browse", command=self.browse_output_folder)
    output_folder_button.grid(row=1, column=2, padx=5, pady=5) 

    self.gimp_path_entry = tk.Entry(self.master, width=50)
    self.gimp_path_entry.grid(row=2, column=1, padx=5, pady=5)
    self.gimp_path_entry.insert(tk.END, default_gimp_path)
    gimp_path_label = tk.Label(self.master, text="GIMP Path:")
    gimp_path_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
    gimp_path_button = tk.Button(self.master, text="Browse", command=self.browse_gimp_path)
    gimp_path_button.grid(row=2, column=2, padx=5, pady=5) 

    profile_label = tk.Label(self.master, text="Profiles:")
    profile_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.profile_entry_dict = {}
    for idx, profile_name in enumerate(default_profiles.keys()):
        profile_entry = tk.Entry(self.master, width=50)
        profile_entry.grid(row=3+idx, column=1, padx=5, pady=5)
        profile_entry.insert(tk.END, default_profiles[profile_name]["path"])
        profile_button = tk.Button(self.master, text="Browse", command=lambda p_name=profile_name: self.browse_profile(p_name))
        profile_button.grid(row=3+idx, column=2, padx=5, pady=5)
        self.profile_entry_dict[profile_name] = profile_entry 

    self.batch_size_entry = tk.Entry(self.master, width=10)
    self.batch_size_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")
    batch_size_label = tk.Label(self.master, text="Batch Size:")
    batch_size_label.grid(row=7, column=0, sticky="e", padx=5, pady=5)
    self.batch_size_entry.insert(tk.END, "1") 

    self.num_threads_entry = tk.Entry(self.master, width=10)
    self.num_threads_entry.grid(row=8, column=1, padx=5, pady=5, sticky="w")
    num_threads_label = tk.Label(self.master, text="Number of Threads:")
    num_threads_label.grid(row=8, column=0, sticky="e", padx=5, pady=5)
    self.num_threads_entry.insert(tk.END, "1") 

    self.output_format_var = tk.StringVar(self.master)
    self.output_format_var.set(".jpg")
    output_format_label = tk.Label(self.master, text="Output Format:")
    output_format_label.grid(row=9, column=0, sticky="e", padx=5, pady=5)
    output_format_options = (".jpg", ".jpeg", ".png", ".gif")
    output_format_menu = tk.OptionMenu(self.master, self.output_format_var, *output_format_options)
    output_format_menu.grid(row=9, column=1, padx=5, pady=5, sticky="w") 

    self.preview_profile_var = tk.StringVar(self.master)
    self.preview_profile_var.set("sRGB")
    preview_profile_label = tk.Label(self.master, text="Preview Profile:")
    preview_profile_label.grid(row=10, column=0, sticky="e", padx=5, pady=5)
    preview_profile_options = default_profiles.keys()
    preview_profile_menu = tk.OptionMenu(self.master, self.preview_profile_var, *preview_profile_options)
    preview_profile_menu.grid(row=10, column=1, padx=5, pady=5, sticky="w") 

    self.progress_var = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="determinate")
    self.progress_var.grid(row=11, column=1, padx=5, pady=5, sticky="w")
    progress_label = tk.Label(self.master, text="Progress:")
    progress_label.grid(row=11, column=0, sticky="e", padx=5, pady=5) 

    process_button = tk.Button(self.master, text="Process Files", command=self.process_files)
    process_button.grid(row=12, column=1, padx=5, pady=5, sticky="w") 

    preview_button = tk.Button(self.master, text="Preview Conversion", command=self.preview_conversion)
    preview_button.grid(row=12, column=1, padx=5, pady=5) 

    self.status_bar = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    self.status_bar.grid(row=13, column=0, columnspan=3, sticky="we") 

def run(self):
    self.pack()
    self.select_files()
    self.master.mainloop() 

if name == "main": root = tk.Tk() app = ColorConversionTool(master=root) app.run()
