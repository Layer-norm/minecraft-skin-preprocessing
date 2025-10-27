"""
Minecraft Skin Converter
Converts legacy 64x32 skins to modern 64x64 format
Swap layer2 and layer1
"""

import os
import json
import sys
from PIL import Image
import base64
from io import BytesIO
import argparse

DEFAULT_SKIN_REGIONS = {
    "layer1": {
        "head": [
            {"name": "head1_layer1", "coords": [8, 0, 24, 8]},
            {"name": "head2_layer1", "coords": [0, 8, 32, 16]}
        ],
        "body": [
            {"name": "body1_layer1", "coords": [20, 16, 36, 20]},
            {"name": "body2_layer1", "coords": [16, 20, 40, 32]}
        ],
        "right_arm": [
            {"name": "right_arm1_layer1", "coords": [44, 16, 52, 20]},
            {"name": "right_arm2_layer1", "coords": [40, 20, 56, 32]}
        ],
        "left_arm": [
            {"name": "left_arm1_layer1", "coords": [36, 48, 44, 52]},
            {"name": "left_arm2_layer1", "coords": [32, 52, 48, 64]}
        ],
        "right_leg": [
            {"name": "right_leg1_layer1", "coords": [4, 16, 12, 20]},
            {"name": "right_leg2_layer1", "coords": [0, 20, 16, 32]}
        ],
        "left_leg": [
            {"name": "left_leg1_layer1", "coords": [20, 48, 28, 52]},
            {"name": "left_leg2_layer1", "coords": [16, 52, 32, 64]}
        ]
    },
    "layer2": {
        "head": [
            {"name": "head1_layer2", "coords": [40, 0, 56, 8]},
            {"name": "head2_layer2", "coords": [32, 8, 64, 16]}
        ],
        "body": [
            {"name": "body1_layer2", "coords": [20, 32, 36, 36]},
            {"name": "body2_layer2", "coords": [16, 36, 40, 48]}
        ],
        "right_arm": [
            {"name": "right_arm1_layer2", "coords": [44, 32, 52, 36]},
            {"name": "right_arm2_layer2", "coords": [40, 36, 56, 48]}
        ],
        "left_arm": [
            {"name": "left_arm1_layer2", "coords": [52, 48, 60, 52]},
            {"name": "left_arm2_layer2", "coords": [48, 52, 64, 64]}
        ],
        "right_leg": [
            {"name": "right_leg1_layer2", "coords": [4, 32, 12, 36]},
            {"name": "right_leg2_layer2", "coords": [0, 36, 16, 48]}
        ],
        "left_leg": [
            {"name": "left_leg1_layer2", "coords": [4, 48, 12, 52]},
            {"name": "left_leg2_layer2", "coords": [0, 52, 16, 64]}
        ]
    }
}

def _convert_skin_64x32_to_64x64(img):
    """Convert a 64x32 skin image to 64x64 format"""
    # Create new 64x64 image
    new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            
    # For 64x32 skins, we need to create the additional layer parts
    # The additional layer is typically a copy/mirror of the existing parts
            
    # Copy head layer1
    head1_layer1 = img.crop((8, 0, 24, 8))
    new_skin.paste(head1_layer1, (8, 0, 24, 8))

    head2_layer1 = img.crop((0, 8, 32, 16))
    new_skin.paste(head2_layer1, (0, 8, 32, 16))

    # Copy head layer2
    head1_layer2 = img.crop((40, 0, 56, 8))
    new_skin.paste(head1_layer2, (40, 0, 56, 8))

    head2_layer2 = img.crop((32, 8, 64, 16))
    new_skin.paste(head2_layer2, (32, 8, 64, 16))
            
    # Copy body layer1
    body1_layer1 = img.crop((20, 16, 36, 20))
    new_skin.paste(body1_layer1, (20, 16, 36, 20))

    body2_layer1 = img.crop((16, 20, 40, 32))
    new_skin.paste(body2_layer1, (16, 20, 40, 32))
            
    # Copy right arm layer1
    right_arm1_layer1 = img.crop((44, 16, 52, 20))
    new_skin.paste(right_arm1_layer1, (44, 16, 52, 20))

    right_arm2_layer1 = img.crop((40, 20, 56, 32))
    new_skin.paste(right_arm2_layer1, (40, 20, 56, 32))
            
    # Copy left arm layer1
    left_arm1_layer1 = img.crop((44, 16, 52, 20))
    new_skin.paste(left_arm1_layer1, (36, 48, 44, 52))

    left_arm2_layer1 = img.crop((40, 20, 56, 32))
    new_skin.paste(left_arm2_layer1, (32, 52, 48, 64))


    # Copy right leg layer1
    right_leg1_layer1 = img.crop((4, 16, 12, 20))
    new_skin.paste(right_leg1_layer1, (4, 16, 12, 20))

    right_leg2_layer1 = img.crop((0, 20, 16, 32))
    new_skin.paste(right_leg2_layer1, (0, 20, 16, 32))

    # Copy left leg layer1
    left_leg1_layer1 = img.crop((4, 16, 12, 20))
    new_skin.paste(left_leg1_layer1, (20, 48, 28, 52))

    left_leg2_layer1 = img.crop((0, 20, 16, 32))
    new_skin.paste(left_leg2_layer1, (16, 52, 32, 64))

    return new_skin

