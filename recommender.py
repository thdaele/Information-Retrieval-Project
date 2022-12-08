import math
import requests
import json
import random
import pathlib

def fetch_terms():
    terms = requests.get('http://localhost:8983/solr/decks/terms', params={
        'terms.fl': 'cards',
        'terms.limit': -1,
    }).json()['terms']['cards']

    it = iter(terms)
    return dict(zip(it, it))

TERMS = fetch_terms()


def generate_recommendations(query_cards, k=10, ignore_id=None):
    r = requests.get('http://localhost:8983/solr/decks/mlt', params={
        'stream.body': query_cards,
        'mlt.interestingTerms': 'details',
        'mlt.mindf': 0,
        'mlt.mintf': 0,
        'mlt.boost': 'true',
        'fl': 'id, cards, score',
        'rows': 20
    })

    data = r.json()
    docs = data['response']['docs']

    query_cards_set = set(query_cards.split(' '))

    new_cards = dict()
    for doc in docs:
        if doc['id'] == ignore_id:
            continue
        score = doc['score']
        cards_set = set(doc['cards'].split(' '))

        new_cards_set = cards_set - query_cards_set
        for card in new_cards_set:
            if not card in new_cards:
                new_cards[card] = (0, 0)
            
            # include df weighting here?
            # + correct for the fact that very common cards will appear in many decks and thus get boosted here
            # + if you didn't include a very common card like sol-ring there porbabily is a reason
            # - but maybe we actually want to recommnd sol ring if it is not in your deck
            df = math.log(TERMS[card])
            new_cards[card] = (new_cards[card][0] + score / df, new_cards[card][1] + 1)

    result = sorted(new_cards.items(), key=lambda t: t[1], reverse=True)
    return list(t for t in result[:k])


def evaluate(filename, leave_out_count=20, k=5, runs=100):
    with open(filename, 'r') as f:
        data = json.load(f)
        deck_id = data['id']
        cards = data['cards'].split(' ')
        cards_set = set(cards)

        c = 0
        for _ in range(runs):
            leave_out = set(random.sample(cards, leave_out_count))
            query = cards_set - leave_out

            recs = generate_recommendations(' '.join(query), k, deck_id)
            # recs = generate_recommendations(' '.join(query), k)
            recs = set(t[0] for t in recs)

            correct_retrieved = recs & leave_out
            # print(*correct_retrieved)

            c += len(correct_retrieved)
        P = c / (runs * k)
        R = c / (runs * leave_out_count)

        # print(deck_id, c/runs, P, R)

        return P, R


if __name__ == '__main__':
    # cards = 'treasure-mage angel-of-the-ruins arcanists-owl burnished-hart cataclysmic-gearhulk etherium-sculptor ethersworn-canonist ethersworn-sphinx foundry-inspector gold-myr jhoiras-familiar kuldotha-forgemaster master-transmuter myr-battlesphere myr-retriever oswald-fiddlebender phyrexian-metamorph raff-capashen-ships-mage shimmer-myr silver-myr thought-monitor trinket-mage trophy-mage dispatch dramatic-reversal thirst-for-meaning fabricate open-the-vaults phyrexian-rebirth thoughtcast claws-of-gix ichor-wellspring mirrorworks nettlecyst razortide-bridge rings-of-brighthearth spine-of-ish-sah swiftfoot-boots travelers-amulet voltaic-key weatherlight mirrodin-besieged island plains'
    # cards = 'aerial-extortionist alela-artful-provocateur an-offer-you-cant-refuse arcane-sanctum arcane-signet archon-of-coronation ash-barrens austere-command azorius-signet cephalid-facetaker champion-of-wits change-of-plans chasm-skulker choked-estuary command-tower commanders-sphere commit-memory creeping-tar-pit currency-converter custodi-lich daring-saboteur darkwater-catacombs daxos-of-meletis dimir-signet dragonlord-ojutai drana-liberator-of-malakir dusk-dawn esper-panorama exotic-orchard fallen-shinobi fellwar-stone fetid-heath ghostly-pilferer graveblade-marauder identity-thief in-too-deep inkfathom-witch island jailbreak kamiz-obscura-oculus lethal-scheme life-insurance looter-il-kor mask-of-riddles mask-of-the-schemer misfortune-teller myriad-landscape nadir-kraken nightmare-unmaking obscura-charm obscura-confluence obscura-storefront orzhov-signet oskar-rubbish-reclaimer path-of-ancestry plains port-town prairie-stream profane-command quietus-spike rogues-passage shadowmage-infiltrator silent-blade-oni skycloud-expanse skyway-robber smugglers-share sol-ring stolen-identity strionic-resonator sun-titan sunken-hollow swamp swiftfoot-boots swords-to-plowshares temple-of-silence thief-of-sanity thriving-heath thriving-isle thriving-moor tivit-seller-of-secrets treasure-cruise utter-end wayfarers-bauble whirler-rogue wrexial-the-risen-deep writ-of-return'
    # recs = generate_recommendations(cards, 10)
    # print(*recs, sep="\n")

    P = 0
    R = 0
    count = 0
    for f in pathlib.Path('test_decks').iterdir():
        p, r = evaluate(f)
        P += p
        R += r
        count += 1

    P = P / count
    R = R / count

    print(P, R)
