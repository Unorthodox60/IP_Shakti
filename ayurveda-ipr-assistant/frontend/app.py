import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Ayurveda IPR Assistant", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
/* ---------------------------------------------------------
   CSS VARIABLES & DESIGN SYSTEM
--------------------------------------------------------- */
:root {
    --color-bg: #0B0D10;
    --color-surface: #161920;
    --color-border: #2A2E37;
    --color-primary: #E8A33D;
    --color-success: #2D6A4F;
    --color-warning: #E8A33D;
    --color-danger: #DC4C4C;
    --color-text: #E2E8F0;
    --color-text-muted: #94A3B8;
    
    --shadow-elevation: 0 4px 24px rgba(0, 0, 0, 0.4);
    --shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.5);
    
    --font-base: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* ---------------------------------------------------------
   GLOBAL & LAYOUT
--------------------------------------------------------- */
.stApp {
    background-color: var(--color-bg);
    color: var(--color-text);
    font-family: var(--font-base);
    font-size: 16px;
    line-height: 1.5;
    /* Subtle radial gradient behind header */
    background-image: radial-gradient(circle at 50% 0%, rgba(232, 163, 61, 0.05) 0%, transparent 40%);
    background-attachment: fixed;
}

header { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* Typography */
h1 { font-size: 32px !important; margin-bottom: 24px !important; color: #FFFFFF !important; font-weight: 700 !important; }
h2 { font-size: 24px !important; margin-bottom: 16px !important; color: #FFFFFF !important; font-weight: 700 !important; }
h3 { font-size: 18px !important; margin-bottom: 16px !important; color: #FFFFFF !important; font-weight: 700 !important; }
.caption { font-size: 14px; color: var(--color-text-muted); font-weight: 400; }

/* ---------------------------------------------------------
   ANIMATIONS
--------------------------------------------------------- */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes pulseOnce {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

/* Staggered classes for load */
.animate-in-1 { animation: fadeSlideUp 250ms ease-out forwards; animation-delay: 0ms; opacity: 0; }
.animate-in-2 { animation: fadeSlideUp 250ms ease-out forwards; animation-delay: 40ms; opacity: 0; }
.animate-in-3 { animation: fadeSlideUp 250ms ease-out forwards; animation-delay: 80ms; opacity: 0; }
.animate-in-4 { animation: fadeSlideUp 250ms ease-out forwards; animation-delay: 120ms; opacity: 0; }
.animate-msg { animation: fadeSlideUp 200ms ease-out forwards; }
.animate-badge { animation: scaleIn 200ms ease-out forwards; }
.animate-pulse { animation: pulseOnce 300ms ease-out forwards; }

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; opacity: 1 !important; }
}

/* ---------------------------------------------------------
   COMPONENTS
--------------------------------------------------------- */
.topbar-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 24px;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 8px;
    margin-bottom: 32px;
}
.svg-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* Jurisdiction Pill Switch */
.stRadio > div {
    background-color: var(--color-surface);
    border-radius: 9999px;
    padding: 4px;
    display: flex;
    gap: 4px;
    border: 1px solid var(--color-border);
    float: right;
    margin-top: 8px;
    box-shadow: var(--shadow-elevation);
}
.stRadio > div > label {
    background-color: transparent;
    padding: 8px 24px;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
    margin: 0;
}
.stRadio > div > label[data-checked="true"] {
    background-color: var(--color-primary) !important;
}
.stRadio > div > label[data-checked="true"] p {
    color: var(--color-bg) !important;
    font-weight: 600;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--color-bg) !important;
    border-right: 1px solid var(--color-border) !important;
}
[data-testid="stSidebarContent"] {
    padding-top: 32px !important;
}

/* Cards */
.custom-card {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-elevation);
    transition: transform 150ms ease, box-shadow 150ms ease;
}
.custom-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.status-dot {
    height: 10px;
    width: 10px;
    background-color: var(--color-success);
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulseOnce 2s infinite;
}

/* Badges */
.badge {
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: background-color 200ms, color 200ms;
}
.badge-high { background-color: rgba(45, 106, 79, 0.15); color: var(--color-success); border: 1px solid var(--color-success); }
.badge-medium { background-color: rgba(232, 163, 61, 0.15); color: var(--color-warning); border: 1px solid var(--color-warning); }
.badge-low { background-color: rgba(220, 76, 76, 0.15); color: var(--color-danger); border: 1px solid var(--color-danger); }
.badge-neutral { background-color: rgba(148, 163, 184, 0.15); color: var(--color-text-muted); border: 1px solid var(--color-text-muted); }

/* Chips */
.chip {
    display: inline-flex;
    align-items: center;
    background-color: var(--color-bg);
    border: 1px solid var(--color-border);
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    margin-right: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 150ms ease;
    color: var(--color-text-muted);
}
.chip:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
}

