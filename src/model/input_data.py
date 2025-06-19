
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
                 area_1:float, area_2:float, area_3:float, area_4:float, area_5:float, area_6:float, area_7:float, area_8:float):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        self.area_1 = area_1
        self.area_2 = area_2
        self.area_3 = area_3
        self.area_4 = area_4
        self.area_5 = area_5
        self.area_6 = area_6
        self.area_7 = area_7
        self.area_8 = area_8
        
    def to_dict(self):
        dict = {
        0 : self.x_block,
        1 : self.y_block,
        2 : self.block_type,
        3 : self.block_fall_speed,
        4 : self.block_rotation,
        5 : self.area_1,
        6 : self.area_2,
        7 : self.area_3,
        8 : self.area_4,
        9 : self.area_5,
        10 : self.area_6,
        11 : self.area_7,
        12 : self.area_8
        }
        return dict