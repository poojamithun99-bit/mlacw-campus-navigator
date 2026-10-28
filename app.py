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

from ui_strings import UI_STRINGS
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

def handle_voice_query_action(q_text: str):
    if not q_text or not str(q_text).strip():
        return
    clean_q = str(q_text).strip()
    clean_cmd = clean_q.lower()

    # 1. Spoken Voice Navigation Commands
    if any(w in clean_cmd for w in ["next", "forward", "ಮುಂದೆ", "ಮುಂದಿನ", "आगे", "अगला", "done", "reached", "ತಲುಪಿದೆ", "पहुँच गए"]):
        curr_idx = st.session_state.get("current_step_index", 0)
        st.session_state["current_step_index"] = curr_idx + 1
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()
    elif any(w in clean_cmd for w in ["repeat", "again", "replay", "ಮತ್ತೊಮ್ಮೆ", "ಮತ್ತೆ", "ಪುನಃ", "दोहराएं", "फिर से"]):
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()
    elif any(w in clean_cmd for w in ["back", "previous", "ಹಿಂದೆ", "ಹಿಂದಿನ", "ಹಿಂತಿರುಗಿ", "पीछे", "पिछला"]):
        curr_idx = st.session_state.get("current_step_index", 0)
        st.session_state["current_step_index"] = max(0, curr_idx - 1)
        st.session_state["auto_speech"] = True
        st.session_state["mic_active"] = False
        st.rerun()
    elif any(w in clean_cmd for w in ["lost", "confused", "help", "ದಾರಿ ತಪ್ಪಿದೆ", "ಕಳೆದು", "ಸಹಾಯ", "खो गया", "भटक", "मदद"]):
        st.session_state["recovery_mode"] = True
        st.session_state["mic_active"] = False
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
    detected_language = parsed.get("detected_language", "English")
    matched_target = parsed.get("matched_node")

    if matched_target and matched_target in graph_engine.locations_dict:
        st.session_state["language"] = detected_language
        st.session_state["target_destination"] = matched_target
        st.session_state["current_step_index"] = 0
        st.session_state["completed_steps"] = []
        st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
        st.session_state["mic_active"] = False

        target_info = graph_engine.locations_dict.get(matched_target, {})
        orig_info = graph_engine.locations_dict.get(st.session_state["current_origin"], {})

        if detected_language == "Kannada":
            t_name = target_info.get("kannada_name") or matched_target
            o_name = orig_info.get("kannada_name") or st.session_state["current_origin"]
            spoken_ans = f"{t_name} ಗೆ ಮಾರ್ಗಸೂಚಿ ಸಿದ್ಧವಾಗಿದೆ. {o_name} ನಿಂದ ಪ್ರಾರಂಭಿಸಿ, ಕೆಳಗಿನ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ."
        elif detected_language == "Hindi":
            t_name = target_info.get("hindi_name") or matched_target
            o_name = orig_info.get("hindi_name") or st.session_state["current_origin"]
            spoken_ans = f"{t_name} के लिए नेविगेशन शुरू हो रहा है। {o_name} से शुरू करके नीचे दिए गए निर्देशों का पालन करें।"
        else:
            spoken_ans = f"Navigating to {matched_target}. Starting from {st.session_state['current_origin']}, follow the turn-by-turn guidance below."

        reply_audio = generate_step_audio(spoken_ans, detected_language)
        st.session_state["voice_assistant_response"] = (spoken_ans, detected_language, reply_audio)
        st.session_state["auto_speech"] = True
        st.rerun()
    else:
        if detected_language == "Kannada":
            err_ans = f"ಕ್ಷಮಿಸಿ, '{clean_q}' ಸ್ಥಳ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಲೈಬ್ರರಿ, ಜಿ11, ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ಅಥವಾ ಶೌಚಾಲಯ ಪ್ರಯತ್ನಿಸಿ."
        elif detected_language == "Hindi":
            err_ans = f"क्षमा करें, '{clean_q}' स्थान नहीं मिला। कृपया पुस्तकालय, जी11, कंप्यूटर साइंस या शौचालय बोलें।"
        else:
            err_ans = f"Sorry, could not find '{clean_q}'. Try asking for Library, Classroom G11, Computer Science, or Washroom."
        err_audio = generate_step_audio(err_ans, detected_language)
        st.session_state["voice_assistant_response"] = (err_ans, detected_language, err_audio)
        st.session_state["mic_active"] = False
        st.rerun()

