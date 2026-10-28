# AI Based Multilingual Smart Campus Navigation (MLACW)
### Maharani Lakshmi Ammanni College for Women (Autonomous), Malleswaram, Bengaluru

An end-to-end intelligent wayfinding web application integrating multilingual natural language processing (NLP), topological graph pathfinding (NetworkX Dijkstra), barrier-free accessibility filtering, and a Google Maps-style dynamic compass navigation interface with Leaflet.js.

---

## 1. System Architecture & Tech Stack

- **Backend & Graph Engine:** Python 3, NetworkX (topological graph construction, dynamic Dijkstra edge weighting, dynamic crowd congestion penalties), Pandas, Pydantic schemas.
- **Frontend & Geospatial Canvas:** Streamlit with pure white minimalist theme (`#FFFFFF`, `#0F172A`), Leaflet.js with OpenStreetMap base layer, custom HTML5 dynamic components.
- **Sensors & Audio APIs:**
  - HTML5 `DeviceOrientation` API (compass/bearing for live turn mode).
  - HTML5 `Geolocation` API (`watchPosition`).
  - Web Speech API: `webkitSpeechRecognition` (voice Speech-to-Text in English, Kannada, Hindi) and `window.speechSynthesis` (spoken turn directives).
- **Design Language:** Pure white minimalist theme (`#FFFFFF`) with high-contrast text (`#0F172A`), clean borders (`#E2E8F0`), and clear step-by-step guidance cards without decorative animations or clipart.

---

## 2. Relational Schema & Structured Datasets (10 Data Tables)

Located in `data/`:
1. `campus_locations.csv` - 74 calibrated campus landmarks across Floors 0 to 3 with exact coordinates, blocks, and accessibility flags (including Ground Floor Classrooms G1-G11, Golden Jubilee Seminar Hall, Reprography Room, Mushroom Cultivation Lab, Controller of Examination, Sports & Gym, Girls Washroom, Canteen Area, and Xerox Kiosk).
2. `departments.csv` - 15 academic departments, Heads of Department, office locations, and contact info.
3. `classrooms.csv` - 32 classrooms, lecture halls, and specialized science laboratories with capacities and facilities.
4. `navigation_paths.csv` - 99 topological edges with meter distances, path types (corridor, stairs, elevator, ramp), accessibility flags, and crowd levels.
5. `students.csv` - Student directory with programs, years, and accessibility profiles.
6. `faculty.csv` - Faculty directory with designations, cabin locations, and consultation hours.
7. `navigation_logs.csv` - Historical and live session records for wayfinding queries.
8. `nlp_queries.csv` - Multilingual test queries in English, Kannada, and Hindi with detected intents and landmark entity mappings.
9. `dashboard_data.csv` - Institutional space analytics, peak transition periods, and congestion hotspots.
10. `database.sql` - Complete Relational SQL DDL script defining tables, foreign keys, indexes, and analytical views.

---

## 3. Key Functional Modules & Project Architecture

The application is structured into clean, modular, and maintainable components:

1. **`app.py`** — Main Streamlit Application controller, floor-by-floor explorer, journey progress tracker, and interactive wayfinding UI.
2. **`style.css`** — Clean, responsive CSS design system providing high-contrast UI cards, balanced typography, and mobile-friendly thumb targets.
3. **`ui_strings.py`** — Multilingual UI localization dictionary with full Kannada, Hindi, and English strings.
4. **`graph_engine.py`** — Campus topological graph builder, dynamic crowd-weighted Dijkstra shortest-path engine, and wheelchair-accessible routing.
5. **`nlp_engine.py`** — Multilingual Conversational AI extracting intent and resolving destination entities in English, Kannada, and Hindi.
6. **`nlg_engine.py`** — Turn-by-Turn Natural Language Generation providing human-readable walking directions, physical landmarks, and visual verification cues.
7. **`map_component.py`** — Interactive 2D Leaflet campus floor maps with multi-floor toggle and live route rendering.
8. **`voice_audio_component.py`** — Speech-to-Text and Text-to-Speech audio assistant with mic permission handling and playback controls.
9. **`schemas.py`** — Pydantic models and coordinate validation rules.
10. **`test_system.py`** — Automated 7-stage end-to-end verification test suite.

---

## 4. Calibrated Geographic Coordinate Bounds

All campus landmarks are anchored strictly within the physical building footprint of MLACW:
- **Anchor Point (Main Gate):** Margosa Road entrance arch at `[13.011670, 77.568960]`.
- **Latitude Range:** `13.01138 N` to `13.01168 N`.
- **Longitude Range:** `77.56860 E` to `77.56898 E`.

---

## 5. How to Run & Test the Application

### Running the Verification Suite
```bash
cd C:\Users\pooja\.gemini\antigravity-ide\scratch\mlacw-campus-navigator
python test_system.py
```

### Launching the Web Application
```bash
cd C:\Users\pooja\.gemini\antigravity-ide\scratch\mlacw-campus-navigator
streamlit run app.py
```
Or double-click `run.bat` in Windows Explorer.
The application will be live at `http://localhost:8501`.
