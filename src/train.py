import multiprocessing
from model.genome import InnovationDatabase
from model.model import Model
from model.common_genome_data import CommonRates
from game.model_scripts.game_with_ai import TetrisGameWithAI
from game.model_scripts.ai_controller import AIController
from misc.probability_functions import Softmax

def train_single_instance(seed):
    common_rates = CommonRates(0.8, 0.1, 0.4, 0.2, 0.6, 5)
    innovation_db = InnovationDatabase()
    model = Model.generate_network(input_size=6, output_size=6, common_rates=common_rates, innovation_db=innovation_db)

    game = TetrisGameWithAI(seed=seed, ai_model=model)
    
    max_steps = 10000
    steps = 0
    while not game.game_over and steps < max_steps:
        game.update()
        steps += 1
   
    return {'seed': seed, 'score': game.score, 'lines_cleared': game.lines_cleared}

def main():
    num_workers = multiprocessing.cpu_count() - 1
    seeds = list(range(num_workers))
    for generation in range(10):
        with multiprocessing.Pool(processes=num_workers) as pool:
            results = pool.map(train_single_instance, seeds)
        print(f"Generation {generation}: {results}")

if __name__ == "__main__":
    main()
