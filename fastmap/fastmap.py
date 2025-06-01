import heapq, math
import numpy as np
from collections import defaultdict
import random

class FastMap:
    """
    Your original FastMap implementation — unchanged.
    Returns embeddings as dict[node] -> list[float].
    """
    def __init__(self, graph, K=2, epsilon=1e-3):
        self.graph = graph
        self.K = K
        self.epsilon = epsilon
        self.nodes = list(graph.keys())
        self.embeddings = {v: [0.0] * K for v in self.nodes}
        self.edge_weights = {(u, v): w for u in graph for v, w in graph[u]}

    # ------------------ helpers ------------------
    def dijkstra(self, start):
        dist = {v: math.inf for v in self.nodes}
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self.graph[u]:
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], v))
        return dist

    def get_farthest_pair(self):
        """Pick (a, b) that are far apart using two Dijkstras."""
        a = random.choice(self.nodes)       # 1. random seed
        dist_a = self.dijkstra(a)           # 2. one full Dijkstra
        b = max(dist_a, key=dist_a.get)     # 3. farthest from a
        dist_b = self.dijkstra(b)           # 4. second Dijkstra
        a = max(dist_b, key=dist_b.get)     # 5. farthest from b
        return a, b, dist_a, dist_b         # also return the two tables


    # ------------------ main routine -------------
    def compute_embeddings(self):
        for k in range(self.K):
            a, b, dist_a, dist_b = self.get_farthest_pair()
            dab = dist_a[b]
            if dab < self.epsilon:
                break
            for v in self.nodes:
                da, db = dist_a[v], dist_b[v]
                self.embeddings[v][k] = (da + dab - db) / 2

            # L1 projection update
            new_graph = defaultdict(list)
            for u in self.graph:
                for v, w in self.graph[u]:
                    if u < v:
                        diff   = abs(self.embeddings[u][k] - self.embeddings[v][k])
                        new_w  = max(0.0, self.edge_weights[(u, v)] - diff)
                        new_graph[u].append((v, new_w))
                        new_graph[v].append((u, new_w))
                        self.edge_weights[(u, v)] = self.edge_weights[(v, u)] = new_w
            self.graph = new_graph

        return self.embeddings
