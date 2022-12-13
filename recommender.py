import numpy as np
import requests
import random
from collections import defaultdict
import matplotlib.pyplot as plt

import utils
import constants


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


def generate_recommendations(deck_string, k=10, similar_decks_count=10, use_deck_score=False, discount_factor=1.0, calculate_df_factor=None):
    """
    Generate k card recommendations for a (partial) commander deck.
    """

    if calculate_df_factor is None:
        calculate_df_factor = lambda _: 1

    r = requests.get('http://localhost:8983/solr/decks/mlt', params={
        'stream.body': deck_string,
        'mlt.interestingTerms': 'details',
        'mlt.mindf': 0,
        'mlt.mintf': 0,
        'mlt.boost': 'true',
        'fl': 'id, cards, score',
        'rows': similar_decks_count
    })

    decks = r.json()['response']['docs']
    query_cards_set = set(deck_string.split(' '))

    cards_score = defaultdict(lambda: 0)
    discount = 1.0
    for deck in decks:
        deck_score = deck['score']
        deck_cards = set(deck['cards'].split(' '))

        cards = deck_cards - query_cards_set
        for card in cards:
            term_freq = Terms.get_terms()[card]

            card_score = deck_score if use_deck_score else 1
            
            cards_score[card] += discount * card_score * calculate_df_factor(term_freq)

        discount *= discount_factor

    result = sorted(cards_score.items(), key=lambda t: t[1], reverse=True)
    return list(t[0] for t in result[:k])


def deck_to_testcase(deck, leave_out_count=25, seed=None):
    """
    Convert a test deck into a test case by removing <leave_out_count> random cards from the deck.
    Return the modified deck and the taken out cards.
    The taken out cards act as a set of relevant cards for calculating recall.
    """
    if seed is not None:
        random.seed(seed)
    leave_out_set = set(random.sample(deck, leave_out_count))
    query_set = set(deck) - leave_out_set

    return query_set, leave_out_set


def r_precision(recommendations, relevant_cards):
    """
    Calculate R-precision
    """
    k = len(relevant_cards)
    correct_retrieved = set(recommendations[:k]) & relevant_cards
    return len(correct_retrieved) / k


def average_precision(recommendations, relevant_cards):
    """
    Calculate average precision ~ area under precision-recall curve
    """
    result = 0
    for k, r in enumerate(recommendations):
        if r in relevant_cards:
            correct_retrieved = set(recommendations[:k+1]) & relevant_cards
            result += len(correct_retrieved) / (k+1)

    c = len(set(recommendations) & relevant_cards)

    return result / c if c > 0 else 0


def pr_values(recommendations, relevant_cards):
    """
    Calculate precision@k and recall@k values for a ranked list of recommendation based on a set of relevant cards.
    k values from 1 to the length of the recommendations list will be used.
    """

    P = list()
    R = list()
    for k in range(0, len(recommendations)):
        correct_retrieved = set(recommendations[:k+1]) & relevant_cards
        c = len(correct_retrieved)
        P.append(c / (k+1))
        R.append(c / len(relevant_cards))

    return P, R


def pr_curve(P, R):
    """
    Create a precision-recall curve plot.
    """
    # https://stackoverflow.com/questions/39836953/how-to-draw-a-precision-recall-curve-with-interpolation-in-python
    P_interpolated = np.maximum.accumulate(np.array(P)[::-1])[::-1]
    
    _, ax = plt.subplots()
    ax.plot(R, P)
    ax.step(R, P_interpolated, linewidth=1)
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])


def generate_deck(commander, k=1, deck_size=80):
    """
    Fun procedure to generate a full commander deck by starting with a commander and expanding the deck by repeatedly picking from the top k recommendations.
    Deck size lower than 100 to account for manually deciding on basic land counts.
    """
    deck = [commander]
    while len(deck) < deck_size:
        index = random.randrange(k)
        deck.append(generate_recommendations(" ".join(deck), k=k)[index])

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

    deck = utils.import_deck(constants.TEST_DECKS / '_1ucLPMTGWAouSCQuLRyig.json')
    query, relevant_cards = deck_to_testcase(deck, seed=0)
    recommendations = generate_recommendations(" ".join(query), k=1000)

    print(average_precision(recommendations, relevant_cards))
    P, R = pr_values(recommendations, relevant_cards)
    pr_curve(P, R)
    plt.show()
    # plt.savefig('test.png')
    pass

