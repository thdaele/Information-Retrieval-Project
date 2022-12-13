import pathlib
import random
import math
from collections import Counter
import matplotlib.pyplot as plt
from tqdm import tqdm

import constants
import utils
import recommender

TEST_DECKS_IDS = list()
for deck in constants.TEST_DECKS.iterdir():
    TEST_DECKS_IDS.append(str(deck)[-27:-5])


def run_experiment(fn, deck_count=10, seed_count=1, root_directory='results'):
    # create experiment folder
    parent_folder = pathlib.Path(f'{root_directory}/{fn.__name__}')
    if not parent_folder.is_dir():
        parent_folder.mkdir(parents=True)

    # hold accumulated average precision
    acc1 = Counter()
    acc2 = Counter()
    big_acc = dict()

    # go over random decks and random seeds = random test cases
    random.seed(0)
    for deck_id in tqdm(random.sample(TEST_DECKS_IDS, deck_count)):
        deck = utils.import_deck(constants.TEST_DECKS / f'{deck_id}.json')

        if seed_count > 1:
            for seed in range(seed_count):
                # create folder for test case
                folder = parent_folder / f'{deck_id}/seed={seed}'
                if not folder.is_dir():
                    folder.mkdir(parents=True)

                # perform experiment on test case
                results = fn(deck, seed)

                res = dict()
                for key, value in results.items():
                    recommendations, relevant_cards = value

                    # calculate precision and recall for different k
                    P, R = recommender.pr_values(recommendations, relevant_cards)

                    # calculate metrics
                    m1 = recommender.average_precision(recommendations, relevant_cards)
                    m2 = recommender.r_precision(recommendations, relevant_cards)
                    acc1[key] += m1
                    acc2[key] += m2

                    res[key] = m1, m2

                    # plot precision and recall values
                    recommender.pr_curve(P, R)
                    plt.savefig(folder / f'{key}.png')
                    plt.close()
                big_acc[f'{deck_id} {seed}'] = res
        else:
            folder = parent_folder / deck_id
            if not folder.is_dir():
                folder.mkdir(parents=True)

            # perform experiment on test case
            results = fn(deck, 0)

            res = dict()
            for key, value in results.items():
                recommendations, relevant_cards = value

                # calculate precision and recall for different k
                P, R = recommender.pr_values(recommendations, relevant_cards)

                # calculate metrics
                m1 = recommender.average_precision(recommendations, relevant_cards)
                m2 = recommender.r_precision(recommendations, relevant_cards)
                acc1[key] += m1
                acc2[key] += m2

                res[key] = m1, m2

                # plot precision and recall values
                recommender.pr_curve(P, R)
                plt.savefig(folder / f'{key}.png')
                plt.close()
            big_acc[f'{deck_id}'] = res

            
    # write average precision in summary file
    with open(parent_folder / 'summary.txt', 'w') as f:
        for k, v1 in acc1.items():
            v2 = acc2[k]

            v1f = "{:5.4f}".format(v1 / (deck_count * seed_count))
            v2f = "{:5.4f}".format(v2 / (deck_count * seed_count))
            f.write(f'{k}\t{v1f}\t{v2f}\n')
        f.write('\n')
        
        for k, vacc in big_acc.items():
            r = ''
            for _, v in vacc.items():
                v1, v2 = v
                
                v1f = "{:5.4f}".format(v1)
                v2f = "{:5.4f}".format(v2)

                r += f'{v1f} {v2f} | '
            f.write(f'{k}\t{r}\n')


def varying_left_out(folder, deck, seed):
    """
    Test how the amount of cards taken out of a deck to form a testcase, influences the final results.
        + test values from 5 to 50
    """
    results = dict()
    for leave_out_count in range(5, 51, 5):
        query, relevant_cards  = recommender.deck_to_testcase(deck, leave_out_count, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000)
        results[leave_out_count] = recommendations, relevant_cards

    return results

def use_deck_score(deck, seed):
    """
    Test weighting the term occuring by the decks's similarity score
    """
    results = dict()
    for value in [True, False]:
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, use_deck_score=value)
        results[value] = recommendations, relevant_cards

    return results

def similar_decks_count(deck, seed):
    """
    Test weighting the term occuring by the decks's similarity score
    """
    results = dict()
    for value in [10, 100, 1000]:
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, similar_decks_count=value)
        results[value] = recommendations, relevant_cards

    return results

def test(deck, seed):
    """
    Test weighting the term occuring by the decks's similarity score
    """
    results = dict()
    for value1 in [3, 4, 5, 6, 7, 10, 15]:
        for value2 in [True, False]:
            for value3 in [1.0]:
                query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
                recommendations = recommender.generate_recommendations(" ".join(query), k=1000, similar_decks_count=value1, use_deck_score=value2, discount_factor=value3)
                results[f'{value1}-{value2}-{value3}'] = recommendations, relevant_cards

    return results

def df_factor(folder, deck, seed):
    """
    Test how the df factor in the ranking of cards influences the final results.
        + one: don't use df value (always divide score by 1)
        + identity: use df value as is (divide score by df)
        + log: us logarithm of df (divide by log(df))
    """
    results = dict()
    for desc, value in zip(['one', 'log', 'identity'], [
        lambda _: 1,
        lambda df: max(math.log(df), 1),
        lambda df: max(df, 1)
    ]):
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, calculate_df_factor=value)
        results[desc] = recommendations, relevant_cards

    return results


def discount_factor(folder, deck, seed):
    """
    Test the influence of a discount factor on the final results
        + 1.0, 0.9, 0.8
    """
    results = dict()
    for value in [1.0, 0.9, 0.8]:
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, discount_factor=value)
        results[value] = recommendations, relevant_cards

    return results


if __name__ == '__main__':
    run_experiment(test, 1000)
    # run_experiment(varying_left_out, 10, 10)
    # run_experiment(df_factor, 100, 5)
    # run_experiment(discount_factor, 100, 5)