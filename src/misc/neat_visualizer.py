import pygame
import math
from model.model_constants import INPUT_NODE, OUTPUT_NODE, HIDDEN_NODE

class NEATVisualizer:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 16)
        self.title_font = pygame.font.Font(None, 24)
        
        self.colors = {
            INPUT_NODE: (100, 200, 100),# green
            OUTPUT_NODE: (200, 100, 100),# red
            HIDDEN_NODE: (100, 100, 200),# blue
        }
        
        self.node_radius = 15
        self.connection_width = 2
        
    def draw_network(self, screen, model):
        if not model or not model.genome:
            return
            
        pygame.draw.rect(screen, (40, 40, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), 2)
        
        title_text = self.title_font.render("NEAT Network", True, (255, 255, 255))
        screen.blit(title_text, (self.x + 10, self.y + 10))
        
        node_positions = self._calculate_node_positions(model.genome.nodes)
        
        self._draw_connections(screen, model.genome.connections, node_positions)
        self._draw_nodes(screen, model.genome.nodes, node_positions)
        
        self._draw_stats(screen, model)
        
    def _calculate_node_positions(self, nodes):
        positions = {}
        
        input_nodes = [n for n in nodes if n.type == INPUT_NODE]
        output_nodes = [n for n in nodes if n.type == OUTPUT_NODE]
        hidden_nodes = [n for n in nodes if n.type == HIDDEN_NODE]
        
        if input_nodes:
            input_spacing = (self.height - 100) / max(1, len(input_nodes) - 1) if len(input_nodes) > 1 else 0
            for i, node in enumerate(input_nodes):
                y_pos = self.y + 60 + i * input_spacing if len(input_nodes) > 1 else self.y + self.height // 2
                positions[node.id] = (self.x + 40, y_pos)
        
        if output_nodes:
            output_spacing = (self.height - 100) / max(1, len(output_nodes) - 1) if len(output_nodes) > 1 else 0
            for i, node in enumerate(output_nodes):
                y_pos = self.y + 60 + i * output_spacing if len(output_nodes) > 1 else self.y + self.height // 2
                positions[node.id] = (self.x + self.width - 40, y_pos)
        
        if hidden_nodes:
            layers = self._organize_hidden_layers(hidden_nodes, input_nodes, output_nodes)
            layer_width = (self.width - 120) / max(1, len(layers))
            
            for layer_idx, layer_nodes in enumerate(layers):
                x_pos = self.x + 70 + layer_idx * layer_width
                node_spacing = (self.height - 100) / max(1, len(layer_nodes) - 1) if len(layer_nodes) > 1 else 0
                
                for i, node in enumerate(layer_nodes):
                    y_pos = self.y + 60 + i * node_spacing if len(layer_nodes) > 1 else self.y + self.height // 2
                    positions[node.id] = (x_pos, y_pos)
        
        return positions
    
    def _organize_hidden_layers(self, hidden_nodes, input_nodes, output_nodes):
        layers = []
        
        if hidden_nodes:
            layers.append(hidden_nodes)
        
        return layers
    
    def _draw_connections(self, screen, connections, node_positions):
        for connection in connections:
            if connection.is_disabled:
                continue
                
            start_pos = node_positions.get(connection.in_node.id)
            end_pos = node_positions.get(connection.out_node.id)
            
            if start_pos and end_pos:
                weight = connection.weight
                if weight > 0:
                    color = (0, int(min(255, abs(weight) * 255)), 0)  # Green
                else:
                    color = (int(min(255, abs(weight) * 255)), 0, 0)  # Red
                
                pygame.draw.line(screen, color, start_pos, end_pos, self.connection_width)
                
                mid_x = (start_pos[0] + end_pos[0]) // 2
                mid_y = (start_pos[1] + end_pos[1]) // 2
                weight_text = self.font.render(f"{weight:.2f}", True, (255, 255, 255))
                text_rect = weight_text.get_rect(center=(mid_x, mid_y))
                
                pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 2))
                screen.blit(weight_text, text_rect)
    
    def _draw_nodes(self, screen, nodes, node_positions):
        for node in nodes:
            pos = node_positions.get(node.id)
            if not pos:
                continue
                
            color = self.colors.get(node.type, (128, 128, 128))
            
            pygame.draw.circle(screen, color, pos, self.node_radius)
            pygame.draw.circle(screen, (255, 255, 255), pos, self.node_radius, 2)
            
            id_text = self.font.render(str(node.id), True, (255, 255, 255))
            id_rect = id_text.get_rect(center=pos)
            screen.blit(id_text, id_rect)
            
            if hasattr(node, 'output') and node.output is not None:
                output_text = self.font.render(f"{node.output:.2f}", True, (255, 255, 255))
                screen.blit(output_text, (pos[0] - 20, pos[1] + self.node_radius + 5))
    
    def _draw_stats(self, screen, model):
        stats_y = self.y + self.height - 80
        
        node_count = len(model.genome.nodes)
        connection_count = len([c for c in model.genome.connections if not c.is_disabled])
        
        stats = [
            f"Nodes: {node_count}",
            f"Connections: {connection_count}",
            f"Fitness: {getattr(model, 'fitness', 0):.2f}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, (255, 255, 255))
            screen.blit(stat_text, (self.x + 10, stats_y + i * 20))
