from model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)

class Gene:
    def __init__(self, innovation_number=int):
        self.innovation_number = innovation_number

class NodeGene(Gene):
    def __init__(self, id, type, innovation_number=int):
        super().__init__(innovation_number)
        self.id = id
        self.type = type

class ConnectionGene(Gene):
    def __init__(self, start_node_id, end_node_id, weight, innovation_number=int):
        super().__init__(innovation_number)
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
        self.weight = weight
        
class Genome:
    def __init__(self, input_nodes = list[NodeGene], output_nodes = list[NodeGene], connections = list[ConnectionGene]):
        self.nodes = input_nodes + output_nodes
        self.connections = connections
        self.node_count = len(self.nodes)
        self.connection_count = len(connections)
        self.size = self.node_count + self.connection_count
    
    def mutation_add_node(self, id, ):
        node = NodeGene(0, HIDDEN_NODE, 0) # temporary
        self.nodes += node
        self.node_count += 1
        self.size += 1
        
    def mutation_add_connection(self):
        connection = ConnectionGene(0, 1, 0.5, 0) # temporary
        self.connections += connection
        self.connection_count += 1
        self.size += 1