from graph import Graph


trade_paths = {
    "RUB": ["EURO", "USD"],
    "EURO": ["HUF", "SEK", "USD", "RUB"],
    "USD": ["MXN", "RUB", "EURO"],
    "HUF": ["EURO"],
    "SEK": ["EURO"],
    "MXN": ["USD"],
}

graph = Graph(trade_paths)
print(" -> ".join(graph.find_path("RUB", "RUB")))