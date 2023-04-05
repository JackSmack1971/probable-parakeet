import os
import sys
import cv2
import json
import shutil
import random
import numpy as np
from pathlib import Path
from skimage import io
from tqdm import tqdm
from typing import List, Tuple, Union, Optional, Any
from sklearn.model_selection import train_test_split
import logging
import click 

logger = logging.getLogger(__name__)


@click.command()
@click.option('--config', type=str, required=True, help='Path to the configuration file')
def main(config: str) -> None:
    """
    Process datasets and apply data augmentation. 

    Args:
        config (str): Path to the configuration file.
    """
    config = load_config(config) 

    dataset_dirs = [Path(dir) for dir in config['dataset_dirs']]
    output_dir = Path(config['output_dir'])
    target_format = config.get('target_format', 'PNG')
    aug_config = config.get('aug_config', None) 

    try:
        process_datasets(dataset_dirs, output_dir, target_format=target_format, aug_config=aug_config)
    except Exception as e:
        logger.exception("Error processing datasets")
        raise


def load_config(config_path: Union[str, Path]) -> dict:
    """
    Load configuration file. 

    Args:
        config_path (Union[str, Path]): Path to the configuration file. 

    Returns:
        dict: Configuration parameters.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def preprocess_image(img_path: Union[str, Path], target_format: str = 'PNG') -> np.ndarray:
    """
    Load and preprocess image. 

    Args:
        img_path (Union[str, Path]): Path to the image file.
        target_format (str): Target format of the image. 

    Returns:
        np.ndarray: Preprocessed image.
    """
    try:
        img = io.imread(str(img_path))
        img = cv2.cvtColor(
            img, cv2.COLOR_RGBA2RGB) if target_format == 'PNG' else img
        return img
    except Exception as e:
        logger.exception(f"Error loading image file: {img_path}")
        raise


def apply_random_rotation(img: np.ndarray, rotation_range: int = 10) -> np.ndarray:
    """
    Apply random rotation to image. 

    Args:
        img (np.ndarray): Image to be rotated.
        rotation_range (int): Range of rotation in degrees. 

    Returns:
        np.ndarray: Rotated image.
    """
    angle = np.random.uniform(-rotation_range, rotation_range)
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, rotation_matrix, (width, height))


def apply_random_brightness(img: np.ndarray, brightness_range: float = 0.2) -> np.ndarray:
    """
    Apply random brightness to image. 

    Args:
        img (np.ndarray): Image to be adjusted.
        brightness_range (float): Range of brightness adjustment. 

    Returns:
        np.ndarray: Brightness-adjusted image.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv = np.float32(hsv)
    hsv[:, :, 2] *= np.random.uniform(1 - brightness_range, 1 + brightness_range)
    hsv = np.clip(hsv, 0, 255)
    return cv2.cvtColor(np.uint8(hsv), cv2.COLOR_HSV2RGB)


def create_augmented_image(img: np.ndarray, aug_config: dict) -> np.ndarray:
    """
    Create an augmented image. 

    Args:
        img (np.ndarray): Image to be augmented.
        aug_config (dict): Augmentation configuration. 

    Returns:
        np.ndarray: Augmented image.
    """
    if aug_config.get('horizontal_flip', False):
        img = cv2.flip(img, 1) 

    if aug_config.get('random_rotation', False):
        rotation_range = aug_config.get('rotation_range', 10)
        img = apply_random_rotation(img, rotation_range) 

    if aug_config.get('random_brightness', False):
        brightness_range = aug_config.get('brightness_range', 0.2)
        img = apply_random_brightness(img, brightness_range) 

    return img


def create_augmented_images(img: np.ndarray, aug_config: dict) -> List[np.ndarray]:
    """
    Create a list of augmented images. 

    Args:
        img (np.ndarray): Image to be augmented.
        aug_config (dict): Augmentation configuration. 

    Returns:
        List[np.ndarray]: List of augmented images.
    """
    aug_images = [img]
    for _ in range(aug_config.get('num_augmentations', 0)):
        aug_images.append(create_augmented_image(img, aug_config))
    return aug_images


def save_image(img: np.ndarray, output_path: Union[str, Path]) -> None:
    """
    Save image to disk. 

    Args:
        img (np.ndarray): Image to be saved.
        output_path (Union[str, Path]): Output path for the image.
    """
    cv2.imwrite(str(output_path), img)


def get_image_files(directory: Union[str, Path], target_format: str = 'PNG') -> List[Path]:
    """
    Get a list of image files from a directory. 

    Args:
        directory (Union[str, Path]): Directory containing the image files.
        target_format (str): Target format of the image files. 

    Returns:
        List[Path]: List of image file paths.
    """
    directory = Path(directory)
    image_files = [f for f in directory.iterdir() if f.suffix.lower() == f'.{target_format.lower()}']
    return image_files


def split_datasets(combined_imgs: List[np.ndarray]) -> dict:
    """
    Split images into training, validation, and testing sets. 

    Args:
        combined_imgs (List[np.ndarray]): List of images. 

    Returns:
        dict: Dictionary containing the split sets.
    """
    train_imgs, test_imgs = train_test_split(combined_imgs, test_size=0.2, random_state=42)
    val_imgs, test_imgs = train_test_split(test_imgs, test_size=0.5, random_state=42)
    return {'train': train_imgs, 'val': val_imgs, 'test': test_imgs}


def save_images(images: List[np.ndarray], output_dir: Path, set_name: str, target_format: str = 'PNG') -> None:
    """
    Save a list of images to disk. 

    Args:
        images (List[np.ndarray]): List of images to be saved.
        output_dir (Path): Output directory for the images.
        set_name (str): Name of the image set.
        target_format (str): Target format of the image files.
    """
    set_output_dir = output_dir / set_name
    set_output_dir.mkdir(parents=True, exist_ok=True) 

    for i, img in enumerate(tqdm(images, desc=f"Saving {set_name} images")):
        output_path = set_output_dir / f'{set_name}_{i:04d}.{target_format.lower()}'
        save_image 

def process_datasets(dataset_dirs: List[Union[str, Path]], output_dir: Union[str, Path], target_format: str = 'PNG', aug_config: Optional[dict] = None) -> None:
    """
    Process datasets and save augmented images to disk. 

    Args:
        dataset_dirs (List[Union[str, Path]]): List of directories containing the datasets.
        output_dir (Union[str, Path]): Output directory for the augmented images.
        target_format (str): Target format of the image files.
        aug_config (Optional[dict]): Augmentation configuration. 

    Raises:
        Exception: If there is an error while processing the datasets.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True) 

    combined_imgs = []
    for dataset_dir in dataset_dirs:
        image_files = get_image_files(dataset_dir, target_format)
        for img_path in tqdm(image_files, desc=f"Processing {dataset_dir}"):
            img = preprocess_image(img_path, target_format)
            augmented_imgs = create_augmented_images(
                img, aug_config) if aug_config else [img]
            combined_imgs.extend(augmented_imgs) 

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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main() 

def main():
    """
    Main function that parses arguments, loads configuration, and processes datasets.
    """
    args = parse_args()
    config = load_config(args.config) 

    dataset_dirs = [Path(dir) for dir in config['dataset_dirs']]
    output_dir = Path(config['output_dir'])
    target_format = config.get('target_format', 'PNG')
    aug_config = config.get('aug_config', None) 

    try:
        process_datasets(dataset_dirs, output_dir,
                          target_format=target_format, aug_config=aug_config)
    except Exception as e:
        logger.exception("Error processing datasets")
        raise
