import sys
import time
from game.constants import DEFAULT_SEED, DEFAULT_SEED_MODEL
from model.model import Model
from model.common_genome_data import *
from game.model_scripts.game_with_ai import TetrisGameWithAI

def headless_main(seed, ai_model, max_games=1, max_steps_per_game=10000):
    print(f"Starting headless mode with seed {seed}")
    print(f"Max games: {max_games}, Max steps per game: {max_steps_per_game}")
    
    for game_num in range(max_games):
        print(f"\n=== Game {game_num + 1}/{max_games} ===")
        
        game = TetrisGameWithAI(seed=seed, ai_model=ai_model)
        
        steps = 0
        start_time = time.time()
        
        while not game.game_over and steps < max_steps_per_game:
            game.update()
            steps += 1
            
            if steps % 1000 == 0:
                print(f"  Step {steps}, Score: {game.score}, Lines: {game.lines_cleared}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Game {game_num + 1} finished:")
        print(f"  Final Score: {game.score}")
        print(f"  Lines Cleared: {game.lines_cleared}")
        print(f"  Level: {game.level}")
        print(f"  Steps: {steps}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Game Over: {game.game_over}")
        
        if game.game_over:
            print(f"  Reason: Game Over")
        else:
            print(f"  Reason: Max steps reached")
        
        if hasattr(game, 'csv_logger'):
            game.csv_logger.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Tetris AI in headless mode')
    parser.add_argument('--seed', type=int, default=DEFAULT_SEED, help='Game seed')
    parser.add_argument('--games', type=int, default=1, help='Number of games to run')
    parser.add_argument('--steps', type=int, default=10000, help='Max steps per game')
    parser.add_argument('--model-seed', type=int, default=DEFAULT_SEED_MODEL, help='Model seed')
    
    args = parser.parse_args()
    
    common_rates = CommonRates(0.8, 0.1, 0.4, 0.2, 0.6, 5)
    innovation_db = InnovationDatabase()
    model = Model.generate_network(
        input_size=6, 
        output_size=6, 
        common_rates=common_rates, 
        innovation_db=innovation_db, 
        seed=args.model_seed
    )
    
    headless_main(args.seed, model, args.games, args.steps)
