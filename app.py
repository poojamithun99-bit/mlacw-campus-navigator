"""
AI Based Multilingual Smart Campus Navigation (MLACW)
Maharani Lakshmi Ammanni College for Women (Autonomous), Malleswaram, Bengaluru

User-Friendly Floor-by-Floor Directory & Wayfinding System:
- Complete campus multi-story explorer: Ground Floor (Floor 0), First Floor (Floor 1), Second Floor (Floor 2), Third Floor (Floor 3)
- Direct on-screen room selection: One-click "Start Here" and "Navigate Here" for every classroom, lab, and department
- Turn-by-Turn Pedestrian Guidance with floor transitions (Stairs & Elevators)
- Audio assistant with Play, Pause, and Stop controls
- Balanced, high-contrast modern palette (soft slate-50 canvas #F8FAFC, crisp white cards #FFFFFF, deep slate text #0F172A)
- Guaranteed visible text contrast on all dropdowns, badges, buttons, and tables
"""

import os
import re
import json
import base64
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx

from nlp_engine import CampusNLPEngine
from graph_engine import CampusGraphEngine
from nlg_engine import CampusNLGEngine
import importlib
import voice_audio_component
importlib.reload(voice_audio_component)
from voice_audio_component import get_voice_assistant_html
from schemas import CampusLocationSchema
from map_component import generate_map_html
from ui_strings import UI_STRINGS
from svg_icons import get_svg_icon, icon_badge, icon_text
# ----------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Based Multilingual Smart Campus Navigation",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Balanced, High-Contrast Styling (Neither Too Bright Nor Too Dull)
# ----------------------------------------------------
CSS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. HTML Rendering Helper (Prevents 4-space indented code blocks)
# ----------------------------------------------------
def render_html(html_str: str, sidebar: bool = False):
    """
    Renders HTML safely in Streamlit without triggering Markdown's indented code blocks.
    Strips all leading whitespace from every line so CommonMark never sees 4+ spaces.
    """
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    if sidebar:
        st.sidebar.markdown(cleaned, unsafe_allow_html=True)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)

# ----------------------------------------------------
# Top-Level Parent Window Navigation Bridge for Voice Queries
# ----------------------------------------------------
# Attaches an event listener to the parent Streamlit window via an inline image onerror trigger.
# This ensures that when sandboxed iframes (e.g. SpeechRecognition in components.html) post a
# 'VOICE_NAV' message, the top-level window directly updates its location without being blocked
# by iframe sandbox restrictions (e.g. missing allow-top-navigation).
render_html("""
<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg'></svg>" style="display:none;" onload="(function(){
    if (!window._mlacwVoiceNavAttached) {
        window._mlacwVoiceNavAttached = true;
        window.addEventListener('message', function(event) {
            if (event && event.data && (event.data.type === 'VOICE_NAV' || event.data.voice_q)) {
                var q = event.data.query || event.data.voice_q;
                if (q && typeof q === 'string' && q.trim().length > 0) {
                    var base = window.location.origin + window.location.pathname;
                    if (base.endsWith('/')) base = base.slice(0, -1);
                    window.location.href = base + '/?voice_q=' + encodeURIComponent(q.trim());
                }
            }
        });
    }
})()" onerror="(function(){
    if (!window._mlacwVoiceNavAttached) {
        window._mlacwVoiceNavAttached = true;
        window.addEventListener('message', function(event) {
            if (event && event.data && (event.data.type === 'VOICE_NAV' || event.data.voice_q)) {
                var q = event.data.query || event.data.voice_q;
                if (q && typeof q === 'string' && q.trim().length > 0) {
                    var base = window.location.origin + window.location.pathname;
                    if (base.endsWith('/')) base = base.slice(0, -1);
                    window.location.href = base + '/?voice_q=' + encodeURIComponent(q.trim());
                }
            }
        });
    }
})()">
""")

# ----------------------------------------------------
# 4. Data Loading & Engine Initialization
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_resource
def load_campus_system(loc_mtime: float, paths_mtime: float):
    locations_file = os.path.join(DATA_DIR, "campus_locations.csv")
    paths_file = os.path.join(DATA_DIR, "navigation_paths.csv")
    
    graph_eng = CampusGraphEngine(locations_file, paths_file)
    nlp_eng = CampusNLPEngine(graph_eng.locations_dict)
    nlg_eng = CampusNLGEngine(graph_eng.locations_dict)
    
    return graph_eng, nlp_eng, nlg_eng

_loc_path = os.path.join(DATA_DIR, "campus_locations.csv")
_paths_path = os.path.join(DATA_DIR, "navigation_paths.csv")
_loc_mtime = os.path.getmtime(_loc_path) if os.path.exists(_loc_path) else 0.0
_paths_mtime = os.path.getmtime(_paths_path) if os.path.exists(_paths_path) else 0.0

graph_engine, nlp_engine, nlg_engine = load_campus_system(_loc_mtime, _paths_mtime)

@st.cache_data(show_spinner=False)
def generate_step_audio(text: str, language: str, _v: int = 2) -> bytes:
    """Fetches high-quality natural MP3 audio for checkpoint instructions in English, Kannada, or Hindi.
    Splits text into chunks <= 130 characters so Google Translate TTS never hits HTTP 400 Bad Request,
    and concatenates MPEG frames into a single seamless playable MP3.
    """
    import urllib.parse
    import urllib.request
    import re
    if not text or not text.strip():
        return b""
    lang_code = {"Kannada": "kn", "Hindi": "hi", "English": "en"}.get(language, "en")
    clean = re.sub(r'[*_#`]', '', text).replace('\n', ' ').strip()
    clean = re.sub(r'([,;!?.।॥])(?=[^\s])', r'\1 ', clean)
    sentences = re.split(r'([.?!।॥\n]+)', clean)
    chunks = []
    curr = ""
    for piece in sentences:
        if not piece:
            continue
        if len(curr) + len(piece) <= 130:
            curr += piece
        else:
            if curr.strip():
                chunks.append(curr.strip())
            if len(piece) <= 130:
                curr = piece
            else:
                words = piece.split()
                w_curr = ""
                for w in words:
                    if len(w_curr) + len(w) + 1 <= 130:
                        w_curr += (" " if w_curr else "") + w
                    else:
                        if w_curr:
                            chunks.append(w_curr)
                        w_curr = w
                curr = w_curr
    if curr.strip():
        chunks.append(curr.strip())

    if not chunks:
        chunks = [clean[:130]]

    audio_bytes = b""
    for chunk in chunks:
        if not chunk.strip():
            continue
        query = urllib.parse.urlencode({"ie": "UTF-8", "tl": lang_code, "client": "tw-ob", "q": chunk.strip()})
        url = f"https://translate.google.com/translate_tts?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                audio_bytes += resp.read()
        except Exception:
            pass
    return audio_bytes

# ----------------------------------------------------
# ----------------------------------------------------
# 5. Helper Functions & Floor Mappings
# ----------------------------------------------------
FLOOR_OPTIONS_I18N = {
    "English": [
        (0, "🌿 Ground Floor (Floor 0)"),
        (1, "🔬 First Floor (Floor 1)"),
        (2, "💻 Second Floor (Floor 2)"),
        (3, "🛋️ Third Floor (Floor 3)")
    ],
    "Kannada": [
        (0, "🌿 ನೆಲ ಮಹಡಿ (ಮಹಡಿ 0)"),
        (1, "🔬 1ನೇ ಮಹಡಿ (ಮಹಡಿ 1)"),
        (2, "💻 2ನೇ ಮಹಡಿ (ಮಹಡಿ 2)"),
        (3, "🛋️ 3ನೇ ಮಹಡಿ (ಮಹಡಿ 3)")
    ],
    "Hindi": [
        (0, "🌿 ग्राउंड फ्लोर (मंजिल 0)"),
        (1, "🔬 पहली मंजिल (मंजिल 1)"),
        (2, "💻 दूसरी मंजिल (मंजिल 2)"),
        (3, "🛋️ तीसरी मंजिल (मंजिल 3)")
    ]
}
FLOOR_OPTIONS = FLOOR_OPTIONS_I18N["English"]
FLOOR_LABELS = dict(FLOOR_OPTIONS)

def get_node_floor(node_name: str) -> int:
    info = graph_engine.locations_dict.get(node_name, {})
    return int(info.get("floor", 0))

def get_floor_nodes(floor_num: int) -> list:
    sub = graph_engine.locations_df[graph_engine.locations_df["floor"] == floor_num]
    return sub["location_name"].tolist()

def format_room_label(room_name: str, lang: str) -> str:
    info = graph_engine.locations_dict.get(room_name, {})
    if lang == "Kannada" and info.get("kannada_name"):
        return f"{info['kannada_name']} ({room_name})"
    elif lang == "Hindi" and info.get("hindi_name"):
        return f"{info['hindi_name']} ({room_name})"
    return room_name

# UI_STRINGS is imported from ui_strings.py

# Session State Initialization
if "language" not in st.session_state:
    st.session_state["language"] = "English"

if "language_selected" not in st.session_state:
    st.session_state["language_selected"] = False

if "app_step" not in st.session_state:
    st.session_state["app_step"] = 1

if "input_mode" not in st.session_state:
    st.session_state["input_mode"] = "voice"

if "current_origin" not in st.session_state or st.session_state["current_origin"] not in graph_engine.locations_dict:
    st.session_state["current_origin"] = "Main Gate"

if "target_destination" not in st.session_state or st.session_state["target_destination"] not in graph_engine.locations_dict:
    st.session_state["target_destination"] = "Classroom G11"

if "wheelchair_state" not in st.session_state:
    st.session_state["wheelchair_state"] = False

if "planner_version" not in st.session_state:
    st.session_state["planner_version"] = 0

if "dir_floor" not in st.session_state:
    st.session_state["dir_floor"] = 0

if "current_step_index" not in st.session_state:
    st.session_state["current_step_index"] = 0

if "completed_steps" not in st.session_state:
    st.session_state["completed_steps"] = []

if "recovery_mode" not in st.session_state:
    st.session_state["recovery_mode"] = False

if "auto_speech" not in st.session_state:
    st.session_state["auto_speech"] = False

if "active_route_signature" not in st.session_state:
    st.session_state["active_route_signature"] = ""

if "mic_active" not in st.session_state:
    st.session_state["mic_active"] = False

if "voice_assistant_response" not in st.session_state:
    st.session_state["voice_assistant_response"] = None

def set_route_endpoint(loc_name: str, endpoint_type: str = "destination", trigger_speech: bool = True):
    """
    Sets either 'origin' or 'destination' to loc_name.
    - Synchronizes the Browse Directory selectboxes by bumping planner_version.
    - Synchronizes the directory showcase floor to loc_name's floor.
    - Prevents origin == destination collision by intelligently re-targeting the opposite endpoint.
    - Resets navigation progress (current_step_index = 0, completed_steps = []).
    - Sets clear route notification message so user is never misled or confused.
    - Immediately transitions to Stage 3 (app_step = 3) to provide turn-by-turn walking instructions.
    """
    if not loc_name or loc_name not in graph_engine.locations_dict:
        return

    cur_o = st.session_state.get("current_origin", "Main Gate")
    cur_d = st.session_state.get("target_destination", "Classroom G11")

    if endpoint_type == "origin":
        st.session_state["current_origin"] = loc_name
        # If origin matches destination, pick a sensible, different destination
        if cur_d == loc_name:
            new_d = "Central Library" if loc_name != "Central Library" else "Classroom G11"
            st.session_state["target_destination"] = new_d
            st.session_state["route_notice"] = {
                "type": "info",
                "msg_en": f"🚩 Starting point set to **{loc_name}**. Destination automatically set to **{new_d}** so walking instructions are ready immediately.",
                "msg_kn": f"🚩 ಪ್ರಾರಂಭದ ಸ್ಥಳ **{loc_name}** ಗೆ ಹೊಂದಿಸಲಾಗಿದೆ. ಮಾರ್ಗದರ್ಶನ ಪ್ರಾರಂಭಿಸಲು ಗಮ್ಯಸ್ಥಾನವನ್ನು **{new_d}** ಗೆ ನಿಗದಿಪಡಿಸಲಾಗಿದೆ.",
                "msg_hi": f"🚩 शुरुआती बिंदु **{loc_name}** सेट किया गया। निर्देश तुरंत देखने के लिए गंतव्य **{new_d}** सेट किया गया।"
            }
        else:
            st.session_state["route_notice"] = {
                "type": "success",
                "msg_en": f"🚩 Starting point set to **{loc_name}**. Navigating towards **{st.session_state['target_destination']}**.",
                "msg_kn": f"🚩 ಪ್ರಾರಂಭದ ಸ್ಥಳವನ್ನು **{loc_name}** ಗೆ ಬದಲಾಯಿಸಲಾಗಿದೆ. **{st.session_state['target_destination']}** ಗೆ ಮಾರ್ಗದರ್ಶನ ಆರಂಭವಾಗಿದೆ.",
                "msg_hi": f"🚩 शुरुआती बिंदु **{loc_name}** सेट किया गया। **{st.session_state['target_destination']}** के लिए नेविगेशन शुरू।"
            }
    else: # destination
        st.session_state["target_destination"] = loc_name
        # If destination matches origin, pick a sensible, different origin
        if cur_o == loc_name:
            new_o = "Main Gate" if loc_name != "Main Gate" else "Quadrangle"
            st.session_state["current_origin"] = new_o
            st.session_state["route_notice"] = {
                "type": "info",
                "msg_en": f"🎯 Destination set to **{loc_name}**. Starting point set to **{new_o}** so walking instructions are ready immediately.",
                "msg_kn": f"🎯 ಗಮ್ಯಸ್ಥಾನವನ್ನು **{loc_name}** ಗೆ ಹೊಂದಿಸಲಾಗಿದೆ. ಮಾರ್ಗದರ್ಶನ ಪ್ರಾರಂಭಿಸಲು ಆರಂಭಿಕ ಸ್ಥಳವನ್ನು **{new_o}** ಗೆ ನಿಗದಿಪಡಿಸಲಾಗಿದೆ.",
                "msg_hi": f"🎯 गंतव्य **{loc_name}** सेट किया गया। निर्देश तुरंत देखने के लिए शुरुआती बिंदु **{new_o}** सेट किया गया।"
            }
        else:
            st.session_state["route_notice"] = {
                "type": "success",
                "msg_en": f"🎯 Destination set to **{loc_name}**. Navigating from **{st.session_state['current_origin']}**.",
                "msg_kn": f"🎯 ಗಮ್ಯಸ್ಥಾನವನ್ನು **{loc_name}** ಗೆ ಬದಲಾಯಿಸಲಾಗಿದೆ. **{st.session_state['current_origin']}** ನಿಂದ ಮಾರ್ಗದರ್ಶನ ನೀಡಲಾಗುತ್ತಿದೆ.",
                "msg_hi": f"🎯 गंतव्य **{loc_name}** सेट किया गया। **{st.session_state['current_origin']}** से मार्गदर्शन दिया जा रहा है।"
            }

    # Synchronize Browse Directory selectboxes by bumping planner_version
    st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
    # Also synchronize the directory showcase floor so it opens on the selected floor
    loc_floor = graph_engine.locations_dict[loc_name].get("floor", 0)
    st.session_state["dir_floor"] = loc_floor

    # Reset step counters & navigation state
    st.session_state["current_step_index"] = 0
    st.session_state["completed_steps"] = []
    st.session_state["recovery_mode"] = False
    st.session_state["auto_speech"] = trigger_speech

    # Transition to Stage 3 to immediately provide instructions
    st.session_state["app_step"] = 3
    st.rerun()