def render_live_mic_banner(lang: str, key_suffix: str = "main"):
    lang_code = {"Kannada": "kn-IN", "Hindi": "hi-IN", "English": "en-IN"}.get(lang, "en-IN")
    render_html(f"""
    <style>
    .mic-live-banner {{
        background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%);
        border: 2px solid #E11D48;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 10px 0 12px 0;
        box-shadow: 0 4px 20px rgba(225, 29, 72, 0.22);
        animation: mic-pulse-border 1.6s infinite;
    }}
    @keyframes mic-pulse-border {{
        0% {{ box-shadow: 0 0 0 0 rgba(225, 29, 72, 0.45); }}
        70% {{ box-shadow: 0 0 0 10px rgba(225, 29, 72, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(225, 29, 72, 0); }}
    }}
    .mic-wave-container {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        height: 24px;
    }}
    .mic-wave-bar {{
        width: 4px;
        height: 100%;
        background: #E11D48;
        border-radius: 2px;
        animation: mic-wave-anim 0.8s ease-in-out infinite alternate;
    }}
    .mic-wave-bar:nth-child(1) {{ animation-delay: 0.1s; height: 35%; }}
    .mic-wave-bar:nth-child(2) {{ animation-delay: 0.3s; height: 75%; }}
    .mic-wave-bar:nth-child(3) {{ animation-delay: 0.2s; height: 100%; }}
    .mic-wave-bar:nth-child(4) {{ animation-delay: 0.4s; height: 60%; }}
    .mic-wave-bar:nth-child(5) {{ animation-delay: 0.15s; height: 40%; }}
    @keyframes mic-wave-anim {{
        0% {{ height: 25%; }}
        100% {{ height: 100%; }}
    }}
    </style>
    <div class="mic-live-banner">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div class="mic-wave-container">
                    <div class="mic-wave-bar"></div>
                    <div class="mic-wave-bar"></div>
                    <div class="mic-wave-bar"></div>
                    <div class="mic-wave-bar"></div>
                    <div class="mic-wave-bar"></div>
                </div>
                <div>
                    <div style="font-size:15px; font-weight:800; color:#9F1239; letter-spacing:0.3px;">
                        🔴 VOICE ASSISTANT LISTENING...
                    </div>
                    <div style="font-size:12px; font-weight:700; color:#BE123C; margin-top:2px;">
                        ಧ್ವನಿ ಆಲಿಸಲಾಗುತ್ತಿದೆ • बोलें, सिस्टम सुन रहा है...
                    </div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="font-size:11px; font-weight:700; color:#9F1239; background:#FFE4E6; border:1px solid #FECDD3; padding:4px 10px; border-radius:20px;">
                    Language: {lang} ({lang_code})
                </div>
            </div>
        </div>
        <div id="live-speech-box" style="margin-top:10px; background:#FFFFFF; border:1.5px dashed #F43F5E; border-radius:8px; padding:12px 14px; font-size:14px; color:#1E293B; min-height:48px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div id="live-speech-text" style="font-style:normal; color:#0369A1; font-weight:600; flex:1 1 280px; line-height:1.4;">
                🎙️ <b>Requesting microphone access...</b> Please click <b>'Allow'</b> in the browser prompt.
            </div>
            <button id="btn-request-mic-action" class="btn-mic-perm-trigger" type="button" style="background:linear-gradient(135deg, #E11D48 0%, #BE123C 100%); color:#FFFFFF; border:none; border-radius:6px; padding:7px 16px; font-weight:700; font-size:12.5px; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 6px rgba(225,29,72,0.25); white-space:nowrap; transition:all 0.15s ease;">
                🎙️ Allow Mic / ಅನುಮತಿ ನೀಡಿ
            </button>
        </div>
    </div>
    """)

    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.6, 1.3, 1.4, 1.2, 1.2], gap="small")
    with b_col1:
        if st.button("✕ Stop / Cancel Listening", key=f"btn_stop_live_mic_{key_suffix}", use_container_width=True):
            st.session_state["mic_active"] = False
            st.rerun()
    with b_col2:
        if st.button("🗣️ \"Library\"", key=f"mic_chip_1_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Take me to Library")
    with b_col3:
        if st.button("🗣️ \"Computer Science\"", key=f"mic_chip_2_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Where is Computer Science Department?")
    with b_col4:
        if st.button("🗣️ \"Next Step\"", key=f"mic_chip_3_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Next")
    with b_col5:
        if st.button("🗣️ \"Repeat\"", key=f"mic_chip_4_{key_suffix}", use_container_width=True):
            handle_voice_query_action("Repeat")

    st.html(f"""
    <script>
    (function() {{
        const SpeechClass = window.SpeechRecognition || window.webkitSpeechRecognition;
        const txtBox = document.getElementById("live-speech-text");
        const permBtn = document.getElementById("btn-request-mic-action");

        function updateStatus(html, color) {{
            if (txtBox) {{
                txtBox.innerHTML = html;
                if (color) txtBox.style.color = color;
            }}
        }}

        // Check Secure Context (HTTPS or localhost)
        const isLocalhost = Boolean(
            location.hostname === 'localhost' ||
            location.hostname === '127.0.0.1' ||
            location.hostname === '[::1]'
        );
        const isSecure = window.isSecureContext || isLocalhost || location.protocol === 'https:';

        if (!isSecure) {{
            updateStatus(
                "⚠️ <b>Insecure Network Connection (" + location.hostname + "):</b><br>" +
                "<span style='font-size:12.5px; font-weight:500; color:#991B1B; line-height:1.45; display:inline-block; margin-top:4px;'>" +
                "Browsers block microphone permissions on network IP addresses over plain HTTP.<br>" +
                "• <b>To test locally:</b> Open <b>http://localhost:8501</b> in Chrome or Edge on this computer.<br>" +
                "• <b>For mobile testing:</b> Deploy the application to Streamlit Cloud (which includes free HTTPS <code>https://...</code>).</span>",
                "#B91C1C"
            );
            if (permBtn) permBtn.style.display = "none";
            return;
        }}

        if (!SpeechClass) {{
            if (txtBox) {{
                txtBox.innerHTML = "⚠️ <b>Microphone recognition is not supported in this browser.</b> Please use Google Chrome, Microsoft Edge, or Safari, or tap the quick buttons above!";
                txtBox.style.color = "#DC2626";
            }}
            if (permBtn) permBtn.style.display = "none";
            return;
        }}

        let recognitionInstance = null;

        function showPermissionDenied() {{
            updateStatus(
                "⚠️ <b>Microphone permission blocked or denied.</b><br>" +
                "<span style='font-size:12.5px; font-weight:500; color:#991B1B; line-height:1.45; display:inline-block; margin-top:4px;'>" +
                "1. Click the lock 🔒 or camera/mic icon next to the URL in your browser address bar.<br>" +
                "2. Change <b>Microphone</b> to <b>'Allow'</b>.<br>" +
                "3. Tap <b>'Retry Microphone'</b> on the right, or use the quick action buttons below.</span>",
                "#B91C1C"
            );
            if (permBtn) {{
                permBtn.style.display = "inline-flex";
                permBtn.innerHTML = "🔄 Retry Microphone";
                permBtn.style.background = "#DC2626";
            }}
        }}

        function startRecognitionEngine() {{
            try {{
                if (recognitionInstance) {{
                    try {{ recognitionInstance.abort(); }} catch(e) {{}}
                }}
                const recognition = new SpeechClass();
                recognitionInstance = recognition;
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = "{lang_code}";

                recognition.onstart = function() {{
                    updateStatus("🔴 <b>Microphone Active & Listening!</b> Speak now into your mic...", "#BE123C");
                    if (permBtn) {{
                        permBtn.style.display = "none";
                    }}
                }};

                recognition.onresult = function(event) {{
                    let interimTranscript = '';
                    let finalTranscript = '';
                    for (let i = event.resultIndex; i < event.results.length; ++i) {{
                        if (event.results[i].isFinal) {{
                            finalTranscript += event.results[i][0].transcript;
                        }} else {{
                            interimTranscript += event.results[i][0].transcript;
                        }}
                    }}
                    const displayed = (finalTranscript || interimTranscript).trim();
                    if (displayed) {{
                        updateStatus("🗣️ <b>Heard:</b> \\"" + displayed + "\\"... Processing...", "#0F172A");
                    }}
                    if (finalTranscript.trim().length > 0) {{
                        setTimeout(function() {{
                            const q = encodeURIComponent(finalTranscript.trim());
                            window.location.search = '?voice_q=' + q;
                        }}, 350);
                    }}
                }};

                recognition.onerror = function(event) {{
                    console.warn("Speech recognition error:", event.error);
                    if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {{
                        showPermissionDenied();
                    }} else if (event.error === 'no-speech') {{
                        updateStatus("⚠️ <b>No speech detected.</b> Tap 'Speak Again' and speak clearly.", "#B91C1C");
                        if (permBtn) {{
                            permBtn.style.display = "inline-flex";
                            permBtn.innerHTML = "🎙️ Speak Again";
                        }}
                    }} else {{
                        updateStatus("⚠️ <b>Mic:</b> " + event.error + ". Tap the quick buttons above or type in the box.", "#B91C1C");
                        if (permBtn) permBtn.style.display = "inline-flex";
                    }}
                }};

                recognition.onend = function() {{
                    // recognition ended
                }};

                recognition.start();
            }} catch(err) {{
                console.error("Failed to start speech recognition:", err);
                updateStatus("⚠️ <b>Microphone start error:</b> " + err.message + ". Tap the quick buttons above!", "#DC2626");
                if (permBtn) permBtn.style.display = "inline-flex";
            }}
        }}

        window.requestMicPermissionDirectly = function() {{
            updateStatus("🎙️ <b>Requesting microphone access...</b> Please click <b>'Allow'</b> in the browser prompt.", "#0369A1");
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{ audio: true }})
                    .then(function(stream) {{
                        stream.getTracks().forEach(function(t) {{ t.stop(); }});
                        updateStatus("✅ <b>Microphone Access Granted!</b> Initializing speech recognition...", "#059669");
                        if (permBtn) permBtn.style.display = "none";
                        startRecognitionEngine();
                    }})
                    .catch(function(err) {{
                        console.warn("getUserMedia permission error:", err);
                        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {{
                            showPermissionDenied();
                        }} else {{
                            startRecognitionEngine();
                        }}
                    }});
            }} else {{
                startRecognitionEngine();
            }}
        }};

        // Bind delegated click listener across document so DOMPurify attribute stripping does not block execution
        document.addEventListener('click', function(e) {{
            let el = e.target;
            while (el && el !== document) {{
                if (el.id === 'btn-request-mic-action' || (el.classList && el.classList.contains('btn-mic-perm-trigger'))) {{
                    e.preventDefault();
                    e.stopPropagation();
                    window.requestMicPermissionDirectly();
                    return;
                }}
                el = el.parentElement;
            }}
        }}, true);

        // Bind directly to element if already present in DOM
        if (permBtn) {{
            permBtn.onclick = function(e) {{
                e.preventDefault();
                window.requestMicPermissionDirectly();
            }};
        }}

        // Prompt microphone permission on banner mount
        window.requestMicPermissionDirectly();
    }})();
    </script>
    """, unsafe_allow_javascript=True)

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
# 7. Main Page Header & Prominent Language Tab Bar
# ----------------------------------------------------
# Determine active language and translations
active_lang = st.session_state["language"]
t = UI_STRINGS.get(active_lang, UI_STRINGS["English"])
floor_labels_localized = dict(FLOOR_OPTIONS_I18N.get(active_lang, FLOOR_OPTIONS_I18N["English"]))

