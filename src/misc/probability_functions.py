import math
import numpy as np

class ProbabilityFunction:
    def __call__(self, values):
        raise NotImplementedError('ProbabilityFunction is an abstract class with no implementation. Use a child class object.')
    
class Softmax(ProbabilityFunction):
    def __call__(self, values):
        total = sum(math.exp(number) for number in values)
        return [math.exp(number) / total for number in values]
    
class TemperatureProb(ProbabilityFunction):
    def __call__(self, values):
        epsilon = 0.3  # 30% random exploration
        output_values = values
    
        if np.random.random() < epsilon:
            # Random action
            return [0.2, 0.2, 0.2, 0.2, 0.2]  # Uniform
        else:
            # Greedy action (choose best)
            best_action = np.argmax(output_values)
            probs = [0.05, 0.05, 0.05, 0.05, 0.05]  # Small prob for others
            probs[best_action] = 0.8  # High prob for best
            return probs
        
        