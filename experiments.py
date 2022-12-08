import pathlib
import random
import math
from collections import Counter
import matplotlib.pyplot as plt

import constants
import utils
import recommender

TEST_DECKS_IDS = list()
for deck in constants.TEST_DECKS.iterdir():
    TEST_DECKS_IDS.append(str(deck)[-27:-5])


def run_experiment(fn, deck_count=5, seed_count=5, root_directory='results'):
    # create experiment folder
    parent_folder = pathlib.Path(f'{root_directory}/{fn.__name__}')
    if not parent_folder.is_dir():
        parent_folder.mkdir(parents=True)

    # hold accumulated average precision
    acc = Counter()

    # go over random decks and random seeds = random test cases
    random.seed(0)
    for deck_id in random.sample(TEST_DECKS_IDS, deck_count):
        deck = utils.import_deck(constants.TEST_DECKS / f'{deck_id}.json')
        for seed in range(seed_count):
            # create folder for test case
            folder = parent_folder / f'{deck_id}/seed={seed}'
            if not folder.is_dir():
                folder.mkdir(parents=True)

            # perform experiment on test case
            acc += Counter(fn(folder, deck, seed))
            
    # write average precision in summary file
    with open(parent_folder / 'summary.txt', 'w') as f:
        for key, value in acc.items():
            f.write(f'{key}\t{value / (deck_count * seed_count)}\n')



def varying_left_out(folder, deck, seed):
    """
    Test how the amount of cards taken out of a deck to form a testcase, influences the final results.
        + test values from 5 to 50
    """
    result = dict()
    for leave_out_count in range(5, 51, 5):
        # generate test case from deck and seed
        query, relevant_cards  = recommender.deck_to_testcase(deck, leave_out_count, seed)

        # generate recommendations from test case query
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000)

        # calculate precision and recall for different k
        P, R = recommender.pr_values(recommendations, relevant_cards)

        # calculate average precision
        result[leave_out_count] = recommender.average_precision(recommendations, relevant_cards)

        # plot precision and recall values
        recommender.pr_curve(P, R)
        plt.savefig(folder / f'{leave_out_count}.png')
        plt.close()

    return result

def df_factor(folder, deck, seed):
    """
    Test how the df factor in the ranking of cards influences the final results.
        + one: don't use df value (always divide score by 1)
        + identity: use df value as is (divide score by df)
        + log: us logarithm of df (divide by log(df))
    """
    result = dict()
    for desc, f in zip(['one', 'log', 'identity'], [
        lambda _: 1,
        lambda df: max(math.log(df), 1),
        lambda df: max(df, 1)
    ]):
        # generate test case from deck and seed
        query, relevant_cards  = recommender.deck_to_testcase(deck, 25, seed)

        # generate recommendations from test case query
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, calculate_df_factor=f)

        # calculate precision and recall for different k
        P, R = recommender.pr_values(recommendations, relevant_cards)

        # calculate average precision
        result[desc] = recommender.average_precision(recommendations, relevant_cards)

        # plot precision and recall values
        recommender.pr_curve(P, R)
        plt.savefig(folder / f'{desc}.png')
        plt.close()

    return result


def discount_factor(folder, deck, seed):
    """
    Test the influence of a discount factor on the final results
        + 1.0, 0.9, 0.8
    """
    result = dict()
    for alpha in [1.0, 0.9, 0.8]:
        # generate test case from deck and seed
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)

        # generate recommendations from test case query
        recommendations = recommender.generate_recommendations(" ".join(query), 1000, discount_factor=alpha)

        # calculate precision and recall for different k
        P, R = recommender.pr_values(recommendations, relevant_cards)

        # calculate average precision
        result[alpha] = recommender.average_precision(recommendations, relevant_cards)

        # plot precision and recall values
        recommender.pr_curve(P, R)
        plt.savefig(folder / f'{utils.float_to_filename_safe(alpha)}.png')
        plt.close()

    return result


if __name__ == '__main__':
    run_experiment(varying_left_out, 10, 5)
    run_experiment(df_factor, 10, 5)
    run_experiment(discount_factor, 10, 5)