# Full-width prestigious brand banner
render_html(f"""
<div class="brand-banner" style="margin-bottom:12px; padding:18px 24px;">
    <div class="brand-inst">{t['brand_inst']}</div>
    <h1 class="brand-title" style="margin-top:4px; margin-bottom:4px;">{t['brand_title']}</h1>
    <div class="brand-subtitle">{t['brand_subtitle']}</div>
</div>
""")

# Full-width Language Tab Navigation Bar
render_html(f"""
<div class="lang-tab-bar-container">
    <div class="lang-tab-bar-header">
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:18px;">🌐</span>
            <span class="lang-tab-bar-title">Language Selection / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / भाषा चुनें</span>
            <span class="lang-tab-bar-sub">— Switch interface text, directions & voice assistant</span>
        </div>
        <div class="lang-tab-active-badge">Active: {active_lang}</div>
    </div>
</div>
""")

tab_col1, tab_col2, tab_col3 = st.columns(3, gap="small")

with tab_col1:
    is_active_en = (active_lang == "English")
    label_en = "English" + ("  ✓" if is_active_en else "")
    if st.button(
        label_en,
        key="lang_tab_btn_en",
        type="primary" if is_active_en else "secondary",
        use_container_width=True,
        help="Switch interface and voice announcements to English"
    ):
        st.session_state["language"] = "English"
        st.rerun()

with tab_col2:
    is_active_kn = (active_lang == "Kannada")
    label_kn = "ಕನ್ನಡ (Kannada)" + ("  ✓" if is_active_kn else "")
    if st.button(
        label_kn,
        key="lang_tab_btn_kn",
        type="primary" if is_active_kn else "secondary",
        use_container_width=True,
        help="ಇಂಟರ್ಫೇಸ್ ಮತ್ತು ಧ್ವನಿ ಮಾರ್ಗದರ್ಶನವನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಿ"
    ):
        st.session_state["language"] = "Kannada"
        st.rerun()

with tab_col3:
    is_active_hi = (active_lang == "Hindi")
    label_hi = "हिंदी (Hindi)" + ("  ✓" if is_active_hi else "")
    if st.button(
        label_hi,
        key="lang_tab_btn_hi",
        type="primary" if is_active_hi else "secondary",
        use_container_width=True,
        help="इंटरफ़ेस और आवाज़ मार्गदर्शन को हिंदी में बदलें"
    ):
        st.session_state["language"] = "Hindi"
        st.rerun()

# ----------------------------------------------------
# 6b. Sidebar Controls
# ----------------------------------------------------
render_html(f"""
<div style="padding-bottom: 8px; border-bottom: 1.5px solid #CBD5E1; margin-bottom: 12px;">
    <div style="font-size:11px; font-weight:800; color:#0284C7; letter-spacing:0.8px; text-transform:uppercase;">MLACW WAYFINDER</div>
    <div style="font-size:17px; font-weight:800; color:#0F172A;">{t['brand_title']}</div>
</div>
""", sidebar=True)

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

st.sidebar.markdown(f"<div style='font-size:12px; font-weight:700; color:#0F172A; margin-top:14px;'>{t['wheelchair_label']}:</div>", unsafe_allow_html=True)
wc_mode = st.sidebar.checkbox(
    t["wheelchair_label"],
    value=st.session_state["wheelchair_state"],
    help="Exclusively selects ground paths, elevators, and access ramps."
)
if wc_mode != st.session_state["wheelchair_state"]:
    st.session_state["wheelchair_state"] = wc_mode
    st.rerun()

