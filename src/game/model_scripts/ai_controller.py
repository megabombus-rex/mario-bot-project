import game as g
import model.input_data as input
from blocks import TETROMINOES_INDEXES

# when testing, two modes should be created, for showing and for headless running

class AIController:
    def __init__(self, model):
        self.model = model
        pass
    
    def get_game_data(self, game=g.TetrisGame):
        current_tetromino = game.current_tetromino
        
        x, y = current_tetromino.x, current_tetromino.y
        current_shape_idx = TETROMINOES_INDEXES[current_tetromino.shape]
        next_shape_idx = TETROMINOES_INDEXES[game.next_tetromino.shape]
        
        game_data = input.InputData(x, y, current_shape_idx, game.fall_speed, game.next_tetromino)