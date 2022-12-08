import re
import json

def sanitize(card):
    return re.sub(r'[\#\$\%\&\'\(\)\*\+\,\.\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]', '', re.sub(r'[\ \/]', '-', card)).lower().strip()

def import_deck(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data['cards'].split(' ')

# with open('prosper.txt', 'r') as f:
#     card_list = list()
#     for line in f.readlines():
#         card = sanitize(line)
#         card_list.append(card)
#     print(" ".join(card_list))