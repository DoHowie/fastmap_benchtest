import heapq, math

# ---------------- generic A* --------------------
def astar_general(graph, start, goal, h):
    open_   = [(h(start), 0.0, start)]
    g_best  = {start: 0.0}
    while open_:
        f, g, u = heapq.heappop(open_)
        if g != g_best[u]:
            continue
        if u == goal:
            return g
        for v, w in graph[u]:
            ng = g + w
            if ng < g_best.get(v, math.inf):
                g_best[v] = ng
                heapq.heappush(open_, (ng + h(v), ng, v))
    return math.inf

# ---------------- wrappers using your heuristics -------------
from .heuristics import grid_aware_heuristic, octile_heuristic

def improved_astar_with_fastmap(graph, start, goal, emb, width):
    h = lambda n: grid_aware_heuristic(n, goal, emb, width)
    return astar_general(graph, start, goal, h)

def astar_with_octile(graph, start, goal, width):
    h = lambda n: octile_heuristic(n, goal, width)
    return astar_general(graph, start, goal, h)
