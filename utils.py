import urllib.request
import urllib.parse
import re
import json
import os
import html

DATA_FILE = "pytune_data.json"

def search_youtube(query, max_results=12):
    """
    Searches YouTube for videos matching the query and returns list of metadata dictionaries.
    Uses native scraping to avoid needing an API key.
    """
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
    pattern = r'var ytInitialData = ({.*?});'
    match = re.search(pattern, html_content)
    if not match:
        pattern = r'window\["ytInitialData"\] = ({.*?});'
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
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
        
        for content in contents:
            if 'itemSectionRenderer' in content:
                items = content['itemSectionRenderer']['contents']
                for item in items:
                    if 'videoRenderer' in item:
                        video_data = item['videoRenderer']
                        
                        # Basic fields
                        video_id = video_data.get('videoId')
                        if not video_id:
                            continue
                            
                        # Title
                        title = "Unknown Title"
                        if 'title' in video_data and 'runs' in video_data['title']:
                            title = html.unescape(video_data['title']['runs'][0]['text'])
                        
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

def load_data():
    """Loads favorites and search history from a local JSON file."""
    default_data = {"favorites": [], "history": []}
    if not os.path.exists(DATA_FILE):
        return default_data
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
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

def add_to_history(song):
    """Adds a song to the history. Removes duplicates and limits to last 30 entries."""
    data = load_data()
    # Remove existing copy if present
    data['history'] = [item for item in data['history'] if item['id'] != song['id']]
    # Insert at the beginning (most recent first)
    data['history'].insert(0, song)
    # Keep only the last 30 items
    data['history'] = data['history'][:30]
    save_data(data)

def toggle_favorite(song):
    """Toggles favorite status for a song."""
    data = load_data()
    is_fav = any(item['id'] == song['id'] for item in data['favorites'])
    
    if is_fav:
        # Remove from favorites
        data['favorites'] = [item for item in data['favorites'] if item['id'] != song['id']]
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
    return any(item['id'] == song_id for item in data['favorites'])

def get_audio_stream_url(youtube_url):
    """
    Extracts the direct audio stream URL from a YouTube watch URL using yt-dlp.
    """
    import yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get('url')
        except Exception as e:
            print(f"Error extracting audio stream URL: {e}")
            return None

def download_audio_local(youtube_url):
    """
    Downloads the audio track directly to the user's local Downloads folder.
    Returns (download_dir, filename) if successful, otherwise (None, None).
    """
    import yt_dlp
    import os
    
    try:
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(download_dir):
            download_dir = os.path.join(os.getcwd(), "downloads")
    except Exception:
        download_dir = os.path.join(os.getcwd(), "downloads")
        
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            basename = os.path.basename(filename)
            return download_dir, basename
        except Exception as e:
            print(f"Error downloading audio locally: {e}")
            return None, None
