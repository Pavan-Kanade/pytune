from fastapi import FastAPI, Request, Query, HTTPException, Response, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse, RedirectResponse
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
os.makedirs("downloads", exist_ok=True)

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

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = ""

class UserLoginRequest(BaseModel):
    email: str
    password: str

class OAuthLoginRequest(BaseModel):
    provider: str
    email: str
    name: Optional[str] = ""
    avatar: Optional[str] = ""


def cleanup_temp_file(filepath: str, file_id: str):
    """Deletes temporary cached MP3 file from server disk immediately after download completes."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"[CLEANUP] Deleted server temp file: {filepath} (Storage restored to null)")
    except Exception as e:
        print(f"[CLEANUP ERROR] {e}")


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Renders the Spotify Single Page Application frontend."""
    return templates.TemplateResponse(request=request, name="index.html")


# Auth API Endpoints

@app.post("/api/auth/register")
async def api_register(payload: UserRegisterRequest, response: Response):
    """Registers a new user account."""
    res = utils.register_user(payload.email, payload.password, payload.name)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    token = res.get("token")
    response.set_cookie(key="pytune_session", value=token, max_age=30*24*3600, httponly=False)
    return JSONResponse(res)


@app.post("/api/auth/login")
async def api_login(payload: UserLoginRequest, response: Response):
    """Logs in an existing user with email & password."""
    res = utils.login_user(payload.email, payload.password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    token = res.get("token")
    response.set_cookie(key="pytune_session", value=token, max_age=30*24*3600, httponly=False)
    return JSONResponse(res)


@app.post("/api/auth/oauth")
async def api_oauth_login(payload: OAuthLoginRequest, response: Response):
    """Logs in or registers user via Google or Microsoft OAuth."""
    res = utils.login_oauth_user(payload.provider, payload.email, payload.name, payload.avatar)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    token = res.get("token")
    response.set_cookie(key="pytune_session", value=token, max_age=30*24*3600, httponly=False)
    return JSONResponse(res)


@app.get("/api/auth/me")
async def api_get_current_user(request: Request):
    """Returns currently authenticated user profile."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        token = request.cookies.get("pytune_session", "")
    
    user = utils.get_user_by_session(token)
    if not user:
        return JSONResponse({"authenticated": False, "user": None})
    return JSONResponse({"authenticated": True, "user": user})


@app.post("/api/auth/logout")
async def api_logout(request: Request, response: Response):
    """Logs out user and clears session cookie."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        token = request.cookies.get("pytune_session", "")
    utils.logout_user(token)
    response.delete_cookie("pytune_session")
    return JSONResponse({"success": True})



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
async def api_download(url: str = Query(...), background_tasks: BackgroundTasks = None):
    """
    Pre-buffers audio track into temporary server storage ('downloads/'),
    serves FileResponse directly to browser, and auto-deletes file immediately
    after transfer completes (leaving server storage null).
    """
    if background_tasks is None:
        background_tasks = BackgroundTasks()

    filepath, filename, file_id = utils.save_audio_to_temp_storage(url)
    
    if filepath and os.path.exists(filepath):
        # Schedule automatic cleanup immediately after transfer completes
        background_tasks.add_task(cleanup_temp_file, filepath, file_id)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-cache",
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    # Fallback to direct stream redirect if server temp buffering fails
    stream_url, _ = utils.get_audio_stream_info(url)
    if stream_url:
        return RedirectResponse(url=stream_url, status_code=302)

    raise HTTPException(status_code=500, detail="Could not prepare temporary MP3 file for download.")


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
