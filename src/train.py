import multiprocessing
from model.genome import InnovationDatabase
from model.model import Model
from model.common_genome_data import CommonRates
from game.model_scripts.game_headless import TetrisGameHeadless
from game.model_scripts.ai_controller import AIController
from misc.probability_functions import Softmax

def train_single_instance(seed, max_steps=1000):
    common_rates = CommonRates(0.8, 0.1, 0.4, 0.2, 0.6, 5)
    innovation_db = InnovationDatabase()
    model = Model.generate_network(input_size=6, output_size=6, common_rates=common_rates, innovation_db=innovation_db)

    game = TetrisGameHeadless(seed=seed, ai_model=model)
    
    steps = 0
    while not game.game_over and steps < max_steps:
        game.update()
        steps += 1
    
    game.cleanup()
   
    return {'seed': seed, 'score': game.score, 'lines_cleared': game.lines_cleared, 'steps': steps}

def train_wrapper(args):
    seed, max_steps = args
    return train_single_instance(seed, max_steps)

def main():
    num_workers = multiprocessing.cpu_count() - 1
    max_generations = 1000
    max_steps_per_game = 1000
    
    print(f"Running training with {num_workers} processes")
    print(f"Max {max_generations} generations")
    print(f"Max {max_steps_per_game} steps per game")
    
    seeds = list(range(num_workers))
    args_list = [(seed, max_steps_per_game) for seed in seeds]
    
    for generation in range(max_generations):
        with multiprocessing.Pool(processes=num_workers) as pool:
            results = pool.map(train_wrapper, args_list)
        
        best_score = max(results, key=lambda x: x['score'])
        avg_score = sum(r['score'] for r in results) / len(results)
        
        print(f"Generation {generation}: Avg={avg_score:.1f}, Best={best_score['score']} (seed={best_score['seed']})")

if __name__ == "__main__":
    main()
