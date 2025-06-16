import pygame
import sys
import csv
import time
import argparse
import os
from game.model_scripts.game_replay import TetrisGameReplay
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS

class MoveVisualizer:
    def __init__(self, csv_file_path, seed=None, playback_speed=1.0):
        self.csv_file_path = csv_file_path
        self.seed = seed
        self.playback_speed = playback_speed
        self.moves_data = []
        self.current_move_index = 0
        self.last_move_time = time.time()
        self.paused = False
        
        self.load_moves_from_csv()
        
        if self.seed is None and self.moves_data:
            seed_str = self.moves_data[0].get('seed', 'unknown')
            if isinstance(seed_str, str):
                if seed_str.startswith('[') and seed_str.endswith(']'):
                    self.seed = int(seed_str[1:-1])
                elif seed_str.isdigit():
                    self.seed = int(seed_str)
                else:
                    self.seed = seed_str
            else:
                self.seed = seed_str
        
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        title_with_seed = f"{TITLE} - Replay Seed: {self.seed}"
        pygame.display.set_caption(title_with_seed)
        self.clock = pygame.time.Clock()
        
        self.game = TetrisGameReplay(seed=self.seed)
        
        self.font = pygame.font.SysFont('Arial', 18)
        
        print(f"Loaded {len(self.moves_data)} moves from {csv_file_path}")
        print(f"Game seed: {self.seed}")
        print(f"Playback speed: {self.playback_speed}x")
        print("\nControls:")
        print("  SPACE: Pause/Resume")
        print("  LEFT/RIGHT: Adjust playback speed")
        print("  R: Restart from beginning")
        print("  ESC: Exit")
    
    def load_moves_from_csv(self):
        if not os.path.exists(self.csv_file_path):
            print(f"Error: CSV file {self.csv_file_path} not found")
            return
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                move_data = {
                    'timestamp': row['timestamp'],
                    'game_time': float(row['game_time']),
                    'move_number': int(row['move_number']),
                    'seed': row['seed'],
                    'move_type': row['move_type'],
                    'tetromino_x': int(row['tetromino_x']),
                    'tetromino_y': int(row['tetromino_y']),
                    'tetromino_shape': row['tetromino_shape'],
                    'tetromino_rotation': int(row['tetromino_rotation']),
                    'next_shape': row['next_shape'],
                    'fall_speed': float(row['fall_speed']),
                    'score': int(row['score']),
                    'level': int(row['level']),
                    'lines_cleared': int(row['lines_cleared']),
                    'probabilities': [float(p) for p in row['probabilities'].split(';') if p],
                    'chosen_probability': float(row['chosen_probability'])
                }
                self.moves_data.append(move_data)
    
    def restart_visualization(self):
        self.current_move_index = 0
        self.last_move_time = time.time()
        

        self.game = TetrisGameReplay(seed=self.seed)
        
        print(f"Restarted visualization from beginning")
    
    def process_next_move(self):
        if self.current_move_index >= len(self.moves_data):
            return False
        
        move_data = self.moves_data[self.current_move_index]
        
        from game.constants import Movement
        move_mapping = {
            'MOVE_LEFT': Movement.MOVE_LEFT,
            'MOVE_RIGHT': Movement.MOVE_RIGHT,
            'ROTATE': Movement.ROTATE,
            'SOFT_DROP': Movement.SOFT_DROP,
            'HARD_DROP': Movement.HARD_DROP,
            'NO_MOVE': Movement.NO_MOVE
        }
        
        move_type = move_mapping.get(move_data['move_type'], Movement.NO_MOVE)
        
        ai_move_data = {
            'move': move_type,
            'probabilities': move_data['probabilities'],
            'chosen_probability': move_data['chosen_probability'],
            'chosen_index': int(move_type)
        }
        
        self.game.process_replay_move(ai_move_data)
        
        self.current_move_index += 1
        return True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
                print(f"Playback {'paused' if self.paused else 'resumed'}")
            elif event.key == pygame.K_LEFT:
                self.playback_speed = max(0.1, self.playback_speed - 0.1)
                print(f"Playback speed: {self.playback_speed:.1f}x")
            elif event.key == pygame.K_RIGHT:
                self.playback_speed = min(5.0, self.playback_speed + 0.1)
                print(f"Playback speed: {self.playback_speed:.1f}x")
            elif event.key == pygame.K_r:
                self.restart_visualization()
            elif event.key == pygame.K_ESCAPE:
                return False
        return True
    
    def draw_status(self):
        if not self.moves_data:
            return
        
        current_move = self.moves_data[self.current_move_index - 1] if self.current_move_index > 0 else None
        
        status_y = 10
        status_x = SCREEN_WIDTH - 300
        
        status_info = [
            f"Replay Progress: {self.current_move_index}/{len(self.moves_data)}",
            f"Playback Speed: {self.playback_speed:.1f}x",
            f"Status: {'PAUSED' if self.paused else 'PLAYING'}",
            ""
        ]
        
        if current_move:
            status_info.extend([
                f"Current Move: {current_move['move_type']}",
                f"Move #{current_move['move_number']}",
                f"Game Time: {current_move['game_time']:.2f}s",
                f"Probability: {current_move['chosen_probability']:.3f}"
            ])
        
        status_info.extend([
            "",
            "Controls:",
            "SPACE: Pause/Resume",
            "←→: Speed ±0.1x",
            "R: Restart",
            "ESC: Exit"
        ])
        
        for i, text in enumerate(status_info):
            if text:
                color = (255, 255, 255) if not text.startswith("Controls") else (200, 200, 200)
                text_surface = self.font.render(text, True, color)
                self.screen.blit(text_surface, (status_x, status_y + i * 20))
    
    def run(self):
        running = True
        
        while running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if not self.handle_input(event):
                        running = False
                        break
            
            if not self.paused and self.current_move_index < len(self.moves_data):
                if self.current_move_index == 0:
                    time_delay = 0
                else:
                    current_move_time = self.moves_data[self.current_move_index]['game_time']
                    prev_move_time = self.moves_data[self.current_move_index - 1]['game_time']
                    time_delay = (current_move_time - prev_move_time) / self.playback_speed
                
                if current_time - self.last_move_time >= time_delay:
                    if self.process_next_move():
                        self.last_move_time = current_time
                    else:
                        print("Replay finished!")
                        self.paused = True
            
            if not self.paused:
                self.game.update()
            
            self.screen.fill((0, 0, 0))
            self.game.draw(self.screen)
            self.draw_status()
            pygame.display.flip()
            
            self.clock.tick(FPS)
        
        pygame.quit()

