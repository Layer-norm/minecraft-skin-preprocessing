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
import numpy as np
from PIL import Image
import base64
from io import BytesIO


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

class MCSkinType:
    """
    Class for skin type (slim or regular)

    """
    
    def __init__(self, skin_type=None, regular_regions=DEFAULT_MC_SKIN_REGIONS):
        self._skin_type = skin_type
        
        self.regular_regions = regular_regions
        self._slim_regions = {}
        self.adjust_regions = ['right_arm', 'left_arm']

    @property
    def skin_type(self):
        """
        Get skin type

        Returns:
            str: Skin type ('slim' or 'regular')
        """
        if self._skin_type is None:
            self._skin_type = 'regular'
        return self._skin_type
    
    @skin_type.setter
    def skin_type(self, value):
        """
        Set skin type
        Args:
            value (str): Skin type ('slim' , 'regular', 'steve', 'alex')
        """
        if value in ['regular', 'steve', 'slim', 'alex']:
            self._skin_type = value
        else:
            raise ValueError("Detect invalid skin type. Must be 'slim', 'regular', 'steve', or 'alex'.")


    @property
    def slim_regions(self):
        """
        Get slim skin regions

        Returns:
            dict: Slim skin regions
        """
        for layer_key, layer_value in self.regular_regions.items():
            self._slim_regions[layer_key] = {}
            for region_key, region_value in layer_value.items():
                if region_key in self.adjust_regions:
                    adjusted_parts = []
                    for part in region_value:
                        coords = part["coords"].copy()
                        coords[2] -= 2

                        adjusted_parts.append({
                            "name": part["name"],
                            "coords": coords
                        })
                    self._slim_regions[layer_key][region_key] = adjusted_parts
                else:
                    self._slim_regions[layer_key][region_key] = region_value

        return self._slim_regions
    
    @property
    def skin_regions(self):
        """
        Get skin regions based on skin type

        Returns:
            dict: Skin regions
        """
        skin_type = self.skin_type
        if skin_type in ['regular', 'steve']:
            return self.regular_regions
        elif skin_type in ['slim', 'alex']:
            return self.slim_regions
        else:
            raise ValueError("Invalid skin type. Must be 'regular', 'slim', 'steve', or 'alex'.")

    def auto_detect_skin_type(self, skin_img):
        """
        Detect skin type (slim or regular) based on skin image

        Args:
            skin_img (Image): Input skin image

        Returns:
            str: Detected skin type ('slim' or 'regular')
        """
        if skin_img.mode != 'RGBA':
            skin_img = skin_img.convert('RGBA')

        for arm in self.adjust_regions:
            for layer in ['layer1', 'layer2']:
                arm_region = self.regular_regions[layer][arm]
            
                for arm_part in arm_region:
                    coords = arm_part['coords']
                    arm_img = skin_img.crop(coords)
                    arm_alpha_channel = np.array(arm_img.split()[-1])
                    if np.any(arm_alpha_channel[:, -2:] > 0):
                        self._skin_type = 'regular'
                        return self._skin_type
        

        self._skin_type = 'slim'
        return self._skin_type


