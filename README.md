# minecraft-skin-preprocessing

A Minecraft skin preprocessing Python script.

## Features

- Convert legacy 64x32 skins to modern 64x64 format.
- Swap layer2 and layer1 for skins.
- Swap layer2 and layer1 twice to remove invalid areas.
- Remove specified layer (1 or 2) for skins.
- Process skins from Base64-encoded strings.
- Batch processing of skins in folders.
- Customizable output folder for converted skins.
- Option to overwrite existing files.

## Installation

Ensure you have Python installed on your system. Clone this repository and navigate to the project directory.
Install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Convert format of a single skin (64x32 to 64x64)
```bash
python preprocess.py -c old_skin.png
```

### Convert all skins in a folder
```bash
python preprocess.py -c -i skins_folder
```

### Convert with a custom output folder
```bash
python preprocess.py -c -i old_skins -o new_skins
```

### Convert and overwrite existing files
```bash
python preprocess.py -c -i skins_folder --overwrite
```

### Swap layer2 to layer1 for a single skin
```bash
python preprocess.py -s old_skin.png
```

### Swap layer2 and layer1 twice (to remove invalid areas)
```bash
python preprocess.py -ss old_skin.png
```

### Remove layer1 from a skin
```bash
python preprocess.py -rm 1 old_skin.png
```

### Remove layer2 from a skin
```bash
python preprocess.py -rm 2 old_skin.png
```

### Convert skin from a Base64 string
```bash
python preprocess.py -c -b base64_skin_string
```

## Arguments

- `input`: Input file or folder path (optional).
- `-c, --convert`: Convert 64x32 skins to 64x64 format.
- `-i, --input-folder`: Specify the input folder containing skins.
- `-o, --output-folder`: Specify the output folder for converted skins.
- `-s, --swap-layer2-to-layer1`: Swap layer2 to layer1 for skins.
- `-ss`: Swap layer2 and layer1 twice to remove invalid areas.
- `-rm, --remove-layer`: Remove specified layer (1 or 2) for skins.
- `-b, --base64`: Process Base64-encoded skin images.
- `--overwrite`: Overwrite existing files.

## License

This project is licensed under the [MIT License](LICENSE).