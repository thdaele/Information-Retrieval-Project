import numpy as np
import requests
import random
from collections import defaultdict
import matplotlib.pyplot as plt


# Class to fetch term document frequency
class Terms:
    terms = None
    @staticmethod
    def get_terms():
        if Terms.terms is None:
            terms = requests.get('http://localhost:8983/solr/decks/terms', params={
                'terms.fl': 'cards',
                'terms.limit': -1,
            }).json()['terms']['cards']
            it = iter(terms)
            Terms.terms = dict(zip(it, it))
        return Terms.terms


def generate_recommendations(query_cards, k=10, config=None):
    similar_decks = config['similar_decks'] if 'similar_decks' in config else 100
    discount_factor = config['discount_factor'] if 'discount_factor' in config else 1.0
    calculate_df_factor = config['calculate_df_factor'] if 'calculate_df_factor' in config else lambda _: 1

    r = requests.get('http://localhost:8983/solr/decks/mlt', params={
        'stream.body': query_cards,
        'mlt.interestingTerms': 'details',
        'mlt.mindf': 0,
        'mlt.mintf': 0,
        'mlt.boost': 'true',
        'fl': 'id, cards, score',
        'rows': similar_decks
    })

    data = r.json()['response']['docs']
    query_cards_set = set(query_cards.split(' '))

    new_cards_score = defaultdict(lambda: 0)
    cum_discount = 1
    for doc in data:
        score = doc['score']
        cards_set = set(doc['cards'].split(' '))
        # print(doc['id'], score)

        new_cards_set = cards_set - query_cards_set
        for card in new_cards_set:
            new_cards_score[card] += cum_discount * score / calculate_df_factor(Terms.get_terms()[card])
        
        cum_discount *= discount_factor

    result = sorted(new_cards_score.items(), key=lambda t: t[1], reverse=True)
    return list(t[0] for t in result[:k])


def pr_values(cards, leave_out_count=20, max_k=1000, seed=None, config=None):
    cards_set = set(cards)

    if seed is not None:
        random.seed(seed)
    leave_out = set(random.sample(cards, leave_out_count))
    query_set = cards_set - leave_out
    query = ' '.join(query_set)

    recs = generate_recommendations(query, k=max_k, config=config)

    P = list()
    R = list()
    for k in range(1, max_k + 1):
        correct_retrieved = set(recs[:k]) & leave_out
        c = len(correct_retrieved)
        P.append(c / k)
        R.append(c / leave_out_count)

    return P, R


def pr_curve(cards, leave_out_count=25, max_k=1000, seed=None, config=None):
    P, R = pr_values(cards, leave_out_count, max_k, seed, config)

    P_interpolated = np.maximum.accumulate(np.array(P)[::-1])[::-1]
    
    _, ax = plt.subplots()
    ax.plot(R, P)
    ax.step(R, P_interpolated, linewidth=1)
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    


# def evaluate(directory, leave_out_count=20, seed=None):
#     max_k = 1000
#     test_count = 1
#     k_range = range(1, max_k + 1)

#     C = defaultdict(lambda: 0)
#     for i, f in tqdm(enumerate(directory.iterdir())):
#         if i >= test_count:
#             break

#         with open(f, 'r') as f:
#             data = json.load(f)
#             cards = data['cards'].split(' ')
#             cards_set = set(cards)

#             if seed is not None:
#                 random.seed(seed)

#             leave_out = set(random.sample(cards, leave_out_count))
#             query_set = cards_set - leave_out
#             query = ' '.join(query_set)
#             similar_decks = 100

#             recs = generate_recommendations(query, k=max_k, similar_decks=similar_decks)

#             for k in k_range:
#                 correct_retrieved = set(recs[:k]) & leave_out

#                 C[k] += len(correct_retrieved)
    
#     P = dict()
#     R = dict()
#     for k in k_range:
#         P[k] = C[k] / (test_count * k)
#         R[k] = C[k] / (test_count * leave_out_count)

#     return P, R


def generate_deck(commander):
    deck = [commander]
    while len(deck) < 80:
        deck.append(generate_recommendations(" ".join(deck), k=1)[0][0])

    return deck


