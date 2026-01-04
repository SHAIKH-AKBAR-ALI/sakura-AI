import streamlit as st
import sys
import os
import re
import requests
import html
import time
import logging
from urllib.parse import quote
from dotenv import load_dotenv

# --- Project Setup ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from pipeline.pipeline import AnimeRecommendationPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="Sakura AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🍥 NARUTO THEME CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Roboto+Condensed:wght@400;700&display=swap');
    
    :root {
        --naruto-orange: #FF6600;
        --naruto-dark: #0F0F0F;
        --naruto-grey: #1F1F1F;
        --chakra-blue: #00AAFF;
        --text-color: #FFFFFF;
    }

    .stApp {
        background-color: var(--naruto-dark);
        font-family: 'Roboto Condensed', sans-serif;
    }

    /* === SIDEBAR STYLING === */
    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 2px solid var(--naruto-orange);
    }
    
    /* Ninja Profile HUD */
    .profile-hud {
        background: linear-gradient(160deg, #1a1a1a 0%, #000 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #333;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    
    .profile-hud::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 4px;
        background: var(--naruto-orange);
    }

    .avatar-section {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .avatar-circle {
        width: 60px; height: 60px;
        border-radius: 50%;
        background: #333;
        display: flex; align-items: center; justify-content: center;
        border: 2px solid var(--chakra-blue);
        font-size: 24px;
    }
    
    .user-info h3 {
        margin: 0; color: white; font-size: 1.1rem;
        font-family: 'Bangers', cursive; letter-spacing: 1px;
    }
    
    .user-info span {
        font-size: 0.8rem; color: #888;
    }

    /* Chakra Bar */
    .chakra-container {
        margin-top: 10px;
    }
    .chakra-label {
        font-size: 0.7rem; color: var(--chakra-blue);
        display: flex; justify-content: space-between; margin-bottom: 4px;
    }
    .chakra-bar-bg {
        width: 100%; height: 8px; background: #333; border-radius: 4px; overflow: hidden;
    }
    .chakra-bar-fill {
        height: 100%; background: var(--chakra-blue);
        box-shadow: 0 0 8px var(--chakra-blue);
        transition: width 0.5s ease;
    }

    /* History Items */
    .history-item {
        background: #111;
        border-left: 3px solid #333;
        padding: 8px;
        margin-bottom: 5px;
        font-size: 0.85rem;
        color: #ccc;
        transition: all 0.2s;
        cursor: pointer;
    }
    .history-item:hover {
        border-left-color: var(--naruto-orange);
        background: #1a1a1a;
        color: white;
    }

    /* === MAIN UI === */
    .hero-container {
        text-align: center;
        padding: 3rem 0;
        border-bottom: 2px solid var(--naruto-orange);
        background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(255, 102, 0, 0.05) 100%);
        margin-bottom: 2rem;
    }

    .hero-title {
        font-family: 'Bangers', cursive;
        font-size: 5rem;
        color: var(--naruto-orange);
        letter-spacing: 2px;
        text-shadow: 3px 3px 0px #000;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--chakra-blue);
        font-size: 1.2rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: -10px;
    }

    /* Cards */
    .anime-card {
        background: #1E1E1E;
        border: 2px solid #333;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.3s ease;
        height: 420px;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .anime-card:hover {
        transform: translateY(-5px);
        border-color: var(--chakra-blue);
        box-shadow: 0 0 15px rgba(0, 170, 255, 0.4);
    }
    .card-image {
        height: 240px; width: 100%; object-fit: cover; position: relative;
    }
    .score-tag {
        position: absolute; top: 10px; right: 10px;
        background: var(--naruto-orange); color: black;
        font-weight: bold; padding: 4px 8px;
        font-family: 'Bangers', cursive;
        clip-path: polygon(10% 0, 100% 0%, 100% 100%, 0% 100%);
    }
    .card-content {
        padding: 12px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;
    }
    .card-title {
        color: white; font-weight: bold; font-size: 1.1rem;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .card-desc {
        font-size: 0.85rem; color: #aaa;
        display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }

    /* Buttons */
    .stButton button {
        border: 2px solid var(--naruto-orange);
        color: var(--naruto-orange);
        font-family: 'Bangers', cursive;
        background: transparent;
        border-radius: 0;
        width: 100%;
    }
    .stButton button:hover {
        background: var(--naruto-orange); color: black;
    }
    
    .stChatMessage {
        background: #1a1a1a !important;
        border-left: 4px solid var(--chakra-blue);
    }
</style>
""", unsafe_allow_html=True)

# --- 🧠 LOGIC ---

@st.cache_data(ttl=3600)
def fetch_anime_data(anime_name):
    """Robust Jikan Fetcher."""
    fallback_img = "https://i.imgur.com/v8p1yC8.png"
    fallback_data = {
        "image_url": fallback_img,
        "url": f"https://myanimelist.net/anime.php?q={quote(anime_name)}",
        "score": "N/A", "year": "?", "genres": []
    }

    if not anime_name: return fallback_data
    
    # Cleaning
    clean_title = re.sub(r'(:\s*The Movie)+', ': The Movie', anime_name, flags=re.IGNORECASE)
    clean_title = clean_title.replace("Title:", "").strip()
    search_query = clean_title.split(':')[0].strip()
    
    url = f"https://api.jikan.moe/v4/anime?q={quote(search_query)}&limit=1"
    
    try:
        time.sleep(0.35) 
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                res = data['data'][0]
                img = res.get('images', {}).get('jpg', {}).get('large_image_url') or fallback_img
                return {
                    "image_url": img,
                    "url": res.get('url', fallback_data['url']),
                    "score": res.get('score', 'N/A'),
                    "year": res.get('year', '?'),
                    "genres": [g['name'] for g in res.get('genres', [])[:2]]
                }
    except Exception as e:
        logging.error(f"API Error: {e}")
        
    return fallback_data

def sanitize_html(text):
    return html.escape(str(text)) if text else ""

# --- 🚀 INITIALIZATION ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Dattebayo! 🍥 I'm Sakura AI. What kind of mission (recommendation) do you need today?"}
    ]
if "user_stats" not in st.session_state:
    st.session_state.user_stats = {"genres": {}, "count": 0, "history": []}

@st.cache_resource
def get_pipeline():
    return AnimeRecommendationPipeline() if PIPELINE_AVAILABLE else None

pipeline = get_pipeline()

# --- 📜 NEW DASHBOARD SIDEBAR ---
with st.sidebar:
    # 1. RANK & CHAKRA CALCULATION
    count = st.session_state.user_stats["count"]
    
    # Simple leveling system
    if count < 5:
        rank = "GENIN"
        chakra_percent = min(count * 20, 100) # 0-100% based on 5 missions
    elif count < 20:
        rank = "CHUNIN"
        chakra_percent = min((count-5) * 6, 100)
    elif count < 50:
        rank = "JONIN"
        chakra_percent = min((count-20) * 3, 100)
    else:
        rank = "HOKAGE"
        chakra_percent = 100

    # 2. NINJA HUD
    st.markdown(f"""
    <div class="profile-hud">
        <div class="avatar-section">
            <div class="avatar-circle">🥷</div>
            <div class="user-info">
                <h3>SHINOBI #884</h3>
                <span>RANK: <span style="color: #FF6600; font-weight: bold;">{rank}</span></span>
            </div>
        </div>
        <div class="chakra-container">
            <div class="chakra-label">
                <span>CHAKRA LEVEL</span>
                <span>{count} MISSIONS</span>
            </div>
            <div class="chakra-bar-bg">
                <div class="chakra-bar-fill" style="width: {chakra_percent}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. MISSION LOG (HISTORY)
    st.markdown("### 📜 MISSION LOG")
    if st.session_state.user_stats["history"]:
        # Show last 5 searches
        for past in st.session_state.user_stats["history"][-5:][::-1]:
            if st.button(f"↻ {past[:20]}...", key=f"hist_{past}"):
                st.session_state.messages.append({"role": "user", "content": past})
                st.rerun()
    else:
        st.caption("No missions logged yet.")

    st.markdown("---")
    if st.button("❌ ABORT MISSION (Reset)"):
        st.session_state.messages = [{"role": "assistant", "content": "Dattebayo! Ready for a new mission?"}]
        st.session_state.user_stats = {"genres": {}, "count": 0, "history": []}
        st.rerun()

# --- 🏘️ MAIN UI ---

st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">SAKURA AI</h1>
    <div class="hero-subtitle">⭐ Anime Sensei at Your Service ⭐</div>
</div>
""", unsafe_allow_html=True)

# QUICK ACTIONS
cols = st.columns(4)
actions = ["🔥 Shonen Hits", "⚔️ Ninja Action", "👹 Demon Slayer", "🤖 Mecha"]
for i, act in enumerate(actions):
    with cols[i]:
        if st.button(act, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": f"Recommend me {act} anime"})
            st.rerun()

# CHAT RENDER
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "recommendations" in msg:
            st.markdown(f"**🌟 MISSION REPORT: TOP 3 MATCHES**")
            cols = st.columns(3)
            for idx, rec in enumerate(msg["recommendations"]):
                col_idx = idx % 3
                if "image_data" not in rec:
                    with st.spinner(" gathering intel..."):
                        rec["image_data"] = fetch_anime_data(rec['title'])
                
                data = rec["image_data"]
                title = sanitize_html(rec['title'])
                desc = sanitize_html(rec['desc'])
                
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="anime-card-wrapper">
                        <div class="anime-card">
                            <div class="card-image">
                                <img src="{data['image_url']}" loading="lazy">
                                <div class="score-tag">{data['score']}</div>
                            </div>
                            <div class="card-content">
                                <div>
                                    <div class="card-title" title="{title}">{title}</div>
                                    <div style="color: #00AAFF; font-size: 0.8rem; margin-bottom: 5px;">
                                        {data['year']} • {', '.join(data['genres'])}
                                    </div>
                                    <div class="card-desc">{desc}</div>
                                </div>
                                <div style="margin-top: 10px; display: flex; gap: 5px;">
                                    <a href="{data['url']}" target="_blank" style="flex: 1; text-align: center; background: #333; color: white; padding: 5px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">MAL</a>
                                    <a href="https://www.crunchyroll.com/search?q={quote(title)}" target="_blank" style="flex: 1; text-align: center; background: #FF6600; color: black; padding: 5px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">WATCH</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# INPUT
if prompt := st.chat_input("Enter mission details..."):
    # Add to history if new
    if prompt not in st.session_state.user_stats["history"]:
        st.session_state.user_stats["history"].append(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# LOGIC & RESPONSE GENERATION
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_prompt = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        if pipeline:
            try:
                with st.spinner("🌀 Channeling Chakra..."):
                    creative_prompt = (
                        f"{user_prompt}\n\n"
                        "IMPORTANT: Act like an enthusiastic anime expert."
                        "List EXACTLY 3 anime recommendations. Do not list more."
                        "Use this STRICT format for every single recommendation:\n"
                        "Japanese Title: [Insert Japanese Name] Title: [Insert English Name] Plot Summary: [Description] Why it matches: [Reason]"
                    )
                    
                    response_text = pipeline.recommend(creative_prompt)
                
                # FIXED REGEX
                regex_pattern = r'Japanese Title:\s*(.+?)\s*Title:'
                matches = re.findall(regex_pattern, response_text, re.DOTALL | re.IGNORECASE)
                
                desc_pattern = r'Plot Summary:\s*(.+?)(?:\s+Why it matches:|$)'
                desc_matches = re.findall(desc_pattern, response_text, re.DOTALL | re.IGNORECASE)

                is_chat = any(x in response_text.lower() for x in ['hello', 'hi', 'help'])
                
                if matches and not is_chat:
                    recs = []
                    for i, jap_title in enumerate(matches):
                        if i < len(desc_matches):
                            clean_title = jap_title.strip()
                            clean_desc = desc_matches[i].strip()
                            recs.append({"title": clean_title, "desc": clean_desc})
                            
                            st.session_state.user_stats["count"] += 1
                            st.session_state.user_stats["genres"]["Action"] = st.session_state.user_stats["genres"].get("Action", 0) + 1
                    
                    st.session_state.messages.append({"role": "assistant", "content": "", "recommendations": recs})
                    st.rerun()
                else:
                    # Fallback
                    fallback_pattern = r'Title:\s*([^\n]+?)\s+Plot Summary:\s*([^\n]+?)(?:\s+Why it matches:|$)'
                    matches_fallback = re.findall(fallback_pattern, response_text, re.DOTALL)
                    
                    if matches_fallback and not is_chat:
                        recs = []
                        for title, desc in matches_fallback:
                            recs.append({"title": title.strip(), "desc": desc.strip()})
                        st.session_state.messages.append({"role": "assistant", "content": "", "recommendations": recs})
                        st.rerun()
                    else:
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                st.error(f"Mission Failed: {e}")
        else:
            st.error("Pipeline Disconnected.")