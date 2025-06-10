from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.activation_functions import *
from model.common_genome_data import *
import numpy as np

class Gene:
    def __init__(self):
        pass

class NodeGene(Gene):
    def __init__(self, id=int, type=int, activation_function=ActivationFunction):
        super().__init__()
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
        super().__init__()
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.innovation_number = innovation_number
        self.is_disabled = False
    
    def __str__(self):
        return f'start_node_id: {self.in_node.id}, end_node_id: {self.out_node.id}, weight: {self.weight}'
        
class InnovationDatabase:
    def __init__(self, start_node_count=0, start_innov_count=0):
        self.connection_history = {}  # (in_node_id, out_node_id): innovation_number
        self.node_history = {}        # (split_connection_innov): node_id
        self.innovation_count = start_innov_count
        self.node_count = start_node_count
        
    def get_or_create_connection_innovation(self, in_node_id, out_node_id):
        key = (in_node_id, out_node_id)
        if key in self.connection_history:
            return self.connection_history[key]
        else:
            self.innovation_count += 1
            self.connection_history[key] = self.innovation_count
            return self.innovation_count
        
    def get_or_create_node_id(self, split_connection_innov):
        if split_connection_innov in self.node_history:
            return self.node_history[split_connection_innov]
        else:
            self.node_count += 1
            self.node_history[split_connection_innov] = self.node_count
            return self.node_count
        
    def get_next_node_id(self):
        self.node_count += 1
        return self.node_count

class Genome:
    # inputs -> outputs -> new_nodes
    def __init__(self, nodes:list, connections:list, input_nodes_count:int, output_nodes_count:int, innovation_db:InnovationDatabase, rng:np.random):
        self.nodes = nodes
        self.connections = connections
        self.input_nodes_count = input_nodes_count
        self.output_nodes_count = output_nodes_count
        self.innovation_db = innovation_db
        self.rng = rng
        
        self.node_map = {node.id: node for node in self.nodes}
        for node in self.nodes:
            node.inputs = []

        for connection in self.connections:
            if not connection.is_disabled:
                end_node = self.node_map.get(connection.out_node.id)
                if end_node:
                    end_node.inputs.append(connection)
           
    # taken from the NEAT paper
    # In adding a new node, 
    # the connection gene being split is disabled, and two new connection genes are added to the
    # end the genome. The new node is between the two new connections. A new node gene
    # representing this new node is added to the genome as well.
    def mutation_add_node(self):
        
        # placeholders
        disabled_connection = None
        node_id = 0
        
        # put it in between connections
        if self.connections: 
            disabled_connection = self.rng.choice(self.connections)
            disabled_connection.is_disabled = True
        
        if disabled_connection is not None:
            node_id = self.innovation_db.get_or_create_node_id(disabled_connection.innovation_number)
        else:
            node_id = self.innovation_db.get_next_node_id()
            
        activation_function = self.rng.choice([ReLU(), Sigmoid()])
        node = NodeGene(node_id, HIDDEN_NODE, activation_function)
        new_connections = []
        
        if disabled_connection is not None:
            innov_1 = self.innovation_db.get_or_create_connection_innovation(disabled_connection.in_node.id, node.id)
            innov_2 = self.innovation_db.get_or_create_connection_innovation(node.id, disabled_connection.out_node.id)
            connection_1 = ConnectionGene(disabled_connection.in_node, node, self.rng.random(), innov_1)
            connection_2 = ConnectionGene(node, disabled_connection.out_node, self.rng.random(), innov_2)
            new_connections.append(connection_1)
            new_connections.append(connection_2)
        else:
            # random node that is not an output node
            ran_node_1 = self.rng.choice(list(filter(lambda x: x.type is not OUTPUT_NODE, self.nodes)))
            ran_node_2 = self.rng.choice(list(filter(lambda x: x.type is not INPUT_NODE and x.id is not ran_node_1.id, self.nodes)))
            
            innov_1 = self.innovation_db.get_or_create_connection_innovation(ran_node_1.id, node.id)
            innov_2 = self.innovation_db.get_or_create_connection_innovation(node.id, ran_node_2.id)
            connection_1 = ConnectionGene(ran_node_1, node, self.rng.random(), innov_1)
            connection_2 = ConnectionGene(node, ran_node_2, self.rng.random(), innov_2)
            new_connections.append(connection_1)
            new_connections.append(connection_2)
        
        self.nodes.append(node)
        self.connections += new_connections
        print(f'Added node in between nodes {new_connections[0].in_node.id} and {new_connections[1].out_node.id}.')
        
    # taken from the NEAT paper
    # In adding a connection, a single new connection gene is added to the end of the
    # genome and given the next available innovation number.    
    def mutation_add_connection(self):
        max_connections = len(self.nodes) - self.output_nodes_count        
        
        # choose only INPUT/HIDDEN nodes 
        first_nodes = list(filter(lambda x: x.type is not OUTPUT_NODE, self.nodes))
        if len(first_nodes) < 1:
            return
        
        first_choice = self.rng.choice(first_nodes)
        
        # choose only HIDDEN/OUTPUT nodes that did not exceed the total count of connections and are not the first_choice
        second_nodes = list(filter(lambda x: x.type is not INPUT_NODE and len(x.inputs) < max_connections and x.id != first_choice.id, self.nodes))
        
        print("targeted nodes:", [node.id for node in second_nodes])
        if len(second_nodes) < 1:
            return
        
        second_choice = self.rng.choice(second_nodes)
        
        # if successful
        innovation_nr = self.innovation_db.get_or_create_connection_innovation(first_choice.id, second_choice.id)
        connection = ConnectionGene(first_choice, second_choice, self.rng.random(), innovation_nr)
        self.connections.append(connection)
        
    def mutation_change_random_weight(self):
        connection = self.rng.choice(self.connections)
        connection.weight = self.rng.random()
        
    def mutation_change_activation_function(self):
        node = self.rng.choice(self.nodes)
        new_activation_function = self.rng.choice([ReLU(), Sigmoid()]) 
        node.activation_function = new_activation_function
        
    def mutation_change_connection(self):
        connection = self.rng.choice(self.connections)
        connection.is_disabled = not connection.is_disabled
        
        
    def __str__(self):
        node_strs = [str(node) for node in self.nodes]
        conn_strs = [str(conn) for conn in self.connections]
        return f"Nodes ({self.node_count}): [{', '.join(node_strs)}],\n Connections ({self.connection_count}): [{', '.join(conn_strs)}]"
