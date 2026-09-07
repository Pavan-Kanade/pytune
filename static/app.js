// Global Application State
let appData = { favorites: [], history: [], searches: [], playlists: {} };
let currentQueue = [];
let currentIndex = 0;
let currentSong = null;
let currentView = 'home';
let activePlaylistName = '';

// YouTube API & Playback State
let ytPlayer = null;
let isPlaying = false;
let isUserSeeking = false;

const genres = ["Bollywood", "Lofi Beats", "Acoustic", "Marathi", "Pop Hits", "Indian Idol", "Synthwave", "EDM Hits"];
const quickSuggestions = [
    "Bollywood Romantic Hits", "Lofi Hip Hop Beats", "Arijit Singh Favorites",
    "Chill Acoustic Guitar", "Synthwave 80s Retro", "Top English Pop Hits"
];

// Initialize Application on Page Load
document.addEventListener("DOMContentLoaded", async () => {
    await fetchAppData();
    renderGenres();
    renderQuickMixes();
    setupSeekSlider();
});

// Fetch All Persistent App Data from Backend REST API
async function fetchAppData() {
    try {
        const response = await fetch('/api/data');
        if (response.ok) {
            appData = await response.json();
            renderSidebarPlaylists();
            renderLikedSongs();
            renderHistory();
        }
    } catch (e) {
        console.error("Failed to fetch app data:", e);
    }
}

// YouTube IFrame API Initialization
function onYouTubeIframeAPIReady() {
    ytPlayer = new YT.Player('yt-audio-engine', {
        height: '1',
        width: '1',
        videoId: '',
        playerVars: {
            'autoplay': 1,
            'playsinline': 1,
            'controls': 0
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    // 300ms timer to update seek slider & timestamps
    setInterval(() => {
        if (ytPlayer && ytPlayer.getCurrentTime && !isUserSeeking && isPlaying) {
            const curr = ytPlayer.getCurrentTime();
            const dur = ytPlayer.getDuration();
            if (dur > 0) {
                const percent = (curr / dur) * 100;
                document.getElementById('seek-slider').value = percent;
                document.getElementById('time-current').innerText = formatTime(curr);
                document.getElementById('time-duration').innerText = formatTime(dur);
            }
        }
    }, 300);
}

function onPlayerStateChange(event) {
    // YT.PlayerState: 1 = PLAYING, 2 = PAUSED, 0 = ENDED
    if (event.data === 1) {
        isPlaying = true;
        document.getElementById('btn-player-playpause').innerText = "⏸️";
    } else if (event.data === 2) {
        isPlaying = false;
        document.getElementById('btn-player-playpause').innerText = "▶️";
    } else if (event.data === 0) {
        playNextTrack();
    }
}

// Track Playback Core Method
async function playSong(song, queue = null, index = 0) {
    currentSong = song;
    currentQueue = queue && queue.length ? queue : [song];
    currentIndex = index;

    // Record listening history in backend
    fetch('/api/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(song)
    }).then(() => fetchAppData());

    // Update Player Bar UI
    document.getElementById('player-bar').style.display = 'flex';
    document.getElementById('player-thumb').src = song.thumbnail;
    document.getElementById('player-title').innerText = song.title;
    document.getElementById('player-artist').innerText = song.channel;

    updatePlayerLikeButton();

    // Load and play track via YouTube API engine
    if (ytPlayer && ytPlayer.loadVideoById) {
        ytPlayer.loadVideoById(song.id);
    }
}

function playNextTrack() {
    if (currentQueue && currentIndex + 1 < currentQueue.length) {
        currentIndex++;
        playSong(currentQueue[currentIndex], currentQueue, currentIndex);
    }
}

function togglePlayPause() {
    if (!ytPlayer) return;
    if (isPlaying) {
        ytPlayer.pauseVideo();
    } else {
        ytPlayer.playVideo();
    }
}

function seekRewind(seconds = 10) {
    if (!ytPlayer || !ytPlayer.getCurrentTime) return;
    const curr = ytPlayer.getCurrentTime();
    ytPlayer.seekTo(Math.max(0, curr - seconds), true);
}

function seekForward(seconds = 10) {
    if (!ytPlayer || !ytPlayer.getCurrentTime) return;
    const curr = ytPlayer.getCurrentTime();
    const dur = ytPlayer.getDuration();
    ytPlayer.seekTo(Math.min(dur, curr + seconds), true);
}

function setupSeekSlider() {
    const slider = document.getElementById('seek-slider');
    slider.addEventListener('mousedown', () => { isUserSeeking = true; });
    slider.addEventListener('touchstart', () => { isUserSeeking = true; });
    slider.addEventListener('change', () => {
        if (ytPlayer && ytPlayer.getDuration) {
            const dur = ytPlayer.getDuration();
            if (dur > 0) {
                const targetSec = (slider.value / 100) * dur;
                ytPlayer.seekTo(targetSec, true);
            }
        }
        isUserSeeking = false;
    });
}

function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// Navigation & View Switching
function switchView(viewName, playlistName = '') {
    currentView = viewName;
    activePlaylistName = playlistName;

    // Update active nav styling
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const activeNav = document.getElementById(`nav-${viewName}`);
    if (activeNav) activeNav.classList.add('active');

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => sec.style.display = 'none');

    // Display target view
    const targetSection = document.getElementById(`view-${viewName}`);
    if (targetSection) targetSection.style.display = 'block';

    if (viewName === 'playlist' && playlistName) {
        renderPlaylistDetail(playlistName);
    }
}

// Execute Search from Top Bar or Category Pills
async function executeSearch(customQuery = null) {
    const query = customQuery || document.getElementById('top-search-input').value.trim();
    if (!query) return;

    switchView('search');
    document.getElementById('search-results-heading').innerText = `Results for "${query}"`;
    const grid = document.getElementById('search-results-grid');
    grid.innerHTML = '<div style="color: #1DB954; font-weight: 700;">Searching YouTube...</div>';

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const tracks = await response.json();
            renderCardsGrid(tracks, 'search-results-grid');
            await fetchAppData();
        } else {
            grid.innerHTML = '<div style="color: #ff5555;">No tracks found. Try another search.</div>';
        }
    } catch (e) {
        grid.innerHTML = '<div style="color: #ff5555;">Search error. Check network connection.</div>';
    }
}

