import pygame
import time
from game.blocks import get_random_tetromino, TETROMINOES_INDEXES
from game.board import Board
from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_HEIGHT, 
    INITIAL_FALL_SPEED, LEVEL_SPEEDUP, POINTS_PER_LINE,
    SOFT_DROP_POINTS, HARD_DROP_POINTS, DEFAULT_SEED,
    WHITE, BLACK, Movement, NEAT_VIZ_X, NEAT_VIZ_Y, 
    NEAT_VIZ_WIDTH, NEAT_VIZ_HEIGHT
)
from misc.neat_visualizer import NEATVisualizer
import numpy as np

class TetrisGameReplay:
    def __init__(self, seed=DEFAULT_SEED):
        if seed is not None:
            self.seed = seed
            self.rng = np.random.default_rng(seed)
        else:
            self.seed = np.random.default_rng().integers(0, 1000, size=1)
            self.rng = np.random.default_rng(self.seed)
            
        
        self.board = Board()
        
        
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        
        self.current_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        self.next_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        
        self.last_fall_time = time.time()
        self.fall_speed = INITIAL_FALL_SPEED / 1000 
        self.soft_drop = False
        
        self.ghost_y_offset = self.calculate_drop_position()
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.large_font = pygame.font.SysFont('Arial', 36)
        
    def handle_input(self, key):
        pass
            
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
        if lines_cleared > 0:
            self.score += POINTS_PER_LINE[lines_cleared] * self.level
            self.lines_cleared += lines_cleared
            
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed *= LEVEL_SPEEDUP
                
        fall_time = self.fall_speed
        if self.soft_drop:
            fall_time *= 0.1
            
        if current_time - self.last_fall_time > fall_time:
            if not self.move_tetromino(0, 1):
                self.lock_tetromino()
            
            if self.soft_drop:
                self.score += SOFT_DROP_POINTS
                
            self.last_fall_time = current_time
            
    def process_replay_move(self, move_data):
        move = move_data['move']
        
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
            pass
            
        if move != Movement.SOFT_DROP:
            self.soft_drop = False
            
    def draw(self, screen):
        self.board.draw(screen)
        
        self.board.draw_ghost(screen, self.current_tetromino, self.ghost_y_offset)
        
        self.board.draw_tetromino(screen, self.current_tetromino)
        
        self.draw_next_tetromino(screen)
        
        self.draw_stats(screen)
        
        if self.game_over:
            self.draw_game_over(screen)
        elif self.paused:
            self.draw_paused(screen)
            
    def draw_next_tetromino(self, screen):
        preview_x = 550
        preview_y = 100
        preview_width = 120
        preview_height = 120
        
        pygame.draw.rect(screen, WHITE, (preview_x, preview_y, preview_width, preview_height), 2)
        
        label = self.font.render("Next:", True, WHITE)
        screen.blit(label, (preview_x, preview_y - 30))
        
        for x, y in self.next_tetromino.blocks:
            block_x = preview_x + (preview_width // 2) + x * 20
            block_y = preview_y + (preview_height // 2) + y * 20
            pygame.draw.rect(screen, self.next_tetromino.color, (block_x, block_y, 20, 20))
            pygame.draw.rect(screen, BLACK, (block_x, block_y, 20, 20), 1)
            
    def draw_stats(self, screen):
        stats_x = 850
        stats_y = 50
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (stats_x, stats_y))
        
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (stats_x, stats_y + 30))
        
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (stats_x, stats_y + 60))
        
        replay_text = self.font.render(f"Mode: REPLAY", True, WHITE)
        screen.blit(replay_text, (stats_x, stats_y + 90))
        
        controls_y = 400
        controls = [
            "Replay Mode:",
            "SPACE: Pause/Resume",
            "← →: Speed Control",
            "R: Restart Replay",
            "ESC: Exit"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = self.font.render(text, True, WHITE)
            screen.blit(ctrl_text, (stats_x, controls_y + i * 25))
            
    def draw_game_over(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.large_font.render("REPLAY FINISHED", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(game_over_text, text_rect)
        
        restart_text = self.font.render("Press R to restart replay", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(restart_text, restart_rect)
        
    def draw_paused(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        paused_text = self.large_font.render("PAUSED", True, WHITE)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(paused_text, text_rect)
