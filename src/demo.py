import webbrowser

from src import recommender

mono_red_troublemaker = 'anger arcane-signet atsushi-the-blazing-sky avacyns-judgment birgi-god-of-storytelling blasphemous-act buried-ruin castle-embereth chain-reaction chaos-warp circuit-mender combat-celebrant containment-construct delina-wild-mage desert-of-the-fervent desperate-ritual determined-iteration dolmen-gate dualcaster-mage duplicant dwarven-mine elixir-of-immortality fable-of-the-mirror-breaker faithless-looting feldon-of-the-third-path fiery-temper goblin-bombardment goblin-engineer great-furnace hanweir-battlements hazorets-monument high-market idol-of-oblivion illusionists-bracers impact-tremors imperial-recruiter impulsive-pilferer iron-myr jaxis-the-troublemaker kher-keep kiki-jiki-mirror-breaker lightning-greaves meteor-golem molten-primordial mountain -mountain myr-battlesphere myr-retriever myriad-landscape outpost-siege ox-of-agonas panharmonicon patron-of-the-arts priest-of-urabrask professional-face-breaker purphoros-god-of-the-forge pyretic-ritual ramunap-ruins red-dragon reverberate revolutionist rogues-passage ruby-medallion scavenger-grounds seething-song siege-gang-commander skullclamp sokenzan-crucible-of-defiance sol-ring solemn-simulacrum spinerock-knoll squee-goblin-nabob thornbite-staff thousand-year-elixir thundermare twinflame valakut-the-molten-pinnacle vandalblast war-room warstorm-surge zealous-conscripts'

recommendations = recommender.generate_recommendations(
    mono_red_troublemaker,
    7,
    similar_decks_count=5,
    use_deck_score=True,
    discount_factor=0.7,
    calculate_df_factor='df'
)

for recommendation in recommendations:
    webbrowser.open(f"https://edhrec.com/cards/{recommendation}")
