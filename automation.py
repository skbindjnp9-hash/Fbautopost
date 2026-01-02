import os
import requests
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

# ===============================
# Load environment variables
# ===============================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# ===============================
# Gemini API: Generate unique prompt
# ===============================
def generate_gemini_prompt():
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    instruction = (
        "Generate a unique, ultra-cute Good Morning or Good Night image prompt "
        "with detailed background, objects, 3D text, and integrate watermark 'Happy Happy' naturally. "
        "Include variations in color, style, wishes, sometimes date or day. "
        "Make each prompt completely unique and imaginative."
    )
    body = {"contents":[{"parts":[{"text": instruction}]}]}

    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        prompt_text = data['candidates'][0]['content']
    except Exception as e:
        print("Gemini API Error:", e)
        prompt_text = "Good Morning! Have a great day!"
    return prompt_text

# ===============================
# Image API: Generate image
# ===============================
def generate_image(prompt_text):
    payload = {
        "prompt": prompt_text,
        "size": "1024x1024"
    }
    headers = {"Authorization": f"Bearer {IMAGE_API_KEY}"}

    try:
        response = requests.post("https://api.your-image-generator.com/v1/generate", json=payload, headers=headers)
        if response.status_code == 200:
            image_url = response.json().get("url")
            return image_url
        else:
            print("Image generation failed:", response.text)
            return None
    except Exception as e:
        print("Image API Error:", e)
        return None

# ===============================
# Facebook API: Post image
# ===============================
def post_to_facebook(image_url, caption_text):
    try:
        image_data = requests.get(image_url).content
        url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/photos"
        files = {'source': image_data}
        data = {'caption': caption_text, 'access_token': FB_PAGE_TOKEN}
        response = requests.post(url, files=files, data=data)
        print("Facebook Response:", response.json())
    except Exception as e:
        print("Facebook API Error:", e)

# ===============================
# Full Automation Job
# ===============================
def automation_job():
    print(f"[{datetime.now()}] Starting automation job...")

    # Step 1: Gemini prompt
    prompt_text = generate_gemini_prompt()
    print("Generated Prompt:", prompt_text)

    # Step 2: Generate image
    image_url = generate_image(prompt_text)
    if not image_url:
        print("Skipping post due to image generation failure.\n")
        return

    # Step 3: Post to Facebook
    post_to_facebook(image_url, prompt_text)
    print(f"[{datetime.now()}] Post completed.\n")

# ===============================
# Run first job immediately (1-minute instant post)
# ===============================
automation_job()

# ===============================
# Scheduler: Every 30 minutes
# ===============================
schedule.every(30).minutes.do(automation_job)

print("Scheduler started. Next posts will run every 30 minutes...")

while True:
    schedule.run_pending()
    time.sleep(10)
