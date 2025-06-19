#import game.model_scripts.game_with_ai as g
import model.input_data as input
from game.constants import (GRID_WIDTH, GRID_HEIGHT, EMPIRICAL_MAX_SPEED)
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
        self.input = input.InputDataNew(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    # this must be normalized!!
    def get_game_data(self, game):
        current_tetromino = game.current_tetromino
        
        x, y = current_tetromino.x / float(GRID_WIDTH), current_tetromino.y / float(GRID_HEIGHT)
        current_shape_idx = TETROMINOES_INDEXES[current_tetromino.shape] / float(len(TETROMINOES_INDEXES))
        #next_shape_idx = TETROMINOES_INDEXES[game.next_tetromino.shape] / float(len(TETROMINOES_INDEXES))
        rotation = current_tetromino.rotation / 4.0
        game_speed = game.fall_speed / float(EMPIRICAL_MAX_SPEED)
        area_values = []
        for i in range(game.board.area_count):
            #print(f'Checking area: {i}')
            area_value = game.board.get_area_pooled(i, MaxPoolingAlgorithm()) / float(game.board.get_area_size(i))
            area_values.append(area_value)
        
        # value / area_size 
        #self.input = input.InputData(x, y, current_shape_idx, game.fall_speed, current_tetromino.rotation, next_block_type=next_shape_idx)
        self.input = input.InputDataNew(x, y, current_shape_idx, game.fall_speed, rotation, 
                                        area_1=area_values[0], area_2=area_values[1], area_3=area_values[2], area_4=area_values[3],
                                        area_5=area_values[4], area_6=area_values[5], area_7=area_values[6], area_8=area_values[7])
        #print(f"""
        #    InputDataNew initialized with:
        #    x: {x}
        #    y: {y}
        #    current_shape_idx: {current_shape_idx}
        #    fall_speed: {game.fall_speed}
        #    rotation: {rotation}
        #    area_1: {area_values[0]}
        #    area_2: {area_values[1]}
        #    area_3: {area_values[2]}
        #    area_4: {area_values[3]}
        #    area_5: {area_values[4]}
        #    area_6: {area_values[5]}
        #    area_7: {area_values[6]}
        #    area_8: {area_values[7]}
        #    """)
    
    def get_next_move(self):
        outputs = self.model(self.input)
        probabilities = self.probability_function(outputs)
        chosen_index = self.model.genome.rng.choice(range(len(probabilities)), replace=False, p=probabilities)
        chosen_probability = probabilities[chosen_index] if chosen_index < len(probabilities) else 0.0
        #print('probabilities:' + '-'.join(map(str, probabilities)))
        #print(f'Chosen index: {chosen_index}')
        
        return {
            'move': Movement(chosen_index),
            'probabilities': probabilities,
            'chosen_probability': chosen_probability,
            'chosen_index': chosen_index
        }