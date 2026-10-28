"""
Leaflet.js Interactive Google Maps-Style "Heading-Up" Live Turn Map Component
Pure White Minimalist Theme (#FFFFFF, #0F172A, #E2E8F0):
- Google Maps-style Navigation Chevron with dynamic Blue Vision Beam
- Top Turn-by-Turn Action Card (shows Next Turn, Distance, and Stair/Elevator alert)
- Distinctive Staircase (🪜) and Elevator (🛗) Transit Markers with floor change indicators
- Dynamic "Heading-Up" compass rotation (DeviceOrientation API + Bearing computation)
- Interactive "▶ Start Live Navigation" / "Next Step" walking simulation player
- Automatic multi-floor layer switching when ascending/descending stairs
"""

import json
from typing import List, Dict, Any, Optional

def generate_map_html(
    route_coords: List[List[float]],
    path_nodes: List[str],
    all_locations: Dict[str, Dict],
    start_node: str,
    dest_node: str,
    language: str = "English",
    selected_floor: str = "All",
    steps_data: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Renders an interactive Google Maps-style navigation canvas with live Heading-Up
    compass rotation, navigation chevron, floor filters, and staircase/elevator badges.
    """
    markers_payload = []
    for name, info in all_locations.items():
        is_stairs = "stairs" in name.lower() or "stairwell" in name.lower()
        is_elevator = "elevator" in name.lower() or "lift" in name.lower()
        
        markers_payload.append({
            "name": name,
            "kannada": info.get("kannada_name", name),
            "hindi": info.get("hindi_name", name),
            "lat": info["latitude"],
            "lng": info["longitude"],
            "floor": info["floor"],
            "category": info["category"],
            "block": info["block"],
            "is_accessible": info["is_accessible"],
            "is_stairs": is_stairs,
            "is_elevator": is_elevator
        })

    # Authentic MLACW Triangular Courtyard Footprints (Calibrated from campus architectural blueprint)
    triangle_footprints = [
        {
            "name": "MLACW Main Campus Triangular Perimeter",
            "coords": [
                [13.011685, 77.568975],
                [13.011335, 77.568635],
                [13.011665, 77.568660]
            ],
            "color": "#0284C7",
            "fill": "rgba(2, 132, 199, 0.04)",
            "dashArray": "5, 5",
            "weight": 2
        },
        {
            "name": "Central Open Quadrangle & Courtyard",
            "coords": [
                [13.011625, 77.568885],
                [13.011465, 77.568765],
                [13.011585, 77.568735]
            ],
            "color": "#10B981",
            "fill": "rgba(16, 185, 129, 0.09)",
            "weight": 2
        },
        {
            "name": "Ground Floor Classroom Wing (Classrooms G1 - G11)",
            "coords": [
                [13.011605, 77.568785],
                [13.011345, 77.568735],
                [13.011345, 77.568695],
                [13.011605, 77.568745]
            ],
            "color": "#6366F1",
            "fill": "rgba(99, 102, 241, 0.16)",
            "weight": 2
        },
        {
            "name": "North Corridor (Golden Jubilee Seminar Hall & Reprography)",
            "coords": [
                [13.011645, 77.568860],
                [13.011600, 77.568770],
                [13.011625, 77.568765],
                [13.011655, 77.568850]
            ],
            "color": "#F59E0B",
            "fill": "rgba(245, 158, 11, 0.16)",
            "weight": 2
        },
        {
            "name": "Administrative Foyer & Reception (Dr. M.C. Sastri Bust / ATM)",
            "coords": [
                [13.011675, 77.568965],
                [13.011600, 77.568870],
                [13.011630, 77.568855],
                [13.011685, 77.568945]
            ],
            "color": "#0284C7",
            "fill": "rgba(2, 132, 199, 0.18)",
            "weight": 2
        },
        {
            "name": "South Canteen Pavilion & Kitchen",
            "coords": [
                [13.011360, 77.568715],
                [13.011335, 77.568655],
                [13.011365, 77.568650],
                [13.011375, 77.568710]
            ],
            "color": "#D97706",
            "fill": "rgba(217, 119, 6, 0.18)",
            "weight": 2
        },
        {
            "name": "First Floor Science & Classroom Quadrangle (F1-F5, Science Labs & Depts)",
            "coords": [
                [13.011665, 77.568840],
                [13.011400, 77.568840],
                [13.011385, 77.568565],
                [13.011665, 77.568570]
            ],
            "color": "#06B6D4",
            "fill": "rgba(6, 182, 212, 0.08)",
            "dashArray": "4, 4",
            "weight": 2
        }
    ]

    # Departmental Blocks Layout
    block_footprints = [
        {
            "name": "Administrative Quadrangle & Entrance",
            "coords": [
                [13.011680, 77.568970],
                [13.011680, 77.568850],
                [13.011570, 77.568850],
                [13.011570, 77.568970]
            ],
            "color": "#0284C7",
            "fill": "rgba(2, 132, 199, 0.12)"
        },
        {
            "name": "Block A (CS, IS, Maths & Central Library)",
            "coords": [
                [13.011565, 77.568850],
                [13.011565, 77.568780],
                [13.011475, 77.568780],
                [13.011475, 77.568850]
            ],
            "color": "#4F46E5",
            "fill": "rgba(79, 70, 229, 0.10)"
        },
        {
            "name": "Block B (Sciences, Labs & Computer Labs 1 & 2)",
            "coords": [
                [13.011495, 77.568775],
                [13.011495, 77.568695],
                [13.011415, 77.568695],
                [13.011415, 77.568775]
            ],
            "color": "#059669",
            "fill": "rgba(5, 150, 105, 0.10)"
        },
        {
            "name": "Block C (Commerce, BBA, Auditorium & Cafeteria)",
            "coords": [
                [13.011450, 77.568670],
                [13.011450, 77.568570],
                [13.011360, 77.568570],
                [13.011360, 77.568670]
            ],
            "color": "#D97706",
            "fill": "rgba(217, 119, 6, 0.10)"
        },
        {
            "name": "Block D (Humanities, Languages & Sanskrit Wing)",
            "coords": [
                [13.011540, 77.568660],
                [13.011540, 77.568590],
                [13.011470, 77.568590],
                [13.011470, 77.568660]
            ],
            "color": "#7C3AED",
            "fill": "rgba(124, 58, 237, 0.10)"
        },
        {
            "name": "Block E (Psychology, Journalism & Media)",
            "coords": [
                [13.011590, 77.568720],
                [13.011590, 77.568665],
                [13.011550, 77.568665],
                [13.011550, 77.568720]
            ],
            "color": "#DB2777",
            "fill": "rgba(219, 39, 119, 0.10)"
        }
    ]

    steps_json = json.dumps(steps_data if steps_data else [])

    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <title>MLACW Campus Wayfinder</title>
        <!-- Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        
        <!-- Google Font Inter -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

        <style>
            * {{
                box-sizing: border-box;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            body, html {{
                margin: 0;
                padding: 0;
                height: 100%;
                background: #FFFFFF;
                color: #0F172A;
                overflow: hidden;
            }}
            #map-wrapper {{
                position: relative;
                width: 100%;
                height: 540px;
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            }}
            #map-canvas {{
                width: 100%;
                height: 100%;
                background: #FFFFFF;
                transform-origin: center center;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}

            /* Google Maps-Style Next Turn Card */
            .google-nav-card {{
                position: absolute;
                top: 12px;
                left: 12px;
                right: 12px;
                background: #0F172A;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 10px 14px;
                box-shadow: 0 4px 16px rgba(15, 23, 42, 0.25);
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: all 0.2s ease;
            }}
            .nav-icon-badge {{
                width: 38px;
                height: 38px;
                border-radius: 8px;
                background: #0284C7;
                color: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                flex-shrink: 0;
            }}
            .nav-content {{
                flex: 1;
                min-width: 0;
            }}
            .nav-distance {{
                font-size: 15px;
                font-weight: 700;
                color: #38BDF8;
                line-height: 1.2;
            }}
            .nav-instruction {{
                font-size: 12px;
                color: #F8FAFC;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-top: 2px;
            }}
            .nav-controls {{
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .btn-nav {{
                background: #1E293B;
                border: 1px solid #334155;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 600;
                padding: 6px 10px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
                white-space: nowrap;
            }}
            .btn-nav:hover {{
                background: #334155;
            }}
            .btn-nav.active {{
                background: #0284C7;
                border-color: #38BDF8;
            }}

            /* Floating Floor Selector */
            .floor-bar {{
                position: absolute;
                bottom: 16px;
                left: 12px;
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #E2E8F0;
                backdrop-filter: blur(8px);
                border-radius: 8px;
                padding: 4px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
                z-index: 1000;
                display: flex;
                gap: 4px;
            }}
            .floor-pill {{
                background: transparent;
                border: none;
                color: #475569;
                font-size: 11px;
                font-weight: 600;
                padding: 6px 11px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
            }}
            .floor-pill:hover {{
                background: #F1F5F9;
                color: #0F172A;
            }}
            .floor-pill.active {{
                background: #0F172A;
                color: #FFFFFF;
                font-weight: 700;
            }}

            /* Blueprint Layout View Switcher (Authentic Triangle vs Blocks) */
            .layout-toggle-bar {{
                position: absolute;
                top: 70px;
                left: 12px;
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #E2E8F0;
                backdrop-filter: blur(8px);
                border-radius: 8px;
                padding: 4px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .layout-pill {{
                background: transparent;
                border: none;
                color: #475569;
                font-size: 11px;
                font-weight: 600;
                padding: 5px 10px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
                white-space: nowrap;
            }}
            .layout-pill:hover {{
                background: #F1F5F9;
                color: #0F172A;
            }}
            .layout-pill.active {{
                background: #0284C7;
                color: #FFFFFF;
                font-weight: 700;
            }}

            /* Heading Controls */
            .heading-controls {{
                position: absolute;
                bottom: 16px;
                right: 12px;
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #E2E8F0;
                backdrop-filter: blur(8px);
                border-radius: 8px;
                padding: 6px 12px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 11px;
                color: #475569;
                font-weight: 500;
            }}
            .heading-slider {{
                width: 70px;
                accent-color: #0284C7;
                cursor: pointer;
            }}

            /* Google Maps Navigation Chevron with Directional Vision Beam */
            .nav-chevron-wrap {{
                width: 44px;
                height: 44px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.25s ease-out;
            }}
            .vision-beam {{
                position: absolute;
                top: -20px;
                width: 0;
                height: 0;
                border-left: 18px solid transparent;
                border-right: 18px solid transparent;
                border-top: 30px solid rgba(2, 132, 199, 0.28);
                border-radius: 50% 50% 0 0;
                pointer-events: none;
            }}
            .nav-chevron {{
                width: 22px;
                height: 22px;
                background: #0284C7;
                border: 2.5px solid #FFFFFF;
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(2, 132, 199, 0.6);
                position: relative;
            }}
            .nav-chevron::after {{
                content: '';
                position: absolute;
                top: -8px;
                left: 50%;
                transform: translateX(-50%);
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-bottom: 9px solid #0284C7;
            }}

            /* Staircase and Elevator Map Badges */
            .transit-badge {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 13px;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                background: #FFFFFF;
                border: 2px solid #0F172A;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.15);
            }}
            .transit-badge.stairs {{
                border-color: #D97706;
                color: #D97706;
            }}
            .transit-badge.elevator {{
                border-color: #059669;
                color: #059669;
            }}

            /* Custom Leaflet Popups */
            .leaflet-popup-content-wrapper {{
                background: #FFFFFF !important;
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 8px !important;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1) !important;
                padding: 4px 8px !important;
            }}
            .leaflet-popup-tip {{
                background: #FFFFFF !important;
            }}
            .popup-title {{
                font-size: 13px;
                font-weight: 700;
                color: #0F172A;
                margin-bottom: 2px;
            }}
            .popup-tag {{
                display: inline-block;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
                background: #F1F5F9;
                color: #475569;
                border: 1px solid #E2E8F0;
                margin-top: 4px;
            }}
        </style>
    </head>
    <body>
        <div id="map-wrapper">
            <!-- Google Maps-Style Top Navigation Card -->
            <div class="google-nav-card" id="google-nav-card">
                <div class="nav-icon-badge" id="nav-step-icon">🚶</div>
                <div class="nav-content">
                    <div class="nav-distance" id="nav-step-dist">Start at {start_node}</div>
                    <div class="nav-instruction" id="nav-step-text">Head towards {dest_node}</div>
                </div>
                <div class="nav-controls">
                    <button class="btn-nav" id="btn-play-sim" onclick="toggleSimulation()">
                        ▶ Simulate Walk
                    </button>
                    <button class="btn-nav" id="btn-heading-mode" onclick="toggleHeadingUpMode()">
                        🧭 Heading-Up: OFF
                    </button>
                </div>
            </div>

            <!-- Blueprint Layout View Switcher -->
            <div class="layout-toggle-bar">
                <button class="layout-pill active" id="pill-tri" onclick="setLayoutView('triangle')">📐 Triangular Blueprint</button>
                <button class="layout-pill" id="pill-blocks" onclick="setLayoutView('blocks')">🏢 Department Blocks</button>
                <button class="layout-pill" id="pill-both" onclick="setLayoutView('both')">🌟 Compare Both</button>
            </div>

            <!-- Floating Floor Selector -->
            <div class="floor-bar">
                <button class="floor-pill {'active' if selected_floor == 'All' else ''}" onclick="filterFloor('All', this)">All</button>
                <button class="floor-pill {'active' if selected_floor == '0' else ''}" onclick="filterFloor('0', this)">Floor 0</button>
                <button class="floor-pill {'active' if selected_floor == '1' else ''}" onclick="filterFloor('1', this)">Floor 1</button>
                <button class="floor-pill {'active' if selected_floor == '2' else ''}" onclick="filterFloor('2', this)">Floor 2</button>
                <button class="floor-pill {'active' if selected_floor == '3' else ''}" onclick="filterFloor('3', this)">Floor 3</button>
            </div>

            <!-- Manual Bearing Controls -->
            <div class="heading-controls">
                <span>Compass:</span>
                <input type="range" class="heading-slider" id="bearing-slider" min="0" max="360" value="0" oninput="onManualBearingChange(this.value)">
                <span id="slider-val" style="min-width: 25px; color:#0284C7; font-weight:700;">0&deg;</span>
            </div>

            <!-- Map Viewport -->
            <div id="map-canvas"></div>
        </div>

        <script>
            const routeCoords = {json.dumps(route_coords)};
            const pathNodes = {json.dumps(path_nodes)};
            const allLocations = {json.dumps(markers_payload)};
            const triangleFootprints = {json.dumps(triangle_footprints)};
            const blockFootprints = {json.dumps(block_footprints)};
            const stepsData = {steps_json};
            const startName = "{start_node}";
            const destName = "{dest_node}";
            const userLang = "{language}";

            // Map Bounds calibrated strictly within MLACW Margosa Road Footprint
            const campusCenter = [13.011520, 77.568770];
            const maxBounds = [
                [13.01125, 77.56845],
                [13.01180, 77.56910]
            ];

            const map = L.map('map-canvas', {{
                zoomControl: false,
                attributionControl: false,
                maxBounds: maxBounds,
                minZoom: 18,
                maxZoom: 22
            }}).setView(campusCenter, 20);

            // OpenStreetMap base layer
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                subdomains: 'abc',
                maxZoom: 22
            }}).addTo(map);

            // Footprint Layer Groups (Authentic Triangular Blueprint & Departmental Blocks)
            const triangleLayer = L.layerGroup().addTo(map);
            const blockLayer = L.layerGroup();

            function initFootprints() {{
                triangleFootprints.forEach(bldg => {{
                    L.polygon(bldg.coords, {{
                        color: bldg.color,
                        weight: bldg.weight || 2,
                        opacity: 0.95,
                        dashArray: bldg.dashArray || null,
                        fillColor: bldg.fill,
                        fillOpacity: 0.65
                    }}).addTo(triangleLayer).bindTooltip(bldg.name, {{
                        permanent: false,
                        direction: 'center',
                        className: 'popup-tag'
                    }});
                }});

                blockFootprints.forEach(bldg => {{
                    L.polygon(bldg.coords, {{
                        color: bldg.color,
                        weight: 2,
                        opacity: 0.9,
                        fillColor: bldg.fill,
                        fillOpacity: 0.6
                    }}).addTo(blockLayer).bindTooltip(bldg.name, {{
                        permanent: false,
                        direction: 'center',
                        className: 'popup-tag'
                    }});
                }});
            }}
            initFootprints();

            window.setLayoutView = function(mode) {{
                document.getElementById('pill-tri').classList.remove('active');
                document.getElementById('pill-blocks').classList.remove('active');
                document.getElementById('pill-both').classList.remove('active');

                if (mode === 'triangle') {{
                    document.getElementById('pill-tri').classList.add('active');
                    if (!map.hasLayer(triangleLayer)) map.addLayer(triangleLayer);
                    if (map.hasLayer(blockLayer)) map.removeLayer(blockLayer);
                }} else if (mode === 'blocks') {{
                    document.getElementById('pill-blocks').classList.add('active');
                    if (map.hasLayer(triangleLayer)) map.removeLayer(triangleLayer);
                    if (!map.hasLayer(blockLayer)) map.addLayer(blockLayer);
                }} else if (mode === 'both') {{
                    document.getElementById('pill-both').classList.add('active');
                    if (!map.hasLayer(triangleLayer)) map.addLayer(triangleLayer);
                    if (!map.hasLayer(blockLayer)) map.addLayer(blockLayer);
                }}
            }};

            // Location Markers Layer
            const markersLayer = L.layerGroup().addTo(map);

            function renderLocations(filterFloorVal) {{
                markersLayer.clearLayers();

                allLocations.forEach(loc => {{
                    if (filterFloorVal !== 'All' && String(loc.floor) !== String(filterFloorVal)) {{
                        return;
                    }}

                    const isStart = loc.name === startName;
                    const isDest = loc.name === destName;

                    let displayName = loc.name;
                    if (userLang === 'Kannada' && loc.kannada) displayName = loc.kannada;
                    if (userLang === 'Hindi' && loc.hindi) displayName = loc.hindi;

                    // Specialized Transit Badges (Stairs / Elevators)
                    if (loc.is_stairs || loc.is_elevator) {{
                        const iconHtml = loc.is_stairs 
                            ? '<div class="transit-badge stairs" title="Staircase">🪜</div>' 
                            : '<div class="transit-badge elevator" title="Elevator">🛗</div>';
                        
                        const transitIcon = L.divIcon({{
                            html: iconHtml,
                            className: 'custom-transit-div',
                            iconSize: [24, 24],
                            iconAnchor: [12, 12]
                        }});

                        const tMarker = L.marker([loc.lat, loc.lng], {{ icon: transitIcon }}).addTo(markersLayer);
                        tMarker.bindPopup(`
                            <div class="popup-title">${{loc.is_stairs ? '🪜 ' : '🛗 '}}${{displayName}}</div>
                            <div style="font-size:11px; color:#475569;">Floor ${{loc.floor}} &bull; ${{loc.block}}</div>
                            <span class="popup-tag" style="background:${{loc.is_stairs ? '#FEF3C7; color:#92400E' : '#ECFDF5; color:#065F46'}};">Vertical Transit</span>
                        `);
                        return;
                    }}

                    let pinColor = '#64748B';
                    let radius = 5;

                    if (isStart) {{
                        pinColor = '#10B981'; // Green Start
                        radius = 8;
                    }} else if (isDest) {{
                        pinColor = '#EF4444'; // Red Dest
                        radius = 8;
                    }} else if (loc.category === 'Classroom') {{
                        pinColor = '#4F46E5'; // Indigo for Classrooms G1-G11
                        radius = 6;
                    }} else if (loc.category === 'Facility') {{
                        pinColor = '#0D9488'; // Teal for Reprography, Xerox, Washroom
                        radius = 6;
                    }} else if (loc.category === 'Food') {{
                        pinColor = '#EA580C'; // Warm Orange for Canteen & Kitchen
                        radius = 6;
                    }} else if (loc.category === 'Hall') {{
                        pinColor = '#7C3AED'; // Purple for Golden Jubilee & CS Hall
                        radius = 6.5;
                    }} else if (loc.category === 'Sports') {{
                        pinColor = '#059669'; // Emerald for Sports & Gym
                        radius = 6;
                    }} else if (loc.category === 'Academic' || loc.category === 'Lab') {{
                        pinColor = '#0284C7';
                    }} else if (loc.category === 'Library') {{
                        pinColor = '#6366F1';
                    }} else if (loc.category === 'Administration') {{
                        pinColor = '#D97706';
                    }}

                    const marker = L.circleMarker([loc.lat, loc.lng], {{
                        radius: radius,
                        fillColor: pinColor,
                        color: '#FFFFFF',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.95
                    }}).addTo(markersLayer);

                    marker.bindPopup(`
                        <div class="popup-title">${{displayName}}</div>
                        <div style="font-size:11px; color:#475569;">Floor ${{loc.floor}} &bull; ${{loc.block}}</div>
                        <span class="popup-tag">${{loc.category}}</span>
                        ${{loc.is_accessible ? '<span class="popup-tag" style="background:#ECFDF5; color:#065F46; border-color:#A7F3D0;">Accessible</span>' : ''}}
                    `);
                }});
            }}

            renderLocations('All');

            // Draw Route Polyline
            let routeLine = null;
            if (routeCoords && routeCoords.length > 1) {{
                L.polyline(routeCoords, {{
                    color: '#0284C7',
                    weight: 7,
                    opacity: 0.3
                }}).addTo(map);

                routeLine = L.polyline(routeCoords, {{
                    color: '#0284C7',
                    weight: 4,
                    opacity: 1,
                    dashArray: '8, 6'
                }}).addTo(map);

                map.fitBounds(routeLine.getBounds(), {{ padding: [60, 60], maxZoom: 21 }});
            }}

            // Google Maps Navigation Chevron with Directional Vision Beam
            const chevronIcon = L.divIcon({{
                className: 'nav-chevron-wrap-outer',
                html: '<div class="nav-chevron-wrap" id="nav-user-chevron"><div class="vision-beam"></div><div class="nav-chevron"></div></div>',
                iconSize: [44, 44],
                iconAnchor: [22, 22]
            }});

            const userMarkerPos = routeCoords.length > 0 ? routeCoords[0] : campusCenter;
            const userMarker = L.marker(userMarkerPos, {{ icon: chevronIcon, zIndexOffset: 2000 }}).addTo(map);

            // Calculation of Bearing between coordinates (Spherical trigonometry)
            function calculateBearing(lat1, lon1, lat2, lon2) {{
                const dLon = (lon2 - lon1) * Math.PI / 180;
                const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180);
                const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
                          Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon);
                let brng = Math.atan2(y, x) * 180 / Math.PI;
                return (brng + 360) % 360;
            }}

            // Heading & Live Navigation State
            let isHeadingUp = false;
            let currentHeading = 0;
            let simIndex = 0;
            let simTimer = null;
            let isSimulating = false;

            function toggleHeadingUpMode() {{
                isHeadingUp = !isHeadingUp;
                const btn = document.getElementById('btn-heading-mode');

                if (isHeadingUp) {{
                    btn.classList.add('active');
                    btn.innerText = "🧭 Heading-Up: ON";

                    if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {{
                        DeviceOrientationEvent.requestPermission().then(state => {{
                            if (state === 'granted') enableOrientationListener();
                        }}).catch(err => console.log(err));
                    }} else {{
                        enableOrientationListener();
                    }}
                }} else {{
                    btn.classList.remove('active');
                    btn.innerText = "🧭 Heading-Up: OFF";
                    applyRotation(0);
                }}
            }}

            function enableOrientationListener() {{
                window.addEventListener('deviceorientationabsolute', handleDeviceOrientation, true);
                window.addEventListener('deviceorientation', handleDeviceOrientation, true);
            }}

            function handleDeviceOrientation(e) {{
                let heading = e.webkitCompassHeading || (360 - e.alpha);
                if (heading !== undefined && heading !== null) {{
                    onHeadingUpdate(Math.round(heading));
                }}
            }}

            function onManualBearingChange(val) {{
                document.getElementById('slider-val').innerText = val + '°';
                onHeadingUpdate(parseInt(val));
            }}

            function onHeadingUpdate(heading) {{
                currentHeading = heading;
                const chevronEl = document.getElementById('nav-user-chevron');
                const canvasEl = document.getElementById('map-canvas');

                if (isHeadingUp) {{
                    canvasEl.style.transform = `rotate(${{-heading}}deg)`;
                    if (chevronEl) chevronEl.style.transform = 'rotate(0deg)';
                }} else {{
                    canvasEl.style.transform = 'rotate(0deg)';
                    if (chevronEl) chevronEl.style.transform = `rotate(${{heading}}deg)`;
                }}
            }}

            function applyRotation(deg) {{
                const canvasEl = document.getElementById('map-canvas');
                const chevronEl = document.getElementById('nav-user-chevron');
                canvasEl.style.transform = `rotate(${{deg}}deg)`;
                if (chevronEl) chevronEl.style.transform = `rotate(${{deg}}deg)`;
            }}

            function filterFloor(floorVal, btnEl) {{
                document.querySelectorAll('.floor-pill').forEach(b => b.classList.remove('active'));
                if (btnEl) btnEl.classList.add('active');
                renderLocations(floorVal);
            }}

            // Live Walking Simulation
            function toggleSimulation() {{
                const btn = document.getElementById('btn-play-sim');
                if (isSimulating) {{
                    clearInterval(simTimer);
                    isSimulating = false;
                    btn.innerHTML = "▶ Resume Walk";
                    btn.classList.remove('active');
                }} else {{
                    isSimulating = true;
                    btn.innerHTML = "⏸ Pause";
                    btn.classList.add('active');
                    if (simIndex >= routeCoords.length - 1) {{
                        simIndex = 0;
                    }}
                    simTimer = setInterval(stepSimulation, 2200);
                    stepSimulation();
                }}
            }}

            function stepSimulation() {{
                if (simIndex >= routeCoords.length) {{
                    clearInterval(simTimer);
                    isSimulating = false;
                    document.getElementById('btn-play-sim').innerHTML = "🔄 Replay Walk";
                    document.getElementById('btn-play-sim').classList.remove('active');
                    document.getElementById('nav-step-icon').innerText = "🎯";
                    document.getElementById('nav-step-dist').innerText = "Arrived at " + destName;
                    document.getElementById('nav-step-text').innerText = "You have reached your destination.";
                    return;
                }}

                const currCoord = routeCoords[simIndex];
                userMarker.setLatLng(currCoord);
                map.panTo(currCoord, {{ animate: true, duration: 0.6 }});

                // Compute forward bearing to next waypoint
                if (simIndex < routeCoords.length - 1) {{
                    const nextCoord = routeCoords[simIndex + 1];
                    const bearing = calculateBearing(currCoord[0], currCoord[1], nextCoord[0], nextCoord[1]);
                    document.getElementById('bearing-slider').value = Math.round(bearing);
                    document.getElementById('slider-val').innerText = Math.round(bearing) + '°';
                    onHeadingUpdate(Math.round(bearing));
                }}

                // Update Top Navigation Card
                if (stepsData && stepsData.length > 0) {{
                    const currentStep = stepsData[Math.min(simIndex, stepsData.length - 1)];
                    document.getElementById('nav-step-icon').innerText = currentStep.icon || "🚶";
                    document.getElementById('nav-step-dist').innerText = (currentStep.distance > 0 ? "In " + currentStep.distance + "m" : "Destination Ahead");
                    document.getElementById('nav-step-text').innerText = currentStep.instruction.replace(/\\*\\*/g, '');

                    // Auto switch floor if step involves stairs/elevator
                    if (currentStep.target_floor) {{
                        const fNum = currentStep.target_floor.replace(/[^0-9]/g, '');
                        if (fNum) {{
                            const floorBtn = document.querySelectorAll('.floor-pill')[parseInt(fNum) + 1];
                            if (floorBtn && !floorBtn.classList.contains('active')) {{
                                filterFloor(fNum, floorBtn);
                            }}
                        }}
                    }}
                }}

                simIndex++;
            }}
        </script>
    </body>
    </html>
    """
    return html_code
