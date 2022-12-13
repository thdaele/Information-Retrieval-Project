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

# with open('mono-red-troublemaker.txt', 'r') as f:
#     card_list = list()
#     for line in f.readlines():
#         card = sanitize(line)
#         card_list.append(card)
#     print(" ".join(card_list))


# deck1 = 'squee-goblin-nabob atsushi-the-blazing-sky containment-construct circuit-mender skyscanner burnished-hart purphoros-god-of-the-forge witty-roastmaster wily-goblin filigree-familiar dualcaster-mage wurmcoil-engine delina-wild-mage myr-battlesphere goblin-engineer priest-of-urabrask fanatic-of-mogis humble-defector impulsive-pilferer emrakuls-hatcher iron-myr generator-servant imperial-recruiter riveteers-requisitioner phyrexian-triniform goblin-welder solemn-simulacrum triplicate-titan myr-retriever junk-diver workshop-assistant chaos-warp red-elemental-blast battle-hymn pyroblast valakut-awakening seething-song blasphemous-act faithless-looting thrill-of-possibility vandalblast jeskas-will seize-the-spotlight infernal-plunge trash-for-treasure sol-ring arcane-signet lightning-greaves sundial-of-the-infinite thousand-year-elixir idol-of-oblivion panharmonicon skullclamp bag-of-holding conjurers-closet ruby-medallion elixir-of-immortality thornbite-staff wayfarers-bauble impact-tremors determined-iteration fable-of-the-mirror-breaker daretti-scrap-savant goblin-bombardment war-room sokenzan-crucible-of-defiance nykthos-shrine-to-nyx buried-ruin inventors-fair castle-embereth valakut-the-molten-pinnacle reliquary-tower spinerock-knoll high-market great-furnace dwarven-mine flamekin-village cavern-of-souls snow-covered-mountain jaxis-the-troublemaker'
# deck2 = 'anger arcane-signet atsushi-the-blazing-sky avacyns-judgment birgi-god-of-storytelling blasphemous-act buried-ruin castle-embereth chain-reaction chaos-warp circuit-mender combat-celebrant containment-construct delina-wild-mage desert-of-the-fervent desperate-ritual determined-iteration dolmen-gate dualcaster-mage duplicant dwarven-mine elixir-of-immortality fable-of-the-mirror-breaker faithless-looting feldon-of-the-third-path fiery-temper goblin-bombardment goblin-engineer great-furnace hanweir-battlements hazorets-monument high-market idol-of-oblivion illusionists-bracers impact-tremors imperial-recruiter impulsive-pilferer iron-myr jaxis-the-troublemaker kher-keep kiki-jiki-mirror-breaker lightning-greaves meteor-golem molten-primordial mountain -mountain myr-battlesphere myr-retriever myriad-landscape outpost-siege ox-of-agonas panharmonicon patron-of-the-arts priest-of-urabrask professional-face-breaker purphoros-god-of-the-forge pyretic-ritual ramunap-ruins red-dragon reverberate revolutionist rogues-passage ruby-medallion scavenger-grounds seething-song siege-gang-commander skullclamp sokenzan-crucible-of-defiance sol-ring solemn-simulacrum spinerock-knoll squee-goblin-nabob thornbite-staff thousand-year-elixir thundermare twinflame valakut-the-molten-pinnacle vandalblast war-room warstorm-surge zealous-conscripts'

# d1 = set(deck1.split(' '))
# d2 = set(deck2.split(' '))

# print(len(d2 & d1), '/', len(d2))