/* Buttons */
.stButton > button {
    background-color: var(--color-primary) !important;
    color: var(--color-bg) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    transition: all 150ms ease !important;
    min-height: 44px;
    width: 100%;
}
.stButton > button:hover {
    background-color: #f0b75e !important;
    transform: scale(0.97);
}
.stButton > button:active {
    transform: scale(0.95);
}

/* Secondary Button (Reset) */
.stButton:nth-of-type(1) > button {
    background-color: transparent !important;
    border: 1px solid var(--color-border) !important;
    color: var(--color-text) !important;
}
.stButton:nth-of-type(1) > button:hover {
    border-color: var(--color-primary) !important;
    color: var(--color-primary) !important;
    background-color: rgba(232, 163, 61, 0.1) !important;
    transform: scale(0.97);
}

/* Chat Interface */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: 24px;
}
[data-testid="stChatMessageContent"] {
    border-radius: 12px;
    padding: 16px 24px;
    color: var(--color-text);
}
/* Assistant Bubble */
[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-elevation);
}
/* User Bubble */
[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
    background-color: rgba(232, 163, 61, 0.05);
    border: 1px solid rgba(232, 163, 61, 0.15);
}

/* Chat Input */
.stChatInputContainer {
    background-color: var(--color-surface) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 9999px !important;
    padding: 4px 16px !important;
    margin-bottom: 48px !important;
    box-shadow: var(--shadow-elevation) !important;
    transition: border-color 200ms, box-shadow 200ms;
}
.stChatInputContainer:focus-within {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 2px rgba(232, 163, 61, 0.3), var(--shadow-elevation) !important;
}
.stTextArea textarea {
    background-color: transparent !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 8px !important;
    color: var(--color-text) !important;
}
.stTextArea textarea:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 1px var(--color-primary) !important;
}

/* Alerts / Error */
.status-alert {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 14px;
    margin-top: 16px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-elevation);
}
.status-alert.error { border-color: rgba(220, 76, 76, 0.5); background-color: rgba(220, 76, 76, 0.05); color: var(--color-danger); }
.status-alert.warning { border-color: rgba(232, 163, 61, 0.5); background-color: rgba(232, 163, 61, 0.05); color: var(--color-warning); }
.status-alert.info { border-color: var(--color-border); color: var(--color-text); }

/* Disclaimer */
.disclaimer-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-bg);
    text-align: center;
    font-size: 12px;
    color: var(--color-text-muted);
    padding: 12px;
    z-index: 999;
    border-top: 1px solid var(--color-border);
}

