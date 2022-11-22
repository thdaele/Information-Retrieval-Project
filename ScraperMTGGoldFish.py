import pathlib
import time

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm


def scraper():
    r = requests.get('https://www.mtggoldfish.com/deck/custom/standard#paper')
    soup = BeautifulSoup(r.content, 'html.parser')

    pagination = soup.find('ul', class_='pagination')
    paginationItems = pagination.findChildren('li')
    # The second last item is the last page
    pages = int(paginationItems[-2].text)

    for i in tqdm(range(1, pages + 1, 10), desc="Pages"):
        deckids = list()
        for j in range(10):
            if i + j > pages:
                break
            r = requests.get('https://www.mtggoldfish.com/deck/custom/standard?page=' + str(i + j) + "#paper")
            soup = BeautifulSoup(r.content, 'html.parser')
            s = soup.find('div', class_='deck-display')
            decks = s.find_all('span', class_='deck-price-paper')

            for deck in decks:
                for child in deck.findChildren():
                    deckid = child.get('href')
                    if deckid is not None:
                        deckid = deckid.split('/')[-1]
                        deckid = deckid.split('#')[0]
                        deckids.append(deckid)

        file = open(f'Data/deckids/deckids-{i}-{i+9}.txt', 'w')
        for deckid in deckids:
            file.write(deckid + '\n')
        file.close()


def downloader():
    last_page = 1

    while True:
        startTime = time.time()
        if not pathlib.Path(f'Data/deckids/deckids-{last_page}-{last_page+9}.txt').exists():
            break
        file = open(f'Data/deckids/deckids-{last_page}-{last_page+9}.txt', 'r')
        deckids = file.read().splitlines()
        file.close()
        for deckid in deckids:
            r = requests.get('https://www.mtggoldfish.com/deck/download/' + str(deckid))

            if r.status_code == 200:
                file = open(f'Data/decks/{deckid}.txt', 'wb')
                file.write(r.content)
                file.close()
            else:
                print(r.status_code)

        last_page += 10
        print(f'Time for page {last_page}-{last_page+9}: {time.time() - startTime}')


if __name__ == '__main__':
    # scraper()
    downloader()
