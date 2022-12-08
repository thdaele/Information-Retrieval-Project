import pathlib
import random
import math
import matplotlib.pyplot as plt

import constants
import utils
import recommender

TEST_DECKS_IDS = list()
for deck in constants.TEST_DECKS.iterdir():
    TEST_DECKS_IDS.append(str(deck)[-27:-5])


def repeat_experiment(fn, deck_count=5, seed_count=5):
    random.seed(0)
    for deck_id in random.sample(TEST_DECKS_IDS, deck_count):
        deck = utils.import_deck(constants.TEST_DECKS / f'{deck_id}.json')
        for seed in range(seed_count):
            folder = pathlib.Path(f'plots/{fn.__name__}/{deck_id}/seed={seed}')
            if not folder.is_dir():
                folder.mkdir(parents=True)

            fn(folder, deck, seed)


def varying_left_out(folder, deck, seed):
    for leftout in range(5, 51, 5):
        recommender.pr_curve(deck, seed=seed, leave_out_count=leftout)
        plt.savefig(folder / f'{leftout}.png')
        plt.close()


def df_factor(folder, deck, seed):
    for desc, f in zip(['one', 'log', 'identity'], [
        lambda df: 1,
        lambda df: max(math.log(df), 1),
        lambda df: max(df, 1)
    ]):
        recommender.pr_curve(deck, seed=seed, config={
            "calculate_df_factor": f
        })
        plt.savefig(folder / f'{desc}.png')
        plt.close()

if __name__ == '__main__':
    # repeat_experiment(varying_left_out, 1, 1)
    repeat_experiment(df_factor, 5, 5)