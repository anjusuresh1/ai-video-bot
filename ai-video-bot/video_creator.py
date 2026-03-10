from moviepy.editor import *
from moviepy.video.fx.all import fadein, fadeout
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def add_text_overlay(clip, text, position='bottom'):
    """Add caption text to video clip"""
    txt_clip = TextClip(
        text,
        fontsize=45,
        color='white',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(900, None),
        align='center'
    ).set_duration(clip.duration)
    
    if position == 'bottom':
        txt_clip = txt_clip.set_position(('center', 0.75), relative=True)
    else:
        txt_clip = txt_clip.set_position(('center', 0.1), relative=True)
    
    return CompositeVideoClip([clip, txt_clip])

def add_title_card(title, duration=3):
    """Create dramatic title card"""
    bg = ColorClip(size=(1080, 1920), color=[5, 5, 20], duration=duration)
    
    title_txt = TextClip(
        title,
        fontsize=60,
        color='#FFD700',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(900, None),
        align='center'
    ).set_duration(duration).set_position('center')
    
    watermark = TextClip(
        "WHAT IF?",
        fontsize=90,
        color='white',
        font='Arial-Bold',
        stroke_color='#FFD700',
        stroke_width=4
    ).set_duration(duration).set_position(('center', 0.2), relative=True).set_opacity(0.15)
    
    return CompositeVideoClip([bg, watermark, title_txt]).fadein(0.5).fadeout(0.5)

def create_scene_clip(image_path, audio_path, narration_text, duration=None):
    """Create a single scene with Ken Burns effect"""
    
    # Load audio to get duration
    audio = AudioFileClip(audio_path)
    clip_duration = duration or (audio.duration + 0.5)
    
    # Load and animate image (Ken Burns zoom effect)
    img_clip = ImageClip(image_path).set_duration(clip_duration)
    
    # Ken Burns effect - slow zoom
    def zoom_effect(t):
        scale = 1 + 0.03 * (t / clip_duration)
        return scale
    
    img_clip = img_clip.resize(lambda t: zoom_effect(t))
    img_clip = img_clip.set_position('center')
    
    # Crop to 9:16
    img_clip = img_clip.crop(
        x_center=img_clip.w/2,
        y_center=img_clip.h/2,
        width=1080,
        height=1920
    )
    
    # Add dark overlay for text readability
    overlay = ColorClip(size=(1080, 1920), color=[0, 0, 0], duration=clip_duration).set_opacity(0.35)
    
    # Add caption text
    scene_with_overlay = CompositeVideoClip([img_clip, overlay])
    scene_with_text = add_text_overlay(scene_with_overlay, narration_text)
    
    # Add audio
    final_clip = scene_with_text.set_audio(audio)
    
    return final_clip.fadein(0.3).fadeout(0.3)

def add_progress_bar(clip):
    """Add a cinematic progress bar at bottom"""
    duration = clip.duration
    
    def make_bar(t):
        progress = t / duration
        bar_width = int(1080 * progress)
        img = Image.new('RGBA', (1080, 6), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, bar_width, 6], fill=(255, 215, 0, 200))
        return np.array(img)
    
    bar_clip = VideoClip(make_bar, duration=duration, ismask=False)
    bar_clip = bar_clip.set_position(('center', 1900))
    
    return CompositeVideoClip([clip, bar_clip])

def create_full_video(script, image_paths, audio_path, output_path="output_video.mp4"):
    """Assemble the complete video"""
    
    print("🎬 Assembling video...")
    clips = []
    
    # 1. Title card
    title_card = add_title_card(script['title'], duration=2)
    clips.append(title_card)
    
    # 2. Scene clips with audio segments
    audio_segments = generate_audio_segments(script['narration'])
    
    for i, (narration, img_path, audio_seg) in enumerate(
        zip(script['narration'], image_paths, audio_segments)
    ):
        if os.path.exists(img_path) and os.path.exists(audio_seg):
            scene = create_scene_clip(img_path, audio_seg, narration)
            clips.append(scene)
    
    # 3. End card
    end_card = create_end_card(script['movie'])
    clips.append(end_card)
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Add progress bar
    final_video = add_progress_bar(final_video)
    
    # Export
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    final_video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        bitrate='4000k',
        audio_bitrate='192k',
        threads=4,
        preset='fast'
    )
    
    print(f"✅ Video created: {output_path}")
    return output_path

def create_end_card(movie_title):
    bg = ColorClip(size=(1080, 1920), color=[5, 5, 20], duration=3)
    
    subscribe_txt = TextClip(
        "LIKE & FOLLOW\nfor more What If scenarios!",
        fontsize=55,
        color='white',
        font='Arial-Bold',
        align='center',
        method='caption',
        size=(900, None)
    ).set_duration(3).set_position('center')
    
    return CompositeVideoClip([bg, subscribe_txt]).fadein(0.5)

def generate_audio_segments(narration_list):
    """Generate audio for each narration segment"""
    from gtts import gTTS
    os.makedirs("temp_audio", exist_ok=True)
    paths = []
    for i, text in enumerate(narration_list):
        path = f"temp_audio/seg_{i}.mp3"
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)
        paths.append(path)
    return paths

