# app.py

import streamlit as st
import matplotlib.pyplot as plt
from graph_logic import generate_collatz_tree, get_node_style

st.set_page_config(
    page_title="Collatz Tree Visualizer",
    layout="wide"
)

st.title("🌳 Collatz Conjecture Tree Visualizer")
st.markdown("""
This app visualizes the recursive tree structure of the **Collatz Conjecture** using the form:
> `n = (2^k · m - 1) / 3`, where `n` and `m` are odd integers

You can adjust the parameters to explore deeper branches and generational legs.
""")

# Sidebar controls
with st.sidebar:
    st.header("Tree Parameters")
    max_k = st.slider("Main Leg Depth (2^k)", 5, 24, 12)
    leg_depth = st.slider("G1 Leg Length", 3, 12, 6)
    st.markdown("---")
    st.markdown("Developed by [Ahmed Al-absi](https://zenodo.org/record/15178879)")

# Generate the graph
G, pos, labels, G1_nodes, G2_nodes, main_leg, G1_legs, G1_stations_with_odd_connection, stations_with_odd_connection, formula_annotations = generate_collatz_tree(max_k, leg_depth)

# Draw using matplotlib
fig, ax = plt.subplots(figsize=(24, 18))
plt.margins(0.15)

# Edges
root_edges = {(4, 2), (2, 1), (1, 4)}
normal_edges = [edge for edge in G.edges() if edge not in root_edges]
import networkx as nx
nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color='gray', alpha=0.5, ax=ax)

# Root arrows
for a, b in root_edges:
    ax.annotate("", xy=pos[b], xytext=pos[a],
                arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                zorder=3)

# Node styles
node_colors, edge_colors, line_widths, node_sizes = [], [], [], []
context = (main_leg, G1_nodes, G2_nodes, G1_legs, G1_stations_with_odd_connection, stations_with_odd_connection)
for node in G.nodes():
    color, edge, width, size = get_node_style(node, context)
    node_colors.append(color)
    edge_colors.append(edge)
    line_widths.append(width)
    node_sizes.append(size)

nx.draw_networkx_nodes(
    G, pos,
    node_color=node_colors,
    edgecolors=edge_colors,
    linewidths=line_widths,
    node_size=node_sizes,
    ax=ax
)

# Labels
for node, (x, y) in pos.items():
    ax.text(x + 0.25, y, labels[node], fontsize=9, ha='left', va='center',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

# Formulas on top
for x, y, text in formula_annotations:
    ax.text(
        x, y, text,
        fontsize=9,
        color='black',
        ha='center',
        va='bottom',
        bbox=dict(
            facecolor='white',
            alpha=0.9,
            edgecolor='none',
            boxstyle='round,pad=0.1'
        )
    )

# Legend
legend_handles = [
    plt.Line2D([0], [0], marker='o', color='w', label='Root Nodes (1, 2, 4)', markerfacecolor='skyblue', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='Main Leg (2^k with odd connection)', markerfacecolor='black', markersize=10),
    plt.Line2D([0], [0], marker='o', color='k', label='Main Leg (2^k without connection)', markerfacecolor='white', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='G1 Nodes (odd predecessors)', markerfacecolor='limegreen', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='G2 Nodes (secondary predecessors)', markerfacecolor='orange', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='∞ Infinity Markers', markerfacecolor='red', markersize=10)
]
ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.1, 1), fontsize=9, title="Node Types", title_fontsize=10)
ax.set_title(f"Collatz Tree (Main Depth = {max_k}, Leg Depth = {leg_depth})", fontsize=16, pad=20)
ax.axis('off')
plt.tight_layout()

# Display
st.pyplot(fig)
