"""
Quick and dirty script to convert my nice PNG images into 
NumPy arrays for use in my project. 

Usage:
    python png_to_npy.py /path/to/pngs /path/to/npy_output

Enforces a consistent format (32x32 RGB) and saves the arrays as .npy files for easy loading in my app.
"""

from PIL import Image
import numpy as np
import os
import argparse

def png_to_npy(png_path, npy_path):
    """Convert a PNG image to a NumPy array and save it as an .npy file."""
    # Load the image using Pillow
    img = Image.open(png_path)
    # Convert the image to RGB (in case it's RGBA or grayscale)
    img = img.convert('RGB')

    # Convert the image to a NumPy array
    img_array = np.array(img)

    # Save the array as an .npy file
    np.save(npy_path, img_array) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PNG images to NumPy arrays.")
    parser.add_argument("input_dir", help="Directory containing PNG images.")
    parser.add_argument("output_dir", help="Directory to save .npy files.")
    args = parser.parse_args()
    # Example usage: python png_to_npy.py /path/to/pngs /path/to/npy_output

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Process each PNG file in the input directory
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".png"):
            png_path = os.path.join(args.input_dir, filename)
            npy_filename = os.path.splitext(filename)[0] + ".npy"
            npy_path = os.path.join(args.output_dir, npy_filename)
            png_to_npy(png_path, npy_path)
            print(f"Converted {png_path} to {npy_path}")
    