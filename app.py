import streamlit as st
import importlib
import utils
importlib.reload(utils)
import os
import html

# Page Configuration
st.set_page_config(
    page_title="PyTune - Spotify Music",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Spotify Signature Dark Theme Styling
SPOTIFY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

/* Apply font globally */
html, body, [class*="css"], .stApp {
    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #121212 !important;
    color: #ffffff !important;
}

.stApp {
    background-color: #121212 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #121212;
}
::-webkit-scrollbar-thumb {
    background: #535353;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #b3b3b3;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
    border-right: 1px solid #181818 !important;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2, 
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #b3b3b3 !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
}

/* Spotify Card Container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #181818 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    transition: all 0.3s cubic-bezier(0.3, 0, 0, 1) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    background-color: #282828 !important;
    border-color: #383838 !important;
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] img {
    border-radius: 6px !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4) !important;
}

/* Primary Button - Spotify Green */
div.stButton > button[kind="primary"] {
    background-color: #1DB954 !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 500px !important;
    padding: 8px 20px !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3) !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #1ed760 !important;
    transform: scale(1.04) !important;
    box-shadow: 0 6px 20px rgba(29, 185, 84, 0.5) !important;
    color: #000000 !important;
}

/* Secondary Button - Dark Glass */
div.stButton > button[kind="secondary"] {
    background-color: #242424 !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
    border-radius: 500px !important;
    padding: 6px 16px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #ffffff !important;
    background-color: #2a2a2a !important;
    color: #1DB954 !important;
    transform: scale(1.02);
}

/* Input Search bar */
div[data-testid="stTextInput"] input {
    background-color: #242424 !important;
    color: #ffffff !important;
    border: 1px solid #383838 !important;
    border-radius: 500px !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #1DB954 !important;
    box-shadow: 0 0 12px rgba(29, 185, 84, 0.3) !important;
}

/* Logo & Headers */
.spotify-logo {
    font-size: 1.8rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-bottom: 1rem;
}
.spotify-logo span {
    color: #1DB954;
}

