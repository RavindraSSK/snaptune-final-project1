import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# 🔐 Set Spotify credentials from Streamlit secrets
os.environ['1dcc31fe1856414bb5f6166002009a60'] = st.secrets["1dcc31fe1856414bb5f6166002009a60"]
os.environ['e006ba5dd99c44f2994aafd0a62bb8e6'] = st.secrets["e006ba5dd99c44f2994aafd0a62bb8e6"]

# UI setup
st.set_page_config(page_title="SnapTune 🎵", layout="centered")
st.title("🎵 SnapTune – AI Story Music Generator")

uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # 🤖 Step 1: Caption Generation with BLIP
    st.info("Generating image caption...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    st.success(f"🧠 Caption: {caption}")

    # 💬 Step 2: Mood Inference using GPT2
    st.info("Inferring music mood...")
    theme_generator = pipeline("text-generation", model="distilgpt2")
    theme_prompt = f"What is the music mood or theme suitable for this photo description: {caption}? Respond with 2-3 keywords only."
    theme_result = theme_generator(theme_prompt, max_new_tokens=20, do_sample=True)[0]["generated_text"]
    mood_keywords = theme_result.split(":")[-1].strip()
    st.success(f"🎼 Mood/Theme: {mood_keywords}")

    # 🎧 Step 3: Song Recommendations (Telugu, Hindi, English, Tamil)
    st.subheader("🎧 Recommended Songs Based on Mood")
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    languages = {
        "Telugu": f"{mood_keywords} telugu",
        "Hindi": f"{mood_keywords} hindi",
        "English": f"{mood_keywords} english",
        "Tamil": f"{mood_keywords} tamil"
    }

    for lang, query in languages.items():
        try:
            results = sp.search(q=query + " music", limit=1, type='track')
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                st.markdown(f"**{lang}:** [{track['name']} - {track['artists'][0]['name']}]({track['external_urls']['spotify']})")
            else:
                st.warning(f"No {lang} result.")
        except Exception as e:
            st.error(f"Spotify error for {lang}: {e}")

    # 📝 Step 4: Instagram Caption + Hashtags + Quote
    def generate_caption_tags(text):
        caption_line = f"{text.capitalize()} 🎶📷"
        keywords = [w for w in text.split() if w.isalpha() and len(w) > 3]
        hashtags = "#" + " #".join(keywords)
        return caption_line, hashtags

    def generate_quote(text):
        text = text.lower()
        if "flower" in text: return "Let yourself bloom like the flowers — quietly and beautifully."
        elif "sunset" in text: return "Every sunset brings the promise of a new dawn."
        elif "beach" in text: return "The cure for anything is saltwater — sweat, tears, or the sea."
        elif "rain" in text: return "Rain is just confetti from the sky."
        else: return "Every picture tells a story — make yours worth sharing."

    final_caption, final_tags = generate_caption_tags(caption)
    final_quote = generate_quote(caption)

    st.subheader("📸 Instagram Post Generator")
    st.text_area("📝 Caption", value=final_caption, height=60)
    st.text_area("🏷️ Hashtags", value=final_tags, height=50)
    st.markdown(f"💬 **Quote:** _{final_quote}_")
