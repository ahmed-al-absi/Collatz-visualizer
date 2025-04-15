# graph_logic.py

import networkx as nx
import matplotlib.pyplot as plt
from functools import lru_cache

def is_valid_odd(n):
    return n == int(n) and n % 2 == 1 and n > 0

@lru_cache(maxsize=None)
def collatz_reverse(k, m):
    g2 = (2**k * m - 1) / 3
    return int(g2) if is_valid_odd(g2) and g2 != 1 else None

def get_node_style(node, context):
    main_leg, G1_nodes, G2_nodes, G1_legs, G1_stations_with_odd_connection, stations_with_odd_connection = context
    if node in {1, 2, 4}:
        return "skyblue", "black", 1, 600
    elif node in main_leg:
        color = "black" if node in stations_with_odd_connection else "white"
        return color, "black", 1.5, 400
    elif node in G1_nodes:
        return "limegreen", "black", 1, 500
    elif node in G2_nodes:
        return "orange", "black", 1, 500
    elif any(node in leg for leg in G1_legs.values()):
        color = "black" if node in G1_stations_with_odd_connection else "white"
        return color, "black", 1.5, 350
    elif "∞" in str(node):
        return "red", "black", 1, 300
    else:
        return "lightgray", "black", 1, 350

def generate_collatz_tree(max_k=20, leg_depth=6):
    G = nx.DiGraph()
    pos = {}
    node_labels = {}
    formula_annotations = []
    y_spacing = 2.0
    x_spacing = 5.0

    root_y = 0
    root_spacing = 4.0
    root_nodes = {
        4: (0, root_y + y_spacing * 2),
        2: (-root_spacing/2, root_y),
        1: (root_spacing/2, root_y)
    }
    pos.update(root_nodes)
    G.add_edges_from([(4, 2), (2, 1), (1, 4)])
    node_labels.update({n: str(n) for n in root_nodes})

    main_leg = [2**k for k in range(3, max_k + 1)]
    main_leg_set = set(main_leg)
    for i, val in enumerate(main_leg):
        parent = val // 2
        G.add_edge(val, parent)
        pos[val] = (root_nodes[4][0], root_nodes[4][1] + (i + 1) * y_spacing)
        node_labels[val] = str(val)

    G1_nodes = []
    G1_legs = {}
    left_legs = []
    right_legs = []
    valid_main_leg = [val for val in main_leg if (val - 1) % 3 == 0]
    max_n = max([(val - 1) // 3 for val in valid_main_leg]) if valid_main_leg else 0

    side = -1
    index = 0
    for n in range(3, max_n + 1, 2):
        station = 3 * n + 1
        if station not in main_leg_set:
            continue

        x_shift = side * (x_spacing + (index // 2) * 2)
        G.add_edge(n, station)
        pos[n] = (x_shift, pos[station][1])
        node_labels[n] = str(n)
        G1_nodes.append(n)

        (left_legs if side == -1 else right_legs).append((x_shift, n))

        leg = [n * 2**i for i in range(1, leg_depth + 1)]
        for i, node in enumerate(leg):
            parent = node // 2
            G.add_edge(node, parent)
            pos[node] = (x_shift, pos[n][1] + (i + 1) * y_spacing)
            node_labels[node] = str(node)
        G1_legs[n] = leg

        inf_node = f"∞_{n}"
        pos[inf_node] = (x_shift, pos[leg[-1]][1] + y_spacing)
        node_labels[inf_node] = "∞"
        G.add_edge(inf_node, leg[-1])
        formula_annotations.append((pos[inf_node][0], pos[inf_node][1] + 0.4, f"{n}×2^k−1"))

        side *= -1
        index += 1

    if main_leg:
        last_main_node = main_leg[-1]
        main_inf_node = "∞_main"
        pos[main_inf_node] = (pos[last_main_node][0], pos[last_main_node][1] + y_spacing)
        node_labels[main_inf_node] = "∞"
        G.add_edge(main_inf_node, last_main_node)
        formula_annotations.append((pos[main_inf_node][0], pos[main_inf_node][1] + 0.4, "2^k"))

    G2_nodes = []
    G1_stations_with_odd_connection = set()
    for m in G1_legs:
        for k in range(1, max_k + 1):
            station = m * (2 ** k)
            if station not in pos:
                continue

            g2 = collatz_reverse(k, m)
            if g2 and g2 not in G:
                G.add_edge(g2, station)
                G2_nodes.append(g2)
                G1_stations_with_odd_connection.add(station)

                current_side = 'left' if pos[m][0] < 0 else 'right'
                legs = left_legs if current_side == 'left' else right_legs
                sorted_legs = sorted(legs, key=lambda x: x[0])
                current_idx = next((i for i, (x, n) in enumerate(sorted_legs) if n == m), -1)
                if current_idx != -1 and current_idx < len(sorted_legs) - 1:
                    next_leg = sorted_legs[current_idx + 1][0]
                    x_pos = (pos[m][0] + next_leg) / 2
                else:
                    x_pos = pos[m][0] + 3
                y_pos = pos[station][1] + 0.5 * y_spacing
                pos[g2] = (x_pos, y_pos)
                node_labels[g2] = str(g2)

    stations_with_odd_connection = set()
    for node in main_leg:
        for predecessor in G.predecessors(node):
            if predecessor % 2 == 1:
                stations_with_odd_connection.add(node)
                break

    return G, pos, node_labels, G1_nodes, G2_nodes, main_leg, G1_legs, G1_stations_with_odd_connection, stations_with_odd_connection, formula_annotations
