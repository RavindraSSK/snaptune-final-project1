import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Set up Streamlit UI
st.set_page_config(page_title="SnapTune 🎵", layout="centered")
st.title("🎵 SnapTune – Photo to Music Recommender")

# Upload an image
uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Load BLIP caption model
    st.info("Generating image caption using BLIP...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    st.success(f"🧠 Caption: {caption}")

    # Use GPT2 or similar to generate mood/theme
    st.info("Inferring music mood from caption...")
    theme_generator = pipeline("text-generation", model="distilgpt2")
    theme_prompt = f"Describe music mood for: {caption}. Use 2-3 keywords."
    theme_output = theme_generator(theme_prompt, max_new_tokens=20, do_sample=True)[0]["generated_text"]
    mood_keywords = theme_output.split(":")[-1].strip()
    st.success(f"🎼 Mood: {mood_keywords}")

    # Spotify setup (your keys are assumed to be in the code)
    os.environ['SPOTIPY_CLIENT_ID'] = 'your_spotify_client_id_here'
    os.environ['SPOTIPY_CLIENT_SECRET'] = 'your_spotify_client_secret_here'
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    # Search 1 song per language
    languages = {
        "Telugu": f"{mood_keywords} telugu",
        "Hindi": f"{mood_keywords} hindi",
        "English": f"{mood_keywords} english",
        "Tamil": f"{mood_keywords} tamil"
    }

    st.subheader("🎧 Recommended Songs")
    for lang, query in languages.items():
        results = sp.search(q=query + " music", limit=1, type='track')
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            st.markdown(f"**{lang}:** [{track['name']} - {track['artists'][0]['name']}]({track['external_urls']['spotify']})")
        else:
            st.warning(f"No result found for {lang}.")

    # Format caption + hashtags
    def generate_caption_tags(text):
        emojis = "🎶🌟📷💬"
        caption_line = f"{text.capitalize()}. {emojis}"
        keywords = [w for w in text.split() if w.isalpha() and len(w) > 3]
        hashtags = "#" + " #".join(keywords)
        return caption_line, hashtags

    # Quote suggestion
    def generate_quote(text):
        if "flower" in text: return "Let yourself bloom like the flowers — quietly and beautifully."
        elif "sunset" in text: return "Every sunset brings the promise of a new dawn."
        elif "beach" in text: return "The cure for anything is saltwater — sweat, tears, or the sea."
        elif "rain" in text: return "Rain is just confetti from the sky."
        else: return "Every picture tells a story — make yours worth sharing."

    caption_final, hashtags_final = generate_caption_tags(caption)
    quote_final = generate_quote(caption)

    st.subheader("📸 Instagram Content")
    st.text_area("📝 Caption", value=caption_final, height=60)
    st.text_area("🏷️ Hashtags", value=hashtags_final, height=50)
    st.markdown(f"💬 **Quote:** _{quote_final}_")
