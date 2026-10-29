"""
HTML5 Web Speech API Component with Voice Assistant & Progressive State Synchronization
Features:
1. Speech-to-Text (webkitSpeechRecognition) supporting Voice Commands:
   - "Next" / "Done" / "Next step" -> Advances to next checkpoint
   - "Previous" / "Back" -> Returns to previous step
   - "Repeat" / "Again" -> Re-reads current checkpoint instruction
   - "Lost" / "Where am I" -> Triggers lost user recovery
2. Text-to-Speech (window.speechSynthesis) for Active Checkpoint with Parent Window Execution
3. Multi-language support: English (en-IN), Kannada (kn-IN), Hindi (hi-IN)
4. Chrome bug workaround: Unfreezing synthesizer queue via .cancel() + .resume()
5. Multi-tier voice selection with automatic fallback to avoid language-unavailable drops
6. Top-level parent DOM script injection to eliminate iframe microphone policy blocks
"""

import json
from svg_icons import get_svg_icon

def get_voice_assistant_html(
    language: str = "English",
    audio_script: str = "",
    audio_b64: str = "",
    checkpoint_num: int = 1,
    total_checkpoints: int = 1,
    auto_play: bool = False,
    **kwargs
) -> str:
    total_checkpoints = max(1, int(total_checkpoints or 1))
    checkpoint_num = max(1, min(int(checkpoint_num or 1), total_checkpoints))
    audio_script = str(audio_script or "")
    audio_b64 = str(audio_b64 or "")

    lang_code_map = {
        "English": "en-IN",
        "Kannada": "kn-IN",
        "Hindi": "hi-IN"
    }
    lang_code = lang_code_map.get(language, "en-IN")
    escaped_audio = json.dumps(audio_script)
    auto_play_js = "true" if auto_play else "false"

    # Crisp Vector SVG Icons
    icon_mic = get_svg_icon("mic", size=14, color="currentColor")
    icon_play = get_svg_icon("play", size=13, color="currentColor", filled=True)
    icon_pause = get_svg_icon("pause", size=13, color="currentColor", filled=True)
    icon_stop = get_svg_icon("stop", size=13, color="currentColor", filled=True)
    icon_next = get_svg_icon("arrow_right", size=12, color="currentColor")
    icon_repeat = get_svg_icon("repeat", size=12, color="currentColor")
    icon_back = get_svg_icon("skip_back", size=12, color="currentColor", filled=True)
    icon_lost = get_svg_icon("lifebuoy", size=13, color="#DC2626")
    icon_globe = get_svg_icon("globe", size=13, color="#0369A1")

    panel_i18n = {
        "English": {
            "badge": f"Step {checkpoint_num}/{total_checkpoints}",
            "mic": f"{icon_mic}<span>Voice Command</span>",
            "play": f"{icon_play}<span>Speak Step</span>",
            "pause": f"{icon_pause}<span>Pause</span>",
            "stop": f"{icon_stop}<span>Stop</span>",
            "quick": "Quick:",
            "btn_next": f"<span>Next</span>{icon_next}",
            "btn_repeat": f"{icon_repeat}<span>Repeat</span>",
            "btn_back": f"{icon_back}<span>Back</span>",
            "btn_lost": f"{icon_lost}<span>Lost</span>",
            "status": "Voice assistant active &bull; Tap <b>\"Speak Step\"</b> or say <b>\"Next\"</b>, <b>\"Repeat\"</b>, or <b>\"Lost\"</b>"
        },
        "Kannada": {
            "badge": f"ಹಂತ {checkpoint_num}/{total_checkpoints}",
            "mic": f"{icon_mic}<span>ಧ್ವನಿ ಆದೇಶ</span>",
            "play": f"{icon_play}<span>ಹಂತ ಕೇಳಿ</span>",
            "pause": f"{icon_pause}<span>ವಿರಾಮ</span>",
            "stop": f"{icon_stop}<span>ನಿಲ್ಲಿಸಿ</span>",
            "quick": "ತ್ವರಿತ:",
            "btn_next": f"<span>ಮುಂದೆ</span>{icon_next}",
            "btn_repeat": f"{icon_repeat}<span>ಮತ್ತೊಮ್ಮೆ</span>",
            "btn_back": f"{icon_back}<span>ಹಿಂದೆ</span>",
            "btn_lost": f"{icon_lost}<span>ದಾರಿ ತಪ್ಪಿದೆ</span>",
            "status": "ಧ್ವನಿ ಸಹಾಯಕ ಸಿದ್ಧವಾಗಿದೆ &bull; <b>\"ಹಂತ ಕೇಳಿ\"</b> ಕ್ಲಿಕ್ ಮಾಡಿ ಅಥವಾ <b>\"ಮುಂದೆ\"</b>, <b>\"ಮತ್ತೊಮ್ಮೆ\"</b> ಹೇಳಿ"
        },
        "Hindi": {
            "badge": f"कदम {checkpoint_num}/{total_checkpoints}",
            "mic": f"{icon_mic}<span>वॉइस कमांड</span>",
            "play": f"{icon_play}<span>निर्देश सुनें</span>",
            "pause": f"{icon_pause}<span>विराम</span>",
            "stop": f"{icon_stop}<span>रोकें</span>",
            "quick": "त्वरित:",
            "btn_next": f"<span>आगे</span>{icon_next}",
            "btn_repeat": f"{icon_repeat}<span>दोहराएं</span>",
            "btn_back": f"{icon_back}<span>पीछे</span>",
            "btn_lost": f"{icon_lost}<span>भटक गया</span>",
            "status": "वॉइस असिस्टेंट सक्रिय है &bull; <b>\"निर्देश सुनें\"</b> पर क्लिक करें या <b>\"आगे\"</b>, <b>\"दोहराएं\"</b> बोलें"
        }
    }
    pi18n = panel_i18n.get(language, panel_i18n["English"])

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
                -webkit-tap-highlight-color: transparent;
            }}
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}
            .voice-panel {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                padding: 10px 14px;
                background: #FFFFFF;
                border: 1.5px solid #0284C7;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(2, 132, 199, 0.08);
            }}
            .lang-strip {{
                display: flex;
                align-items: center;
                gap: 6px;
                padding-bottom: 6px;
                border-bottom: 1px solid #E2E8F0;
                flex-wrap: wrap;
            }}
            .lang-strip-label {{
                font-size: 11px;
                font-weight: 800;
                color: #0369A1;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-right: 4px;
            }}
            .btn-lang {{
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                cursor: pointer;
                background: #F8FAFC;
                color: #334155;
                border: 1px solid #CBD5E1;
                transition: all 0.15s ease;
                min-height: 28px;
                touch-action: manipulation;
            }}
            .btn-lang:hover {{
                background: #E2E8F0;
                color: #0F172A;
            }}
            .btn-lang.active {{
                background: #0284C7;
                color: #FFFFFF;
                border-color: #0284C7;
                box-shadow: 0 1px 4px rgba(2, 132, 199, 0.3);
            }}
            .controls-strip {{
                display: flex;
                align-items: center;
                gap: 6px;
                flex-wrap: wrap;
            }}
            .btn-action {{
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 11.5px;
                font-weight: 800;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                transition: all 0.15s ease;
                border: 1px solid transparent;
                min-height: 32px;
                touch-action: manipulation;
            }}
            .btn-mic {{
                background: #0284C7;
                color: #FFFFFF;
                border-color: #0284C7;
                box-shadow: 0 1px 4px rgba(2, 132, 199, 0.25);
            }}
            .btn-mic:hover {{
                background: #0369A1;
            }}
            .btn-mic.recording {{
                background: #DC2626 !important;
                border-color: #B91C1C !important;
                box-shadow: 0 0 10px rgba(220, 38, 38, 0.6) !important;
                animation: pulse 1.2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.02); opacity: 0.85; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            .btn-play {{
                background: #4F46E5;
                color: #FFFFFF;
                border-color: #4338CA;
                box-shadow: 0 1px 4px rgba(79, 70, 229, 0.25);
            }}
            .btn-play:hover {{
                background: #4338CA;
            }}
            .btn-pause {{
                background: #D97706;
                color: #FFFFFF;
                border-color: #B45309;
            }}
            .btn-pause:hover {{
                background: #B45309;
            }}
            .btn-stop {{
                background: #64748B;
                color: #FFFFFF;
                border-color: #475569;
            }}
            .btn-stop:hover {{
                background: #475569;
            }}
            .btn-pill-cmd {{
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                cursor: pointer;
                background: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                transition: all 0.15s ease;
                min-height: 28px;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                touch-action: manipulation;
            }}
            .btn-pill-cmd:hover {{
                background: #0284C7;
                color: #FFFFFF;
                border-color: #0284C7;
            }}
            .voice-status {{
                font-size: 11.5px;
                color: #334155;
                font-weight: 600;
                padding: 4px 6px;
                background: #F1F5F9;
                border-radius: 6px;
                border: 1px solid #E2E8F0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .voice-status b {{
                color: #0F172A;
            }}
            .badge-cp {{
                background: #EFF6FF;
                color: #1D4ED8;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 12px;
                border: 1px solid #BFDBFE;
                font-size: 10.5px;
            }}
        </style>
    </head>
    <body>
        <div class="voice-panel">
            <div class="lang-strip">
                <span class="lang-strip-label" style="display:inline-flex; align-items:center; gap:5px;">{icon_globe} Voice Language:</span>
                <button class="btn-lang {'active' if language=='English' else ''}" onclick="switchLanguage('English')" title="English Voice">English</button>
                <button class="btn-lang {'active' if language=='Kannada' else ''}" onclick="switchLanguage('Kannada')" title="ಕನ್ನಡ ಧ್ವನಿ">ಕನ್ನಡ (Kannada)</button>
                <button class="btn-lang {'active' if language=='Hindi' else ''}" onclick="switchLanguage('Hindi')" title="हिंदी आवाज">हिंदी (Hindi)</button>
                <span class="badge-cp" style="margin-left:auto;">{pi18n['badge']}</span>
            </div>
            <div class="controls-strip">
                <button class="btn-action btn-mic" id="btn-stt" onclick="toggleVoiceCommand()" title="Click to speak a voice command into your microphone">
                    {pi18n['mic']}
                </button>
                <button class="btn-action btn-play" id="btn-play" onclick="playActiveStepAudio()" title="Speak active checkpoint aloud">
                    {pi18n['play']}
                </button>
                <button class="btn-action btn-pause" id="btn-pause" onclick="pauseAudio()" title="Pause audio">
                    {pi18n['pause']}
                </button>
                <button class="btn-action btn-stop" id="btn-stop" onclick="stopAudio()" title="Stop audio">
                    {pi18n['stop']}
                </button>

                <div style="display:flex; align-items:center; gap:4px; margin-left:auto; flex-wrap:wrap;">
                    <span style="font-size:10.5px; font-weight:700; color:#64748B;">{pi18n['quick']}</span>
                    <button class="btn-pill-cmd" onclick="handleVoiceCommand('next')" title="Next step">{pi18n['btn_next']}</button>
                    <button class="btn-pill-cmd" onclick="playActiveStepAudio()" title="Repeat instruction">{pi18n['btn_repeat']}</button>
                    <button class="btn-pill-cmd" onclick="handleVoiceCommand('previous')" title="Previous step">{pi18n['btn_back']}</button>
                    <button class="btn-pill-cmd" onclick="handleVoiceCommand('lost')" title="Lost recovery">{pi18n['btn_lost']}</button>
                </div>
            </div>
            <div class="voice-status" id="voice-status">
                {pi18n['status']}
            </div>
        </div>

        <script>
            const speechLang = "{lang_code}";
            const activeScript = {escaped_audio};
            const audioB64 = "{audio_b64}";
            const audioDataUri = audioB64 ? ("data:audio/mp3;base64," + audioB64) : "";
            const shouldAutoPlay = {auto_play_js};
            let isRecording = false;
            let isPaused = false;
            let currentUtterance = null;
            let localRecognition = null;

            // -----------------------------------------------------------------
            // 1. Get Top-Level Window & Synthesis Reference (Parent Bridge)
            // -----------------------------------------------------------------
            function getSpeechContext() {{
                try {{
                    if (window.parent && window.parent.speechSynthesis && window.parent.SpeechSynthesisUtterance) {{
                        return {{
                            win: window.parent,
                            synth: window.parent.speechSynthesis,
                            Utterance: window.parent.SpeechSynthesisUtterance,
                            Speech: window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition || null
                        }};
                    }}
                }} catch(e) {{
                    console.warn("Parent speech context unavailable, using local frame context:", e);
                }}
                return {{
                    win: window,
                    synth: window.speechSynthesis || null,
                    Utterance: window.SpeechSynthesisUtterance || null,
                    Speech: window.SpeechRecognition || window.webkitSpeechRecognition || null
                }};
            }}

            // Pre-load voices immediately on load
            (function initVoices() {{
                const ctx = getSpeechContext();
                if (ctx.synth) {{
                    try {{
                        ctx.synth.getVoices();
                        if (ctx.synth.onvoiceschanged !== undefined) {{
                            ctx.synth.onvoiceschanged = function() {{
                                try {{ ctx.synth.getVoices(); }} catch(e) {{}}
                            }};
                        }}
                    }} catch(e) {{}}
                }}
            }})();

            // Unlock audio on touch or click across top window and iframe
            function unlockAudio() {{
                const ctx = getSpeechContext();
                if (ctx.synth) {{
                    try {{
                        ctx.synth.resume();
                    }} catch(e) {{}}
                }}
            }}
            window.addEventListener('click', unlockAudio, {{ passive: true }});
            window.addEventListener('touchstart', unlockAudio, {{ passive: true }});
            try {{
                if (window.parent && window.parent.document) {{
                    window.parent.document.addEventListener('click', unlockAudio, {{ passive: true }});
                    window.parent.document.addEventListener('touchstart', unlockAudio, {{ passive: true }});
                }}
            }} catch(e) {{}}

            // -----------------------------------------------------------------
            // 2. Multi-tier Voice Search Algorithm
            // -----------------------------------------------------------------
            function findBestVoice(synth, targetLang) {{
                let voices = [];
                try {{
                    voices = synth.getVoices() || [];
                }} catch(e) {{}}
                if (!voices || voices.length === 0) return null;

                const prefix = targetLang.split('-')[0].toLowerCase(); // 'kn', 'hi', 'en'

                // 1. Exact match (e.g. kn-IN, hi-IN, en-IN)
                let matched = voices.find(v => v.lang && v.lang.toLowerCase() === targetLang.toLowerCase());
                if (matched) return matched;

                // 2. Language prefix match (e.g. kn, hi, en)
                matched = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(prefix));
                if (matched) return matched;

                // 3. Regional Indian voice (for Indian context)
                matched = voices.find(v => v.lang && (v.lang.toLowerCase().includes('in') || v.name.toLowerCase().includes('india')));
                if (matched) return matched;

                // 4. Default voice
                matched = voices.find(v => v.default);
                if (matched) return matched;

                // 5. English or first voice
                matched = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('en'));
                return matched || voices[0] || null;
            }}

            // -----------------------------------------------------------------
            // 3. Play Active Step Audio (HD Audio Stream + Web Speech Fallback)
            // -----------------------------------------------------------------
            let activeAudioElement = null;

            function playActiveStepAudio() {{
                const statusEl = document.getElementById('voice-status');

                // Resume if currently paused audio element
                if (activeAudioElement && activeAudioElement.paused && activeAudioElement.currentTime > 0 && !activeAudioElement.ended) {{
                    activeAudioElement.play().catch(function(e) {{}});
                    isPaused = false;
                    statusEl.innerHTML = "🔊 <b>Resumed playback...</b>";
                    return;
                }}

                // Stop any previous playing audio
                stopAudio();

                if (audioDataUri && audioDataUri.length > 50) {{
                    try {{
                        statusEl.innerHTML = "🔊 <b>Playing Checkpoint {checkpoint_num} audio...</b>";
                        const audio = new Audio(audioDataUri);
                        activeAudioElement = audio;

                        audio.onplay = function() {{
                            isPaused = false;
                            statusEl.innerHTML = "🔊 <b>Speaking Checkpoint {checkpoint_num}...</b>";
                        }};

                        audio.onended = function() {{
                            isPaused = false;
                            activeAudioElement = null;
                            statusEl.innerText = "Checkpoint {checkpoint_num} audio completed.";
                        }};

                        audio.onerror = function(e) {{
                            console.warn("Base64 audio playback error, falling back to Web Speech:", e);
                            activeAudioElement = null;
                            playFallbackWebSpeech();
                        }};

                        audio.play().catch(function(err) {{
                            console.warn("Audio play() blocked:", err);
                            activeAudioElement = null;
                            playFallbackWebSpeech();
                        }});
                        return;
                    }} catch(err) {{
                        console.warn("Audio initialization error:", err);
                    }}
                }}

                playFallbackWebSpeech();
            }}

            function playFallbackWebSpeech() {{
                const ctx = getSpeechContext();
                const statusEl = document.getElementById('voice-status');

                if (!ctx.synth || !ctx.Utterance) {{
                    statusEl.innerText = "Audio playback ended.";
                    return;
                }}

                try {{
                    ctx.synth.cancel();
                    ctx.synth.resume();
                }} catch(e) {{}}

                try {{
                    const utterance = new ctx.Utterance(activeScript);
                    const matchedVoice = findBestVoice(ctx.synth, speechLang);

                    if (matchedVoice) {{
                        utterance.voice = matchedVoice;
                        utterance.lang = matchedVoice.lang;
                    }} else {{
                        utterance.lang = speechLang;
                    }}

                    utterance.rate = 0.95;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;

                    utterance.onstart = function() {{
                        statusEl.innerHTML = "🔊 <b>Reading Checkpoint {checkpoint_num}...</b>";
                    }};

                    utterance.onend = function() {{
                        isPaused = false;
                        statusEl.innerText = "Checkpoint {checkpoint_num} audio completed.";
                    }};

                    utterance.onerror = function(event) {{
                        if (event.error === 'canceled' || event.error === 'interrupted') return;
                        if (event.error === 'language-unavailable' || event.error === 'synthesis-failed') {{
                            try {{
                                const fallback = new ctx.Utterance(activeScript);
                                fallback.lang = 'en-US';
                                fallback.rate = 0.95;
                                ctx.synth.speak(fallback);
                                statusEl.innerHTML = "🔊 <b>Speaking using system voice...</b>";
                                return;
                            }} catch(fallbackErr) {{}}
                        }}
                        isPaused = false;
                        statusEl.innerText = "Playback finished.";
                    }};

                    currentUtterance = utterance;
                    ctx.synth.speak(utterance);
                }} catch(err) {{
                    console.error("Web speech fallback error:", err);
                    statusEl.innerText = "Playback finished.";
                }}
            }}

            function pauseAudio() {{
                if (activeAudioElement && !activeAudioElement.paused) {{
                    activeAudioElement.pause();
                    isPaused = true;
                    document.getElementById('voice-status').innerHTML = "⏸ <b>Audio paused.</b> Click Speak Step to resume.";
                    return;
                }}
                const ctx = getSpeechContext();
                if (ctx.synth && ctx.synth.speaking && !ctx.synth.paused) {{
                    ctx.synth.pause();
                    isPaused = true;
                    document.getElementById('voice-status').innerHTML = "⏸ <b>Audio paused.</b> Click Speak Step to resume.";
                }}
            }}

            function stopAudio() {{
                if (activeAudioElement) {{
                    try {{
                        activeAudioElement.pause();
                        activeAudioElement.currentTime = 0;
                    }} catch(e) {{}}
                    activeAudioElement = null;
                }}
                const ctx = getSpeechContext();
                if (ctx.synth) {{
                    try {{ ctx.synth.cancel(); }} catch(e) {{}}
                }}
                isPaused = false;
                document.getElementById('voice-status').innerText = "Audio stopped.";
            }}

            // -----------------------------------------------------------------
            // 4. Speech Recognition (STT Voice Command)
            // -----------------------------------------------------------------
            function resetMicButton() {{
                isRecording = false;
                const btn = document.getElementById('btn-stt');
                btn.classList.remove('recording');
                btn.innerHTML = "{pi18n['mic']}";
            }}

            function toggleVoiceCommand() {{
                if (isRecording) {{
                    if (localRecognition) {{
                        try {{ localRecognition.stop(); }} catch(e) {{}}
                    }}
                    resetMicButton();
                    document.getElementById('voice-status').innerText = "Microphone listening stopped.";
                    return;
                }}
                startVoiceRecognition();
            }}

            function startVoiceRecognition() {{
                try {{
                    if (window.frameElement) {{
                        window.frameElement.setAttribute('allow', 'microphone; speech-recognition; autoplay');
                    }}
                }} catch(e) {{}}

                const ctx = getSpeechContext();
                const statusEl = document.getElementById('voice-status');

                if (!ctx.Speech) {{
                    statusEl.innerHTML = "⚠️ <b>Microphone not supported</b> in this browser. Use the <b>Quick Action</b> buttons above!";
                    return;
                }}

                function executeRecognition() {{
                    try {{
                        const recognition = new ctx.Speech();
                        localRecognition = recognition;
                        recognition.continuous = false;
                        recognition.interimResults = false;
                        recognition.lang = speechLang;

                        recognition.onstart = function() {{
                            isRecording = true;
                            const btn = document.getElementById('btn-stt');
                            if (btn) {{
                                btn.classList.add('recording');
                                btn.innerHTML = "🔴 Listening...";
                            }}
                            statusEl.innerHTML = "🎙️ <b>Listening...</b> Speak in English, ಕನ್ನಡ, or हिंदी (e.g. 'Next', 'Repeat', or name any location).";
                        }};

                        recognition.onresult = function(event) {{
                            const transcript = (event.results && event.results[0] && event.results[0][0])
                                ? event.results[0][0].transcript.trim()
                                : '';
                            statusEl.innerHTML = "🗣️ <b>Heard:</b> \"" + transcript + "\" &bull; Executing...";
                            handleVoiceCommand(transcript);
                        }};

                        recognition.onerror = function(event) {{
                            console.warn("STT Error:", event.error);
                            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {{
                                statusEl.innerHTML = "⚠️ <b>Microphone permission blocked:</b> Click lock/camera icon in address bar to Allow Mic, or tap <b>Quick Action</b> buttons.";
                            }} else if (event.error === 'no-speech') {{
                                statusEl.innerHTML = "⚠️ <b>No speech detected.</b> Click <b>Voice Command</b> and speak again.";
                            }} else {{
                                statusEl.innerHTML = "⚠️ <b>Mic:</b> " + event.error + ". Use the <b>Quick Action</b> buttons.";
                            }}
                            resetMicButton();
                        }};

                        recognition.onend = function() {{
                            resetMicButton();
                        }};

                        recognition.start();
                    }} catch(err) {{
                        console.error("Speech Recognition Start Error:", err);
                        statusEl.innerHTML = "⚠️ <b>Mic Access:</b> Tap <b>Voice Command</b> again or use the <b>Quick Action</b> buttons.";
                        resetMicButton();
                    }}
                }}

                // Explicitly prompt user for microphone permission via getUserMedia
                const nav = (window.parent && window.parent.navigator && window.parent.navigator.mediaDevices)
                    ? window.parent.navigator
                    : navigator;

                if (nav.mediaDevices && nav.mediaDevices.getUserMedia) {{
                    statusEl.innerHTML = "🎙️ <b>Requesting microphone access...</b> Please click <b>'Allow'</b> in the browser prompt.";
                    nav.mediaDevices.getUserMedia({{ audio: true }})
                        .then(function(stream) {{
                            stream.getTracks().forEach(function(t) {{ t.stop(); }});
                            executeRecognition();
                        }})
                        .catch(function(err) {{
                            console.warn("getUserMedia permission error:", err);
                            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {{
                                statusEl.innerHTML = "⚠️ <b>Microphone permission denied:</b> Click lock 🔒 in address bar, choose <b>'Allow'</b> for Microphone, then tap <b>Voice Command</b> again.";
                                resetMicButton();
                            }} else {{
                                executeRecognition();
                            }}
                        }});
                }} else {{
                    executeRecognition();
                }}
            }}

            // -----------------------------------------------------------------
            // 5. Parent Navigation Trigger & Action Handler
            // -----------------------------------------------------------------
            function triggerParentAction(actionType) {{
                try {{
                    const parentDoc = window.parent.document;
                    let targetSelector = null;
                    if (actionType === 'next') {{
                        targetSelector = '.st-key-btn_next_step button, .st-key-btn_finish_step button';
                    }} else if (actionType === 'prev') {{
                        targetSelector = '.st-key-btn_prev_step button';
                    }} else if (actionType === 'lost') {{
                        targetSelector = '.st-key-btn_lost_user button';
                    }}

                    if (targetSelector) {{
                        const btn = parentDoc.querySelector(targetSelector);
                        if (btn) {{
                            btn.click();
                            return true;
                        }}
                    }}

                    // Fallback button search by text
                    const buttons = parentDoc.querySelectorAll('button');
                    for (let btn of buttons) {{
                        const txt = (btn.innerText || '').toLowerCase();
                        if (actionType === 'next' && (
                            txt.includes('next') || txt.includes('reached') || txt.includes('arrived') ||
                            txt.includes('ಮುಂದಿನ') || txt.includes('ಮುಂದೆ') || txt.includes('ತಲುಪಿದೆ') ||
                            txt.includes('आगे') || txt.includes('अगला') || txt.includes('पहुँच')
                        )) {{
                            btn.click();
                            return true;
                        }} else if (actionType === 'prev' && (
                            txt.includes('previous') || txt.includes('back') ||
                            txt.includes('ಹಿಂದಿನ') || txt.includes('ಹಿಂದೆ') ||
                            txt.includes('पिछला') || txt.includes('पीछे')
                        )) {{
                            btn.click();
                            return true;
                        }} else if (actionType === 'lost' && (
                            txt.includes('lost') || txt.includes('help') || txt.includes('where am i') ||
                            txt.includes('ದಾರಿ ತಪ್ಪಿದೆ') || txt.includes('ಸಹಾಯ') ||
                            txt.includes('भटक') || txt.includes('मदद')
                        )) {{
                            btn.click();
                            return true;
                        }}
                    }}
                }} catch(e) {{
                    console.warn("Parent button click trigger error:", e);
                }}
                return false;
            }}

            function handleVoiceCommand(rawTranscript) {{
                const statusEl = document.getElementById('voice-status');
                const transcript = (rawTranscript || '').toLowerCase().trim();

                // 1. Next Checkpoint
                if (
                    transcript.includes('next') || transcript.includes('done') || transcript.includes('continue') || transcript.includes('reached') || transcript.includes('arrived') ||
                    transcript.includes('ಮುಂದೆ') || transcript.includes('ಮುಂದಿನ') || transcript.includes('ತಲುಪಿದೆ') || transcript.includes('ಹೋಗು') ||
                    transcript.includes('आगे') || transcript.includes('अगला') || transcript.includes('पहुँच') || transcript.includes('चलो')
                ) {{
                    const ok = triggerParentAction('next');
                    statusEl.innerHTML = ok ? "✅ <b>Action:</b> Advancing to Next Checkpoint..." : "Advancing to next step...";
                    return;
                }}

                // 2. Previous Checkpoint
                if (
                    transcript.includes('previous') || transcript.includes('back') ||
                    transcript.includes('ಹಿಂದೆ') || transcript.includes('ಹಿಂದಿನ') ||
                    transcript.includes('वापस') || transcript.includes('पीछे') || transcript.includes('पिछला')
                ) {{
                    const ok = triggerParentAction('prev');
                    statusEl.innerHTML = ok ? "⏮️ <b>Action:</b> Returning to Previous Checkpoint..." : "Returning to previous step...";
                    return;
                }}

                // 3. Repeat Active Instruction
                if (
                    transcript.includes('repeat') || transcript.includes('again') || transcript.includes('once more') || transcript.includes('speak') || transcript.includes('listen') ||
                    transcript.includes('ಮತ್ತೊಮ್ಮೆ') || transcript.includes('ಮತ್ತೆ') || transcript.includes('ಪುನರಾವರ್ತಿಸಿ') || transcript.includes('ಹೇಳಿ') || transcript.includes('ಕೇಳಿ') ||
                    transcript.includes('दोहराएं') || transcript.includes('फिर') || transcript.includes('सुनाओ') || transcript.includes('बोलो')
                ) {{
                    statusEl.innerHTML = "🔄 <b>Action:</b> Repeating Checkpoint Instruction...";
                    playActiveStepAudio();
                    return;
                }}

                // 4. Lost User Recovery
                if (
                    transcript.includes('lost') || transcript.includes('help') || transcript.includes('where am i') || transcript.includes('confused') ||
                    transcript.includes('ದಾರಿ ತಪ್ಪಿದೆ') || transcript.includes('ಸಹಾಯ') || transcript.includes('ಕಳೆದು') ||
                    transcript.includes('भटक') || transcript.includes('खो गया') || transcript.includes('मदद')
                ) {{
                    const ok = triggerParentAction('lost');
                    statusEl.innerHTML = ok ? "🆘 <b>Action:</b> Opening Lost User Recovery..." : "Opening help...";
                    return;
                }}

                // 5. Spoken destination or query (e.g. "Library", "G11", "Toilet", "ಕಂಪ್ಯೂಟರ್", "ಗ್ರಂಥಾಲಯ")
                try {{
                    const parentDoc = window.parent.document;
                    const voiceInput = parentDoc.querySelector('.st-key-multilingual_voice_input input, .st-key-sb_search_field input, input[type="text"]');
                    if (voiceInput && rawTranscript.length > 2) {{
                        voiceInput.value = rawTranscript;
                        voiceInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        voiceInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        statusEl.innerHTML = "🎯 <b>Searching destination:</b> \"" + rawTranscript + "\"...";
                        setTimeout(function() {{
                            const submitBtn = parentDoc.querySelector('.st-key-voice_submit_btn button, .st-key-qs_navigate_btn button');
                            if (submitBtn) submitBtn.click();
                        }}, 200);
                        return;
                    }}
                }} catch(e) {{
                    console.warn("Parent query search trigger error:", e);
                }}

                statusEl.innerHTML = "🗣️ Heard: \"" + rawTranscript + "\". Say <b>'Next'</b>, <b>'Repeat'</b>, or name a destination.";
            }}

            // -----------------------------------------------------------------
            // 6. Switch Language
            // -----------------------------------------------------------------
            function switchLanguage(targetLang) {{
                try {{
                    const parentDoc = window.parent.document;
                    if (targetLang === 'English') {{
                        const btn = parentDoc.querySelector('.st-key-lang_tab_btn_en button');
                        if (btn) {{ btn.click(); return; }}
                    }} else if (targetLang === 'Kannada') {{
                        const btn = parentDoc.querySelector('.st-key-lang_tab_btn_kn button');
                        if (btn) {{ btn.click(); return; }}
                    }} else if (targetLang === 'Hindi') {{
                        const btn = parentDoc.querySelector('.st-key-lang_tab_btn_hi button');
                        if (btn) {{ btn.click(); return; }}
                    }}
                    const buttons = parentDoc.querySelectorAll('button');
                    for (let btn of buttons) {{
                        const txt = (btn.innerText || '').trim();
                        if (targetLang === 'English' && txt.includes('English')) {{
                            btn.click();
                            return;
                        }} else if (targetLang === 'Kannada' && (txt.includes('ಕನ್ನಡ') || txt.includes('Kannada'))) {{
                            btn.click();
                            return;
                        }} else if (targetLang === 'Hindi' && (txt.includes('हिंदी') || txt.includes('Hindi'))) {{
                            btn.click();
                            return;
                        }}
                    }}
                }} catch(e) {{
                    console.log("Language switch error:", e);
                }}
            }}

            // -----------------------------------------------------------------
            // 7. Auto-play on step advancement if enabled
            // -----------------------------------------------------------------
            if (shouldAutoPlay) {{
                setTimeout(playActiveStepAudio, 300);
            }}
        </script>
    </body>
    </html>
    """
    return html_code
