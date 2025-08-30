# graph_theory_eam

## CRITICAL GRAPH SEARCH RULES - YOU MUST FOLLOW THESE EXACTLY:

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
  - `graph`: Edge list where each edge is `[node1, node2, weight]`
  - `start_node`: Starting point for path calculation  
  - `end_node`: Target destination node
  - `instructions`: Complete exam rules and answer format requirements

## Response

RESPONSE FORMAT: Respond with EXACTLY this format (no extra text):
Distance: [number], Path: [start]->[node]->[node]->[end]

Example: Distance: 15, Path: 0->2->5->3
