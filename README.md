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

## Update

- 2025-11-1: Add support for skin convert between regular and slim (steve and alex).
- 2025-10-30: Add function for skin type detection (steve or alex).
- 2025-10-29: Initial release.

## Working in Progress

- [ ] skin type detection in cli.
- [ ] two skins merge by layer.
- [ ] Improve examples.

## Installation

Install the package using pip:

```bash
pip install mcskinprep
```

## Usage

### Command Line Interface

The package provides a command line interface for easy skin preprocessing.

#### Arguments

- `input`: Input file or folder path (optional).
- `-c, --convert`: Convert 64x32 skins to 64x64 format.
- `-i, --input-folder`: Specify the input folder containing skins.
- `-o, --output-folder`: Specify the output folder for converted skins.
- `-t, --type`: Specify the source skin type (steve or alex) for conversion.
- `-s, --swap-layer2-to-layer1`: Swap layer2 to layer1 for skins.
- `-ss`: Swap layer2 and layer1 twice to remove invalid areas.
- `-rm, --remove-layer`: Remove specified layer (1 or 2) for skins.
- `-to, --target-type`: Convert skin between regular (steve) and slim (alex) types.
- `-b, --base64`: Process Base64-encoded skin images.
- `--overwrite`: Overwrite existing files.
- `-h, --help`: Show help message.
- `-v, --version`: Show version information.

#### Examples
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
from mcskinprep import MCSkinTools
from PIL import Image

# Create tools instance
tools = MCSkinTools()

# Load an image
img = Image.open("skin.png")

# Convert 64x32 to 64x64
converted_img = tools.convert_skin_64x32_to_64x64(img)

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
```

## License

This project is licensed under the [MIT License](LICENSE).