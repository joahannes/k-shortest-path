# -*- coding: utf-8 -*-
"""
A NetworkX based implementation of Yen's algorithm for computing K-shortest paths.   
Yen's algorithm computes single-source K-shortest loopless paths for a 
graph with non-negative edge cost. For more details, see: 
http://en.m.wikipedia.org/wiki/Yen%27s_algorithm
"""
__author__ = 'Guilherme Maia <guilhermemm@gmail.com>'

__all__ = ['k_shortest_paths']

from heapq import heappush, heappop
from itertools import count

import networkx as nx

def k_shortest_paths(G, source, target, k=1, weight='weight'):
    """Returns the k-shortest paths from source to target in a weighted graph G.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node

    target : node
       Ending node
       
    k : integer, optional (default=1)
        The number of shortest paths to find

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight

    Returns
    -------
    lengths, paths : lists
       Returns a tuple with two lists.
       The first list stores the length of each k-shortest path.
       The second list stores each k-shortest path.  

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    Examples
    --------
    >>> G=nx.complete_graph(5)    
    >>> print(k_shortest_paths(G, 0, 4, 4))
    ([1, 2, 2, 2], [[0, 4], [0, 1, 4], [0, 2, 4], [0, 3, 4]])

    Notes
    ------
    Edge weight attributes must be numerical and non-negative.
    Distances are calculated as sums of weighted edges traversed.

    """
    if source == target:
        return ([0], [[source]]) 
       
    length, path = nx.single_source_dijkstra(G, source, target, weight=weight)
    if target not in length:
        raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))
        
    lengths = [length[target]]
    paths = [path[target]]
    c = count()        
    B = []                        
    G_original = G.copy()    
    
    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):            
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]
            
            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G.has_edge(u, v):
                        edge_attr = G.edge[u][v]
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            
            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                # for u, v, edge_attr in G.edges_iter(node, data=True):
                #     G.remove_edge(u, v)
                #     edges_removed.append((u, v, edge_attr))

                # inicio modificacao Joahannes
                temp_G = []
                temp_edge_attr = []
                for u, v, edge_attr in G.edges_iter(node, data=True):
                    temp_G.append((u,v))
                    temp_edge_attr.append((u, v, edge_attr))
                for temp_remove in temp_G:
                    G.remove_edge(temp_remove[0],temp_remove[1])
                for temp_remove_edge_attr in temp_edge_attr:
                    edges_removed.append((temp_remove_edge_attr[0],temp_remove_edge_attr[1],temp_remove_edge_attr[2]))
                # final modificação Joahannes
                
                if G.is_directed():
                    # in-edges
                    for u, v, edge_attr in G.in_edges_iter(node, data=True):
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            
            spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, target, weight=weight)            
            if target in spur_path and spur_path[target]:
                total_path = root_path[:-1] + spur_path[target]
                total_path_length = get_path_length(G_original, root_path, weight) + spur_path_length[target]                
                heappush(B, (total_path_length, next(c), total_path))
                
            for e in edges_removed:
                u, v, edge_attr = e
                G.add_edge(u, v, edge_attr)
                       
        if B:
            (l, _, p) = heappop(B)        
            lengths.append(l)
            paths.append(p)
        else:
            break
    
    return (lengths, paths)

def get_path_length(G, path, weight='weight'):
    length = 0
    if len(path) > 1:
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            
            length += G.edge[u][v].get(weight, 1)
    
    return length    
    
if __name__ == "__main__":

    G = nx.DiGraph()
    G.add_edge('A', 'B', length=7, weight=7)
    G.add_edge('A', 'C', length=12, weight=12)
    G.add_edge('B', 'C', length=2, weight=2)
    G.add_edge('B', 'D', length=9, weight=9)
    G.add_edge('C', 'E', length=10, weight=10)
    G.add_edge('E', 'D', length=4, weight=4)
    G.add_edge('E', 'F', length=5, weight=5)
    G.add_edge('D', 'F', length=1, weight=1)

    # TESTE DESCONEXAO
    # G.add_edge('G', 'H', length=2, weight=10)

    valor_k = 3

    caminhos = k_shortest_paths(G, 'A', 'F', valor_k, "weight")
    for i in range(len(caminhos[0])):
        print(caminhos[0][i],caminhos[1][i])