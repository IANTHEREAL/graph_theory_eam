import random
import heapq
import json
from collections import defaultdict
from termcolor import colored
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

"""
🚫 ABSOLUTELY FORBIDDEN: Do NOT use any advanced algorithms or formulas!
❌ NO Dijkstra's algorithm
❌ NO Bellman-Ford algorithm  
❌ NO Floyd-Warshall algorithm
❌ NO A* search
❌ NO any graph algorithms you've memorized
❌ NO shortcuts or optimizations

✅ REQUIRED: Use ONLY basic methods:
- Start from the source node
- Explore neighbors step by step
- Keep track of visited nodes
- Update distances manually
- Choose the unvisited node with smallest current distance
- Work through the graph systematically

⚠️ CRITICAL: You MUST explore the graph manually without using any named algorithms!

RESPONSE FORMAT: Respond with EXACTLY this format (no extra text):
Distance: [number], Path: [start]->[node]->[node]->[end]

Example: Distance: 15, Path: 0->2->5->3
"""

NUM_GRAPHS = 5
MAX_WEIGHT = 20  # Maximum edge weight

def generate_random_graph(num_nodes=28):
    """
    Generate a random connected undirected graph with positive weights
    Returns adjacency list and string representation
    """
    nodes = list(range(num_nodes))
    edges = []

    # Ensure the graph is connected by creating a spanning tree first
    # Start with a random spanning tree
    used_nodes = {0}  # Start with node 0
    unused_nodes = set(nodes[1:])

    # Add edges to connect all nodes
    while unused_nodes:
        from_node = random.choice(list(used_nodes))
        to_node = random.choice(list(unused_nodes))
        weight = random.randint(1, MAX_WEIGHT)
        edges.append((from_node, to_node, weight))
        used_nodes.add(to_node)
        unused_nodes.remove(to_node)

    # Add some additional random edges to make it more interesting
    # Add up to num_nodes extra edges
    for _ in range(random.randint(0, num_nodes)):
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v and not any((u == e[0] and v == e[1]) or (u == e[1] and v == e[0]) for e in edges):
            weight = random.randint(1, MAX_WEIGHT)
            edges.append((u, v, weight))

    # Create adjacency list
    adj_list = defaultdict(list)
    for u, v, w in edges:
        adj_list[u].append((v, w))
        adj_list[v].append((u, w))  # Undirected graph

    # Create string representation for LLM
    edge_strings = []
    for u, v, w in sorted(edges):  # Sort for consistent ordering
        edge_strings.append(f"{u}-{v}:{w}")

    graph_str = ", ".join(edge_strings)

    # Choose random start and end nodes (different from each other)
    start_node = random.randint(0, num_nodes - 1)
    end_node = random.randint(0, num_nodes - 1)
    while end_node == start_node:
        end_node = random.randint(0, num_nodes - 1)

    return adj_list, graph_str, start_node, end_node, edges

def dijkstra_shortest_path(adj_list, start, end, num_nodes):
    """
    Compute shortest path using Dijkstra's algorithm
    Returns distance and path
    """
    distances = {node: float('infinity') for node in range(num_nodes)}
    distances[start] = 0
    previous = {node: None for node in range(num_nodes)}

    priority_queue = [(0, start)]  # (distance, node)
    visited = set()

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in adj_list[current_node]:
            if neighbor in visited:
                continue

            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    # Reconstruct path
    if distances[end] == float('infinity'):
        return float('infinity'), []  # No path exists

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return distances[end], path

def save_graph_visualization(edges, graph_num, start_node, end_node, correct_path=None, timestamp=None):
    """
    Save a visualization of the graph as an image file
    """
    # Create NetworkX graph
    G = nx.Graph()

    # Add edges with weights
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    # Create positions using spring layout for better visualization
    pos = nx.spring_layout(G, seed=42, k=1.5)  # k controls spacing

    plt.figure(figsize=(12, 8))

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500, alpha=0.8)

    # Draw edges with weights
    edges_list = list(G.edges())
    weights = [G[u][v]['weight'] for u, v in edges_list]
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color='gray')

    # Draw edge labels (weights)
    edge_labels = {(u, v): w for u, v, w in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10, font_color='red')

    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    # Highlight start and end nodes
    start_color = 'green'
    end_color = 'red'

    # Draw start node
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node],
                          node_color=start_color, node_size=600, alpha=0.9)

    # Draw end node
    nx.draw_networkx_nodes(G, pos, nodelist=[end_node],
                          node_color=end_color, node_size=600, alpha=0.9)

    # Highlight correct path if provided
    if correct_path:
        path_edges = [(correct_path[i], correct_path[i+1]) for i in range(len(correct_path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                              width=4, edge_color='blue', alpha=0.8)

    # Add title and legend
    title = f"Graph {graph_num}: Start={start_node} (green), End={end_node} (red)"
    if correct_path:
        title += f"\nCorrect Path: {' -> '.join(map(str, correct_path))}"
    plt.title(title, fontsize=14, pad=20)

    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='lightblue', alpha=0.8, label='Regular Nodes'),
        plt.Rectangle((0,0),1,1, facecolor='green', alpha=0.9, label='Start Node'),
        plt.Rectangle((0,0),1,1, facecolor='red', alpha=0.9, label='End Node')
    ]
    if correct_path:
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor='blue', alpha=0.8, label='Shortest Path'))

    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

    plt.axis('off')
    plt.tight_layout()

    # Create filename
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"graph_{graph_num}_{timestamp}.png"

    # Save the plot
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

    return filename

