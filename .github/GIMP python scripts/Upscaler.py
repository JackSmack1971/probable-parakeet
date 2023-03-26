import argparse
from pathlib import Path 

# Import the necessary GIMP modules
import gimp
from gimpfu import * 

def upscale_image(input_file_path: Path, output_directory: Path, canvas_width: int, canvas_height: int, canvas_resolution: int):
    """Upscales an image to the specified canvas size and saves it to the output directory. 

    Args:
        input_file_path (pathlib.Path): The path to the image file to be upscaled.
        output_directory (pathlib.Path): The output directory where the upscaled image will be saved.
        canvas_width (int): The desired canvas width in inches.
        canvas_height (int): The desired canvas height in inches.
        canvas_resolution (int): The desired canvas resolution in pixels per inch.
    """
    # Check if the input file exists and is a valid image file
    if not input_file_path.exists():
        raise FileNotFoundError("The input file does not exist.")
    if input_file_path.suffix not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
        raise ValueError("The input file is not a valid image file.") 

    # Open the image in GIMP
    image = pdb.gimp_file_load(str(input_file_path), str(input_file_path)) 

    # Calculate the new width and height based on the desired canvas size
    new_width = int(canvas_width * canvas_resolution)
    new_height = int(canvas_height * canvas_resolution) 

    # Scale the image to the new size
    pdb.gimp_image_scale(image, new_width, new_height) 

    # Save the upscaled image
    output_file_path = output_directory / input_file_path.name
    pdb.file_png_save(image, image.active_drawable, str(output_file_path), str(output_file_path), 0, 9, 1, 1, 1, 1, 1) 

    # Close the image
    pdb.gimp_image_delete(image) 

if __name__ == '__main__':
    # Parse the command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file_path', help='the path to the image file to be upscaled')
    parser.add_argument('output_directory', help='the output directory where the upscaled image will be saved')
    parser.add_argument('--canvas_width', type=int, default=72, help='the desired canvas width in inches')
    parser.add_argument('--canvas_height', type=int, default=36, help='the desired canvas height in inches')
    parser.add_argument('--canvas_resolution', type=int, default=300, help='the desired canvas resolution in pixels per inch')
    args = parser.parse_args() 

    # Upscale the image
    input_file_path = Path(args.input_file_path)
        output_directory = Path(args.output_directory)
    upscale_image(input_file_path, output_directory, args.canvas_width, args.canvas_height, args.canvas_resolution)