def find_csv_file(seed):
    logs_dir = "logs"
    possible_names = [
        f"ai_moves_seed{seed}.csv",
        f"ai_moves_seed[{seed}].csv"
    ]
    
    for name in possible_names:
        filepath = os.path.join(logs_dir, name)
        if os.path.exists(filepath):
            return filepath
    
    return None

def list_available_logs():
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        print("No logs directory found")
        return []
    
    csv_files = [f for f in os.listdir(logs_dir) if f.endswith('.csv') and 'ai_moves' in f]
    return sorted(csv_files)

def main():
    parser = argparse.ArgumentParser(description='Visualize Tetris AI moves from CSV logs')
    parser.add_argument('--seed', '-s', type=int, help='Seed number to visualize')
    parser.add_argument('--file', '-f', type=str, help='Specific CSV file to visualize')
    parser.add_argument('--speed', type=float, default=1.0, help='Playback speed multiplier (default: 1.0)')
    parser.add_argument('--list', '-l', action='store_true', help='List available log files')
    
    args = parser.parse_args()
    
    if args.list:
        print("Available log files:")
        files = list_available_logs()
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")
        return
    
    csv_file = None
    seed = None
    
    if args.file:
        csv_file = args.file
        if not os.path.exists(csv_file):
            csv_file = os.path.join("logs", args.file)
    elif args.seed:
        csv_file = find_csv_file(args.seed)
        seed = args.seed
        if not csv_file:
            print(f"No CSV file found for seed {args.seed}")
            print("Available files:")
            files = list_available_logs()
            for file in files[:5]:
                print(f"  {file}")
            return
    else:
        files = list_available_logs()
        if not files:
            print("No log files found. Run the game first to generate logs.")
            return
        csv_file = os.path.join("logs", files[0])
        print(f"No file specified. Using latest: {files[0]}")
    
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found")
        return
    
    visualizer = MoveVisualizer(csv_file, seed=seed, playback_speed=args.speed)
    visualizer.run()

if __name__ == "__main__":
    main()
