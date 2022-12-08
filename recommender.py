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


def generate_recommendations(query_cards, k=10, ignore_id=None, discount_factor=1.0):
    query_cards_set = set(query_cards.split(' '))

    r = requests.get('http://localhost:8983/solr/decks/mlt', params={
        'stream.body': query_cards,
        'mlt.interestingTerms': 'details',
        'mlt.mindf': 0,
        'mlt.mintf': 0,
        'mlt.boost': 'true',
        'fl': 'id, cards, score',
        'rows': int(10000 / len(query_cards_set))
    })

    data = r.json()
    docs = data['response']['docs']

    

    new_cards = dict()
    cum_discount = 1
    for doc in docs:
        if doc['id'] == ignore_id:
            continue
        score = doc['score']
        cards_set = set(doc['cards'].split(' '))
        # print(doc['id'], score)

        new_cards_set = cards_set - query_cards_set
        for card in new_cards_set:
            if not card in new_cards:
                new_cards[card] = (0, 0)
            
            # include df weighting here?
            # + correct for the fact that very common cards will appear in many decks and thus get boosted here
            # + if you didn't include a very common card like sol-ring there porbabily is a reason
            # - but maybe we actually want to recommnd sol ring if it is not in your deck
            df = 1 #math.log(TERMS[card])
            new_cards[card] = (new_cards[card][0] + cum_discount * score / df, new_cards[card][1] + 1)
        
        cum_discount *= discount_factor

    result = sorted(new_cards.items(), key=lambda t: t[1], reverse=True)
    return list(t for t in result[:k])


def evaluate_file(filename, leave_out_count=20, k=5, runs=1):
    with open(filename, 'r') as f:
        data = json.load(f)
        deck_id = data['id']
        cards = data['cards'].split(' ')
        cards_set = set(cards)

        c = 0
        for _ in range(runs):
            leave_out = set(random.sample(cards, leave_out_count))
            query = cards_set - leave_out

            recs = generate_recommendations(' '.join(query), k=k, ignore_id=deck_id, discount_factor=1)
            recs = set(t[0] for t in recs)

            correct_retrieved = recs & leave_out
            # print(*correct_retrieved)

            c += len(correct_retrieved)
        
        P = c / (runs * k)
        R = c / (runs * leave_out_count)

        return P, R


def evaluate(directory, k):
    P = 0
    R = 0
    count = 0
    for f in directory.iterdir():
        p, r = evaluate_file(f, k=k)
        P += p
        R += r
        count += 1

    return P / count, R / count


def generate_deck(commander):
    cards = [commander]
    while len(cards) < 80:
        cards.append(generate_recommendations(" ".join(cards), k=1)[0][0])

    return cards




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

    # for k in [1, 2, 3, 5, 10, 15, 20, 25, 50]:
    #     print(k, *evaluate(pathlib.Path('test_decks'), k))

    deck = generate_deck('prosper-tome-bound')
    print(*deck, sep="\n")
    # deck = 'prosper-tome-bound sol-ring mountain swamp arcane-signet command-tower rakdos-signet mind-stone rakdos-charm terminate bedevil etali-primal-storm hurl-through-hell wild-magic-sorcerer ignite-the-future light-up-the-stage gonti-lord-of-luxury dire-fleet-daredevil theater-of-horrors vandalblast talisman-of-indulgence chaos-warp fellwar-stone commune-with-lava you-find-some-prisoners foreboding-ruins smoldering-marsh tainted-peak bojuka-bog exotic-orchard fevered-suspicion grim-hireling shadowblood-ridge commanders-sphere marionette-master reckless-endeavor mortuary-mire rakdos-carnarium spinerock-knoll tectonic-giant chaos-wand throes-of-chaos dead-mans-chest bituminous-blast consuming-vapors fiend-of-the-shadows dream-pillager share-the-spoils chaos-channeler izzet-chemister apex-of-power disrupt-decorum hex shiny-impetus lorcan-warlock-collector underdark-rift karazikar-the-eye-tyrant dark-dweller-oracle pontiff-of-blight hellish-rebuke danse-macabre unstable-obelisk zhalfirin-void bucknards-everfull-purse ebony-fly death-tyrant bag-of-devouring loyal-apprentice orazca-relic warlock-class phthisis fiendlash piper-of-the-swarm ogre-slumlord chittering-witch revel-in-riches xorn jeskas-will kalain-reclusive-painter valki-god-of-lies'
    # recs = [t[0] for t in generate_recommendations(deck, 20)]
    # print(*recs, sep="\n")

    # recs = generate_recommendations('prosper-tome-bound')
    # print(*recs, sep="\n")

    
