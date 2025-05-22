
import pygame
from game.constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y, COLORS, BLACK, GRAY, WHITE

class Board:
    def __init__(self):
        """Initialize an empty Tetris board."""
        # Create empty grid (None indicates empty cell)
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Track filled lines for clearing and scoring
        self.lines_to_clear = []
        self.clear_animation_counter = 0
    
    def is_valid_position(self, positions):
        """
        Check if a set of positions is valid on the board.
        
        Args:
            positions (list): List of (x, y) tuples representing block positions
            
        Returns:
            bool: True if all positions are valid, False otherwise
        """
        for x, y in positions:
            # Check if position is out of bounds
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            
            # Blocks above the visible grid are allowed (for spawning)
            if y < 0:
                continue
                
            # Check if position overlaps with existing blocks
            if self.grid[y][x] is not None:
                return False
                
        return True
    
    def add_tetromino(self, tetromino):
        """
        Place a tetromino on the board permanently.
        
        Args:
            tetromino (Tetromino): The tetromino to place
            
        Returns:
            bool: True if placement was successful, False if game over
        """
        positions = tetromino.get_positions()
        
        # Check if any positions are above the visible grid (game over)
        for x, y in positions:
            if y < 0 or self.grid[y][x]:
                return False  # Game over
        
        # Add each block to the grid
        for x, y in positions:
            self.grid[y][x] = tetromino.color
            
        # Check for completed lines
        self.check_lines()
        
        return True
    
    def check_lines(self):
        """Check for and mark completed lines for clearing."""
        self.lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            # Check if this row is completely filled
            if all(cell is not None for cell in self.grid[y]):
                self.lines_to_clear.append(y)
    
    def clear_lines(self):
        """Clear completed lines and shift rows down."""
        # Sort lines in descending order to avoid shifting issues
        lines = sorted(self.lines_to_clear, reverse=True)
        
        for line in lines:
            # Remove the completed line
            self.grid.pop(line)
            # Add a new empty line at the top
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
        
        # Reset lines to clear
        cleared_count = len(self.lines_to_clear)
        self.lines_to_clear = []
        self.clear_animation_counter = 0
        
        return cleared_count
    
    def update_clear_animation(self):
        """Update the line clearing animation counter."""
        if self.lines_to_clear:
            self.clear_animation_counter += 1
            # After animation is complete, actually clear the lines
            if self.clear_animation_counter >= 10:  # 10 frames for the animation
                return self.clear_lines()
        return 0
    
    def draw(self, screen):
        """
        Draw the board and its contents.
        
        Args:
            screen (pygame.Surface): The screen to draw on
        """
        # Draw the board background
        board_rect = pygame.Rect(
            BOARD_OFFSET_X - 1, 
            BOARD_OFFSET_Y - 1, 
            GRID_WIDTH * CELL_SIZE + 2, 
            GRID_HEIGHT * CELL_SIZE + 2
        )
        pygame.draw.rect(screen, WHITE, board_rect, 2)
        
        # Draw the grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_x = BOARD_OFFSET_X + x * CELL_SIZE
                cell_y = BOARD_OFFSET_Y + y * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                # Draw filled cell or empty cell
                if self.grid[y][x] is not None:
                    # If this line is being cleared, flash it
                    if y in self.lines_to_clear:
                        if self.clear_animation_counter % 2 == 0:
                            pygame.draw.rect(screen, WHITE, cell_rect)
                        else:
                            pygame.draw.rect(screen, self.grid[y][x], cell_rect)
                    else:
                        pygame.draw.rect(screen, self.grid[y][x], cell_rect)
                    # Draw cell border
                    pygame.draw.rect(screen, BLACK, cell_rect, 1)
                else:
                    # Draw empty cell with slight grid pattern
                    pygame.draw.rect(screen, BLACK, cell_rect)
                    pygame.draw.rect(screen, GRAY, cell_rect, 1)
    
    def draw_tetromino(self, screen, tetromino):
        """
        Draw a tetromino on the board.
        
        Args:
            screen (pygame.Surface): The screen to draw on
            tetromino (Tetromino): The tetromino to draw
        """
        for x, y in tetromino.get_positions():
            # Only draw blocks within the visible grid
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                cell_x = BOARD_OFFSET_X + x * CELL_SIZE
                cell_y = BOARD_OFFSET_Y + y * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                pygame.draw.rect(screen, tetromino.color, cell_rect)
                pygame.draw.rect(screen, BLACK, cell_rect, 1)
    
    def draw_ghost(self, screen, tetromino, ghost_y):
        """
        Draw the ghost piece (where the tetromino will land).
        
        Args:
            screen (pygame.Surface): The screen to draw on
            tetromino (Tetromino): The current tetromino
            ghost_y (int): The y-offset for the ghost piece
        """
        ghost_positions = [(x, y + ghost_y) for x, y in tetromino.get_positions()]
        
        for x, y in ghost_positions:
            # Only draw blocks within the visible grid
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                cell_x = BOARD_OFFSET_X + x * CELL_SIZE
                cell_y = BOARD_OFFSET_Y + y * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                # Draw semi-transparent ghost block
                ghost_color = (*tetromino.color[:3], 100)  # Transparent version of the color
                pygame.draw.rect(screen, ghost_color, cell_rect)
                pygame.draw.rect(screen, BLACK, cell_rect, 1)