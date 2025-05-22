import networkx as nx
import matplotlib.pyplot as plt
from model.model_constants import (INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE)

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