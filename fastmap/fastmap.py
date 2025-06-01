import heapq, math, random
from collections import defaultdict
import numpy as np


class FastMap:
    """
    FastMap for graphs.  Returns a dict  node -> [K-dim embedding].
    Works even when the graph has multiple disconnected components.
    """
    def __init__(self, graph, K=2, epsilon=1e-3):
        self.graph     = graph                       # {u: [(v,w), ...]}
        self.K         = K
        self.epsilon   = epsilon
        self.nodes     = list(graph.keys())
        self.embeddings = {v: [0.0] * K for v in self.nodes}
        self.edge_w    = {(u, v): w
                          for u in graph for v, w in graph[u]}

    # ───────────────────────── helpers ──────────────────────────
    def dijkstra(self, start):
        dist = {v: math.inf for v in self.nodes}
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self.graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist

    def _finite_max(self, iterable, key):
        """
        Return the element with maximal key(value) **among those whose key
        is finite**.  If none is finite, return None.
        """
        best, best_val = None, -math.inf
        for x in iterable:
            kx = key(x)
            if math.isfinite(kx) and kx > best_val:
                best, best_val = x, kx
        return best

    def get_farthest_pair(self):
        """
        Choose pivots (a, b) that lie in the same connected component,
        i.e. their distance is finite.  Also return the two distance tables.
        """
        while True:
            a_seed = random.choice(self.nodes)
            dist_a = self.dijkstra(a_seed)
            b = self._finite_max(self.nodes, lambda v: dist_a[v])
            if b is None:           # a_seed was an isolated vertex — try again
                continue
            dist_b = self.dijkstra(b)
            a = self._finite_max(self.nodes, lambda v: dist_b[v])
            if a is None or not math.isfinite(dist_b[a]):
                continue            # a and b not connected — try again
            return a, b, dist_a, dist_b

    # ───────────────────── main routine ────────────────────────
    def compute_embeddings(self):
        for k in range(self.K):
            a, b, dist_a, dist_b = self.get_farthest_pair()
            dab = dist_a[b]
            if dab < self.epsilon:              # exhausted meaningful dims
                break

            finite_coord = set()                # nodes that get a coord here
            for v in self.nodes:
                da, db = dist_a[v], dist_b[v]
                if math.isfinite(da) and math.isfinite(db):
                    self.embeddings[v][k] = (da + dab - db) / 2
                    finite_coord.add(v)         # remember for weight update

            # ---------- project edge weights on new axis ----------
            new_graph = defaultdict(list)
            for u in self.graph:
                for v, w in self.graph[u]:
                    if u < v:                   # handle each undirected edge once
                        if u in finite_coord and v in finite_coord:
                            diff = abs(self.embeddings[u][k]
                                       - self.embeddings[v][k])
                            w = max(0.0, self.edge_w[(u, v)] - diff)
                            self.edge_w[(u, v)] = self.edge_w[(v, u)] = w
                        # keep old weight if one end has no coord this round
                        new_graph[u].append((v, w))
                        new_graph[v].append((u, w))
            self.graph = new_graph

        return self.embeddings
