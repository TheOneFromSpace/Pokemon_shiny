import requests
from bs4 import BeautifulSoup
import os
import re
import time

BASE_URL = "https://pokemondb.net"
SPRITES_URL = f"{BASE_URL}/sprites"

os.makedirs("sprites", exist_ok=True)

res = requests.get(SPRITES_URL)
soup = BeautifulSoup(res.text, "html.parser")

gen_links = []
for link in soup.select("a[href^='/sprites/']"):
    href = link['href']
    if href.startswith("/sprites/"):
        gen_links.append(href)

gen_links = list(set(gen_links))

print(f"Found {len(gen_links)} sprite pages.")

for idx, link in enumerate(gen_links, 1):
    url = BASE_URL + link
    print(f"[Page {idx}/{len(gen_links)}] Scraping: {url}")
    res = requests.get(url)
    s = BeautifulSoup(res.text, "html.parser")

    title = s.select_one("h1").get_text(strip=True)
    safe_title = re.sub(r'[^a-zA-Z0-9_-]+', '_', title)
    out_dir = os.path.join("sprites", safe_title)
    os.makedirs(out_dir, exist_ok=True)

    imgs = s.select(".grid-col img")
    print(f"Found {len(imgs)} sprites on {title}.")

    for img in imgs:
        src = img['src']
        name = os.path.basename(src)
        name = re.sub(r'\?.*$', '', name)
        outpath = os.path.join(out_dir, name)

        if not os.path.exists(outpath):
            img_data = requests.get(src).content
            with open(outpath, "wb") as f:
                f.write(img_data)
            print(f"Saved {outpath}")

    time.sleep(1)

print("All done!")