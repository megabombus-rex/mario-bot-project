from collections import defaultdict

class InputData:
    def __init__(self, x_block:int, y_block:int, block_type:int, block_fall_speed:int, block_rotation:int, next_block_type:int):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        self.next_block_type = next_block_type
        
    def to_dict(self):
        dict = defaultdict(int)
        dict[0] = self.x_block
        dict[1] = self.y_block
        dict[2] = self.block_type
        dict[3] = self.block_fall_speed
        dict[4] = self.block_rotation
        dict[5] = self.next_block_type
        return dict