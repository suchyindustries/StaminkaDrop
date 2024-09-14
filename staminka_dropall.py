import sys
import json
import cv2
import numpy as np
import pyautogui
import time
import random
from rich import print
from rich.console import Console
from rich.table import Table
from region_utils import load_config, find_occupied_regions
import random

def check_inventory_open(screen, indicator_image, threshold=0.95):
    screen_height, screen_width, _ = screen.shape
    roi = screen[:, int(screen_width * 0.8):]
    result = cv2.matchTemplate(roi, indicator_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= threshold

def ensure_inventory_open(indicator_image, config, max_attempts=3):
    for attempt in range(max_attempts):
        screen = np.array(pyautogui.screenshot())
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        if check_inventory_open(screen, indicator_image, config['threshold']):
            print("Inventory is open.")
            return True
        print(f"Attempt {attempt + 1}: Inventory not open, pressing key.")
        pyautogui.press(config['inventory_key'])
        time.sleep(0.5)
    print("Failed to open inventory after max attempts.")
    return False

def search_ga_in_occupied_regions(occupied_regions, ga_image):
    full_screen = np.array(pyautogui.screenshot())
    full_screen_gray = cv2.cvtColor(full_screen, cv2.COLOR_BGR2GRAY)
    ga_image_gray = cv2.cvtColor(ga_image, cv2.COLOR_BGRA2GRAY)
    ga_found = []

    for region in occupied_regions:
        x1, y1, x2, y2 = region['x1'], max(0, region['y1'] - 20), region['x2'], region['y2']
        region_image = full_screen_gray[y1:y2, x1:x2]
        res_ga = cv2.matchTemplate(region_image, ga_image_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val_ga, _, _ = cv2.minMaxLoc(res_ga)
        if max_val_ga > 0.51:
            ga_found.append(region['name'])

    return ga_found

def main(action):
    start_time = time.time()
    config = load_config()
    indicator_image = cv2.imread('inv.png', cv2.IMREAD_COLOR)

    if not ensure_inventory_open(indicator_image, config):
        return

    with open('regions_full.json', 'r') as f_full:
        regions_full = json.load(f_full)

    ga_image = cv2.imread('ga.png', cv2.IMREAD_UNCHANGED)
    if ga_image is None:
        print("Error: Could not load ga.png. Check the file path.")
        return

    dark_threshold = config.get('threshold', 0.85)
    occupied_regions = find_occupied_regions(regions_full, dark_threshold)
    occupied_region_names = [region['name'] for region in occupied_regions]

    ga_found = search_ga_in_occupied_regions(occupied_regions, ga_image)
    occupied_with_ga = [name for name in occupied_region_names if name in ga_found]
    occupied_without_ga = [name for name in occupied_region_names if name not in ga_found]
    empty_regions = [region['name'] for region in regions_full if region['name'] not in occupied_region_names]

    identy_time = time.time()
    console = Console()
    table = Table(title="Inventory Analysis")
    table.add_column("Slots", style="cyan", no_wrap=True)
    table.add_column("Quantity", justify="right", style="green")
    table.add_column("Regions", style="magenta")

    table.add_row("Occupied", str(len(occupied_regions)), ", ".join(occupied_region_names))
    table.add_row("Empty", str(len(empty_regions)), ", ".join(empty_regions))
    table.add_row("Occupied with GA", str(len(occupied_with_ga)), ", ".join(occupied_with_ga))
    table.add_row("Occupied w/o GA", str(len(occupied_without_ga)), ", ".join(occupied_without_ga))
    table.add_row("Time to Identify Slots", f"{(identy_time - start_time):.3f} seconds", "")

    console.print(table)

    actions = {
        "dropall": lambda r: True,
        "dropallexceptga": lambda r: r['name'] not in ga_found,
        "dropgaonly": lambda r: r['name'] in ga_found
    }

    if action not in actions:
        print("Invalid action. Please choose from: dropall, dropallexceptga, dropgaonly")
        return



    pyautogui.keyDown('ctrl')
    for region in filter(actions[action], occupied_regions):
        x1, y1, x2, y2 = region['x1'], region['y1'], region['x2'], region['y2']
        click_x = random.randint(x1, x2)
        click_y = random.randint(y1, y2)
        pyautogui.click(click_x, click_y)
        pyautogui.PAUSE = random.uniform(0.1, 0.15)  # Set a random pause
    pyautogui.keyUp('ctrl')


    end_time = time.time()
    print(f"[cyan]Total time: [green]{end_time - start_time:.2f} seconds[/green][/cyan]")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        action = sys.argv[1]
        main(action)
    else:
        print("Please provide an action: dropall, dropallexceptga, dropgaonly")
