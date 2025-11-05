"""
Detector for Minecraft skin regions.

This module provides functionality to detect if skin regions have pixels or transparency.
"""

import numpy as np
from PIL import Image

from typing import List, Optional

from .skin_type import MCSkinType
from .constants import DEFAULT_MC_SKIN_REGIONS


class MCSkinRegionDetector:
    """
    A class for detecting properties of Minecraft skin regions.
    """

    def __init__(self, skin_type: Optional[str] = None) -> None:
        """
        Initialize the MCSkinRegionDetector.
        
        Args:
            skin_type (Optional[str]): The skin type ('slim' or 'regular')
        """
        self.type_detector = MCSkinType(skin_type=skin_type)
        try:
            self.skin_regions = self.type_detector.skin_regions
        except (ValueError, AttributeError):
            self.skin_regions = DEFAULT_MC_SKIN_REGIONS

    def has_pixels(self, 
                   regions: Optional[List[str]] = None, 
                   layer: Optional[int] = None,
                   skin_img: Image.Image = None) -> bool:
        """
        Check if specified regions have any pixels (alpha != 0).
        
        Args:
            regions (Optional[List[str]]): List of region names to check. If None, check all regions.
            layer (Optional[int]): Layer to check (1 for layer1, 2 for layer2). If None, check both layers.
            skin_img (Image.Image): The skin image to analyze
            
        Returns:
            bool: True if any of the specified regions contain pixels, False otherwise
        """
        if skin_img.mode != 'RGBA':
            skin_img = skin_img.convert('RGBA')
            
        layers_to_check = []
        if layer is None:
            layers_to_check = ['layer1', 'layer2']
        else:
            layers_to_check = [f'layer{layer}']
            
        regions_to_check = regions
        if regions_to_check is None:
            regions_to_check = list(self.skin_regions['layer1'].keys())
            
        for layer_name in layers_to_check:
            for region_name in regions_to_check:
                if region_name in self.skin_regions[layer_name]:
                    for part in self.skin_regions[layer_name][region_name]:
                        coords = part['coords']
                        # Make sure coordinates are within image bounds
                        if (coords[0] < skin_img.width and coords[1] < skin_img.height and 
                            coords[2] <= skin_img.width and coords[3] <= skin_img.height):
                            region_img = skin_img.crop(coords)
                            alpha_channel = np.array(region_img.split()[-1])
                            if np.any(alpha_channel > 0):
                                return True
        return False

    def has_transparency(self, 
                         regions: Optional[List[str]] = None, 
                         layer: Optional[int] = None,
                         skin_img: Image.Image = None) -> bool:
        """
        Check if specified regions have any transparent pixels (alpha == 0).
        
        Args:
            regions (Optional[List[str]]): List of region names to check. If None, check all regions.
            layer (Optional[int]): Layer to check (1 for layer1, 2 for layer2). If None, check both layers.
            skin_img (Image.Image): The skin image to analyze
            
        Returns:
            bool: True if any of the specified regions contain transparency, False otherwise
        """
        if skin_img.mode != 'RGBA':
            skin_img = skin_img.convert('RGBA')
            
        layers_to_check = []
        if layer is None:
            layers_to_check = ['layer1', 'layer2']
        else:
            layers_to_check = [f'layer{layer}']
            
        regions_to_check = regions
        if regions_to_check is None:
            regions_to_check = list(self.skin_regions['layer1'].keys())
            
        for layer_name in layers_to_check:
            for region_name in regions_to_check:
                if region_name in self.skin_regions[layer_name]:
                    for part in self.skin_regions[layer_name][region_name]:
                        coords = part['coords']
                        # Make sure coordinates are within image bounds
                        if (coords[0] < skin_img.width and coords[1] < skin_img.height and 
                            coords[2] <= skin_img.width and coords[3] <= skin_img.height):
                            region_img = skin_img.crop(coords)
                            alpha_channel = np.array(region_img.split()[-1])
                            if np.any(alpha_channel == 0):
                                return True
        return False