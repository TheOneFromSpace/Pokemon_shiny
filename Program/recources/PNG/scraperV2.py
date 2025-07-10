import requests
import os
import time
import json
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

# Configuration
CONFIG_FILE = "allgen_progress.json"
REQUEST_DELAY = 1.0  # Conservative delay to prevent bans

# Primary source (Pokémon DB)
POKEDB_BASE = "https://img.pokemondb.net/sprites"
POKEDB_GAMES = {
    'red-blue': {'gen': 1, 'has_shiny': False},
    'yellow': {'gen': 1, 'has_shiny': False},
    'gold': {'gen': 2, 'has_shiny': True},
    'silver': {'gen': 2, 'has_shiny': True},
    'crystal': {'gen': 2, 'has_shiny': True},
    'ruby-sapphire': {'gen': 3, 'has_shiny': True},
    'emerald': {'gen': 3, 'has_shiny': True},
    'firered-leafgreen': {'gen': 3, 'has_shiny': True},
    'diamond-pearl': {'gen': 4, 'has_shiny': True},
    'platinum': {'gen': 4, 'has_shiny': True},
    'heartgold-soulsilver': {'gen': 4, 'has_shiny': True},
    'black-white': {'gen': 5, 'has_shiny': True},
    'black-2-white-2': {'gen': 5, 'has_shiny': True},
    'x-y': {'gen': 6, 'has_shiny': True},
    'omega-ruby-alpha-sapphire': {'gen': 6, 'has_shiny': True},
    'sun-moon': {'gen': 7, 'has_shiny': True},
    'ultra-sun-ultra-moon': {'gen': 7, 'has_shiny': True},
    'sword-shield': {'gen': 8, 'has_shiny': True},
    'brilliant-diamond-shining-pearl': {'gen': 8, 'has_shiny': True},
    'legends-arceus': {'gen': 8, 'has_shiny': True},
    'scarlet-violet': {'gen': 9, 'has_shiny': True}
}

# Fallback source (PokéAPI)
POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon/"
POKEAPI_SPRITES = {
    'official-artwork': 'other/official-artwork/front_default',
    'home': 'other/home/front_default',
    'default': 'front_default'
}


def load_progress():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'downloaded': [], 'pokemon': []}


def save_progress(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)


def get_all_pokemon():
    """Get complete list with generation info"""
    print("Fetching Pokémon db...")
    url = "https://pokemondb.net/pokedex/all"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pokemon = []
    for row in soup.select("table#pokedex tbody tr"):
        name = row.select_one("td:nth-of-type(2) a").text.strip().lower()
        # Get the national dex number from the row
        dex_num_cell = row.select_one("td:nth-of-type(1)")
        dex_num = int(dex_num_cell.text.strip()) if dex_num_cell else 0
        pokemon.append((name, dex_num))

    return pokemon


def download_pokedb_sprite(game, variant, pokemon):
    url = f"{POKEDB_BASE}/{game}/{variant}/{pokemon}.png"
    path = Path("sprites") / "pokedb" / game / variant / f"{pokemon}.png"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return True

        time.sleep(REQUEST_DELAY)
        response = requests.get(url, stream=True, timeout=10)

        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return True
        return False
    except:
        return False


def download_pokeapi_sprite(pokemon, sprite_type):
    try:
        data = requests.get(f"{POKEAPI_BASE}{pokemon}").json()
        parts = POKEAPI_SPRITES[sprite_type].split('/')
        sprite_url = data['sprites']
        for part in parts:
            sprite_url = sprite_url.get(part, {})

        if not sprite_url or not isinstance(sprite_url, str):
            return False

        path = Path("sprites") / "pokeapi" / sprite_type / f"{pokemon}.png"
        path.parent.mkdir(parents=True, exist_ok=True)

        time.sleep(REQUEST_DELAY)
        response = requests.get(sprite_url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return True
        return False
    except:
        return False


def main():
    progress = load_progress()
    if not progress['pokemon']:
        progress['pokemon'] = get_all_pokemon()
        save_progress(progress)

    total = len(progress['pokemon'])
    print(f"Starting download for {total} Pokémon across all generations")

    with tqdm(total=total, unit="pokemon") as pbar:
        for name, dex_num in progress['pokemon']:
            if name in progress['downloaded']:
                pbar.update(1)
                continue

            # Try PokéDB first (game-specific sprites)
            downloaded = False
            for game, data in POKEDB_GAMES.items():
                variants = ['normal'] if not data['has_shiny'] else ['normal', 'shiny']
                for variant in variants:
                    if download_pokedb_sprite(game, variant, name):
                        downloaded = True

            # Fallback to PokéAPI if PokéDB failed
            if not downloaded:
                for sprite_type in POKEAPI_SPRITES:
                    if download_pokeapi_sprite(name, sprite_type):
                        downloaded = True

            if downloaded:
                progress['downloaded'].append(name)
                if len(progress['downloaded']) % 20 == 0:
                    save_progress(progress)

            pbar.update(1)
            pbar.set_postfix_str(name)

    save_progress(progress)
    print("\nDownload complete! Sprites saved in:")
    print("  - sprites/pokedb/[game]/[variant]/")
    print("  - sprites/pokeapi/[sprite_type]/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload interrupted. Progress saved.")
    except Exception as e:
        print(f"Error: {e}")