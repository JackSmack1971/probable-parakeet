import os
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from skimage.measure import compare_ssim 

# Global variables
original_image = None
upscaled_image = None
original_image_tk = None
upscaled_image_tk = None
original_path = None
upscaled_path = None
MSE_WEIGHT = 0.4
PSNR_WEIGHT = 0.3
SSIM_WEIGHT = 0.3
# Create GUI window
window = tk.Tk()
window.title("Image Quality Evaluator") 

# Create widgets
original_image_label = tk.Label(window, text="Original Image")
upscaled_image_label = tk.Label(window, text="Upscaled Image")
grade_label = tk.Label(window, text="Grade: -")
original_image_label.pack()
upscaled_image_label.pack()
grade_label.pack() 

# Create menu bar
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_image)
file_menu.add_command(label="Exit", command=window.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
window.config(menu=menu_bar)
def open_image():
    """Function to open original and upscaled images"""
    global original_image, upscaled_image, original_image_tk, upscaled_image_tk, original_path, upscaled_path
    
    # Open original image
    original_path = filedialog.askopenfilename(title="Select Original Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))
    original_image = Image.open(original_path).convert("RGB")
    original_image_tk = ImageTk.PhotoImage(original_image)
    original_image_label.config(image=original_image_tk)
    
    # Open upscaled image
    upscaled_path = filedialog.askopenfilename(title="Select Upscaled Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))
    upscaled_image = Image.open(upscaled_path).convert("RGB")
    upscaled_image_tk = ImageTk.PhotoImage(upscaled_image)
    upscaled_image_label.config(image=upscaled_image_tk)
    
    # Calculate and display grade
    grade = calculate_grade(original_image, upscaled_image)
    grade_label.config(text="Grade: {:.2f}".format(grade))
def calculate_grade(original_image, upscaled_image):
    """Function to calculate the grade for the upscaled image"""
    # Calculate PSNR
    mse = calculate_mse(original_image, upscaled_image)
    psnr = calculate_psnr(mse)
    
    # Calculate SSIM
    ssim = calculate_ssim(original_image, upscaled_image)
    
    # Normalize metrics to a common range
    psnr_norm = psnr / 100
    ssim_norm = (ssim + 1) / 2
    mse_norm = 1 / (mse + 1)
    
    # Calculate grade
    grade = (psnr_norm * PSNR_WEIGHT) + (ssim_norm * SSIM_WEIGHT) + (mse_norm * MSE_WEIGHT)
    
    return grade
def normalize_scores(scores, variance):
    """
    Function to normalize a list of scores by their variance.
    """
    norm_scores = []
    for score in scores:
        norm_scores.append((score - np.mean(scores)) / math.sqrt(variance))
    return norm_scores


def calculate_weighted_grade(mse_scores, psnr_scores, ssim_scores):
    """
    Function to calculate the weighted grade for a set of images based on their
    MSE, PSNR, and SSIM scores.
    """
    # Calculate means
    mse_mean = np.mean(mse_scores)
    psnr_mean = np.mean(psnr_scores)
    ssim_mean = np.mean(ssim_scores) 

    # Calculate variances
    mse_var = np.var(mse_scores)
    psnr_var = np.var(psnr_scores)
    ssim_var = np.var(ssim_scores) 

    # Normalize scores
    mse_norm = normalize_scores(mse_scores, mse_var)
    psnr_norm = normalize_scores(psnr_scores, psnr_var)
    ssim_norm = normalize_scores(ssim_scores, ssim_var) 

    # Calculate weighted grade
    grade = (mse_norm * MSE_WEIGHT) + (psnr_norm * PSNR_WEIGHT) + (ssim_norm * SSIM_WEIGHT) 

    return grade
def normalize_scores(scores, var):
    """
    Function to normalize scores to a common range using min-max normalization.
    """
    norm_scores = (scores - np.mean(scores)) / np.sqrt(var)
    return norm_scores


def calculate_grade(original_image, upscaled_image):
    """
    Function to calculate the grade for the upscaled image.
    """
    # Calculate metrics
    mse_scores, psnr_scores, ssim_scores = calculate_metrics(original_image, upscaled_image) 

    # Calculate means
    mu1 = original_image.convert("L").getchannel(0).getdata().mean()
    mu2 = upscaled_image.convert("L").getchannel(0).getdata().mean() 

    # Calculate variances
    mse_var = np.var(mse_scores)
    psnr_var = np.var(psnr_scores)
    ssim_var = np.var(ssim_scores) 

    # Normalize scores
    mse_norm = normalize_scores(mse_scores, mse_var)
    psnr_norm = normalize_scores(psnr_scores, psnr_var)
    ssim_norm = normalize_scores(ssim_scores, ssim_var) 

    # Calculate weighted grade
    grade = (mse_norm * MSE_WEIGHT) + (psnr_norm * PSNR_WEIGHT) + (ssim_norm * SSIM_WEIGHT) 

    return grade
def normalize_scores(scores, var):
    """Function to normalize a list of scores"""
    std_dev = math.sqrt(var)
    normalized_scores = [(score - np.mean(scores)) / std_dev for score in scores]
    return normalized_scores 

def calculate_grade(original_image, upscaled_image):
    """Function to calculate the grade for the upscaled image"""
    # Calculate PSNR
    mse = calculate_mse(original_image, upscaled_image)
    psnr = calculate_psnr(mse) 

    # Calculate SSIM
    ssim = calculate_ssim(original_image, upscaled_image) 

    # Normalize metrics to a common range
    psnr_norm = psnr / 100
    ssim_norm = (ssim + 1) / 2
    mse_norm = 1 / (mse + 1) 

    # Calculate grade
    grade = (psnr_norm * PSNR_WEIGHT) + (ssim_norm * SSIM_WEIGHT) + (mse_norm * MSE_WEIGHT) 

    return grade 

def open_image():
    """Function to open original and upscaled images"""
    global original_image, upscaled_image, original_image_tk, upscaled_image_tk, original_path, upscaled_path 

    # Open original image
    original_path = filedialog.askopenfilename(title="Select Original Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))
    original_image = Image.open(original_path).convert("RGB")
    original_image_tk = ImageTk.PhotoImage(original_image)
    original_image_label.config(image=original_image_tk) 

    # Open upscaled image
    upscaled_path = filedialog.askopenfilename(title="Select Upscaled Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))
    upscaled_image = Image.open(upscaled_path).convert("RGB")
    upscaled_image_tk = ImageTk.PhotoImage(upscaled_image)
    upscaled_image_label.config(image=upscaled_image_tk) 

    # Calculate and display grade
    grade = calculate_grade(original_image, upscaled_image)
    grade_label.config(text="Grade: {:.2f}".format(grade))
def normalize_scores(scores, var):
    """Function to normalize scores based on variance"""
    return (scores - scores.mean()) / math.sqrt(var)
def normalize_scores(scores, variance):
    """Function to normalize scores to range [0, 1]"""
    std_dev = math.sqrt(variance)
    normalized_scores = [(s - np.mean(scores)) / std_dev for s in scores]
    return np.array(normalized_scores) 

def main():
    """Function to create and run the GUI"""
    global original_image_label, upscaled_image_label, grade_label 

    # Create GUI window
    window = tk.Tk()
    window.title("Image Quality Evaluator") 

    # Create frame for original image
    original_frame = tk.Frame(window)
    original_frame.pack(side="left") 

    # Create label for original image
    original_label = tk.Label(original_frame, text="Original Image")
    original_label.pack() 

    # Create label for original image display
    original_image_label = tk.Label(original_frame)
    original_image_label.pack() 

    # Create button to select original image
    original_button = tk.Button(original_frame, text="Select Image", command=open_image)
    original_button.pack() 

    # Create frame for upscaled image
    upscaled_frame = tk.Frame(window)
    upscaled_frame.pack(side="left") 

    # Create label for upscaled image
    upscaled_label = tk.Label(upscaled_frame, text="Upscaled Image")
    upscaled_label.pack() 

    # Create label for upscaled image display
    upscaled_image_label = tk.Label(upscaled_frame)
    upscaled_image_label.pack() 

    # Create button to select upscaled image
    upscaled_button = tk.Button(upscaled_frame, text="Select Image", command=open_image)
    upscaled_button.pack() 

    # Create frame for grade
    grade_frame = tk.Frame(window)
    grade_frame.pack() 

    # Create label for grade
    grade_label = tk.Label(grade_frame, text="Grade: ")
    grade_label.pack() 

    # Run GUI
    window.mainloop() 

if __name__ == "__main__":
    main()
# Create Tkinter GUI
root = tk.Tk()
root.title("Image Quality Assessment") 

# Create widgets
original_image_label = tk.Label(root, text="Original Image", font=("TkDefaultFont", 16))
upscaled_image_label = tk.Label(root, text="Upscaled Image", font=("TkDefaultFont", 16))
grade_label = tk.Label(root, text="Grade: 0.00", font=("TkDefaultFont", 16))
open_button = tk.Button(root, text="Open Images", font=("TkDefaultFont", 16), command=open_image) 

# Grid widgets
original_image_label.grid(row=0, column=0)
upscaled_image_label.grid(row=0, column=1)
grade_label.grid(row=1, column=0, columnspan=2)
open_button.grid(row=2, column=0, columnspan=2) 

# Define weights for weighted grade calculation
MSE_WEIGHT = 0.4
PSNR_WEIGHT = 0.4
SSIM_WEIGHT = 0.2 

# Start GUI
root.mainloop()
