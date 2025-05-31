from model.common_genome_data import *
from model.model import *
from model.model_constants import INPUT_NETWORK_SIZE, OUTPUT_NETWORK_SIZE
from model.genome import InnovationDatabase

class Experiment:
    def __init__(self, iteration_count:int, population_size:int, common_rates:CommonRates):
        self.iteration_count = iteration_count
        self.population = []
        self.population_size = population_size
        self.common_rates = common_rates
        
    def __call__(self):
        common_innovation_db = InnovationDatabase()
        for _ in range(self.population_size - 1):
            model = Model.generate_network(input_size=INPUT_NETWORK_SIZE, output_size=OUTPUT_NETWORK_SIZE, common_rates=self.common_rates, )
    
        
    
    