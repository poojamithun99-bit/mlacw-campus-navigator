"""
Topological Graph Pathfinding & Routing Engine (NetworkX)
Calculates optimal pedestrian paths using Dijkstra's algorithm.
Supports dynamic crowd penalties, multi-floor transitions, and barrier-free wheelchair accessibility routing.
"""

import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, Optional

class CampusGraphEngine:
    def __init__(self, locations_csv_path: str, paths_csv_path: str):
        self.locations_csv_path = locations_csv_path
        self.paths_csv_path = paths_csv_path
        self.locations_df = pd.read_csv(locations_csv_path)
        self.paths_df = pd.read_csv(paths_csv_path)
        
        self.locations_dict = {}
        for _, row in self.locations_df.iterrows():
            name = str(row["location_name"]).strip()
            self.locations_dict[name] = {
                "location_id": row["location_id"],
                "kannada_name": row["kannada_name"],
                "hindi_name": row["hindi_name"],
                "category": row["category"],
                "block": row["block"],
                "floor": int(row["floor"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "is_accessible": bool(row["is_accessible"]),
                "has_elevator_access": bool(row["has_elevator_access"]),
                "description": str(row["description"])
            }
            
        self.crowd_penalties = {
            "Low": 1.0,
            "Medium": 1.3,
            "High": 1.8
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.Graph:
        """Constructs NetworkX graph with topological edges and weighted distances."""
        G = nx.Graph()
        
        # Add all location nodes
        for name, info in self.locations_dict.items():
            G.add_node(
                name,
                location_id=info["location_id"],
                kannada_name=info["kannada_name"],
                hindi_name=info["hindi_name"],
                category=info["category"],
                block=info["block"],
                floor=info["floor"],
                lat=info["latitude"],
                lon=info["longitude"],
                is_accessible=info["is_accessible"],
                description=info["description"]
            )
            
        # Add edges from navigation_paths.csv
        for _, row in self.paths_df.iterrows():
            u = str(row["source_node"]).strip()
            v = str(row["target_node"]).strip()
            dist = float(row["distance_meters"])
            path_type = str(row["path_type"]).strip()
            is_acc = str(row["is_accessible"]).lower() in ["true", "1", "yes"]
            crowd = str(row["crowd_level"]).strip()
            transition = str(row["transition_type"]).strip()
            
            penalty = self.crowd_penalties.get(crowd, 1.0)
            weight = dist * penalty
            
            if u in G and v in G:
                G.add_edge(
                    u, v,
                    distance=dist,
                    weight=weight,
                    path_type=path_type,
                    is_accessible=is_acc,
                    crowd_level=crowd,
                    transition_type=transition
                )
        return G

    def get_routing_subgraph(self, wheelchair_mode: bool = False, custom_crowd_multiplier: float = 1.0) -> nx.Graph:
        """Returns graph filtered by accessibility and optionally scaled by crowd conditions."""
        subgraph = nx.Graph()
        
        # Copy nodes
        for node, data in self.graph.nodes(data=True):
            subgraph.add_node(node, **data)
            
        # Add allowed edges
        for u, v, data in self.graph.edges(data=True):
            if wheelchair_mode:
                # Prune non-accessible edges (e.g. stairs)
                if not data.get("is_accessible", True):
                    continue
                if data.get("path_type", "").lower() == "stairs":
                    continue
                    
            edge_data = dict(data)
            base_weight = edge_data["weight"]
            # Apply dynamic crowd multiplier if specified
            edge_data["weight"] = base_weight * custom_crowd_multiplier
            subgraph.add_edge(u, v, **edge_data)
            
        return subgraph

    def find_shortest_path(self, start_node: str, dest_node: str, wheelchair_mode: bool = False, crowd_multiplier: float = 1.0) -> Tuple[List[str], float, float]:
        """
        Computes shortest path between start and destination using Dijkstra's algorithm.
        Returns:
            (path_nodes_list, total_physical_distance_m, total_weighted_cost)
        """
        alias_map = {
            "Main Reception": "Main Reception Staircase",
            "Main Reception Desk": "Main Reception Staircase",
            "Reception": "Main Reception Staircase",
            "Dept. of Computer Science": "Dept. of Computer Science & Staff Room",
            "Computer Science": "Dept. of Computer Science & Staff Room",
            "BBA": "Dept. of Commerce & Management (BBA)",
            "G11": "Classroom G11"
        }
        if start_node not in self.graph and start_node in alias_map:
            start_node = alias_map[start_node]
        if dest_node not in self.graph and dest_node in alias_map:
            dest_node = alias_map[dest_node]

        if start_node not in self.graph or dest_node not in self.graph:
            raise ValueError(f"Nodes '{start_node}' or '{dest_node}' not found in campus topological graph.")
            
        if start_node == dest_node:
            return [start_node], 0.0, 0.0
            
        subG = self.get_routing_subgraph(wheelchair_mode=wheelchair_mode, custom_crowd_multiplier=crowd_multiplier)
        
        try:
            path = nx.shortest_path(subG, source=start_node, target=dest_node, weight="weight")
            total_dist = sum(subG[path[i]][path[i+1]]["distance"] for i in range(len(path) - 1))
            total_cost = sum(subG[path[i]][path[i+1]]["weight"] for i in range(len(path) - 1))
            return path, total_dist, total_cost
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # Fallback if strictly wheelchair unreachable
            if wheelchair_mode:
                # Attempt standard route and flag
                path = nx.shortest_path(self.graph, source=start_node, target=dest_node, weight="weight")
                total_dist = sum(self.graph[path[i]][path[i+1]]["distance"] for i in range(len(path) - 1))
                return path, total_dist, -1.0
            raise nx.NetworkXNoPath(f"No valid path found between {start_node} and {dest_node}.")

    def verify_reachability(self, start_anchor: str = "Main Gate") -> Dict:
        """
        Verifies 100% reachability across all campus destinations.
        Tests both Standard and Wheelchair Accessibility Modes.
        """
        standard_unreachable = []
        wheelchair_unreachable = []
        
        all_destinations = [n for n in self.graph.nodes() if n != start_anchor]
        
        # Standard mode check
        for dest in all_destinations:
            if not nx.has_path(self.graph, start_anchor, dest):
                standard_unreachable.append(dest)
                
        # Wheelchair mode check
        wheelchair_subgraph = self.get_routing_subgraph(wheelchair_mode=True)
        for dest in all_destinations:
            if not nx.has_path(wheelchair_subgraph, start_anchor, dest):
                wheelchair_unreachable.append(dest)
                
        return {
            "total_nodes": len(self.graph.nodes()),
            "total_edges": len(self.graph.edges()),
            "standard_reachable_count": len(all_destinations) - len(standard_unreachable),
            "standard_unreachable": standard_unreachable,
            "wheelchair_reachable_count": len(all_destinations) - len(wheelchair_unreachable),
            "wheelchair_unreachable": wheelchair_unreachable,
            "standard_reachability_pct": 100.0 * (len(all_destinations) - len(standard_unreachable)) / len(all_destinations),
            "wheelchair_reachability_pct": 100.0 * (len(all_destinations) - len(wheelchair_unreachable)) / len(all_destinations)
        }
