import os
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk
from skimage.metrics import structural_similarity

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

def open_original_image():
    """Function to open the original image"""
    global original_image, original_image_tk, original_path

    original_path = filedialog.askopenfilename(title="Select Original Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))

    original_image = Image.open(original_path).convert("RGB")
    original_image_tk = ImageTk.PhotoImage(original_image)
    original_image_label.config(image=original_image_tk)

    # Calculate and display grade
    grade = calculate_grade(original_image, upscaled_image)
    grade_label.config(text="Grade: {:.2f}".format(grade))

original_button = tk.Button(original_frame, text="Select Image", command=open_original_image)

def open_upscaled_image():
    """Function to open the upscaled image"""
    global upscaled_image, upscaled_image_tk, upscaled_path

    upscaled_path = filedialog.askopenfilename(title="Select Upscaled Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"),))

    upscaled_image = Image.open(upscaled_path).convert("RGB")
    upscaled_image_tk = ImageTk.PhotoImage(upscaled_image)
    upscaled_image_label.config(image=upscaled_image_tk)

    # Calculate and display grade
    grade = calculate_grade(original_image, upscaled_image)
    grade_label.config(text="Grade: {:.2f}".format(grade))

upscaled_button = tk.Button(upscaled_frame, text="Select Image", command=open_upscaled_image)


file_menu.add_command(label="Open", command=open_image)
file_menu.add_command(label="Exit", command=window.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
window.config(menu=menu_bar)

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

    # Update grade label
    grade_label.config(text="Grade: {:.2f}".format(grade))
