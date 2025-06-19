import pygame
import time
from game.blocks import get_random_tetromino, TETROMINOES_INDEXES
from game.board import Board
from game.model_scripts.ai_controller import AIController
from game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_HEIGHT, 
    INITIAL_FALL_SPEED, LEVEL_SPEEDUP, POINTS_PER_LINE,
    SOFT_DROP_POINTS, HARD_DROP_POINTS, DEFAULT_SEED,
    WHITE, BLACK, Movement, NEAT_VIZ_X, NEAT_VIZ_Y, 
    NEAT_VIZ_WIDTH, NEAT_VIZ_HEIGHT
)
from model.model import *
from misc.probability_functions import *
from misc.neat_visualizer import NEATVisualizer
from misc.csv_logger import CSVLogger
import misc.visualizers
import numpy as np

class TetrisGameWithAI:
    def __init__(self, seed=DEFAULT_SEED, ai_model=None):
        """
        Initialize the Tetris game.
        
        Args:
            seed (int, optional): Random seed for tetromino generation
            ai_model (callable, optional): AI model for automated play
        """
        # Set the random seed if provided
        if seed is not None:
            self.seed = seed
            self.rng = np.random.default_rng(seed)
        else:
            self.seed = np.random.default_rng().integers(0, 1000, size=1)
            self.rng = np.random.default_rng(self.seed)
            
        # Create the game board
        self.board = Board()
        
        # Game state
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        
        # test
        self.hard_drop_count = 0
        self.move_count = 0
        
        # AI controller
        self.ai_controller = AIController(model=ai_model, move_selection_probability_function=Softmax())
        
        # NEAT visualizer
        self.neat_visualizer = NEATVisualizer(NEAT_VIZ_X, NEAT_VIZ_Y, NEAT_VIZ_WIDTH, NEAT_VIZ_HEIGHT)
        
        # CSV Logger for AI moves
        #self.csv_logger = CSVLogger(seed=self.seed)
        
        # Create the first tetromino
        self.current_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        self.next_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        
        # Initialize timing
        self.last_fall_time = time.time()
        self.fall_speed = INITIAL_FALL_SPEED / 1000  # Convert to seconds
        self.soft_drop = False
        
        # Set up a ghost piece (shows where the piece will land)
        self.ghost_y_offset = self.calculate_drop_position()
        
        # Load font for text rendering
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.large_font = pygame.font.SysFont('Arial', 36)
        
    def handle_input(self, key):
        """
        Handle keyboard input.
        
        Args:
            key (int): Pygame key constant
        """
        if self.game_over:
            if key == pygame.K_r:
                #self.csv_logger.reset()
                
                # for the time being, here we can mutate the model
                if self.ai_controller.model.genome.rng.random() < self.ai_controller.model.genome.common_rates.node_addition_mutation_rate:
                    self.ai_controller.model.genome.mutation_add_node() # test
                    self.ai_controller.model.phenotype = Model.topological_sort(self.ai_controller.model.genome.nodes, self.ai_controller.model.genome.connections)
                    print('Node added to the genome')
                    
                if self.ai_controller.model.genome.rng.random() < self.ai_controller.model.genome.common_rates.connection_addition_mutation_rate:
                    self.ai_controller.model.genome.mutation_add_connection() # test
                    self.ai_controller.model.phenotype = Model.topological_sort(self.ai_controller.model.genome.nodes, self.ai_controller.model.genome.connections)
                    print('Connection added to the genome')
                
                self.ai_controller.model = Model(genome=self.ai_controller.model.genome, previous_network_fitness=self.score)
                misc.visualizers.visualize_phenotype(self.ai_controller.model.genome, title="Phenotype Visualization")
                self.__init__(self.seed, self.ai_controller.model)  # Reset the game
            return
            
        if key == pygame.K_p:
            self.paused = not self.paused
            return
            
        if self.paused:
            return
            
    def move_tetromino(self, dx, dy):
        """
        Move the current tetromino.
        
        Args:
            dx (int): Change in x position
            dy (int): Change in y position
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        new_positions = self.current_tetromino.move(dx, dy)
        
        if self.board.is_valid_position(new_positions):
            self.current_tetromino.apply_move(dx, dy)
            
            # Update ghost piece position
            self.ghost_y_offset = self.calculate_drop_position()
            return True
        return False
        
    def rotate_tetromino(self, clockwise=True):
        """
        Rotate the current tetromino.
        
        Args:
            clockwise (bool): True for clockwise, False for counter-clockwise
            
        Returns:
            bool: True if rotation was successful, False otherwise
        """
        # Save current blocks to restore if rotation fails
        original_blocks = self.current_tetromino.blocks.copy()
        original_rotation = self.current_tetromino.rotation
        
        # Try to rotate
        new_positions = self.current_tetromino.rotate(clockwise)
        
        # Check if rotation is valid
        if self.board.is_valid_position(new_positions):
            # Update ghost piece position
            self.ghost_y_offset = self.calculate_drop_position()
            return True
        
        # If rotation fails, restore original state
        self.current_tetromino.blocks = original_blocks
        self.current_tetromino.rotation = original_rotation
        return False
        
    def hard_drop(self):
        """Immediately drop the tetromino to the bottom."""
        drop_distance = self.get_drop_distance()
            
        # Add points for hard drop
        self.score += drop_distance * HARD_DROP_POINTS
        
        # Lock the tetromino in place
        self.lock_tetromino()
        
    # Keep moving down until collision
    def get_drop_distance(self):
        drop_distance = 0
        while self.move_tetromino(0, 1):
            drop_distance += 1
        return drop_distance
        
        
    def calculate_drop_position(self):
        """Calculate how far the current tetromino can drop."""
        drop_distance = 0
        while True:
            new_positions = self.current_tetromino.move(0, drop_distance + 1)
            if not self.board.is_valid_position(new_positions):
                break
            drop_distance += 1
        return drop_distance
        
    def lock_tetromino(self):
        """Lock the current tetromino in place and spawn a new one."""
        # Add the current tetromino to the board
        if not self.board.add_tetromino(self.current_tetromino):
            self.game_over = True
            self.cleanup()
            return
            
        # Create the next tetromino
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = get_random_tetromino(x=5, y=0, rng=self.rng)
        
        # Reset soft drop
        self.soft_drop = False
        
        # Update ghost piece position
        self.ghost_y_offset = self.calculate_drop_position()
        
    def update(self):
        """Update the game state."""
        if self.game_over or self.paused:
            return
            
        current_time = time.time()
        
        # Check if any lines need to be cleared
        lines_cleared = self.board.update_clear_animation()
        self.ai_controller.get_game_data(self)
        if lines_cleared > 0:
            # Update score
            self.score += POINTS_PER_LINE[lines_cleared] * self.level
            self.lines_cleared += lines_cleared
            
            # Level up every 10 lines
            new_level = self.lines_cleared // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed *= LEVEL_SPEEDUP
        
        # Process AI move
        ai_move_data = self.ai_controller.get_next_move()
        if ai_move_data:
            self.process_ai_move(ai_move_data)
                
        # Check if it's time for the tetromino to fall
        fall_time = self.fall_speed
        if self.soft_drop:
            fall_time *= 0.1  # Move down 10x faster when soft dropping
            
        if current_time - self.last_fall_time > fall_time:
            # Try to move the tetromino down
            if not self.move_tetromino(0, 1):
                # If the tetromino can't move down, lock it in place
                self.lock_tetromino()
            
            # Add points for soft drop
            if self.soft_drop:
                self.score += SOFT_DROP_POINTS
                
            self.last_fall_time = current_time
            
    def process_ai_move(self, move_data):
        """
        Process a move from the AI controller.
        
        Args:
            move_data (dict): Dictionary containing move and probability information
        """
        move = move_data['move']
        probabilities = move_data['probabilities']
        chosen_probability = move_data['chosen_probability']
        
        current_tetromino = self.current_tetromino
        next_tetromino = self.next_tetromino
        
        # OLD
        #move_names = {
        #    Movement.MOVE_LEFT: "MOVE_LEFT",
        #    Movement.MOVE_RIGHT: "MOVE_RIGHT", 
        #    Movement.ROTATE: "ROTATE",
        #    Movement.SOFT_DROP: "SOFT_DROP",
        #    Movement.HARD_DROP: "HARD_DROP",
        #    Movement.NO_MOVE: "NO_MOVE"
        #}
        
        # NEW
        move_names = {
            Movement.MOVE_LEFT: "MOVE_LEFT",
            Movement.MOVE_RIGHT: "MOVE_RIGHT", 
            Movement.ROTATE: "ROTATE",
            Movement.NO_MOVE: "NO_MOVE",
            Movement.HARD_DROP: "HARD_DROP"
        }
        
        #log_data = {
        #    'move_type': move_names.get(move, "UNKNOWN"),
        #    'tetromino_x': current_tetromino.x,
        #    'tetromino_y': current_tetromino.y,
        #    'tetromino_shape': current_tetromino.shape,
        #    'tetromino_rotation': current_tetromino.rotation,
        #    'next_shape': next_tetromino.shape,
        #    'fall_speed': self.fall_speed,
        #    'score': self.score,
        #    'level': self.level,
        #    'lines_cleared': self.lines_cleared,
        #    'probabilities': probabilities,
        #    'chosen_probability': chosen_probability
        #}
        #self.csv_logger.log_move(log_data)
         
        self.move_count += 1
        if move == Movement.MOVE_LEFT:
            #print('Moving left.')
            self.move_tetromino(-1, 0)
        elif move == Movement.MOVE_RIGHT:
            #print('Moving right.')
            self.move_tetromino(1, 0)
        elif move == Movement.ROTATE:
            #print('Rotating.')
            self.rotate_tetromino()
        #elif move == Movement.SOFT_DROP:
        #    print('Soft drop done.')
        #    self.soft_drop = True
        elif move == Movement.HARD_DROP:
        #    print('Hard drop d(-__-)b.')
            self.hard_drop_count += 1
            self.hard_drop()
        elif move == Movement.NO_MOVE:
            #print('Doing nothing.')
            return
        # Reset soft drop after processing
        #if move != Movement.SOFT_DROP:
        #    self.soft_drop = False
               
    def draw(self, screen):
        """
        Draw the game state.
        
        Args:
            screen (pygame.Surface): The screen to draw on
        """
        # Draw the board
        self.board.draw(screen)
        
        # Draw the ghost piece
        self.board.draw_ghost(screen, self.current_tetromino, self.ghost_y_offset)
        
        # Draw the current tetromino
        self.board.draw_tetromino(screen, self.current_tetromino)
        
        # Draw the next tetromino preview
        self.draw_next_tetromino(screen)
        
        # Draw the score, level, and lines cleared
        self.draw_stats(screen)
        
        # Draw NEAT vis
        if self.ai_controller and self.ai_controller.model:
            self.neat_visualizer.draw_network(screen, self.ai_controller.model)
        
        # Draw game over or paused message if needed
        if self.game_over:
            self.draw_game_over(screen)
        elif self.paused:
            self.draw_paused(screen)
            
    def draw_next_tetromino(self, screen):
        """Draw the next tetromino preview."""
        # Draw the preview box
        preview_x = 550
        preview_y = 100
        preview_width = 120
        preview_height = 120
        
        pygame.draw.rect(screen, WHITE, (preview_x, preview_y, preview_width, preview_height), 2)
        
        # Draw the label
        label = self.font.render("Next:", True, WHITE)
        screen.blit(label, (preview_x, preview_y - 30))
        
        # Draw the tetromino (centered in the preview box)
        for x, y in self.next_tetromino.blocks:
            block_x = preview_x + (preview_width // 2) + x * 20
            block_y = preview_y + (preview_height // 2) + y * 20
            pygame.draw.rect(screen, self.next_tetromino.color, (block_x, block_y, 20, 20))
            pygame.draw.rect(screen, BLACK, (block_x, block_y, 20, 20), 1)
            
    def draw_stats(self, screen):
        """Draw the game statistics."""
        stats_x = 850
        stats_y = 50
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (stats_x, stats_y))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (stats_x, stats_y + 30))
        
        # Draw lines cleared
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (stats_x, stats_y + 60))
        
        # Draw AI mode status
        ai_text = self.font.render(f"AI Mode: ON", True, WHITE)
        screen.blit(ai_text, (stats_x, stats_y + 90))
        
        # Draw controls
        controls_y = 400
        controls = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "P : Pause"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = self.font.render(text, True, WHITE)
            screen.blit(ctrl_text, (stats_x, controls_y + i * 25))
            
    def draw_game_over(self, screen):
        """Draw the game over message."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw game over message
        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(game_over_text, text_rect)
        
        # Draw restart message
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(restart_text, restart_rect)
        
    def draw_paused(self, screen):
        """Draw the paused message."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw paused message
        paused_text = self.large_font.render("PAUSED", True, WHITE)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(paused_text, text_rect)
        
    def cleanup(self):
        if hasattr(self, 'csv_logger'):
            self.csv_logger.close()
    
    def __del__(self):
        pass
        #self.cleanup()