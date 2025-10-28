
import argparse
import sys
import os
from .tools import MCSkinTools, MCSkinFileProcessor

def main():
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

  # Convert skin from base64 string
  mcskinprep -c -b base64_skin_string
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
        img = MCSkinTools.load_skin_from_base64(args.base64)
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