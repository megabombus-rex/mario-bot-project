#import game.model_scripts.game_with_ai as g
import model.input_data as input
from game.constants import (GRID_WIDTH, GRID_HEIGHT, EMPIRICAL_MAX_SPEED, ALMOST_COMPLETE_LINES_BLOCK_COUNT)
from game.blocks import (TETROMINOES_INDEXES, TETROMINOES)
from game.constants import Movement
from misc.probability_functions import *
from game.pooling_algorithms import *
import numpy as np
# when testing, two modes should be created, for showing and for headless running

class AIController:
    def __init__(self, model, move_selection_probability_function:ProbabilityFunction):
        self.model = model
        self.probability_function = move_selection_probability_function
        self.input = input.InputDataExtended(0.0, 0.0, 0.0, 0.0, 0.0, [], 0.0, [], [], [])
    
    # this must be normalized!!
    def get_game_data(self, game):
        current_tetromino = game.current_tetromino
        
        x, y = current_tetromino.x / float(GRID_WIDTH), current_tetromino.y / float(GRID_HEIGHT)
        current_shape_idx = TETROMINOES_INDEXES[current_tetromino.shape] / float(len(TETROMINOES_INDEXES))
        #next_shape_idx = TETROMINOES_INDEXES[game.next_tetromino.shape] / float(len(TETROMINOES_INDEXES))
        rotation = current_tetromino.rotation / 3.0 # 0 - 3 values 
        game_speed = game.fall_speed / float(EMPIRICAL_MAX_SPEED)
        column_heights = game.board.get_column_heights()
        column_heights_normalized = [column / float(GRID_HEIGHT) for column in column_heights]
        drop_distance = game.current_drop_distance / float(GRID_HEIGHT)
        almost_complete_lines = [x * 0.7 for x in game.board.get_almost_complete_lines(ALMOST_COMPLETE_LINES_BLOCK_COUNT)] # 'normalize' to not overwhelm the network with 20 neurons
        board_state_flattened = [x * 0.1 for x in game.board.get_board_state_flattened()] # 'normalize' to not overwhelm the network with 200 neurons
        differences = [(column_heights[i] - column_heights[i - 1] / float(GRID_HEIGHT)) for i in range(1, len(column_heights))]
            
        
        
        #print(''.join(str(almost_complete_lines)))
        
        # value / area_size 
        #self.input = input.InputData(x, y, current_shape_idx, game.fall_speed, current_tetromino.rotation, next_block_type=next_shape_idx)
        self.input = input.InputDataExtended(x_block=x, y_block=y, 
                                             block_type=current_shape_idx, 
                                             block_fall_speed=game_speed, 
                                             block_rotation=rotation, 
                                             columns_normalized=column_heights_normalized, 
                                             drop_distance=drop_distance, 
                                             almost_complete_lines=almost_complete_lines,
                                             board_state=board_state_flattened,
                                             height_differences_normalized=differences
                                             )
    
    def get_next_move(self):
        outputs = self.model(self.input)
        probabilities = self.probability_function(outputs)
        chosen_index = self.model.genome.rng.choice(range(len(probabilities)), replace=False, p=probabilities)
        chosen_probability = probabilities[chosen_index] if chosen_index < len(probabilities) else 0.0
        #print('probabilities:' + '-'.join(map(str, probabilities)))
        #print(f'Chosen index: {chosen_index}')
        #print(f"Raw network outputs: {outputs}")
        #print(f"Probabilities: {probabilities}")
        #print(f"Probabilities by action: LEFT:{probabilities[0]:.3f}, RIGHT:{probabilities[1]:.3f}, ROTATE:{probabilities[2]:.3f}, NO_MOVE:{probabilities[3]:.3f}, HARD_DROP:{probabilities[4]:.3f}")
        return {
            'move': Movement(chosen_index),
            'probabilities': probabilities,
            'chosen_probability': chosen_probability,
            'chosen_index': chosen_index
        }