def handle_voice_query_action(q_text: str):
    if not q_text or not str(q_text).strip():
        return
    clean_q = str(q_text).strip()
    clean_cmd = clean_q.lower()

    # 1. Spoken Voice Navigation Commands during active navigation
    if any(w in clean_cmd for w in ["next", "forward", "ಮುಂದೆ", "ಮುಂದಿನ", "आगे", "अगला", "done", "reached", "ತಲುಪಿದೆ", "ಪಹುँच गए"]):
        curr_idx = st.session_state.get("current_step_index", 0)
        st.session_state["current_step_index"] = curr_idx + 1
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.session_state["app_step"] = 3
        st.rerun()
    elif any(w in clean_cmd for w in ["repeat", "again", "replay", "ಮತ್ತೊಮ್ಮೆ", "ಮತ್ತೆ", "ಪುನಃ", "दोहराएं", "फिर से"]):
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.session_state["app_step"] = 3
        st.rerun()
    elif any(w in clean_cmd for w in ["back", "previous", "ಹಿಂದೆ", "ಹಿಂದಿನ", "ಹಿಂತಿರುಗಿ", "पीछे", "पिछला"]):
        curr_idx = st.session_state.get("current_step_index", 0)
        st.session_state["current_step_index"] = max(0, curr_idx - 1)
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.session_state["app_step"] = 3
        st.rerun()
    elif any(w in clean_cmd for w in ["lost", "confused", "help", "ದಾರಿ ತಪ್ಪಿದೆ", "ಕಳೆದು", "ಸಹಾಯ", "खो गया", "भटक", "मदद"]):
        st.session_state["recovery_mode"] = True
        st.session_state["mic_active"] = False
        st.session_state["app_step"] = 3
        st.rerun()
    elif clean_cmd in ["english", "in english"]:
        st.session_state["language"] = "English"
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()
    elif any(w in clean_cmd for w in ["kannada", "ಕನ್ನಡ"]):
        st.session_state["language"] = "Kannada"
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()
    elif any(w in clean_cmd for w in ["hindi", "हिंदी"]):
        st.session_state["language"] = "Hindi"
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()

    # 2. Spoken Destination or Query (Multilingual Conversational NLP)
    parsed = nlp_engine.parse_query(clean_q)
    detected_language = parsed.get("detected_language", st.session_state.get("language", "English"))
    matched_target = parsed.get("matched_node")

    # Collect smart candidate recommendations based on voice query
    candidates = []
    if matched_target and matched_target in graph_engine.locations_dict:
        candidates.append(matched_target)

    # Substring & keyword matching
    clean_words = [w for w in re.sub(r'[^\w\s]', ' ', clean_cmd).split() if len(w) >= 2]
    for loc_name in graph_engine.locations_dict.keys():
        loc_lower = loc_name.lower()
        if loc_name not in candidates:
            if loc_lower in clean_cmd or any(token in clean_cmd for token in loc_lower.split() if len(token) > 2):
                candidates.append(loc_name)
            elif any(w in loc_lower for w in clean_words if len(w) > 3):
                candidates.append(loc_name)

    # Category synonyms (washroom, lab, library, canteen, classroom, principal)
    if any(w in clean_cmd for w in ["washroom", "toilet", "restroom", "ಶೌಚಾಲಯ", "शौचालय"]):
        for w_loc in ["Girls Washroom", "Floor 1 Student Washroom", "Gents Washroom", "Floor 2 West Restroom"]:
            if w_loc in graph_engine.locations_dict and w_loc not in candidates:
                candidates.append(w_loc)
    if any(w in clean_cmd for w in ["library", "ಗ್ರಂಥಾಲಯ", "ಪುಸ್ತಕ", "लाइब्रेरी", "पुस्तकालय"]):
        for l_loc in ["Central Library", "Library (PG)"]:
            if l_loc in graph_engine.locations_dict and l_loc not in candidates:
                candidates.append(l_loc)
    if any(w in clean_cmd for w in ["cs", "comp", "computer", "ಕಂಪ್ಯೂಟರ್", "कंप्यूटर"]):
        for c_loc in ["Dept. of Computer Science & Staff Room", "Computer Lab 1", "Computer Lab 2"]:
            if c_loc in graph_engine.locations_dict and c_loc not in candidates:
                candidates.append(c_loc)

    # If still no candidates, provide popular campus hubs so user always gets an active route
    if not candidates:
        for p_loc in ["Central Library", "Classroom G11", "Dept. of Computer Science & Staff Room", "Girls Washroom", "Canteen Area"]:
            if p_loc in graph_engine.locations_dict and p_loc not in candidates:
                candidates.append(p_loc)

    # Pick best destination: primary match if valid, else first candidate
    chosen_dest = matched_target if (matched_target and matched_target in graph_engine.locations_dict) else candidates[0]

    # Store remaining candidates as clickable alternative options for the user
    st.session_state["suggested_destinations"] = [c for c in candidates if c != chosen_dest][:4]

    st.session_state["language"] = detected_language
    st.session_state["language_selected"] = True
    st.session_state["mic_active"] = False

    target_info = graph_engine.locations_dict.get(chosen_dest, {})
    cur_o = st.session_state.get("current_origin", "Main Gate")
    if cur_o == chosen_dest:
        cur_o = "Main Gate" if chosen_dest != "Main Gate" else "Quadrangle"
        st.session_state["current_origin"] = cur_o
    orig_info = graph_engine.locations_dict.get(cur_o, {})

    if detected_language == "Kannada":
        t_name = target_info.get("kannada_name") or chosen_dest
        o_name = orig_info.get("kannada_name") or cur_o
        spoken_ans = f"{t_name} ಗೆ ಮಾರ್ಗಸೂಚಿ ಸಿದ್ಧವಾಗಿದೆ. {o_name} ನಿಂದ ಪ್ರಾರಂಭಿಸಿ, ಕೆಳಗಿನ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ."
    elif detected_language == "Hindi":
        t_name = target_info.get("hindi_name") or chosen_dest
        o_name = orig_info.get("hindi_name") or cur_o
        spoken_ans = f"{t_name} के लिए नेविगेशन शुरू हो रहा है। {o_name} से शुरू करके नीचे दिए गए निर्देशों का पालन करें।"
    else:
        spoken_ans = f"Navigating to {chosen_dest}. Starting from {cur_o}, follow the turn-by-turn guidance below."

    # Immediate response for instant browser TTS speech without network blocking
    st.session_state["voice_assistant_response"] = (spoken_ans, detected_language, None)
    st.session_state["auto_speech"] = True
    st.session_state["app_step"] = 3
    set_route_endpoint(chosen_dest, "destination", trigger_speech=True)
    return


def render_live_mic_banner(lang: str, key_suffix: str = "main"):
    lang_code = {"Kannada": "kn-IN", "Hindi": "hi-IN", "English": "en-IN"}.get(lang, "en-IN")
    
    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }}
      .mic-box {{
        background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%);
        border: 2px solid #E11D48;
        border-radius: 12px;
        padding: 14px 18px;
        box-sizing: border-box;
      }}
      .mic-status-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
      }}
      .pulse-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        height: 20px;
      }}
      .pulse-bar {{
        width: 4px;
        height: 100%;
        background: #E11D48;
        border-radius: 2px;
        animation: pulse 0.8s ease-in-out infinite alternate;
      }}
      .pulse-bar:nth-child(2) {{ animation-delay: 0.2s; }}
      .pulse-bar:nth-child(3) {{ animation-delay: 0.4s; }}
      @keyframes pulse {{
        0% {{ height: 30%; }}
        100% {{ height: 100%; }}
      }}
      #transcript-view {{
        margin-top: 10px;
        background: #FFFFFF;
        border: 1.5px dashed #F43F5E;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
        color: #0F172A;
        min-height: 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }}
      .mic-btn {{
        background: #E11D48;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
      }}
      .mic-btn:hover {{
        background: #BE123C;
      }}
    </style>
    </head>
    <body>
      <div class="mic-box">
        <div class="mic-status-row">
          <div style="display:flex; align-items:center; gap:8px;">
            <div class="pulse-indicator">
              <div class="pulse-bar"></div>
              <div class="pulse-bar"></div>
              <div class="pulse-bar"></div>
            </div>
            <div>
              <span style="font-weight:800; color:#9F1239; font-size:14px;">🔴 VOICE ASSISTANT LISTENING</span>
              <div style="font-size:11px; color:#BE123C;">ಧ್ವನಿ ಆಲಿಸಲಾಗುತ್ತಿದೆ • बोलें, सिस्टम सुन रहा है...</div>
            </div>
          </div>
          <div style="font-size:11px; font-weight:700; color:#9F1239; background:#FFE4E6; border:1px solid #FECDD3; padding:4px 8px; border-radius:12px;">
            Lang: {lang_code}
          </div>
        </div>

        <div id="transcript-view">
          <span id="transcript-text" style="color:#0369A1; font-weight:600;">🎙️ Click 'Start Speaking' and say your destination...</span>
          <button class="mic-btn" id="listen-toggle">🎙️ Start Speaking</button>
        </div>
      </div>

      <script>
        const SpeechClass = window.SpeechRecognition || window.webkitSpeechRecognition;
        const txt = document.getElementById("transcript-text");
        const btn = document.getElementById("listen-toggle");

        if (!SpeechClass) {{
          txt.innerHTML = "⚠️ Speech Recognition is not supported in this browser. Please use Chrome or Edge.";
          btn.style.display = "none";
        }} else {{
          const recognition = new SpeechClass();
          recognition.continuous = false;
          recognition.interimResults = true;
          recognition.lang = "{lang_code}";

          let active = false;

          btn.onclick = () => {{
            if (!active) {{
              try {{
                recognition.start();
              }} catch (e) {{
                console.warn(e);
              }}
            }} else {{
              recognition.stop();
            }}
          }};

          recognition.onstart = () => {{
            active = true;
            btn.textContent = "🔴 Listening...";
            btn.style.background = "#9F1239";
            txt.innerHTML = "Listening... Speak clearly now.";
          }};

          recognition.onresult = (event) => {{
            let interim = '';
            let final = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
              if (event.results[i].isFinal) {{
                final += event.results[i][0].transcript;
              }} else {{
                interim += event.results[i][0].transcript;
              }}
            }}
            const spoken = (final || interim).trim();
            if (spoken) {{
              txt.innerHTML = "🗣️ <i>" + spoken + "</i>";
            }}
            if (final.trim().length > 0) {{
              const cleanFinal = encodeURIComponent(final.trim());
              txt.innerHTML = "✅ Processing: <b>" + final.trim() + "</b>...";
              setTimeout(() => {{
                try {{
                  if (window.parent) window.parent.postMessage({{ type: 'VOICE_NAV', query: final.trim() }}, '*');
                }} catch (e) {{}}
                try {{
                  if (window.top) window.top.postMessage({{ type: 'VOICE_NAV', query: final.trim() }}, '*');
                }} catch (e) {{}}
                try {{
                  if (window.parent && window.parent.document && window.parent.document.body) {{
                    const scr = window.parent.document.createElement('script');
                    scr.textContent = 'window.location.search = "?voice_q=" + ' + JSON.stringify(cleanFinal) + ';';
                    window.parent.document.body.appendChild(scr);
                  }}
                }} catch (e) {{}}
                try {{
                  window.top.location.search = '?voice_q=' + cleanFinal;
                }} catch (e) {{
                  try {{
                    window.parent.location.search = '?voice_q=' + cleanFinal;
                  }} catch (e2) {{}}
                }}
              }}, 300);
            }}
          }};

          recognition.onerror = (e) => {{
            active = false;
            btn.textContent = "🎙️ Start Speaking";
            btn.style.background = "#E11D48";
            if (e.error === 'not-allowed') {{
              txt.innerHTML = "⚠️ Microphone access was blocked. Please allow mic permissions in your browser.";
            }} else if (e.error === 'no-speech') {{
              txt.innerHTML = "⚠️ No speech detected. Click Start to try again.";
            }} else {{
              txt.innerHTML = "⚠️ Error: " + e.error;
            }}
          }};

          recognition.onend = () => {{
            active = false;
            btn.textContent = "🎙️ Start Speaking";
            btn.style.background = "#E11D48";
          }};
        }}
      </script>
    </body>
    </html>
    """

    components.html(component_html, height=125, scrolling=False)

    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.6, 1.3, 1.4, 1.2, 1.2], gap="small")
    with b_col1:
        if st.button("✕ Stop / Cancel Listening", key=f"btn_stop_live_mic_{key_suffix}", use_container_width=True):
            st.session_state["mic_active"] = False
            st.rerun()
    with b_col2:
        if st.button('🗣️ "Library"', key=f"mic_chip_1_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Take me to Library")
    with b_col3:
        if st.button('🗣️ "Computer Science"', key=f"mic_chip_2_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Where is Computer Science Department?")
    with b_col4:
        if st.button('🗣️ "Next Step"', key=f"mic_chip_3_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Next")
    with b_col5:
        if st.button('🗣️ "Repeat"', key=f"mic_chip_4_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Repeat")

# Check URL query param bridge for Web Speech STT transcripts
if "voice_q" in st.query_params:
    raw_v_query = str(st.query_params["voice_q"]).strip()
    del st.query_params["voice_q"]
    if raw_v_query:
        handle_voice_query_action(raw_v_query)

# ----------------------------------------------------
# 6. Language Synchronization & Session State
# ----------------------------------------------------
LANG_MAP = {
    "English": "English",
    "ಕನ್ನಡ": "Kannada",
    "हिंदी": "Hindi"
}
INV_LANG_MAP = {
    "English": "English",
    "Kannada": "ಕನ್ನಡ",
    "Hindi": "हिंदी"
}

# ----------------------------------------------------
# 7. Main Page Header & Progressive Stepper Flow
# ----------------------------------------------------
active_lang = st.session_state["language"]
t = UI_STRINGS.get(active_lang, UI_STRINGS["English"])
floor_labels_localized = dict(FLOOR_OPTIONS_I18N.get(active_lang, FLOOR_OPTIONS_I18N["English"]))

def render_floor_directory_component(key_suffix: str = "main"):
    render_html(f"""
    <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:12px; padding:16px 20px; margin-top:14px; margin-bottom:12px; box-shadow:0 1px 4px rgba(15,23,42,0.04);">
        <div style="font-size:16px; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:8px;">
            <span style="color:#0284C7;">{get_svg_icon('building', size=22, color='#0284C7')}</span>
            <span>{t['floor_dir_title']}</span>
        </div>
        <div style="font-size:12.5px; color:#475569; margin-top:2px;">
            {t['floor_dir_sub']}
        </div>
    </div>
    """)

    col_f_select, col_r_select = st.columns([1.2, 1.8], gap="medium")
    cur_fl_idx = min(3, max(0, st.session_state.get("dir_floor", 0)))
    with col_f_select:
        dir_floor = st.selectbox(
            "📍 " + t["start_floor"] + ":",
            options=[0, 1, 2, 3],
            format_func=lambda f: [
                f"🌿 {t['floor_0_label']} — {t['floor_0_rooms'][:45]}...",
                f"🔬 {t['floor_1_label']} — {t['floor_1_rooms'][:45]}...",
                f"💻 {t['floor_2_label']} — {t['floor_2_rooms'][:45]}...",
                f"🛋️ {t['floor_3_label']} — {t['floor_3_rooms'][:45]}..."
            ][f],
            index=cur_fl_idx,
            key=f"dir_floor_sel_{key_suffix}"
        )
        st.session_state["dir_floor"] = dir_floor

    floor_all_rooms = get_floor_nodes(dir_floor)
    cur_selected_room = st.session_state.get("target_destination", floor_all_rooms[0])
    room_default_idx = floor_all_rooms.index(cur_selected_room) if cur_selected_room in floor_all_rooms else 0

    with col_r_select:
        featured_room = st.selectbox(
            f"🏫 {floor_labels_localized[dir_floor]}:",
            options=floor_all_rooms,
            format_func=lambda rm: format_room_label(rm, active_lang),
            index=room_default_idx,
            key=f"dir_room_sel_{key_suffix}_{dir_floor}"
        )

    r_info = graph_engine.locations_dict.get(featured_room, {})
    r_kn = r_info.get("kannada_name", "")
    r_hi = r_info.get("hindi_name", "")
    r_cat = r_info.get("category", "")
    r_block = r_info.get("block", "")
    r_acc = r_info.get("is_accessible", True)
    r_desc = r_info.get("description", "")
    r_fl_name = floor_labels_localized.get(dir_floor, f"Floor {dir_floor}")

    fl_badge = icon_badge('layers', r_fl_name, bg='#EFF6FF', color='#1D4ED8', border='#BFDBFE')
    cat_badge = icon_badge('folder', r_cat, bg='#E0F2FE', color='#0369A1', border='#BAE6FD')
    blk_badge = icon_badge('building', r_block, bg='#F1F5F9', color='#334155', border='#CBD5E1')
    acc_badge = icon_badge('wheelchair', 'Wheelchair Accessible', bg='#ECFDF5', color='#065F46', border='#A7F3D0') if r_acc else icon_badge('stairs', 'Stairs Access', bg='#FEF3C7', color='#92400E', border='#FDE68A')

    render_html(f"""
    <div style="background:#F8FAFC; border:1.5px solid #0284C7; border-radius:10px; padding:14px 18px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-size:18px; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:8px;">
                    {get_svg_icon('map_pin', size=20, color='#0284C7')}
                    <span>{featured_room}</span>
                </div>
                {f'<div style="font-size:12.5px; color:#475569; margin-top:2px;">{r_kn} &bull; {r_hi}</div>' if r_kn or r_hi else ''}
                {f'<div style="font-size:12.5px; color:#334155; margin-top:4px;">{r_desc}</div>' if r_desc else ''}
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                {fl_badge}
                {cat_badge}
                {blk_badge}
                {acc_badge}
            </div>
        </div>
    </div>
    """)

    col_act_a, col_act_b = st.columns(2, gap="small")
    with col_act_a:
        if st.button(f"🧭 Navigate to {featured_room} ➔", key=f"btn_showcase_dest_{key_suffix}", type="primary", use_container_width=True):
            set_route_endpoint(featured_room, "destination")
    with col_act_b:
        if st.button(f"🚩 {t['btn_set_orig']} & Start Guidance ➔", key=f"btn_showcase_orig_{key_suffix}", use_container_width=True):
            set_route_endpoint(featured_room, "origin")

# Full-width prestigious brand banner
render_html(f"""
<div class="brand-banner" style="margin-bottom:12px; padding:18px 24px;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
        <div style="display:flex; align-items:flex-start; gap:14px;">
            <div style="background:linear-gradient(135deg, #EFF6FF, #DBEAFE); border:1.5px solid #93C5FD; border-radius:12px; padding:10px; display:flex; align-items:center; justify-content:center; color:#0284C7; box-shadow:0 2px 6px rgba(2,132,199,0.12);">
                {get_svg_icon('campus', size=34, color='#0284C7')}
            </div>
            <div>
                <div class="brand-inst">{t['brand_inst']}</div>
                <h1 class="brand-title" style="margin-top:2px; margin-bottom:4px;">{t['brand_title']}</h1>
                <div class="brand-subtitle">{t['brand_subtitle']}</div>
            </div>
        </div>
        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
            {icon_badge('layers', '4 Floors', bg='#F8FAFC', color='#0284C7', border='#CBD5E1')}
            {icon_badge('globe', '3 Languages', bg='#F8FAFC', color='#D97706', border='#CBD5E1')}
            {icon_badge('wheelchair', 'Accessible', bg='#F8FAFC', color='#059669', border='#CBD5E1')}
        </div>
    </div>
