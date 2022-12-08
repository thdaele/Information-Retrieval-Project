import json
import pathlib
import random
import re
from tqdm import tqdm

DECK_DIR = pathlib.Path('Data') / 'decks'
PROCESSED_DIR = pathlib.Path('Data') / 'processed_decks'
PROCESSED_TEST_DIR = pathlib.Path('Data') / 'processed_test_decks'

TRAIN_TEST_SPLIT = 0.95


def main():
    for file in tqdm(DECK_DIR.iterdir()):
        processed_json = {}
        with open(file, 'r') as f:
            data = json.load(f)
        processed_json['id'] = data['urlhash']

        processed_decklist = list()
        decklist = data['cards']
        for card in decklist:
            processed_decklist.append(sanitize(card))

        processed_decklist.append(sanitize(data['commanders'][0]))

        if len(processed_decklist) < 50:
            continue

        processed_json['cards'] = ' '.join(processed_decklist)

        if random.random() < TRAIN_TEST_SPLIT:
            processed_file = PROCESSED_DIR / (file.stem + '.json')
        else:
            processed_file = PROCESSED_TEST_DIR / (file.stem + '.json')
        with open(processed_file, 'w') as f:
            json.dump(processed_json, f)


def sanitize(card):
    return re.sub(r'[\#\$\%\&\'\(\)\*\+\,\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]', '',
                  re.sub(r'[\ ]', '-', card)).lower().strip()


if __name__ == '__main__':
    main()
