import os 
import sys 
import cv2 
import json 
import shutil 
import random 
import argparse 
import numpy as np from pathlib 
import Path from skimage 
import io from tqdm 
import tqdm from typing 
import List, Tuple, Union from sklearn.model_selection 
import train_test_split 
import logging 

def parse_args() -> argparse.Namespace: parser = argparse.ArgumentParser(description='Process datasets and apply data augmentation.') parser.add_argument('--config', type=str, required=True, help='Path to the configuration file 

args = parser.parse_args() 

# Validate that the config file is a valid JSON file
config_file = Path(args.config)
if not config_file.is_file() or config_file.suffix != '.json':
    raise ValueError(f"Invalid config file: {config_file}") 

return args 

def load_config(config_path: Union[str, Path]) -> dict: with open(config_path, 'r') as f: config = json.load(f) return config 

def preprocess_image(img_path: Union[str, Path], target_format: str = 'PNG') -> np.ndarray: """ Load and preprocess an image file. 

Args:
    img_path (Union[str, Path]): The path to the input image file.
    target_format (str): The desired output image format. 

Returns:
    np.ndarray: The preprocessed image array.
"""
logger = logging.getLogger(__name__)
try:
    img = io.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB) if target_format == 'PNG' else img
    return img
except Exception as e:
    logger.exception(f"Error loading image file: {img_path}")
    raise 

def random_rotation(img: np.ndarray, rotation_range: int = 10) -> np.ndarray: """ Apply a random rotation to an image. 

Args:
    img (np.ndarray): The input image array.
    rotation_range (int): The maximum rotation angle in degrees. 

Returns:
    np.ndarray: The rotated image array.
"""
angle = np.random.uniform(-rotation_range, rotation_range)
height, width = img.shape[:2]
center = (width // 2, height // 2)
rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
return cv2.warpAffine(img, rotation_matrix, (width, height)) 

def random_brightness(img: np.ndarray, brightness_range: float = 0.2) -> np.ndarray: """ Apply a random brightness adjustment to an image. 

Args:
    img (np.ndarray): The input image array.
    brightness_range (float): The maximum brightness adjustment range. 

Returns:
    np.ndarray: The brightness-adjusted image array.
"""
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
hsv = np.float32(hsv)
hsv[:, :, 2] *= np.random.uniform(1 - brightness_range, 1 + brightness_range)
hsv = np.clip(hsv, 0, 255)
return cv2.cvtColor(np.uint8(hsv), cv2.COLOR_HSV2RGB) 

def create_augmented_images(img: np.ndarray, aug_config: dict) -> List[np.ndarray]: """ Create a list of augmented images from a single input image. 

Args:
    img (np.ndarray): The input image array.
    aug_config (dict): The data augmentation configuration. 

Returns:
    List[np.ndarray]: The list of augmented image arrays.
"""
logger = logging.getLogger(__name__)
aug_images = [img] 

try:
    if aug_config.get('horizontal_flip', False):
        aug_images.append(cv2.flip(img, 1)) 

    if aug_config.get('random_rotation', False):
        rotation_range = aug_config.get('rotation_range', 10)
        aug_images.extend([random_rotation(img, rotation_range) for img in aug_images.copy()]) 

    if aug_config.get('random_brightness', False):
        brightness_range = aug_config.get('brightness_range', 0.2)
        aug_images.extend([random_brightness(img, brightness_range) for img in aug_images.copy()])
except Exception as e 

logger.exception("Error creating augmented images")
    raise 

return aug_images 

def save_image(img: np.ndarray, output_path: Union[str, Path]) -> None: """ Save an image array to a file. 

Args:
    img (np.ndarray): The input image array.
    output_path (Union[str, Path]): The path to the output image file.
"""
cv2.imwrite(str(output_path), img) 

def get_image_files(directory: Union[str, Path], target_format: str = 'PNG') -> List[Path]: """ Get a list of image files in a directory. 

Args:
    directory (Union[str, Path]): The path to the input directory.
    target_format (str): The desired image file format. 

Returns:
    List[Path]: The list of image file paths.
"""
directory = Path(directory)
image_files = [f for f in directory.iterdir() if f.suffix.lower() == f'.{target_format.lower()}']
return image_files 

def split_datasets(combined_imgs: List[np.ndarray]) -> dict: """ Split a list of image arrays into training, validation, and test sets. 

Args:
    combined_imgs (List[np.ndarray]): The list of input image arrays. 

Returns:
    dict: The dictionary containing the split datasets.
"""
train_imgs, test_imgs = train_test_split(combined_imgs, test_size=0.2, random_state=42)
val_imgs, test_imgs = train_test_split(test_imgs, test_size=0.5, random_state=42)
return {'train': train_imgs, 'val': val_imgs, 'test': test_imgs} 

def save_images(images: List[np.ndarray], output_dir: Path, set_name: str, target_format: str = 'PNG') -> None: """ Save a list of image arrays to files. 

Args:
    images (List[np.ndarray]): The list of input image arrays.
    output_dir (Path): The path to the output directory.
    set_name (str): The name of the image set.
    target_format (str): The desired image file format.
"""
set_output_dir = output_dir / set_name
set_output_dir.mkdir(parents=True, exist_ok=True) 

for i, img in enumerate(tqdm(images, desc=f"Saving {set_name} images")):
    output_path = set_output_dir / f'{set_name}_{i:04d}.{target_format.lower()}'
    save_image(img, output_path) 

def process_datasets(dataset_dirs: List[Union[str, Path]], output_dir: Union[str, Path], target_format: str = 'PNG', aug_config: dict = None) -> None: """ Process a set of image datasets and apply data augmentation. 

Args:
    dataset_dirs (List[Union[str, Path]]): The list of input dataset directories.
    output_dir (Union[str, Path]): The path to the output directory.
    target_format (str): The desired image file format.
    aug_config (dict): The data augmentation configuration.
"""
output_dir = Path(output_dir)
output_dir.mkdir(parents=True, exist_ok=True) 

combined_imgs = [] 

for dataset_dir in dataset_dirs:
    image_files = get_image_files(dataset_dir, target_format)
    for img_path in tqdm(image_files, desc=f"Processing {dataset_dir}"):
        img = preprocess_image(img_path, target_format)
        combined_imgs.extend(create_augmented_images(img, aug_config)) 

random.shuffle(combined_imgs) 

try:
    sets = split_datasets(combined_imgs)
except Exception as e:
    logger.exception("Error splitting datasets")
    raise 

for set_name, images in sets.items():
    try:
        save_images(images, output_dir, set_name, target_format)
    except Exception as e:
        logger.exception(f"Error saving {set_name} images")
        raise 

if name == 'main': logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name) 

args = parse_args()
config = load_config(args.config) 

dataset_dirs = [Path(dir) for dir in config['dataset_dirs']]
output_dir = Path(config['output_dir'])
target_format = config.get('target_format', 'PNG')
aug_config = config.get('aug_config', None) 

try:
    process_datasets(dataset_dirs, output_dir, target_format=target_format, aug_config=aug_config)
except Exception as e:
    logger.exception("Error processing datasets")
    raise