class MCSkinTools:
    """
    A class for preprocessing Minecraft skins
    """

    def __init__(self, skin_type=None):
        """Initialize the MCSkinTools class"""
        self.skin_type = skin_type
        self.type_detector = MCSkinType(skin_type=skin_type)

        try:
            self.skin_regions = self.type_detector.skin_regions
        except (ValueError, AttributeError):
            self.skin_regions = self.type_detector.regular_regions

        self.regular_regions = self.type_detector.regular_regions
        self.slim_regions = self.type_detector.slim_regions

 
    def convert_skin_64x32_to_64x64(self,img):
        """Convert a 64x32 skin image to 64x64 format"""
        # Create new 64x64 image
        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        exist_region_layer1 = ["head", "body", "right_arm", "right_leg"]
        exist_region_layer2 = ["head"]

        skin_regions = self.skin_regions

        # Copy exist region in layer1
        for region in exist_region_layer1:
            for part in skin_regions["layer1"][region]:
                part_img = img.crop(part["coords"])
                new_skin.paste(part_img, part["coords"])

        # Copy exist region in layer2
        for region in exist_region_layer2:
            for part in skin_regions["layer2"][region]:
                part_img = img.crop(part["coords"])
                new_skin.paste(part_img, part["coords"])

        # Copy left arm and left leg region in layer1
        mirror_regions = {
            "left_arm": "right_arm",
            "left_leg": "right_leg"
        }

        for target_region, source_region in mirror_regions.items():
            source_parts = skin_regions["layer1"][source_region]
            target_parts = skin_regions["layer1"][target_region]

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
    
    def twice_swap_skin_layer(self,img):
        """swap layer1 and layer2 twice in a 64x64 skin image"""
        new_skin = self.swap_skin_layer2_to_layer1(img)
        new_skin = self.swap_skin_layer2_to_layer1(new_skin)
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
    
    def steve_to_alex(self,img):
        """Convert a steve skin image to alex skin type"""
        self.skin_type = self.type_detector.auto_detect_skin_type(img)
        if self.skin_type not in ["steve", "regular", "alex", "slim"]:
            raise ValueError(f"✗ Invalid skin type: {self.skin_type}")
        elif self.skin_type in ["alex", "slim"]:
            return img

        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        i = 2
        delete_columns = {
            "right_arm": [
                [i, 4 + i],
                [4 + i, 3 * 4 + (3 - i)]
            ],
            "left_arm": [
                [3 - i, 4 + (3 - i)],
                [4 + (3 - i), 3 * 4 + i]
            ]
        }

        for layer in ["layer1", "layer2"]:
            for arm_side in ["right_arm", "left_arm"]:
                arm_parts = self.regular_regions[layer][arm_side]
                col_indices = delete_columns[arm_side]

                for idx, (part, delect_col) in enumerate(zip(arm_parts, col_indices)):
                    part_img = img.crop(part["coords"])
                    part_array = np.array(part_img)

                    new_part_array = np.delete(part_array, delect_col, axis=1)
                    new_part_img = Image.fromarray(new_part_array, mode='RGBA')

                    target_coords = self.slim_regions[layer][arm_side][idx]["coords"]
                    new_skin.paste(new_part_img, target_coords)

        return new_skin
    
    def alex_to_steve(self,img):
        """Convert a alex skin image to steve skin type"""
        self.skin_type = self.type_detector.auto_detect_skin_type(img)
        if self.skin_type not in ["alex", "slim", "steve", "regular"]:
            raise ValueError(f"✗ Invalid skin type: {self.skin_type}")
        elif self.skin_type in ["steve", "regular"]:
            return img
        
        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        i = 1

        # Insert columns in reverse order to avoid index shift
        insert_columns = {
            "right_arm": [
                [3 + i, i],           # right_arm part1: i 和 3+i
                [11 + (2 - i), 4 + i] # right_arm part2: 4+i 和 11+(2-i)
            ],
            "left_arm": [
                [3 + (2 - i), 2 - i], # left_arm part1: 2-i 和 3+(2-i)
                [11 + i, 4 + (2 - i)] # left_arm part2: 4+(2-i) 和 11+i
            ]
        }

        for layer in ["layer1", "layer2"]:
            for arm_side in ["right_arm", "left_arm"]:
                arm_parts = self.slim_regions[layer][arm_side]
                indices = insert_columns[arm_side]

                for idx, (part, insert_col) in enumerate(zip(arm_parts, indices)):
                    part_img = img.crop(part["coords"])

                    new_part_array = np.array(part_img)

                    for pos in insert_col:
                        column_to_copy = new_part_array[:, pos, :]
                        new_part_array = np.insert(new_part_array, pos, column_to_copy, axis=1)

                    new_part_img = Image.fromarray(new_part_array, mode='RGBA')

                    target_coords = self.regular_regions[layer][arm_side][idx]["coords"]

                    new_skin.paste(new_part_img, target_coords)

        return new_skin

    def convert_skin_type(self, img, target_type=None):
        """Convert a skin image to the specified skin type"""

        if target_type is None:
            if self.skin_type is None:
                print(f"Warning: Current skin type not specific, using detected type: {self.skin_type}")
                self.skin_type = self.type_detector.auto_detect_skin_type(img)

            if self.skin_type in ["steve", "regular"]:
                target_type = "alex"
            elif self.skin_type in ["alex", "slim"]:
                target_type = "steve"
            else:
                print(f"✗ Invalid skin type: {self.skin_type}")
                return None

        elif target_type not in ["steve", "alex", "regular", "slim"]:
            print(f"✗ Invalid target skin type: {target_type}")
            return None

        if target_type in ["steve", "regular"]:
            new_skin = self.alex_to_steve(img)
        elif target_type in ["alex", "slim"]:
            new_skin = self.steve_to_alex(img)
        else:
            print(f"✗ Invalid skin type: {self.skin_type}")
            return None
        return new_skin

    @staticmethod
    def load_skin_from_base64(base64_str):
        """Load skin image from base64 string"""
        img = base64.b64decode(base64_str)
        new_skin = Image.open(BytesIO(img))
        return new_skin

