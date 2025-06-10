from enum import IntEnum

# Game window settings
SCREEN_WIDTH = 1200  
SCREEN_HEIGHT = 700
TITLE = "Team Tetris"
FPS = 60

# Board dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

# Movement mapping
class Movement(IntEnum):
    MOVE_LEFT = 0
    MOVE_RIGHT = 1
    ROTATE = 2
    SOFT_DROP = 3
    HARD_DROP = 4
    NO_MOVE = 5

# Board position
BOARD_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
BOARD_OFFSET_Y = 50

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino colors
COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# Game timing (milliseconds)
INITIAL_FALL_SPEED = 1000  # 1 second
LEVEL_SPEEDUP = 0.8  # Each level is 20% faster than the previous level
SOFT_DROP_FACTOR = 0.1  # Soft drop is 10x faster than normal

# Scoring
POINTS_PER_LINE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800  # Tetris!
}
SOFT_DROP_POINTS = 1  # Per cell dropped
HARD_DROP_POINTS = 2  # Per cell dropped

# Key repeat settings
KEY_DELAY = 200
KEY_INTERVAL = 100

# Seed for randomization (if needed), those seeds should be different
DEFAULT_SEED = None
DEFAULT_SEED_MODEL = 12345

# NEAT Network Visualizer window positioning consts
NEAT_VIZ_X = 50
NEAT_VIZ_Y = 50
NEAT_VIZ_WIDTH = 300
NEAT_VIZ_HEIGHT = 400

CSV_LOG_ENABLED = True
CSV_LOG_FILENAME = "ai_moves.csv"
CSV_LOG_DIRECTORY = "logs"