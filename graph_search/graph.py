class Graph:
    def __init__(self, graph_dict=None):
        if graph_dict is None:
            graph_dict = {}
        self._graph_dict = graph_dict

    def find_path(self, start_vertex, end_vertex, path=None, long_path=True):
        if path is None:
            path = []
        path = path + [start_vertex]
        if start_vertex == end_vertex and not (long_path and len(path) == 1):
            return path
        shortest = None
        for node in self._graph_dict[start_vertex]:
            if node not in path or path.index(node) == 0:
                new_path = self.find_path(node, end_vertex, path, long_path)
                if new_path and (not shortest or len(new_path) < len(shortest)):
                    shortest = new_path
        return shortest
