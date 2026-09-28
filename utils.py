import urllib.request
import urllib.parse
import re
import json
import os
import html
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATA_FILE = os.getenv("DATA_FILE", "pytune_data.json")
DEFAULT_MAX_RESULTS = int(os.getenv("DEFAULT_SEARCH_MAX_RESULTS", 12))

def search_youtube(query, max_results=None):
    """
    Searches YouTube for videos matching the query and returns list of metadata dictionaries.
    Uses native scraping to avoid needing an API key.
    """
    if max_results is None:
        max_results = DEFAULT_MAX_RESULTS
    if not query.strip():
        return []
        
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return []
    
    # Locate the ytInitialData JSON object
    pattern = r'(?:var|window\[")ytInitialData(?:\])?\s*=\s*({.+?});\s*(?:</script>|\n)'
    match = re.search(pattern, html_content)
    if not match:
        pattern = r'ytInitialData\s*=\s*({.+?});'
        match = re.search(pattern, html_content)
        
    if not match:
        print("Could not find ytInitialData in page source")
        return []
        
    try:
        data = json.loads(match.group(1))
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return []
    
    videos = []
    try:
        # Navigate the JSON structure of search results
        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
        
        for content in contents:
            if 'itemSectionRenderer' in content:
                items = content['itemSectionRenderer'].get('contents', [])
                for item in items:
                    if 'videoRenderer' in item:
                        video_data = item['videoRenderer']
                        
                        # Basic fields
                        video_id = video_data.get('videoId')
                        if not video_id:
                            continue
                            
                        # Title
                        title = "Unknown Title"
                        if 'title' in video_data:
                            if 'runs' in video_data['title'] and video_data['title']['runs']:
                                title = html.unescape(video_data['title']['runs'][0]['text'])
                            elif 'simpleText' in video_data['title']:
                                title = html.unescape(video_data['title']['simpleText'])
                        
                        # Thumbnail
                        thumbnail = "https://images.unsplash.com/photo-1614680376593-902f74fa0d41?w=400&q=80"
                        if 'thumbnail' in video_data and 'thumbnails' in video_data['thumbnail'] and video_data['thumbnail']['thumbnails']:
                            thumbnail = video_data['thumbnail']['thumbnails'][0]['url']
                        
                        # Duration
                        duration = "Unknown"
                        if 'lengthText' in video_data and 'simpleText' in video_data['lengthText']:
                            duration = video_data['lengthText']['simpleText']
                        
                        # Channel name
                        channel = "Unknown Channel"
                        if 'ownerText' in video_data and 'runs' in video_data['ownerText'] and video_data['ownerText']['runs']:
                            channel = html.unescape(video_data['ownerText']['runs'][0]['text'])
                            
                        # Views
                        views = "Unknown views"
                        if 'shortViewCountText' in video_data and 'simpleText' in video_data['shortViewCountText']:
                            views = video_data['shortViewCountText']['simpleText']
                            
                        videos.append({
                            'id': video_id,
                            'title': title,
                            'thumbnail': thumbnail,
                            'duration': duration,
                            'channel': channel,
                            'views': views,
                            'url': f"https://www.youtube.com/watch?v={video_id}"
                        })
                        
                        if len(videos) >= max_results:
                            return videos
    except Exception as e:
        print(f"Error parsing YouTube search results structure: {e}")
        
    return videos

# Local Data Persistence Functions

import hashlib
import uuid

def load_data():
    """Loads favorites, search history, playlists, users, and sessions from a local JSON file."""
    default_data = {
        "favorites": [],
        "history": [],
        "searches": [],
        "playlists": {},
        "users": {},
        "sessions": {}
    }
    if not os.path.exists(DATA_FILE):
        return default_data
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return default_data
            # Ensure default keys exist
            if 'favorites' not in data or not isinstance(data['favorites'], list): data['favorites'] = []
            if 'history' not in data or not isinstance(data['history'], list): data['history'] = []
            if 'searches' not in data or not isinstance(data['searches'], list): data['searches'] = []
            if 'playlists' not in data or not isinstance(data['playlists'], dict): data['playlists'] = {}
            if 'users' not in data or not isinstance(data['users'], dict): data['users'] = {}
            if 'sessions' not in data or not isinstance(data['sessions'], dict): data['sessions'] = {}
            return data
    except Exception as e:
        print(f"Error loading local data: {e}")
        return default_data

