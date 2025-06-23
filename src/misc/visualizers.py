import networkx as nx
import matplotlib.pyplot as plt
from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.common_genome_data import *

""" def visualize_phenotype(genome, title="Phenotype Visualization"):
    G = nx.DiGraph()

    # Define node colors by type
    node_colors = []
    labels = {}
    pos = {}
    
    type_map = {
    0: ("INPUT", "skyblue"),
    1: ("HIDDEN", "lightgray"),
    2: ("OUTPUT", "salmon")
    }

    # Assign x positions by layer/type for clean layout

    for node in genome.nodes:
        node_id = node.id
        node_type = getattr(node, 'type', 1)

        node_label, node_color = type_map.get(node_type, ("HIDDEN", "gray"))

        if node_id not in G:
            G.add_node(node_id)

            node_colors.append(node_color)
            labels[node_id] = f"{node_label[0]}{node_id}"

            # Basic layout: INPUT (x=0), HIDDEN (x=1), OUTPUT (x=2)
            x = node_type
            y = -node_id  # Simple vertical stacking
            pos[node_id] = (x, y)

    # Add connections
    for conn in genome.connections:
        if conn.is_disabled:
            continue  # skip disabled connections

        in_id = conn.in_node.id
        out_id = conn.out_node.id
        weight = conn.weight

        G.add_edge(in_id, out_id, weight=round(weight, 2))

    edge_labels = nx.get_edge_attributes(G, 'weight')

    # Draw the graph
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, labels=labels,
            node_color=node_colors, node_size=800,
            edge_color='black', arrows=True, font_weight='bold')

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show() """
    
def visualize_phenotype(genome, title="Phenotype Visualization"):
    G = nx.DiGraph()

    # Define node colors by type
    node_colors = []
    labels = {}
    pos = {}
    
    type_map = {
        0: ("INPUT", "skyblue"),
        1: ("HIDDEN", "lightgray"),
        2: ("OUTPUT", "salmon")
    }

    # First pass: add all nodes to the graph
    node_types = {}
    for node in genome.nodes:
        node_id = node.id
        node_type = getattr(node, 'type', 1)
        node_types[node_id] = node_type
        
        if node_id not in G:
            G.add_node(node_id)

    # Add connections
    for conn in genome.connections:
        if conn.is_disabled:
            continue
        
        in_id = conn.in_node.id
        out_id = conn.out_node.id
        weight = conn.weight
        
        G.add_edge(in_id, out_id, weight=round(weight, 2))

    # Calculate layers using topological sorting
    def calculate_layers():
        layers = {}
        
        # Start with input nodes at layer 0
        input_nodes = [node_id for node_id, node_type in node_types.items() if node_type == 0]
        output_nodes = [node_id for node_id, node_type in node_types.items() if node_type == 2]
        all_nodes = set(node_types.keys())
        
        # Initialize input nodes
        for node_id in input_nodes:
            layers[node_id] = 0
        
        # Use modified BFS to assign layers
        queue = input_nodes.copy()
        visited = set(input_nodes)
        
        while queue:
            current = queue.pop(0)
            current_layer = layers[current]
            
            # Check all successors
            for successor in G.successors(current):
                if successor not in layers:
                    layers[successor] = current_layer + 1
                else:
                    # Update layer if we found a longer path
                    layers[successor] = max(layers[successor], current_layer + 1)
                
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)
        
        # Handle any unvisited nodes (isolated or disconnected)
        unvisited = all_nodes - set(layers.keys())
        if unvisited:
            # Place isolated input nodes at layer 0
            for node_id in unvisited:
                if node_types[node_id] == 0:  # Input node
                    layers[node_id] = 0
            
            # Place isolated output nodes at final layer
            max_layer = max(layers.values()) if layers else 0
            for node_id in unvisited:
                if node_types[node_id] == 2:  # Output node
                    layers[node_id] = max_layer + 1
            
            # Place remaining isolated hidden nodes at middle layer
            for node_id in unvisited:
                if node_types[node_id] == 1:  # Hidden node
                    layers[node_id] = max_layer // 2 if max_layer > 0 else 1
        
        # Ensure output nodes are in the final layer
        if output_nodes and layers:
            max_layer = max(layers.values())
            for node_id in output_nodes:
                if node_id in layers:
                    layers[node_id] = max(layers[node_id], max_layer)
                else:
                    layers[node_id] = max_layer
        
        return layers

    # Calculate node layers
    node_layers = calculate_layers()
    
    # Group nodes by layer for better vertical positioning
    layers_dict = {}
    for node_id, layer in node_layers.items():
        if layer not in layers_dict:
            layers_dict[layer] = []
        layers_dict[layer].append(node_id)
    
    # Position nodes
    layer_width = 3.0  # Horizontal spacing between layers
    node_spacing = 1.5  # Vertical spacing between nodes in same layer
    
    for layer_num, nodes_in_layer in layers_dict.items():
        num_nodes = len(nodes_in_layer)
        
        # Center nodes vertically in each layer
        start_y = -(num_nodes - 1) * node_spacing / 2
        
        for i, node_id in enumerate(sorted(nodes_in_layer)):
            node_type = node_types[node_id]
            node_label, node_color = type_map.get(node_type, ("HIDDEN", "gray"))
            
            # Position
            x = layer_num * layer_width
            y = start_y + i * node_spacing
            pos[node_id] = (x, y)
            
            # Styling
            node_colors.append(node_color)
            labels[node_id] = f"{node_label[0]}{node_id}"

    # Ensure all nodes have positions (safety check)
    for node_id in G.nodes():
        if node_id not in pos:
            print(f"Warning: Node {node_id} has no position, placing at origin")
            pos[node_id] = (0, 0)
            node_type = node_types.get(node_id, 1)
            node_label, node_color = type_map.get(node_type, ("HIDDEN", "gray"))
            node_colors.append(node_color)
            labels[node_id] = f"{node_label[0]}{node_id}"

    # Get edge attributes
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    # Create edge colors based on weight (positive = green, negative = red)
    edge_colors = []
    for edge in G.edges():
        weight = G[edge[0]][edge[1]]['weight']
        if weight > 0:
            edge_colors.append('green')
        elif weight < 0:
            edge_colors.append('red')
        else:
            edge_colors.append('gray')

    # Draw the graph
    plt.figure(figsize=(max(12, len(layers_dict) * 3), 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, alpha=0.9)
    
    # Draw edges with colors
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, 
                          arrowsize=20, width=2, alpha=0.7, connectionstyle="arc3,rad=0.1")
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    # Draw edge labels (weights)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
    
    # Add layer labels
    for layer_num in layers_dict.keys():
        plt.text(layer_num * layer_width, max(pos.values(), key=lambda x: x[1])[1] + 1, 
                f'Layer {layer_num}', ha='center', fontsize=12, fontweight='bold')
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('off')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markersize=10, label='Input'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgray', markersize=10, label='Hidden'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='salmon', markersize=10, label='Output'),
        plt.Line2D([0], [0], color='green', linewidth=2, label='Positive Weight'),
        plt.Line2D([0], [0], color='red', linewidth=2, label='Negative Weight')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    # Print layer information
    print(f"\nNetwork Structure:")
    for layer_num in sorted(layers_dict.keys()):
        nodes_info = []
        for node_id in sorted(layers_dict[layer_num]):
            node_type = node_types[node_id]
            type_name = type_map[node_type][0]
            nodes_info.append(f"{type_name}{node_id}")
        print(f"Layer {layer_num}: {', '.join(nodes_info)}")
    