function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
        executeSearch();
    }
}

// Render UI Components
function renderCardsGrid(tracks, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!tracks || tracks.length === 0) {
        container.innerHTML = '<div style="color: #b3b3b3;">No tracks available.</div>';
        return;
    }

    container.innerHTML = tracks.map((track, idx) => `
        <div class="track-card">
            <div class="card-img-wrapper" onclick='playSong(${JSON.stringify(track).replace(/'/g, "&apos;")}, ${JSON.stringify(tracks).replace(/'/g, "&apos;")}, ${idx})'>
                <img src="${track.thumbnail}" alt="${track.title}">
                <div class="play-badge">▶</div>
            </div>
            <div class="card-title">${escapeHtml(track.title)}</div>
            <div class="card-artist">👤 ${escapeHtml(track.channel)}</div>
            <div class="card-actions">
                <button class="btn-icon" onclick='toggleFavoriteTrack(${JSON.stringify(track).replace(/'/g, "&apos;")})' title="Like">
                    ${isLiked(track.id) ? '❤️' : '🤍'}
                </button>
                ${renderPlaylistDropdownHTML(track)}
            </div>
        </div>
    `).join('');
}

function renderQuickMixes() {
    const grid = document.getElementById('home-quick-grid');
    if (!grid) return;

    grid.innerHTML = quickSuggestions.map(sugg => `
        <div class="track-card" onclick="executeSearch('${sugg}')">
            <div class="card-title" style="color: #1DB954; font-size: 1.1rem;">🎵 ${sugg}</div>
            <div class="card-artist">Tap to load mix</div>
        </div>
    `).join('');
}

