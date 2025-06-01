import math
import numpy as np

def fastmap_L1(emb, a, b):
    ea, eb = emb[a], emb[b]
    return sum(abs(x - y) for x, y in zip(ea, eb))

def octile_heuristic(u, v, width):
    ur, uc = divmod(u, width)
    vr, vc = divmod(v, width)
    dx, dy = abs(uc - vc), abs(ur - vr)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

def grid_aware_heuristic(u, v, emb, width):
    """max{FastMap-L1, Octile} to keep admissibility."""
    return max(
        fastmap_L1(emb, u, v),
        octile_heuristic(u, v, width),
    )
