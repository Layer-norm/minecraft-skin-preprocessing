"""
Detector for Minecraft skin regions.

This module provides functionality to detect if skin regions have pixels or transparency.
"""

import numpy as np
from PIL import Image

from .skin_type import MCSkinType
from .constants import DEFAULT_MC_SKIN_REGIONS

from typing import List, Optional, Callable


class MCSkinRegionDetector:
    """
    A class for detecting properties of Minecraft skin regions.
    """

    def __init__(self, skin_type: Optional[str] = None) -> None:
        """
        Initialize the MCSkinRegionDetector.
        
        Args:
            skin_type (Optional[str]): The skin type ('slim', 'regular', 'steve', 'alex')
        """
        self.type_detector = MCSkinType(skin_type=skin_type)
        try:
            self.skin_regions = self.type_detector.skin_regions
        except (ValueError, AttributeError):
            self.skin_regions = DEFAULT_MC_SKIN_REGIONS

    def _get_layers_to_check(self, layer: Optional[List[int]]) -> List[str]:
        """
        Determine which layers to check based on input.
        
        Args:
            layer (Optional[int]): Layer to check (1 for layer1, 2 for layer2). 
                                   If None, check both layers.
                                   
        Returns:
            List[str]: List of layer names to check
        """
        if layer is None:
            return ['layer1', 'layer2']
        else:
            return [f'layer{x}' for x in layer]
        

    def _get_regions_to_check(self, regions: Optional[List[str]]) -> List[str]:
        """
        Determine which regions to check based on input.
        
        Args:
            regions (Optional[List[str]]): List of region names to check. 
                                           If None, check all regions.
                                           
        Returns:
            List[str]: List of region names to check
        """
        if regions is None:
            return list(self.skin_regions['layer1'].keys()) # Layer1 and Layer2 have same regions.
        return regions
    
    def _check_condition_in_regions(self, 
                                    condition_func: Callable[[np.ndarray], bool],
                                    regions: Optional[List[str]] = None, 
                                    layer: Optional[List[int]] = None,
                                    skin_img: Image.Image = None) -> bool:
        """
        Check if a condition is met in specified regions.
        
        Args:
            condition_func (Callable[[np.ndarray], bool]): Function that takes an alpha channel array 
                                                           and returns a boolean
            regions (Optional[List[str]]): List of region names to check. If None, check all regions.
            layer (Optional[int]): Layer to check (1 for layer1, 2 for layer2). If None, check both layers.
            skin_img (Image.Image): The skin image to analyze
            
        Returns:
            bool: True if condition is met in any of the specified regions, False otherwise
        """
        if skin_img.mode != 'RGBA':
            skin_img = skin_img.convert('RGBA')
            
        layers_to_check = self._get_layers_to_check(layer)
        regions_to_check = self._get_regions_to_check(regions)
            
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
                            if condition_func(alpha_channel):
                                return True
        return False

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
           return self._check_condition_in_regions(
               lambda alpha_channel: np.any(alpha_channel > 0),
               regions, layer, skin_img
           )
    
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
        return self._check_condition_in_regions(
            lambda alpha_channel: np.any(alpha_channel == 0),
            regions, layer, skin_img
        )