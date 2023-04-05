import os
import cv2
import shutil
import random
import numpy as np
from pathlib import Path
from skimage import io
from sklearn.model_selection import train_test_split

def preprocess_image(img_path, target_format='PNG'):
    img = io.imread(img_path)
    return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB) if target_format == 'PNG' else img

def random_rotation(img, rotation_range=10):
    angle = np.random.uniform(-rotation_range, rotation_range)
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, rotation_matrix, (width, height))

def random_brightness(img, brightness_range=0.2):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv = np.float32(hsv)
    hsv[:, :, 2] *= np.random.uniform(1 - brightness_range, 1 + brightness_range)
    hsv = np.clip(hsv, 0, 255)
    return cv2.cvtColor(np.uint8(hsv), cv2.COLOR_HSV2RGB)

def create_augmented_images(img, aug_config):
    aug_images = [img]

    if aug_config.get('horizontal_flip', False):
        aug_images.append(cv2.flip(img, 1))

    if aug_config.get('random_rotation', False):
        aug_images.extend([random_rotation(img) for img in aug_images.copy()])

    if aug_config.get('random_brightness', False):
        aug_images.extend([random_brightness(img) for img in aug_images.copy()])

    return aug_images

def process_datasets(dataset_dirs, output_dir, target_format='PNG', aug_config=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    combined_imgs = []

    for dataset_dir in dataset_dirs:
        dataset_path = Path(dataset_dir)
        for img_path in dataset_path.glob(f'*.{target_format.lower()}'):
            img = preprocess_image(img_path, target_format)
            combined_imgs.extend(create_augmented_images(img, aug_config))

    random.shuffle(combined_imgs)

    train_imgs, test_imgs = train_test_split(combined_imgs, test_size=0.2, random_state=42)
    val_imgs, test_imgs = train_test_split(test_imgs, test_size=0.5, random_state=42)

    sets = {'train': train_imgs, 'val': val_imgs, 'test': test_imgs}

    for set_name, images in sets.items():
        set_output_dir = output_dir / set_name
        set_output_dir.mkdir(parents=True, exist_ok=True)

        for i, img in enumerate(images):
            output_path = set_output_dir / f'{set_name}_{i:04d}.{target_format.lower()}'
            cv2.imwrite(str(output_path), img)

if __name__ == '__main__':
    dataset_dirs = ['path/to/dataset1', 'path/to/dataset2', 'path/to/dataset3']
    output_dir = 'path/to/output_dir'

    aug_config = {
        'horizontal_flip': True,
        'random_rotation': True,
        'random_brightness': True,
    }

    process_datasets(dataset_dirs, output_dir, target_format='PNG', aug_config=aug_config)