st.sidebar.markdown("""
<div style="font-size:12px; font-weight:800; color:#0F172A; margin-top:16px; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
  <span style="font-size:15px;">🔍</span> Quick Location Search
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
        qr_fl_icon  = {0: "🌿", 1: "🔬", 2: "💻", 3: "🛋️"}.get(qr_floor, "🏢")
        access_badge = '<span style="font-size:10px; font-weight:700; color:#065F46; background:#D1FAE5; border:1px solid #6EE7B7; border-radius:10px; padding:2px 6px;">♿ Accessible</span>' if qr_accessible else '<span style="font-size:10px; font-weight:700; color:#92400E; background:#FEF3C7; border:1px solid #FDE68A; border-radius:10px; padding:2px 6px;">🪜 Stairs</span>'

        st.sidebar.markdown(f"""
<div style="background:linear-gradient(135deg,#EFF6FF,#F0F9FF); border:2px solid #3B82F6; border-radius:14px; padding:14px 15px; margin-top:8px; box-shadow:0 4px 16px rgba(59,130,246,0.12);">
  <div style="font-size:14px; font-weight:800; color:#1E3A5F; margin-bottom:2px;">📍 {matched}</div>
  {f'<div style="font-size:10.5px; color:#64748B; margin-bottom:5px;">{qr_kn} • {qr_hi}</div>' if qr_kn or qr_hi else ''}
  <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px;">
    <span style="font-size:10px; font-weight:700; color:#1D4ED8; background:#DBEAFE; border-radius:10px; padding:2px 7px;">{qr_fl_icon} {qr_fl_label}</span>
    <span style="font-size:10px; font-weight:700; color:#4338CA; background:#EEF2FF; border-radius:10px; padding:2px 7px;">📂 {qr_cat}</span>
    <span style="font-size:10px; font-weight:600; color:#334155; background:#F1F5F9; border-radius:10px; padding:2px 7px;">🏢 {qr_block}</span>
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
            st.session_state["target_destination"] = matched
            st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
            st.session_state["current_step_index"] = 0
            st.session_state["completed_steps"] = []
            st.session_state["route_updated_msg"] = f"🎯 Destination set to **{matched}**! Route from **{st.session_state['current_origin']}** → **{matched}**."
            st.rerun()

        if st.sidebar.button(
            f"🚩 Set as Start: {matched[:28]}{'…' if len(matched) > 28 else ''}",
            key="qs_set_start_btn",
            use_container_width=True
        ):
            st.session_state["current_origin"] = matched
            st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
            st.session_state["current_step_index"] = 0
            st.session_state["completed_steps"] = []
            st.session_state["route_updated_msg"] = f"🚩 Start set to **{matched}**!"
            st.rerun()

    else:
        # Fuzzy suggestions — show top partial matches
        all_names = list(graph_engine.locations_dict.keys())
        q_lower = user_query.lower()
        suggestions = [n for n in all_names if q_lower in n.lower()][:5]
        suggestion_html = ""
        if suggestions:
            items = "".join(
                f'<li style="color:#1E3A5F; font-weight:600; font-size:11.5px; margin-bottom:3px;">📍 {s}</li>'
                for s in suggestions
            )
            suggestion_html = f"""
<div style="margin-top:6px; font-size:11px; color:#64748B; font-weight:600;">Did you mean:</div>
<ul style="margin:4px 0 0 0; padding-left:14px;">{items}</ul>
"""
        st.sidebar.markdown(f"""
<div style="background:#FFF7ED; border:1.5px solid #FB923C; border-radius:12px; padding:12px 14px; margin-top:8px;">
  <div style="font-size:12px; font-weight:800; color:#9A3412; margin-bottom:4px;">❓ No exact match for "{user_query}"</div>
  <div style="font-size:11px; color:#78350F;">Try: "Library", "G11", "Botany", "Computer Science", "Principal"</div>
  {suggestion_html}
</div>
""", unsafe_allow_html=True)


render_html(f"""
<div style="margin-top:20px; padding:14px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:12px; font-size:11.5px; color:#475569; box-shadow:0 1px 3px rgba(15,23,42,0.05);">
  <div style="font-weight:800; color:#0F172A; margin-bottom:8px; font-size:12.5px; letter-spacing:0.3px;">🏛️ MLACW Campus Stats</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="font-size:18px; font-weight:800; color:#0284C7;">4</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Floors</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="font-size:18px; font-weight:800; color:#059669;">{len(graph_engine.locations_dict)}</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Locations</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="font-size:18px; font-weight:800; color:#D97706;">3</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Languages</div>
    </div>
    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:8px 6px; text-align:center;">
      <div style="font-size:18px; font-weight:800; color:#7C3AED;">♿</div>
      <div style="font-size:9.5px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Accessible</div>
    </div>
  </div>
</div>
""", sidebar=True)

# ----------------------------------------------------
# 7a. Multilingual Conversational Voice Assistant Hub
# ----------------------------------------------------
render_html(f"""
<div style="background:#FFFFFF; border:1.8px solid #0284C7; border-radius:12px; padding:16px 20px; margin-top:14px; margin-bottom:16px; box-shadow:0 3px 12px rgba(2,132,199,0.08);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:10px; border-bottom:1px solid #E2E8F0; padding-bottom:10px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:26px;">🎙️</span>
            <div>
                <div style="font-size:15px; font-weight:800; color:#0369A1; text-transform:uppercase; letter-spacing:0.5px;">
                    Multilingual Conversational Voice Assistant
                </div>
                <div style="font-size:12px; color:#475569; font-weight:600;">
                    ಬಹುಭಾಷಾ ಧ್ವನಿ ಸಹಾಯಕ • बहुभाषी वॉइस असिस्टेंट
                </div>
            </div>
        </div>
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:20px; padding:4px 12px; font-size:11.5px; font-weight:700; color:#1D4ED8;">
            🌐 Speaks English, ಕನ್ನಡ & हिंदी
        </div>
    </div>
    <div style="font-size:12.5px; color:#334155; line-height:1.5;">
        Speak or ask for directions in <b>whichever language you prefer (English, ಕನ್ನಡ, or हिंदी)</b>. The system automatically detects your language, sets your destination, and <b>vocally answers in your spoken language!</b>
    </div>
</div>
""")

# Voice Assistant Vocal Response Card (if an answer was spoken)
if st.session_state.get("voice_assistant_response"):
    v_ans_text, v_ans_lang, v_ans_audio = st.session_state["voice_assistant_response"]
    render_html(f"""
    <div style="background:linear-gradient(135deg, #F0F9FF, #E0F2FE); border:2px solid #0284C7; border-radius:12px; padding:14px 18px; margin-bottom:16px; box-shadow:0 3px 10px rgba(2,132,199,0.12);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:20px;">🗣️</span>
                <span style="font-size:13px; font-weight:800; color:#0369A1; text-transform:uppercase;">
                    Spoken Response ({v_ans_lang})
                </span>
            </div>
            <span style="font-size:11px; font-weight:700; color:#0284C7; background:#FFFFFF; border:1px solid #BAE6FD; padding:3px 8px; border-radius:6px;">
                🔊 Vocal Answer Active
            </span>
        </div>
        <div style="font-size:15px; font-weight:700; color:#0F172A; line-height:1.5; margin-bottom:8px;">
            "{v_ans_text}"
        </div>
    </div>
    """)
    if v_ans_audio:
        st.audio(v_ans_audio, format="audio/mp3", autoplay=True)

# Voice input row: Text input + Mic/Ask button
v_in_col1, v_in_col2 = st.columns([4, 1.2], gap="small")
with v_in_col1:
    v_user_query = st.text_input(
        "Ask Voice Assistant in any language:",
        placeholder="🎙️ Speak or type: 'Where is Library?', 'ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?', 'पुस्तकालय कहाँ है?'...",
        key="multilingual_voice_input",
        label_visibility="collapsed"
    )
with v_in_col2:
    v_ask_triggered = st.button("🎙️ Ask / ಕೇಳಿ", key="voice_submit_btn", type="primary", use_container_width=True)

mic_permission_tips = {
    "English": "🎙️ **Microphone Voice Search:** Tap **'🎙️ Ask / ಕೇಳಿ'** to speak. When your browser requests permission, click **'Allow'** to let the assistant listen.",
    "Kannada": "🎙️ **ಧ್ವನಿ ಹುಡುಕಾಟ:** ಮಾತನಾಡಲು **'🎙️ Ask / ಕೇಳಿ'** ಕ್ಲಿಕ್ ಮಾಡಿ. ಬ್ರೌಸರ್ ಅನುಮತಿ ಕೇಳಿದಾಗ ಮೈಕ್ರೊಫೋನ್‌ಗಾಗಿ **'Allow'** ಆಯ್ಕೆಮಾಡಿ.",
    "Hindi": "🎙️ **वॉयस सर्च:** बोलने के लिए **'🎙️ Ask / ಕೇಳಿ'** पर क्लिक करें। ब्राउज़र पूछे जाने पर माइक्रोफ़ोन के लिए **'Allow'** चुनें।"
}
st.caption(mic_permission_tips.get(active_lang, mic_permission_tips["English"]))

if v_ask_triggered:
    if v_user_query and v_user_query.strip():
        handle_voice_query_action(v_user_query.strip())
    else:
        st.session_state["mic_active"] = True
        st.rerun()

# High-Visibility Live Listening Banner
if st.session_state.get("mic_active"):
    render_live_mic_banner(active_lang, key_suffix="assistant")

# Quick Multilingual Spoken Prompts Pills (One-Click Spoken Interaction)
st.markdown("<div style='font-size:12px; font-weight:700; color:#475569; margin-top:8px; margin-bottom:6px;'>⚡ Quick Spoken Queries — Tap any question to test multilingual voice:</div>", unsafe_allow_html=True)
vp_c1, vp_c2, vp_c3 = st.columns(3, gap="small")

with vp_c1:
    st.markdown("<div style='font-size:11px; font-weight:800; color:#0369A1; text-transform:uppercase; margin-bottom:4px;'>🇬🇧 English Voice Prompts</div>", unsafe_allow_html=True)
    if st.button("🗣️ \"Take me to Library\"", key="vp_en_1", use_container_width=True):
        handle_voice_query_action("Take me to Library")
    if st.button("🗣️ \"Where is Classroom G11?\"", key="vp_en_2", use_container_width=True):
        handle_voice_query_action("Where is Classroom G11?")
    if st.button("🗣️ \"Gents Washroom\"", key="vp_en_3", use_container_width=True):
        handle_voice_query_action("Where is Gents Washroom?")
    if st.button("🗣️ \"Computer Science Dept\"", key="vp_en_4", use_container_width=True):
        handle_voice_query_action("Computer Science Department")

with vp_c2:
    st.markdown("<div style='font-size:11px; font-weight:800; color:#059669; text-transform:uppercase; margin-bottom:4px;'>🇮🇳 ಕನ್ನಡ ಧ್ವನಿ ಪ್ರಶ್ನೆಗಳು</div>", unsafe_allow_html=True)
    if st.button("🗣️ \"ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?\"", key="vp_kn_1", use_container_width=True):
        handle_voice_query_action("ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ?")
    if st.button("🗣️ \"ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ\"", key="vp_kn_2", use_container_width=True):
        handle_voice_query_action("ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಎಲ್ಲಿದೆ?")
    if st.button("🗣️ \"ಪುರುಷರ ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?\"", key="vp_kn_3", use_container_width=True):
        handle_voice_query_action("ಪುರುಷರ ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?")
    if st.button("🗣️ \"ಪ್ರಿನ್ಸಿಪಾಲ್ ಆಫೀಸ್\"", key="vp_kn_4", use_container_width=True):
        handle_voice_query_action("ಪ್ರಿನ್ಸಿಪಾಲ್ ಆಫೀಸ್")

with vp_c3:
    st.markdown("<div style='font-size:11px; font-weight:800; color:#D97706; text-transform:uppercase; margin-bottom:4px;'>🇮🇳 हिंदी आवाज प्रश्न</div>", unsafe_allow_html=True)
    if st.button("🗣️ \"पुस्तकालय कहाँ है?\"", key="vp_hi_1", use_container_width=True):
        handle_voice_query_action("पुस्तकालय कहाँ है?")
    if st.button("🗣️ \"कंप्यूटर लैब 1 कहाँ है?\"", key="vp_hi_2", use_container_width=True):
        handle_voice_query_action("कंप्यूटर लैब 1 कहाँ है?")
    if st.button("🗣️ \"शौचालय कहाँ है?\"", key="vp_hi_3", use_container_width=True):
        handle_voice_query_action("शौचालय कहाँ है?")
    if st.button("🗣️ \"प्रिंसिपल ऑफिस\"", key="vp_hi_4", use_container_width=True):
        handle_voice_query_action("प्रिंसिपल ऑफिस")

# ----------------------------------------------------
# 7b. Floor Directory Summary Card (Above Route Selection)
# ----------------------------------------------------
render_html(f"""
<div class="floor-guide-card">
    <div class="floor-guide-header">
        <span style="font-size:22px;">🏢</span>
        <div>
            <div class="floor-guide-title">{t['floor_guide_title']}</div>
            <div class="floor-guide-sub">{t['floor_guide_sub']}</div>
        </div>
    </div>
    <div class="floor-guide-grid">
        <div class="floor-guide-row">
            <span class="floor-tag-pill floor-0-badge">🌿 {t['floor_0_label']}</span>
            <span class="floor-tag-desc">{t['floor_0_rooms']}</span>
        </div>
        <div class="floor-guide-row">
            <span class="floor-tag-pill floor-1-badge">🔬 {t['floor_1_label']}</span>
            <span class="floor-tag-desc">{t['floor_1_rooms']}</span>
        </div>
        <div class="floor-guide-row">
            <span class="floor-tag-pill floor-2-badge">💻 {t['floor_2_label']}</span>
            <span class="floor-tag-desc">{t['floor_2_rooms']}</span>
        </div>
        <div class="floor-guide-row">
            <span class="floor-tag-pill floor-3-badge">🛋️ {t['floor_3_label']}</span>
            <span class="floor-tag-desc">{t['floor_3_rooms']}</span>
        </div>
    </div>
</div>
""")

# ----------------------------------------------------
# 8. Main Page Route Planner (Select Floor -> Select Room)
# ----------------------------------------------------
render_html(f"""
<div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px 18px; margin-bottom:12px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
    <div style="font-size:16px; font-weight:800; color:#0F172A;">🧭 {t['route_planner_title']}</div>
    <div style="font-size:12.5px; color:#475569; margin-top:2px;">
        {t['route_planner_sub']}
    </div>
</div>
""")

def handle_swap_locations():
    """Swaps origin and destination, increments planner version to reset selectboxes cleanly."""
    old_orig = st.session_state["current_origin"]
    old_dest = st.session_state["target_destination"]
    st.session_state["current_origin"] = old_dest
    st.session_state["target_destination"] = old_orig
    st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
    st.session_state["current_step_index"] = 0
    st.session_state["completed_steps"] = []
    st.session_state["recovery_mode"] = False
    st.session_state["route_updated_msg"] = f"⇄ Swapped! Active route: **{old_dest}** → **{old_orig}**."

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

col_btn_swap, col_btn_wc, _ = st.columns([1.6, 1.8, 1.2], gap="small")
col_btn_swap.button(
    t["swap_btn"],
    key="btn_swap_main_box",
    on_click=handle_swap_locations,
    use_container_width=True,
    help="Swap starting point and destination to reverse your walking journey"
)

wc_active = col_btn_wc.checkbox(t["wheelchair_label"], value=st.session_state["wheelchair_state"], key="wc_main_planner")
if wc_active != st.session_state["wheelchair_state"]:
    st.session_state["wheelchair_state"] = wc_active
    st.rerun()

# ----------------------------------------------------
# 9. Progressive Step-by-Step Navigation & Guidance
# ----------------------------------------------------
render_html('<div id="active-route-top"></div>')
start_node = st.session_state["current_origin"]
dest_node = st.session_state["target_destination"]

# Task 1: Same-Origin and Same-Destination Edge-Case Guard
if start_node == dest_node:
    same_dest_msgs = {
        "English": "You are already at your destination!",
        "Kannada": "ನೀವು ಈಗಾಗಲೇ ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನದಲ್ಲಿದ್ದೀರಿ!",
        "Hindi": "आप पहले से ही अपने गंतव्य पर मौजूद हैं!"
    }
    same_msg = same_dest_msgs.get(active_lang, t.get("same_destination_msg", "You are already at your destination!"))
    st.info(same_msg)
    st.stop()

# Task 2: Session State Route Change Synchronization
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

    # Progress State Tracking with Strict Boundary Protection
    total_steps = len(steps)
    if total_steps == 0:
        st.warning("No guidance steps available for this route.")
        st.stop()

    current_idx = max(0, min(st.session_state.get("current_step_index", 0), total_steps - 1))
    st.session_state["current_step_index"] = current_idx
    active_step = steps[current_idx]
    is_last_step = (current_idx == total_steps - 1)
    progress_pct = int(((current_idx + 1) / total_steps) * 100)

    start_display = format_room_label(start_node, active_lang)
    dest_display = format_room_label(dest_node, active_lang)
    start_fl_label = floor_labels_localized.get(start_floor, f"Floor {start_floor}")
    dest_fl_label = floor_labels_localized.get(dest_floor, f"Floor {dest_floor}")

    wc_tag = f"<span class='floor-pill-tag' style='background:#ECFDF5; color:#065F46; font-weight:700;'>{t['wheelchair_label']}</span>" if st.session_state['wheelchair_state'] else ""

    render_html(f"""
    <div class="journey-summary-box" style="margin-top:16px;">
        <div class="journey-header">
            <div>
                <span class="journey-title">{t['journey_title']}</span>
                <div class="journey-route-tag">
                    🚩 {start_display} <span style="color:#64748B; font-weight:400;">→</span> 🎯 {dest_display}
                </div>
            </div>
            <div>
                <span class="floor-pill-tag" style="background:#EFF6FF; color:#1D4ED8; font-weight:700;">
                    {start_fl_label} → {dest_fl_label}
                </span>
                {wc_tag}
            </div>
        </div>
        <div class="journey-metrics">
            <div class="metric-pill">
                <div class="metric-pill-label">{t['total_dist']}</div>
                <div class="metric-pill-value">{int(total_distance)} m</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">{t['est_time']}</div>
                <div class="metric-pill-value">~{eta} min</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">{t['floor_changes']}</div>
                <div class="metric-pill-value">{floor_changes} {'(Stairs/Elevator)' if floor_changes > 0 else '(Level)'}</div>
            </div>
            <div class="metric-pill">
                <div class="metric-pill-label">{t['checkpoint_prog']}</div>
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
            stepper_html += f'<span class="stepper-pill completed">✓ {t["step_x_of_y"].format(current=s_step_num, total=total_steps)}: {s_title}</span>'
        elif i == current_idx:
            stepper_html += f'<span class="stepper-pill active">🎯 {t["checkpoint_active"]}: {s_step_num}</span>'
        else:
            stepper_html += f'<span class="stepper-pill pending">⭕ {s_step_num}: {s_title}</span>'
    stepper_html += '</div>'
    render_html(stepper_html)

    # Synchronized Progress Bar
    st.progress(progress_pct / 100.0)

    # Audio Voice Assistant Bar (Reads ONLY the active checkpoint instruction)
    active_speech_text = active_step.get("audio_text", active_step.get("instruction", ""))
    should_play_speech = st.session_state.get("auto_speech", False)

    # -----------------------------------------------------------------
    # Unified Native Voice Guidance & Step Navigation Control Panel
    # (100% native Streamlit controls with zero iframe barriers)
    # -----------------------------------------------------------------
    panel_i18n = {
        "English": {
            "badge": f"Step {current_idx + 1}/{total_steps}",
            "mic": "🎙️ Voice Command",
            "play": "▶ Speak Step",
            "btn_next": "Next ➔",
            "btn_repeat": "Repeat 🔄",
            "btn_back": "⏮ Back",
            "btn_lost": "🆘 Lost",
            "btn_arrived": "🏁 Arrived!",
            "status": f"🔊 Spoken audio ready in <b>{active_lang}</b> • Tap <b>\"Speak Step\"</b> or <b>\"🎙️ Voice Command\"</b> to talk."
        },
        "Kannada": {
            "badge": f"ಹಂತ {current_idx + 1}/{total_steps}",
            "mic": "🎙️ ಧ್ವನಿ ಆದೇಶ",
            "play": "▶ ಹಂತ ಕೇಳಿ",
            "btn_next": "ಮುಂದೆ ➔",
            "btn_repeat": "ಮತ್ತೊಮ್ಮೆ 🔄",
            "btn_back": "⏮ ಹಿಂದೆ",
            "btn_lost": "🆘 ದಾರಿ ತಪ್ಪಿದೆ",
            "btn_arrived": "🏁 ತಲುಪಿದೆ!",
            "status": f"🔊 <b>{active_lang}</b> ಧ್ವನಿ ಮಾರ್ಗದರ್ಶನ ಸಿದ್ಧವಾಗಿದೆ • <b>\"ಹಂತ ಕೇಳಿ\"</b> ಅಥವಾ <b>\"ಧ್ವನಿ ಆದೇಶ\"</b> ಕ್ಲಿಕ್ ಮಾಡಿ."
        },
        "Hindi": {
            "badge": f"कदम {current_idx + 1}/{total_steps}",
            "mic": "🎙️ वॉइस कमांड",
            "play": "▶ निर्देश सुनें",
            "btn_next": "आगे ➔",
            "btn_repeat": "दोहराएं 🔄",
            "btn_back": "⏮ पीछे",
            "btn_lost": "🆘 भटक गया",
            "btn_arrived": "🏁 पहुँच गए!",
            "status": f"🔊 <b>{active_lang}</b> आवाज सक्रिय है • <b>\"निर्देश सुनें\"</b> या <b>\"वॉइस कमांड\"</b> पर टैप करें।"
        }
    }
    p_texts = panel_i18n.get(active_lang, panel_i18n["English"])

    # High-Visibility Live Listening Banner if mic is active
    if st.session_state.get("mic_active"):
        render_live_mic_banner(active_lang, key_suffix="navigation")

    # Native Voice & Language Control Container Header
    render_html(f"""
    <div style="background:#FFFFFF; border:1.8px solid #0284C7; border-radius:12px; padding:12px 14px 4px 14px; margin-top:12px; margin-bottom:8px; box-shadow:0 2px 10px rgba(2,132,199,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:17px;">🌐</span>
                <span style="font-size:12px; font-weight:800; color:#0369A1; text-transform:uppercase; letter-spacing:0.5px;">
                    VOICE LANGUAGE:
                </span>
            </div>
            <div style="background:#EFF6FF; color:#1D4ED8; font-weight:800; font-size:11.5px; padding:3px 10px; border-radius:12px; border:1px solid #BFDBFE;">
                {p_texts['badge']}
            </div>
        </div>
    </div>
    """)

    # Language Switcher Buttons (100% Native)
    vl_c1, vl_c2, vl_c3 = st.columns(3, gap="small")
    with vl_c1:
        if st.button("English", key="ctrl_lang_en", type="primary" if active_lang == "English" else "secondary", use_container_width=True):
            st.session_state["language"] = "English"
            st.session_state["auto_speech"] = True
            st.rerun()
    with vl_c2:
        if st.button("ಕನ್ನಡ (Kannada)", key="ctrl_lang_kn", type="primary" if active_lang == "Kannada" else "secondary", use_container_width=True):
            st.session_state["language"] = "Kannada"
            st.session_state["auto_speech"] = True
            st.rerun()
    with vl_c3:
        if st.button("हिंदी (Hindi)", key="ctrl_lang_hi", type="primary" if active_lang == "Hindi" else "secondary", use_container_width=True):
            st.session_state["language"] = "Hindi"
            st.session_state["auto_speech"] = True
            st.rerun()

    # Action Controls & Quick Navigation (100% Native Streamlit Buttons)
    c_col1, c_col2, c_col3, c_col4, c_col5, c_col6 = st.columns([1.5, 1.4, 1.4, 1.2, 1.1, 1.1], gap="small")
    with c_col1:
        if st.button(p_texts["mic"], key="ctrl_btn_mic", use_container_width=True):
            st.session_state["mic_active"] = True
            st.rerun()
    with c_col2:
        if st.button(p_texts["play"], key="ctrl_btn_speak", type="primary", use_container_width=True):
            st.session_state["auto_speech"] = True
            st.rerun()
    with c_col3:
        if is_last_step:
            if st.button(p_texts["btn_arrived"], key="ctrl_btn_arrived", type="primary", use_container_width=True):
                if current_idx not in st.session_state["completed_steps"]:
                    st.session_state["completed_steps"].append(current_idx)
                st.session_state["auto_speech"] = False
                st.balloons()
                st.success(f"🎉 {dest_display}!")
                st.rerun()
        else:
            if st.button(p_texts["btn_next"], key="ctrl_btn_next", type="primary", use_container_width=True):
                if current_idx not in st.session_state["completed_steps"]:
                    st.session_state["completed_steps"].append(current_idx)
                st.session_state["current_step_index"] = min(total_steps - 1, current_idx + 1)
                st.session_state["auto_speech"] = True
                st.rerun()
    with c_col4:
        if st.button(p_texts["btn_repeat"], key="ctrl_btn_repeat", use_container_width=True):
            st.session_state["auto_speech"] = True
            st.rerun()
    with c_col5:
        prev_disabled = (current_idx == 0)
        if st.button(p_texts["btn_back"], key="ctrl_btn_prev", disabled=prev_disabled, use_container_width=True):
            st.session_state["current_step_index"] = max(0, current_idx - 1)
            st.session_state["auto_speech"] = True
            st.rerun()
    with c_col6:
        lost_label = t["btn_close_help"] if st.session_state["recovery_mode"] else p_texts["btn_lost"]
        if st.button(lost_label, key="ctrl_btn_lost", use_container_width=True):
            st.session_state["recovery_mode"] = not st.session_state["recovery_mode"]
            st.rerun()

    # Native HTML5 High-Definition Audio Player
    step_audio_bytes = generate_step_audio(active_speech_text, active_lang)
    if step_audio_bytes:
        st.audio(step_audio_bytes, format="audio/mp3", autoplay=should_play_speech)

    # Dynamic status bar
    render_html(f"""
    <div style="background:#F1F5F9; border:1px solid #E2E8F0; border-radius:6px; padding:6px 12px; font-size:12px; color:#334155; margin-top:4px; margin-bottom:12px;">
        {p_texts['status']}
    </div>
    """)
    if should_play_speech:
        st.session_state["auto_speech"] = False

    # Active Checkpoint Hero Card ("Checkpoint / Game" Mode)
    clean_instruction = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(active_step.get('instruction', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
    clean_verification = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(active_step.get('verification', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
    step_icon = active_step.get('icon', '🚶')
    step_floor = active_step.get('floor', dest_floor)
    step_dist = active_step.get('distance', 0)
    step_fl_label = floor_labels_localized.get(step_floor, f"Floor {step_floor}")

    render_html(f"""
    <div class="checkpoint-hero-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:24px;">{step_icon}</span>
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
                <span class="floor-pill-tag" style="background:#EFF6FF; color:#1D4ED8; font-weight:700;">
                    {step_fl_label}
                </span>
                <span class="floor-pill-tag" style="background:#F0FDF4; color:#065F46; font-weight:700; border-color:#BBF7D0;">
                    🚶 {step_dist}m
                </span>
            </div>
        </div>

        <div style="font-size:16px; line-height:1.6; color:#0F172A; font-weight:600; padding:12px 14px; background:#F8FAFC; border-radius:8px; border:1px solid #E2E8F0;">
            {clean_instruction}
        </div>

        <div class="landmark-box">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="font-size:18px;">🧭</span>
                <span style="font-size:12.5px; font-weight:800; color:#92400E; letter-spacing:0.5px; text-transform:uppercase;">
                    {t['landmark_box_title']}
                </span>
            </div>
            <div style="font-size:13.5px; color:#78350F; line-height:1.55; font-weight:500;">
                {clean_verification}
            </div>
            <div style="font-size:12px; color:#B45309; font-weight:700; margin-top:8px; display:flex; align-items:center; gap:6px;">
                <span>{t['orientation_rule']}</span>
            </div>
        </div>
    </div>
    """)

    # Interactive Step-by-Step Control Action Bar
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.1, 1.2, 1.8, 1.3])

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

    # Lost User Fallback & Orientation Recovery Panel
    if st.session_state["recovery_mode"]:
        render_html(f"""
        <div class="recovery-card">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span style="font-size:22px;">🆘</span>
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

    # Collapsible Journey Overview (All Checkpoints)
    with st.expander(t["view_all_expander"].format(total=total_steps), expanded=False):
        for idx, step in enumerate(steps, 1):
            clean_step_inst = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(step.get('instruction', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
            clean_step_verif = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(step.get('verification', ''))).replace('\n\n', '<br><br>').replace('\n', '<br>')
            is_step_active = (idx - 1 == current_idx)
            is_step_done = (idx - 1 in st.session_state.get("completed_steps", []))

            border_color = "#0284C7" if is_step_active else ("#10B981" if is_step_done else "#CBD5E1")
            bg_color = "#F0F9FF" if is_step_active else ("#F0FDF4" if is_step_done else "#FFFFFF")
            status_tag = f"🎯 {t['checkpoint_active']}" if is_step_active else ("✓ COMPLETED" if is_step_done else t['step_x_of_y'].format(current=idx, total=total_steps))
            st_fl_label = floor_labels_localized.get(step.get('floor', 0), f"Floor {step.get('floor', 0)}")

            render_html(f"""
            <div style="border:1.5px solid {border_color}; background:{bg_color}; border-radius:8px; padding:12px 16px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:12px; font-weight:800; color:{border_color};">{step.get('icon', '🚶')} {status_tag}</span>
                    <span class="floor-pill-tag">{step.get('distance', 0)}m &bull; {st_fl_label}</span>
                </div>
                <div style="font-size:13.5px; color:#0F172A; font-weight:600;">
                    {clean_step_inst}
                </div>
                <div style="font-size:12px; color:#78350F; margin-top:4px;">
                    🧭 {clean_step_verif}
                </div>
            </div>
            """)

except nx.NetworkXNoPath:
    st.error(
        f"No accessible route found between **{start_node}** and **{dest_node}**. "
        "Try turning off wheelchair-only mode if this wing only has stairs."
    )


st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 10. Dedicated Floor Directory & Room Finder (Dropdown for Each Floor)
# ----------------------------------------------------
render_html(f"""
<div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:16px 20px; margin-bottom:14px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
    <div style="font-size:18px; font-weight:800; color:#0F172A;">{t['floor_dir_title']}</div>
    <div style="font-size:13px; color:#475569; margin-top:2px;">
        {t['floor_dir_sub']}
    </div>
</div>
""")

col_f_select, col_r_select = st.columns([1.2, 1.8], gap="medium")

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
        index=st.session_state["dir_floor"],
        key="dir_floor_select_key"
    )
    st.session_state["dir_floor"] = dir_floor

floor_all_rooms = get_floor_nodes(dir_floor)

with col_r_select:
    featured_room = st.selectbox(
        f"🏫 {floor_labels_localized[dir_floor]}:",
        options=floor_all_rooms,
        format_func=lambda rm: format_room_label(rm, active_lang),
        index=0,
        key="dir_room_select_key"
    )

# Selected Room Showcase Card
r_info = graph_engine.locations_dict.get(featured_room, {})
r_kn = r_info.get("kannada_name", "")
r_hi = r_info.get("hindi_name", "")
r_cat = r_info.get("category", "")
r_block = r_info.get("block", "")
r_acc = r_info.get("is_accessible", True)
r_desc = r_info.get("description", "")

render_html(f"""
<div style="background:#F8FAFC; border:1.5px solid #0284C7; border-radius:10px; padding:14px 18px; margin-bottom:12px;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
        <div>
            <div style="font-size:18px; font-weight:800; color:#0F172A;">{featured_room}</div>
            <div style="font-size:12.5px; color:#475569; margin-top:2px;">{r_kn} • {r_hi}</div>
            <div style="font-size:12.5px; color:#334155; margin-top:4px;">{r_desc}</div>
        </div>
        <div>
            <span class="cat-tag" style="background:#E0F2FE; color:#0369A1; font-weight:700;">{r_cat}</span>
            <span class="cat-tag" style="background:#F1F5F9; color:#334155; font-weight:600;">{r_block}</span>
            {'<span class="cat-tag" style="background:#ECFDF5; color:#065F46; font-weight:700;">♿ Wheelchair Accessible</span>' if r_acc else ''}
        </div>
    </div>
</div>
""")

col_act_a, col_act_b, _ = st.columns([1.4, 1.4, 1.8])
if col_act_a.button(f"{t['btn_set_dest']}: {format_room_label(featured_room, active_lang)}", key="btn_showcase_dest", use_container_width=True):
    st.session_state["target_destination"] = featured_room
    st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
    st.session_state["current_step_index"] = 0
    st.session_state["completed_steps"] = []
    st.session_state["route_updated_msg"] = f"🎯 Destination updated to **{featured_room}**! Active route: **{st.session_state['current_origin']}** → **{featured_room}**."
    st.rerun()
if col_act_b.button(f"{t['btn_set_orig']}: {format_room_label(featured_room, active_lang)}", key="btn_showcase_orig", use_container_width=True):
    st.session_state["current_origin"] = featured_room
    st.session_state["planner_version"] = st.session_state.get("planner_version", 0) + 1
    st.session_state["current_step_index"] = 0
    st.session_state["completed_steps"] = []
    st.session_state["route_updated_msg"] = f"🚩 Starting point updated to **{featured_room}**! Active route: **{featured_room}** → **{st.session_state['target_destination']}**."
    st.rerun()

if st.session_state.get("route_updated_msg"):
    st.success(st.session_state["route_updated_msg"])
    render_html("""
    <div style="margin-top:6px; margin-bottom:12px;">
        <a href="#active-route-top" style="display:inline-flex; align-items:center; gap:6px; padding:7px 14px; background:#0284C7; color:#FFFFFF; text-decoration:none; border-radius:6px; font-weight:700; font-size:12.5px; box-shadow:0 2px 4px rgba(2,132,199,0.2);">
            ⬆️ Click to View Active Walking Checkpoints & Voice Guidance
        </a>
    </div>
    """)

# ----------------------------------------------------
# 11. Dropdown for EACH Floor (Floor Room Rosters)
# ----------------------------------------------------
st.markdown(f"<div style='font-size:15px; font-weight:700; color:#0F172A; margin-top:18px; margin-bottom:8px;'>{t['explore_floors_title']}</div>", unsafe_allow_html=True)

floor_descriptions = {
    0: (f"🌿 {t['floor_0_label']}", t['floor_0_rooms']),
    1: (f"🔬 {t['floor_1_label']}", t['floor_1_rooms']),
    2: (f"💻 {t['floor_2_label']}", t['floor_2_rooms']),
    3: (f"🛋️ {t['floor_3_label']}", t['floor_3_rooms'])
}

for fl_idx in [0, 1, 2, 3]:
    fl_title, fl_sub = floor_descriptions[fl_idx]
    fl_rooms = get_floor_nodes(fl_idx)
    with st.expander(f"{fl_title} — ({len(fl_rooms)} Rooms & Locations)", expanded=(fl_idx == dir_floor)):
        st.markdown(f"<div style='font-size:12px; color:#475569; margin-bottom:10px;'>{fl_sub}</div>", unsafe_allow_html=True)

        fl_df = graph_engine.locations_df[graph_engine.locations_df["floor"] == fl_idx][["location_name", "category", "block", "is_accessible"]].copy()
        fl_df.columns = ["Location Name", "Category", "Wing / Block", "Wheelchair Accessible"]
        fl_df["Wheelchair Accessible"] = fl_df["Wheelchair Accessible"].apply(lambda a: "♿ Accessible" if a else "Stairs Only")
        st.markdown(fl_df.to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

# ----------------------------------------------------
# 12. Reference Tables Expander
# ----------------------------------------------------
with st.expander("📋 Institutional Reference Tables (Departments & Classrooms)", expanded=False):
    t_col1, t_col2 = st.columns(2, gap="medium")
    with t_col1:
        st.markdown("<div style='font-size:14px; font-weight:700; color:#0F172A; margin-bottom:6px;'>Academic Departments</div>", unsafe_allow_html=True)
        dept_csv = os.path.join(DATA_DIR, "departments.csv")
        dept_df = pd.read_csv(dept_csv)
        st.markdown(dept_df[["department_name", "block", "floor", "hod_name", "contact_email"]].to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

    with t_col2:
        st.markdown("<div style='font-size:14px; font-weight:700; color:#0F172A; margin-bottom:6px;'>Classrooms & Lecture Halls (G1-G11, F1-F5, S1-S12, LH3)</div>", unsafe_allow_html=True)
        cr_csv = os.path.join(DATA_DIR, "classrooms.csv")
        cr_df = pd.read_csv(cr_csv)
        st.markdown(cr_df[["room_number", "room_name", "block", "floor", "capacity", "facilities"]].to_html(index=False, classes="campus-table"), unsafe_allow_html=True)

