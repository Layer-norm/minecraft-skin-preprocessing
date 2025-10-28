"""
Minecraft Skin Preprocessing Tool

Author: Faxuan Cai

License: MIT License

Description:
Converts legacy 64x32 skins to modern 64x64 format
Swap layer2 and layer1
Remove specific layer
"""

import os
import json
import sys
from PIL import Image
import base64
from io import BytesIO
import argparse

DEFAULT_MC_SKIN_REGIONS = {
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

class MCSkinTools:
    """
    A class for preprocessing Minecraft skins
    """

    def __init__(self, skin_regions=None):
        """Initialize the MCSkinTools class"""
        if skin_regions is None:
            self.skin_regions = DEFAULT_MC_SKIN_REGIONS
        else:
            self.skin_regions = skin_regions
    
 
    def convert_skin_64x32_to_64x64(self,img):
        """Convert a 64x32 skin image to 64x64 format"""
        # Create new 64x64 image
        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        exist_region_layer1 = ["head", "body", "right_arm", "right_leg"]
        exist_region_layer2 = ["head"]

        # Copy exist region in layer1
        for region in exist_region_layer1:
            for part in self.skin_regions["layer1"][region]:
                part_img = img.crop(part["coords"])
                new_skin.paste(part_img, part["coords"])

        # Copy exist region in layer2
        for region in exist_region_layer2:
            for part in self.skin_regions["layer2"][region]:
                part_img = img.crop(part["coords"])
                new_skin.paste(part_img, part["coords"])

        # Copy left arm and left leg region in layer1
        mirror_regions = {
            "left_arm": "right_arm",
            "left_leg": "right_leg"
        }

        for target_region, source_region in mirror_regions.items():
            source_parts = self.skin_regions["layer1"][source_region]
            target_parts = self.skin_regions["layer1"][target_region]

            coord_mapping = {
                source_part["name"].replace("right", "left"): target_part["coords"]
                for source_part, target_part in zip(source_parts, target_parts)
            }

            for source_part in source_parts:
                target_part_name = source_part["name"].replace("right", "left")
                if target_part_name in coord_mapping:
                    part_img = img.crop(source_part["coords"])
                    target_coords = coord_mapping[target_part_name]
                    new_skin.paste(part_img, target_coords)

        return new_skin

    def swap_skin_layer2_to_layer1(self,img):
        """swap layer2 to layer1 in a 64x64 skin image"""

        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        # create mapping for layer swap
        layer_mapping = {
            'layer1': 'layer2',
            'layer2': 'layer1'
        }

        # get layer rigions from self.skin_regions
        for layer, regions in self.skin_regions.items():
            target_layer = layer_mapping[layer]
            for part, parts in regions.items():
                for part_info in parts:
                    name = part_info['name']
                    coords = part_info['coords']
                    cropped_part = img.crop(tuple(coords))

                    # Find corresponding part in target layer
                    target_part_info = next((p for p in self.skin_regions[target_layer][part] if p['name'] == name.replace(layer, target_layer)), None)
                    if target_part_info:
                        new_coords = target_part_info['coords']
                        new_skin.paste(cropped_part, tuple(new_coords))

        return new_skin
    
    def remove_layer(self,img, layer_index):
        """Remove a layer from a 64x64 skin image"""
        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        if layer_index == 1:
            keep_layer = 'layer2'
        elif layer_index == 2:
            keep_layer = 'layer1'
        else:
            print(f"✗ Invalid layer index: {layer_index}")
            return None

        # get layer rigions from self.skin_regions
        for parts in self.skin_regions[keep_layer].values():
            for part_info in parts:
                coords = part_info['coords']
                cropped_part = img.crop(tuple(coords))
                new_skin.paste(cropped_part, tuple(coords))

        return new_skin

class MCSkinFileProcessor:
    """
    A class for processing Minecraft skin files
    """
    def __init__(self, skin_regions=None):
        self.skin_tools = MCSkinTools(skin_regions)
 
    def convert_skin_64x32_to_64x64(self, input_path, output_path=None):
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
                new_skin = self.skin_tools.convert_skin_64x32_to_64x64(img)

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

    def swap_skin_layer2_to_layer1(self,input_file, output_file=None):
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

            new_skin = self.skin_tools.swap_skin_layer2_to_layer1(img)
            if output_file is None:
                output_file = os.path.splitext(input_file)[0] + '_swap.png'
            new_skin.save(output_file)

            print(f"✓ {os.path.basename(input_file)}: Saved swap layer skin to {output_file}")
            return True
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def twice_swap_skin_layers(self, input_file, output_file=None):
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

            new_skin = self.skin_tools.swap_skin_layer2_to_layer1(img)
            new_skin = self.skin_tools.swap_skin_layer2_to_layer1(new_skin)
            if output_file is None:
                output_file = os.path.splitext(input_file)[0] + '_swap_swap.png'
            new_skin.save(output_file)

            print(f"✓ {os.path.basename(input_file)}: Saved swap layer skin to {output_file}")
            return True
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def remove_layer(self, input_file, output_file=None, layer_index=None):
        """
        Remove a layer from a 64x64 skin image

        Args:
            input_file (str): Path to the input file
            output_file (str): Path to the output file
            layer_index (int): Index of the layer to remove (1 or 2)

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

            if layer_index not in [1, 2]:
                print(f"✗ Invalid layer index: {layer_index}")
                return False

            new_skin = self.skin_tools.remove_layer(img, layer_index)
            if output_file is None:
                output_file = os.path.splitext(input_file)[0] + f'_rm_layer{layer_index}.png'
            new_skin.save(output_file)

            print(f"✓ {os.path.basename(input_file)}: Saved remove layer skin to {output_file}")
            return True
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def batch_convert_folder(self, convert_func, input_folder, layer_index=None, output_folder=None, overwrite=False):
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
            if convert_func is self.convert_skin_64x32_to_64x64:
                output_filename = f"{base_name}_64x64.png"
            elif convert_func is self.swap_skin_layer2_to_layer1:
                output_filename = f"{base_name}_swap.png"
            elif convert_func is self.remove_layer:
                output_filename = f"{base_name}_rm_layer{layer_index}.png"
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

def load_skin_from_base64(base64_str):
    """Load skin image from base64 string"""
    img_data = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_data))
    return img

def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Convert Minecraft skins from 64x32 to 64x64 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single skin
  python MinecraftSkinTools.py -c old_skin.png
  
  # Convert all skins in a folder
  python MinecraftSkinTools.py -c -i skins_folder
  
  # Convert with custom output folder
  python MinecraftSkinTools.py -c -i old_skins -o new_skins

  # Convert and overwrite existing files
  python MinecraftSkinTools.py -c -i skins_folder --overwrite

  # Swap layer2 and layer1
  python MinecraftSkinTools.py -s old_skin.png

  # Swap layer2 and layer1 twice (to remove invalid areas)
  python MinecraftSkinTools.py -ss old_skin.png

  # Remove layer1
  python MinecraftSkinTools.py -rm 1 old_skin.png

  # Remove layer2
  python MinecraftSkinTools.py -rm 2 old_skin.png

  # Convert skin from base64 string
  python MinecraftSkinTools.py -c -b base64_skin_string
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input file or folder path')
    parser.add_argument('-c', '--convert', action='store_true', help='Convert 64x32 to 64x64')
    parser.add_argument('-i', '--input-folder', help='Input folder containing skins')
    parser.add_argument('-o', '--output-folder', help='Output folder for converted skins')
    parser.add_argument('-s','--swap-layer2-to-layer1', action='store_true', help='Swap layer2 to layer1')
    parser.add_argument('-ss','--twice-swap-layer2-to-layer1', action='store_true', help='Swap layer2 and layer1 twice (to remove invalid areas)')
    parser.add_argument('-b', '--base64', help='Base64 encoded skin image')
    parser.add_argument('-rm', '--remove-layer', type=int, choices=[1, 2], help='Remove specified layer (1 or 2)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    
    args = parser.parse_args()

    processor = MCSkinFileProcessor()
    
    # Determine function
    if args.convert:
        convert_func = processor.convert_skin_64x32_to_64x64
    elif args.swap_layer2_to_layer1:
        convert_func = processor.swap_skin_layer2_to_layer1
    elif args.twice_swap_layer2_to_layer1:
        convert_func = processor.twice_swap_skin_layers
    elif args.remove_layer:
        convert_func = lambda x, y: processor.remove_layer(x, y, layer_index=args.remove_layer)
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
        processor.batch_convert_folder(convert_func=convert_func, input_folder=input_path, output_folder=args.output_folder, overwrite=args.overwrite)
    else:
        print(f"Error: '{input_path}' is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()