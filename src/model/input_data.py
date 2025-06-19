
class InputData:
    def __init__(self, x_block:int, y_block:int, block_type:int, block_fall_speed:int, block_rotation:int, next_block_type:int):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        self.next_block_type = next_block_type
        
    def to_dict(self):
        dict = {
        0 : self.x_block,
        1 : self.y_block,
        2 : self.block_type,
        3 : self.block_fall_speed,
        4 : self.block_rotation,
        5 : self.next_block_type,
        }
        return dict
    
# areas are min/max/mean pooled 
class InputDataNew:
    def __init__(self, x_block:float, y_block:float, block_type:float, block_fall_speed:float, block_rotation:float, 
                 column_1:float, column_2:float, column_3:float, column_4:float, column_5:float, column_6:float, column_7:float, column_8:float, column_9: float, column_10: float, drop_distance: float):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        self.column_1 = column_1
        self.column_2 = column_2
        self.column_3 = column_3
        self.column_4 = column_4
        self.column_5 = column_5
        self.column_6 = column_6
        self.column_7 = column_7
        self.column_8 = column_8
        self.column_9 = column_9
        self.column_10 = column_10
        self.drop_distance = drop_distance
        
    def to_dict(self):
        dict = {
        0 : self.x_block,
        1 : self.y_block,
        2 : self.block_type,
        3 : self.block_fall_speed,
        4 : self.block_rotation,
        5 : self.column_1,
        6 : self.column_2,
        7 : self.column_3,
        8 : self.column_4,
        9 : self.column_5,
        10 : self.column_6,
        11 : self.column_7,
        12 : self.column_8,
        13 : self.column_9,
        14 : self.column_10,
        15 : self.drop_distance
        }
        return dict