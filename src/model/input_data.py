
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
class InputDataExtended:
    def __init__(self, x_block:float, y_block:float, block_type:float, block_fall_speed:float, block_rotation:float, 
                 columns_normalized:list, drop_distance: float, almost_complete_lines: list, height_differences_normalized:list, # normalized
        board_state:list
        ):
        self.x_block = x_block
        self.y_block = y_block
        self.block_type = block_type
        self.block_fall_speed = block_fall_speed
        self.block_rotation = block_rotation
        if len(columns_normalized) > 1:
            self.column_1 = columns_normalized[0]
            self.column_2 = columns_normalized[1]
            self.column_3 = columns_normalized[2]
            self.column_4 = columns_normalized[3]
            self.column_5 = columns_normalized[4]
            self.column_6 = columns_normalized[5]
            self.column_7 = columns_normalized[6]
            self.column_8 = columns_normalized[7]
            self.column_9 = columns_normalized[8]
            self.column_10 = columns_normalized[9]
        self.drop_distance = drop_distance
        #self.almost_complete_lines = almost_complete_lines # 20 inputs (GRID_HEIGHT)
        self.height_differences = height_differences_normalized # 10 inputs (GRID_WIDTH)
        #self.board_state = board_state # 200 inputs (GRID_HEIGHT * GRID_WIDTH)
        
    def to_dict(self):
        #dict = {
        #0 : self.x_block,
        #1 : self.y_block,
        #2 : self.block_type,
        #3 : self.block_fall_speed,
        #4 : self.block_rotation,
        #5 : self.column_1,
        #6 : self.column_2,
        #7 : self.column_3,
        #8 : self.column_4,
        #9 : self.column_5,
        #10 : self.column_6,
        #11 : self.column_7,
        #12 : self.column_8,
        #13 : self.column_9,
        #14 : self.column_10,
        #15 : self.drop_distance
        #}
        
        #dict_len = len(dict) # in the case 0-15, len = 16, i = 0 -> dict[16 + 0] = next value
        
        dict = {
        0 : self.x_block,
        1 : self.y_block,
        2 : self.block_type,
        3 : self.block_rotation,
        4 : self.column_1,
        5 : self.column_2,
        6 : self.column_3,
        7 : self.column_4,
        8 : self.column_5,
        9  : self.column_6,
        10 : self.column_7,
        11 : self.column_8,
        12 : self.column_9,
        13 : self.column_10,
        14 : self.drop_distance
        }
        
        dict_len = len(dict) # in the case 0-14, len = 15, i = 0 -> dict[15 + 0] = next value
        
        #for i, value in enumerate(self.almost_complete_lines):
        #    dict[dict_len + i] = value
        #    
        #dict_len = len(dict) # update after last list
        
        for i, value in enumerate(self.height_differences):
            dict[dict_len + i] = value
            
        #dict_len = len(dict) # update after last list
        #        
        #for i, value in enumerate(self.board_state):
        #    dict[dict_len + i] = value
        return dict