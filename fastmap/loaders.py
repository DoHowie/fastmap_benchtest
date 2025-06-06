import os
import math

def _load_map(filepath):
    """Load a map from the given filepath and return a 2D grid."""
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    # Parse the header
    type_line = lines[0].strip()
    height_line = lines[1].strip()
    width_line = lines[2].strip()
    map_line = lines[3].strip()
    
    # Extract dimensions
    height = int(height_line.split()[1])
    width = int(width_line.split()[1])
    
    # Extract the grid
    grid = []
    for i in range(4, 4 + height):
        if i < len(lines):
            row = list(lines[i].strip())
            # Pad row if necessary
            while len(row) < width:
                row.append('@')
            grid.append(row)
        else:
            # Add missing rows as out of bounds
            grid.append(['@'] * width)
    
    return grid, width, height

def _is_passable(cell):
    """Check if a cell is passable."""
    terrain_info = {
        '.': True, 
        'G': True, 
        'S': True, 
        'W': True, 
        '@': False, 
        'O': False, 
        'T': False, 
    }
    return terrain_info.get(cell, False)

def can_move_between_terrains(from_terrain, to_terrain):
    """Check if movement is allowed between two terrain types."""
    compatibility = {
        '.': {'.', 'G', 'S'},
        'G': {'.', 'G', 'S'},
        'S': {'.', 'G', 'S'},
        'W': {'W'}, # water can only go to water
        '@': set(),
        'O': set(),
        'T': set(),
    }
    
    allowed = compatibility.get(from_terrain, set())
    return to_terrain in allowed

def _build_graph(grid, width, height):
    """Build a graph from the grid where each cell is connected to its passable neighbors."""
    graph = {}
    
    for y in range(height):
        for x in range(width):
            if passable(grid[y][x]):
                neighbors = []
                current_terrain = grid[y][x]

                directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    
                    # Check bounds
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor_terrain = grid[ny][nx]
                        
                        # Check if neighbor is passable and terrain types are compatible
                        if (passable(neighbor_terrain) and 
                            can_move_between_terrains(current_terrain, neighbor_terrain)):
                            
                            # Check corner cutting for diagonal moves
                            is_diagonal = dx != 0 and dy != 0
                            can_move = True
                            
                            if is_diagonal:
                                adj1_terrain = grid[y][nx] if 0 <= nx < width else '@'
                                adj2_terrain = grid[ny][x] if 0 <= ny < height else '@'

                                if (not passable(adj1_terrain) or 
                                    not passable(adj2_terrain)):
                                    can_move = False

                                elif (not can_move_between_terrains(current_terrain, adj1_terrain) or
                                      not can_move_between_terrains(current_terrain, adj2_terrain)):
                                    can_move = False
                            
                            if can_move:
                                if is_diagonal:
                                    cost = math.sqrt(2)
                                else:
                                    cost = 1.0
                                
                                neighbors.append(((nx, ny), cost))

                graph[(x, y)] = neighbors
    return graph

def load_scen(filepath):
    """Load scenarios from the given filepath."""
    scenarios = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    # Skip the version line
    for line in lines[1:]:
        if line.strip():
            parts = line.strip().split('\t')
            if len(parts) >= 9:
                scenario = {
                    'bucket': int(parts[0]),
                    'map': parts[1],
                    'map_width': int(parts[2]),
                    'map_height': int(parts[3]),
                    'start_x': int(parts[4]),
                    'start_y': int(parts[5]),
                    'goal_x': int(parts[6]),
                    'goal_y': int(parts[7]),
                    'optimal_length': float(parts[8])
                }
                scenarios.append(scenario)
    
    return scenarios

# Compatibility wrappers to rework on less code
def load_map(path):
    """
    Wrapper that keeps the old (grid, H, W) return order.
    Internally calls the new WC3 loader.
    """
    grid, W, H = _load_map(path) # new code returns (grid, width, height)
    return grid, H, W # old callers expect (grid, H, W)

def passable(ch):
    return _is_passable(ch)

def cell_cost(ch):
    return 1.0 if _is_passable(ch) else math.inf

def build_graph(grid):
    H, W = len(grid), len(grid[0])
    raw_G = _build_graph(grid, W, H)
    G = {}
    for (x, y), nbrs in raw_G.items():
        uid = y * W + x
        G[uid] = [(ny * W + nx, w) for (nx, ny), w in nbrs]
    return G, W
