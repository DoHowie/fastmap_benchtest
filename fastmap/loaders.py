import math
from .constants import DIRS_8

def passable(ch):
    return ch in ".GSW" or ('A' <= ch <= 'Z' and ch not in "T@O")

def cell_cost(ch: str) -> float:
    if ch in ".G":
        return 1.0
    if ch == "S":
        return 2.0
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 1
    return math.inf

def load_map(path):
    with open(path) as f:
        header = [next(f).strip() for _ in range(4)]
        H = int(header[1].split()[1])
        W = int(header[2].split()[1])
        grid = [list(next(f).rstrip()) for _ in range(H)]
    return grid, H, W

def load_scen(path, limit=None):
    with open(path) as f:
        next(f)
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            _, _, W, _, sx, sy, gx, gy, opt = line.split()
            W = int(W)
            yield int(sy) * W + int(sx), int(gy) * W + int(gx), float(opt)

def build_graph(grid):
    # turn the ASCII grid into an adjacency dict
    H, W = len(grid), len(grid[0])
    vid = lambda r, c: r * W + c # vertex id
    G = {} # initialization of graph, list of tuples for all walkable cells

    for r in range(H):
        for c in range(W):
            if not passable(grid[r][c]): # check whether current block is passable
                continue
            u = vid(r, c)
            G[u] = [] # empty neighbor list, max number of elem. = 8
            for dr, dc in DIRS_8:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < H and 0 <= nc < W): # true --> off the map
                    continue
                if not passable(grid[nr][nc]): # target block is not passable
                    continue
                if dr and dc: 
                    # one of the side block is not passable then continue
                    if (not passable(grid[r][nc]) or not passable(grid[nr][c])):
                        continue
                    here  = cell_cost(grid[r][c])
                    side1 = cell_cost(grid[r][nc])
                    side2 = cell_cost(grid[nr][c])
                    there = cell_cost(grid[nr][nc])
                    if side1 != here or side2 != here or there != here: # checking they are all same type of block
                        continue
                step = math.sqrt(2) if dr and dc else 1.0 # geometric distance
                w = step * (cell_cost(grid[r][c]) + cell_cost(grid[nr][nc])) / 2
                G[u].append((vid(nr, nc), w)) # (vertex id, edge weight from G[u] to G[(nr, nc)])
    return G, W
