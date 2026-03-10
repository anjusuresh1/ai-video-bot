import google.generativeai as genai
import json
import random
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_todays_topic():
    with open("topics.json") as f:
        data = json.load(f)
    
    all_scenarios = []
    for movie in data["movies"]:
        for scenario in movie["scenarios"]:
            all_scenarios.append({
                "movie": movie["title"],
                "scenario": scenario
            })
    
    # Pick based on day to avoid repeats
    from datetime import datetime
    day_index = datetime.now().timetuple().tm_yday % len(all_scenarios)
    return all_scenarios[day_index]

def generate_script(topic):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Create a SHORT, ENGAGING YouTube Shorts script (60 seconds max) for this topic:
    Movie/Show: {topic['movie']}
    Scenario: {topic['scenario']}
    
    FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
    TITLE: [Catchy title with emoji]
    HOOK: [First 5 seconds - shocking question to grab attention]
    SCENE_1: [10-second narration for scene 1]
    SCENE_2: [10-second narration for scene 2]  
    SCENE_3: [10-second narration for scene 3]
    SCENE_4: [10-second narration for scene 4]
    SCENE_5: [10-second narration for scene 5]
    ENDING: [5-second dramatic conclusion]
    CAPTION: [Instagram caption with 10 relevant hashtags]
    IMAGE_PROMPTS: [5 image descriptions for each scene, separated by |]
    
    Make it dramatic, emotional, and shareable. Use present tense narration.
    Keep total narration under 150 words.
    """
    
    response = model.generate_content(prompt)
    return parse_script(response.text, topic)

def parse_script(raw_text, topic):
    lines = raw_text.strip().split('\n')
    script = {
        "movie": topic['movie'],
        "scenario": topic['scenario'],
        "title": "",
        "narration": [],
        "caption": "",
        "image_prompts": []
    }
    
    for line in lines:
        if line.startswith("TITLE:"):
            script["title"] = line.replace("TITLE:", "").strip()
        elif line.startswith("HOOK:"):
            script["narration"].append(line.replace("HOOK:", "").strip())
        elif line.startswith("SCENE_"):
            script["narration"].append(line.split(":", 1)[1].strip())
        elif line.startswith("ENDING:"):
            script["narration"].append(line.replace("ENDING:", "").strip())
        elif line.startswith("CAPTION:"):
            script["caption"] = line.replace("CAPTION:", "").strip()
        elif line.startswith("IMAGE_PROMPTS:"):
            prompts = line.replace("IMAGE_PROMPTS:", "").strip()
            script["image_prompts"] = [p.strip() for p in prompts.split("|")]
    
    return script

if __name__ == "__main__":
    topic = get_todays_topic()
    script = generate_script(topic)
    print(json.dumps(script, indent=2))

