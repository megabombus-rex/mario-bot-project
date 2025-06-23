import pygame
import sys
#from game.game import TetrisGame
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, DEFAULT_SEED, DEFAULT_SEED_MODEL
from model.model import Model
from model.input_data import InputData
from model.common_genome_data import *
from game.model_scripts.game_with_ai import *
from simulation.test_sim import *
from visualize_moves import *

def main(seed, ai_model):
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    title_with_seed = f"{TITLE} - Seed: {seed}"
    pygame.display.set_caption(title_with_seed)
    
    # Create a clock for controlling the frame rate
    clock = pygame.time.Clock()
    
    # Create a game instance
    #game = TetrisGame()
    game = TetrisGameWithAI(seed=seed, ai_model=ai_model)
    
    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                game.handle_input(event.key)
        
        # Update game state
        game.update()
        
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the game
        game.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)

def experiment(common_rates:CommonRates):
    exp = Experiment(iteration_count=201, population_size=200, tournament_size=10, elite_size_percent=0.1, enable_pruning=False, prune_percent=0.1, stagnation_mean_percent=0.1, common_rates=common_rates)
    exp()
    

if __name__ == "__main__":
    common_rates = CommonRates(crossover_rate=0.7, weight_mutation_rate=0.4, activation_mutation_rate=0.1, 
                               connection_addition_mutation_rate=0.3, node_addition_mutation_rate=0.05, connection_change_mutation_rate=0.1, 
                               start_connection_probability=0.6, max_start_connection_count=5)
    #innovation_db = InnovationDatabase(11) # (input size + output size -1) is the beginning node count
    #main(DEFAULT_SEED, model)
    experiment(common_rates)
    #visualizer = MoveVisualizer('logs/ai_moves_seed[42].csv', 42, playback_speed=1)
    #visualizer.run()