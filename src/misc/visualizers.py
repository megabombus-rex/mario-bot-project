import networkx as nx
import matplotlib.pyplot as plt
from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)

def visualize_phenotype(genome, title="Phenotype Visualization"):
    G = nx.DiGraph()

    # Define node colors by type
    node_colors = []
    labels = {}
    pos = {}

    # Assign x positions by layer/type for clean layout
    layer_map = {INPUT_NODE: 0, OUTPUT_NODE: 1, HIDDEN_NODE: 2}

    for node in genome.nodes:
        node_id = node.id
        node_type = getattr(node, 'type', 1)

        # Add node to graph
        G.add_node(node_id)
        labels[node_id] = f"{layer_map[node_type]}{node_id}"

        # Color by node type
        if node_type == INPUT_NODE:
            node_colors.append('skyblue')
        elif node_type == OUTPUT_NODE:
            node_colors.append('salmon')
        else:
            node_colors.append('lightgray')

        # Simple horizontal layer-based positioning
        x = layer_map.get(node_type, 1)
        y = -node_id  # stack vertically
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