def draw_diagrams(generations, mean_scores, mean_runtimes, mean_clearedLines, best_fitness, pop_size, common_rates:CommonRates, max_lines, iteration_lines, fps_recordered=60, pruning_enabled: bool=False):
    # the mean values are corresponding to iterations (ordered)
    iterations = range(1, len(mean_scores) + 1)
    fig, (ax_sc, ax_rt, ax_cl, ax_sc_rt)  = plt.subplots(1, 4, figsize=(18, 18))
    
    ax_sc.set(xlabel='Iteration', ylabel='Mean score') 
    ax_sc.set_title('Mean score per iteration')
    
    ax_rt.set(xlabel='Iteration', ylabel='Mean runtime') 
    ax_rt.set_title('Mean runtime per iteration')
    
    ax_cl.set(xlabel='Iteration', ylabel='Mean cleared lines') 
    ax_cl.set_title('Mean cleared lines per iteration')
    
    ax_sc_rt.set(xlabel='Runtime', ylabel='Score') 
    ax_sc_rt.set_title('Runtime vs Score (mean)')
    
    fig.suptitle(f'Parameters: CxR: {common_rates.crossover_rate}, WMR: {common_rates.weight_mutation_rate}, AFR: {common_rates.activation_mutation_rate}, CAMR: {common_rates.connection_addition_mutation_rate}, NAMR: {common_rates.node_addition_mutation_rate}, SCP: {common_rates.start_connection_probability}, MaxSC: {common_rates.max_start_connection_count}  FPS: {fps_recordered}, Best fitness: {best_fitness}, Max lines: {max_lines} at iteration {iteration_lines}')
    ax_sc.plot(iterations, mean_scores, 'tab:green')
    ax_rt.plot(iterations, mean_runtimes, 'tab:blue')
    ax_cl.plot(iterations, mean_clearedLines, 'tab:red')
    ax_sc_rt.scatter(mean_runtimes, mean_scores, c='tab:orange')
    fig.savefig(f'results/It_{generations}_pop{pop_size}_CxR{common_rates.crossover_rate}_WMR{common_rates.weight_mutation_rate}_AFR{common_rates.activation_mutation_rate}_CAMR{common_rates.connection_addition_mutation_rate}_NAMR{common_rates.node_addition_mutation_rate}_SCP{common_rates.start_connection_probability}_MaxSC_{common_rates.max_start_connection_count}_{'p' if pruning_enabled else 'np'}.png')
    plt.close()
    #plt.scatter(mean_runtimes, mean_scores)
    #plt.xlabel('Mean runtime')
    #plt.ylabel('Mean score')
    #plt.title(f'Parameters: CxR: {common_rates.crossover_rate}, WMR: {common_rates.weight_mutation_rate}, AFR: {common_rates.activation_mutation_rate}, CAMR: {common_rates.connection_addition_mutation_rate}, NAMR: {common_rates.node_addition_mutation_rate}, SCP: {common_rates.start_connection_probability}, MaxSC: {common_rates.max_start_connection_count}  FPS: {fps_recordered}, Best fitness: {best_fitness}')
    #plt.show()
    
    #plt.savefig(f'It_{len(mean_scores)}_pop{pop_size}_CxR{common_rates.crossover_rate}_WMR{common_rates.weight_mutation_rate}_AFR{common_rates.activation_mutation_rate}_CAMR{common_rates.connection_addition_mutation_rate}_NAMR{common_rates.node_addition_mutation_rate}_SCP{common_rates.start_connection_probability}_MaxSC_{common_rates.max_start_connection_count}_rt_vs_sc.png')