</div>
""")

# Progressive Stepper Navigation Bar
cur_step = st.session_state.get("app_step", 1)
step_1_cls = "completed" if cur_step > 1 else ("active" if cur_step == 1 else "pending")
step_2_cls = "completed" if cur_step > 2 else ("active" if cur_step == 2 else "pending")
step_3_cls = "active" if cur_step == 3 else "pending"

step_labels = {
    "English": ("Language Selection", "Find Destination", "Active Wayfinding"),
    "Kannada": ("ಭಾಷೆ ಆಯ್ಕೆ", "ಗಮ್ಯಸ್ಥಾನ ಹುಡುಕಾಟ", "ಸಕ್ರಿಯ ಮಾರ್ಗದರ್ಶನ"),
    "Hindi": ("भाषा का चयन", "गंतव्य खोजें", "सक्रिय नेविगेशन")
}
sl_1, sl_2, sl_3 = step_labels.get(active_lang, step_labels["English"])

render_html(f"""
<div class="stepper-nav">
    <div class="stepper-step {step_1_cls}">
        <span class="stepper-num">1</span>
        <span style="display:inline-flex; align-items:center; gap:6px;">{get_svg_icon('globe', size=14)} {sl_1}</span>
    </div>
    <span class="stepper-divider">{get_svg_icon('arrow_right', size=13, color='#94A3B8')}</span>
    <div class="stepper-step {step_2_cls}">
        <span class="stepper-num">2</span>
        <span style="display:inline-flex; align-items:center; gap:6px;">{get_svg_icon('search', size=14)} {sl_2}</span>
    </div>
    <span class="stepper-divider">{get_svg_icon('arrow_right', size=13, color='#94A3B8')}</span>
    <div class="stepper-step {step_3_cls}">
        <span class="stepper-num">3</span>
        <span style="display:inline-flex; align-items:center; gap:6px;">{get_svg_icon('route', size=14)} {sl_3}</span>
    </div>
</div>
""")

# Top Quick-Status Sub-Bar (Visible in Step 2 & Step 3)
if cur_step > 1:
    top_col_info, top_col_act1, top_col_act2 = st.columns([3, 1.2, 1.4], gap="small")
    with top_col_info:
        if cur_step == 3:
            s_disp = format_room_label(st.session_state["current_origin"], active_lang)
            d_disp = format_room_label(st.session_state["target_destination"], active_lang)
            render_html(f"""
            <div style="font-size:13px; font-weight:700; color:#0F172A; padding:6px 0; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                <span style="display:inline-flex; align-items:center; gap:5px; color:#0369A1;">{get_svg_icon('globe', size=14, color='#0284C7')} <b>{active_lang}</b></span>
                <span style="color:#CBD5E1;">&bull;</span>
                <span style="display:inline-flex; align-items:center; gap:4px; color:#991B1B;">{get_svg_icon('flag', size=14, color='#DC2626')} {s_disp}</span>
                <span style="color:#64748B;">{get_svg_icon('arrow_right', size=12, color='#64748B')}</span>
                <span style="display:inline-flex; align-items:center; gap:4px; color:#065F46;">{get_svg_icon('target', size=14, color='#059669')} {d_disp}</span>
            </div>
            """)
        else:
            render_html(f"""
            <div style="font-size:13px; font-weight:700; color:#0F172A; padding:6px 0; display:flex; align-items:center; gap:6px;">
                {get_svg_icon('globe', size=15, color='#0284C7')}
                <span>Active Language: <b>{active_lang}</b></span>
            </div>
            """)
    with top_col_act1:
        if st.button("🌐 Change Language", key="top_change_lang_btn", use_container_width=True, help="Change language selection"):
            st.session_state["app_step"] = 1
            st.rerun()
    with top_col_act2:
        if cur_step == 3:
            if st.button("✏️ Change Destination", key="top_change_dest_btn", use_container_width=True, help="Plan a different route or destination"):
                st.session_state["app_step"] = 2
                st.session_state["input_mode"] = "browse"
                st.rerun()

# ----------------------------------------------------
# 8. Sidebar Controls
# ----------------------------------------------------
render_html(f"""
<div style="padding-bottom: 8px; border-bottom: 1.5px solid #CBD5E1; margin-bottom: 12px; display:flex; align-items:center; gap:10px;">
    <div style="color:#0284C7; display:flex; align-items:center;">{get_svg_icon('campus', size=24, color='#0284C7')}</div>
    <div>
        <div style="font-size:11px; font-weight:800; color:#0284C7; letter-spacing:0.8px; text-transform:uppercase;">MLACW WAYFINDER</div>
        <div style="font-size:16px; font-weight:800; color:#0F172A; line-height:1.2;">{t['brand_title']}</div>
    </div>
</div>
""", sidebar=True)

st.sidebar.markdown(f"""
<div style="font-size:12px; font-weight:800; color:#0F172A; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
  {get_svg_icon('compass', size=15, color='#0284C7')}
  <span>Step Navigation</span>
</div>
""", unsafe_allow_html=True)

sb_col_s1, sb_col_s2, sb_col_s3 = st.sidebar.columns(3, gap="small")
with sb_col_s1:
    if st.button("1. Lang", key="sb_step_1_btn", type="primary" if cur_step == 1 else "secondary", use_container_width=True):
        st.session_state["app_step"] = 1
        st.rerun()
with sb_col_s2:
    if st.button("2. Dest", key="sb_step_2_btn", type="primary" if cur_step == 2 else "secondary", use_container_width=True):
        st.session_state["app_step"] = 2
        st.rerun()
with sb_col_s3:
    if st.button("3. Route", key="sb_step_3_btn", type="primary" if cur_step == 3 else "secondary", use_container_width=True):
        st.session_state["app_step"] = 3
        st.rerun()

cur_lang_idx = ["English", "Kannada", "Hindi"].index(st.session_state["language"])
sb_lang = st.sidebar.selectbox(
    "🌐 Language / ಭಾಷೆ / भाषा:",
    options=["English", "Kannada", "Hindi"],
    index=cur_lang_idx,
    key=f"sb_language_select_{st.session_state['language']}"
)
if sb_lang != st.session_state["language"]:
    st.session_state["language"] = sb_lang
    st.rerun()

st.sidebar.markdown(f"<div style='font-size:12px; font-weight:700; color:#0F172A; margin-top:14px; display:flex; align-items:center; gap:5px;'>{get_svg_icon('wheelchair', size=14, color='#0284C7')}<span>{t['wheelchair_label']}:</span></div>", unsafe_allow_html=True)
wc_mode = st.sidebar.checkbox(
    t["wheelchair_label"],
    value=st.session_state["wheelchair_state"],
    help="Exclusively selects ground paths, elevators, and access ramps."
)
if wc_mode != st.session_state["wheelchair_state"]:
    st.session_state["wheelchair_state"] = wc_mode
    st.rerun()

st.sidebar.markdown(f"""
<div style="font-size:12px; font-weight:800; color:#0F172A; margin-top:16px; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
  {get_svg_icon('search', size=15, color='#0284C7')}
  <span>Quick Location Search</span>
</div>
""", unsafe_allow_html=True)

user_query = st.sidebar.text_input(
    "Search room or department:",
    placeholder="e.g. G11, Library, Botany, Computer Science...",
    key="sb_search_field",
    label_visibility="collapsed"
)

if user_query.strip():
    nlp_res = nlp_engine.parse_query(user_query)
    matched = nlp_res.get("matched_node")

    if matched:
        qr_info = graph_engine.locations_dict.get(matched, {})
        qr_floor = qr_info.get("floor", 0)
        qr_cat = qr_info.get("category", "")
        qr_block = qr_info.get("block", "")
        qr_desc = qr_info.get("description", "")
        qr_kn = qr_info.get("kannada_name", "")
        qr_hi = qr_info.get("hindi_name", "")
        qr_accessible = qr_info.get("is_accessible", True)
        fl_label_map = {0: "Ground Floor", 1: "First Floor", 2: "Second Floor", 3: "Third Floor"}
        qr_fl_label = fl_label_map.get(qr_floor, f"Floor {qr_floor}")
        access_badge = icon_badge('wheelchair', 'Accessible', bg='#D1FAE5', color='#065F46', border='#6EE7B7', size=10) if qr_accessible else icon_badge('stairs', 'Stairs', bg='#FEF3C7', color='#92400E', border='#FDE68A', size=10)

        st.sidebar.markdown(f"""
