from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.activation_functions import *
from model.common_genome_data import *
import numpy as np
import copy

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
    def __init__(self, nodes:list, connections:list, input_nodes_count:int, output_nodes_count:int, innovation_db:InnovationDatabase, rng:np.random, common_rates:CommonRates):
        self.nodes = nodes
        self.connections = connections
        self.input_nodes_count = input_nodes_count
        self.output_nodes_count = output_nodes_count
        self.innovation_db = innovation_db
        self.rng = rng
        self.common_rates = common_rates
        
        self.node_map = {node.id: node for node in self.nodes}
        for node in self.nodes:
            node.inputs = []

        for connection in self.connections:
            if not connection.is_disabled:
                end_node = self.node_map.get(connection.out_node.id)
                if end_node:
                    end_node.inputs.append(connection)

    def copy(self):
        return copy.deepcopy(self)

    def crossover(self, other:'Genome', fitness_self:float, fitness_other:float) -> 'Genome':
        if fitness_self >= fitness_other:
            parent1, parent2 = self, other
        else:
            parent1, parent2 = other, self

        child_nodes_map = {}
        for n in parent1.nodes:
            child_nodes_map[n.id] = NodeGene(n.id, n.type, n.activation_function)
        for n in parent2.nodes:
            if n.id not in child_nodes_map:
                child_nodes_map[n.id] = NodeGene(n.id, n.type, n.activation_function)

        child_connections = []

        conn_dict1 = {conn.innovation_number: conn for conn in parent1.connections}
        conn_dict2 = {conn.innovation_number: conn for conn in parent2.connections}

        all_innovations = set(conn_dict1.keys()).union(conn_dict2.keys())

        for innovation in sorted(all_innovations):
            gene1 = conn_dict1.get(innovation)
            gene2 = conn_dict2.get(innovation)

            chosen_gene = None
            if gene1 and gene2:  # Matching gene
                chosen_gene = self.rng.choice([gene1, gene2])
            elif gene1:  # Disjoint or excess from the fitter parent
                chosen_gene = gene1
            #elif gene2: # Disjoint or excess from the LESS fit parent
            #    continue
        
            if chosen_gene:
                if (chosen_gene.in_node.id not in child_nodes_map or chosen_gene.out_node.id not in child_nodes_map):
                    continue  # Skip this connection if nodes don't exist
                
                in_node = child_nodes_map[chosen_gene.in_node.id]
                out_node = child_nodes_map[chosen_gene.out_node.id]
                new_conn = ConnectionGene(in_node, out_node, chosen_gene.weight, chosen_gene.innovation_number)
            
                if gene1 and gene2:
                    new_conn.is_disabled = (gene1.is_disabled or gene2.is_disabled) and self.rng.random() < 0.75
                else:
                    new_conn.is_disabled = chosen_gene.is_disabled

                child_connections.append(new_conn)

        child = Genome(
            nodes=list(child_nodes_map.values()),
            connections=child_connections,
            input_nodes_count=self.input_nodes_count,
            output_nodes_count=self.output_nodes_count,
            innovation_db=self.innovation_db,
            rng=self.rng,
            common_rates=self.common_rates
        )
        return child

    # taken from the NEAT paper
    # In adding a new node, 
    # the connection gene being split is disabled, and two new connection genes are added to the
    # end the genome. The new node is between the two new connections. A new node gene
    # representing this new node is added to the genome as well.
    def mutation_add_node(self):
        
        enabled_connections = [conn for conn in self.connections if not conn.is_disabled]
    
        if not enabled_connections:
            return
        
        connection_to_split = self.rng.choice(enabled_connections)
        node_id = self.innovation_db.get_or_create_node_id(connection_to_split.innovation_number)
        connection_to_split.is_disabled = True
                    
        #activation_function = self.rng.choice([ReLU(), Sigmoid()])
        activation_function = Sigmoid()
        new_node = NodeGene(node_id, HIDDEN_NODE, activation_function)
        
        innov_1 = self.innovation_db.get_or_create_connection_innovation(connection_to_split.in_node.id, new_node.id)
        innov_2 = self.innovation_db.get_or_create_connection_innovation(new_node.id, connection_to_split.out_node.id)
        connection_1 = ConnectionGene(connection_to_split.in_node, new_node, 1.0, innov_1)
        connection_2 = ConnectionGene(new_node, connection_to_split.out_node, connection_to_split.weight, innov_2)
        
        self.nodes.append(new_node)
        self.connections.extend([connection_1, connection_2])
        #print(f'Added node in between nodes {new_connections[0].in_node.id} and {new_connections[1].out_node.id}.')
        
    # taken from the NEAT paper
    # In adding a connection, a single new connection gene is added to the end of the
    # genome and given the next available innovation number.    
    def mutation_add_connection(self):
        source_nodes = [node for node in self.nodes if node.type != OUTPUT_NODE]
        if not source_nodes:
            return
        
        target_nodes = [node for node in self.nodes if node.type != INPUT_NODE]
        if not target_nodes:
            return
        
        max_attempts = 20
        for _ in range(max_attempts):
            source_node = self.rng.choice(source_nodes)
            target_node = self.rng.choice(target_nodes)
            
            if source_node.id == target_node.id:
                continue
                
            existing_connection = any(conn.in_node.id == source_node.id and conn.out_node.id == target_node.id for conn in self.connections)
            if existing_connection:
                continue
                
            if self._would_create_cycle(source_node, target_node):
                continue
            
            innovation_nr = self.innovation_db.get_or_create_connection_innovation(source_node.id, target_node.id)
            connection = ConnectionGene(source_node, target_node, self.rng.uniform(-1, 1), innovation_nr)
            self.connections.append(connection)
            return
        return
        
    def _would_create_cycle(self, source_node, target_node):
        if source_node.type == INPUT_NODE and target_node.type == OUTPUT_NODE:
            return False  # Input -> Output can't create cycle
        if source_node.type == target_node.type == OUTPUT_NODE:
            return True   # Output -> Output would be a cycle
        # Add more sophisticated logic if needed
        return False
        
    def mutation_change_random_weight(self):
        if not self.connections:
            return
        connection = self.rng.choice(self.connections)
        connection.weight = self.rng.uniform(-1, 1)
        
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
