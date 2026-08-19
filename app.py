import streamlit as st
import importlib
import utils
importlib.reload(utils)
import os
import html

# Page Configuration
st.set_page_config(
    page_title="PyTune - Your Personal Music Streamer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Apply font globally */
html, body, [class*="css"], .stApp {
    font-family: 'Poppins', sans-serif !important;
    background-color: #090a0f !important;
}

/* Main background glow effect */
.stApp {
    background: radial-gradient(circle at 80% 20%, #1e113a 0%, #090a0f 70%) !important;
    color: #f0f1f5 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #090a0f;
}
::-webkit-scrollbar-thumb {
    background: #7c4dff;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #00e5ff;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #050608 !important;
    border-right: 1px solid #1a1c24 !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #00e5ff !important;
    font-size: 1.25rem !important;
    border-bottom: 1px solid #1a1c24;
    padding-bottom: 8px;
    margin-top: 1.5rem;
}

/* Cards (st.container with border) styling */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #0e1017 !important;
    border: 1px solid #1f2330 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #7c4dff !important;
    box-shadow: 0 8px 24px rgba(124, 77, 255, 0.25) !important;
    transform: translateY(-4px);
}

/* Song card images styling */
div[data-testid="stVerticalBlockBorderWrapper"] img {
    border-radius: 8px !important;
}

/* Button Custom Styling */
/* Play button (Primary) */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c4dff 0%, #00e5ff 100%) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(124, 77, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(0, 229, 255, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* Other buttons (Secondary) */
div.stButton > button[kind="secondary"] {
    background-color: #161821 !important;
    color: #e2e8f0 !important;
    border: 1px solid #2a2d3d !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #00e5ff !important;
    color: #00e5ff !important;
    background-color: #1a1d29 !important;
}

/* Input Search bar */
div[data-testid="stTextInput"] input {
    background-color: #0e1017 !important;
    color: #ffffff !important;
    border: 1px solid #1f2330 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important;
}

/* Branding header styling */
.brand-title {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.brand-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Sidebar Logo & Branding */
.sidebar-brand {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Quick play list items */
.song-list-item {
    padding: 8px;
    border-radius: 8px;
    background-color: #0f1015;
    border: 1px solid #1a1c24;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.song-list-item:hover {
    background-color: #171822;
    border-color: #7c4dff;
}

/* Floating player info */
.player-container {
    background-color: #0b0d16 !important;
    border: 1px solid #7c4dff !important;
    box-shadow: 0 0 20px rgba(124, 77, 255, 0.2) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper function to play a song
def play_song(song, playlist=None, index=0):
    if playlist:
        st.session_state.playlist = playlist
        st.session_state.playlist_index = index
    else:
        st.session_state.playlist = [song]
        st.session_state.playlist_index = 0
        
    with st.spinner("Extracting audio stream..."):
        audio_url = utils.get_audio_stream_url(song['url'])
        if audio_url:
            st.session_state.current_song = song
            st.session_state.current_audio_url = audio_url
            utils.add_to_history(song)
            st.rerun()
        else:
            st.error("Could not extract audio stream. Please try another song.")

# Helper function to toggle favorite status
def toggle_fav_song(song):
    is_now_fav = utils.toggle_favorite(song)
    if is_now_fav:
        st.toast(f"❤️ Added to Favorites: {song['title'][:30]}...")
    else:
        st.toast(f"💔 Removed from Favorites: {song['title'][:30]}...")
    st.rerun()

# Initialize Session State
if 'current_song' not in st.session_state:
    st.session_state.current_song = None

if 'current_audio_url' not in st.session_state:
    st.session_state.current_audio_url = None

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'search_input_val' not in st.session_state:
    st.session_state.search_input_val = ""

if 'playlist' not in st.session_state:
    st.session_state.playlist = []

if 'playlist_index' not in st.session_state:
    st.session_state.playlist_index = 0

# Load persistent favorites, history, and searches
local_data = utils.load_data()
favorites = local_data.get('favorites', [])
history = local_data.get('history', [])
recent_searches = local_data.get('searches', [])

# Autoplay query param handler
if "play_index" in st.query_params:
    try:
        new_idx = int(st.query_params["play_index"])
        del st.query_params["play_index"] # Clear immediately to avoid loop
        
        if 'playlist' in st.session_state and 0 <= new_idx < len(st.session_state.playlist):
            st.session_state.playlist_index = new_idx
            next_song = st.session_state.playlist[new_idx]
            
            with st.spinner("Loading next song..."):
                audio_url = utils.get_audio_stream_url(next_song['url'])
                if audio_url:
                    st.session_state.current_song = next_song
                    st.session_state.current_audio_url = audio_url
                    utils.add_to_history(next_song)
                    st.rerun()
                else:
                    st.toast("⚠️ Could not load next song in playlist.")
    except Exception as e:
        print(f"Error in autoplay handler: {e}")

# SIDEBAR: Favorites and History
with st.sidebar:
    st.markdown('<p class="sidebar-brand">PyTune 🎵</p>', unsafe_allow_html=True)
    
    # Favorites Section
    st.markdown("## ❤️ Favorites")
    if not favorites:
        st.caption("No favorites added yet. Search and click ❤️ to add.")
    else:
        for f_idx, fav in enumerate(favorites):
            # Let's create a row with two columns: Clickable song name and delete button
            col_name, col_btn = st.columns([4, 1])
            with col_name:
                # Custom HTML look for item
                safe_title = fav['title'][:25] + "..." if len(fav['title']) > 25 else fav['title']
                if st.button(f"🎵 {safe_title}", key=f"fav_play_{fav['id']}_{f_idx}", use_container_width=True, type="secondary"):
                    play_song(fav, playlist=favorites, index=f_idx)
            with col_btn:
                if st.button("❌", key=f"fav_del_{fav['id']}_{f_idx}", help="Remove from favorites"):
                    utils.toggle_favorite(fav)
                    st.toast(f"💔 Removed: {fav['title'][:20]}...")
                    st.rerun()

    # History Section
    st.markdown("## 🕒 Recently Played")
    if not history:
        st.caption("No songs played yet. Go play some music!")
    else:
        for idx, hist in enumerate(history[:10]):  # Show top 10 recent
            safe_title = hist['title'][:28] + "..." if len(hist['title']) > 28 else hist['title']
            if st.button(f"⏱️ {safe_title}", key=f"hist_play_{hist['id']}_{idx}", use_container_width=True, type="secondary"):
                play_song(hist, playlist=history, index=idx)
                
        # Clear History button
        st.write("")
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            data = utils.load_data()
            data['history'] = []
            utils.save_data(data)
            st.toast("History cleared!")
            st.rerun()

    # Recent Searches Section
    st.markdown("## 🔎 Recent Searches")
    if not recent_searches:
        st.caption("No recent searches yet.")
    else:
        for s_idx, search_item in enumerate(recent_searches):
            if st.button(f"🔎 {search_item}", key=f"recent_search_{s_idx}_{search_item}", use_container_width=True, type="secondary"):
                st.session_state.search_input_val = search_item
                with st.spinner(f"Searching for '{search_item}'..."):
                    results = utils.search_youtube(search_item)
                    st.session_state.search_results = results
                    utils.add_recent_search(search_item)
                st.rerun()


# MAIN CONTENT AREA
st.markdown('<p class="brand-title">PyTune</p>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">Stream and play your favorite songs on your local laptop</p>', unsafe_allow_html=True)

# 1. NOW PLAYING COMPONENT (Placed at the top when active)
if st.session_state.current_song and st.session_state.get('current_audio_url'):
    song = st.session_state.current_song
    audio_url = st.session_state.current_audio_url
    
    with st.container(border=True):
        col_thumb, col_info = st.columns([1, 3])
        
        with col_thumb:
            st.image(song['thumbnail'], use_container_width=True)
            
        with col_info:
            st.markdown("### 🎵 Now Playing (Audio Only)")
            st.markdown(f"**Title:** {song['title']}")
            st.markdown(f"**Channel:** {song['channel']} | **Duration:** {song['duration']}")
            
            # Action buttons
            is_fav = utils.is_favorite(song['id'])
            fav_label = "💔 Remove" if is_fav else "❤️ Favorite"
            
            # Reset download state if we change song
            if st.session_state.get('download_song_id') != song['id']:
                st.session_state.download_ready = False
                st.session_state.download_failed = False
                st.session_state.download_bytes = None
                st.session_state.download_filename = ""
                st.session_state.download_song_id = song['id']
                
            col_actions_1, col_actions_2, col_actions_3 = st.columns([1, 1, 1])
            with col_actions_1:
                if st.button(fav_label, key="player_fav_btn", type="primary" if not is_fav else "secondary"):
                    toggle_fav_song(song)
            with col_actions_2:
                if st.session_state.get('download_ready'):
                    # Native Streamlit browser download button
                    st.download_button(
                        label="⬇️ Save MP3",
                        data=st.session_state.download_bytes,
                        file_name=st.session_state.download_filename,
                        mime="audio/mp3",
                        type="primary",
                        use_container_width=True,
                        key="browser_dl_btn"
                    )
                elif st.session_state.get('download_failed'):
                    st.link_button(
                        label="🔗 Open MP3 Link",
                        url=audio_url,
                        type="primary",
                        use_container_width=True,
                        help="Right-click on the page and choose 'Save Audio As...'"
                    )
                    st.caption("💡 Right-click and select 'Save audio as...' to download.")
                else:
                    if st.button("📥 Download", key="player_dl_btn", type="secondary", help="Prepare song for download"):
                        with st.spinner("Preparing..."):
                            data, filename = utils.get_audio_bytes_via_ytdl(song['url'])
                            if data:
                                st.session_state.download_bytes = data
                                st.session_state.download_filename = filename
                                st.session_state.download_ready = True
                                st.session_state.download_failed = False
                                st.toast("✅ Download ready! Click Save below.")
                                st.rerun()
                            else:
                                st.session_state.download_failed = True
                                st.toast("⚠️ Cloud block detected. Use fallback link.")
                                st.rerun()
            with col_actions_3:
                if st.button("❌ Close", key="player_close_btn", type="secondary"):
                    st.session_state.current_song = None
                    st.session_state.current_audio_url = None
                    st.session_state.download_ready = False
                    st.session_state.download_failed = False
                    st.session_state.download_bytes = None
                    st.session_state.download_filename = ""
                    st.rerun()
                    
        # Custom HTML player that triggers parent window to load the next song in playlist when audio finishes
        st.write("")
        current_idx = st.session_state.get('playlist_index', 0)
        playlist = st.session_state.get('playlist', [])
        next_idx = current_idx + 1
        
        has_next = next_idx < len(playlist)
        
        if has_next:
            player_html = f"""
            <audio id="audio-player" src="{html.escape(audio_url)}" controls autoplay style="width: 100%;"></audio>
            <script>
                var audio = document.getElementById("audio-player");
                audio.onended = function() {{
                    console.log("Audio ended. Navigating parent to play_index={next_idx}...");
                    try {{
                        var parentUrl = new URL(window.parent.location.href);
                        parentUrl.searchParams.set("play_index", "{next_idx}");
                        window.parent.location.href = parentUrl.href;
                    }} catch(e) {{
                        console.error("Error modifying parent location:", e);
                    }}
                }};
            </script>
            """
            st.components.v1.html(player_html, height=60)
        else:
            st.audio(audio_url, format="audio/mp3", autoplay=True)

# 2. SEARCH SYSTEM
col_search, col_btn = st.columns([5, 1])

# Check for updates from suggestion clicks
search_query = col_search.text_input(
    label="Search for a song, artist or playlist",
    value=st.session_state.search_input_val,
    placeholder="Type song name and press Enter...",
    label_visibility="collapsed"
)

# Search button click
search_clicked = col_btn.button("🔍 Search", type="primary", use_container_width=True)

# If search query changed, or search clicked
if search_clicked or (search_query and search_query != st.session_state.search_input_val):
    st.session_state.search_input_val = search_query
    
    if search_query.strip():
        with st.spinner("Searching online platforms... Please wait."):
            results = utils.search_youtube(search_query)
            if results:
                st.session_state.search_results = results
                utils.add_recent_search(search_query)
            else:
                st.session_state.search_results = []
                st.warning("No songs found. Please check spelling or try another term.")
    else:
        st.session_state.search_results = []

# Search Tips and Helper Box
with st.expander("💡 Song Searching Help & Tips", expanded=False):
    st.markdown("""
    * **Use Artist Name:** Search with the artist's name for best results (e.g., `Arijit Singh Kesariya`).
    * **Autoplay Playlist:** When you play a song, the player will **automatically play the next song** from the search results or favorites list!
    * **Specific Version:** Add terms like `Lyrical` or `Official Audio` for studio versions.
    * **Indian Idol & Live Shows:** Include the show name for live performances (e.g., `Indian Idol Udit Main Yahan Hoon`).
    """)

# QUICK RECOMMENDATIONS (Show when there are no search results or search query is empty)
if not st.session_state.search_input_val:
    st.markdown("### 🔥 Popular Searches")
    suggestions = ["Lofi Hip Hop beats", "Bollywood Romantic Hits 2026", "Arijit Singh playlist", "Chill Acoustic guitar", "Synthwave 80s", "Top English Pop Hits"]
    
    cols = st.columns(3)
    for index, suggestion in enumerate(suggestions):
        col_idx = index % 3
        with cols[col_idx]:
            if st.button(f"🎵 {suggestion}", key=f"sugg_{index}", use_container_width=True):
                st.session_state.search_input_val = suggestion
                with st.spinner(f"Searching for '{suggestion}'..."):
                    results = utils.search_youtube(suggestion)
                    st.session_state.search_results = results
                st.rerun()

# 3. DISPLAY SEARCH RESULTS
if st.session_state.search_results:
    st.markdown(f"### 🔍 Results for '{st.session_state.search_input_val}'")
    
    # Grid Layout: 3 columns
    results_list = st.session_state.search_results
    num_cols = 3
    
    for i in range(0, len(results_list), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            if i + j < len(results_list):
                song = results_list[i + j]
                with cols[j]:
                    with st.container(border=True):
                        # Song Thumbnail
                        st.image(song['thumbnail'], use_container_width=True)
                        
                        # Title truncated
                        disp_title = song['title']
                        if len(disp_title) > 55:
                            disp_title = disp_title[:52] + "..."
                            
                        st.markdown(f"##### **{disp_title}**")
                        st.caption(f"👤 {song['channel']}")
                        st.caption(f"⏱️ Duration: {song['duration']} | {song['views']}")
                        
                        # Card action buttons
                        col_card_play, col_card_fav = st.columns([2, 1])
                        with col_card_play:
                            if st.button("▶️ Play", key=f"play_card_{song['id']}", type="primary", use_container_width=True):
                                play_song(song, playlist=results_list, index=i+j)
                        with col_card_fav:
                            is_fav = utils.is_favorite(song['id'])
                            heart_icon = "❤️" if is_fav else "🤍"
                            if st.button(heart_icon, key=f"fav_card_{song['id']}", type="secondary", use_container_width=True, help="Toggle Favorite"):
                                toggle_fav_song(song)
