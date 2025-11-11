
import argparse
import sys
import os

from .file_processor import MCSkinFileProcessor
from .decorators import OperationName


import importlib.metadata

from typing import Optional

try:
    __version__ = importlib.metadata.version('mcskinprep')
except importlib.metadata.PackageNotFoundError:
    __version__ = '0.2.0'

def main() -> None:
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Convert Minecraft skins from 64x32 to 64x64 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single skin
  mcskinprep -c old_skin.png
  
  # Convert all skins in a folder
  mcskinprep -c -i skins_folder
  
  # Convert with custom output folder
  mcskinprep -c -i old_skins -o new_skins

  # Convert and overwrite existing files
  mcskinprep -c -i skins_folder --overwrite

  # Swap layer2 and layer1
  mcskinprep -s old_skin.png

  # Swap layer2 and layer1 twice (to remove invalid areas)
  mcskinprep -ss old_skin.png

  # Remove layer1
  mcskinprep -rm 1 old_skin.png

  # Remove layer2
  mcskinprep -rm 2 old_skin.png

  # Convert skin type (e.g., steve to alex)
  mcskinprep -to alex old_skin.png

  # Convert skin from base64 string
  mcskinprep -c -b base64_skin_string

  # Detect skin type
  mcskinprep old_skin.png -dp skintype
  
  # Detect skin layer1 has non transparent pixels:
  mcskinprep old_skin.png -dp pixels -dp_layer 1

  # Detect skin layer1 has non transparent pixels in body region:
  mcskinprep old_skin.png -dp pixels -dp_layer 1 -dp_region body

  # Detect skin layer1 has transparency in body region:
  mcskinprep old_skin.png -dp transparency -dp_layer 1 -dp_region body
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
    parser.add_argument('-to', '--target-type', choices=['steve', 'alex', 'regular', 'slim'], help='Target skin type (steve or alex)')
    parser.add_argument('-to_mode', choices=['0','1','2','3'], help='Mode for skin type convert, steve_to_alex have mode [0,1,2,3], default is 2, alex_to_steve have mode [0,1,2], default is 1')
    parser.add_argument('-t', '--type', choices=['steve', 'alex', 'regular', 'slim'], help='Skin type (steve or alex)')
    parser.add_argument('-dp', '--detect-properties', choices=['skintype','pixels','transparency','all'], default=None, help='Detect properties (skintype, pixels, transparency, all)')
    parser.add_argument('-dp_layer', nargs='+', type=int, choices=[1, 2], default=[1], help='Layer for detect properties (eg., 1, 2, 1 2) default is 1')
    parser.add_argument('-dp_region', nargs='+', choices=['head', 'body', 'right_arm', 'left_arm', 'right_leg', 'left_leg'], default=None, help='Regions for detect properties (e.g., head, body, right_arm), None for all regions')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()

    if not any([args.convert, args.swap_layer2_to_layer1, args.twice_swap_layer2_to_layer1, args.remove_layer, args.target_type, args.detect_properties]):
        if not args.version:
            parser.print_help()
            return

    if args.type:
        processor = MCSkinFileProcessor(skin_type=args.type)
    else:
        processor = MCSkinFileProcessor()
    
    # Determine function

    def convert_func(input_path: str, output_path: Optional[str] = None) -> bool:
        if args.convert:
            convert_func.operation_name = "convert_skin_64x32_to_64x64"
            return processor.convert_skin_64x32_to_64x64(input_path, output_path)
        elif args.swap_layer2_to_layer1:
            convert_func.operation_name = "swap_skin_layer2_to_layer1"
            return processor.swap_skin_layer2_to_layer1(input_path, output_path)
        elif args.twice_swap_layer2_to_layer1:
            convert_func.operation_name = "twice_swap_skin_layers"
            return processor.twice_swap_skin_layers(input_path, output_path)
        elif args.remove_layer:
            convert_func.operation_name = "remove_skin_layer"
            return processor.remove_layer(input_path, output_path, layer_index=args.remove_layer)
        elif args.target_type:
            convert_func.operation_name = "convert_skin_type"
            mode = int(args.to_mode) if args.to_mode is not None else None
            return processor.convert_skin_type(input_path, output_path, target_type=args.target_type, mode=mode)
        else:
            return None
    
    def detect_func(input_path: str, output_path: Optional[str] = None) -> bool:
        if args.detect_properties == 'skintype':
            detect_func.operation_name = "detect_skin_type"
            return processor.detect_skin_type(input_path, output_path)
        elif args.detect_properties == 'pixels':
            detect_func.operation_name = "detect_region_pixels"
            return processor.detect_region_pixels(input_path, output_path, layers=args.dp_layer, regions=args.dp_region)
        elif args.detect_properties == 'transparency':
            detect_func.operation_name = "detect_region_transparency"
            return processor.detect_region_transparency(input_path, output_path, layers=args.dp_layer, regions=args.dp_region)
        elif args.detect_properties == 'all':
            detect_func.operation_name = "detect_region_all"
            return processor.detect_region_all(input_path, output_path, layers=args.dp_layer, regions=args.dp_region)
        else:
            return None
    

    # Determine input source
    if args.base64:
        img, input_path = processor.load_skin_from_base64(args.base64)
        if img is None or input_path is None:
            print("Error: Failed to decode base64 string")
            return
    elif args.input_folder:
        input_path = args.input_folder
    elif args.input:
        input_path = args.input
    else:
        parser.print_help()
        return
    
    # Check if input is file or folder
    # detection
    if args.detect_properties:
        if os.path.isfile(input_path):
            # Single file detection
            detect_func(input_path, args.output_folder)
        elif os.path.isdir(input_path):
            # Batch detection
            processor.batch_detect_folder(detect_func=detect_func, input_folder=input_path, output_folder=args.output_folder, regions=args.dp_region, layers=args.dp_layer, overwrite=args.overwrite)
        else:
            print(f"Error: '{input_path}' is not a valid file or directory")
            sys.exit(1)
    # conversion
    else:
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