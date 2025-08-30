package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
)

type Edge struct {
	From   int `json:"0"`
	To     int `json:"1"`
	Weight int `json:"2"`
}

type GraphQuestion struct {
	GraphID      int     `json:"graph_id"`
	Graph        [][]int `json:"graph"`
	StartNode    int     `json:"start_node"`
	EndNode      int     `json:"end_node"`
	Instructions string  `json:"instructions"`
}

type Graph struct {
	AdjList map[int][]Edge
	Nodes   map[int]bool
}

func NewGraph() *Graph {
	return &Graph{
		AdjList: make(map[int][]Edge),
		Nodes:   make(map[int]bool),
	}
}

func (g *Graph) AddEdge(from, to, weight int) {
	g.AdjList[from] = append(g.AdjList[from], Edge{From: from, To: to, Weight: weight})
	g.AdjList[to] = append(g.AdjList[to], Edge{From: to, To: from, Weight: weight})
	g.Nodes[from] = true
	g.Nodes[to] = true
}

func (g *Graph) ValidatePath(path []int) (int, bool, string) {
	if len(path) < 2 {
		return 0, false, "Path must have at least 2 nodes"
	}

	totalDistance := 0
	
	for i := 0; i < len(path)-1; i++ {
		current := path[i]
		next := path[i+1]
		
		if !g.Nodes[current] {
			return 0, false, fmt.Sprintf("Node %d does not exist in graph", current)
		}
		
		edgeFound := false
		var edgeWeight int
		
		for _, edge := range g.AdjList[current] {
			if edge.To == next {
				edgeFound = true
				edgeWeight = edge.Weight
				break
			}
		}
		
		if !edgeFound {
			return 0, false, fmt.Sprintf("No edge exists between nodes %d and %d", current, next)
		}
		
		totalDistance += edgeWeight
	}
	
	return totalDistance, true, ""
}

func (g *Graph) FindShortestPath(start, end int) (int, []int) {
	if start == end {
		return 0, []int{start}
	}

	distances := make(map[int]int)
	previous := make(map[int]int)
	visited := make(map[int]bool)
	
	for node := range g.Nodes {
		distances[node] = int(^uint(0) >> 1)
	}
	distances[start] = 0
	
	for {
		current := -1
		minDist := int(^uint(0) >> 1)
		
		for node := range g.Nodes {
			if !visited[node] && distances[node] < minDist {
				current = node
				minDist = distances[node]
			}
		}
		
		if current == -1 || current == end {
			break
		}
		
		visited[current] = true
		
		for _, edge := range g.AdjList[current] {
			if !visited[edge.To] {
				newDist := distances[current] + edge.Weight
				if newDist < distances[edge.To] {
					distances[edge.To] = newDist
					previous[edge.To] = current
				}
			}
		}
	}
	
	if distances[end] == int(^uint(0) >> 1) {
		return -1, nil
	}
	
	path := []int{}
	for current := end; current != start; current = previous[current] {
		path = append([]int{current}, path...)
		if _, exists := previous[current]; !exists && current != start {
			return -1, nil
		}
	}
	path = append([]int{start}, path...)
	
	return distances[end], path
}

func parseAnswer(answer string) (int, []int, error) {
	re := regexp.MustCompile(`Distance:\s*(\d+),\s*Path:\s*(.+)`)
	matches := re.FindStringSubmatch(answer)
	
	if len(matches) != 3 {
		return 0, nil, fmt.Errorf("invalid answer format. Expected: 'Distance: X, Path: A->B->C'")
	}
	
	distance, err := strconv.Atoi(matches[1])
	if err != nil {
		return 0, nil, fmt.Errorf("invalid distance: %v", err)
	}
	
	pathStr := strings.TrimSpace(matches[2])
	nodeStrs := strings.Split(pathStr, "->")
	
	path := make([]int, len(nodeStrs))
	for i, nodeStr := range nodeStrs {
		node, err := strconv.Atoi(strings.TrimSpace(nodeStr))
		if err != nil {
			return 0, nil, fmt.Errorf("invalid node in path: %s", nodeStr)
		}
		path[i] = node
	}
	
	return distance, path, nil
}

func validateAnswer(question GraphQuestion, answer string) {
	fmt.Printf("=== Validating Graph %d ===\n", question.GraphID)
	fmt.Printf("Start: %d, End: %d\n", question.StartNode, question.EndNode)
	
	graph := NewGraph()
	for _, edge := range question.Graph {
		if len(edge) >= 3 {
			graph.AddEdge(edge[0], edge[1], edge[2])
		}
	}
	
	correctDistance, correctPath := graph.FindShortestPath(question.StartNode, question.EndNode)
	fmt.Printf("Correct answer: Distance %d, Path: %v\n", correctDistance, correctPath)
	
	userDistance, userPath, err := parseAnswer(answer)
	if err != nil {
		fmt.Printf("❌ Parse Error: %v\n", err)
		return
	}
	
	fmt.Printf("User answer: Distance %d, Path: %v\n", userDistance, userPath)
	
	if len(userPath) == 0 {
		fmt.Printf("❌ Empty path provided\n")
		return
	}
	
	if userPath[0] != question.StartNode {
		fmt.Printf("❌ Path start mismatch: expected %d, got %d\n", question.StartNode, userPath[0])
		return
	}
	
	if userPath[len(userPath)-1] != question.EndNode {
		fmt.Printf("❌ Path end mismatch: expected %d, got %d\n", question.EndNode, userPath[len(userPath)-1])
		return
	}
	
	actualDistance, isValid, errorMsg := graph.ValidatePath(userPath)
	if !isValid {
		fmt.Printf("❌ Invalid path: %s\n", errorMsg)
		return
	}
	
	if actualDistance != userDistance {
		fmt.Printf("❌ Distance calculation error: claimed %d, actual %d\n", userDistance, actualDistance)
		return
	}
	
	if actualDistance != correctDistance {
		fmt.Printf("❌ Suboptimal path: distance %d, optimal is %d\n", actualDistance, correctDistance)
		return
	}
	
	fmt.Printf("✅ Correct! Distance: %d, Path: %v\n", actualDistance, userPath)
}

func main() {
	if len(os.Args) < 3 {
		fmt.Printf("Usage: %s <question_file.json> <answer>\n", os.Args[0])
		fmt.Printf("Answer format: \"Distance: X, Path: A->B->C\"\n")
		os.Exit(1)
	}
	
	questionFile := os.Args[1]
	answer := os.Args[2]
	
	data, err := os.ReadFile(questionFile)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}
	
	var question GraphQuestion
	err = json.Unmarshal(data, &question)
	if err != nil {
		fmt.Printf("Error parsing JSON: %v\n", err)
		os.Exit(1)
	}
	
	validateAnswer(question, answer)
}