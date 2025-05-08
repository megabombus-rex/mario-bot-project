# Mapping of data between the game and our model

## Model input coming from a game:

1. X pos of the block
2. Y pos of the block
3. block type (index or character)
4. block fall speed
5. block rotation (0 - none, 1 - rotated 90 degrees, 2 - rotated 180 degrees, 3 - rotated 270 degrees)
6. next block coming (type, as 3)

## Model output sent to the game
1. Move left
2. Move right
3. Move down
4. Rotate
5. Instant fall