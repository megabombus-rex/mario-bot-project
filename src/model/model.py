from genome import (NodeGene as Node, ConnectionGene as Connection, Genome)
from input_data import InputData
from model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
import random

class Model:
    def __init__(self, genome=Genome):
        self.genome = genome
        
    # max possible starting connections should be low, significantly lower
    def __init__(self, input_size, output_size, start_connection_probability, max_start_connection_count):
        input_nodes = []
        output_nodes = []
        connections = []
        id_count = 0
        for i in input_size:
            node = Node(id_count, INPUT_NODE, 0)
            input_nodes += node
            id_count += 1
        
        for i in output_size:
            node = Node(id_count, OUTPUT_NODE, 0)
            output_nodes += node
            id_count += 1
        
        for i in max_start_connection_count:
            if random.uniform(0, 1) > start_connection_probability:
                idx1 = random.choice(input_nodes).id              
                idx2 = random.choice(output_nodes).id
                
                if any(x.start_node_id == idx1 and x.end_node_id == idx2 for x in connections):
                    continue
                
                connection = Connection(idx1, idx2, random.uniform(0, 1), 0)
                connections += connection
        
        self.genome = Genome(input_nodes=input_nodes, output_nodes=output_nodes)         
        
    # forward the data
    def __call__(self, input=InputData):
        pass