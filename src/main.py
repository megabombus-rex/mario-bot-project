import pygame
import sys
#from game.game import TetrisGame
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS
from model.model import Model
from model.input_data import InputData
from model.common_genome_data import *
from game.model_scripts.game_with_ai import *

def main(seed, ai_model):
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    
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

if __name__ == "__main__":
    common_rates = CommonRates(0.8, 0.1, 0.4, 0.2, 0.6, 5)
    innovation_db = InnovationDatabase()
    model = Model.generate_network(input_size=6, output_size=6, common_rates=common_rates, innovation_db=innovation_db)
    #input = InputData(10, 20, 25, 30, 40, 50)
    #model(input=input)
    main(1, model)