def convert_skin_64x32_to_64x64(input_path, output_path=None):
    """
    Convert a 64x32 Minecraft skin to 64x64 format
    
    Args:
        input_path (str): Path to input skin file
        output_path (str): Path for output file (optional)
    
    Returns:
        bool: True if conversion was successful
    """
    
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            width, height = img.size
            
            # Check if it's already 64x64
            if width == 64 and height == 64:
                print(f"✓ {os.path.basename(input_path)} is already 64x64")
                return True
            
            # Verify it's 64x32
            if width != 64 or height != 32:
                print(f"✗ {os.path.basename(input_path)}: Invalid dimensions {width}x{height}, expected 64x32")
                return False
            
            # Perform conversion
            new_skin = _convert_skin_64x32_to_64x64(img)
            
            # Determine output path
            if output_path is None:
                # Create output filename
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}_64x64.png"
            
            # Save the converted skin
            new_skin.save(output_path, 'PNG')
            print(f"✓ Converted {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            return True
            
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(input_path)}: {str(e)}")
        return False

def _swap_skin_layer2_to_layer1(img):
    # """swap layer2 to layer1 in a 64x64 skin image"""

    new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

    # get layer rigions from DEFAULT_SKIN_REGIONS
    for layer, regions in DEFAULT_SKIN_REGIONS.items():
        for part, parts in regions.items():
            for part_info in parts:
                name = part_info['name']
                coords = part_info['coords']
                cropped_part = img.crop(tuple(coords))
                
                if layer == 'layer1':
                    # find corresponding layer2 part
                    layer2_part_info = next((p for p in DEFAULT_SKIN_REGIONS['layer2'][part] if p['name'] == name.replace('layer1', 'layer2')), None)
                    if layer2_part_info:
                        new_coords = layer2_part_info['coords']
                        new_skin.paste(cropped_part, tuple(new_coords))
                else:
                    # find corresponding layer1 part
                    layer1_part_info = next((p for p in DEFAULT_SKIN_REGIONS['layer1'][part] if p['name'] == name.replace('layer2', 'layer1')), None)
                    if layer1_part_info:
                        new_coords = layer1_part_info['coords']
                        new_skin.paste(cropped_part, tuple(new_coords))

    return new_skin

def swap_skin_layer2_to_layer1(input_file, output_file=None):
    """
    swap layer2 to layer1 in a 64x64 skin image
    
    Args:
        input_file (str): Path to the input file
        output_file (str): Path to the output file

    Returns:
        bool: True if conversion was successful, False otherwise
    
    """

    try:
        img = Image.open(input_file)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Check image size
        width, height = img.size
        if width != 64 or height != 64:
            print(f"✗ {os.path.basename(input_file)}: Invalid dimensions {width}x{height}, expected 64x64")
            return False

        new_skin = _swap_skin_layer2_to_layer1(img)
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '_swap.png'
        new_skin.save(output_file)

        print(f"✓ {os.path.basename(input_file)}: Saved swap layer skin to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def twice_swap_skin_layers(input_file, output_file=None):
    """
    Swap layer2 and layer1 twice (to remove invalid areas) in a 64x64 skin image
    
    Args:
        input_file (str): Path to the input file
        output_file (str): Path to the output file

    Returns:
        bool: True if conversion was successful, False otherwise
    
    """
    try: 
        img = Image.open(input_file)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Check image size
        width, height = img.size
        if width != 64 or height != 64:
            print(f"✗ {os.path.basename(input_file)}: Invalid dimensions {width}x{height}, expected 64x64")
            return False

        new_skin = _swap_skin_layer2_to_layer1(img)
        new_skin = _swap_skin_layer2_to_layer1(new_skin)
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '_swap_swap.png'
        new_skin.save(output_file)

        print(f"✓ {os.path.basename(input_file)}: Saved swap layer skin to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False



def load_skin_from_base64(base64_str):
    """Load skin image from base64 string"""
    img_data = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_data))
    return img