def save_data(data):
    """Saves favorites and search history to a local JSON file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving local data: {e}")

def hash_password(password: str) -> str:
    """Hashes user password using SHA-256 with a salt."""
    salt = "pytune_secret_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def register_user(email: str, password: str, name: str = ""):
    """Registers a new user account with email and password."""
    email = email.strip().lower()
    if not email or '@' not in email:
        return {"success": False, "error": "Invalid email address format."}
    if not password or len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters long."}
    
    data = load_data()
    if email in data['users']:
        return {"success": False, "error": "An account with this email already exists."}

    user_id = f"user_{str(uuid.uuid4())[:8]}"
    clean_name = name.strip() if name else email.split('@')[0].capitalize()
    
    user_record = {
        "id": user_id,
        "email": email,
        "name": clean_name,
        "password_hash": hash_password(password),
        "provider": "email",
        "avatar": f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"
    }
    
    session_token = f"sess_{str(uuid.uuid4())}"
    data['users'][email] = user_record
    data['sessions'][session_token] = {
        "user_id": user_id,
        "email": email
    }
    save_data(data)
    
    return {
        "success": True,
        "token": session_token,
        "user": {
            "id": user_id,
            "email": email,
            "name": clean_name,
            "provider": "email",
            "avatar": user_record["avatar"]
        }
    }

def login_user(email: str, password: str):
    """Authenticates user with email and password."""
    email = email.strip().lower()
    if not email or not password:
        return {"success": False, "error": "Please provide both email and password."}
        
    data = load_data()
    user = data['users'].get(email)
    if not user:
        return {"success": False, "error": "No account found with this email address."}
        
    if user.get("password_hash") != hash_password(password):
        return {"success": False, "error": "Incorrect password."}

    session_token = f"sess_{str(uuid.uuid4())}"
    data['sessions'][session_token] = {
        "user_id": user.get("id"),
        "email": email
    }
    save_data(data)

    return {
        "success": True,
        "token": session_token,
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "provider": user.get("provider", "email"),
            "avatar": user.get("avatar", "")
        }
    }

def login_oauth_user(provider: str, email: str, name: str = "", avatar: str = ""):
    """Registers or logs in a user using OAuth (Google or Microsoft)."""
    email = email.strip().lower()
    if not email:
        return {"success": False, "error": "OAuth user email required."}

    data = load_data()
    clean_name = name.strip() if name else email.split('@')[0].capitalize()
    
    if email in data['users']:
        user_record = data['users'][email]
        user_record["provider"] = provider
        if avatar:
            user_record["avatar"] = avatar
    else:
        user_id = f"user_{str(uuid.uuid4())[:8]}"
        user_record = {
            "id": user_id,
            "email": email,
            "name": clean_name,
            "password_hash": "",
            "provider": provider,
            "avatar": avatar or f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"
        }
        data['users'][email] = user_record

    session_token = f"sess_{str(uuid.uuid4())}"
    data['sessions'][session_token] = {
        "user_id": user_record.get("id"),
        "email": email
    }
    save_data(data)

    return {
        "success": True,
        "token": session_token,
        "user": {
            "id": user_record.get("id"),
            "email": user_record.get("email"),
            "name": user_record.get("name"),
            "provider": provider,
            "avatar": user_record.get("avatar")
        }
    }

def get_user_by_session(token: str):
    """Retrieves logged in user details by session token."""
    if not token:
        return None
    data = load_data()
    session = data['sessions'].get(token)
    if not session:
        return None
    email = session.get("email")
    user = data['users'].get(email)
    if not user:
        return None
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "provider": user.get("provider", "email"),
        "avatar": user.get("avatar", "")
    }

def logout_user(token: str):
    """Logs out user by invalidating the session token."""
    if not token:
        return True
    data = load_data()
    if token in data['sessions']:
        del data['sessions'][token]
        save_data(data)
    return True


def add_to_history(song):
    """Adds a song to the history. Removes duplicates and limits to last 30 entries."""
    if not isinstance(song, dict) or 'id' not in song:
        return
    data = load_data()
    # Remove existing copy if present
    data['history'] = [item for item in data['history'] if item.get('id') != song.get('id')]
    # Insert at the beginning (most recent first)
    data['history'].insert(0, song)
    # Keep only the last 30 items
    data['history'] = data['history'][:30]
    save_data(data)

def toggle_favorite(song):
    """Toggles favorite status for a song."""
    if not isinstance(song, dict) or 'id' not in song:
        return False
    data = load_data()
    is_fav = any(item.get('id') == song.get('id') for item in data['favorites'])
    
    if is_fav:
        # Remove from favorites
        data['favorites'] = [item for item in data['favorites'] if item.get('id') != song.get('id')]
        added = False
    else:
        # Add to favorites
        data['favorites'].insert(0, song)
        added = True
        
    save_data(data)
    return added

def is_favorite(song_id):
    """Checks if a song is in favorites."""
    data = load_data()
    return any(item.get('id') == song_id for item in data['favorites'])

def extract_video_id(url_or_id):
    """Safely extracts 11-character YouTube video ID from watch URL, short URL, or plain ID."""
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and not ('/' in url_or_id or '.' in url_or_id):
        return url_or_id
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url_or_id)
    if match:
        return match.group(1)
    return url_or_id

def get_audio_stream_url(youtube_url):
    """
    Extracts the direct audio stream URL from a YouTube watch URL using yt-dlp.
    """
    url, _ = get_audio_stream_info(youtube_url)
    return url

def get_audio_stream_info(youtube_url):
    """
    Extracts direct audio stream URL and sanitized title filename without downloading bytes.
    Uses multi-strategy yt-dlp client fallback + Invidious API fallback for 100% cloud reliability.
    """
    import yt_dlp
    
    video_id = extract_video_id(youtube_url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else youtube_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    # Sequential player client configs to bypass YouTube cloud IP blocks
    client_configs = [
        {'player_client': ['android']},
        {'player_client': ['web']},
        {'player_client': ['ios']},
        {'player_client': ['mweb']},
        {} # Default fallback
    ]

    for config in client_configs:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'http_headers': headers
        }
        if config:
            ydl_opts['extractor_args'] = {'youtube': config}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                stream_url = info.get('url')
                
                # Fallback format search if top-level url is missing
                if not stream_url and 'formats' in info and isinstance(info['formats'], list):
                    audio_formats = [
                        f for f in info['formats'] 
                        if (f.get('vcodec') == 'none' or f.get('acodec') != 'none') and f.get('url')
                    ]
                    if audio_formats:
                        audio_formats.sort(key=lambda x: x.get('tbr') or x.get('abr') or 0)
                        stream_url = audio_formats[-1]['url']

                if stream_url:
                    title = info.get('title', 'audio')
                    clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
                    if not clean_title:
                        clean_title = "audio"
                    filename = f"{clean_title}.mp3"
                    return stream_url, filename
        except Exception as e:
            print(f"Extraction attempt failed: {e}")

    # Fallback: Invidious API for cloud IP bypass if yt-dlp is blocked
    try:
        if video_id:
            invidious_api_url = f"https://api.invidious.io/api/v1/videos/{video_id}"
            req = urllib.request.Request(invidious_api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                inv_data = json.loads(resp.read().decode('utf-8'))
                fmt_streams = inv_data.get('adaptiveFormats', [])
                audio_streams = [f for f in fmt_streams if 'audio' in f.get('type', '') and f.get('url')]
                if audio_streams:
                    stream_url = audio_streams[0]['url']
                    title = inv_data.get('title', 'audio')
                    clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
                    if not clean_title: clean_title = "audio"
                    return stream_url, f"{clean_title}.mp3"
    except Exception as e_inv:
        print(f"Invidious API fallback error: {e_inv}")

def save_audio_to_temp_storage(youtube_url):
    """
    Downloads audio track to temporary 'downloads/' cache directory on server,
    returns (file_path, filename, file_id).
    Streams stream_url directly to temp file if yt-dlp local disk download fails on Cloud IPs.
    """
    import os
    import uuid
    import urllib.request
    
    downloads_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    file_id = str(uuid.uuid4())[:8]

    # 1. Attempt yt-dlp local download first
    try:
        data, filename = get_audio_bytes_via_ytdl(youtube_url)
        if data and filename:
            temp_filepath = os.path.join(downloads_dir, f"{file_id}_{filename}")
            with open(temp_filepath, 'wb') as f:
                f.write(data)
            return temp_filepath, filename, file_id
    except Exception as e:
        print(f"Byte extraction failed: {e}")

    # 2. Fallback: Stream direct audio stream into temp file on server
    try:
        stream_url, filename = get_audio_stream_info(youtube_url)
        if stream_url:
            temp_filepath = os.path.join(downloads_dir, f"{file_id}_{filename}")
            req = urllib.request.Request(
                stream_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp, open(temp_filepath, 'wb') as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            return temp_filepath, filename, file_id
    except Exception as e2:
        print(f"Stream buffer save failed: {e2}")

    return None, "song.mp3", None

def get_audio_bytes_via_ytdl(youtube_url):
    """
    Downloads the audio track using yt-dlp to a temporary file,
    reads its bytes, deletes the temp file, and returns (bytes, filename).
    Compatible with both local laptop run and Streamlit Cloud deployment.
    """
    import yt_dlp
    import tempfile
    import os
    
    # Use system temp directory
    temp_dir = tempfile.gettempdir()
    
    # We want a unique template name
    outtmpl = os.path.join(temp_dir, 'pytune_temp_%(id)s.%(ext)s')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # Cloud-optimized yt-dlp options (bypasses YouTube AWS/GCP cloud IP blocks)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'http_headers': headers,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],
                'skip': ['hls', 'dash']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Read bytes
            with open(filename, 'rb') as f:
                data = f.read()
                
            # Clean up the file
            try:
                os.remove(filename)
            except Exception:
                pass
                
            title = info.get('title', 'audio')
            clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
            if not clean_title:
                clean_title = "audio"
            download_filename = f"{clean_title}.mp3"
            
            return data, download_filename
    except Exception as e:
        print(f"Primary download failed: {e}. Trying fallback options...")
        try:
            fallback_opts = {
                'format': 'ba/b',
                'outtmpl': outtmpl,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'noplaylist': True
            }
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                filename = ydl.prepare_filename(info)
                with open(filename, 'rb') as f:
                    data = f.read()
                try:
                    os.remove(filename)
                except Exception:
                    pass
                title = info.get('title', 'audio')
                clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
                if not clean_title: clean_title = "audio"
                return data, f"{clean_title}.mp3"
        except Exception as e2:
            print(f"Fallback download error: {e2}")
            return None, None

def add_recent_search(query):
    """Adds a search query to the persistent search history list."""
    query = query.strip()
    if not query:
        return
    data = load_data()
    # Remove existing copy if present
    data['searches'] = [item for item in data['searches'] if item.lower() != query.lower()]
    # Insert at the beginning (most recent first)
    data['searches'].insert(0, query)
    # Keep only the last 5 items
    data['searches'] = data['searches'][:5]
    save_data(data)

def create_playlist(name):
    """Creates a new custom playlist."""
    name = name.strip()
    if not name:
        return False
    data = load_data()
    if name not in data['playlists']:
        data['playlists'][name] = []
        save_data(data)
        return True
    return False

def delete_playlist(name):
    """Deletes a custom playlist."""
    data = load_data()
    if name in data['playlists']:
        del data['playlists'][name]
        save_data(data)
        return True
    return False

def add_to_playlist(name, song):
    """Adds a song to a custom playlist."""
    if not isinstance(song, dict) or 'id' not in song:
        return False
    data = load_data()
    if name in data['playlists']:
        if not any(item.get('id') == song.get('id') for item in data['playlists'][name]):
            data['playlists'][name].append(song)
            save_data(data)
            return True
    return False

def remove_from_playlist(name, song_id):
    """Removes a song from a custom playlist."""
    data = load_data()
    if name in data['playlists']:
        data['playlists'][name] = [item for item in data['playlists'][name] if item.get('id') != song_id]
        save_data(data)
        return True
    return False