function renderSidebarPlaylists() {
    const ul = document.getElementById('sidebar-playlist-list');
    if (!ul) return;

    const playlists = appData.playlists || {};
    const keys = Object.keys(playlists);

    if (keys.length === 0) {
        ul.innerHTML = '<li class="playlist-item" style="color: #777;">No playlists</li>';
        return;
    }

    ul.innerHTML = keys.map(name => `
        <li class="playlist-item" onclick="switchView('playlist', '${escapeHtml(name)}')">
            📁 ${escapeHtml(name)} (${playlists[name].length})
        </li>
    `).join('');
}

function renderGenres() {
    const container = document.getElementById('genre-container');
    if (!container) return;

    container.innerHTML = genres.map(g => `
        <button class="genre-pill" onclick="executeSearch('${g}')">${g}</button>
    `).join('');
}

function renderLikedSongs() {
    const liked = appData.favorites || [];
    document.getElementById('liked-count-subtitle').innerText = `${liked.length} saved tracks in your collection`;

    const tbody = document.getElementById('liked-tbody');
    if (!tbody) return;

    if (liked.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="color: #777;">No liked songs yet. Click ❤️ on any track!</td></tr>';
        return;
    }

    tbody.innerHTML = liked.map((track, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td style="font-weight: 700; color: #fff;">${escapeHtml(track.title)}</td>
            <td style="color: #b3b3b3;">${escapeHtml(track.channel)}</td>
            <td style="color: #b3b3b3;">${track.duration}</td>
            <td>
                <button class="btn-search" style="padding: 4px 12px; font-size: 0.8rem;" onclick='playSong(${JSON.stringify(track).replace(/'/g, "&apos;")}, ${JSON.stringify(liked).replace(/'/g, "&apos;")}, ${idx})'>▶️ Play</button>
                <button class="btn-icon" onclick='toggleFavoriteTrack(${JSON.stringify(track).replace(/'/g, "&apos;")})'>💔</button>
            </td>
        </tr>
    `).join('');
}

function renderHistory() {
    const history = appData.history || [];
    renderCardsGrid(history.slice(0, 4), 'home-recent-grid');

    const tbody = document.getElementById('library-history-tbody');
    if (!tbody) return;

    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="color: #777;">No history yet. Start listening!</td></tr>';
        return;
    }

    tbody.innerHTML = history.map((track, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td style="font-weight: 700; color: #fff;">${escapeHtml(track.title)}</td>
            <td style="color: #b3b3b3;">${escapeHtml(track.channel)}</td>
            <td style="color: #b3b3b3;">${track.duration}</td>
            <td>
                <button class="btn-search" style="padding: 4px 12px; font-size: 0.8rem;" onclick='playSong(${JSON.stringify(track).replace(/'/g, "&apos;")}, ${JSON.stringify(history).replace(/'/g, "&apos;")}, ${idx})'>▶️ Play</button>
            </td>
        </tr>
    `).join('');
}

