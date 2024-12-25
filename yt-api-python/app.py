from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Constants
CLIENT_SECRETS_FILE = "./secrets/client_secret_172892498928-9t6med904ivd94vcaaq10gcsfka9fjhs.apps.googleusercontent.com.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.upload'
]
REDIRECT_URI = "http://localhost:3001/oauth2callback"

# Global variable to store credentials
credentials = None

@app.get("/auth")
async def authenticate():
    '''
    This function is used to authenticate the user.
    Takes the secrets which will authenticate the user and redirect to the auth url.
    when redirected to the auth url, the user will be asked to give permission to the app to upload videos to their channel.
    After the user gives permission, the user will be redirected to the oauth2callback function.
    with a code which will be used to get the access token and refresh token.
    '''
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    print('debug log 1 - yt-api-python - app.py - auth_url: ', auth_url)
    return RedirectResponse(url=auth_url)

@app.get("/oauth2callback")
async def oauth2callback(code: str):
    '''
    This function is used to get the access token and refresh token.
    Takes the code which will be used to get the access token and refresh token.
    '''
    global credentials
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {"message": "Authentication successful! You can now upload videos."}

@app.get("/channel-info")
async def get_channel_info():
    """
    Get information about the authenticated user's YouTube channel
    """
    global credentials
    if not credentials:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Call the channels().list method to retrieve channel information
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    print("Debug log: Rendering upload form")
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_video(
    video: UploadFile = File(...),
    title: str = Form("Default Title"),
    description: str = Form("Default Description"),
    tags: str = Form(""),
    privacy_status: str = Form("private")
):
    print(f"Debug log: Uploading video with title: {title}")
    global credentials
    if not credentials:
        print("Debug log: User is not authenticated")
        raise HTTPException(status_code=401, detail="User is not authenticated")

    temp_file_path = f"temp_{video.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
            print(f"Debug log: Video file saved to {temp_file_path}")

        youtube = build('youtube', 'v3', credentials=credentials)
        print("Debug log: YouTube API client created")

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags.split(',') if tags else [],
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        # Insert video with chunked upload
        media = MediaFileUpload(
            temp_file_path,
            chunksize=1024*1024,
            resumable=True
        )

        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        # Clean up
        os.remove(temp_file_path)
        
        print(f"Debug log: Video uploaded successfully. Video ID: {response['id']}")
        return {
            "message": "Video uploaded successfully",
            "video_id": response['id'],
            "video_url": f"https://youtube.com/watch?v={response['id']}"
        }

    except Exception as e:
        print(f"Debug log: Error occurred during video upload - {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
