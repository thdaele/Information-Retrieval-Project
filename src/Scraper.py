import grequests
import requests
import json
import pathlib
from tqdm import tqdm

import utils

DATA_PATH = pathlib.Path('Data')
BATCH_SIZE = 100


def scraper(overwrite=False):
    deckhashes = DATA_PATH / 'deckhash.txt'
    if deckhashes.exists() and not overwrite:
        return

    r = requests.get('https://json.edhrec.com/static/typeahead/commanders')
    commanders = json.loads(r.content)

    file = open(deckhashes, 'w')
    for commander in tqdm(commanders):
        r = requests.get(f'https://json.edhrec.com/pages/decks/{utils.sanitize(commander)}.json')
        if r.status_code == 200:
            decks = json.loads(r.content)['table']
            for deck in decks:
                file.write(deck['urlhash'] + '\n')
        else:
            print(f'Error: {commander} - {utils.sanitize(commander)}')
            print(f'Error: {r.status_code}')
            print(r.content)
    file.close()


def downloader():
    deck_dir = DATA_PATH / 'decks'
    deckhashes = DATA_PATH / 'deckhash.txt'

    if not deck_dir.exists() or not deckhashes.exists():
        print(f'Error: Missing {deckhashes} or {deck_dir} directory')
        return

    with open(deckhashes, 'r') as file:
        deckhashes = file.read().splitlines()
    amount_of_decks = len(deckhashes)
    for index in tqdm(range(0, amount_of_decks, BATCH_SIZE)):
        batch = set()
        for offset in range(0, BATCH_SIZE):
            if index + offset >= amount_of_decks:
                continue
            batch.add(grequests.get(f'https://json.edhrec.com/pages/deckpreview-temp/{deckhashes[index + offset]}.json'))

        for resp in grequests.imap(batch):
            filename = resp.url.split('/')[-1]
            if resp.status_code == 200:
                with open(deck_dir / filename, 'wb') as file:
                    file.write(resp.content)
            else:
                print(f'File: {filename}')
                print(f'Error: {resp.status_code}')
                print(resp.content)


if __name__ == '__main__':
    # scraper()
    downloader()
