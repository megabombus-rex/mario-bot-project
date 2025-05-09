class InputData:
    def __init__(self, x_block = int, y_block = int, block_type = int, block_fall_speed = int, block_rotation = int, next_block_type = int):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        self.next_block_type = next_block_type