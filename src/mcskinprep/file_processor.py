
import os
from PIL import Image

from .tools import MCSkinTools


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
 
    def load_skin_from_base64(self, base64_string):
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

    def convert_skin_type(self, input_file, output_file=None, target_type=None, mode=None):
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

