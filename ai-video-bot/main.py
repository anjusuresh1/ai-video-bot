#!/usr/bin/env python3
"""
AI "What If" Video Bot
Generates and posts daily videos to YouTube Shorts + Instagram
"""

import os
import json
import shutil
from datetime import datetime
from script_generator import get_todays_topic, generate_script
from image_generator import generate_all_images
from video_creator import create_full_video
from uploader import upload_to_youtube, upload_to_instagram

def cleanup_temp_files():
    """Remove temp files to save space"""
    for folder in ["temp_images", "temp_audio"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    print("🧹 Temp files cleaned")

def log_video(script, youtube_id, instagram_id):
    """Log posted videos to avoid repeats"""
    log_file = "posted_videos.json"
    log = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            log = json.load(f)
    
    log.append({
        "date": datetime.now().isoformat(),
        "scenario": script["scenario"],
        "movie": script["movie"],
        "youtube_id": youtube_id,
        "instagram_id": str(instagram_id)
    })
    
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)

def main():
    print("=" * 50)
    print(f"🎬 AI Video Bot Starting - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    try:
        # Step 1: Get today's topic
        print("\n📖 Step 1: Getting today's topic...")
        topic = get_todays_topic()
        print(f"  Movie: {topic['movie']}")
        print(f"  Scenario: {topic['scenario']}")
        
        # Step 2: Generate script
        print("\n✍️  Step 2: Generating AI script...")
        script = generate_script(topic)
        print(f"  Title: {script['title']}")
        
        # Step 3: Generate images
        print("\n🎨 Step 3: Generating AI images...")
        image_paths = generate_all_images(script)
        
        # Step 4: Create video
        print("\n🎬 Step 4: Creating video...")
        today = datetime.now().strftime("%Y%m%d")
        video_path = f"outputs/video_{today}.mp4"
        os.makedirs("outputs", exist_ok=True)
        create_full_video(script, image_paths, None, video_path)
        
        # Step 5: Upload to YouTube
        print("\n📺 Step 5: Uploading to YouTube Shorts...")
        tags = [script['movie'].replace(" ", ""), "WhatIf", "MovieTheory", "FilmTheory", "Shorts"]
        youtube_id = upload_to_youtube(
            video_path,
            script['title'],
            script['caption'],
            tags
        )
        
        # Step 6: Upload to Instagram
        print("\n📸 Step 6: Uploading to Instagram Reels...")
        instagram_id = upload_to_instagram(video_path, script['caption'])
        
        # Step 7: Log and cleanup
        log_video(script, youtube_id, instagram_id)
        cleanup_temp_files()
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS! Daily video posted!")
        print(f"  YouTube: https://youtube.com/shorts/{youtube_id}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()

