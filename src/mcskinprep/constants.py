"""
Constants for the Minecraft skin preprocessing package.

Contains:
- DEFAULT_MC_SKIN_REGIONS: A dictionary containing the default skin regions for each layer.
- DEFAULT_FILE_SUFFIXES: A dictionary containing the default file suffixes for each operation.

"""

DEFAULT_MC_SKIN_REGIONS = {
    "layer1": {
        "head": [
            {"name": "head1_layer1", "coords": [8, 0, 24, 8]},
            {"name": "head2_layer1", "coords": [0, 8, 32, 16]}
        ],
        "body": [
            {"name": "body1_layer1", "coords": [20, 16, 36, 20]},
            {"name": "body2_layer1", "coords": [16, 20, 40, 32]}
        ],
        "right_arm": [
            {"name": "right_arm1_layer1", "coords": [44, 16, 52, 20]},
            {"name": "right_arm2_layer1", "coords": [40, 20, 56, 32]}
        ],
        "left_arm": [
            {"name": "left_arm1_layer1", "coords": [36, 48, 44, 52]},
            {"name": "left_arm2_layer1", "coords": [32, 52, 48, 64]}
        ],
        "right_leg": [
            {"name": "right_leg1_layer1", "coords": [4, 16, 12, 20]},
            {"name": "right_leg2_layer1", "coords": [0, 20, 16, 32]}
        ],
        "left_leg": [
            {"name": "left_leg1_layer1", "coords": [20, 48, 28, 52]},
            {"name": "left_leg2_layer1", "coords": [16, 52, 32, 64]}
        ]
    },
    "layer2": {
        "head": [
            {"name": "head1_layer2", "coords": [40, 0, 56, 8]},
            {"name": "head2_layer2", "coords": [32, 8, 64, 16]}
        ],
        "body": [
            {"name": "body1_layer2", "coords": [20, 32, 36, 36]},
            {"name": "body2_layer2", "coords": [16, 36, 40, 48]}
        ],
        "right_arm": [
            {"name": "right_arm1_layer2", "coords": [44, 32, 52, 36]},
            {"name": "right_arm2_layer2", "coords": [40, 36, 56, 48]}
        ],
        "left_arm": [
            {"name": "left_arm1_layer2", "coords": [52, 48, 60, 52]},
            {"name": "left_arm2_layer2", "coords": [48, 52, 64, 64]}
        ],
        "right_leg": [
            {"name": "right_leg1_layer2", "coords": [4, 32, 12, 36]},
            {"name": "right_leg2_layer2", "coords": [0, 36, 16, 48]}
        ],
        "left_leg": [
            {"name": "left_leg1_layer2", "coords": [4, 48, 12, 52]},
            {"name": "left_leg2_layer2", "coords": [0, 52, 16, 64]}
        ]
    }
}

DEFAULT_FILE_SUFFIXES = {
    "convert": {
        "convert_skin_64x32_to_64x64": "_64x64.png",
        "swap_skin_layer2_to_layer1": "_swap.png",
        "twice_swap_skin_layers": "_swap_swap.png",
        "remove_layer": "_rm_layer{layer_index}.png",
        "convert_skin_type": "_{target_type}.png",
        "default": "_converted.png"
    },
    "detect": {
        "detect_skin_type": "_skintype.jsonl",
        "detect_region_pixels": "_{region}_{layer}_has_pixels.jsonl",
        "detect_region_transparency": "_{region}_{layer}_has_transparency.jsonl",
        "detect_region_all": "_{region}_{layer}_properties.jsonl",
        "default": "_detected.jsonl"
    }
}

REGION_NAMES = {
    "head": "h",
    "body": "b",
    "right_arm": "ra",
    "left_arm": "la", 
    "right_leg": "rl",
    "left_leg": "ll"
}