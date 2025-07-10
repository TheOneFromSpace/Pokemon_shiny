import requests
import os
import time
import json
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

# Configuration
CONFIG_FILE = "download_progress.json"
BASE_URL = "https://img.pokemondb.net/sprites"
REQUEST_DELAY = 1.5  # Seconds between requests
ERROR_DELAY = 3.0  # Seconds to wait after errors

# Maps generations to their game groups
GENERATIONS = {
    1: {
        'games': ['red-blue', 'yellow'],
        'has_shiny': False  # Gen 1 doesn't have shinies
    },
    2: {
        'games': ['gold', 'silver', 'crystal'],
        'has_shiny': True
    },
    3: {
        'games': ['ruby-sapphire', 'emerald', 'firered-leafgreen'],
        'has_shiny': True
    },
    # ... (rest of generations with 'has_shiny': True)
}


def download_sprite(game, variant, pokemon):
    time.sleep(REQUEST_DELAY)
    url = f"{BASE_URL}/{game}/{variant}/{pokemon}.png"
    path = Path("sprites") / game / variant / f"{pokemon}.png"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return True

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        elif response.status_code == 404:
            return False  # Silent fail for expected 404s
        else:
            print(f"HTTP Error {response.status_code} for {url}")
            time.sleep(ERROR_DELAY)
            return False

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        time.sleep(ERROR_DELAY)
        return False


def main():
    # ... (previous setup code remains the same)

    total = 0
    tasks = []
    for pokemon in pokemon_list:
        pokemon_gen = gen_map.get(pokemon, 1)  # Default to Gen 1 if unknown

        # Only try games from this Pokémon's generation and later
        for gen, gen_data in GENERATIONS.items():
            if gen >= pokemon_gen:
                for game in gen_data['games']:
                    # For Gen 1, only download normal sprites
                    if gen == 1:
                        variant = 'normal'
                        identifier = f"{game}/{variant}/{pokemon}"
                        if identifier not in downloaded:
                            tasks.append((game, variant, pokemon))
                            total += 1
                    # For other gens, try both normal and shiny
                    else:
                        for variant in ['normal', 'shiny']:
                            identifier = f"{game}/{variant}/{pokemon}"
                            if identifier not in downloaded:
                                tasks.append((game, variant, pokemon))
                                total += 1

    # ... (rest of the main function remains the same)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload interrupted. Progress has been saved.")
    except Exception as e:
        print(f"Fatal error: {e}")