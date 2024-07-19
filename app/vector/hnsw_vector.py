from heapq import heapify, heappop, heappush, heapreplace, nlargest, nsmallest
from math import log2
from operator import itemgetter
from random import random

import numpy as np
from app.vector.vector_store import VectorStore

class HNSWVectorStore(VectorStore):
    def __init__(self, space='cosine', dim=128, m=5, ef=200, m0=None, heuristic=True, vectorized=False):
        super().__init__()
        self.space = space
        self.dim = dim
        self._m = m
        self._ef = ef
        self._m0 = 2 * m if m0 is None else m0
        self._level_mult = 1 / log2(m)
        self._select = self._select_heuristic if heuristic else self._select_naive
        
        self.distance_func = self._calculate_similarity

        if vectorized:
            self.distance = self._distance
            self.vectorized_distance = self.distance_func
        else:
            self.distance = self.distance_func
            self.vectorized_distance = self.vectorized_distance_

    def _distance(self, x, y):
        return self.distance_func(x, [y])[0]

    def vectorized_distance_(self, x, ys):
        return [self.distance_func(x, y) for y in ys]

    def add_vector_store(self, store_id: int):
        if store_id not in self.vector_stores:
            self.vector_stores[store_id] = {
                'vector_data': {},                
                'metadata': {},
                'data': [],
                'graphs': [],
                'enter_point': None,
                'vector_ids_aux': {},
            }

    def delete_vector_store(self, store_id: int):
        if store_id in self.vector_stores:
            del self.vector_stores[store_id]

    def get_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            return vector_data.get(vector_id, None)

    def add_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            metadata_store = self.vector_stores[store_id]['metadata']
            if vector_id not in vector_data:
                vector_data[vector_id] = vector
                if metadata:
                    metadata_store[vector_id] = metadata
                self.add(store_id, vector_id, vector)

    def update_vector(self, store_id: int, vector_id: int, new_vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            self.delete_vector(store_id, vector_id)
            self.add_vector(store_id, vector_id, new_vector, metadata)

    def delete_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores and vector_id in self.vector_stores[store_id]['vector_data']:
            del self.vector_stores[store_id]['vector_data'][vector_id]
            if vector_id in self.vector_stores[store_id]['metadata']:
                del self.vector_stores[store_id]['metadata'][vector_id]

    def add(self, store_id: int, vector_id: int, vector: list[float]):
        ef = self._ef

        distance = self.distance
        data = self.vector_stores[store_id]['data']
        graphs = self.vector_stores[store_id]['graphs']
        point = self.vector_stores[store_id]['enter_point']
        m = self._m

        level = int(-log2(random()) * self._level_mult) + 1
        idx = len(data)
        self.vector_stores[store_id]['vector_ids_aux'][idx] = vector_id #save real vector_id
        data.append(vector)

        if point is not None:
            dist = distance(vector, data[point])            
            for layer in reversed(graphs[level:]):
                point, dist = self._search_graph_ef1(vector, point, dist, layer, data)
            ep = [(-dist, point)]
            layer0 = graphs[0]            
            for layer in reversed(graphs[:level]):
                level_m = m if layer is not layer0 else self._m0
                ep = self._search_graph(vector, ep, layer, ef, data)
                layer[idx] = layer_idx = {}
                self._select(layer_idx, ep, level_m, layer, heap=True)
                for j, dist in layer_idx.items():
                    self._select(layer[j], (idx, dist), level_m, layer)
        for i in range(len(graphs), level):
            graphs.append({idx: {}})
            self.vector_stores[store_id]['enter_point'] = idx

    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None, space: str = 'cosine'):
        if store_id not in self.vector_stores:
            return []
    
        metadata = self.vector_stores[store_id]['metadata']        
        data = self.vector_stores[store_id]['data']
        graphs = self.vector_stores[store_id]['graphs']
        enter_point = self.vector_stores[store_id]['enter_point']
        vector_ids_aux = self.vector_stores[store_id]['vector_ids_aux']

        if enter_point is None:
            raise ValueError("Empty graph")

        dist = self.distance(query_vector, data[enter_point])
        
        # look for the closest neighbor from the top to the 2nd level
        for layer in reversed(graphs[1:]):
            enter_point, dist = self._search_graph_ef1(query_vector, enter_point, dist, layer, data)            

        # look for ef neighbors in the bottom level
        ep = self._search_graph(query_vector, [(-dist, enter_point)], graphs[0], self._ef, data)        

        if metadata_filter:
            ep = [(idx, md) for md, idx in ep if self._metadata_matches(metadata[idx], metadata_filter)]

        ep.sort()
        ep = ep[:num_results]
        return [(vector_ids_aux[idx], -md) for md, idx in ep]
    

    def _search_graph_ef1(self, q, entry, dist, layer, data):
        vectorized_distance = self.vectorized_distance

        best = entry
        best_dist = dist
        candidates = [(dist, entry)]
        visited = set([entry])

        while candidates:
            dist, c = heappop(candidates)
            if dist > best_dist:
                break
            edges = [e for e in layer[c] if e not in visited]
            visited.update(edges)
            dists = vectorized_distance(q, [data[e] for e in edges])
            for e, dist in zip(edges, dists):
                if dist < best_dist:
                    best = e
                    best_dist = dist
                    heappush(candidates, (dist, e))

        return best, best_dist

    def _search_graph(self, q, ep, layer, ef, data):
        vectorized_distance = self.vectorized_distance

        candidates = [(-mdist, p) for mdist, p in ep]
        heapify(candidates)
        visited = set(p for _, p in ep)

        while candidates:
            dist, c = heappop(candidates)
            mref = ep[0][0]
            if dist > -mref:
                break

            edges = [e for e in layer[c] if e not in visited]
            visited.update(edges)
            dists = vectorized_distance(q, [data[e] for e in edges])
            for e, dist in zip(edges, dists):
                mdist = -dist
                if len(ep) < ef:
                    heappush(candidates, (dist, e))
                    heappush(ep, (mdist, e))
                    mref = ep[0][0]
                elif mdist > mref:
                    heappush(candidates, (dist, e))
                    heapreplace(ep, (mdist, e))
                    mref = ep[0][0]

        return ep

    def _select_naive(self, d, to_insert, m, layer, heap=False):
        if not heap:
            idx, dist = to_insert
            assert idx not in d
            if len(d) < m:
                d[idx] = dist
            else:
                max_idx, max_dist = max(d.items(), key=itemgetter(1))
                if dist < max_dist:
                    del d[max_idx]
                    d[idx] = dist
            return

        assert not any(idx in d for _, idx in to_insert)
        to_insert = nlargest(m, to_insert)
        unchecked = m - len(d)
        assert 0 <= unchecked <= m
        to_insert, checked_ins = to_insert[:unchecked], to_insert[unchecked:]
        to_check = len(checked_ins)
        if to_check > 0:
            checked_del = nlargest(to_check, d.items(), key=itemgetter(1))
        else:
            checked_del = []
        for md, idx in to_insert:
            d[idx] = -md
        zipped = zip(checked_ins, checked_del)
        for (md_new, idx_new), (idx_old, d_old) in zipped:
            if d_old <= -md_new:
                break
            del d[idx_old]
            d[idx_new] = -md_new
            assert len(d) == m

    def _select_heuristic(self, d, to_insert, m, g, heap=False):
        nb_dicts = [g[idx] for idx in d]

        def prioritize(idx, dist):
            return any(nd.get(idx, float('inf')) < dist for nd in nb_dicts), dist, idx

        if not heap:
            idx, dist = to_insert
            to_insert = [prioritize(idx, dist)]
        else:
            to_insert = nsmallest(m, (prioritize(idx, -mdist) for mdist, idx in to_insert))

        assert len(to_insert) > 0
        assert not any(idx in d for _, _, idx in to_insert)

        unchecked = m - len(d)
        assert 0 <= unchecked <= m
        to_insert, checked_ins = to_insert[:unchecked], to_insert[unchecked:]
        to_check = len(checked_ins)
        if to_check > 0:
            checked_del = nlargest(to_check, (prioritize(idx, dist) for idx, dist in d.items()))
        else:
            checked_del = []
        for _, dist, idx in to_insert:
            d[idx] = dist
        zipped = zip(checked_ins, checked_del)
        for (p_new, d_new, idx_new), (p_old, d_old, idx_old) in zipped:
            if (p_old, d_old) <= (p_new, d_new):
                break
            del d[idx_old]
            d[idx_new] = d_new
            assert len(d) == m
