#import game.model_scripts.game_with_ai as g
import model.input_data as input
from game.blocks import TETROMINOES_INDEXES
from game.constants import Movement
from misc.probability_functions import *
import numpy as np
# when testing, two modes should be created, for showing and for headless running

class AIController:
    def __init__(self, model, move_selection_probability_function:ProbabilityFunction):
        self.model = model
        self.probability_function = move_selection_probability_function
        self.input = input.InputData(0, 0, 0, 0, 0, 0)
    
    def get_game_data(self, game):
        current_tetromino = game.current_tetromino
        
        x, y = current_tetromino.x, current_tetromino.y
        current_shape_idx = TETROMINOES_INDEXES[current_tetromino.shape]
        next_shape_idx = TETROMINOES_INDEXES[game.next_tetromino.shape]
        
        self.input = input.InputData(x, y, current_shape_idx, game.fall_speed, current_tetromino.rotation, next_block_type=next_shape_idx)
    
    def get_next_move(self):
        outputs = self.model(self.input)
        probabilities = self.probability_function(outputs)
        chosen_index = self.model.genome.rng.choice(range(len(probabilities)), replace=False, p=probabilities)
        #print('probabilities:' + '-'.join(map(str, probabilities)))
        #print(f'Chosen index: {chosen_index}')
        return Movement(chosen_index)