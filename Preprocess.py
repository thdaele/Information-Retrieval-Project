import json
import pathlib
from tqdm import tqdm

DECK_DIR = pathlib.Path('Data') / 'decks'
PROCESSED_DIR = pathlib.Path('Data') / 'processed_decks'


def main():
    for file in tqdm(DECK_DIR.iterdir()):
        processed_json = {}
        with open(file, 'r') as f:
            data = json.load(f)
        processed_json['id'] = data['urlhash']

        processed_decklist = list()
        decklist = data['container']['json_dict']['cardlists']
        for cardlist in decklist:
            cardViews = cardlist['cardviews']
            for cardView in cardViews:
                processed_decklist.append(cardView['sanitized'])
        processed_json['cards'] = ' '.join(processed_decklist)

        with open(PROCESSED_DIR / file.name, 'w') as f:
            json.dump(processed_json, f)


if __name__ == '__main__':
    main()
