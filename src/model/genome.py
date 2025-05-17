from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)

class Gene:
    def __init__(self, innovation_number=int):
        self.innovation_number = innovation_number

class NodeGene(Gene):
    def __init__(self, id=int, type=int, weight=float, innovation_number=int):
        super().__init__(innovation_number)
        self.id = id
        self.type = type
        self.weight = weight
        
    def __str__(self):
        return f'node_id: {self.id}, type: {self.type}, weight: {self.weight}'

class ConnectionGene(Gene):
    def __init__(self, start_node_id=int, end_node_id=int, innovation_number=int):
        super().__init__(innovation_number)
        self.start_node_id = start_node_id
        self.end_node_id = end_node_id
    
    def __str__(self):
        return f'start_node_id: {self.start_node_id}, end_node_id: {self.end_node_id}'
        
class Genome:
    def __init__(self, input_nodes = list[NodeGene], output_nodes = list[NodeGene], connections = list[ConnectionGene]):
        self.nodes = input_nodes + output_nodes
        self.connections = connections
        self.node_count = len(self.nodes)
        self.connection_count = len(self.connections)
        self.size = self.node_count + self.connection_count
    
    def mutation_add_node(self):
        self.size += 1
        node = NodeGene(self.size, HIDDEN_NODE, 0.5, 0) # temporary
        self.nodes.append(node)
        self.node_count += 1
        
    def mutation_add_connection(self):
        connection = ConnectionGene(0, 1, 0) # temporary
        self.connections.append(connection)
        self.connection_count += 1
        self.size += 1
        
    def __str__(self):
        node_strs = [str(node) for node in self.nodes]
        conn_strs = [str(conn) for conn in self.connections]
        return f"Nodes ({self.node_count}): [{', '.join(node_strs)}],\n Connections ({self.connection_count}): [{', '.join(conn_strs)}]"