import re

def sanitize(card):
    return re.sub(r'[\#\$\%\&\'\(\)\*\+\,\.\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~]', '', re.sub(r'[\ \/]', '-', card)).lower().strip()

with open('obscura.txt', 'r') as f:
    card_list = list()
    for line in f.readlines():
        card = sanitize(line)
        card_list.append(card)
    print(" ".join(card_list))