import game_with_ai as g
import model.input_data as input
from blocks import TETROMINOES_INDEXES

# when testing, two modes should be created, for showing and for headless running

class AIController:
    def __init__(self, model):
        self.model = model
    
    def get_game_data(self, game=g.TetrisGame):
        current_tetromino = game.current_tetromino
        
        x, y = current_tetromino.x, current_tetromino.y
        current_shape_idx = TETROMINOES_INDEXES[current_tetromino.shape]
        next_shape_idx = TETROMINOES_INDEXES[game.next_tetromino.shape]
        
        self.input = input.InputData(x, y, current_shape_idx, game.fall_speed, current_tetromino.rotation, game.next_tetromino)
    
    def get_next_move(self):
        return self.model(self.input)