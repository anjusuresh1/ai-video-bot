import requests
import os
from PIL import Image
from io import BytesIO

def generate_image(prompt, scene_number, movie_title):
    """Uses Pollinations.ai - completely FREE, no API key needed"""
    
    # Enhance prompt for cinematic look
    enhanced_prompt = f"cinematic movie scene, {movie_title} style, {prompt}, dramatic lighting, 4k, emotional, film still, wide angle"
    
    # Pollinations.ai free API
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced_prompt)}?width=1080&height=1920&model=flux"
    
    response = requests.get(url, timeout=60)
    
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        # Ensure 9:16 ratio for Shorts/Reels
        img = img.resize((1080, 1920), Image.LANCZOS)
        
        os.makedirs("temp_images", exist_ok=True)
        path = f"temp_images/scene_{scene_number}.jpg"
        img.save(path, quality=95)
        return path
    else:
        # Fallback: create a dark cinematic placeholder
        return create_fallback_image(scene_number, movie_title, prompt)

def create_fallback_image(scene_number, movie_title, text):
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGB', (1080, 1920), color=(10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    # Add gradient overlay effect
    for i in range(1920):
        alpha = int(255 * (i / 1920) * 0.3)
        draw.line([(0, i), (1080, i)], fill=(20, 0, 40, alpha))
    
    # Add text
    draw.text((540, 960), movie_title, fill=(200, 160, 255), anchor="mm")
    draw.text((540, 1000), text[:50], fill=(255, 255, 255), anchor="mm")
    
    path = f"temp_images/scene_{scene_number}.jpg"
    img.save(path)
    return path

def generate_all_images(script):
    """Generate all scene images"""
    image_paths = []
    prompts = script.get("image_prompts", [])
    movie = script.get("movie", "movie")
    
    # Ensure we have enough prompts
    while len(prompts) < 7:
        prompts.append(f"{movie} dramatic cinematic scene")
    
    print("🎨 Generating AI images...")
    for i, prompt in enumerate(prompts[:7]):
        print(f"  Image {i+1}/7: {prompt[:50]}...")
        path = generate_image(prompt, i+1, movie)
        image_paths.append(path)
    
    return image_paths

