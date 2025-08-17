#!/usr/bin/env python3
"""
Script to remove white background from static logo and create a transparent PNG.

Defaults:
- Input: assets/static_logo1.jpeg (or any provided path)
- Output: assets/static_logo.png
"""

from PIL import Image
import os
import sys

def remove_white_background(input_path: str, output_path: str, threshold: int = 240) -> bool:
    """
    Remove white background from an image and make it transparent.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image with transparency
        threshold (int): RGB threshold for considering pixels as white (0-255)
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get image data
        data = img.getdata()
        
        # Create new image data with transparency
        new_data = []
        for item in data:
            # Check if pixel is close to white (high RGB values)
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                # Make white pixels transparent
                new_data.append((255, 255, 255, 0))
            else:
                # Keep other pixels as they are
                new_data.append(item)
        
        # Create new image with transparency
        new_img = Image.new('RGBA', img.size)
        new_img.putdata(new_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        # Save the image with transparency as PNG
        new_img.save(output_path, 'PNG')
        print(f"Successfully removed white background from {input_path}")
        print(f"Transparent logo saved as {output_path}")
        
        return True
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def main():
    # CLI args: input [output]
    # Defaults align with project assets and processor expectations
    default_input = "assets/static_logo1.jpeg"
    default_output = "assets/static_logo.png"

    args = sys.argv[1:]
    if len(args) >= 1:
        input_logo = args[0]
    else:
        input_logo = default_input
    if len(args) >= 2:
        output_logo = args[1]
    else:
        output_logo = default_output

    if not os.path.exists(input_logo):
        print(f"Error: Input file {input_logo} not found!")
        return

    success = remove_white_background(input_logo, output_logo)
    if success:
        print("\nLogo processing completed successfully!")
        print(f"Original: {input_logo}")
        print(f"Transparent: {output_logo}")
    else:
        print("Failed to process the logo.")

if __name__ == "__main__":
    main()
