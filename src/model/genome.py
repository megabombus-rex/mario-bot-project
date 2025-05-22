from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.activation_functions import *
from model.common_genome_data import *
import random

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
    def __init__(self):
        self.connections = []
        self.nodes = []
        self.innovation_count = 0
        self.node_count = 0
        self.connection_history = {}  # (from_id, to_id): innovation_number
        
    def get_next_innovation_count(self):
        return self.innovation_count + 1
        
    def increment_innovation_count(self):
        self.innovation_count += 1

    def get_next_node_id(self):
        return self.node_count + 1
        
    def increment_node_count(self):
        self.node_count += 1

    # maybe try add connections, for possible conflicts
    def add_connection_to_connection_genes(self, gene:ConnectionGene):
        self.connections.add(gene)        

    # maybe try add nodes, for possible conflicts
    def add_node_to_node_genes(self, gene:NodeGene):
        self.nodes.add(gene)        

class Genome:
    # inputs -> outputs -> new_nodes
    def __init__(self, nodes:list, connections:list, input_nodes_count:int, output_nodes_count:int, innovation_db:InnovationDatabase, common_rates:CommonRates):
        self.nodes = nodes
        self.connections = connections
        self.node_count = len(self.nodes)
        self.connection_count = len(self.connections)
        self.size = self.node_count + self.connection_count
        self.input_nodes_count = input_nodes_count
        self.output_nodes_count = output_nodes_count
        self.innovation_db = innovation_db
        self.common_rates = common_rates
        innovation_db.node_count = len(nodes) 
        
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
        node_id = self.innovation_db.get_next_node_id()
        
        activation_function = random.choice([ReLU(), Sigmoid()])
        node = NodeGene(node_id, HIDDEN_NODE, activation_function)
        
        disabled_connection = None
        
        if self.connections: 
            disabled_connection = random.choice(self.connections)
            disabled_connection.is_disabled = True
        
        new_connections = []
        
        inn = self.innovation_db.get_next_innovation_count()
        
        if disabled_connection is not None:
            connection_1 = ConnectionGene(disabled_connection.in_node, node, random.random(), inn)
            connection_2 = ConnectionGene(node, disabled_connection.out_node, random.random(), inn + 1)
            new_connections.append(connection_1)
            new_connections.append(connection_2)
            print(f"Selected node {disabled_connection.in_node.id} as input, {disabled_connection.out_node.id} as output, current node is {node.id}.")
        else:
            # random node that is not an output node
            first_list = list(filter(lambda x: x.type is not OUTPUT_NODE, self.nodes))
            ran_node_1 = random.choice(first_list)
            second_list = list(filter(lambda x: x.type is not INPUT_NODE and x.id is not ran_node_1.id, self.nodes))
            ran_node_2 = random.choice(second_list)
            print(f"Selected node {ran_node_1.id} as input, {ran_node_2.id} as output, current node is {node.id}.")
            connection_1 = ConnectionGene(ran_node_1, node, random.random(), inn)
            connection_2 = ConnectionGene(node, ran_node_2, random.random(), inn + 1)
            new_connections.append(connection_1)
            new_connections.append(connection_2)

        
        # if successful
        self.nodes.append(node)
        self.innovation_db.add_node_to_node_genes(node)
        self.innovation_db.add_connection_to_connection_genes(new_connections[0])
        self.innovation_db.add_connection_to_connection_genes(new_connections[1])
        self.connections += new_connections
        self.node_count += 1
        self.size += 1
        self.innovation_db.increment_innovation_count()
        self.innovation_db.increment_innovation_count()
        self.innovation_db.increment_node_count()
        print(f'Added node in between nodes {new_connections[0].in_node.id} and {new_connections[1].out_node.id}.')
        
    # taken from the NEAT paper
    # In adding a connection, a single new connection gene is added to the end of the
    # genome and given the next available innovation number.    
    def mutation_add_connection(self):
        innovation_nr = self.innovation_db.get_next_innovation_count()
        max_connections = self.node_count - self.output_nodes_count        
        
        # choose only INPUT/HIDDEN nodes 
        first_nodes = list(filter(lambda x: x.type is not OUTPUT_NODE, self.nodes))
        if len(first_nodes) < 1:
            return
        
        first_choice = random.choice(first_nodes)
        
        # choose only HIDDEN/OUTPUT nodes that did not exceed the total count of connections and are not the first_choice
        second_nodes = list(filter(lambda x: x.type is not INPUT_NODE & len(x.inputs) < max_connections & x.id is not first_choice.id, self.nodes))
        if len(second_nodes) < 1:
            return
        
        second_choice = random.choice(second_nodes)
        
        # if successful
        connection = ConnectionGene(first_choice, second_choice, random.random(), innovation_nr)
        self.connections.append(connection)
        self.innovation_db.add_connection_to_connection_genes(connection)
        self.connection_count += 1
        self.size += 1
        self.innovation_db.increment_innovation_count()
        
    def mutation_change_random_weight(self):
        connection = random.choice(self.connections)
        connection.weight = random.random()
        
    def mutation_change_activation_function(self):
        node = random.choice(self.nodes)
        new_activation_function = random.choice(ReLU(), Sigmoid()) 
        node.activation_function = new_activation_function
        
    def mutation_change_connection(self):
        connection = random.choice(self.connections)
        connection.is_disabled = not connection.is_disabled
        
        
    def __str__(self):
        node_strs = [str(node) for node in self.nodes]
        conn_strs = [str(conn) for conn in self.connections]
        return f"Nodes ({self.node_count}): [{', '.join(node_strs)}],\n Connections ({self.connection_count}): [{', '.join(conn_strs)}]"
