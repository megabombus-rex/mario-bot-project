class PoolingAlgorithm:
    def __call__(self, grid, width, height, x_offset, y_offset):
        raise NotImplementedError("Activation Function is an abstract class with no implementation. Use a child class object.")

# this is kinda useless as the values are 0 or 1
class MaxPoolingAlgorithm(PoolingAlgorithm):
    def __call__(self, grid, width, height, x_offset, y_offset):
        max = 0.0
        for i in range(x_offset, x_offset + width):
            for j in range(y_offset, y_offset + height):
                if (grid[i][j] == None):
                    continue
                if (grid[i][j] > max):
                    max = grid                     
        
        return max


# this is kinda useless as the values are 0 or 1
class MinPoolingAlgorithm(PoolingAlgorithm):
    def __call__(self, grid, width, height, x_offset, y_offset):
        min = 2.0
        for i in range(x_offset, x_offset + width):
            for j in range(y_offset, y_offset + height):
                if (grid[i][j] == None):
                    continue
                if (grid[i][j] < min):
                    min = grid                     
        
        return min
    
class MeanPoolingAlgorithm(PoolingAlgorithm):
    def __call__(self, grid, width, height, x_offset, y_offset):
        #print(f'offset x: {x_offset}, offset y: {y_offset}')
        sum = 0.0
        for i in range(int(x_offset), int(x_offset + width)):
            for j in range(int(y_offset), int(y_offset + height)):
                if (grid[i][j] == None):
                    #print(f'grid[{i}][{j}] is none.')
                    continue
                sum += grid[i][j]
        mean = sum / (width * height) if sum > 0.0 else 0.0
        #print(f'From grid on x: {x_offset} and y: {y_offset} mean: {mean}, sum: {sum}')
        return mean