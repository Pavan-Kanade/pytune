from fastapi import FastAPI, Request, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, Optional
import utils
import os

app = FastAPI(title="PyTune Web Application", description="Spotify-style Full-Stack Web Music Streaming App")

# Mount Static & Template directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Request Pydantic Schemas
class SongModel(BaseModel):
    id: str
    title: str
    thumbnail: str
    duration: str
    channel: str
    views: Optional[str] = ""
    url: str

class PlaylistCreateRequest(BaseModel):
    name: str

class PlaylistDeleteRequest(BaseModel):
    name: str

class PlaylistAddTrackRequest(BaseModel):
    playlist_name: str
    song: Dict[str, Any]

class PlaylistRemoveTrackRequest(BaseModel):
    playlist_name: str
    song_id: str


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Renders the Spotify Single Page Application frontend."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=1), max_results: int = 12):
    """Searches YouTube for videos and returns list of track metadata."""
    results = utils.search_youtube(q, max_results=max_results)
    if q.strip():
        utils.add_recent_search(q)
    return JSONResponse(results)


@app.get("/api/stream")
async def api_stream(url: str = Query(...)):
    """Extracts direct audio stream URL."""
    stream_url = utils.get_audio_stream_url(url)
    if not stream_url:
        raise HTTPException(status_code=404, detail="Audio stream URL could not be extracted.")
    return JSONResponse({"stream_url": stream_url})


@app.get("/api/download")
async def api_download(url: str = Query(...)):
    """Downloads audio track and streams MP3 file directly to browser."""
    # 1. Try local disk byte extraction
    try:
        data, filename = utils.get_audio_bytes_via_ytdl(url)
        if data and filename:
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "audio/mpeg",
                "Content-Length": str(len(data)),
                "Cache-Control": "no-cache",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
            return Response(content=data, media_type="audio/mpeg", headers=headers)
    except Exception as e:
        print(f"Local byte download error: {e}")

    # 2. Proxy Stream Fallback (Bypasses Render cloud disk download blocks)
    stream_url, filename = utils.get_audio_stream_info(url)
    if stream_url:
        try:
            import urllib.request
            def audio_chunk_generator():
                req = urllib.request.Request(
                    stream_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as resp:
                    while True:
                        chunk = resp.read(64 * 1024)
                        if not chunk:
                            break
                        yield chunk

            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "audio/mpeg",
                "Cache-Control": "no-cache",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
            return StreamingResponse(audio_chunk_generator(), media_type="audio/mpeg", headers=headers)
        except Exception as e2:
            print(f"Proxy chunk streaming error: {e2}. Redirecting...")
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=stream_url, status_code=302)

    raise HTTPException(status_code=404, detail="Audio stream unavailable.")


@app.get("/api/data")
async def api_get_data():
    """Returns persistent local storage data (favorites, history, searches, playlists)."""
    return JSONResponse(utils.load_data())


@app.post("/api/favorites")
async def api_toggle_favorite(song: Dict[str, Any]):
    """Toggles song in Liked Songs."""
    added = utils.toggle_favorite(song)
    return JSONResponse({"added": added, "data": utils.load_data()})


@app.post("/api/history")
async def api_add_history(song: Dict[str, Any]):
    """Adds song to listening history."""
    utils.add_to_history(song)
    return JSONResponse({"success": True})


@app.post("/api/playlists/create")
async def api_create_playlist(payload: PlaylistCreateRequest):
    """Creates a new custom playlist."""
    created = utils.create_playlist(payload.name)
    return JSONResponse({"success": created, "data": utils.load_data()})


@app.post("/api/playlists/delete")
async def api_delete_playlist(payload: PlaylistDeleteRequest):
    """Deletes a custom playlist."""
    deleted = utils.delete_playlist(payload.name)
    return JSONResponse({"success": deleted, "data": utils.load_data()})


@app.post("/api/playlists/add_track")
async def api_add_to_playlist(payload: PlaylistAddTrackRequest):
    """Adds a song to a custom playlist."""
    added = utils.add_to_playlist(payload.playlist_name, payload.song)
    return JSONResponse({"success": added, "data": utils.load_data()})


@app.post("/api/playlists/remove_track")
async def api_remove_from_playlist(payload: PlaylistRemoveTrackRequest):
    """Removes a song from a custom playlist."""
    removed = utils.remove_from_playlist(payload.playlist_name, payload.song_id)
    return JSONResponse({"success": removed, "data": utils.load_data()})


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload_flag = os.getenv("ENV", "development").lower() == "development"
    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)
