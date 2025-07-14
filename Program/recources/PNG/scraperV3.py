import requests
import os
import time
import json
import re
import urllib.parse
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

# Configuration
CONFIG_FILE = "allgen_progress.json"
REQUEST_DELAY = 1.0
MAX_RETRIES = 3

# Sprite sources
SOURCES = {
    'pokedb': {
        'base_url': "https://img.pokemondb.net/sprites",
        'games': {
            'home': {'gen': 9, 'has_shiny': True},
        }
    },
    'pokeapi': {
        'base_url': "https://pokeapi.co/api/v2/pokemon",
        'sprites': {
            'official-artwork': 'other/official-artwork/front_default',
            'home': 'other/home/front_default',
            'dream-world': 'other/dream-world/front_default',
            'default': 'front_default'
        }
    },
    'pkgdex': {
        'base_url': "https://raw.githubusercontent.com/PKMN-Devs/pkgdex/main/sprites"
    }
}


def sanitize_pokemon_name(name):
    """Clean up Pokémon names by removing special chars and fixing spaces"""
    # First handle regional forms
    regional_forms = {
        'alolan': 'alolan',
        'galarian': 'galarian',
        'hisuian': 'hisuian',
        'paldean': 'paldean',
        'mega': 'mega',
        'mega x': 'mega-x',
        'mega y': 'mega-y',
        'gmax': 'gmax'
    }

    # Check for regional forms
    form = None
    for form_name, form_suffix in regional_forms.items():
        if form_name in name.lower():
            form = form_suffix
            name = name.lower().replace(form_name, '').strip()
            break

    # Remove special characters
    name = re.sub(r"[\'\.:]", "", name)
    # Replace spaces with hyphens
    name = name.replace(" ", "-").lower()

    # Add form suffix if exists
    if form:
        name = f"{name}-{form}"

    return name


def load_progress():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'downloaded': [], 'pokemon': []}


def save_progress(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_all_pokemon():
    """Get complete list with generation info"""
    print("Fetching Pokémon db...")
    url = "https://pokemondb.net/pokedex/all"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pokemon = []
    for row in soup.select("table#pokedex tbody tr"):
        name_cell = row.select_one("td:nth-of-type(2)")
        name = name_cell.text.strip()

        # Get the small text which often contains the form
        form_text = name_cell.select_one("small")
        if form_text:
            name = f"{name} {form_text.text.strip()}"

        clean_name = sanitize_pokemon_name(name)
        dex_num_cell = row.select_one("td:nth-of-type(1)")
        dex_num = int(dex_num_cell.text.strip()) if dex_num_cell else 0
        pokemon.append((clean_name, dex_num))

    return pokemon


def download_sprite(source, game, variant, pokemon, retry=0):
    try:
        if source == 'pokedb':
            url = f"{SOURCES['pokedb']['base_url']}/{game}/{variant}/{pokemon}.png"
            path = Path("sprites") / game / variant / f"{pokemon}.png"
        elif source == 'pokeapi':
            # For PokeAPI, we need to handle forms differently
            base_name = pokemon.split('-')[0]  # Remove form suffix for API call
            url = f"{SOURCES['pokeapi']['base_url']}/{base_name}"
            path = Path("sprites") / "pokeapi" / variant / f"{pokemon}.png"
        elif source == 'pkgdex':
            url = f"{SOURCES['pkgdex']['base_url']}/{pokemon}.png"
            path = Path("sprites") / "pkgdex" / f"{pokemon}.png"
        else:
            return False

        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return True

        time.sleep(REQUEST_DELAY)

        if source == 'pokeapi':
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            parts = SOURCES['pokeapi']['sprites'][variant].split('/')
            sprite_url = data['sprites']
            for part in parts:
                sprite_url = sprite_url.get(part, {})
                if sprite_url is None:
                    return False

            if not sprite_url or not isinstance(sprite_url, str):
                return False

            url = sprite_url
            response = requests.get(url, stream=True, timeout=10)
        else:
            response = requests.get(url, stream=True, timeout=10)

        response.raise_for_status()

        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            print(f"✓ Downloaded {pokemon} from {source} ({game}/{variant})")
            return True
        return False
    except requests.exceptions.RequestException as e:
        if retry < MAX_RETRIES:
            time.sleep(2)
            return download_sprite(source, game, variant, pokemon, retry + 1)
        print(f"✗ Failed {pokemon} from {source} ({game}/{variant}): {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error with {pokemon} from {source}: {str(e)}")
        return False


def main():
    progress = load_progress()
    if not progress['pokemon']:
        progress['pokemon'] = get_all_pokemon()
        save_progress(progress)

    total = len(progress['pokemon'])
    print(f"Starting download for {total} Pokémon")

    Path("sprites").mkdir(exist_ok=True)

    with tqdm(total=total, unit="pokemon") as pbar:
        for name, dex_num in progress['pokemon']:
            if name in progress['downloaded']:
                pbar.update(1)
                continue

            downloaded = False

            # Try PokéDB first
            for game, data in SOURCES['pokedb']['games'].items():
                variants = ['normal'] if not data['has_shiny'] else ['normal', 'shiny']
                for variant in variants:
                    if download_sprite('pokedb', game, variant, name):
                        downloaded = True
                        break
                if downloaded:
                    break

            # Try PokéAPI if PokéDB failed
            if not downloaded:
                for variant in SOURCES['pokeapi']['sprites']:
                    if download_sprite('pokeapi', 'pokeapi', variant, name):
                        downloaded = True
                        break

            # Try PKGDex as last resort
            if not downloaded:
                if download_sprite('pkgdex', 'pkgdex', 'default', name):
                    downloaded = True

            if downloaded:
                progress['downloaded'].append(name)
                if len(progress['downloaded']) % 20 == 0:
                    save_progress(progress)

            pbar.update(1)
            pbar.set_postfix_str(name)

    save_progress(progress)
    print("\nDownload complete! Sprites saved in:")
    print("  - sprites/[game]/[variant]/")
    print("  - sprites/pokeapi/[variant]/")
    print("  - sprites/pkgdex/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload interrupted. Progress saved.")
    except Exception as e:
        print(f"Error: {e}")