class MCSkinFileProcessor:
    """
    A class for processing Minecraft skin files
    """
    def __init__(self, skin_type=None):
        self.skin_tools = MCSkinTools(skin_type)

    def _load_skin(self, input_path):
        """Load and verify Minecraft skin image"""
        try:
            img = Image.open(input_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            return img
        except Exception as e:
            print(f"✗ Error loading {os.path.basename(input_path)}: {str(e)}")
            return None
        
    def _verify_skin_dimensions(self, img, expected_size=(64, 64)):
        """Verify if skin image has the expected dimensions"""
        width, height = img.size
        if width != expected_size[0] or height != expected_size[1]:
            return False
        return True
 
    def convert_skin_64x32_to_64x64(self, input_path, output_path=None):
        """
        Convert a 64x32 Minecraft skin to 64x64 format

        Args:
            input_path (str): Path to input skin file
            output_path (str): Path for output file (optional)

        Returns:
            bool: True if conversion was successful
        """

        # Open the image
        img = self._load_skin(input_path)
        if img is None:
            print(f"✗ {os.path.basename(input_path)}: Error loading skin")
            return False
        
        # check if the skin is already 64x64
        if self._verify_skin_dimensions(img, (64, 64)):
            print(f"✓ {os.path.basename(input_path)} is already 64x64")
            return True
        elif not self._verify_skin_dimensions(img, (64, 32)):
            print(f"✗ {os.path.basename(input_path)}: Invalid dimensions expected 64x32")
            return False

        try:    
            # Perform conversion
            new_skin = self.skin_tools.convert_skin_64x32_to_64x64(img)

            # Determine output path
            if output_path is None:
                # Create output filename
                base_name = os.path.splitext(input_path)[0]
                output_path = f"{base_name}_64x64.png"

            # Save the converted skin
            try:
                new_skin.save(output_path, 'PNG')
            except Exception as e:
                print(f"✗ Error saving {os.path.basename(output_path)}: {str(e)}")
                return False
            
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
            img = self._load_skin(input_file)
            if img is None:
                return False
            if not self._verify_skin_dimensions(img, (64, 64)):
                print(f"✗ {os.path.basename(input_file)}: Invalid dimensions expected 64x64")
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
            img = self._load_skin(input_file)
            if img is None:
                return False
            if not self._verify_skin_dimensions(img, (64, 64)):
                print(f"✗ {os.path.basename(input_file)}: Invalid dimensions expected 64x64")
                return False

            new_skin = self.skin_tools.twice_swap_skin_layer(img)
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
            img = self._load_skin(input_file)
            if img is None:
                return False
            if not self._verify_skin_dimensions(img, (64, 64)):
                print(f"✗ {os.path.basename(input_file)}: Invalid dimensions expected 64x64")
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

    def convert_skin_type(self, input_file, output_file=None, target_type=None):
        """
        Convert a skin image to specified type
        Args:
            input_file (str): Path to the input file
            output_file (str): Path to the output file
            skin_type (str): Type of skin to convert to (e.g., 'regular', 'slim', 'steve', 'alex')
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            img = self._load_skin(input_file)
            if img is None:
                return False
            if not self._verify_skin_dimensions(img, (64, 64)):
                print(f"✗ {os.path.basename(input_file)}: Invalid dimensions expected 64x64")
                return False

            new_skin = self.skin_tools.convert_skin_type(img, target_type)
            if output_file is None:
                output_file = os.path.splitext(input_file)[0] + f'_{target_type}.png'
            new_skin.save(output_file)

            print(f"✓ {os.path.basename(input_file)}: Saved convert skin type to {output_file}")
            return True
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def batch_convert_folder(self, convert_func, input_folder, output_folder=None, layer_index=None, overwrite=False):
        """
        Convert all skins in a folder with specified convert function

        Args:
            input_folder (str): Path to folder containing skins
            convert_func (function): Function to apply to each skin
            output_folder (str): Output folder path (optional)
            layer_index (int): Index of the layer to remove (1 or 2) for remove_layer function
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