if __name__ == '__main__':
    # cards = 'treasure-mage angel-of-the-ruins arcanists-owl burnished-hart cataclysmic-gearhulk etherium-sculptor ethersworn-canonist ethersworn-sphinx foundry-inspector gold-myr jhoiras-familiar kuldotha-forgemaster master-transmuter myr-battlesphere myr-retriever oswald-fiddlebender phyrexian-metamorph raff-capashen-ships-mage shimmer-myr silver-myr thought-monitor trinket-mage trophy-mage dispatch dramatic-reversal thirst-for-meaning fabricate open-the-vaults phyrexian-rebirth thoughtcast claws-of-gix ichor-wellspring mirrorworks nettlecyst razortide-bridge rings-of-brighthearth spine-of-ish-sah swiftfoot-boots travelers-amulet voltaic-key weatherlight mirrodin-besieged island plains'
    
    # Kamiz, Obscura Oculus precon
    # cards = 'kamiz-obscura-oculus aerial-extortionist alela-artful-provocateur an-offer-you-cant-refuse arcane-sanctum arcane-signet archon-of-coronation ash-barrens austere-command azorius-signet cephalid-facetaker champion-of-wits change-of-plans chasm-skulker choked-estuary command-tower commanders-sphere commit-memory creeping-tar-pit currency-converter custodi-lich daring-saboteur darkwater-catacombs daxos-of-meletis dimir-signet dragonlord-ojutai drana-liberator-of-malakir dusk-dawn esper-panorama exotic-orchard fallen-shinobi fellwar-stone fetid-heath ghostly-pilferer graveblade-marauder identity-thief in-too-deep inkfathom-witch island jailbreak lethal-scheme life-insurance looter-il-kor mask-of-riddles mask-of-the-schemer misfortune-teller myriad-landscape nadir-kraken nightmare-unmaking obscura-charm obscura-confluence obscura-storefront orzhov-signet oskar-rubbish-reclaimer path-of-ancestry plains port-town prairie-stream profane-command quietus-spike rogues-passage shadowmage-infiltrator silent-blade-oni skycloud-expanse skyway-robber smugglers-share sol-ring stolen-identity strionic-resonator sun-titan sunken-hollow swamp swiftfoot-boots swords-to-plowshares temple-of-silence thief-of-sanity thriving-heath thriving-isle thriving-moor tivit-seller-of-secrets treasure-cruise utter-end wayfarers-bauble whirler-rogue wrexial-the-risen-deep writ-of-return'
    
    # Mizzix of the Izmagnus precon
    # cards = 'mizzix-of-the-izmagnus goblin-electromancer jaces-archivist gigantoplasm talrand-sky-summoner psychosis-crawler broodbirth-viper illusory-ambusher lone-revenant warchief-giant charmbreaker-devils arjun-the-shifting-flame etherium-horn-sorcerer melek-izzet-paragon dragon-mage preordain faithless-looting vandalblast mizzium-mortars windfall mystic-retrieval stolen-goods mizzixs-mastery rite-of-replication sleep chain-reaction call-the-skybreaker blatant-thievery epic-experiment meteor-blast blustersquall brainstorm echoing-truth desperate-ravings urzas-rage counterflux aetherize fact-or-fiction reins-of-power steam-augury mystic-confluence word-of-seizing act-of-aggression prophetic-bolt aethersnatch mirror-match fireminds-foresight repeal comet-storm magmaquake stroke-of-genius dominate blue-suns-zenith sol-ring izzet-signet thought-vessel worn-powerstone seal-of-the-guildpact awaken-the-sky-tyrant rite-of-the-raging-storm thought-reflection command-tower evolving-wilds izzet-boilerworks izzet-guildgate reliquary-tower rogues-passage spinerock-knoll swiftwater-cliffs temple-of-the-false-god terramorphic-expanse vivid-crag vivid-creek island mountain'
    
    # Prosper Tome-Bound precon
    # cards = 'prosper-tome-bound apex-of-power arcane-signet bag-of-devouring bedevil bituminous-blast bojuka-bog bucknards-everfull-purse chaos-channeler chaos-wand chaos-warp chittering-witch command-tower commanders-sphere commune-with-lava consuming-vapors danse-macabre dark-dweller-oracle dead-mans-chest death-tyrant dire-fleet-daredevil disrupt-decorum dream-pillager ebony-fly etali-primal-storm exotic-orchard fellwar-stone fevered-suspicion fiend-of-the-shadows fiendlash foreboding-ruins gonti-lord-of-luxury grim-hireling hellish-rebuke hex hurl-through-hell ignite-the-future izzet-chemister karazikar-the-eye-tyrant light-up-the-stage lorcan-warlock-collector loyal-apprentice marionette-master mind-stone mortuary-mire mountain ogre-slumlord orazca-relic phthisis piper-of-the-swarm pontiff-of-blight rakdos-carnarium rakdos-charm rakdos-signet reckless-endeavor shadowblood-ridge share-the-spoils shiny-impetus smoldering-marsh sol-ring spinerock-knoll swamp tainted-peak talisman-of-indulgence tectonic-giant terminate theater-of-horrors throes-of-chaos underdark-rift unstable-obelisk vandalblast warlock-class wild-magic-sorcerer you-find-some-prisoners zhalfirin-void'
    
    # recs = [t[0] for t in generate_recommendations(cards, 20)]
    # print(*recs, sep="\n")

    # deck = generate_deck('prosper-tome-bound')
    # print(*deck, sep="\n")
    # deck = 'prosper-tome-bound sol-ring mountain swamp arcane-signet command-tower rakdos-signet mind-stone rakdos-charm terminate bedevil etali-primal-storm hurl-through-hell wild-magic-sorcerer ignite-the-future light-up-the-stage gonti-lord-of-luxury dire-fleet-daredevil theater-of-horrors vandalblast talisman-of-indulgence chaos-warp fellwar-stone commune-with-lava you-find-some-prisoners foreboding-ruins smoldering-marsh tainted-peak bojuka-bog exotic-orchard fevered-suspicion grim-hireling shadowblood-ridge commanders-sphere marionette-master reckless-endeavor mortuary-mire rakdos-carnarium spinerock-knoll tectonic-giant chaos-wand throes-of-chaos dead-mans-chest bituminous-blast consuming-vapors fiend-of-the-shadows dream-pillager share-the-spoils chaos-channeler izzet-chemister apex-of-power disrupt-decorum hex shiny-impetus lorcan-warlock-collector underdark-rift karazikar-the-eye-tyrant dark-dweller-oracle pontiff-of-blight hellish-rebuke danse-macabre unstable-obelisk zhalfirin-void bucknards-everfull-purse ebony-fly death-tyrant bag-of-devouring loyal-apprentice orazca-relic warlock-class phthisis fiendlash piper-of-the-swarm ogre-slumlord chittering-witch revel-in-riches xorn jeskas-will kalain-reclusive-painter valki-god-of-lies'
    # recs = [t[0] for t in generate_recommendations(deck, 20)]
    # print(*recs, sep="\n")

    
    # pr_curve(deck, seed=0, leave_out_count=25)
    # plt.savefig('test.png')
    pass

