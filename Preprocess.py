import json
import pathlib
import random
import re
from tqdm import tqdm

import utils
import constants

TRAIN_TEST_SPLIT = 0.99



def main():
    """
    Preprocesses raw json files and split into test and stored sets
    -> preprocess means removing extra information and only keeping deck id and card list
    -> card list is a single string containing sanitized card names (see utils) seperated by spaces
    """
    for file in tqdm(constants.RAW_DECKS.iterdir()):
        processed_json = {}
        with open(file, 'r') as f:
            data = json.load(f)
        processed_json['id'] = data['urlhash']

        processed_decklist = list()
        decklist = data['cards']
        for card in decklist:
            processed_decklist.append(utils.sanitize(card))

        processed_decklist.append(utils.sanitize(data['commanders'][0]))

        if len(processed_decklist) < 50:
            continue

        processed_json['cards'] = ' '.join(processed_decklist)

        if random.random() < TRAIN_TEST_SPLIT:
            processed_file = constants.STORED_DECKS / f'{file.stem}.json'
        else:
            processed_file = constants.TEST_DECKS / f'{file.stem}.json'
        with open(processed_file, 'w') as f:
            json.dump(processed_json, f)


if __name__ == '__main__':
    main()