.spotify-hero {
    background: linear-gradient(180deg, #450af5 0%, #121212 100%);
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.spotify-hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    margin: 0;
    color: #ffffff;
}
.spotify-hero-sub {
    color: #e0e0e0;
    font-size: 1.1rem;
    font-weight: 500;
    margin-top: 0.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    color: #ffffff;
}

/* Pill buttons for categories */
.genre-pill {
    background-color: #2a2a2a;
    color: #fff;
    padding: 8px 18px;
    border-radius: 500px;
    font-size: 0.85rem;
    font-weight: 700;
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.genre-pill:hover {
    background-color: #1DB954;
    color: #000;
}
</style>
"""
st.markdown(SPOTIFY_CSS, unsafe_allow_html=True)

# Helper function to play a song
def play_song(song, playlist=None, index=0):
    if playlist:
        st.session_state.playlist = playlist
        st.session_state.playlist_index = index
    else:
        st.session_state.playlist = [song]
        st.session_state.playlist_index = 0
        
    st.session_state.current_song = song
    utils.add_to_history(song)
    st.rerun()

# Helper function to toggle favorite status
def toggle_fav_song(song):
    is_now_fav = utils.toggle_favorite(song)
    if is_now_fav:
        st.toast(f"❤️ Added to Liked Songs: {song['title'][:30]}...")
    else:
        st.toast(f"💔 Removed from Liked Songs: {song['title'][:30]}...")
    st.rerun()

# Initialize Session State
if 'current_song' not in st.session_state:
    st.session_state.current_song = None

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'search_input_val' not in st.session_state:
    st.session_state.search_input_val = ""

if 'playlist' not in st.session_state:
    st.session_state.playlist = []

if 'playlist_index' not in st.session_state:
    st.session_state.playlist_index = 0

if 'active_nav' not in st.session_state:
    st.session_state.active_nav = "Home"

# Load persistent favorites, history, playlists, and searches
local_data = utils.load_data()
favorites = local_data.get('favorites', [])
history = local_data.get('history', [])
recent_searches = local_data.get('searches', [])
user_playlists = local_data.get('playlists', {})

# Autoplay query param handler
if "play_index" in st.query_params:
    try:
        new_idx = int(st.query_params["play_index"])
        del st.query_params["play_index"] # Clear immediately
        
        if 'playlist' in st.session_state and 0 <= new_idx < len(st.session_state.playlist):
            st.session_state.playlist_index = new_idx
            next_song = st.session_state.playlist[new_idx]
            st.session_state.current_song = next_song
            utils.add_to_history(next_song)
            st.rerun()
    except Exception as e:
        print(f"Error in autoplay handler: {e}")

# SIDEBAR: Spotify Navigation
with st.sidebar:
    st.markdown('<p class="spotify-logo">🟢 <span>PyTune</span></p>', unsafe_allow_html=True)
    
    # Navigation Menu
    nav_choice = st.radio(
        label="Navigation",
        options=["🏠 Home", "🔍 Search", "📚 Your Library", "❤️ Liked Songs"],
        index=["🏠 Home", "🔍 Search", "📚 Your Library", "❤️ Liked Songs"].index(
            f"🏠 Home" if st.session_state.active_nav == "Home" else
            f"🔍 Search" if st.session_state.active_nav == "Search" else
            f"📚 Your Library" if st.session_state.active_nav == "Library" else
            f"❤️ Liked Songs"
        ),
        label_visibility="collapsed"
    )
    
    # Update active nav state
    if nav_choice == "🏠 Home":
        st.session_state.active_nav = "Home"
    elif nav_choice == "🔍 Search":
        st.session_state.active_nav = "Search"
    elif nav_choice == "📚 Your Library":
        st.session_state.active_nav = "Library"
    elif nav_choice == "❤️ Liked Songs":
        st.session_state.active_nav = "Liked Songs"

    st.markdown("---")

    # Custom Playlists Section
    st.markdown("### 📁 Custom Playlists")
    
    # Create Playlist Input
    with st.expander("➕ Create New Playlist", expanded=False):
        new_pl_name = st.text_input("Playlist Name", key="new_playlist_input", placeholder="My Cool Mix...")
        if st.button("Create", key="btn_create_pl", type="primary", use_container_width=True):
            if new_pl_name.strip():
                created = utils.create_playlist(new_pl_name)
                if created:
                    st.toast(f"✅ Created Playlist '{new_pl_name}'!")
                    st.session_state.active_nav = f"Playlist:{new_pl_name}"
                    st.rerun()
                else:
                    st.toast("⚠️ Playlist already exists.")

    if not user_playlists:
        st.caption("No custom playlists yet.")
    else:
        for pl_name in list(user_playlists.keys()):
            song_cnt = len(user_playlists[pl_name])
            if st.button(f"🎶 {pl_name} ({song_cnt})", key=f"pl_nav_{pl_name}", use_container_width=True, type="secondary"):
                st.session_state.active_nav = f"Playlist:{pl_name}"
                st.rerun()

    # Recent Searches Section
    st.markdown("### 🔎 Recent Searches")
    if recent_searches:
        for s_idx, search_item in enumerate(recent_searches):
            if st.button(f"⏱️ {search_item}", key=f"sidebar_search_{s_idx}_{search_item}", use_container_width=True, type="secondary"):
                st.session_state.search_input_val = search_item
                st.session_state.active_nav = "Search"
                with st.spinner(f"Searching for '{search_item}'..."):
                    results = utils.search_youtube(search_item)
                    st.session_state.search_results = results
                    utils.add_recent_search(search_item)
                st.rerun()


# MAIN CONTENT AREA

# 1. PROMINENT HEADER SEARCH BAR (Always accessible at top)
col_top_search, col_top_btn = st.columns([5, 1])
top_query = col_top_search.text_input(
    label="Header Search Bar",
    value=st.session_state.search_input_val if st.session_state.active_nav == "Search" else "",
    placeholder="🔍 Search for songs, artists, playlists, genres...",
    key="header_top_search_input",
    label_visibility="collapsed"
)
top_btn_clicked = col_top_btn.button("🔍 Search", key="btn_top_search", type="primary", use_container_width=True)

if top_btn_clicked or (top_query and top_query != st.session_state.search_input_val and st.session_state.active_nav != "Search"):
    if top_query.strip():
        st.session_state.search_input_val = top_query
        st.session_state.active_nav = "Search"
        with st.spinner(f"Searching for '{top_query}'..."):
            results = utils.search_youtube(top_query)
            st.session_state.search_results = results
            utils.add_recent_search(top_query)
        st.rerun()

st.write("")

# 2. AUDIO-ONLY MP3 PLAYER COMPONENT (Top Sticky Container when Active)
if st.session_state.current_song:
    song = st.session_state.current_song
    video_id = song['id']
    
    with st.container(border=True):
        col_thumb, col_info, col_controls = st.columns([1, 2.5, 1.5])
        
        with col_thumb:
            st.image(song['thumbnail'], use_container_width=True)
            
        with col_info:
            st.markdown('<span style="background-color: #1DB954; color: #000; font-weight: 700; padding: 4px 12px; border-radius: 500px; font-size: 0.75rem;">🎧 PLAYING MP3 AUDIO</span>', unsafe_allow_html=True)
            st.markdown(f"### **{song['title']}**")
            st.markdown(f"👤 **{song['channel']}** | ⏱️ {song['duration']} | 👀 {song.get('views', '')}")
            
        with col_controls:
            is_fav = utils.is_favorite(song['id'])
            fav_label = "💔 Liked" if is_fav else "❤️ Like"
            
            if st.session_state.get('download_song_id') != song['id']:
                st.session_state.download_ready = False
                st.session_state.download_failed = False
                st.session_state.download_bytes = None
                st.session_state.download_filename = ""
                st.session_state.download_song_id = song['id']
                
            if st.button(fav_label, key="player_fav_btn", type="primary" if not is_fav else "secondary", use_container_width=True):
                toggle_fav_song(song)
                
            if st.session_state.get('download_ready'):
                st.download_button(
                    label="⬇️ Save MP3 File",
                    data=st.session_state.download_bytes,
                    file_name=st.session_state.download_filename,
                    mime="audio/mp3",
                    type="primary",
                    use_container_width=True,
                    key="browser_dl_btn"
                )
            else:
                if st.button("📥 Download MP3", key="player_dl_btn", type="secondary", use_container_width=True, help="Download track as MP3 file"):
                    with st.spinner("Preparing MP3..."):
                        data, filename = utils.get_audio_bytes_via_ytdl(song['url'])
                        if data:
                            st.session_state.download_bytes = data
                            st.session_state.download_filename = filename
                            st.session_state.download_ready = True
                            st.session_state.download_failed = False
                            st.toast("✅ MP3 ready! Click Save MP3 File below.")
                            st.rerun()
                        else:
                            st.session_state.download_failed = True
                            st.toast("⚠️ Download failed. Please try another song.")
                            st.rerun()
                            
            if st.button("❌ Stop & Close", key="player_close_btn", type="secondary", use_container_width=True):
                st.session_state.current_song = None
                st.session_state.download_ready = False
                st.session_state.download_failed = False
                st.session_state.download_bytes = None
                st.session_state.download_filename = ""
                st.rerun()

        # Hidden background audio engine (no video iframe box visible on UI)
        current_idx = st.session_state.get('playlist_index', 0)
        playlist = st.session_state.get('playlist', [])
        next_idx = current_idx + 1
        has_next = next_idx < len(playlist)
        
        audio_engine_html = f"""
        <div style="position: absolute; left: -9999px; top: -9999px; width: 1px; height: 1px; opacity: 0; pointer-events: none; overflow: hidden;">
            <div id="yt-player"></div>
        </div>
        <script>
            var tag = document.createElement('script');
            tag.src = "https://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

            var player;
            function onYouTubeIframeAPIReady() {{
                player = new YT.Player('yt-player', {{
                    height: '1',
                    width: '1',
                    videoId: '{video_id}',
                    playerVars: {{
                        'autoplay': 1,
                        'playsinline': 1,
                        'controls': 0
                    }},
                    events: {{
                        'onStateChange': onPlayerStateChange
                    }}
                }});
            }}

            function onPlayerStateChange(event) {{
                if (event.data === 0 && {str(has_next).lower()}) {{
                    try {{
                        var parentUrl = new URL(window.parent.location.href);
                        parentUrl.searchParams.set("play_index", "{next_idx}");
                        window.parent.location.href = parentUrl.href;
                    }} catch(e) {{
                        console.error("Autoplay error:", e);
                    }}
                }}
            }}
        </script>
        """
        st.components.v1.html(audio_engine_html, height=1)

# ROUTE 1: HOME VIEW
if st.session_state.active_nav == "Home":
    st.markdown("""
    <div class="spotify-hero">
        <p class="spotify-hero-title">Welcome to PyTune</p>
        <p class="spotify-hero-sub">Stream millions of MP3 songs and podcasts on your local machine with Spotify UI.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-title">🔥 Popular Quick Mixes</p>', unsafe_allow_html=True)
    
    quick_suggestions = [
        "Bollywood Romantic Hits", "Lofi Hip Hop Beats", "Arijit Singh Favorites",
        "Chill Acoustic Guitar", "Synthwave 80s Retro", "Top English Pop Hits"
    ]
    
    cols = st.columns(3)
    for index, sugg in enumerate(quick_suggestions):
        col_idx = index % 3
        with cols[col_idx]:
            if st.button(f"🎵 {sugg}", key=f"home_quick_{index}", use_container_width=True, type="secondary"):
                st.session_state.search_input_val = sugg
                st.session_state.active_nav = "Search"
                with st.spinner(f"Loading '{sugg}'..."):
                    results = utils.search_youtube(sugg)
                    st.session_state.search_results = results
                st.rerun()

    # Recently Played section if history exists
    if history:
        st.markdown('<p class="section-title">🕒 Recently Played</p>', unsafe_allow_html=True)
        h_cols = st.columns(4)
        for h_idx, h_song in enumerate(history[:4]):
            with h_cols[h_idx]:
                with st.container(border=True):
                    st.image(h_song['thumbnail'], use_container_width=True)
                    disp_t = h_song['title'][:35] + "..." if len(h_song['title']) > 35 else h_song['title']
                    st.markdown(f"**{disp_t}**")
                    st.caption(f"👤 {h_song['channel']}")
                    if st.button("▶️ Play MP3", key=f"home_hist_play_{h_song['id']}_{h_idx}", type="primary", use_container_width=True):
                        play_song(h_song, playlist=history, index=h_idx)

# ROUTE 2: SEARCH VIEW
elif st.session_state.active_nav == "Search":
    st.markdown('<p class="section-title">🔍 Search Music</p>', unsafe_allow_html=True)
    
    # Genre & Quick Filter Pills
    st.markdown("### Browse Categories")
    genres = ["All", "Bollywood", "Lofi Beats", "Acoustic", "Marathi", "Pop Hits", "Indian Idol", "Synthwave"]
    g_cols = st.columns(len(genres))
    for g_idx, g_name in enumerate(genres):
        with g_cols[g_idx]:
            if st.button(g_name, key=f"genre_btn_{g_idx}", use_container_width=True, type="secondary"):
                if g_name != "All":
                    st.session_state.search_input_val = g_name
                    with st.spinner(f"Loading category '{g_name}'..."):
                        results = utils.search_youtube(g_name)
                        st.session_state.search_results = results
                    st.rerun()

    # Display Search Results in 4-Column Grid
    if st.session_state.search_results:
        st.markdown(f"### Results for '{st.session_state.search_input_val}'")
        results_list = st.session_state.search_results
        num_cols = 4
        
        for i in range(0, len(results_list), num_cols):
            cols = st.columns(num_cols)
            for j in range(num_cols):
                if i + j < len(results_list):
                    song_item = results_list[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.image(song_item['thumbnail'], use_container_width=True)
                            disp_title = song_item['title'][:45] + "..." if len(song_item['title']) > 45 else song_item['title']
                            st.markdown(f"##### **{disp_title}**")
                            st.caption(f"👤 {song_item['channel']} | ⏱️ {song_item['duration']}")
                            
                            col_p, col_f = st.columns([3, 1])
                            with col_p:
                                if st.button("▶️ Play MP3", key=f"search_play_{song_item['id']}_{i+j}", type="primary", use_container_width=True):
                                    play_song(song_item, playlist=results_list, index=i+j)
                            with col_f:
                                is_fav = utils.is_favorite(song_item['id'])
                                icon = "❤️" if is_fav else "🤍"
                                if st.button(icon, key=f"search_fav_{song_item['id']}_{i+j}", type="secondary", use_container_width=True):
                                    toggle_fav_song(song_item)
                                    
                            # Add to playlist drop menu
                            if user_playlists:
                                with st.popover("➕ Add to Playlist", use_container_width=True):
                                    for plk in user_playlists.keys():
                                        if st.button(f"➕ {plk}", key=f"add_pl_{plk}_{song_item['id']}_{i+j}"):
                                            utils.add_to_playlist(plk, song_item)
                                            st.toast(f"Added to '{plk}'!")

# ROUTE 3: YOUR LIBRARY VIEW
elif st.session_state.active_nav == "Library":
    st.markdown('<p class="section-title">📚 Your Library</p>', unsafe_allow_html=True)
    
    lib_tab1, lib_tab2 = st.tabs(["📜 Listening History", "📁 Custom Playlists"])
    
    with lib_tab1:
        if not history:
            st.info("No songs played yet. Explore and play music!")
        else:
            col_clear, _ = st.columns([1, 4])
            with col_clear:
                if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
                    data = utils.load_data()
                    data['history'] = []
                    utils.save_data(data)
                    st.toast("History cleared!")
                    st.rerun()
            
            st.write("")
            for h_idx, h_item in enumerate(history):
                c1, c2, c3, c4 = st.columns([1, 4, 2, 1])
                with c1:
                    st.image(h_item['thumbnail'], width=60)
                with c2:
                    st.markdown(f"**{h_item['title']}**")
                    st.caption(f"👤 {h_item['channel']}")
                with c3:
                    st.caption(f"⏱️ {h_item['duration']}")
                with c4:
                    if st.button("▶️ Play MP3", key=f"lib_hist_{h_item['id']}_{h_idx}", type="primary"):
                        play_song(h_item, playlist=history, index=h_idx)
                st.markdown("---")

    with lib_tab2:
        if not user_playlists:
            st.info("No custom playlists yet. Use the sidebar to create one!")
        else:
            for pl_name, pl_songs in user_playlists.items():
                with st.expander(f"📁 Playlist: {pl_name} ({len(pl_songs)} songs)", expanded=True):
                    c_p, c_d = st.columns([4, 1])
                    with c_p:
                        if pl_songs and st.button(f"▶️ Play All '{pl_name}'", key=f"play_all_pl_{pl_name}", type="primary"):
                            play_song(pl_songs[0], playlist=pl_songs, index=0)
                    with c_d:
                        if st.button("🗑️ Delete Playlist", key=f"del_pl_{pl_name}", type="secondary"):
                            utils.delete_playlist(pl_name)
                            st.toast(f"Deleted playlist '{pl_name}'")
                            st.rerun()
                            
                    st.write("")
                    if not pl_songs:
                        st.caption("This playlist is empty. Add songs from the Search tab!")
                    else:
                        for s_idx, s_item in enumerate(pl_songs):
                            sc1, sc2, sc3 = st.columns([4, 1, 1])
                            with sc1:
                                st.markdown(f"🎵 **{s_item['title']}** - *{s_item['channel']}*")
                            with sc2:
                                if st.button("▶️ Play MP3", key=f"pl_song_play_{pl_name}_{s_item['id']}_{s_idx}", type="primary"):
                                    play_song(s_item, playlist=pl_songs, index=s_idx)
                            with sc3:
                                if st.button("❌", key=f"pl_song_rem_{pl_name}_{s_item['id']}_{s_idx}"):
                                    utils.remove_from_playlist(pl_name, s_item['id'])
                                    st.toast("Removed from playlist!")
                                    st.rerun()

# ROUTE 4: LIKED SONGS VIEW
elif st.session_state.active_nav == "Liked Songs":
    st.markdown(f"""
    <div class="spotify-hero" style="background: linear-gradient(180deg, #5038a0 0%, #121212 100%);">
        <p class="spotify-hero-title">❤️ Liked Songs</p>
        <p class="spotify-hero-sub">{len(favorites)} saved tracks in your personal collection</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not favorites:
        st.info("You haven't liked any songs yet! Click ❤️ on any track to add it here.")
    else:
        if st.button("▶️ Play All Liked Songs", type="primary", key="play_all_liked"):
            play_song(favorites[0], playlist=favorites, index=0)
            
        st.write("")
        st.markdown("---")
        
        for f_idx, fav_item in enumerate(favorites):
            col_t, col_info, col_dur, col_play, col_del = st.columns([1, 5, 2, 1.5, 1])
            with col_t:
                st.image(fav_item['thumbnail'], width=55)
            with col_info:
                st.markdown(f"**{fav_item['title']}**")
                st.caption(f"👤 {fav_item['channel']}")
            with col_dur:
                st.caption(f"⏱️ {fav_item['duration']}")
            with col_play:
                if st.button("▶️ Play MP3", key=f"liked_play_{fav_item['id']}_{f_idx}", type="primary", use_container_width=True):
                    play_song(fav_item, playlist=favorites, index=f_idx)
            with col_del:
                if st.button("💔", key=f"liked_del_{fav_item['id']}_{f_idx}", help="Remove from Liked Songs"):
                    utils.toggle_favorite(fav_item)
                    st.toast(f"Removed: {fav_item['title'][:20]}...")
                    st.rerun()
            st.markdown("---")

# ROUTE 5: CUSTOM PLAYLIST VIEW (Direct Nav)
elif st.session_state.active_nav.startswith("Playlist:"):
    pl_name = st.session_state.active_nav.split("Playlist:")[1]
    pl_songs = user_playlists.get(pl_name, [])
    
    st.markdown(f"""
    <div class="spotify-hero" style="background: linear-gradient(180deg, #1e3264 0%, #121212 100%);">
        <p class="spotify-hero-title">📁 {pl_name}</p>
        <p class="spotify-hero-sub">{len(pl_songs)} songs in playlist</p>
    </div>
    """, unsafe_allow_html=True)
    
    if pl_songs:
        col_p, col_d = st.columns([3, 1])
        with col_p:
            if st.button(f"▶️ Play Playlist", type="primary", key="pl_view_play_all"):
                play_song(pl_songs[0], playlist=pl_songs, index=0)
        with col_d:
            if st.button("🗑️ Delete Playlist", type="secondary", key="pl_view_del"):
                utils.delete_playlist(pl_name)
                st.toast(f"Deleted playlist '{pl_name}'!")
                st.session_state.active_nav = "Library"
                st.rerun()
                
        st.write("")
        st.markdown("---")
        for s_idx, s_item in enumerate(pl_songs):
            col_t, col_info, col_dur, col_play, col_del = st.columns([1, 5, 2, 1.5, 1])
            with col_t:
                st.image(s_item['thumbnail'], width=55)
            with col_info:
                st.markdown(f"**{s_item['title']}**")
                st.caption(f"👤 {s_item['channel']}")
            with col_dur:
                st.caption(f"⏱️ {s_item['duration']}")
            with col_play:
                if st.button("▶️ Play MP3", key=f"pl_view_play_{s_item['id']}_{s_idx}", type="primary", use_container_width=True):
                    play_song(s_item, playlist=pl_songs, index=s_idx)
            with col_del:
                if st.button("❌", key=f"pl_view_rem_{s_item['id']}_{s_idx}", help="Remove song from playlist"):
                    utils.remove_from_playlist(pl_name, s_item['id'])
                    st.toast("Removed from playlist!")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("This playlist is currently empty. Go to the Search tab to add songs!")
