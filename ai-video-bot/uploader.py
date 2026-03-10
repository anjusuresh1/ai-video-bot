import os
import json
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ============ YOUTUBE UPLOADER ============
def upload_to_youtube(video_path, title, description, tags=[]):
    """Upload to YouTube Shorts"""
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None
    
    if os.path.exists("credentials/youtube_token.json"):
        creds = Credentials.from_authorized_user_file("credentials/youtube_token.json", SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials/youtube_creds.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("credentials/youtube_token.json", "w") as f:
            f.write(creds.to_json())
    
    youtube = build("youtube", "v3", credentials=creds)
    
    # Add #Shorts to description for YouTube Shorts eligibility
    shorts_description = f"{description}\n\n#Shorts #WhatIf #MovieTheory #FilmTheory"
    
    body = {
        "snippet": {
            "title": title[:100],
            "description": shorts_description,
            "tags": tags + ["Shorts", "WhatIf", "MovieTheory"],
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  YouTube upload: {int(status.progress() * 100)}%")
    
    video_id = response["id"]
    print(f"✅ YouTube uploaded: https://youtube.com/shorts/{video_id}")
    return video_id

# ============ INSTAGRAM UPLOADER ============
def upload_to_instagram(video_path, caption):
    """Upload to Instagram Reels"""
    try:
        from instagrapi import Client
        
        cl = Client()
        
        # Load saved session or login
        session_file = "credentials/instagram_session.json"
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(os.environ["INSTAGRAM_USER"], os.environ["INSTAGRAM_PASS"])
        else:
            cl.login(os.environ["INSTAGRAM_USER"], os.environ["INSTAGRAM_PASS"])
            cl.dump_settings(session_file)
        
        # Upload as Reel
        media = cl.clip_upload(
            video_path,
            caption=caption
        )
        
        print(f"✅ Instagram uploaded: https://instagram.com/p/{media.code}/")
        return media.pk
        
    except Exception as e:
        print(f"⚠️ Instagram upload failed: {e}")
        return None

