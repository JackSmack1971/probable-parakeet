import os
import logging
import concurrent.futures
from typing import Tuple, List
import argparse 

import numpy as np
import tensorflow as tf
from PIL import Image
from skimage.transform import resize


# Constants
VALID_IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp')
CONFIG_FILE = 'config.json'


# Utility functions
def get_cpu_specifications() -> Tuple[int, float]:
    """Returns the number of logical CPUs and the maximum CPU frequency."""
    cpu_count: int = os.cpu_count() or 1
    cpu_freq: float = os.cpu_count() or psutil.cpu_freq().max
    return cpu_count, cpu_freq


def select_upscaling_method(num_cpus: int, max_cpu_freq: float) -> str:
    """Selects the upscaling method to use based on CPU specifications."""
    if max_cpu_freq > 2500 and num_cpus > 4:
        upscaling_method: str = "EDSR"
    else:
        upscaling_method: str = "SRCNN"
    return upscaling_method


def calculate_resized_image_size(image_size: Tuple[int, int], canvas_size: Tuple[int, int]) -> Tuple[int, int]:
    """Calculates the new size of an image after upscaling it to fit inside a canvas of a certain size."""
    canvas_ratio: float = canvas_size[0] / canvas_size[1]
    image_ratio: float = image_size[0] / image_size[1]
    if image_ratio > canvas_ratio:
        new_width: int = canvas_size[0]
        new_height: int = int(new_width / image_ratio)
    elif image_ratio < canvas_ratio:
        new_height: int = canvas_size[1]
        new_width: int = int(new_height * image_ratio)
    else:
        new_width: int = canvas_size[0]
        new_height: int = canvas_size[1]
    return (new_width, new_height)


def resize_image(image: Image, new_size: Tuple[int, int], model=None) -> Image:
    """Resizes an image to a new size using the EDSR upscaling method."""
    image_array = np.array(image)
    resized_image = edsr_sr(model, image_array, new_size)
    resized_image = Image.fromarray((resized_image * 255).astype(np.uint8))
    return resized_image
def edsr(scale=4, num_res_blocks=16, num_filters=64, res_block_scaling=None):
    """Creates an EDSR model."""
    inputs = tf.keras.Input(shape=(None, None, 3))
    x = tf.keras.layers.Conv2D(num_filters, 3, padding='same')(inputs)
    x_temp = x
    for i in range(num_res_blocks):
        x = res_block(x, num_filters, 3)
    if res_block_scaling is not None:
        x = tf.keras.layers.Add()([x_temp, x]) * res_block_scaling
    else:
        x = tf.keras.layers.Add()([x_temp, x])
    for i in range(int(scale / 2)):
        x = tf.keras.layers.Conv2D(num_filters * 4, 3, padding='same')(x)
        x = tf.keras.layers.Conv2D(num_filters * 4, 3, padding='same')(x)
        x = tf.keras.layers.Conv2D(num_filters, 3, padding='same')(x)
    x = tf.keras.layers.Conv2D(3, 3, padding='same')(x)
    model = tf.keras.Model(inputs, x)
    return model


def res_block(inputs, num_filters, kernel_size):
    """Creates a residual block for the EDSR model."""
    x = tf.keras.layers.Conv2D(num_filters, kernel_size, padding='same')(inputs)
    x = tf.keras.layers.Activation('relu')(x)
    x = tf.keras.layers.Conv2D(num_filters, kernel_size, padding='same')(x)
    x = tf.keras.layers.Add()([inputs, x])
    return x


