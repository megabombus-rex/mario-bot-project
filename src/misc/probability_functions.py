import math

class ProbabilityFunction:
    def __call__(self, values):
        raise NotImplementedError('ProbabilityFunction is an abstract class with no implementation. Use a child class object.')
    
class Softmax(ProbabilityFunction):
    def __call__(self, values):
        total = sum(math.exp(number) for number in values)
        return [math.exp(number) / total for number in values]
        
        