def validate_shortest_path(llm_distance, llm_path, correct_distance, correct_path):
    """
    Validate LLM's shortest path solution
    """
    try:
        # Check if distance matches
        if llm_distance != correct_distance:
            print(colored(f"Distance mismatch: LLM={llm_distance}, Correct={correct_distance}", "red"))
            return False

        # Check if path is valid (same start and end, same length or valid alternative)
        if not llm_path or llm_path[0] != correct_path[0] or llm_path[-1] != correct_path[-1]:
            print(colored(f"Path endpoints mismatch: LLM path={llm_path}, Correct path={correct_path}", "red"))
            return False

        # For undirected graphs, multiple paths might have same distance
        # So we mainly check distance and endpoints
        print(colored(f"Path validation: Distance correct, endpoints match", "green"))
        return True

    except Exception as e:
        print(colored(f"Validation error: {e}", "red"))
        return False

def generate_test_graphs():
    """Generate 5 test graphs with different node counts and save to JSON files"""
    node_counts = [20, 50, 80, 100, 120]
    
    for i, num_nodes in enumerate(node_counts, 1):
        print(f"Generating graph {i} with {num_nodes} nodes...")
        
        # Set seed for reproducibility
        random.seed(42 + i)
        
        # Generate graph
        adj_list, graph_str, start_node, end_node, edges = generate_random_graph(num_nodes)
        
        # Calculate correct answer using Dijkstra
        correct_distance, correct_path = dijkstra_shortest_path(adj_list, start_node, end_node, num_nodes)
        
        # Convert adjacency list to JSON serializable format
        adj_list_dict = {str(k): v for k, v in adj_list.items()}
        
        # Create question data
        question_data = {
            "graph_id": i,
            "graph": edges,
            "start_node": start_node,
            "end_node": end_node,
            "instructions": """## CRITICAL GRAPH SEARCH RULES - YOU MUST FOLLOW THESE EXACTLY:

    🚫 ABSOLUTELY FORBIDDEN: Do NOT use ANY named graph algorithms:
    ❌ DO NOT use Dijkstra's algorithm
    ❌ DO NOT use Bellman-Ford algorithm
    ❌ DO NOT use Floyd-Warshall algorithm
    ❌ DO NOT use A* search
    ❌ DO NOT use breadth-first search (BFS)
    ❌ DO NOT use depth-first search (DFS)
    ❌ DO NOT use any shortest path algorithms
    ❌ DO NOT use any memorized graph traversal methods

    ✅ REQUIRED: Only use basic systematic exploration:
    - Start from source node with distance 0
    - Examine each node's neighbors one by one
    - Keep a list of visited nodes
    - Track current best distance to each node
    - When at a node, check all its unvisited neighbors
    - Update distances if you find a shorter path
    - Choose which node to explore next based on smallest known distance
    - Continue until you reach the target or exhaust all possibilities

    ⚠️ WARNING: If you use ANY named algorithm, your answer will be marked WRONG.
    You MUST explore the graph manually and systematically.

## Test Question Files
- **File Format**: JSON files named `undirected_graph_X_Y_nodes.json` (e.g., `undirected_graph_1_20_nodes.json`, `undirected_graph_2_50_nodes.json`)
- **Question Content**: Each file contains:
  - `graph_id`: Unique identifier for the graph
  - `graph`: Edge list where each edge is `[node1, node2, distance]`
  - `start_node`: Starting point for path calculation  
  - `end_node`: Target destination node
  - `instructions`: Complete exam rules and answer format requirements

## Response

RESPONSE FORMAT: Respond with EXACTLY this format (no extra text):
Distance: [number], Path: [start]->[node]->[node]->[end]

Example: Distance: 15, Path: 0->2->5->3
            """.strip()
        }
        
        # Save to JSON file
        filename = f"undirected_graph_{i}_{num_nodes}_nodes.json"
        with open(filename, 'w') as f:
            json.dump(question_data, f, indent=2)
        
        print(f"Question {i}: {num_nodes} nodes, Start: {start_node}, End: {end_node}")
        print(f"Correct answer: Distance {correct_distance}, Path: {' -> '.join(map(str, correct_path))}")
        print(f"Saved to: {filename}")
        print("-" * 60)

if __name__ == "__main__":
    generate_test_graphs()
