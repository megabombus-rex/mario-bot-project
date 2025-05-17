import math

class ActivationFunction:    
    def __call__(self, input):
        raise NotImplementedError("Activation Function is an abstract class with no implementation. Use a child class object.")

class ReLU(ActivationFunction):
    def __call__(self, input):
        return max(0, input)
    
class Sigmoid(ActivationFunction):
    def __call__(self, input):
        return 1 / (1 + math.exp(-input))