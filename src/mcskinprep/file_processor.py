
import os
import json
from PIL import Image

from .tools import MCSkinTools
from .detector import MCSkinRegionDetector

from typing import Optional, Tuple, Callable, List


class MCSkinFileProcessor:
    """
    A class for processing Minecraft skin files
    """
    def __init__(self, skin_type: Optional[str] = None) -> None:
        self.skin_type = skin_type
        self.skin_tools = MCSkinTools(skin_type)
        self._detection_method = "pixels"

    @property
    def detection_method(self) -> str:
        """Get the current detection method"""
        return self._detection_method

    def _load_skin(self, input_path: str) -> Optional[Image.Image]:
        """Load and verify Minecraft skin image"""
        try:
            with Image.open(input_path) as img:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # create a copy to ensure the file is closed
                img_copy = img.copy()
            return img_copy
        except Exception as e:
            print(f"✗ Error loading {os.path.basename(input_path)}: {str(e)}")
            return None
        
    def _verify_skin_dimensions(self, img: Image, expected_size: Tuple[int, int]= (64, 64)) -> bool:
        """Verify if skin image has the expected dimensions"""
        width, height = img.size
        if width != expected_size[0] or height != expected_size[1]:
            return False
        return True


    def load_skin_from_base64(self, base64_string: str) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Load skin from base64 encoded string

        Args:
            base64_string (str): Base64 encoded skin image

        Returns:
            tuple: (Image object, temporary file path)
        """
        try:
            img = MCSkinTools.load_skin_from_base64(base64_string)
            temp_path = "base64_skin.png"
            img.save(temp_path, 'PNG')
            return img, temp_path
        except Exception as e:
            print(f"✗ Error loading skin from base64: {str(e)}")
            return None, None

    def convert_skin_64x32_to_64x64(self, input_path: str, output_path: Optional[str] = None) -> bool:
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

    def swap_skin_layer2_to_layer1(self,input_file: str, output_file: Optional[str] = None) -> bool:
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

    def twice_swap_skin_layers(self, input_file: str, output_file: Optional[str] = None) -> bool:
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

    def remove_layer(self, input_file: str, output_file: Optional[str] = None, layer_index: Optional[int] = None) -> bool:
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

    def convert_skin_type(self, input_file: str, output_file: Optional[str] = None, target_type: Optional[str] = None, mode: Optional[int] = None) -> bool:
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

            new_skin = self.skin_tools.convert_skin_type(img, target_type, mode)
            if output_file is None:
                output_file = os.path.splitext(input_file)[0] + f'_{target_type}.png'
            new_skin.save(output_file)

            print(f"✓ {os.path.basename(input_file)}: Saved convert skin type to {output_file}")
            return True
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")
            return False

    def _detect_skin(self, input_file: str, output_file: Optional[str] = None,
                               regions: Optional[List[str]] = None, 
                               layers: Optional[List[int]] = None,
                               save_base64: Optional[bool] = False,
                               detection_method: str = "skintype") -> bool:
        """
        Internal method to detect skin
        
        Args:
            input_file (str): Path to the input skin file
            output_file (str): Path to the output JSONL file
            regions (list): List of region names to check. If None, check all regions.
            layers (list): List of layer indices to check (1 for layer1, 2 for layer2, [1,2] for both). If None, check both layers.
            detection_method (str): Type of detection ("skintype" or "pixels" or "transparency" or "all")
            
        """
        try:
            img = self._load_skin(input_file)
            if img is None:
                return False
            
            if not self._verify_skin_dimensions(img, (64, 64)):
                print(f"✗ {os.path.basename(input_file)}: Invalid dimensions expected 64x64")
                return False
            
            # Create detector instance
            if self.skin_type is None or detection_method == "skintype":
                skin_type = self.skin_tools.type_detector.auto_detect_skin_type(img)
            else:
                skin_type = self.skin_type

            result = {
                "filename": os.path.basename(input_file),
                "skin_type": skin_type,
            }
            
            if detection_method != "skintype":
                detector = MCSkinRegionDetector(skin_type)
                
                # Get regions to check
                regions_to_check = regions if regions is not None else list(detector.skin_regions['layer1'].keys())
                layers_to_check = layers if layers is not None else [1, 2]

                # Perform detection and write results
                if detection_method == "pixels":
                    result_value = detector.has_pixels(regions_to_check, layers_to_check, img)
                    result["checked_layers"] = layers_to_check
                    result["checked_regions"] = regions_to_check
                    result["has_pixels"] = result_value
                elif detection_method == "transparency":
                    result_value = detector.has_transparency(regions_to_check, layers_to_check, img)
                    result["checked_layers"] = layers_to_check
                    result["checked_regions"] = regions_to_check
                    result["has_transparency"] = result_value
                elif detection_method == "all":
                    result["checked_layers"] = layers_to_check
                    result["checked_regions"] = regions_to_check
                    result["has_pixels"] = detector.has_pixels(regions_to_check, layers_to_check, img)
                    result["has_transparency"] = detector.has_transparency(regions_to_check, layers_to_check, img) 
            
            if save_base64:
                result["image"] = self.skin_tools.convert_skin_to_base64(img)
                
            # Determine output path
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                if detection_method == "skintype":
                    suffix = "_skintype"
                elif detection_method == "all":
                    suffix = "_has_properties"
                else:
                    suffix = "_has_pixels" if detection_method == "pixels" else "_has_transparency"
                output_file = f"{base_name}{suffix}.jsonl"

            # write results
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            
            action = "skin type detection" if detection_method == "skintype" else (
                "pixel detection" if detection_method == "pixels" else "transparency detection")
            print(f"✓ {os.path.basename(input_file)}: Saved {action} results to {output_file}")
            return True
            
        except Exception as e:
            action = "skin type detection" if detection_method == "skintype" else (
                "pixel detection" if detection_method == "pixels" else "transparency detection")
            print(f"Error {action} in {input_file}: {str(e)}")
            return False

    def detect_skin_type(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """
        Detect skin type (slim or regular) based on skin image
        """
        self._detection_method = "skintype"
        return self._detect_skin(input_file, output_file, detection_method=self._detection_method)

    def detect_region_pixels(self, input_file: str, output_file: Optional[str] = None, 
                           regions: Optional[list] = None, layers: Optional[int] = None) -> bool:
        """
        Detect if specified regions have pixels (alpha != 0) in a skin image
        """
        self._detection_method = "pixels"
        return self._detect_skin(input_file, output_file, regions, layers, detection_method=self._detection_method)

    def detect_region_transparency(self, input_file: str, output_file: Optional[str] = None,
                                 regions: Optional[list] = None, layers: Optional[int] = None) -> bool:
        """
        Detect if specified regions have transparency (alpha == 0) in a skin image
        """        
        self._detection_method = "transparency"
        return self._detect_skin(input_file, output_file, regions, layers, detection_method=self._detection_method)
    
    def detect_region_all(self, input_file: str, output_file: Optional[str] = None,
                           regions: Optional[list] = None, layers: Optional[int] = None) -> bool:
        """
        Detect if specified regions have pixels (alpha != 0) and transparency (alpha == 0) in a skin image
        """
        self._detection_method = "all"
        return self._detect_skin(input_file, output_file, regions, layers, detection_method=self._detection_method)

    def _jsonl_suffix(self, detection_method: str,
                      regions: Optional[List[str]] = None, 
                      layers: Optional[List[int]] = None,) -> str:
        """
        Get JSONL suffix based on detection method
        """
        if detection_method == "skintype":
            return "_skintype"
        else:
            if regions is not None:
                region =''.join(str(x) for x in regions)
            else:
                region = 'all'
            if layers is not None:
                if len(layers) == 1:
                    layer = f"layer{layers[0]}"
                else:
                    layer = 'all'
            else:
                layer = 'layer1'
            if detection_method == "pixels":
                return f"{region}_{layer}_has_pixels"
            elif detection_method == "transparency":
                return f"{region}_{layer}_has_transparency"
            else:
                return f"{region}_{layer}_properties"
    

    def _batch_process_operation(self, input_folder: str, output_folder: Optional[str] = None,
                                 operation_func: Optional[Callable] = None, 
                                 operation_action: str = "convert",
                                 layer_index: Optional[int] = None,
                                 regions: Optional[List[str]] = None, 
                                 layers: Optional[List[int]] = None, 
                                 overwrite: bool = False) -> None:
        """
        Process all files in input folder using specified operation function

        Args:
            input_folder (str): Path to folder containing input files
            output_folder (str): Path to folder for output files (optional)
            operation_func (function): Function to apply to each file
            operation_action (str): Description of the operation (e.g., "convert", "detect")
            layer_index (int): Index of the layer to process (1 or 2) (optional)
            regions (list): List of region names to check (optional)
            layers (list): List of layer indices to process (optional)
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
        processed_files = 0
        skipped_files = 0
        error_files = 0

        print(f"{operation_action.capitalize()} skins in: {input_folder}")
        print(f"Output folder: {output_folder}")
        print("-" * 50)

        input_folder_name = os.path.basename(input_folder)

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
            if operation_action == "convert":
                if operation_func is self.convert_skin_64x32_to_64x64:
                    output_filename = f"{base_name}_64x64.png"
                elif operation_func is self.swap_skin_layer2_to_layer1:
                    output_filename = f"{base_name}_swap.png"
                elif operation_func is self.twice_swap_skin_layers:
                    output_filename = f"{base_name}_swap_swap.png"
                elif operation_func is self.remove_layer:
                    output_filename = f"{base_name}_rm_layer{layer_index}.png"    
                else:
                    output_filename = f"{base_name}_converted.png"
            elif operation_action == "detect":
                jsonl_suffix = self._jsonl_suffix(self._detection_method, regions, layers)
                output_filename = f"{input_folder_name}_{jsonl_suffix}.jsonl"
            
            output_path = os.path.join(output_folder, output_filename)

            # Handle overwrite logic for detection operations
            if operation_action == "detect" and os.path.exists(output_path) and overwrite:
                # If overwrite is True, remove the existing file to start fresh
                try:
                    os.remove(output_path)
                except Exception as e:
                    print(f"Warning: Could not remove existing file {output_path}: {str(e)}")

            # Check if output file already exists (only for convert operations or when not overwriting)
            if operation_action != "detect" and os.path.exists(output_path) and not overwrite:
                print(f"⏭️ Skipped {filename} (output already exists)")
                skipped_files += 1
                continue

             # Operate the skin
            if operation_func(file_path, output_path):
                processed_files += 1
            else:
                error_files += 1
        
        # Print summary
        print("-" * 50)
        if operation_action == "convert":
            print("Conversion Summary:")
        else:
            print(f"{self._detection_method.capitalize()} Detection Summary:")
        print(f"Total files processed: {total_files}")
        print(f"Successfully processed: {processed_files}")
        print(f"Skipped: {skipped_files}")
        print(f"Errors: {error_files}")


    def batch_convert_folder(self, convert_func: Callable[[str, Optional[str], Optional[str], Optional[int]], bool], 
                             input_folder: str, 
                             output_folder: Optional[str] = None, 
                             layer_index: Optional[int] = None, 
                             overwrite: bool = False) -> None:
        """
        Convert all skins in a folder with specified convert function
        """
        self._batch_process_operation(
            input_folder=input_folder,
            output_folder=output_folder,
            operation_action="convert",
            operation_func=convert_func,
            layer_index=layer_index,
            overwrite=overwrite
        )
    
    def batch_detect_folder(self, detect_func: Callable[[str, Optional[str], Optional[list], Optional[int]], bool], 
                             input_folder: str, 
                             output_folder: Optional[str] = None, 
                             regions: Optional[List[str]] = None,
                             layers: Optional[List[int]] = None, 
                             overwrite: bool = False) -> None:
        """
        Detect pixels or transparency in all skins in a folder with specified detect function
        """
        self._batch_process_operation(
            input_folder=input_folder,
            output_folder=output_folder,
            operation_action="detect",
            operation_func=detect_func,
            regions=regions,
            layers=layers,
            overwrite=overwrite
        )