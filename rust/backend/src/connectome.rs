//! Sparse connectome data structures and graph algorithms.
//!
//! Mirrors `src/synthetic_brain/connectome.py`: a directed weighted graph
//! with conduction-delay edge costs, degree queries, weighted strength, and
//! Dijkstra shortest paths. Same semantics, same reference values as the
//! Python tests (`tests/test_connectome.py`).

use std::collections::{BTreeMap, BTreeSet};

/// One directed connectome edge.
#[derive(Debug, Clone, PartialEq)]
pub struct ConnectomeEdge {
    pub source: String,
    pub target: String,
    pub weight: f64,
    pub delay_ms: f64,
    pub excitatory: bool,
}

impl ConnectomeEdge {
    pub fn new(source: &str, target: &str, weight: f64, delay_ms: f64, excitatory: bool) -> Self {
        assert!(delay_ms >= 0.0, "delay_ms must be non-negative");
        Self {
            source: source.to_string(),
            target: target.to_string(),
            weight,
            delay_ms,
            excitatory,
        }
    }

    pub fn excitable(source: &str, target: &str, weight: f64) -> Self {
        Self::new(source, target, weight, 1.0, true)
    }

    pub fn inhibitory(source: &str, target: &str, weight: f64) -> Self {
        Self::new(source, target, weight, 1.0, false)
    }
}

/// Directed weighted graph suitable for region/population connectomes.
#[derive(Debug, Clone, Default)]
pub struct Connectome {
    pub nodes: BTreeSet<String>,
    pub edges: Vec<ConnectomeEdge>,
}

impl Connectome {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_node(&mut self, node: &str) {
        self.nodes.insert(node.to_string());
    }

    pub fn add_edge(&mut self, edge: ConnectomeEdge) {
        self.nodes.insert(edge.source.clone());
        self.nodes.insert(edge.target.clone());
        self.edges.push(edge);
    }

    pub fn out_edges(&self, node: &str) -> Vec<&ConnectomeEdge> {
        self.edges.iter().filter(|edge| edge.source == node).collect()
    }

    pub fn in_edges(&self, node: &str) -> Vec<&ConnectomeEdge> {
        self.edges.iter().filter(|edge| edge.target == node).collect()
    }

    /// (in-degree, out-degree) pair.
    pub fn degree(&self, node: &str) -> (usize, usize) {
        (self.in_edges(node).len(), self.out_edges(node).len())
    }

    /// Sum of |weight| over outgoing edges.
    pub fn weighted_out_strength(&self, node: &str) -> f64 {
        self.out_edges(node)
            .iter()
            .map(|edge| edge.weight.abs())
            .sum()
    }

    /// Dijkstra shortest paths using conduction delay as edge cost.
    /// Unreachable nodes are absent from the result.
    pub fn shortest_path_delays(&self, source: &str) -> Result<BTreeMap<String, f64>, String> {
        if !self.nodes.contains(source) {
            return Err(format!("unknown source node: {source}"));
        }
        let node_list: Vec<&String> = self.nodes.iter().collect();
        let index_of: BTreeMap<&str, usize> = node_list.iter().enumerate().map(|(index, node)| (node.as_str(), index)).collect();
        let mut distances: Vec<f64> = vec![f64::INFINITY; node_list.len()];
        distances[index_of[source]] = 0.0;
        let mut visited: Vec<bool> = vec![false; node_list.len()];

        for _ in 0..node_list.len() {
            let Some(current) = (0..node_list.len())
                .filter(|index| !visited[*index] && distances[*index] < f64::INFINITY)
                .min_by(|a, b| distances[*a].partial_cmp(&distances[*b]).unwrap())
            else {
                break;
            };
            visited[current] = true;
            let current_node = node_list[current].as_str();
            for edge in self.out_edges(current_node) {
                let candidate = distances[current] + edge.delay_ms;
                let target_index = index_of[edge.target.as_str()];
                if candidate < distances[target_index] {
                    distances[target_index] = candidate;
                }
            }
        }

        Ok(node_list
            .iter()
            .enumerate()
            .filter(|(_, _)| true)
            .filter_map(|(index, node)| {
                if distances[index].is_finite() {
                    Some(((*node).clone(), distances[index]))
                } else {
                    None
                }
            })
            .collect())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample() -> Connectome {
        let mut connectome = Connectome::new();
        connectome.add_edge(ConnectomeEdge::excitable("A", "B", 1.0));
        connectome.add_edge(ConnectomeEdge::new("B", "C", 1.0, 2.5, true));
        connectome.add_edge(ConnectomeEdge::inhibitory("C", "A", -1.0));
        connectome
    }

    #[test]
    fn edges_register_nodes() {
        let connectome = sample();
        assert_eq!(connectome.nodes.len(), 3);
        assert!(connectome.nodes.contains("A") && connectome.nodes.contains("C"));
    }

    #[test]
    fn degree_and_strength_match_python() {
        let connectome = sample();
        assert_eq!(connectome.degree("A"), (1, 1));
        assert_eq!(connectome.degree("B"), (1, 1));
        assert!((connectome.weighted_out_strength("A") - 1.0).abs() < 1e-12);
        assert!((connectome.weighted_out_strength("C") - 1.0).abs() < 1e-12);
    }

    #[test]
    fn shortest_paths_match_python_reference() {
        // Same graph as tests/test_connectome.py; verified against the Python
        // result {'A': 0.0, 'B': 1.0, 'C': 3.5}.
        let connectome = sample();
        let paths = connectome.shortest_path_delays("A").unwrap();
        assert!((paths["A"] - 0.0).abs() < 1e-12);
        assert!((paths["B"] - 1.0).abs() < 1e-12);
        assert!((paths["C"] - 3.5).abs() < 1e-12);
    }

    #[test]
    fn unknown_source_errors() {
        let connectome = sample();
        assert!(connectome.shortest_path_delays("Z").is_err());
    }

    #[test]
    fn negative_delay_rejected() {
        let result = std::panic::catch_unwind(|| ConnectomeEdge::new("A", "B", 1.0, -1.0, true));
        assert!(result.is_err());
    }
}
