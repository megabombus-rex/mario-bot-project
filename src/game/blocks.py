import random
from game.constants import COLORS

# Tetromino shapes defined as offsets from their center
# Each shape is defined in its default orientation (spawn orientation)
TETROMINOES = {
    'I': [(-1, 0), (0, 0), (1, 0), (2, 0)],  # Horizontal line
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],   # Square
    'T': [(-1, 0), (0, 0), (1, 0), (0, 1)],  # T-shape
    'S': [(-1, 1), (0, 1), (0, 0), (1, 0)],  # S-shape
    'Z': [(-1, 0), (0, 0), (0, 1), (1, 1)],  # Z-shape
    'J': [(-1, 0), (0, 0), (1, 0), (-1, 1)], # J-shape
    'L': [(-1, 0), (0, 0), (1, 0), (1, 1)]   # L-shape
}

TETROMINOES_INDEXES = {
    'I': 0,
    'O': 1,
    'T': 2,
    'S': 3,
    'Z': 4,
    'J': 5,
    'L': 6
}

class Tetromino:
    def __init__(self, shape=None, x=None, y=None, seed=None):
        """
        Initialize a tetromino.
        
        Args:
            shape (str, optional): Shape type ('I', 'O', 'T', 'S', 'Z', 'J', 'L'). Random if None.
            x (int, optional): Initial x position. Defaults to center if None.
            y (int, optional): Initial y position. Defaults to top if None.
            seed (int, optional): Seed for random shape generation.
        """
        if seed is not None:
            random.seed(seed)
        
        # Choose a random shape if not specified
        self.shape = shape if shape else random.choice(list(TETROMINOES.keys()))
        self.color = COLORS[self.shape]
        
        # Set initial position (default is center top of the grid)
        self.x = x if x is not None else 5  # Center of standard 10-width grid
        self.y = y if y is not None else 0  # Top of the grid
        
        # Get the blocks for this shape
        self.blocks = TETROMINOES[self.shape].copy()
        
        # Rotation state (0-3 representing 0, 90, 180, 270 degrees)
        self.rotation = 0

    def get_positions(self):
        """Return the current positions of all blocks in the grid."""
        return [(self.x + block[0], self.y + block[1]) for block in self.blocks]

    def rotate(self, clockwise=True):
        """
        Rotate the tetromino.
        
        Args:
            clockwise (bool): True for clockwise, False for counter-clockwise
        
        Returns:
            list: The new positions after rotation (before applying)
        """
        # For O tetromino, rotation doesn't change anything
        if self.shape == 'O':
            return self.get_positions()
        
        # Create rotated version of blocks
        rotated = []
        for x, y in self.blocks:
            # Rotate 90 degrees clockwise: (x, y) -> (y, -x)
            # Rotate 90 degrees counter-clockwise: (x, y) -> (-y, x)
            if clockwise:
                rotated.append((y, -x))
            else:
                rotated.append((-y, x))
        
        # Calculate the new positions
        new_positions = [(self.x + block[0], self.y + block[1]) for block in rotated]
        
        # If rotation is valid (checked elsewhere), update the blocks
        self.blocks = rotated
        self.rotation = (self.rotation + (1 if clockwise else -1)) % 4
        
        return new_positions

    def move(self, dx, dy):
        """
        Move the tetromino.
        
        Args:
            dx (int): Change in x position
            dy (int): Change in y position
            
        Returns:
            list: The new positions after movement (before applying)
        """
        new_positions = [(self.x + block[0] + dx, self.y + block[1] + dy) for block in self.blocks]
        return new_positions
        
    def apply_move(self, dx, dy):
        """
        Apply the movement to the tetromino.
        
        Args:
            dx (int): Change in x position
            dy (int): Change in y position
        """
        self.x += dx
        self.y += dy
        
    def __str__(self):
        return f"Tetromino({self.shape} at ({self.x}, {self.y}), rotation: {self.rotation})"


def get_random_tetromino(x=None, y=None, seed=None):
    """Convenience function to get a random tetromino."""
    return Tetromino(x=x, y=y, seed=seed)