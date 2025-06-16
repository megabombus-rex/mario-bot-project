import time
from game.blocks import get_random_tetromino, TETROMINOES_INDEXES
from game.board import Board
from game.model_scripts.ai_controller import AIController
from game.constants import (
    GRID_HEIGHT, INITIAL_FALL_SPEED, LEVEL_SPEEDUP, POINTS_PER_LINE,
    SOFT_DROP_POINTS, HARD_DROP_POINTS, DEFAULT_SEED, Movement
)
from model.model import *
from misc.probability_functions import *
from misc.csv_logger import CSVLogger
import numpy as np

class TetrisGameHeadless:
    def __init__(self, seed=DEFAULT_SEED, ai_model=None):
        if seed is not None:
            self.seed = seed
            self.rng = np.random.default_rng(seed)
        else:
            self.seed = np.random.default_rng().integers(0, 1000, size=1)[0]
            self.rng = np.random.default_rng(self.seed)
            
        self.board = Board()
        
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        
        self.ai_controller = AIController(model=ai_model, move_selection_probability_function=Softmax())
        
        self.csv_logger = CSVLogger(seed=self.seed)
        
        self.current_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        self.next_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        
        self.last_fall_time = time.time()
        self.fall_speed = INITIAL_FALL_SPEED / 1000  # Convert to seconds
        self.soft_drop = False
        
        self.ghost_y_offset = self.calculate_drop_position()
        
    def move_tetromino(self, dx, dy):
        new_positions = self.current_tetromino.move(dx, dy)
        
        if self.board.is_valid_position(new_positions):
            self.current_tetromino.apply_move(dx, dy)
            
            self.ghost_y_offset = self.calculate_drop_position()
            return True
        return False
        
    def rotate_tetromino(self, clockwise=True):
        original_blocks = self.current_tetromino.blocks.copy()
        original_rotation = self.current_tetromino.rotation
        
        new_positions = self.current_tetromino.rotate(clockwise)
        
        if self.board.is_valid_position(new_positions):
            self.ghost_y_offset = self.calculate_drop_position()
            return True
        
        self.current_tetromino.blocks = original_blocks
        self.current_tetromino.rotation = original_rotation
        return False
        
    def hard_drop(self):
        drop_distance = 0
        
        while self.move_tetromino(0, 1):
            drop_distance += 1
            
        self.score += drop_distance * HARD_DROP_POINTS
        
        self.lock_tetromino()
        
    def calculate_drop_position(self):
        drop_distance = 0
        while True:
            new_positions = self.current_tetromino.move(0, drop_distance + 1)
            if not self.board.is_valid_position(new_positions):
                break
            drop_distance += 1
        return drop_distance
        
    def lock_tetromino(self):
        if not self.board.add_tetromino(self.current_tetromino):
            self.game_over = True
            return
            
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        
        self.soft_drop = False
        
        self.ghost_y_offset = self.calculate_drop_position()
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        current_time = time.time()
        
        lines_cleared = self.board.update_clear_animation()
        self.ai_controller.get_game_data(self)
        if lines_cleared > 0:
            self.score += POINTS_PER_LINE[lines_cleared] * self.level
            self.lines_cleared += lines_cleared
            
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed *= LEVEL_SPEEDUP
                
        ai_move_data = self.ai_controller.get_next_move()
        if ai_move_data:
            self.process_ai_move(ai_move_data)
                
        fall_time = self.fall_speed
        if self.soft_drop:
            fall_time *= 0.1
            
        if current_time - self.last_fall_time > fall_time:
            if not self.move_tetromino(0, 1):
                self.lock_tetromino()
            
            if self.soft_drop:
                self.score += SOFT_DROP_POINTS
                
            self.last_fall_time = current_time
            
    def process_ai_move(self, move_data):
        move = move_data['move']
        probabilities = move_data['probabilities']
        chosen_probability = move_data['chosen_probability']
        
        current_tetromino = self.current_tetromino
        next_tetromino = self.next_tetromino
        
        move_names = {
            Movement.MOVE_LEFT: "MOVE_LEFT",
            Movement.MOVE_RIGHT: "MOVE_RIGHT", 
            Movement.ROTATE: "ROTATE",
            Movement.SOFT_DROP: "SOFT_DROP",
            Movement.HARD_DROP: "HARD_DROP",
            Movement.NO_MOVE: "NO_MOVE"
        }
        
        log_data = {
            'move_type': move_names.get(move, "UNKNOWN"),
            'tetromino_x': current_tetromino.x,
            'tetromino_y': current_tetromino.y,
            'tetromino_shape': current_tetromino.shape,
            'tetromino_rotation': current_tetromino.rotation,
            'next_shape': next_tetromino.shape,
            'fall_speed': self.fall_speed,
            'score': self.score,
            'level': self.level,
            'lines_cleared': self.lines_cleared,
            'probabilities': probabilities,
            'chosen_probability': chosen_probability
        }
        self.csv_logger.log_move(log_data)
        
        if move == Movement.MOVE_LEFT:
            self.move_tetromino(-1, 0)
        elif move == Movement.MOVE_RIGHT:
            self.move_tetromino(1, 0)
        elif move == Movement.ROTATE:
            self.rotate_tetromino()
        elif move == Movement.SOFT_DROP:
            self.soft_drop = True
        elif move == Movement.HARD_DROP:
            self.hard_drop()
        elif move == Movement.NO_MOVE:
            return
        if move != Movement.SOFT_DROP:
            self.soft_drop = False
            
    def cleanup(self):
        if self.csv_logger:
            self.csv_logger.close()
            
    def __del__(self):
        self.cleanup()
