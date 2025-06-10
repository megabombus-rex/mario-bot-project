import csv
import os
import time
from datetime import datetime
from game.constants import CSV_LOG_ENABLED, CSV_LOG_FILENAME, CSV_LOG_DIRECTORY

class CSVLogger:
    def __init__(self, enabled=CSV_LOG_ENABLED, filename=CSV_LOG_FILENAME, directory=CSV_LOG_DIRECTORY, seed=None):
        self.enabled = enabled
        self.directory = directory
        self.filename = filename
        self.seed = seed
        self.filepath = None
        self.file_handle = None
        self.csv_writer = None
        self.session_start_time = None
        self.move_count = 0
        
        if self.enabled:
            self._setup_logging()
    
    def _setup_logging(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        base_name = os.path.splitext(self.filename)[0]
        
        if self.seed is not None:
            self.filepath = os.path.join(self.directory, f"{base_name}_seed{self.seed}.csv")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filepath = os.path.join(self.directory, f"{base_name}_{timestamp}.csv")
        
        self.file_handle = open(self.filepath, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file_handle)
        
        header = [
            'timestamp',
            'game_time',
            'move_number',
            'seed',
            'move_type',
            'tetromino_x',
            'tetromino_y', 
            'tetromino_shape',
            'tetromino_rotation',
            'next_shape',
            'fall_speed',
            'score',
            'level',
            'lines_cleared',
            'probabilities',
            'chosen_probability'
        ]
        self.csv_writer.writerow(header)
        self.file_handle.flush()
        
        self.session_start_time = time.time()
        print(f"CSV logging enabled. Saving to: {self.filepath}")
    
    def log_move(self, move_data):
        if not self.enabled or not self.csv_writer:
            return
        
        current_time = time.time()
        game_time = current_time - self.session_start_time if self.session_start_time else 0
        self.move_count += 1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        move_type = move_data.get('move_type', 'UNKNOWN')
        tetromino_x = move_data.get('tetromino_x', 0)
        tetromino_y = move_data.get('tetromino_y', 0)
        tetromino_shape = move_data.get('tetromino_shape', 'UNKNOWN')
        tetromino_rotation = move_data.get('tetromino_rotation', 0)
        next_shape = move_data.get('next_shape', 'UNKNOWN')
        fall_speed = move_data.get('fall_speed', 0)
        score = move_data.get('score', 0)
        level = move_data.get('level', 1)
        lines_cleared = move_data.get('lines_cleared', 0)
        probabilities = move_data.get('probabilities', [])
        chosen_probability = move_data.get('chosen_probability', 0.0)
        
        prob_str = ';'.join([f"{p:.4f}" for p in probabilities])
        
        row = [
            timestamp,
            f"{game_time:.3f}",
            self.move_count,
            self.seed if self.seed is not None else 'unknown',
            move_type,
            tetromino_x,
            tetromino_y,
            tetromino_shape,
            tetromino_rotation,
            next_shape,
            f"{fall_speed:.3f}",
            score,
            level,
            lines_cleared,
            prob_str,
            f"{chosen_probability:.4f}"
        ]
        
        self.csv_writer.writerow(row)
        self.file_handle.flush()
    
    def reset(self):
        if not self.enabled:
            return
            
        if self.file_handle:
            self.file_handle.close()
        
        self.move_count = 0
        self.session_start_time = time.time()
        
        self.file_handle = open(self.filepath, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.file_handle)
        
        header = [
            'timestamp',
            'game_time',
            'move_number',
            'seed',
            'move_type',
            'tetromino_x',
            'tetromino_y', 
            'tetromino_shape',
            'tetromino_rotation',
            'next_shape',
            'fall_speed',
            'score',
            'level',
            'lines_cleared',
            'probabilities',
            'chosen_probability'
        ]
        self.csv_writer.writerow(header)
        self.file_handle.flush()
        
        print(f"CSV log reset. Overwriting: {self.filepath}")

    def close(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            if self.enabled:
                print(f"CSV log closed. Total moves logged: {self.move_count}")
    
    def __del__(self):
        self.close()
