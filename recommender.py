import math
import requests

def fetch_terms():
    terms = requests.get('http://localhost:8983/solr/decks/terms', params={
        'terms.fl': 'cards',
        'terms.limit': -1,
    }).json()['terms']['cards']

    it = iter(terms)
    return dict(zip(it, it))

TERMS = fetch_terms()


def generate_recommendations(query_cards, k=10):
    r = requests.get('http://localhost:8983/solr/decks/mlt', params={
        'stream.body': query_cards,
        'mlt.interestingTerms': 'details',
        'mlt.mindf': 0,
        'mlt.mintf': 0,
        'mlt.boost': 'true',
        'fl': 'id, cards, score',
        'rows': 10
    })

    data = r.json()
    docs = data['response']['docs']

    query_cards_set = set(query_cards.split(' '))

    new_cards = dict()
    for doc in docs:
        score = doc['score']
        cards_set = set(doc['cards'].split(' '))

        new_cards_set = cards_set - query_cards_set
        for card in new_cards_set:
            if not card in new_cards:
                new_cards[card] = (0, 0)
            
            # perhaps include df weighting here?
            # + correct for the fact that very common cards will appear in many decks and thus get boosted here
            # + if you didn't include a very common card like sol-ring there porbabily is a reason
            # - but maybe we actually want to recommnd sol ring if it is not in your deck?
            df = math.log10(TERMS[card])
            new_cards[card] = (new_cards[card][0] + score / df, new_cards[card][1] + 1)

    result = sorted(new_cards.items(), key=lambda t: t[1], reverse=True)
    return list(t for t in result[:k])


if __name__ == '__main__':
    cards = 'treasure-mage angel-of-the-ruins arcanists-owl burnished-hart cataclysmic-gearhulk etherium-sculptor ethersworn-canonist ethersworn-sphinx foundry-inspector gold-myr jhoiras-familiar kuldotha-forgemaster master-transmuter myr-battlesphere myr-retriever oswald-fiddlebender phyrexian-metamorph raff-capashen-ships-mage shimmer-myr silver-myr thought-monitor trinket-mage trophy-mage dispatch dramatic-reversal thirst-for-meaning fabricate open-the-vaults phyrexian-rebirth thoughtcast claws-of-gix ichor-wellspring mirrorworks nettlecyst razortide-bridge rings-of-brighthearth spine-of-ish-sah swiftfoot-boots travelers-amulet voltaic-key weatherlight mirrodin-besieged island plains'
    recs = generate_recommendations(cards, 10)
    print(*recs, sep="\n")