def batch_convert_folder(convert_func, input_folder, output_folder=None, overwrite=False):
    """
    Convert all 64x32 skins in a folder to 64x64 format
    
    Args:
        input_folder (str): Path to folder containing skins
        output_folder (str): Output folder path (optional)
        overwrite (bool): Whether to overwrite existing files
    """
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist")
        return
    
    # Use input folder as output if not specified
    if output_folder is None:
        output_folder = input_folder
    else:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
    
    # Supported image extensions
    supported_extensions = {'.png', '.jpg', '.jpeg'}
    
    # Counters for statistics
    total_files = 0
    converted_files = 0
    skipped_files = 0
    error_files = 0
    
    print(f"Converting skins in: {input_folder}")
    print(f"Output folder: {output_folder}")
    print("-" * 50)
    
    # Process all image files in the folder
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Check if it's a supported image file
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in supported_extensions:
            continue
        
        total_files += 1
        
        # Add suffix to filename
        base_name = os.path.splitext(filename)[0]
        if convert_func is convert_skin_64x32_to_64x64:
            output_filename = f"{base_name}_64x64.png"
        elif convert_func is swap_skin_layer2_to_layer1:
            output_filename = f"{base_name}_swap.png"
        else:
            output_filename = f"{base_name}_out.png"
        output_path = os.path.join(output_folder, output_filename)
        
        # Check if output file already exists
        if os.path.exists(output_path) and not overwrite:
            print(f"⏭️ Skipped {filename} (output already exists)")
            skipped_files += 1
            continue
        
        # Convert the skin
        if convert_func(file_path, output_path):
            converted_files += 1
        else:
            error_files += 1
    
    # Print summary
    print("-" * 50)
    print("Conversion Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Successfully converted: {converted_files}")
    print(f"Skipped: {skipped_files}")
    print(f"Errors: {error_files}")


def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Convert Minecraft skins from 64x32 to 64x64 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single skin
  python preprocess.py -c old_skin.png
  
  # Convert all skins in a folder
  python preprocess.py -c -i skins_folder
  
  # Convert with custom output folder
  python preprocess.py -c -i old_skins -o new_skins

  # Convert and overwrite existing files
  python preprocess.py -c -i skins_folder --overwrite

  # Swap layer2 and layer1
  python preprocess.py -s old_skin.png

  # Swap layer2 and layer1 twice (to remove invalid areas)
  python preprocess.py -ss old_skin.png

  # Convert skin from base64 string
  python preprocess.py -c -b base64_skin_string
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input file or folder path')
    parser.add_argument('-c', '--convert', action='store_true', help='Convert 64x32 to 64x64')
    parser.add_argument('-i', '--input-folder', help='Input folder containing skins')
    parser.add_argument('-o', '--output-folder', help='Output folder for converted skins')
    parser.add_argument('-s','--swap-layer2-to-layer1', action='store_true', help='Swap layer2 to layer1')
    parser.add_argument('-ss','--twice-swap-layer2-to-layer1', action='store_true', help='Swap layer2 and layer1 twice (to remove invalid areas)')
    parser.add_argument('-b', '--base64', help='Base64 encoded skin image')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    
    args = parser.parse_args()
    
    # Determine function
    if args.convert:
        convert_func = convert_skin_64x32_to_64x64
    elif args.swap_layer2_to_layer1:
        convert_func = swap_skin_layer2_to_layer1
    elif args.double_swap_layer2_to_layer1:
        convert_func = twice_swap_skin_layers
    else:
        parser.print_help()
        return

    # Determine input source
    if args.base64:
        img = load_skin_from_base64(args.base64)
        input_path = "base64_skin.png"
        with open(input_path, "wb") as f:
            f.write(img.tobytes())
    elif args.input_folder:
        input_path = args.input_folder
    elif args.input:
        input_path = args.input
    else:
        parser.print_help()
        return
    
    # Check if input is file or folder
    if os.path.isfile(input_path):
        # Single file conversion
        convert_func(input_path, args.output_folder)
    elif os.path.isdir(input_path):
        # Batch conversion
        batch_convert_folder(convert_func, input_path, args.output_folder, args.overwrite)
    else:
        print(f"Error: '{input_path}' is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()