import json
import cv2
import numpy as np
import pyautogui
import os

def load_config():
    config_file = 'config.json'
    default_config = {"threshold": 0.85, "inventory_key": "c"}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return default_config

def is_region_empty(region, screen, threshold):
    x1, y1, x2, y2 = region['x1'], region['y1'], region['x2'], region['y2']
    region_image = screen[y1:y2, x1:x2]
    gray_image = cv2.cvtColor(region_image, cv2.COLOR_RGB2GRAY)
    dark_pixels_ratio = np.mean(gray_image < 50)
    return dark_pixels_ratio > threshold

def find_occupied_regions(regions_full, dark_threshold):
    screen = np.array(pyautogui.screenshot())
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

    occupied_regions = []
    for region in regions_full:
        if not is_region_empty(region, screen, dark_threshold):
            occupied_regions.append(region)

    return occupied_regions