/* Shimmer Loading */
.skeleton {
    height: 16px;
    border-radius: 4px;
    margin-bottom: 12px;
    background: linear-gradient(to right, var(--color-surface) 8%, #222630 18%, var(--color-surface) 33%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite linear forwards;
}
.skeleton.w-75 { width: 75%; }
.skeleton.w-50 { width: 50%; }

/* Simple Mode Pill */
.simple-mode-pill {
    position: absolute;
    bottom: 110px;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--color-success);
    color: #fff;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    z-index: 100;
    box-shadow: var(--shadow-elevation);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    animation: fadeSlideUp 200ms ease-out forwards;
}
</style>
"""

# SVG Icons
ICON_LEAF = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>'
ICON_SHIELD = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>'
ICON_ALERT_RED = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
ICON_ALERT_AMBER = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
ICON_CHECK = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
ICON_SCALE = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M3 13.9v-2a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2"/><path d="M3 14c0 1.66 1.79 3 4 3s4-1.34 4-3"/><path d="M13 14c0 1.66 1.79 3 4 3s4-1.34 4-3"/></svg>'
ICON_HISTORY = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
ICON_FARMER = '<svg class="svg-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

# Layout: Top Bar
st.markdown('<div class="animate-in-1">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f'<div class="topbar-title">{ICON_LEAF} Ayurveda IPR Assistant</div>', unsafe_allow_html=True)
with col2:
    jurisdiction = st.radio("Jurisdiction", ["India", "International"], horizontal=True, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# State Management
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "classifier_node" not in st.session_state: st.session_state.classifier_node = "q1"; st.session_state.classification_done = False
if "scanner_result" not in st.session_state: st.session_state.scanner_result = None

# Sidebar: Farmer Mode Toggle
st.sidebar.markdown(f'<div class="animate-in-1" style="font-size: 18px; font-weight: 700; color: #FFF; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">{ICON_FARMER} Settings</div>', unsafe_allow_html=True)
farmer_mode = st.sidebar.toggle("Explain Like I'm a Farmer 🌾", value=False, key="farmer_toggle")
simplicity_mode = "simple" if farmer_mode else "technical"
st.sidebar.divider()

# Sidebar: Formulation Classification
st.sidebar.markdown(f'<div class="animate-in-2" style="font-size: 18px; font-weight: 700; color: #FFF; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">{ICON_SCALE} Formulation Classification</div>', unsafe_allow_html=True)

if not st.session_state.classification_done:
    try:
        response = requests.post(f"{API_URL}/classify", json={"node_id": st.session_state.classifier_node})
        if response.status_code == 200:
            node_data = response.json()
            if node_data.get("type") == "classification":
                st.sidebar.markdown(f'''
                <div class="custom-card animate-in-3">
                    <div style="margin-bottom: 12px; font-weight: 700; color: #FFF; display: flex; align-items: center;"><span class="status-dot"></span>{node_data['category']}</div>
                    <div class="caption">{node_data['explanation']}</div>
                </div>
                ''', unsafe_allow_html=True)
                st.session_state.classification_done = True
                if st.sidebar.button("Reset Classification", key="reset_1"):
                    st.session_state.classifier_node = "q1"
                    st.session_state.classification_done = False
                    st.rerun()
            else:
                st.sidebar.markdown(f'<div class="animate-in-3" style="font-size: 14px; margin-bottom: 16px; font-weight: 500;">{node_data["text"]}</div>', unsafe_allow_html=True)
                for i, option in enumerate(node_data['options']):
                    if st.sidebar.button(option['label'], key=f"opt_{i}"):
                        st.session_state.classifier_node = option['next']
                        st.rerun()
    except Exception as e:
        st.sidebar.markdown(f'''
        <div class="status-alert error animate-in-3">
            {ICON_ALERT_RED}
            <div><strong>Backend not running</strong><br/>Start api.py first.</div>
        </div>
        ''', unsafe_allow_html=True)
else:
    # Final Result State
    try:
        response = requests.post(f"{API_URL}/classify", json={"node_id": st.session_state.classifier_node})
        if response.status_code == 200:
            node_data = response.json()
            st.sidebar.markdown(f'''
            <div class="custom-card animate-in-3">
                <div style="margin-bottom: 12px; font-weight: 700; color: #FFF; display: flex; align-items: center;"><span class="status-dot" style="animation: none;"></span>{node_data['category']}</div>
                <div class="caption">{node_data['explanation']}</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.sidebar.button("Reset Classification", key="reset_2"):
                st.session_state.classifier_node = "q1"
                st.session_state.classification_done = False
                st.rerun()
    except:
        pass

# Sidebar: Patent Risk Scanner
st.sidebar.markdown(f'<div class="animate-in-4" style="font-size: 18px; font-weight: 700; color: #FFF; margin-top: 32px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">{ICON_SHIELD} Patent Risk Scanner</div>', unsafe_allow_html=True)
scanner_input = st.sidebar.text_area("Describe formulation...", placeholder="e.g. Ashwagandha mixed with Vitamin C...", label_visibility="collapsed", height=100)

if st.sidebar.button("Scan Form", key="scan_btn"):
    if scanner_input.strip():
        # Loading Shimmer
        placeholder = st.sidebar.empty()
        placeholder.markdown('''
        <div class="custom-card">
            <div class="skeleton w-75"></div>
            <div class="skeleton"></div>
            <div class="skeleton w-50"></div>
        </div>
        ''', unsafe_allow_html=True)
        try:
            res = requests.post(f"{API_URL}/scan-risk", json={"description": scanner_input})
            st.session_state.scanner_result = res.json() if res.status_code == 200 else {"error": "API Error"}
        except Exception:
            st.session_state.scanner_result = {"error": "Connection Failed"}
        placeholder.empty()
    else:
        st.session_state.scanner_result = None

if st.session_state.scanner_result:
    res = st.session_state.scanner_result
    if "error" in res:
        st.sidebar.markdown(f'''
        <div class="status-alert error animate-msg">
            {ICON_ALERT_RED}
            <div><strong>{res["error"]}</strong><br/>Ensure backend is running.</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        rl = res.get("risk_level", "Unknown")
        badge_cls = "badge-high" if rl == "Low Risk" else "badge-medium" if rl == "Medium Risk" else "badge-low" if rl == "High Risk" else "badge-neutral"
        icon = ICON_CHECK if rl == "Low Risk" else ICON_ALERT_AMBER if rl == "Medium Risk" else ICON_ALERT_RED if rl == "High Risk" else ICON_ALERT_AMBER
        
        st.sidebar.markdown(f'''
        <div class="custom-card animate-badge">
            <span class="badge {badge_cls} animate-pulse" style="float: right; margin-bottom: 12px;">{icon} {rl}</span>
            <div style="clear: both;"></div>
            <div class="caption" style="margin-bottom: 12px;">{res.get('explanation', '')}</div>
        ''', unsafe_allow_html=True)
        
        if res.get("matched_sources"):
            with st.sidebar.expander("Matched Sources"):
                chips_html = "".join([f'<span class="chip">{src}</span>' for src in res["matched_sources"]])
                st.markdown(chips_html, unsafe_allow_html=True)
                
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        case = res.get("related_case_study")
        if case:
            st.sidebar.markdown(f'''
            <div class="custom-card animate-msg" style="border-left: 4px solid var(--color-text-muted); margin-top: 8px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #E2E8F0; margin-bottom: 12px;">
                    {ICON_HISTORY} Historical Precedent
                </div>
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #FFF;">{case['ingredient']} patent by {case['applicant']} ({case['year']})</div>
                <div class="caption" style="margin-bottom: 12px;">{case['summary']}</div>
                <div style="font-size: 13px; color: var(--color-text-muted); font-weight: 600; display: flex; align-items: flex-start; gap: 4px;">
                    <div style="margin-top: 2px;">↳</div>
                    <div>Outcome: {case['outcome']}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

st.sidebar.markdown('<div style="margin-top: 64px; font-size: 12px; color: var(--color-text-muted); text-align: center;">Ayurveda IPR Assistant v1.0<br/>Legal-Tech SaaS UI</div>', unsafe_allow_html=True)

# Main Chat Interface
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            confidence = msg.get("confidence", "Low")
            badge_cls = "badge-high" if confidence == "High" else "badge-medium" if confidence == "Medium" else "badge-low"
            icon = ICON_CHECK if confidence == "High" else ICON_ALERT_AMBER if confidence == "Medium" else ICON_ALERT_RED
            
            st.markdown(f'<div class="badge {badge_cls}" style="float: right;">{icon} {confidence}</div><div style="clear: both; margin-bottom: 12px;"></div>', unsafe_allow_html=True)
            st.write(msg["content"])
            
            if confidence == "Low":
                st.markdown(f'''
                <div class="status-alert warning">
                    {ICON_ALERT_AMBER} 
                    <div><strong>Uncertain Result</strong><br/>Consider escalating to a human IP facilitator before filing.</div>
                </div>
                ''', unsafe_allow_html=True)
                
            citations = msg.get("citations", [])
            if citations:
                with st.expander("Sources & Citations"):
                    chips_html = "".join([f'<span class="chip">{cit}</span>' for cit in citations])
                    st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.write(msg["content"])

if farmer_mode:
    st.markdown(f'<div class="simple-mode-pill">{ICON_CHECK} Simple Mode Active</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask a question about Ayurveda IP..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="animate-msg">{prompt}</div>', unsafe_allow_html=True)
        
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown('''
        <div class="skeleton w-75"></div>
        <div class="skeleton"></div>
        <div class="skeleton w-50"></div>
        ''', unsafe_allow_html=True)
        
        try:
            payload = {"query": prompt, "jurisdiction": jurisdiction, "simplicity_mode": simplicity_mode}
            res = requests.post(f"{API_URL}/chat", json=payload)
            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "")
                confidence = data.get("confidence", "Low")
                citations = data.get("citations", [])
                
                placeholder.empty()
                
                # Container for animation
                st.markdown('<div class="animate-msg">', unsafe_allow_html=True)
                
                badge_cls = "badge-high" if confidence == "High" else "badge-medium" if confidence == "Medium" else "badge-low"
                icon = ICON_CHECK if confidence == "High" else ICON_ALERT_AMBER if confidence == "Medium" else ICON_ALERT_RED
                
                st.markdown(f'<div class="badge {badge_cls} animate-pulse" style="float: right;">{icon} {confidence}</div><div style="clear: both; margin-bottom: 12px;"></div>', unsafe_allow_html=True)
                st.write(answer)
                
                if confidence == "Low":
                    st.markdown(f'''
                    <div class="status-alert warning">
                        {ICON_ALERT_AMBER} 
                        <div><strong>Uncertain Result</strong><br/>Consider escalating to a human IP facilitator before filing.</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                if citations:
                    with st.expander("Sources & Citations"):
                        chips_html = "".join([f'<span class="chip">{cit}</span>' for cit in citations])
                        st.markdown(chips_html, unsafe_allow_html=True)
                        
                st.markdown('</div>', unsafe_allow_html=True)
                        
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "confidence": confidence,
                    "citations": citations
                })
            else:
                placeholder.empty()
                st.error("Error from backend.")
        except Exception as e:
            placeholder.empty()
            st.markdown(f'''
            <div class="status-alert error animate-msg">
                {ICON_ALERT_RED}
                <div><strong>Backend Connection Failed</strong><br/>Ensure api.py is running on port 8000.</div>
            </div>
            ''', unsafe_allow_html=True)

# Fixed bottom disclaimer
st.markdown('<div class="disclaimer-bar">This is information, not legal advice.</div>', unsafe_allow_html=True)
