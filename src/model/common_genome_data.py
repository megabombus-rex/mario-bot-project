class CommonRates:
    def __init__(self, weight_mutation_rate=float, activation_mutation_rate=float, connection_addition_mutation_rate=float, node_addition_mutation_rate=float, start_connection_probability=int, max_start_connection_count=int):
        self.weight_mutation_rate = weight_mutation_rate
        self.activation_mutation_rate = activation_mutation_rate
        self.connection_addition_mutation_rate = connection_addition_mutation_rate
        self.node_addition_mutation_rate = node_addition_mutation_rate
        self.start_connection_probability = start_connection_probability
        self.max_start_connection_count = max_start_connection_count
        
class Weights:
    def __init__(self, weight_range):
        self.weight_range = weight_range