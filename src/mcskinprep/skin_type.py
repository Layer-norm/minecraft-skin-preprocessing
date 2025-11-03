import numpy as np
from PIL import Image

from .constants import DEFAULT_MC_SKIN_REGIONS

from typing import Optional, Dict, List, Any

class MCSkinType:
    """
    Class for skin type (slim or regular)

    """
    
    def __init__(self, skin_type: Optional[str] = None, regular_regions: Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]] = None) -> None:
        self._skin_type = skin_type
        
        self.regular_regions = regular_regions if regular_regions is not None else DEFAULT_MC_SKIN_REGIONS
        self._slim_regions = {}
        self.adjust_regions = ['right_arm', 'left_arm']

    @property
    def skin_type(self) -> str:
        """
        Get skin type

        Returns:
            str: Skin type ('slim' or 'regular')
        """
        if self._skin_type is None:
            self._skin_type = 'regular'
        return self._skin_type
    
    @skin_type.setter
    def skin_type(self, value: str) -> str:
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
    def slim_regions(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
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
    def skin_regions(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
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

    def auto_detect_skin_type(self, skin_img: Image.Image) -> str:
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

