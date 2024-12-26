from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import os
import google.generativeai as genai
import time

from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
API_KEY = os.environ['YT_DEV_API_KEY']

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
# open default credentials file
credentials = None
try:
    with open('secrets/credentials.json', 'r') as f:
        credentials = json.load(f)
except FileNotFoundError:
    print("Debug log: credentials.json not found")

# to get trending topics on youtube
@app.get("/create-video")
async def create_video():
    '''
    This function is used to create a video.
    It will search for trending topics on youtube.
    It will figure out the trending topic with the content that is most relevant to the user.
    It will request google api to create a text to explain the trending topic.
    It will request google converts text to speech.
    It will select one of the agents avaliable.
    It will request the joyvasa model to create a video with agent and the text to explain the trending topic.
    '''
    # Search for trending topics on youtube
    def search_trending_topics_on_youtube():
        '''
        This function is used to search for trending topics on youtube.
        '''
        try:
            # Create YouTube client with API key instead of credentials
            print("Debug log: API_KEY: ", API_KEY)
            youtube = build('youtube', 'v3', developerKey=API_KEY)
            print("Debug log: YouTube API client created with API key")
            
            request = youtube.search().list(
                part="snippet",
                type="video",
                q="trending topics to get explained",
                maxResults=10,
                fields="*"
            )
            response = request.execute()
            print("Debug log: response: ", response["items"])
            return {"trending_topics": response["items"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Trending topics on youtube
    trending_topics = search_trending_topics_on_youtube()
    print("Debug log: trending_topics: ", trending_topics)
    # return {"trending_topics": trending_topics}

    # get the above trending topics and create a optimal topic using gemini api
    def create_optimal_topic_using_gemini_api(trending_topics):
        '''
        This function uses Gemini API to analyze trending topics and select the best one for an explanatory video.
        '''
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            generation_config = genai.GenerationConfig(
                temperature=0.5,
                top_p=0.80,
                top_k=64,
                max_output_tokens=2048,
            )
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            # Simplify the system instruction to ensure valid JSON output
            prompt = f"""Analyze these YouTube trending topics and create a video script.
            Topics: {json.dumps(trending_topics)}

            Return a JSON object in this exact format:
            {{
                "selected_topic": "topic title",
                "explanation_angle": "brief approach explanation",
                "key_points": ["point1", "point2", "point3"],
                "target_duration": "3",
                "video_script": "complete script here",
                "tags": ["tag1", "tag2", "tag3"]
            }} video script should be in the form of a script for a video, use punctuation and natural language its hould be a script for a video with series of sentences without any gaps and it hsould last of 30 seconds when converted to audio"""

            response = model.generate_content(prompt)
            
            # Clean and parse the response
            response_text = response.text.strip()
            
            # Remove markdown formatting if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            try:
                parsed_response = json.loads(response_text)
                print("Successfully parsed JSON response")
                
                return {
                    "title": parsed_response["selected_topic"],
                    "description": {
                        "explanation_angle": parsed_response["explanation_angle"],
                        "key_points": parsed_response["key_points"],
                        "tags": parsed_response.get("tags", [])  # Use get() with default empty list
                    },
                    "video_script": parsed_response["video_script"],
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Raw response text: {response_text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid JSON response from Gemini API: {str(e)}"
                )
                
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Gemini API: {str(e)}"
            )

    # get the optimal topic
    optimal_topic = create_optimal_topic_using_gemini_api(trending_topics)
    print("Debug log: optimal_topic: ", optimal_topic)
    # return optimal_topic

    #convert the optimal topic to a video script
    def video_script_to_audio(video_script):
        '''
        This function converts the video script to audio using Coqui TTS.
        Returns the path to the generated audio file.
        '''
        try:
            from TTS.api import TTS
            # Create a unique filename using timestamp
            output_file = f"generated_audio/audio_{int(time.time())}.wav"
            
            # Initialize TTS with the specified model
            # tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            tts = TTS(model_name="tts_models/en/jenny/jenny")
            
            # Generate and save the audio
            tts.tts_to_file(text=video_script, file_path=output_file)
            print(f"Audio content written to file: {output_file}")

            return output_file
        except Exception as e:
            print(f"Error in text-to-speech conversion: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    audio_file = video_script_to_audio(optimal_topic["video_script"])
    print("Debug log: audio_file: ", audio_file)
    return "HELoooo boiii"

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
    # TODO: save the credentials to a file
    with open('secrets/credentials.json', 'w') as f:
        json.dump(credentials.to_json(), f)
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
