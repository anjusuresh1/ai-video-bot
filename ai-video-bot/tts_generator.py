from gtts import gTTS
import os

def generate_voiceover(narration_list, output_path="temp_audio/voiceover.mp3"):
    """Uses Google TTS - completely FREE"""
    os.makedirs("temp_audio", exist_ok=True)
    
    # Join all narration with pauses
    full_text = ". ".join(narration_list)
    
    # Generate TTS
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(output_path)
    
    print(f"🎙️ Voiceover generated: {output_path}")
    return output_path

def generate_voiceover_segments(narration_list):
    """Generate separate audio for each scene"""
    os.makedirs("temp_audio", exist_ok=True)
    paths = []
    
    for i, text in enumerate(narration_list):
        path = f"temp_audio/segment_{i}.mp3"
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)
        paths.append(path)
    
    return paths