def edsr_sr(model, image, new_size):
    """Performs EDSR upscaling on an image."""
    scale = new_size[0] // image.shape[1]
    input_shape = (image.shape[0], image.shape[1], 3)
    output_shape = (new_size[1], new_size[0], 3)
    image = np.expand_dims(image, axis=0)
    image = tf.image.resize(image, (input_shape[0] // scale, input_shape[1] // scale), method='bicubic')
    image = tf.clip_by_value(image, 0.0, 255.0)
    image = image / 255.0
    sr_image = model.predict(image)
    sr_image = sr_image * 255.0
    sr_image = tf.clip_by_value(sr_image, 0.0, 255.0)
    sr_image = sr_image[0]
    sr_image = np.clip(sr_image, 0, 255).astype('uint8')
    sr_image = resize(sr_image, output_shape, order=3, mode='reflect', anti_aliasing=True)
    return sr_image
def resize_image(image: Image, new_size: Tuple[int, int], model=None) -> Image:
    """Resizes an image to a new size using the EDSR upscaling method."""
    image_array = np.array(image)
    resized_image = edsr_sr(model, image_array, new_size)
    resized_image = Image.fromarray((resized_image * 255).astype(np.uint8))
    return resized_image 

def upscale_image(input_path: str, output_path: str, upscaling_method: str, model=None, scale_factor: int = 4):
    """Upscales an image using the specified upscaling method and saves the result to an output file."""
    with Image.open(input_path) as image:
        # Calculate new size
        new_size = calculate_new_size(image.size, (image.size[0]*scale_factor, image.size[1]*scale_factor))
        
        # Resize image
        resized_image = resize_image(image, new_size, upscaling_method, model=model)
        
        # Save image
        save_path = os.path.join(output_path, os.path.basename(input_path))
        resized_image.save(save_path)


def upscale_images(input_folder: str, output_folder: str, upscaling_method: str, model=None, scale_factor: int = 4):
    """Upscales all images in a folder using the specified upscaling method and saves the results to an output folder."""
    # Create output folder
    os.makedirs(output_folder, exist_ok=True) 

    # Load model if using EDSR upscaling method
    if upscaling_method == "EDSR" and not model:
        model = load_edsr_model()
    
    # Upscale images
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(VALID_IMAGE_FORMATS)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        for input_path in input_files:
            output_path = os.path.join(output_folder, os.path.basename(input_path))
            executor.submit(upscale_image, input_path, output_path, upscaling_method, model=model, scale_factor=scale_factor)
def edsr(scale=4, num_res_blocks=16, num_filters=64, res_block_scaling=None):
    """Creates an EDSR model."""
    inputs = tf.keras.Input(shape=(None, None, 3))
    x = tf.keras.layers.Conv2D(num_filters, 3, padding='same')(inputs)
    x_temp = x
    for i in range(num_res_blocks):
        x = res_block(x, num_filters, 3)
    if res_block_scaling is not None:
        x = tf.keras.layers.Add()([x_temp, x]) * res_block_scaling
    else:
        x = tf.keras.layers.Add()([x_temp, x])
    for i in range(int(scale / 2)):
        x = tf.keras.layers.Conv2D(num_filters * 4, 3, padding='same')(x)
        x = tf.keras.layers.Conv2D(num_filters * 4, 3, padding='same')(x)
        x = tf.keras.layers.Conv2D(num_filters, 3, padding='same')(x)
    x = tf.keras.layers.Conv2D(3, 3, padding='same')(x)
    model = tf.keras.Model(inputs, x)
    return model


def res_block(inputs, num_filters, kernel_size):
    """Creates a residual block for the EDSR model."""
    x = tf.keras.layers.Conv2D(num_filters, kernel_size, padding='same')(inputs)
    x = tf.keras.layers.Activation('relu')(x)
    x = tf.keras.layers.Conv2D(num_filters, kernel_size, padding='same')(x)
    x = tf.keras.layers.Add()([inputs, x])
    return x


def edsr_sr(model, image, new_size):
    """Performs EDSR upscaling on an image."""
    scale = new_size[0] // image.shape[1]
    input_shape = (image.shape[0], image.shape[1], 3)
    output_shape = (new_size[1], new_size[0], 3)
    image = np.expand_dims(image, axis=0)
    image = tf.image.resize(image, (input_shape[0] // scale, input_shape[1] // scale), method='bicubic')
    image = tf.clip_by_value(image, 0.0, 255.0)
    image = image / 255.0
    sr_image = model.predict(image)
    sr_image = sr_image * 255.0
    sr_image = tf.clip_by_value(sr_image, 0.0, 255.0)
    sr_image = sr_image[0]
    sr_image = np.clip(sr_image, 0, 255).astype('uint8')
    sr_image = resize(sr_image, output_shape, order=3, mode='reflect', anti_aliasing=True)
    return sr_image


def load_edsr_model() -> tf.keras.Model:
    """Loads a pre-trained EDSR model."""
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
    else:
        model = train_edsr()
    return model


def train_edsr(num_res_blocks: int = 16, num_filters: int = 64, res_block_scaling=None, batch_size: int = 32, epochs: int = 100) -> tf.keras.Model:
    """Trains an EDSR model on the DIV2K dataset."""
    # TODO: Implement training function
    pass
def main():
    """Main function that handles program logic."""
    parser = argparse.ArgumentParser(description="Image upscaler")
    parser.add_argument("input", help="Path to input image or directory")
    parser.add_argument("output", help="Path to output directory")
    parser.add_argument("--method", choices=["nearest", "bilinear", "bicubic", "lanczos", "edsr"], default="nearest",
                        help="Upscaling method to use (default: nearest)")
    parser.add_argument("--scale", type=int, default=4, help="Scale factor for upscaling (default: 4)")
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration (default: False)") 

    args = parser.parse_args() 

    # Check if input is a file or directory
    input_path = args.input
    if os.path.isfile(input_path):
        input_files = [input_path]
    elif os.path.isdir(input_path):
        input_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(VALID_IMAGE_FORMATS)]
    else:
        print("Invalid input path")
        return 

    # Check if output directory exists
    output_path = args.output
    if not os.path.isdir(output_path):
        print("Output directory does not exist")
        return 

    # Set upscaling method
    if args.method == "edsr":
        upscaling_method = "EDSR"
    else:
        upscaling_method = args.method 

    # Use GPU if specified
    if args.gpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        gpus = tf.config.experimental.list_physical_devices("GPU")
        tf.config.experimental.set_memory_growth(gpus[0], True) 

    # Upscale images
    if upscaling_method == "EDSR":
        model = load_edsr_model()
        upscale_images(input_files, output_path, upscaling_method, model=model, scale_factor=args.scale)
    else:
        upscale_images(input_path, output_path, upscaling_method, scale_factor=args.scale) 

if __name__ == "__main__":
    main()
