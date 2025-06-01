import math
from .constants import DIRS_8

# ---------------------------------------------------------------------
def passable(ch):
    # DAO/Baldur/StarCraft/etc.: ground '.', 'G', optional swamp 'S'
    # Terrain maps: letters 'A'..'Z' EXCEPT the DAO wall/obstacle chars.
    return ch in ".GSW" or ('A' <= ch <= 'Z' and ch not in "T@O")


def cell_cost(ch: str) -> float:
    if ch in ".G":          return 1.0
    if ch == "S":           return 2.0
    if "A" <= ch <= "Z":    return ord(ch) - ord("A") + 1
    return math.inf

# ---------------------------------------------------------------------
def load_map(path):
    """Parse Moving-AI .map → (grid list, H, W)."""
    with open(path) as f:
        header = [next(f).strip() for _ in range(4)]
        H = int(header[1].split()[1])
        W = int(header[2].split()[1])
        grid = [list(next(f).rstrip()) for _ in range(H)]
    return grid, H, W

def load_scen(path, limit=None):
    """Yield (start_id, goal_id, optimal_len) triples."""
    with open(path) as f:
        next(f)                    # 'version 1'
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            _, _, W, _, sx, sy, gx, gy, opt = line.split()
            W = int(W)
            yield int(sy) * W + int(sx), int(gy) * W + int(gx), float(opt)

# ---------------------------------------------------------------------
def build_graph(grid):
    """ASCII grid ➜ adjacency dict with corner-cut rule enforced."""
    H, W = len(grid), len(grid[0])
    vid  = lambda r, c: r * W + c
    G    = {}

    for r in range(H):
        for c in range(W):
            if not passable(grid[r][c]):
                continue
            u = vid(r, c)
            G[u] = []
            for dr, dc in DIRS_8:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < H and 0 <= nc < W):
                    continue
                if not passable(grid[nr][nc]):
                    continue
                # Corner-cut rule
                # ----- diagonal tests -----
                if dr and dc:
                    # standard corner-cut block
                    if (not passable(grid[r][nc]) or
                        not passable(grid[nr][c])):
                        continue

                    # NEW: forbid “diagonal   cost-change” shortcuts
                    here  = cell_cost(grid[r][c])
                    side1 = cell_cost(grid[r][nc])
                    side2 = cell_cost(grid[nr][c])
                    there = cell_cost(grid[nr][nc])
                    if side1 != here or side2 != here or there != here:
                        # at least one of the four tiles differs in cost
                        continue
                step = math.sqrt(2) if dr and dc else 1.0
                w    = step * (cell_cost(grid[r][c]) + cell_cost(grid[nr][nc])) / 2
                G[u].append((vid(nr, nc), w))
    return G, W