<div style="background:linear-gradient(135deg,#EFF6FF,#F0F9FF); border:2px solid #3B82F6; border-radius:14px; padding:14px 15px; margin-top:8px; box-shadow:0 4px 16px rgba(59,130,246,0.12);">
  <div style="font-size:14px; font-weight:800; color:#1E3A5F; margin-bottom:2px; display:flex; align-items:center; gap:6px;">
    {get_svg_icon('map_pin', size=15, color='#2563EB')}
    <span>{matched}</span>
  </div>
  {f'<div style="font-size:10.5px; color:#64748B; margin-bottom:5px;">{qr_kn} • {qr_hi}</div>' if qr_kn or qr_hi else ''}
  <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px;">
    {icon_badge('layers', qr_fl_label, bg='#DBEAFE', color='#1D4ED8', border='#93C5FD', size=10)}
    {icon_badge('folder', qr_cat, bg='#EEF2FF', color='#4338CA', border='#C7D2FE', size=10)}
    {icon_badge('building', qr_block, bg='#F1F5F9', color='#334155', border='#CBD5E1', size=10)}
    {access_badge}
  </div>
  {f'<div style="font-size:11.5px; color:#334155; line-height:1.5; margin-bottom:4px;">{qr_desc}</div>' if qr_desc else ''}
</div>
""", unsafe_allow_html=True)

        if nlp_res.get("is_wheelchair_mode"):
            st.session_state["wheelchair_state"] = True

        if st.sidebar.button(
            f"🧭 Navigate to {matched[:30]}{'…' if len(matched) > 30 else ''}",
            key="qs_navigate_btn",
            type="primary",
            use_container_width=True
        ):
            set_route_endpoint(matched, "destination")

        if st.sidebar.button(
            f"🚩 Set as Start: {matched[:28]}{'…' if len(matched) > 28 else ''}",
            key="qs_set_start_btn",
            use_container_width=True
        ):
            set_route_endpoint(matched, "origin")

    else:
        all_names = list(graph_engine.locations_dict.keys())
        q_lower = user_query.lower()
        suggestions = [n for n in all_names if q_lower in n.lower()][:5]
        suggestion_html = ""
        if suggestions:
            items = "".join(
                f'<li style="color:#1E3A5F; font-weight:600; font-size:11.5px; margin-bottom:3px; display:flex; align-items:center; gap:4px;">{get_svg_icon("map_pin", size=12, color="#0284C7")} <span>{s}</span></li>'
                for s in suggestions
            )
            suggestion_html = f"""
<div style="margin-top:6px; font-size:11px; color:#64748B; font-weight:600;">Did you mean:</div>
<ul style="margin:4px 0 0 0; padding-left:14px;">{items}</ul>
"""
        st.sidebar.markdown(f"""
<div style="background:#FFF7ED; border:1.5px solid #FB923C; border-radius:12px; padding:12px 14px; margin-top:8px;">
  <div style="font-size:12px; font-weight:800; color:#9A3412; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
    {get_svg_icon('alert', size=15, color='#EA580C')}
    <span>No exact match for "{user_query}"</span>
  </div>
  <div style="font-size:11px; color:#78350F;">Try: "Library", "G11", "Botany", "Computer Science", "Principal"</div>
  {suggestion_html}
</div>
""", unsafe_allow_html=True)

render_html(f"""
<div style="margin-top:20px; padding:14px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:12px; font-size:11.5px; color:#475569; box-shadow:0 1px 3px rgba(15,23,42,0.05);">
  <div style="font-weight:800; color:#0F172A; margin-bottom:8px; font-size:12.5px; letter-spacing:0.3px; display:flex; align-items:center; gap:6px;">
    {get_svg_icon('campus', size=16, color='#0284C7')}
    <span>MLACW Campus Stats</span>
  </div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="display:flex; justify-content:center; margin-bottom:2px;">{get_svg_icon('layers', size=16, color='#0284C7')}</div>
      <div style="font-size:18px; font-weight:800; color:#0284C7;">4</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Floors</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="display:flex; justify-content:center; margin-bottom:2px;">{get_svg_icon('map_pin', size=16, color='#059669')}</div>
      <div style="font-size:18px; font-weight:800; color:#059669;">{len(graph_engine.locations_dict)}</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Locations</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="display:flex; justify-content:center; margin-bottom:2px;">{get_svg_icon('globe', size=16, color='#D97706')}</div>
      <div style="font-size:18px; font-weight:800; color:#D97706;">3</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Languages</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="display:flex; justify-content:center; margin-bottom:2px;">{get_svg_icon('wheelchair', size=16, color='#7C3AED')}</div>
      <div style="font-size:18px; font-weight:800; color:#7C3AED;">100%</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Accessible</div>
    </div>
  </div>
