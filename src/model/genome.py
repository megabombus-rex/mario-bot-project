from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.activation_functions import *
import random

class Gene:
    def __init__(self, innovation_number=int):
        self.innovation_number = innovation_number
        self.is_disabled = False

class NodeGene(Gene):
    def __init__(self, id=int, type=int,innovation_number=int, activation_function=ActivationFunction):
        super().__init__(innovation_number)
        self.id = id
        self.type = type
        self.input_sum = 0.0
        self.output = 0.0
        self.activation_function = activation_function
        self.inputs = []
        
    def __str__(self):
        return f'node_id: {self.id}, type: {self.type}'

class ConnectionGene(Gene):
    def __init__(self, in_node:NodeGene, out_node:NodeGene, weight:float, innovation_number=int):
        super().__init__(innovation_number)
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
    
    def __str__(self):
        return f'start_node_id: {self.in_node.id}, end_node_id: {self.out_node.id}, weight: {self.weight}'
        
class Genome:
    def __init__(self, input_nodes:list, output_nodes:list, connections:list):
        self.nodes = input_nodes + output_nodes
        self.connections = connections
        self.node_count = len(self.nodes)
        self.connection_count = len(self.connections)
        self.size = self.node_count + self.connection_count
        
        self.node_map = {node.id: node for node in self.nodes}
        for node in self.nodes:
            node.inputs = []

        for connection in self.connections:
            if not connection.is_disabled:
                end_node = self.node_map.get(connection.out_node.id)
                if end_node:
                    end_node.inputs.append(connection)
            
    def __init__(self, nodes:list, connections:list):
        self.nodes = nodes
        self.connections = connections
        self.node_count = len(self.nodes)
        self.connection_count = len(self.connections)
        self.size = self.node_count + self.connection_count
        
        self.node_map = {node.id: node for node in self.nodes}
        for node in self.nodes:
            node.inputs = []

        for connection in self.connections:
            if not connection.is_disabled:
                end_node = self.node_map.get(connection.out_node.id)
                if end_node:
                    end_node.inputs.append(connection)
        
    
    # after innovation_db is implemented this can be changed
    def mutation_add_node(self):
        self.size += 1
        node = NodeGene(self.size, HIDDEN_NODE, 0, ReLU()) # temporary
        self.nodes.append(node)
        self.node_count += 1
        
    # after innovation_db is implemented this can be changed
    def mutation_add_connection(self):
        connection = ConnectionGene(self.node_map[0], self.node_map[1], random(), 0) # temporary
        self.connections.append(connection)
        self.connection_count += 1
        self.size += 1
        
    def __str__(self):
        node_strs = [str(node) for node in self.nodes]
        conn_strs = [str(conn) for conn in self.connections]
        return f"Nodes ({self.node_count}): [{', '.join(node_strs)}],\n Connections ({self.connection_count}): [{', '.join(conn_strs)}]"
    