# minecraft-skin-preprocessing

A Minecraft skin preprocessing Python script.

## Features

- Convert legacy 64x32 skins to modern 64x64 format.
- Convert regular (steve) skin to slim (alex) and vice versa.
- Swap layer2 and layer1 for skins.
- Swap layer2 and layer1 twice to remove invalid areas.
- Remove specified layer (1 or 2) for skins.
- Process skins from Base64-encoded strings.
- Batch processing of skins in folders.
- Customizable output folder for converted skins.
- Option to overwrite existing files.
- Skin type detection (regular or slim).
- Pixels and transparency detection in specific regions.
---
## Update

- 2025-11-11: Add pixel and transparency detection in specific regions.
- 2025-11-4: refactor code.
- 2025-11-1: Add support for skin convert between regular and slim (steve and alex).
- 2025-10-30: Add function for skin type detection (steve or alex).
- 2025-10-29: Initial release.

---
## Installation

Install the package using pip:

```bash
pip install mcskinprep
```
---
## Usage

### Command Line Interface

The package provides a command line interface for easy skin preprocessing.

#### Arguments

- `input`: Input file or folder path (optional).
- `-c, --convert`: Convert 64x32 skins to 64x64 format.
- `-i, --input-folder`: Specify the input folder containing skins.
- `-o, --output-folder`: Specify the output folder for processed skins or output jsonl.
- `-t, --type`: Specify the source skin type (steve or alex) for conversion.
- `-s, --swap-layer2-to-layer1`: Swap layer2 to layer1 for skins.
- `-ss, --twice-swap-layer2-to-layer1`: Swap layer2 and layer1 twice to remove invalid areas.
- `-rm, --remove-layer`: Remove specified layer (1 or 2) for skins.
- `-to, --target-type`: Convert skin between regular (steve) and slim (alex) types.
- `-b, --base64`: Process Base64-encoded skin images.
- `-dp, --detect-properties`: Detect properties (skintype, pixels, transparency) , all for detect all properties.
- `-dp_layer, --detect-properties-layer`: Layer for detect properties (e.g., 1, 2, 1 2) default is 1.
- `-dp_region, --detect-properties-region`: Regions for detect properties (e.g., head, body, right_arm), None for all regions.
- `-dp_base64, --detect-properties-base64`: Save detect results in base64 format in jsonl file.
- `--overwrite`: Overwrite existing files.
- `-h, --help`: Show help message.
- `-v, --version`: Show version information.

#### Examples
---
##### New examples
Detect skin type (regular or slim):
```bash
mcskinprep old_skin.png -dp skintype
```

Detect skin layer pixels in layer 1(result save in xx_all_l1_has_pixels.jsonl):
```bash
mcskinprep old_skin.png -dp pixels
```

Detect skin specific region pixels in layer 1 (save in xx_h_l1_has_pixels.jsonl):

```bash
mcskinprep old_skin.png -dp pixels -dp_region head  -dp_layer 1
```

Detect skin layer transparency(save in xx_hra_l1_has_transparency.jsonl):
```bash
mcskinprep old_skin.png -dp transparency -dp_region head right_arm -dp_layer 1
```
---

Convert format of a single skin (64x32 to 64x64)
```bash
mcskinprep -c old_skin.png
```

Convert all skins in a folder
```bash
mcskinprep -c -i skins_folder
```

Convert with a custom output folder
```bash
mcskinprep -c -i old_skins -o new_skins
```

Convert and overwrite existing files
```bash
mcskinprep -c -i skins_folder --overwrite
```

Swap layer2 and layer1 for a single skin
```bash
mcskinprep -s old_skin.png
```

Swap layer2 and layer1 twice (to remove invalid areas)
```bash
mcskinprep -ss old_skin.png
```

Remove layer2 from a skin
```bash
mcskinprep -rm 2 old_skin.png
```

Convert skin type (steve to alex or vice versa)
```bash
mcskinprep -to alex old_skin.png
mcskinprep -to steve old_skin.png
```

Convert skin from a Base64 string
```bash
mcskinprep -c -b base64_skin_string
```

### Python API

The package also provides a Python API for programmatic skin preprocessing.

#### Examples

usage of core tools
```python
from mcskinprep import MCSkinTools, MCSkinType
from PIL import Image

# Create tools instance
tools = MCSkinTools()

# Load an image
img = Image.open("skin.png")

# Convert 64x32 to 64x64
converted_img = tools.convert_skin_64x32_to_64x64(img)

# Detect skin type
skin_type_detector = MCSkinType()
skin_type = skin_type_detector.auto_detect_skin_type(img)
print(f"Detected skin type: {skin_type}")

# convert skin type (steve to alex or vice versa)
converted_img = tools.convert_skin_type(img, target_type="alex")
# or
converted_img = tools.steve_to_alex(img)

# Swap layers
swapped_img = tools.swap_skin_layer2_to_layer1(img)

# Remove layer
layer_removed_img = tools.remove_layer(img, layer_index=1)

# Save results
converted_img.save("converted_skin.png")

```
usage of file processor 

```python
from mcskinprep import MCSkinFileProcessor

# Create processor instance
processor = MCSkinFileProcessor()

# Convert a single 64x32 skin to 64x64
processor.convert_skin_64x32_to_64x64("old_skin.png", "new_skin.png")

# Swap layers in a skin
processor.swap_skin_layer2_to_layer1("skin.png", "swapped_skin.png")

# Swap layers twice to remove invalid areas
processor.twice_swap_skin_layers("skin.png", "clean_skin.png")

# Remove a specific layer
processor.remove_layer("skin.png", "no_layer1_skin.png", layer_index=1)

# Batch process skins in a folder
processor.batch_convert_folder(
    convert_func=processor.convert_skin_64x32_to_64x64,
    input_folder="input_skins/",
    output_folder="output_skins/",
    overwrite=False
)

# Detect wheather head region in layer 1 has transparent pixels in a folder
batch_detect_folder(
     detect_func=processor.detect_region_transparency, 
     input_folder="input_skins/",
     output_folder="output_skins/",
     regions=["head"],
     layers=[1], 
     overwrite=False
)
```

## License

This project is licensed under the [MIT License](LICENSE).