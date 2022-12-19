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


def run_experiment(fn, test_decks, seed_count=1, root_directory='results', name=None):
    if name is None:
        name = fn.__name__

    # create experiment folder
    parent_folder = pathlib.Path(f'{root_directory}/{name}')
    if not parent_folder.is_dir():
        parent_folder.mkdir(parents=True)

    
    acc1 = Counter() # hold accumulated average precision 
    acc2 = Counter() # hold accumulated R-precision

    # go over random decks and random seeds = random test cases
    for deck_id in tqdm(test_decks):
        deck = utils.import_deck(constants.TEST_DECKS / f'{deck_id}.json')
        
        for seed in range(seed_count):
            # create folder for test case
            if seed_count > 1:
                folder = parent_folder / f'{deck_id}/seed={seed}'
            else:
                folder = parent_folder / f'{deck_id}'
            
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

            with open(folder / 'summary.txt', 'w') as f:
                for k, v in res.items():
                    v1, v2 = v
                    v1f = "{:5.4f}".format(v1 / seed_count)
                    v2f = "{:5.4f}".format(v2 / seed_count)
                    f.write(f'{k}\t{v1f}\t{v2f}\n')
    

    # write average precision in summary file
    with open(parent_folder / 'summary.txt', 'w') as f:
        for k, v1 in acc1.items():
            v2 = acc2[k]

            v1f = "{:5.4f}".format(v1 / (len(test_decks) * seed_count))
            v2f = "{:5.4f}".format(v2 / (len(test_decks) * seed_count))
            f.write(f'{k}\t{v1f}\t{v2f}\n')

def varying_left_out(deck, seed):
    """
    Test how the amount of cards taken out of a deck to form a testcase, influences the final results.
        + test values from 5 to 50
    """
    results = dict()
    for leave_out_count in range(5, 51, 5):
        query, relevant_cards  = recommender.deck_to_testcase(deck, leave_out_count, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), k=1000, 
            similar_decks_count=10,
            use_deck_score=False,
            discount_factor=1.0,
            calculate_df_factor='no'
        )
        results[leave_out_count] = recommendations, relevant_cards

    return results

def final_results(deck, seed):
    results = dict()
    for leave_out_count in [5, 25, 50]:
        query, relevant_cards  = recommender.deck_to_testcase(deck, leave_out_count, seed)
        recommendations = recommender.generate_recommendations(" ".join(query), 
            similar_decks_count=5,
            use_deck_score=True,
            discount_factor=0.7,
            calculate_df_factor='df'
        )
        results[f'{leave_out_count} tuned'] = recommendations, relevant_cards

        recommendations = recommender.generate_recommendations(" ".join(query), 
            similar_decks_count=25,
            use_deck_score=False,
            discount_factor=1.0,
            calculate_df_factor='no'
        )
        results[f'{leave_out_count} untuned'] = recommendations, relevant_cards


    return results


def create_tune_experiment(parameter_grid):
    def fn(deck, seed):
        results = dict()
        query, relevant_cards = recommender.deck_to_testcase(deck, 25, seed)
        for parameters in parameter_grid:
            recommendations = recommender.generate_recommendations(" ".join(query), k=1000, **parameters)
            results[tuple(parameters.values())] = recommendations, relevant_cards
        return results

    return fn


if __name__ == '__main__':
    similar_decks_count = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': list(range(1, 26)),
        'use_deck_score': [False],
        'discount_factor': [1],
        'calculate_df_factor': ['no']
    }))

    similar_decks_count2 = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': list(range(25, 501, 25)),
        'use_deck_score': [False],
        'discount_factor': [1],
        'calculate_df_factor': ['no']
    }))

    use_deck_score = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': [1000],
        'use_deck_score': [False, True],
        'discount_factor': [1],
        'calculate_df_factor': ['no']
    }))

    discount_factor = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': [1000],
        'use_deck_score': [False,],
        'discount_factor': [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        'calculate_df_factor': ['no']
    }))

    combining_three = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': [3, 4, 5, 6, 10, 1000],
        'discount_factor': [1, 0.9, 0.8, 0.7, 0.6, 0.5],
        'use_deck_score': [False, True],
        'calculate_df_factor': ['no']
    }))

    calculate_df_factor = create_tune_experiment(utils.ParameterGrid({
        'similar_decks_count': [5],
        'discount_factor': [0.7],
        'use_deck_score': [True],
        'calculate_df_factor': ['no', 'idf', 'prob-idf', 'df']
    }))

    random.seed(0)
    tune_decks = set(random.sample(TEST_DECKS_IDS, 500))

    # run_experiment(similar_decks_count, tune_decks, name="similar_decks_count")
    # run_experiment(similar_decks_count2, tune_decks, name="similar_decks_count2")
    # run_experiment(use_deck_score, tune_decks, name="use_deck_score")
    # run_experiment(discount_factor, tune_decks, name="discount_factor")
    # run_experiment(combining_three, tune_decks, name="combining_three")
    # run_experiment(calculate_df_factor, tune_decks, name="calculate_df_factor")

    test_decks = set(random.sample(TEST_DECKS_IDS, 5156)) - tune_decks # because 156 decks overlap
    run_experiment(final_results, test_decks)

    
