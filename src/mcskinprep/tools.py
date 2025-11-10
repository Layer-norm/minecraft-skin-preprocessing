"""
Minecraft Skin Preprocessing Tool

Author: Faxuan Cai

License: MIT License

Description:
Converts legacy 64x32 skins to modern 64x64 format
Swap layer2 and layer1
Remove specific layer
"""

import numpy as np
from PIL import Image
import base64
from io import BytesIO

from .skin_type import MCSkinType

from typing import Optional

class MCSkinTools:
    """
    A class for preprocessing Minecraft skins
    """

    def __init__(self, skin_type: Optional[str] = None) -> None:
        """Initialize the MCSkinTools class"""
        self.skin_type = skin_type
        self.type_detector = MCSkinType(skin_type=skin_type)

        try:
            self.skin_regions = self.type_detector.skin_regions
        except (ValueError, AttributeError):
            self.skin_regions = self.type_detector.regular_regions

        self.regular_regions = self.type_detector.regular_regions
        self.slim_regions = self.type_detector.slim_regions
        self.adjust_regions = self.type_detector.adjust_regions

 
    def convert_skin_64x32_to_64x64(self, img: Image.Image) -> Image.Image:
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

    def swap_skin_layer2_to_layer1(self, img: Image.Image) -> Image.Image:
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
    
    def twice_swap_skin_layer(self, img: Image.Image) -> Image.Image:
        """swap layer1 and layer2 twice in a 64x64 skin image"""
        new_skin = self.swap_skin_layer2_to_layer1(img)
        new_skin = self.swap_skin_layer2_to_layer1(new_skin)
        return new_skin
    
    def remove_layer(self, img: Image.Image, layer_index: int) -> Image.Image:
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
    
    def steve_to_alex(self, img: Image.Image , index: int = 2) -> Image.Image:
        """Convert a steve skin image to alex skin type"""
        self.skin_type = self.type_detector.auto_detect_skin_type(img)
        if self.skin_type not in ["steve", "regular", "alex", "slim"]:
            raise ValueError(f"✗ Invalid skin type: {self.skin_type}")
        elif self.skin_type in ["alex", "slim"]:
            return img

        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        i = index

        if i not in [0, 1, 2, 3]:
            raise ValueError(f"✗ Invalid delete index: {i}")
        
        delete_columns = {
            "right_arm": [
                [i, 4 + i],                 # delete right arm column i and 4 + i
                [4 + i, 3 * 4 + (3 - i)]    # delete right arm column 4 + i and 11 + (3 - i)
            ],
            "left_arm": [
                [3 - i, 4 + (3 - i)],       # delete left arm column 3 - i and 4 + (3 - i)
                [4 + (3 - i), 3 * 4 + i]    # delete left arm column 4 + (3 - i) and 11 + i
            ]
        }

        for layer, regions in self.regular_regions.items():
            for region, parts in regions.items():
                if region not in self.adjust_regions:
                    for part in parts:
                        part_img = img.crop(part["coords"])
                        new_skin.paste(part_img, part["coords"])
                else:
                    arm_parts = self.regular_regions[layer][region]
                    col_indices = delete_columns[region]

                    for idx, (part, delect_col) in enumerate(zip(arm_parts, col_indices)):
                        part_img = img.crop(part["coords"])
                        part_array = np.array(part_img)

                        new_part_array = np.delete(part_array, delect_col, axis=1)
                        new_part_img = Image.fromarray(new_part_array, mode='RGBA')

                        target_coords = self.slim_regions[layer][region][idx]["coords"]
                        new_skin.paste(new_part_img, target_coords)

        return new_skin
    
    def alex_to_steve(self, img: Image.Image, index: int = 1) -> Image.Image:
        """Convert a alex skin image to steve skin type"""
        self.skin_type = self.type_detector.auto_detect_skin_type(img)
        if self.skin_type not in ["alex", "slim", "steve", "regular"]:
            raise ValueError(f"✗ Invalid skin type: {self.skin_type}")
        elif self.skin_type in ["steve", "regular"]:
            return img
        
        new_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))

        i = index

        if i not in [0, 1, 2]:
            raise ValueError(f"✗ Invalid append index: {i}")

        # Insert columns in reverse order to avoid index shift
        insert_columns = {
            "right_arm": [
                [3 + i, i],           # right_arm part1: i and 3+i
                [11 + (2 - i), 4 + i] # right_arm part2: 4+i and 11+(2-i)
            ],
            "left_arm": [
                [3 + (2 - i), 2 - i], # left_arm part1: 2-i and 3+(2-i)
                [11 + i, 4 + (2 - i)] # left_arm part2: 4+(2-i) and 11+i
            ]
        }

        for layer, regions in self.regular_regions.items():
            for region, parts in regions.items():
                if region not in self.adjust_regions:
                    for part in parts:
                        part_img = img.crop(part["coords"])
                        new_skin.paste(part_img, part["coords"])
                else:
                    arm_parts = self.slim_regions[layer][region]
                    indices = insert_columns[region]

                    for idx, (part, insert_col) in enumerate(zip(arm_parts, indices)):
                        part_img = img.crop(part["coords"])

                        new_part_array = np.array(part_img)

                        for pos in insert_col:
                            column_to_copy = new_part_array[:, pos, :]
                            new_part_array = np.insert(new_part_array, pos, column_to_copy, axis=1)

                        new_part_img = Image.fromarray(new_part_array, mode='RGBA')

                        target_coords = self.regular_regions[layer][region][idx]["coords"]

                        new_skin.paste(new_part_img, target_coords)

        return new_skin

    def convert_skin_type(self, img: Image.Image, target_type: Optional[str] = None, mode: Optional[int] = None) -> Optional[Image.Image]:
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
            if mode is None:
                mode = 2
            new_skin = self.alex_to_steve(img, index=mode)
        elif target_type in ["alex", "slim"]:
            if mode is None:
                mode = 1
            new_skin = self.steve_to_alex(img, index=mode)
        else:
            print(f"✗ Invalid skin type: {self.skin_type}")
            return None
        return new_skin

    @staticmethod
    def load_skin_from_base64(base64_str: str) -> Image.Image:
        """Load skin image from base64 string"""
        img = base64.b64decode(base64_str)
        new_skin = Image.open(BytesIO(img))
        return new_skin

    @staticmethod
    def convert_skin_to_base64(img: Image.Image) -> str:
        """Convert skin image to base64 string"""
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        base64_str = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
        return base64_str
