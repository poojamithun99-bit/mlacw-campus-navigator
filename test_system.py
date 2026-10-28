"""
Verification Test Suite for AI Based Multilingual Smart Campus Navigation (MLACW)
Tests:
1. All 10 data files existence and structural integrity
2. NetworkX graph building, edge counts, node counts
3. 100% reachability verification in Standard and Wheelchair modes
4. Multilingual NLP parser tests (English, Kannada, Hindi)
5. NLG Turn-by-Turn generator and ETA calculations
6. Pydantic schema validation
7. Map HTML generation with Leaflet and OpenStreetMap
8. Voice HTML component generation
"""

import os
import sys
import pandas as pd
import networkx as nx

# Set UTF-8 encoding for stdout
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_tests():
    print("=" * 60)
    print("RUNNING MLACW SMART CAMPUS NAVIGATOR VERIFICATION SUITE")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    # Test 1: Check 10 Data Files
    print("\n[1/7] Testing 10 Data Files Integrity...")
    required_files = [
        "campus_locations.csv",
        "departments.csv",
        "classrooms.csv",
        "navigation_paths.csv",
        "students.csv",
        "faculty.csv",
        "navigation_logs.csv",
        "nlp_queries.csv",
        "dashboard_data.csv",
        "database.sql"
    ]
    for rf in required_files:
        p = os.path.join(data_dir, rf)
        assert os.path.exists(p), f"Missing data file: {rf}"
        size = os.path.getsize(p)
        assert size > 0, f"Empty file: {rf}"
        print(f"  ✓ {rf} exists ({size} bytes)")

    # Test 2: Graph Engine & Dijkstra
    print("\n[2/7] Testing NetworkX Graph Engine & Dijkstra Pathfinding...")
    from graph_engine import CampusGraphEngine
    loc_file = os.path.join(data_dir, "campus_locations.csv")
    path_file = os.path.join(data_dir, "navigation_paths.csv")
    graph_eng = CampusGraphEngine(loc_file, path_file)

    num_nodes = len(graph_eng.graph.nodes())
    num_edges = len(graph_eng.graph.edges())
    print(f"  ✓ Total Graph Nodes: {num_nodes} (Target >= 40)")
    print(f"  ✓ Total Graph Edges: {num_edges}")
    assert num_nodes >= 40, f"Expected at least 40 nodes, got {num_nodes}"

    # Test 3: Reachability
    print("\n[3/7] Testing 100% Campus Reachability...")
    reachability = graph_eng.verify_reachability("Main Gate")
    print(f"  ✓ Standard Mode Reachability: {reachability['standard_reachability_pct']:.1f}%")
    print(f"  ✓ Wheelchair Mode Reachability: {reachability['wheelchair_reachability_pct']:.1f}%")
    assert reachability["standard_reachability_pct"] == 100.0, f"Standard unreachable: {reachability['standard_unreachable']}"
    assert reachability["wheelchair_reachability_pct"] == 100.0, f"Wheelchair unreachable: {reachability['wheelchair_unreachable']}"

    # Test specialized science labs, Second Floor (S1-S12), Third Floor Lounge, and Ground & First Floor blueprint landmarks reachability
    special_nodes = [
        "Computer Lab 1", "Computer Lab 2", "Dept. of Computer Science & Staff Room", "Central Library",
        "Biotechnology Research Lab", "Language Lab", "Electronics & Hardware Lab", "Dept. of Commerce & Management (BBA)",
        "Classroom G1", "Classroom G8", "Classroom G9", "Classroom G10", "Classroom G11", "Sports & Gym", "Golden Jubilee Seminar Hall",
        "Reprography Room", "Controller of Examination", "Canteen Area", "Xerox & Stationery Kiosk",
        "Classroom F1", "Classroom F5", "Chemistry Lab III", "Physics Lab III",
        "Biotechnology Lab (PG)", "Dept. of Botany", "Dept. of Journalism", "Floor 1 Student Washroom",
        "Classroom S1", "Classroom S2", "Classroom S3", "Classroom S4", "Classroom S5",
        "Classroom S6", "Classroom S7", "Classroom S8", "Classroom S9", "Classroom S10",
        "Classroom S11", "Classroom S12", "KNV Shastri Auditorium", "Student Open Lounge (Third Floor Level)", "Third Floor Lecture Hall"
    ]
    for node in special_nodes:
        assert node in graph_eng.graph, f"Missing required landmark: {node}"
        path, dist, cost = graph_eng.find_shortest_path("Main Gate", node)
        print(f"  ✓ Reachable: Main Gate -> {node} ({dist}m, {len(path)} nodes)")

    # Test 4: Multilingual NLP
    print("\n[4/7] Testing Multilingual NLP Intent & Entity Resolution...")
    from nlp_engine import CampusNLPEngine
    nlp_eng = CampusNLPEngine(graph_eng.locations_dict)

    test_queries = [
        ("Library ಎಲ್ಲಿದೆ?", "Kannada", "Central Library"),
        ("Take me to Central Library", "English", "Central Library"),
        ("कंप्यूटर लैब कहाँ है?", "Hindi", "Computer Lab 1"),
        ("Where is the Principal Office?", "English", "Principal Office"),
        ("ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ", "Kannada", "Dept. of Computer Science & Staff Room"),
        ("Wheelchair route to Auditorium", "English", "Golden Jubilee Seminar Hall"),
        ("Where is KNV Shastri Auditorium?", "English", "KNV Shastri Auditorium"),
        ("ಕೆಎನ್‌ವಿ ಶಾಸ್ತ್ರಿ ಸಭಾಂಗಣ ಎಲ್ಲಿದೆ?", "Kannada", "KNV Shastri Auditorium"),
        ("केएनवी शास्त्री ऑडिटोरियम कहाँ है?", "Hindi", "KNV Shastri Auditorium"),
        ("Where is Classroom G1?", "English", "Classroom G1"),
        ("Where is Classroom G11?", "English", "Classroom G11"),
        ("ತರಗತಿ ಜಿ ೧೦ ಎಲ್ಲಿದೆ?", "Kannada", "Classroom G10"),
        ("कक्षा जी 9 कहाँ है?", "Hindi", "Classroom G9"),
        ("ರಿಪ್ರೋಗ್ರಫಿ ಕೊಠಡಿ ಎಲ್ಲಿದೆ?", "Kannada", "Reprography Room"),
        ("गोल्डन जुबली सेमिनार हॉल", "Hindi", "Golden Jubilee Seminar Hall"),
        ("Controller of Examination", "English", "Controller of Examination"),
        ("Where is Classroom F1?", "English", "Classroom F1"),
        ("ಕಕ್ಷೆ ಎಫ್ ೫ ಎಲ್ಲಿದೆ?", "Kannada", "Classroom F5"),
        ("रसायन विज्ञान लैब 3 कहाँ है?", "Hindi", "Chemistry Lab III"),
        ("Take me to Physics Lab 3", "English", "Physics Lab III"),
        ("ಸಸ್ಯಶಾಸ್ತ್ರ ವಿಭಾಗ", "Kannada", "Dept. of Botany"),
        ("Where is Classroom S12?", "English", "Classroom S12"),
        ("ತರಗತಿ ಎಸ್ ೯ ಎಲ್ಲಿದೆ?", "Kannada", "Classroom S9"),
        ("लाउंज कहाँ है?", "Hindi", "Student Open Lounge (Third Floor Level)"),
        ("Take me to Student Lounge", "English", "Student Open Lounge (Third Floor Level)"),
        ("Third Floor Lecture Hall", "English", "Third Floor Lecture Hall")
    ]
    for query, expected_lang, expected_node in test_queries:
        res = nlp_eng.parse_query(query)
        print(f"  ✓ Query: '{query}' -> Lang: {res['detected_language']}, Matched: '{res['matched_node']}', Confidence: {res['confidence']:.2f}")
        assert res["detected_language"] == expected_lang, f"Lang mismatch for {query}"
        assert res["matched_node"] == expected_node, f"Node mismatch for {query}: got {res['matched_node']}"

    # Test 5: NLG Turn-by-Turn
    print("\n[5/7] Testing Pedestrian Turn-by-Turn NLG & ETA...")
    from nlg_engine import CampusNLGEngine
    nlg_eng = CampusNLGEngine(graph_eng.locations_dict)

    path, dist, _ = graph_eng.find_shortest_path("Main Gate", "Student Open Lounge (Third Floor Level)")
    steps_en = nlg_eng.generate_turn_by_turn(path, graph_eng.graph, language="English")
    steps_kn = nlg_eng.generate_turn_by_turn(path, graph_eng.graph, language="Kannada")
    steps_hi = nlg_eng.generate_turn_by_turn(path, graph_eng.graph, language="Hindi")
    eta = nlg_eng.calculate_eta(dist, floor_changes=3)

    print(f"  ✓ Generated {len(steps_en)} steps for Main Gate -> Student Open Lounge (ETA: {eta} min)")
    print(f"  ✓ Sample Step EN: {steps_en[0]['instruction']}")
    print(f"  ✓ Sample Step KN: {steps_kn[0]['instruction']}")
    print(f"  ✓ Sample Step HI: {steps_hi[0]['instruction']}")
    assert len(steps_en) > 0

    # Test 6: Pydantic Validation
    print("\n[6/7] Testing Pydantic Schema Validation & Geographic Bounds...")
    from schemas import CampusLocationSchema
    for _, row in graph_eng.locations_df.iterrows():
        CampusLocationSchema(
            location_id=str(row["location_id"]),
            location_name=str(row["location_name"]),
            kannada_name=str(row["kannada_name"]) if pd.notna(row["kannada_name"]) else None,
            hindi_name=str(row["hindi_name"]) if pd.notna(row["hindi_name"]) else None,
            category=str(row["category"]),
            block=str(row["block"]),
            floor=int(row["floor"]),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            is_accessible=bool(row["is_accessible"]),
            has_elevator_access=bool(row["has_elevator_access"]),
            description=str(row["description"]) if pd.notna(row["description"]) else None
        )
    print(f"  ✓ All {len(graph_eng.locations_df)} location rows passed Pydantic MLACW coordinate bounds validation.")

    # Test 7: Map & Voice Component HTML
    print("\n[7/7] Testing Map & Voice Component HTML Rendering...")
    from map_component import generate_map_html
    from voice_audio_component import get_voice_assistant_html

    route_coords = [[graph_eng.locations_dict[n]["latitude"], graph_eng.locations_dict[n]["longitude"]] for n in path]
    map_html = generate_map_html(route_coords, path, graph_eng.locations_dict, "Main Gate", "Biotechnology Lab")
    assert "openstreetmap.org" in map_html
    assert "Heading-Up" in map_html
    print("  ✓ Leaflet OpenStreetMap Map HTML generated successfully.")

    voice_html = get_voice_assistant_html(language="Kannada", audio_script="Test script")
    assert "speechSynthesis" in voice_html
    assert "webkitSpeechRecognition" in voice_html
    print("  ✓ HTML5 Speech STT/TTS component generated successfully.")

    print("\n" + "=" * 60)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (100% PASS)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