</div>
""", sidebar=True)

# ====================================================
# STAGE 1: Language Selection (Step 1 of 3)
# ====================================================
if cur_step == 1:
    render_html(f"""
    <div class="wizard-card">
        <div class="wizard-card-header">
            <span class="wizard-step-badge">{get_svg_icon('globe', size=13, color='#0284C7')} Step 1 of 3 • {sl_1}</span>
            <div class="wizard-title">Choose Your Preferred Language / ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / अपनी भाषा चुनें</div>
            <div class="wizard-sub">
                Select your preferred language for visual wayfinding, spoken voice announcements, and conversational assistant support:
            </div>
        </div>
    </div>
    """)

    l_col1, l_col2, l_col3 = st.columns(3, gap="medium")
    with l_col1:
        if st.button("English", key="btn_wizard_en", type="primary" if active_lang == "English" else "secondary", use_container_width=True):
            st.session_state["language"] = "English"
            st.session_state["language_selected"] = True
            st.session_state["app_step"] = 2
            st.rerun()

    with l_col2:
        if st.button("ಕನ್ನಡ (Kannada)", key="btn_wizard_kn", type="primary" if active_lang == "Kannada" else "secondary", use_container_width=True):
            st.session_state["language"] = "Kannada"
            st.session_state["language_selected"] = True
            st.session_state["app_step"] = 2
            st.rerun()

    with l_col3:
        if st.button("हिंदी (Hindi)", key="btn_wizard_hi", type="primary" if active_lang == "Hindi" else "secondary", use_container_width=True):
            st.session_state["language"] = "Hindi"
            st.session_state["language_selected"] = True
            st.session_state["app_step"] = 2
            st.rerun()

# ====================================================
# STAGE 2: Interaction Preference (Step 2 of 3)
# ====================================================
elif cur_step == 2:
    stage2_titles = {
        "English": ("How would you like to navigate?", "Choose your preferred way to search or select your destination:"),
        "Kannada": ("ನೀವು ಹೇಗೆ ನ್ಯಾವಿಗೇಟ್ ಮಾಡಲು ಬಯಸುತ್ತೀರಿ?", "ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನವನ್ನು ಹುಡುಕಲು ಅಥವಾ ಆಯ್ಕೆ ಮಾಡಲು ಸೂಕ್ತ ವಿಧಾನವನ್ನು ಆರಿಸಿ:"),
        "Hindi": ("आप कैसे नेविगेट करना चाहते हैं?", "अपना गंतव्य खोजने या चुनने के लिए पसंदीदा तरीका चुनें:")
    }
    s2_title, s2_sub = stage2_titles.get(active_lang, stage2_titles["English"])

    render_html(f"""
    <div class="wizard-card" style="padding:18px 22px; margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
                <span class="wizard-step-badge">{get_svg_icon('compass', size=13, color='#0284C7')} Step 2 of 3 • {sl_2}</span>
                <div class="wizard-title" style="margin-top:2px;">{s2_title}</div>
                <div class="wizard-sub">{s2_sub}</div>
            </div>
            <div>
                {icon_badge('globe', active_lang, bg='#EFF6FF', color='#0284C7', border='#BFDBFE', size=13)}
            </div>
        </div>
    </div>
    """)

    cur_mode = st.session_state.get("input_mode", "voice")
    m_col1, m_col2, m_col3 = st.columns(3, gap="small")

    mode_labels = {
        "English": (
            "🎙️ Option A: Voice Assistant",
            "⌨️ Option B: Type / Search",
            "🏢 Option C: Browse Directory"
        ),
        "Kannada": (
            "🎙️ ಆಯ್ಕೆ ಎ: ಧ್ವನಿ ಸಹಾಯಕ",
            "⌨️ ಆಯ್ಕೆ ಬಿ: ಟೈಪ್ / ಹುಡುಕಿ",
            "🏢 ಆಯ್ಕೆ ಸಿ: ಮಹಡಿ ಡೈರೆಕ್ಟರಿ"
        ),
        "Hindi": (
            "🎙️ विकल्प अ: वॉयस असिस्टेंट",
            "⌨️ विकल्प ब: टाइप / खोजें",
            "🏢 विकल्प स: फ्लोर डायरेक्टरी"
        )
    }
    ml_a, ml_b, ml_c = mode_labels.get(active_lang, mode_labels["English"])

    with m_col1:
        if st.button(ml_a, key="btn_mode_voice", type="primary" if cur_mode == "voice" else "secondary", use_container_width=True):
            st.session_state["input_mode"] = "voice"
            st.rerun()
    with m_col2:
        if st.button(ml_b, key="btn_mode_search", type="primary" if cur_mode == "search" else "secondary", use_container_width=True):
            st.session_state["input_mode"] = "search"
            st.rerun()
    with m_col3:
        if st.button(ml_c, key="btn_mode_browse", type="primary" if cur_mode == "browse" else "secondary", use_container_width=True):
            st.session_state["input_mode"] = "browse"
            st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # MODE A: Voice Assistant
    # ----------------------------------------------------
    if cur_mode == "voice":
        render_html(f"""
        <div style="background:#FFFFFF; border:1.8px solid #0284C7; border-radius:12px; padding:16px 20px; margin-bottom:16px; box-shadow:0 3px 12px rgba(2,132,199,0.08);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:10px; border-bottom:1px solid #E2E8F0; padding-bottom:10px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="background:#E0F2FE; border-radius:10px; padding:8px; display:flex; align-items:center; justify-content:center; color:#0284C7;">
                        {get_svg_icon('mic', size=24, color='#0284C7')}
                    </div>
                    <div>
                        <div style="font-size:15px; font-weight:800; color:#0369A1; text-transform:uppercase; letter-spacing:0.5px;">
                            Multilingual Conversational Voice Assistant
                        </div>
                        <div style="font-size:12px; color:#475569; font-weight:600;">
                            {active_lang} Voice Recognition Active
                        </div>
                    </div>
                </div>
                <div>
                    {icon_badge('globe', 'Speaks English, ಕನ್ನಡ & हिंदी', bg='#EFF6FF', color='#1D4ED8', border='#BFDBFE', size=13)}
                </div>
            </div>
            <div style="font-size:12.5px; color:#334155; line-height:1.5;">
                Speak your destination or tap the microphone button. The assistant will recognize your query, announce the route vocally, and start navigation.
            </div>
        </div>
        """)

        # Voice Assistant Vocal Response Card (if an answer was spoken)
        if st.session_state.get("voice_assistant_response"):
            v_ans_text, v_ans_lang, v_ans_audio = st.session_state["voice_assistant_response"]
            v_lang_code = {"Kannada": "kn-IN", "Hindi": "hi-IN", "English": "en-IN"}.get(v_ans_lang, "en-IN")
            escaped_v_ans = json.dumps(v_ans_text)
            render_html(f"""
            <div style="background:linear-gradient(135deg, #F0F9FF, #E0F2FE); border:2px solid #0284C7; border-radius:12px; padding:14px 18px; margin-bottom:16px; box-shadow:0 3px 10px rgba(2,132,199,0.12);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="color:#0284C7;">{get_svg_icon('speaker', size=20, color='#0284C7')}</span>
                        <span style="font-size:13px; font-weight:800; color:#0369A1; text-transform:uppercase;">
                            Spoken Response ({v_ans_lang})
                        </span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <button type="button" onclick="window.mlacwSpeakAns()" style="background:#0284C7; color:#FFFFFF; border:none; border-radius:6px; padding:6px 12px; font-size:12px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:5px; box-shadow:0 1px 4px rgba(2,132,199,0.25);">
                            {get_svg_icon('play', size=12, color='#FFFFFF', filled=True)}
                            <span>Listen Aloud / ಧ್ವನಿ ಕೇಳಿ</span>
                        </button>
                        {icon_badge('speaker', 'Vocal Answer Ready', bg='#FFFFFF', color='#0284C7', border='#BAE6FD', size=12)}
                    </div>
                </div>
                <div style="font-size:15px; font-weight:700; color:#0F172A; line-height:1.5; margin-bottom:6px;">
                    "{v_ans_text}"
                </div>
            </div>
            <script>
            window.mlacwSpeakAns = function() {{
                const synth = window.speechSynthesis;
                if (!synth) return;
                synth.cancel();
                synth.resume();
                const u = new SpeechSynthesisUtterance({escaped_v_ans});
                u.lang = '{v_lang_code}';
                u.rate = 0.95;
                const voices = synth.getVoices() || [];
                const prefix = '{v_lang_code}'.split('-')[0].toLowerCase();
                const matched = voices.find(v => v.lang && (v.lang.toLowerCase() === '{v_lang_code}'.toLowerCase() || v.lang.toLowerCase().startsWith(prefix)));
                if (matched) u.voice = matched;
                synth.speak(u);
            }};
            </script>
            """)
            if v_ans_audio:
                st.audio(v_ans_audio, format="audio/mp3", autoplay=True)

        v_in_col1, v_in_col2, v_in_col3 = st.columns([3.4, 1.4, 1.2], gap="small")
        with v_in_col1:
            v_user_query = st.text_input(
                "Ask Voice Assistant:",
                placeholder="🎙️ Speak or type: 'Where is Library?', 'ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?', 'पुस्तकालय कहाँ है?'...",
                key="stage2_voice_input",
                label_visibility="collapsed"
            )
        with v_in_col2:
            v_nav_btn = st.button("🧭 Navigate ➔", key="btn_voice_nav_action", type="primary", use_container_width=True)
        with v_in_col3:
            v_mic_toggle = st.button("🎙️ Mic / ಕೇಳಿ", key="stage2_voice_submit_btn", use_container_width=True)

        mic_permission_tips = {
            "English": "🎙️ **Microphone Voice Search:** Tap **'🎙️ Mic / ಕೇಳಿ'** to speak, or type and tap **'🧭 Navigate ➔'** to get directions immediately.",
            "Kannada": "🎙️ **ಧ್ವನಿ ಹುಡುಕಾಟ:** ಮಾತನಾಡಲು **'🎙️ Mic / ಕೇಳಿ'** ಕ್ಲಿಕ್ ಮಾಡಿ, ಅಥವಾ ಟೈಪ್ ಮಾಡಿ **'🧭 Navigate ➔'** ಕ್ಲಿಕ್ ಮಾಡಿ.",
            "Hindi": "🎙️ **वॉयस सर्च:** बोलने के लिए **'🎙️ Mic / ಕೇಳಿ'** दबाएं, या लिखकर **'🧭 Navigate ➔'** दबाएं।"
        }
        st.caption(mic_permission_tips.get(active_lang, mic_permission_tips["English"]))

        if v_nav_btn:
            target_to_nav = v_user_query.strip() if (v_user_query and v_user_query.strip()) else st.session_state.get("target_destination", "Central Library")
            handle_voice_query_action(target_to_nav)
        elif v_mic_toggle:
            if v_user_query and v_user_query.strip():
                handle_voice_query_action(v_user_query.strip())
            else:
                st.session_state["mic_active"] = "assistant"
                st.rerun()

        if st.session_state.get("mic_active") in ("assistant", True):
            render_live_mic_banner(active_lang, key_suffix="assistant")

        # CRITICAL CONSTRAINT: Show ONLY the 3-4 prompt chips for the CURRENTLY selected language!
        st.markdown(f"<div style='font-size:12px; font-weight:700; color:#475569; margin-top:10px; margin-bottom:8px;'>⚡ Quick Spoken Queries ({active_lang}) — Tap any button to navigate instantly:</div>", unsafe_allow_html=True)

        if active_lang == "English":
            vc1, vc2, vc3, vc4 = st.columns(4, gap="small")
            with vc1:
                if st.button("🗣️ \"Take me to Library\"", key="vp_en_s2_1", use_container_width=True):
                    handle_voice_query_action("Take me to Library")
            with vc2:
                if st.button("🗣️ \"Classroom G11\"", key="vp_en_s2_2", use_container_width=True):
                    handle_voice_query_action("Where is Classroom G11?")
            with vc3:
                if st.button("🗣️ \"Gents Washroom\"", key="vp_en_s2_3", use_container_width=True):
                    handle_voice_query_action("Where is Gents Washroom?")
            with vc4:
                if st.button("🗣️ \"Computer Science\"", key="vp_en_s2_4", use_container_width=True):
                    handle_voice_query_action("Computer Science Department")

        elif active_lang == "Kannada":
            vc1, vc2, vc3, vc4 = st.columns(4, gap="small")
            with vc1:
                if st.button("🗣️ \"ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?\"", key="vp_kn_s2_1", use_container_width=True):
                    handle_voice_query_action("ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?")
            with vc2:
                if st.button("🗣️ \"ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್\"", key="vp_kn_s2_2", use_container_width=True):
                    handle_voice_query_action("ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಎಲ್ಲಿದೆ?")
            with vc3:
                if st.button("🗣️ \"ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?\"", key="vp_kn_s2_3", use_container_width=True):
                    handle_voice_query_action("ಪುರುಷರ ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?")
            with vc4:
                if st.button("🗣️ \"ಪ್ರಿನ್ಸಿಪಾಲ್ ಆಫೀಸ್\"", key="vp_kn_s2_4", use_container_width=True):
                    handle_voice_query_action("ಪ್ರಿನ್ಸಿಪಾಲ್ ಆಫೀಸ್")

        else: # Hindi
            vc1, vc2, vc3, vc4 = st.columns(4, gap="small")
            with vc1:
                if st.button("🗣️ \"पुस्तकालय कहाँ है?\"", key="vp_hi_s2_1", use_container_width=True):
                    handle_voice_query_action("पुस्तकालय कहाँ है?")
            with vc2:
                if st.button("🗣️ \"कंप्यूटर लैब 1\"", key="vp_hi_s2_2", use_container_width=True):
                    handle_voice_query_action("कंप्यूटर लैब 1 कहाँ है?")
            with vc3:
                if st.button("🗣️ \"शौचालय कहाँ है?\"", key="vp_hi_s2_3", use_container_width=True):
                    handle_voice_query_action("शौचालय कहाँ है?")
            with vc4:
                if st.button("🗣️ \"प्रिंसिपल ऑफिस\"", key="vp_hi_s2_4", use_container_width=True):
                    handle_voice_query_action("प्रिंसिपल ऑफिस")

    # ----------------------------------------------------
    # MODE B: Type / Search Destination
    # ----------------------------------------------------
    elif cur_mode == "search":
        render_html(f"""
        <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:12px; padding:16px 20px; margin-bottom:14px; box-shadow:0 2px 6px rgba(15,23,42,0.04);">
            <div style="font-size:16px; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:8px;">
                <span style="color:#0284C7;">{get_svg_icon('keyboard', size=20, color='#0284C7')}</span>
                <span>Type to Search Destination</span>
            </div>
            <div style="font-size:12.5px; color:#475569; margin-top:2px;">
                Enter any classroom number (e.g. G11, S12), department, laboratory, or landmark name:
            </div>
        </div>
        """)

        typed_query = st.text_input(
            "Search destination:",
            placeholder="e.g. Classroom G11, Library, Computer Science, Botany, Auditorium...",
            key="stage2_type_search_input",
            label_visibility="collapsed"
        )

        if typed_query and typed_query.strip():
            nlp_res2 = nlp_engine.parse_query(typed_query.strip())
            m_target = nlp_res2.get("matched_node")

            if m_target and m_target in graph_engine.locations_dict:
                q_inf = graph_engine.locations_dict.get(m_target, {})
                q_fl = q_inf.get("floor", 0)
                q_cat = q_inf.get("category", "")
                q_blk = q_inf.get("block", "")
                q_dsc = q_inf.get("description", "")
                q_kn = q_inf.get("kannada_name", "")
                q_hi = q_inf.get("hindi_name", "")
                q_acc = q_inf.get("is_accessible", True)
                fl_name = floor_labels_localized.get(q_fl, f"Floor {q_fl}")
                acc_pill = icon_badge('wheelchair', 'Wheelchair Accessible', bg='#D1FAE5', color='#065F46', border='#6EE7B7') if q_acc else icon_badge('stairs', 'Stairs Access', bg='#FEF3C7', color='#92400E', border='#FDE68A')
                fl_badge = icon_badge('layers', fl_name, bg='#DBEAFE', color='#1D4ED8', border='#93C5FD')
                cat_badge = icon_badge('folder', q_cat, bg='#EEF2FF', color='#4338CA', border='#C7D2FE')
                blk_badge = icon_badge('building', q_blk, bg='#F1F5F9', color='#334155', border='#CBD5E1')

                render_html(f"""
                <div style="background:#FFFFFF; border:2px solid #0284C7; border-radius:12px; padding:16px 20px; margin-top:10px; margin-bottom:14px; box-shadow:0 4px 14px rgba(2,132,199,0.08);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">
                        <div>
                            <div style="font-size:18px; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:8px;">
                                {get_svg_icon('map_pin', size=20, color='#0284C7')}
                                <span>{m_target}</span>
                            </div>
                            {f'<div style="font-size:12px; color:#64748B; margin-top:2px;">{q_kn} &bull; {q_hi}</div>' if q_kn or q_hi else ''}
                        </div>
                        <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                            {fl_badge}
                            {cat_badge}
                            {blk_badge}
                            {acc_pill}
                        </div>
                    </div>
                    {f'<div style="font-size:13px; color:#334155; line-height:1.5; margin-top:8px;">{q_dsc}</div>' if q_dsc else ''}
                </div>
                """)

                act_s2_col1, act_s2_col2 = st.columns(2, gap="small")
                with act_s2_col1:
                    if st.button(f"🧭 Navigate to {m_target} ➔", key="btn_search_start_nav", type="primary", use_container_width=True):
                        set_route_endpoint(m_target, "destination")
                with act_s2_col2:
                    if st.button(f"🚩 {t['btn_set_orig']} & Start Guidance ➔", key="btn_search_set_start", use_container_width=True):
                        set_route_endpoint(m_target, "origin")

            else:
                all_loc_names = list(graph_engine.locations_dict.keys())
                q_low = typed_query.lower()
                suggs = [n for n in all_loc_names if q_low in n.lower()][:4]
                st.warning(f"No exact match found for \"{typed_query}\".")
                if suggs:
                    st.markdown("<div style='font-size:12px; font-weight:700; color:#475569; margin-bottom:4px;'>Suggested Locations (Tap to Navigate):</div>", unsafe_allow_html=True)
                    s_cols = st.columns(len(suggs), gap="small")
                    for i, s_name in enumerate(suggs):
                        with s_cols[i]:
                            if st.button(f"📍 {s_name}", key=f"sug_btn_{i}", use_container_width=True):
                                set_route_endpoint(s_name, "destination")

    # ----------------------------------------------------
    # MODE C: Browse Campus Directory (Floor & Room)
    # ----------------------------------------------------
    else: # cur_mode == "browse"
        render_html(f"""
        <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:12px; padding:16px 20px; margin-bottom:14px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
            <div style="font-size:16px; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:8px;">
                <span style="color:#0284C7;">{get_svg_icon('compass', size=20, color='#0284C7')}</span>
                <span>{t['route_planner_title']}</span>
            </div>
            <div style="font-size:12.5px; color:#475569; margin-top:2px;">
                {t['route_planner_sub']}
            </div>
        </div>
        """)

        def handle_swap_locations():
            old_orig = st.session_state["current_origin"]
            old_dest = st.session_state["target_destination"]
            st.session_state["current_origin"] = old_dest
            st.session_state["target_destination"] = old_orig
            st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
            st.session_state["current_step_index"] = 0
            st.session_state["completed_steps"] = []
            st.session_state["recovery_mode"] = False

        p_ver = st.session_state.get("planner_version", 0)
        m_cur_o = st.session_state["current_origin"]
        m_cur_d = st.session_state["target_destination"]

        col_main_orig, col_main_dest = st.columns(2, gap="medium")

        with col_main_orig:
            st.markdown(f"<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:4px;'>{t['start_label']}</div>", unsafe_allow_html=True)
            m_cur_of = get_node_floor(m_cur_o)
            
            col_of, col_or = st.columns([1, 1.4])
            with col_of:
                m_o_fl = st.selectbox(
                    t["start_floor"],
                    options=[0, 1, 2, 3],
                    format_func=lambda f: floor_labels_localized.get(f, f"Floor {f}"),
                    index=m_cur_of,
                    key=f"main_o_fl_sel_{p_ver}"
                )
            m_o_rooms = get_floor_nodes(m_o_fl)
            m_o_idx = m_o_rooms.index(m_cur_o) if m_cur_o in m_o_rooms else 0
            with col_or:
                m_o_room = st.selectbox(
                    t["start_room"],
                    options=m_o_rooms,
                    format_func=lambda rm: format_room_label(rm, active_lang),
                    index=m_o_idx,
                    key=f"main_o_rm_sel_{p_ver}_{m_o_fl}"
                )
            if m_o_room != st.session_state["current_origin"]:
                st.session_state["current_origin"] = m_o_room
                st.session_state["current_step_index"] = 0
                st.session_state["completed_steps"] = []
                st.rerun()

        with col_main_dest:
            st.markdown(f"<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:4px;'>{t['dest_label']}</div>", unsafe_allow_html=True)
            m_cur_df = get_node_floor(m_cur_d)
            
            col_df, col_dr = st.columns([1, 1.4])
            with col_df:
                m_d_fl = st.selectbox(
                    t["dest_floor"],
                    options=[0, 1, 2, 3],
                    format_func=lambda f: floor_labels_localized.get(f, f"Floor {f}"),
                    index=m_cur_df,
                    key=f"main_d_fl_sel_{p_ver}"
                )
            m_d_rooms = get_floor_nodes(m_d_fl)
            m_d_idx = m_d_rooms.index(m_cur_d) if m_cur_d in m_d_rooms else 0
            with col_dr:
                m_d_room = st.selectbox(
                    t["dest_room"],
                    options=m_d_rooms,
                    format_func=lambda rm: format_room_label(rm, active_lang),
                    index=m_d_idx,
                    key=f"main_d_rm_sel_{p_ver}_{m_d_fl}"
                )
            if m_d_room != st.session_state["target_destination"]:
                st.session_state["target_destination"] = m_d_room
                st.session_state["current_step_index"] = 0
                st.session_state["completed_steps"] = []
                st.rerun()

        if m_cur_o == m_cur_d:
            st.warning(f"⚠️ Starting point and destination are currently both set to **{m_cur_o}**. Select different rooms above or explore rooms below:")

        col_btn_swap, col_btn_wc, col_btn_go = st.columns([1.4, 1.6, 2], gap="small")
        with col_btn_swap:
            st.button(
                t["swap_btn"],
                key="btn_swap_main_box",
                on_click=handle_swap_locations,
                use_container_width=True,
                help="Swap starting point and destination"
            )

        with col_btn_wc:
            wc_active = st.checkbox(t["wheelchair_label"], value=st.session_state["wheelchair_state"], key="wc_main_planner")
            if wc_active != st.session_state["wheelchair_state"]:
                st.session_state["wheelchair_state"] = wc_active
                st.rerun()

        with col_btn_go:
            if st.button("🧭 Start Wayfinding Guidance ➔", key="btn_go_wayfinding", type="primary", use_container_width=True):
                if st.session_state["current_origin"] == st.session_state["target_destination"]:
                    alt_d = "Central Library" if st.session_state["current_origin"] != "Central Library" else "Classroom G11"
                    set_route_endpoint(alt_d, "destination")
                else:
                    st.session_state["app_step"] = 3
                    st.session_state["current_step_index"] = 0
                    st.session_state["completed_steps"] = []
                    st.session_state["auto_speech"] = True
                    st.rerun()

        # Interactive Campus Floor & Room Directory in Browse Mode
        render_floor_directory_component("mode_c")

    # ----------------------------------------------------
    # Campus Floor Directory Quick Guide (Visible across all 3 options in Step 2)
    # ----------------------------------------------------
    render_html(f"""
    <div class="floor-guide-card" style="margin-top:16px;">
        <div class="floor-guide-header">
            <span style="color:#0284C7;">{get_svg_icon('building', size=22, color='#0284C7')}</span>
            <div>
                <div class="floor-guide-title">{t['floor_guide_title']}</div>
                <div class="floor-guide-sub">{t['floor_guide_sub']}</div>
            </div>
        </div>
        <div class="floor-guide-grid">
            <div class="floor-guide-row">
                <span class="floor-tag-pill floor-0-badge" style="display:inline-flex; align-items:center; gap:5px;">
                    {get_svg_icon('leaf', size=13, color='#15803D')} <span>{t['floor_0_label']}</span>
                </span>
                <span class="floor-tag-desc">{t['floor_0_rooms']}</span>
            </div>
            <div class="floor-guide-row">
                <span class="floor-tag-pill floor-1-badge" style="display:inline-flex; align-items:center; gap:5px;">
                    {get_svg_icon('microscope', size=13, color='#0369A1')} <span>{t['floor_1_label']}</span>
                </span>
                <span class="floor-tag-desc">{t['floor_1_rooms']}</span>
            </div>
            <div class="floor-guide-row">
                <span class="floor-tag-pill floor-2-badge" style="display:inline-flex; align-items:center; gap:5px;">
                    {get_svg_icon('laptop', size=13, color='#4338CA')} <span>{t['floor_2_label']}</span>
                </span>
                <span class="floor-tag-desc">{t['floor_2_rooms']}</span>
            </div>
            <div class="floor-guide-row">
                <span class="floor-tag-pill floor-3-badge" style="display:inline-flex; align-items:center; gap:5px;">
                    {get_svg_icon('book', size=13, color='#92400E')} <span>{t['floor_3_label']}</span>
                </span>
                <span class="floor-tag-desc">{t['floor_3_rooms']}</span>
            </div>
        </div>
    </div>
    """)

# ====================================================
# STAGE 3: Active Route Guidance & Wayfinding (Step 3 of 3)
# ====================================================
else:
    start_node = st.session_state["current_origin"]
    dest_node = st.session_state["target_destination"]

    if st.session_state.get("route_notice"):
        rn = st.session_state.pop("route_notice")
        lang_key = "msg_kn" if active_lang == "Kannada" else ("msg_hi" if active_lang == "Hindi" else "msg_en")
        n_msg = rn.get(lang_key, rn.get("msg_en", ""))
        if rn.get("type") == "info":
            st.info(n_msg)
        else:
            st.success(n_msg)

    # Voice Assistant Vocal Response Card (Spoken Route Confirmation on Step 3 Arrival)
    if st.session_state.get("voice_assistant_response"):
        v_ans_text, v_ans_lang, v_ans_audio = st.session_state.pop("voice_assistant_response")
        v_lang_code = {"Kannada": "kn-IN", "Hindi": "hi-IN", "English": "en-IN"}.get(v_ans_lang, "en-IN")
        if not v_ans_audio:
            v_ans_audio = generate_step_audio(v_ans_text, v_ans_lang)
        b64_ans_audio = base64.b64encode(v_ans_audio).decode('ascii') if v_ans_audio else ""
        escaped_v_ans = json.dumps(v_ans_text)

        confirm_component_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
          body {{ background: transparent; overflow: hidden; padding: 2px; }}
          .confirm-card {{
            background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
            border: 1.8px solid #0284C7;
            border-radius: 12px;
            padding: 12px 16px;
            box-shadow: 0 3px 10px rgba(2, 132, 199, 0.12);
            display: flex;
            flex-direction: column;
            gap: 7px;
          }}
          .confirm-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
          }}
          .title-group {{
            display: flex;
            align-items: center;
            gap: 8px;
          }}
          .title-text {{
            font-size: 12px;
            font-weight: 800;
            color: #0369A1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }}
          .badge-activated {{
            font-size: 11px;
            font-weight: 700;
            color: #0284C7;
            background: #FFFFFF;
            border: 1px solid #BAE6FD;
            padding: 2px 8px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
          }}
          .actions-group {{
            display: flex;
            align-items: center;
            gap: 6px;
          }}
          .btn-audio-action {{
            background: #0284C7;
            color: #FFFFFF !important;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            box-shadow: 0 1px 4px rgba(2, 132, 199, 0.25);
            transition: all 0.15s ease;
          }}
          .btn-audio-action:hover {{ background: #0369A1; transform: translateY(-1px); }}
          .btn-audio-action:active {{ transform: translateY(1px); }}
          .btn-audio-action.playing {{ background: #D97706 !important; }}
          .btn-stop-action {{
            background: #FFFFFF;
            color: #475569;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
          }}
          .btn-stop-action:hover {{ background: #F1F5F9; color: #0F172A; }}
          .quote-text {{
            font-size: 13.5px;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.45;
          }}
        </style>
        </head>
        <body>
          <div class="confirm-card">
            <div class="confirm-header">
              <div class="title-group">
                <span style="color:#0284C7; font-size:15px;">🔊</span>
                <span class="title-text">Spoken Route Confirmation ({v_ans_lang})</span>
                <span class="badge-activated">✓ Vocal Route Activated</span>
              </div>
              <div class="actions-group">
                <button type="button" class="btn-audio-action" id="btn-conf-play" onclick="toggleConfAudio()">
                  <span id="conf-icon">▶</span>
                  <span id="conf-label">Listen Aloud / ಧ್ವನಿ ಕೇಳಿ</span>
                </button>
                <button type="button" class="btn-stop-action" onclick="stopConfAudio()">
                  <span>⏹</span> Stop
                </button>
              </div>
            </div>
            <div class="quote-text">
              "{v_ans_text}"
            </div>
          </div>

          <script>
            const b64Data = "{b64_ans_audio}";
            const textToSpeak = {escaped_v_ans};
            const langCode = "{v_lang_code}";
            let audioObj = null;
            let isPlaying = false;

            if (b64Data && b64Data.length > 50) {{
              try {{
                audioObj = new Audio("data:audio/mp3;base64," + b64Data);
                audioObj.onended = () => resetConfUI();
                audioObj.onerror = () => audioObj = null;
              }} catch(e) {{ audioObj = null; }}
            }}

            function resetConfUI() {{
              isPlaying = false;
              const btn = document.getElementById("btn-conf-play");
              const icon = document.getElementById("conf-icon");
              const label = document.getElementById("conf-label");
              if (btn) btn.classList.remove("playing");
              if (icon) icon.innerText = "▶";
              if (label) label.innerText = "Listen Aloud / ಧ್ವನಿ ಕೇಳಿ";
            }}

            function toggleConfAudio() {{
              if (isPlaying) {{
                stopConfAudio();
                return;
              }}
              playConfAudio();
            }}

            function playConfAudio() {{
              stopConfAudio();
              isPlaying = true;
              const btn = document.getElementById("btn-conf-play");
              const icon = document.getElementById("conf-icon");
              const label = document.getElementById("conf-label");
              if (btn) btn.classList.add("playing");
              if (icon) icon.innerText = "⏸";
              if (label) label.innerText = "Pause / ವಿರಾಮ";

              if (audioObj) {{
                audioObj.currentTime = 0;
                audioObj.play().catch(e => {{
                  fallbackConfSpeech();
                }});
              }} else {{
                fallbackConfSpeech();
              }}
            }}

            function fallbackConfSpeech() {{
              if (!window.speechSynthesis) return;
              try {{
                window.speechSynthesis.cancel();
                window.speechSynthesis.resume();
                const u = new SpeechSynthesisUtterance(textToSpeak);
                u.lang = langCode;
                u.rate = 0.95;
                const voices = window.speechSynthesis.getVoices() || [];
                const prefix = langCode.split('-')[0].toLowerCase();
                const match = voices.find(v => v.lang && (v.lang.toLowerCase() === langCode.toLowerCase() || v.lang.toLowerCase().startsWith(prefix)));
                if (match) u.voice = match;
                u.onend = () => resetConfUI();
                u.onerror = () => resetConfUI();
                window.speechSynthesis.speak(u);
              }} catch(err) {{
                resetConfUI();
              }}
            }}

            function stopConfAudio() {{
              if (audioObj) {{
                try {{ audioObj.pause(); audioObj.currentTime = 0; }} catch(e) {{}}
              }}
              if (window.speechSynthesis) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
              }}
              resetConfUI();
            }}

            // Auto-play immediately on load
            setTimeout(() => {{
              playConfAudio();
            }}, 200);
          </script>
        </body>
        </html>
        """
        components.html(confirm_component_html, height=105, scrolling=False)

    # Suggested / Alternative Destinations from Voice Query (Interactive 1-Click Options)
    if st.session_state.get("suggested_destinations"):
        sugg_list = st.session_state.get("suggested_destinations", [])
        if sugg_list:
            st.markdown(
                f"<div style='background:#F0F9FF; border:1px solid #BAE6FD; border-radius:8px; padding:10px 14px; margin-bottom:12px;'>"
                f"<div style='font-size:12.5px; font-weight:800; color:#0369A1; margin-bottom:6px; display:flex; align-items:center; gap:6px;'>"
                f"{get_svg_icon('compass', size=15, color='#0284C7')} <span>Alternative Voice Matches — Tap to switch route instantly:</span>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            sugg_cols = st.columns(min(len(sugg_list), 4), gap="small")
            for s_idx, cand in enumerate(sugg_list[:4]):
                with sugg_cols[s_idx % len(sugg_cols)]:
                    c_lbl = format_room_label(cand, active_lang)
                    if st.button(f"📍 {c_lbl}", key=f"sugg_dest_btn_{s_idx}_{cand[:10]}", use_container_width=True):
                        set_route_endpoint(cand, "destination", trigger_speech=True)

    # ----------------------------------------------------
    # Active Wayfinding Route Selector (Source & Destination)
    # ----------------------------------------------------
    all_loc_names = sorted(graph_engine.locations_dict.keys())
    p_ver = st.session_state.get("planner_version", 0)

    stage3_route_titles = {
        "English": ("🧭 Change Route Endpoints", "Easily change your starting location or destination to update directions:"),
        "Kannada": ("🧭 ಮಾರ್ಗ ಬದಲಾಯಿಸಿ (ಪ್ರಾರಂಭ ಹಾಗೂ ಗಮ್ಯಸ್ಥಾನ)", "ಹೊಸ ನಡಿಗೆ ಮಾರ್ಗದರ್ಶನವನ್ನು ಪಡೆಯಲು ಪ್ರಾರಂಭದ ಸ್ಥಳ ಅಥವಾ ಗಮ್ಯಸ್ಥಾನವನ್ನು ಬದಲಾಯಿಸಿ:"),
        "Hindi": ("🧭 मार्ग बदलें (शुरुआती बिंदु और गंतव्य)", "पैदल मार्गदर्शन अपडेट करने के लिए अपना शुरुआती स्थान या गंतव्य बदलें:")
    }
    s3_rt_title, s3_rt_sub = stage3_route_titles.get(active_lang, stage3_route_titles["English"])

    src_label = {
        "English": "🚩 Starting Point (Source):",
        "Kannada": "🚩 ಪ್ರಾರಂಭದ ಸ್ಥಳ (Source):",
        "Hindi": "🚩 शुरुआती बिंदु (Source):"
    }.get(active_lang, "🚩 Starting Point (Source):")

    dst_label = {
        "English": "🎯 Destination:",
        "Kannada": "🎯 ಗಮ್ಯಸ್ಥಾನ (Destination):",
        "Hindi": "🎯 गंतव्य (Destination):"
    }.get(active_lang, "🎯 Destination:")

    def format_loc_choice(loc_name: str) -> str:
        loc_meta = graph_engine.locations_dict.get(loc_name, {})
        fl = loc_meta.get("floor", 0)
        fl_str = floor_labels_localized.get(fl, f"Floor {fl}")
        lbl = format_room_label(loc_name, active_lang)
        return f"{lbl} ({fl_str})"

    with st.container(border=True):
        render_html(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:4px;">
            <div style="font-size:13.5px; font-weight:800; color:#0369A1; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px;">
                {get_svg_icon('compass', size=16, color='#0284C7')}
                <span>{s3_rt_title}</span>
            </div>
            <div style="font-size:12px; color:#64748B; font-weight:500;">
                {s3_rt_sub}
            </div>
        </div>
        """)

        col_s3_orig, col_s3_swap, col_s3_dest, col_s3_wc = st.columns([2.4, 0.7, 2.4, 1.2], gap="small")

        with col_s3_orig:
            orig_idx = all_loc_names.index(start_node) if start_node in all_loc_names else 0
            new_s3_orig = st.selectbox(
                src_label,
                options=all_loc_names,
                index=orig_idx,
                format_func=format_loc_choice,
                key=f"stg3_src_sel_{p_ver}"
            )

        with col_s3_swap:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("⇄ Swap", key=f"btn_stg3_swap_{p_ver}", use_container_width=True, help="Swap starting point and destination"):
                handle_swap_locations()

        with col_s3_dest:
            dest_idx = all_loc_names.index(dest_node) if dest_node in all_loc_names else 0
            new_s3_dest = st.selectbox(
                dst_label,
                options=all_loc_names,
                index=dest_idx,
                format_func=format_loc_choice,
                key=f"stg3_dst_sel_{p_ver}"
            )

        with col_s3_wc:
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
            wc_stg3 = st.checkbox(
                t["wheelchair_label"],
                value=st.session_state.get("wheelchair_state", False),
                key=f"wc_stg3_check_{p_ver}"
            )
            if wc_stg3 != st.session_state.get("wheelchair_state", False):
                st.session_state["wheelchair_state"] = wc_stg3
                st.rerun()

        if new_s3_orig != start_node:
            set_route_endpoint(new_s3_orig, "origin")
        elif new_s3_dest != dest_node:
            set_route_endpoint(new_s3_dest, "destination")

    if start_node == dest_node:
        same_dest_warn = {
            "English": f"🚩 Starting point and 🎯 Destination are both set to **{start_node}**.",
            "Kannada": f"🚩 ಪ್ರಾರಂಭದ ಸ್ಥಳ ಮತ್ತು 🎯 ಗಮ್ಯಸ್ಥಾನ ಎರಡೂ **{start_node}** ಆಗಿದೆ.",
            "Hindi": f"🚩 शुरुआती बिंदु और 🎯 गंतव्य दोनों **{start_node}** हैं।"
        }
        st.warning(same_dest_warn.get(active_lang, same_dest_warn["English"]))
        st.markdown(
            "<div style='font-size:13px; color:#475569; margin-bottom:10px;'>"
            "Choose a quick option below to immediately generate turn-by-turn walking instructions:"
            "</div>",
            unsafe_allow_html=True
        )
        c_fix1, c_fix2, c_fix3 = st.columns(3, gap="small")
        with c_fix1:
            alt_d = "Central Library" if start_node != "Central Library" else "Classroom G11"
            if st.button(f"🧭 Walk from {start_node[:14]} → {alt_d}", key="btn_fix_dest", type="primary", use_container_width=True):
                set_route_endpoint(alt_d, "destination")
        with c_fix2:
            alt_o = "Main Gate" if start_node != "Main Gate" else "Quadrangle"
            if st.button(f"🧭 Walk from {alt_o} → {start_node[:14]}", key="btn_fix_orig", type="primary", use_container_width=True):
                set_route_endpoint(alt_o, "origin")
        with c_fix3:
            if st.button("🏢 Change in Browse Directory", key="btn_fix_browse", use_container_width=True):
                st.session_state["app_step"] = 2
                st.session_state["input_mode"] = "browse"
                st.rerun()
        st.stop()

    current_route_signature = f"{start_node}->{dest_node}->{st.session_state.get('wheelchair_state', False)}->{active_lang}"
    if st.session_state.get("active_route_signature") != current_route_signature:
        st.session_state["active_route_signature"] = current_route_signature
        st.session_state["current_step_index"] = 0
        st.session_state["completed_steps"] = []
        st.session_state["recovery_mode"] = False
        st.session_state["auto_speech"] = False

    try:
        path, total_distance, weighted_cost = graph_engine.find_shortest_path(
            start_node=start_node,
            dest_node=dest_node,
            wheelchair_mode=st.session_state["wheelchair_state"],
            crowd_multiplier=1.0
        )

        start_info = graph_engine.locations_dict.get(start_node, {})
        dest_info = graph_engine.locations_dict.get(dest_node, {})
        start_floor = start_info.get("floor", 0)
        dest_floor = dest_info.get("floor", 0)

        floor_changes = sum(
            1 for i in range(len(path) - 1)
            if graph_engine.locations_dict[path[i]]["floor"] != graph_engine.locations_dict[path[i+1]]["floor"]
        )

        eta = nlg_engine.calculate_eta(total_distance, floor_changes, st.session_state["wheelchair_state"])
        steps = nlg_engine.generate_turn_by_turn(path, graph_engine.graph, language=active_lang, wheelchair_mode=st.session_state["wheelchair_state"])

        if not steps:
            arrived_msg = {
                "English": f"You are already at {dest_node}.",
                "Kannada": f"ನೀವು ಈಗಾಗಲೇ {dest_node} ನಲ್ಲಿ ಇದ್ದೀರಿ.",
                "Hindi": f"आप पहले से ही {dest_node} पर मौजूद हैं।"
            }.get(active_lang, f"You are already at {dest_node}.")
            steps = [{
                "step": 1,
                "from": start_node,
                "to": dest_node,
                "distance": 0.0,
                "action": "Arrived",
                "checkpoint_title": f"🎯 {dest_node}",
                "landmark_name": dest_node,
                "verification": arrived_msg,
                "instruction": arrived_msg,
                "audio_text": arrived_msg,
                "icon": "🎯",
                "floor": dest_floor
            }]

        total_steps = len(steps)
        current_idx = max(0, min(st.session_state.get("current_step_index", 0), total_steps - 1))
        st.session_state["current_step_index"] = current_idx
        active_step = steps[current_idx]
        is_last_step = (current_idx == total_steps - 1)
        progress_pct = int(((current_idx + 1) / total_steps) * 100)

        start_display = format_room_label(start_node, active_lang)
        dest_display = format_room_label(dest_node, active_lang)
        start_fl_label = floor_labels_localized.get(start_floor, f"Floor {start_floor}")
        dest_fl_label = floor_labels_localized.get(dest_floor, f"Floor {dest_floor}")

        wc_tag = icon_badge('wheelchair', t['wheelchair_label'], bg='#ECFDF5', color='#065F46', border='#A7F3D0') if st.session_state['wheelchair_state'] else ""
        floor_tag = icon_badge('stairs', f"{start_fl_label} → {dest_fl_label}", bg='#EFF6FF', color='#1D4ED8', border='#BFDBFE')

        # Journey Summary Box
        render_html(f"""
        <div class="journey-summary-box" style="margin-top:8px;">
            <div class="journey-header">
                <div>
                    <div class="journey-title" style="display:flex; align-items:center; gap:8px;">
                        {get_svg_icon('route', size=20, color='#0284C7')}
                        <span>{t['journey_title']}</span>
                    </div>
                    <div class="journey-route-tag" style="margin-top:4px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                        <span style="display:inline-flex; align-items:center; gap:5px; color:#991B1B;">
                            {get_svg_icon('flag', size=16, color='#DC2626')} {start_display}
                        </span>
                        <span style="color:#64748B;">{get_svg_icon('arrow_right', size=13, color='#64748B')}</span>
                        <span style="display:inline-flex; align-items:center; gap:5px; color:#065F46;">
                            {get_svg_icon('target', size=16, color='#059669')} {dest_display}
                        </span>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                    {floor_tag}
                    {wc_tag}
                </div>
            </div>
            <div class="journey-metrics">
                <div class="metric-pill">
                    <div class="metric-pill-label" style="display:flex; align-items:center; gap:4px;">
                        {get_svg_icon('ruler', size=12, color='#64748B')} {t['total_dist']}
                    </div>
                    <div class="metric-pill-value">{int(total_distance)} m</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-pill-label" style="display:flex; align-items:center; gap:4px;">
                        {get_svg_icon('clock', size=12, color='#64748B')} {t['est_time']}
                    </div>
                    <div class="metric-pill-value">~{eta} min</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-pill-label" style="display:flex; align-items:center; gap:4px;">
                        {get_svg_icon('stairs', size=12, color='#64748B')} {t['floor_changes']}
                    </div>
                    <div class="metric-pill-value">{floor_changes} {'(Stairs/Elevator)' if floor_changes > 0 else '(Level)'}</div>
                </div>
                <div class="metric-pill">
                    <div class="metric-pill-label" style="display:flex; align-items:center; gap:4px;">
                        {get_svg_icon('check_circle', size=12, color='#64748B')} {t['checkpoint_prog']}
                    </div>
                    <div class="metric-pill-value">{t['step_x_of_y'].format(current=current_idx + 1, total=total_steps)}</div>
                </div>
            </div>
        </div>
        """)

        # Interactive Checkpoint Stepper Rail
        stepper_html = '<div class="checkpoint-progress-rail">'
        for i, s in enumerate(steps):
            s_step_num = i + 1
            s_title = format_room_label(s.get('to', f'Step {s_step_num}'), active_lang)
            if i in st.session_state.get("completed_steps", []) and i != current_idx:
                chk_svg = get_svg_icon('check', size=12, color='#065F46')
                stepper_html += f'<span class="stepper-pill completed">{chk_svg} {t["step_x_of_y"].format(current=s_step_num, total=total_steps)}: {s_title}</span>'
            elif i == current_idx:
                tgt_svg = get_svg_icon('target', size=13, color='#FFFFFF')
                stepper_html += f'<span class="stepper-pill active">{tgt_svg} {t["checkpoint_active"]}: {s_step_num}</span>'
            else:
                cir_svg = get_svg_icon('circle', size=11, color='#94A3B8')
                stepper_html += f'<span class="stepper-pill pending">{cir_svg} {s_step_num}: {s_title}</span>'
        stepper_html += '</div>'
        render_html(stepper_html)

        # Synchronized Progress Bar
        st.progress(progress_pct / 100.0)

        # Spoken Audio Text & TTS Generation
        active_speech_text = active_step.get("audio_text", active_step.get("instruction", ""))
        should_play_speech = st.session_state.get("auto_speech", False)
        if should_play_speech:
            st.session_state["auto_speech"] = False

        step_audio_bytes = generate_step_audio(active_speech_text, active_lang)
        b64_step_audio = base64.b64encode(step_audio_bytes).decode('ascii') if step_audio_bytes else ""
        step_lang_code = {"Kannada": "kn-IN", "Hindi": "hi-IN", "English": "en-IN"}.get(active_lang, "en-IN")
        escaped_step_text = json.dumps(active_speech_text)
        auto_play_js = "true" if should_play_speech else "false"
        voice_guide_title = t.get('voice_assistant_title', 'Voice Guide')

        guide_component_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
          body {{ background: transparent; overflow: hidden; padding: 2px; }}
          .voice-guide-bar {{
            background: #FFFFFF;
            border: 1.5px solid #0284C7;
            border-radius: 10px;
            padding: 8px 14px;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 48px;
          }}
          .vg-left {{
            display: flex;
            align-items: center;
            gap: 10px;
          }}
          .vg-icon-box {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: #EFF6FF;
            border: 1px solid #BAE6FD;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0284C7;
            font-size: 15px;
          }}
          .vg-title-group {{
            display: flex;
            flex-direction: column;
            gap: 2px;
          }}
          .vg-title {{
            font-size: 12px;
            font-weight: 800;
            color: #0369A1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
          }}
          .vg-status {{
            font-size: 11px;
            color: #64748B;
            font-weight: 600;
          }}
          .sound-wave {{
            display: none;
            align-items: center;
            gap: 3px;
            height: 14px;
          }}
          .sound-wave.active {{
            display: inline-flex;
          }}
          .wave-bar {{
            width: 3px;
            height: 100%;
            background: #0284C7;
            border-radius: 1px;
            animation: wave 0.7s ease-in-out infinite alternate;
          }}
          .wave-bar:nth-child(2) {{ animation-delay: 0.2s; }}
          .wave-bar:nth-child(3) {{ animation-delay: 0.4s; }}
          @keyframes wave {{
            0% {{ height: 25%; }}
            100% {{ height: 100%; }}
          }}
          .vg-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
          }}
          .btn-play-guide {{
            background: #0284C7;
            color: #FFFFFF !important;
            border: none;
            border-radius: 6px;
            padding: 7px 16px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 1px 4px rgba(2, 132, 199, 0.25);
            transition: all 0.15s ease;
          }}
          .btn-play-guide:hover {{ background: #0369A1; transform: translateY(-1px); }}
          .btn-play-guide:active {{ transform: translateY(1px); }}
          .btn-play-guide.playing {{ background: #D97706 !important; }}
          .btn-stop-guide {{
            background: #F8FAFC;
            color: #475569;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 7px 12px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
          }}
          .btn-stop-guide:hover {{ background: #F1F5F9; color: #0F172A; }}
        </style>
        </head>
        <body>
          <div class="voice-guide-bar">
            <div class="vg-left">
              <div class="vg-icon-box">🔊</div>
              <div class="vg-title-group">
                <div class="vg-title">
                  <span>{voice_guide_title} ({active_lang})</span>
                  <div class="sound-wave" id="wave-anim">
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                    <div class="wave-bar"></div>
                  </div>
                </div>
                <div class="vg-status" id="vg-status-text">Click 'Listen Aloud' to hear spoken directions</div>
              </div>
            </div>
            <div class="vg-actions">
              <button type="button" class="btn-play-guide" id="btn-guide-play" onclick="toggleGuideAudio()">
                <span id="guide-icon">▶</span>
                <span id="guide-label">Listen Aloud / ಧ್ವನಿ ಕೇಳಿ</span>
              </button>
              <button type="button" class="btn-stop-guide" onclick="stopGuideAudio()">
                <span>⏹</span> Stop
              </button>
            </div>
          </div>

          <script>
            const b64Audio = "{b64_step_audio}";
            const stepText = {escaped_step_text};
            const langCode = "{step_lang_code}";
            const autoPlayOnLoad = {auto_play_js};

            let audioObj = null;
            let isPlaying = false;

            if (b64Audio && b64Audio.length > 50) {{
              try {{
                audioObj = new Audio("data:audio/mp3;base64," + b64Audio);
                audioObj.onended = () => resetGuideUI();
                audioObj.onerror = () => audioObj = null;
              }} catch(e) {{ audioObj = null; }}
            }}

            function resetGuideUI() {{
              isPlaying = false;
              const btn = document.getElementById("btn-guide-play");
              const icon = document.getElementById("guide-icon");
              const label = document.getElementById("guide-label");
              const wave = document.getElementById("wave-anim");
              const status = document.getElementById("vg-status-text");

              if (btn) btn.classList.remove("playing");
              if (icon) icon.innerText = "▶";
              if (label) label.innerText = "Listen Aloud / ಧ್ವನಿ ಕೇಳಿ";
              if (wave) wave.classList.remove("active");
              if (status) status.innerText = "Instruction playback completed.";
            }}

            function toggleGuideAudio() {{
              if (isPlaying) {{
                stopGuideAudio();
                return;
              }}
              playGuideAudio();
            }}

            function playGuideAudio() {{
              stopGuideAudio();
              isPlaying = true;
              const btn = document.getElementById("btn-guide-play");
              const icon = document.getElementById("guide-icon");
              const label = document.getElementById("guide-label");
              const wave = document.getElementById("wave-anim");
              const status = document.getElementById("vg-status-text");

              if (btn) btn.classList.add("playing");
              if (icon) icon.innerText = "⏸";
              if (label) label.innerText = "Pause / ವಿರಾಮ";
              if (wave) wave.classList.add("active");
              if (status) status.innerText = "🔊 Speaking checkpoint directions...";

              if (audioObj) {{
                audioObj.currentTime = 0;
                audioObj.play().catch(e => {{
                  fallbackGuideSpeech();
                }});
              }} else {{
                fallbackGuideSpeech();
              }}
            }}

            function fallbackGuideSpeech() {{
              if (!window.speechSynthesis) return;
              try {{
                window.speechSynthesis.cancel();
                window.speechSynthesis.resume();
                const u = new SpeechSynthesisUtterance(stepText);
                u.lang = langCode;
                u.rate = 0.95;
                const voices = window.speechSynthesis.getVoices() || [];
                const prefix = langCode.split('-')[0].toLowerCase();
                const match = voices.find(v => v.lang && (v.lang.toLowerCase() === langCode.toLowerCase() || v.lang.toLowerCase().startsWith(prefix)));
                if (match) u.voice = match;
                u.onend = () => resetGuideUI();
                u.onerror = () => resetGuideUI();
                window.speechSynthesis.speak(u);
              }} catch(err) {{
                resetGuideUI();
              }}
            }}

            function stopGuideAudio() {{
              if (audioObj) {{
                try {{ audioObj.pause(); audioObj.currentTime = 0; }} catch(e) {{}}
              }}
              if (window.speechSynthesis) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
              }}
              resetGuideUI();
              const status = document.getElementById("vg-status-text");
              if (status) status.innerText = "Audio stopped. Click Listen Aloud to replay.";
            }}

            if (autoPlayOnLoad) {{
              setTimeout(() => {{
                playGuideAudio();
              }}, 200);
            }}
          </script>
        </body>
        </html>
        """
        components.html(guide_component_html, height=58, scrolling=False)

        # Live Listening Banner if mic is active in navigation
        if st.session_state.get("mic_active") == "navigation":
            render_live_mic_banner(active_lang, key_suffix="navigation")

        # Active Checkpoint Hero Card (Showing ONLY the active checkpoint)
        clean_instruction = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(active_step.get('instruction', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
        clean_verification = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(active_step.get('verification', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
        step_icon = active_step.get('icon', 'walk')
        step_floor = active_step.get('floor', dest_floor)
        step_dist = active_step.get('distance', 0)
        step_fl_label = floor_labels_localized.get(step_floor, f"Floor {step_floor}")
        step_svg = get_svg_icon(step_icon, size=28, color='#0284C7')

        render_html(f"""
        <div class="checkpoint-hero-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="background:#EFF6FF; border:1.5px solid #BAE6FD; border-radius:10px; padding:10px; display:flex; align-items:center; justify-content:center; color:#0284C7; box-shadow:0 2px 6px rgba(2,132,199,0.12);">
                        {step_svg}
                    </div>
                    <div>
                        <div style="font-size:11px; font-weight:800; color:#0284C7; letter-spacing:0.6px; text-transform:uppercase;">
                            {t['checkpoint_active']} &bull; {t['step_x_of_y'].format(current=current_idx + 1, total=total_steps).upper()}
                        </div>
                        <div style="font-size:18px; font-weight:800; color:#0F172A;">
                            {active_step.get('checkpoint_title', f'Checkpoint {current_idx + 1}')}
                        </div>
                    </div>
                </div>
                <div style="display:flex; gap:6px;">
                    {icon_badge('layers', step_fl_label, bg='#EFF6FF', color='#1D4ED8', border='#BFDBFE')}
                    {icon_badge('walk', f'{step_dist}m', bg='#F0FDF4', color='#065F46', border='#BBF7D0')}
                </div>
            </div>

            <div style="font-size:16px; line-height:1.6; color:#0F172A; font-weight:600; padding:12px 14px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;">
                {clean_instruction}
            </div>

            <div class="landmark-box">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="color:#92400E;">{get_svg_icon('landmark', size=18, color='#92400E')}</span>
                    <span style="font-size:12.5px; font-weight:800; color:#92400E; letter-spacing:0.5px; text-transform:uppercase;">
                        {t['landmark_box_title']}
                    </span>
                </div>
                <div style="font-size:13.5px; color:#78350F; line-height:1.55; font-weight:500;">
                    {clean_verification}
                </div>
                <div style="font-size:12px; color:#B45309; font-weight:700; margin-top:8px; display:flex; align-items:center; gap:6px;">
                    {get_svg_icon('alert', size=14, color='#B45309')}
                    <span>{t['orientation_rule']}</span>
                </div>
            </div>
        </div>
        """)

        # Single-Tap Action Buttons
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.1, 1.2, 1.8, 1.3], gap="small")

        with btn_col1:
            prev_disabled = (current_idx == 0)
            if st.button(t["btn_prev"], key="btn_prev_step", disabled=prev_disabled, use_container_width=True):
                st.session_state["current_step_index"] = max(0, current_idx - 1)
                st.session_state["auto_speech"] = True
                st.rerun()

        with btn_col2:
            if st.button(t["btn_repeat"], key="btn_repeat_step", use_container_width=True):
                st.session_state["auto_speech"] = True
                st.rerun()

        with btn_col3:
            if is_last_step:
                if st.button(t["btn_arrived"], key="btn_finish_step", type="primary", use_container_width=True):
                    if current_idx not in st.session_state["completed_steps"]:
                        st.session_state["completed_steps"].append(current_idx)
                    st.session_state["auto_speech"] = False
                    st.balloons()
                    st.success(f"🎉 {dest_display}!")
                    st.rerun()
            else:
                if st.button(t["btn_next"], key="btn_next_step", type="primary", use_container_width=True):
                    if current_idx not in st.session_state["completed_steps"]:
                        st.session_state["completed_steps"].append(current_idx)
                    st.session_state["current_step_index"] = min(total_steps - 1, current_idx + 1)
                    st.session_state["auto_speech"] = True
                    st.rerun()

        with btn_col4:
            lost_label = t["btn_close_help"] if st.session_state["recovery_mode"] else t["btn_lost"]
            if st.button(lost_label, key="btn_lost_user", use_container_width=True):
                st.session_state["recovery_mode"] = not st.session_state["recovery_mode"]
                st.rerun()

        # Orientation Recovery / Lost User Panel
        if st.session_state["recovery_mode"]:
            render_html(f"""
            <div class="recovery-card" style="margin-top:12px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="color:#DC2626;">{get_svg_icon('lifebuoy', size=22, color='#DC2626')}</span>
                    <span style="font-size:16px; font-weight:800; color:#991B1B;">{t['lost_title']}</span>
                </div>
                <div style="font-size:13.5px; color:#7F1D1D; line-height:1.5;">
                    {t['lost_sub']}
                </div>
            </div>
            """)

            all_locs = sorted(graph_engine.locations_dict.keys())
            active_floor = active_step.get("floor", start_floor)
            floor_locs = [loc for loc in all_locs if graph_engine.locations_dict[loc].get("floor") == active_floor]
            other_locs = [loc for loc in all_locs if loc not in floor_locs]
            ordered_options = floor_locs + other_locs

            r_col1, r_col2, r_col3 = st.columns([2.2, 1.8, 1])
            with r_col1:
                recov_landmark = st.selectbox(
                    t["lost_picker_label"],
                    options=ordered_options,
                    format_func=lambda rm: format_room_label(rm, active_lang),
                    key="recovery_landmark_picker"
                )
            with r_col2:
                st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                if st.button(t["lost_recalc_btn"], key="btn_recalc_route", type="primary", use_container_width=True):
                    st.session_state["current_origin"] = recov_landmark
                    st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
                    st.session_state["current_step_index"] = 0
                    st.session_state["completed_steps"] = []
                    st.session_state["recovery_mode"] = False
                    st.session_state["auto_speech"] = True
                    st.rerun()
            with r_col3:
                st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                if st.button(t["lost_cancel_btn"], key="btn_cancel_recov", use_container_width=True):
                    st.session_state["recovery_mode"] = False
                    st.rerun()

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------
        # COMPLETE STEP-BY-STEP WALKING INSTRUCTIONS LIST (Open & Prominently Displayed)
        # -------------------------------------------------------------------------
        steps_heading = {
            "English": ("Step-by-Step Walking Instructions", f"Follow all {total_steps} sequential instructions from start to destination:"),
            "Kannada": ("ಹಂತ-ಹಂತದ ನಡಿಗೆ ಮಾರ್ಗದರ್ಶನ ಸೂಚನೆಗಳು", f"ಪ್ರಾರಂಭದಿಂದ ಗಮ್ಯಸ್ಥಾನದವರೆಗಿನ ಎಲ್ಲಾ {total_steps} ಹಂತಗಳ ಅನುಕ್ರಮ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ:"),
            "Hindi": ("कदम-दर-कदम पैदल मार्गदर्शन निर्देश", f"शुरुआत से गंतव्य तक सभी {total_steps} क्रमिक निर्देशों का पालन करें:")
        }
        sh_title, sh_sub = steps_heading.get(active_lang, steps_heading["English"])

        render_html(f"""
        <div style="margin-top:22px; margin-bottom:14px; border-bottom:1.8px solid #E2E8F0; padding-bottom:8px; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:#0284C7;">{get_svg_icon('list', size=20, color='#0284C7')}</span>
                <div>
                    <div style="font-size:17px; font-weight:800; color:#0F172A;">{sh_title}</div>
                    <div style="font-size:12.5px; color:#64748B; font-weight:500;">{sh_sub}</div>
                </div>
            </div>
            <div style="font-size:12px; font-weight:700; color:#0284C7; background:#EFF6FF; border:1px solid #BFDBFE; padding:3px 10px; border-radius:12px;">
                {total_steps} Steps ({int(total_distance)}m total)
            </div>
        </div>
        """)

        for idx, step in enumerate(steps, 1):
            clean_step_inst = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(step.get('instruction', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
            clean_step_verif = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(step.get('verification', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
            is_step_active = (idx - 1 == current_idx)
            is_step_done = (idx - 1 in st.session_state.get("completed_steps", []))

            border_color = "#0284C7" if is_step_active else ("#10B981" if is_step_done else "#CBD5E1")
            bg_color = "#F0F9FF" if is_step_active else ("#F0FDF4" if is_step_done else "#FFFFFF")
            box_shadow = "0 3px 12px rgba(2,132,199,0.12)" if is_step_active else "0 1px 3px rgba(0,0,0,0.03)"
            status_tag = f"ACTIVE &bull; {t['checkpoint_active']}" if is_step_active else ("✓ COMPLETED" if is_step_done else t['step_x_of_y'].format(current=idx, total=total_steps))
            st_fl_label = floor_labels_localized.get(step.get('floor', 0), f"Floor {step.get('floor', 0)}")
            s_icon_svg = get_svg_icon(step.get('icon', 'walk'), size=16, color=border_color)

            col_step_card, col_step_btn = st.columns([4.2, 0.8], gap="small")
            with col_step_card:
                render_html(f"""
                <div style="border:1.8px solid {border_color}; background:{bg_color}; border-radius:10px; padding:12px 16px; margin-bottom:8px; box-shadow:{box_shadow};">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; flex-wrap:wrap; gap:6px;">
                        <span style="font-size:12.5px; font-weight:800; color:{border_color}; display:inline-flex; align-items:center; gap:6px;">
                            {s_icon_svg} <span>{status_tag}</span>
                        </span>
                        <div style="display:flex; gap:6px;">
                            {icon_badge('layers', st_fl_label, bg='#FFFFFF', color='#334155', border='#CBD5E1', size=11)}
                            {icon_badge('walk', f"{step.get('distance', 0)}m", bg='#FFFFFF', color='#334155', border='#CBD5E1', size=11)}
                        </div>
                    </div>
                    <div style="font-size:14px; color:#0F172A; font-weight:600; line-height:1.5;">
                        {clean_step_inst}
                    </div>
                    <div style="font-size:12px; color:#78350F; background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:6px 10px; margin-top:8px; display:flex; align-items:center; gap:6px;">
                        <span style="color:#B45309;">{get_svg_icon('landmark', size=14, color='#B45309')}</span>
                        <span><strong>Landmark Check:</strong> {clean_step_verif}</span>
                    </div>
                </div>
                """)
            with col_step_btn:
                if not is_step_active:
                    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
                    if st.button(f"👉 Step {idx}", key=f"btn_jump_step_{idx}", use_container_width=True, help=f"View Step {idx}"):
                        st.session_state["current_step_index"] = idx - 1
                        st.session_state["auto_speech"] = True
                        st.rerun()
                else:
                    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
                    st.markdown("<div style='text-align:center; font-size:11px; font-weight:800; color:#0284C7; background:#EFF6FF; border:1px solid #BFDBFE; border-radius:6px; padding:6px 2px;'>ACTIVE</div>", unsafe_allow_html=True)

        with st.expander("🏢 Campus Floor Directory & Institutional Reference Tables", expanded=False):
            render_floor_directory_component("stage3_expander")

            st.markdown(f"<div style='font-size:14px; font-weight:700; color:#0F172A; margin-top:14px; margin-bottom:6px;'>{t['explore_floors_title']}</div>", unsafe_allow_html=True)
            floor_descriptions = {
                0: (f"🌿 {t['floor_0_label']}", t['floor_0_rooms']),
                1: (f"🔬 {t['floor_1_label']}", t['floor_1_rooms']),
                2: (f"💻 {t['floor_2_label']}", t['floor_2_rooms']),
                3: (f"🛋️ {t['floor_3_label']}", t['floor_3_rooms'])
            }
            for fl_idx in [0, 1, 2, 3]:
                fl_title, fl_sub = floor_descriptions[fl_idx]
                fl_rooms = get_floor_nodes(fl_idx)
                with st.expander(f"{fl_title} — ({len(fl_rooms)} Rooms)", expanded=False):
                    st.markdown(f"<div style='font-size:12px; color:#475569; margin-bottom:8px;'>{fl_sub}</div>", unsafe_allow_html=True)
                    fl_df = graph_engine.locations_df[graph_engine.locations_df["floor"] == fl_idx][["location_name", "category", "block", "is_accessible"]].copy()
                    fl_df.columns = ["Location Name", "Category", "Wing / Block", "Wheelchair Accessible"]
                    fl_df["Wheelchair Accessible"] = fl_df["Wheelchair Accessible"].apply(lambda a: "♿ Accessible" if a else "Stairs Only")
                    st.markdown(fl_df.to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

            st.markdown("<div style='font-size:14px; font-weight:700; color:#0F172A; margin-top:14px; margin-bottom:6px;'>Institutional Reference Data</div>", unsafe_allow_html=True)
            t_col1, t_col2 = st.columns(2, gap="medium")
            with t_col1:
                st.markdown("<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:4px;'>Academic Departments</div>", unsafe_allow_html=True)
                dept_csv = os.path.join(DATA_DIR, "departments.csv")
                dept_df = pd.read_csv(dept_csv)
                st.markdown(dept_df[["department_name", "block", "floor", "hod_name", "contact_email"]].to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

            with t_col2:
                st.markdown("<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:4px;'>Classrooms & Lecture Halls</div>", unsafe_allow_html=True)
                cr_csv = os.path.join(DATA_DIR, "classrooms.csv")
                cr_df = pd.read_csv(cr_csv)
                st.markdown(cr_df[["room_number", "room_name", "block", "floor", "capacity", "facilities"]].to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

    except nx.NetworkXNoPath:
        st.error(
            f"No accessible route found between **{start_node}** and **{dest_node}**. "
            "Try turning off wheelchair-only mode if this wing only has stairs."
        )
        if st.button("✏️ Choose Different Destination", key="btn_nopath_back"):
            st.session_state["app_step"] = 2
            st.rerun()

