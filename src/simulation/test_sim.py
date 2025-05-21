from model import * 

class Experiment:
    def __init__(self, iteration_count, population_size, common_rates):
        self.iteration_count = iteration_count
        self.population = []
        self.population_size = population_size
        self.common_rates = common_rates
        
    
    