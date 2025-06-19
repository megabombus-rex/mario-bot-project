import networkx as nx
import matplotlib.pyplot as plt
from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)
from model.common_genome_data import *

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
    plt.show()
    

def draw_diagrams(mean_scores, mean_runtimes, mean_clearedLines, common_rates:CommonRates, fps_recordered=60):
    # the mean values are corresponding to iterations (ordered)
    iterations = range(1, len(mean_scores) + 1)
    
    fig, (ax_sc, ax_rt, ax_cl)  = plt.subplots(1, 3) 
    
    ax_sc.set(xlabel='Iteration', ylabel='Mean score') 
    ax_sc.set_title('Mean score per iteration')
    
    ax_rt.set(xlabel='Iteration', ylabel='Mean runtime') 
    ax_rt.set_title('Mean runtime per iteration')
    
    ax_cl.set(xlabel='Iteration', ylabel='Mean cleared lines') 
    ax_cl.set_title('Mean cleared lines per iteration')
    
    fig.suptitle(f'Parameters: CxR: {common_rates.crossover_rate}, WMR: {common_rates.weight_mutation_rate}, AFR: {common_rates.activation_mutation_rate}, CAMR: {common_rates.connection_addition_mutation_rate}, NAMR: {common_rates.node_addition_mutation_rate}, SCP: {common_rates.start_connection_probability}, MaxSC: {common_rates.max_start_connection_count}  FPS: {fps_recordered}')
    ax_sc.plot(iterations, mean_scores, 'tab:green')
    ax_rt.plot(iterations, mean_runtimes, 'tab:blue')
    ax_cl.plot(iterations, mean_clearedLines, 'tab:red')