function renderPlaylistDetail(name) {
    const playlists = appData.playlists || {};
    const tracks = playlists[name] || [];

    document.getElementById('playlist-detail-title').innerText = `📁 ${name}`;
    document.getElementById('playlist-detail-subtitle').innerText = `${tracks.length} songs`;

    const tbody = document.getElementById('playlist-tbody');
    if (!tbody) return;

    if (tracks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="color: #777;">Playlist is empty. Search and add tracks!</td></tr>';
        return;
    }

    tbody.innerHTML = tracks.map((track, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td style="font-weight: 700; color: #fff;">${escapeHtml(track.title)}</td>
            <td style="color: #b3b3b3;">${escapeHtml(track.channel)}</td>
            <td style="color: #b3b3b3;">${track.duration}</td>
            <td>
                <button class="btn-search" style="padding: 4px 12px; font-size: 0.8rem;" onclick='playSong(${JSON.stringify(track).replace(/'/g, "&apos;")}, ${JSON.stringify(tracks).replace(/'/g, "&apos;")}, ${idx})'>▶️ Play</button>
                <button class="btn-icon" onclick="removeTrackFromPlaylist('${escapeHtml(name)}', '${track.id}')">❌</button>
            </td>
        </tr>
    `).join('');
}

// Liked Songs Toggle API Call
async function toggleFavoriteTrack(song) {
    try {
        const res = await fetch('/api/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(song)
        });
        if (res.ok) {
            const data = await res.json();
            appData = data.data;
            showToast(data.added ? "❤️ Added to Liked Songs" : "💔 Removed from Liked Songs");
            renderLikedSongs();
            updatePlayerLikeButton();
            if (currentView === 'search') {
                const grid = document.getElementById('search-results-grid');
                if (grid) renderCardsGrid(appData.history, 'home-recent-grid');
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function isLiked(songId) {
    return (appData.favorites || []).some(s => s.id === songId);
}

function updatePlayerLikeButton() {
    const btn = document.getElementById('btn-player-like');
    if (btn && currentSong) {
        btn.innerText = isLiked(currentSong.id) ? '❤️' : '🤍';
    }
}

function toggleCurrentSongLike() {
    if (currentSong) {
        toggleFavoriteTrack(currentSong);
    }
}

// Direct 1-Click MP3 Download
function downloadCurrentSong(event) {
    if (!currentSong) {
        event.preventDefault();
        return;
    }
    const downloadUrl = `/api/download?url=${encodeURIComponent(currentSong.url)}`;
    document.getElementById('btn-player-download').href = downloadUrl;
    showToast("📥 Starting MP3 Download...");
}

// Custom Playlist API Operations
function openCreatePlaylistModal() {
    document.getElementById('create-playlist-modal').style.display = 'flex';
}

function closeCreatePlaylistModal() {
    document.getElementById('create-playlist-modal').style.display = 'none';
}

async function submitCreatePlaylist() {
    const input = document.getElementById('modal-playlist-name');
    const name = input.value.trim();
    if (!name) return;

    try {
        const res = await fetch('/api/playlists/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.ok) {
            const data = await res.json();
            appData = data.data;
            showToast(`✅ Created Playlist "${name}"`);
            closeCreatePlaylistModal();
            input.value = '';
            renderSidebarPlaylists();
            switchView('playlist', name);
        }
    } catch (e) {
        console.error(e);
    }
}

async function deleteCurrentPlaylist() {
    if (!activePlaylistName) return;
    try {
        const res = await fetch('/api/playlists/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: activePlaylistName })
        });
        if (res.ok) {
            const data = await res.json();
            appData = data.data;
            showToast(`Deleted Playlist "${activePlaylistName}"`);
            renderSidebarPlaylists();
            switchView('home');
        }
    } catch (e) {
        console.error(e);
    }
}

async function addTrackToPlaylist(playlistName, song) {
    try {
        const res = await fetch('/api/playlists/add_track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ playlist_name: playlistName, song })
        });
        if (res.ok) {
            await fetchAppData();
            showToast(`Added to "${playlistName}"`);
        }
    } catch (e) {
        console.error(e);
    }
}

async function removeTrackFromPlaylist(playlistName, songId) {
    try {
        const res = await fetch('/api/playlists/remove_track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ playlist_name: playlistName, song_id: songId })
        });
        if (res.ok) {
            await fetchAppData();
            showToast("Removed from playlist");
            renderPlaylistDetail(playlistName);
        }
    } catch (e) {
        console.error(e);
    }
}

function renderPlaylistDropdownHTML(track) {
    const playlists = Object.keys(appData.playlists || {});
    if (playlists.length === 0) return '';

    return `
        <select class="genre-pill" style="font-size: 0.75rem; padding: 4px 8px;" onchange="if(this.value){ addTrackToPlaylist(this.value, ${JSON.stringify(track).replace(/"/g, '&quot;')}); this.value=''; }">
            <option value="">➕ Add to...</option>
            ${playlists.map(pl => `<option value="${escapeHtml(pl)}">${escapeHtml(pl)}</option>`).join('')}
        </select>
    `;
}

function playCurrentPlaylist() {
    if (activePlaylistName && appData.playlists[activePlaylistName]) {
        const tracks = appData.playlists[activePlaylistName];
        if (tracks.length > 0) {
            playSong(tracks[0], tracks, 0);
        }
    }
}

// Utility Helpers
function showToast(message) {
    const toast = document.getElementById('toast-container');
    toast.innerText = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
