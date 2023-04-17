import os
import shutil
import numpy as np
from PIL import Image 

def is_neon_or_pastel(color):
    # Adjust the thresholds according to your specific requirements
    r, g, b = color
    if r > 200 and (g < 100 or b < 100):
        return True
    if g > 200 and (r < 100 or b < 100):
        return True
    if b > 200 and (r < 100 or g < 100):
        return True
    if r > 200 and g > 200 and b > 200:
        return True
    return False 

def analyze_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img_data = np.array(img) 

    total_pixels = img_data.shape[0] * img_data.shape[1] 

    reds = img_data[:, :, 0] > 200
    greens = img_data[:, :, 1] > 200
    blues = img_data[:, :, 2] > 200 

    neon_red = np.logical_and(reds, np.logical_or(img_data[:, :, 1] < 100, img_data[:, :, 2] < 100))
    neon_green = np.logical_and(greens, np.logical_or(img_data[:, :, 0] < 100, img_data[:, :, 2] < 100))
    neon_blue = np.logical_and(blues, np.logical_or(img_data[:, :, 0] < 100, img_data[:, :, 1] < 100)) 

    pastel_colors = np.logical_and(reds, np.logical_and(greens, blues)) 

    neon_pastel_colors = np.logical_or(neon_red, np.logical_or(neon_green, np.logical_or(neon_blue, pastel_colors))) 

    neon_pastel_pixels = np.sum(neon_pastel_colors)
    percentage = (neon_pastel_pixels / total_pixels) * 100 

    return percentage 

def organize_images(folder_path):
    image_extensions = {'.png', '.jpg', '.jpeg'}
    for filename in os.listdir(folder_path):
        if os.path.splitext(filename)[1].lower() in image_extensions:
            image_path = os.path.join(folder_path, filename)
            percentage = analyze_image(image_path) 

            # Define the subfolder based on the percentage
            if percentage < 5:
                subfolder = "minimal"
            elif percentage < 15:
                subfolder = "low"
            elif percentage < 30:
                subfolder = "medium"
            else:
                subfolder = "high" 

            # Create the subfolder if it doesn't exist
            subfolder_path = os.path.join(folder_path, subfolder)
            os.makedirs(subfolder_path, exist_ok=True) 

            # Move the image to the subfolder
            shutil.move(image_path, os.path.join(subfolder_path, filename)) 

if __name__ == "__main__":
    folder_path = "path/to/your/folder"
    organize_images(folder_path)
