import re
import json

def sanitize(card):
    return re.sub(r'[\#\$\%\&\'\(\)\*\+\,\.\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]', '', re.sub(r'[\ \/]', '-', card)).lower().strip()

def import_deck(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data['cards'].split(' ')

def float_to_filename_safe(x):
    if int(x) == x:
        return str(int(x))
    else:
        return str(x).replace('.', '_')

# with open('prosper.txt', 'r') as f:
#     card_list = list()
#     for line in f.readlines():
#         card = sanitize(line)
#         card_list.append(card)
#     print(" ".join(card_list))