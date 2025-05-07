import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# ✅ Set Spotify API keys using Streamlit Cloud secrets
os.environ["SPOTIPY_CLIENT_ID"] = st.secrets["SPOTIPY_CLIENT_ID"]
os.environ["SPOTIPY_CLIENT_SECRET"] = st.secrets["SPOTIPY_CLIENT_SECRET"]

# Set up Streamlit page
st.set_page_config(page_title="SnapTune 🎵", layout="centered")
st.title("🎵 SnapTune – AI Music & Caption Recommender")

# Upload an image
uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # ✨ Step 1: Generate image caption using BLIP
    st.info("Generating image caption...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    st.success(f"🧠 Caption: {caption}")

    # ✨ Step 2: Generate mood/theme with DistilGPT2
    st.info("Inferring mood from caption...")
    theme_generator = pipeline("text-generation", model="distilgpt2")
    theme_prompt = f"What kind of music suits this caption: '{caption}'? Use 2-3 words only."
    theme_output = theme_generator(theme_prompt, max_new_tokens=20, do_sample=True)[0]["generated_text"]
    mood_keywords = theme_output.split(":")[-1].strip()
    st.success(f"🎼 Inferred Mood: {mood_keywords}")

    # ✨ Step 3: Recommend songs using Spotify API
    st.subheader("🎧 Music Recommendations")
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
                st.warning(f"No results found for {lang}.")
        except Exception as e:
            st.error(f"Spotify error for {lang}: {e}")

            # ✨ Step 4: Instagram Caption + Hashtags + Quote
    def generate_instagram_caption(caption_text):
        if not caption_text:
            caption_text = "no caption"
        emoji = "🎶📷"
        words = [w for w in caption_text.split() if w.isalpha() and len(w) > 3]
        hashtags = "#" + " #".join(words) if words else "#music"
        return caption_text.capitalize() + " " + emoji, hashtags
#step4 insta
    def generate_quote(caption_text):
        text = (caption_text or "").lower()
        if "flower" in text:
            return "Let yourself bloom like the flowers — quietly and beautifully."
        elif "sunset" in text:
            return "Every sunset brings the promise of a new dawn."
        elif "beach" in text:
            return "The cure for anything is saltwater — sweat, tears, or the sea."
        elif "rain" in text:
            return "Rain is just confetti from the sky."
        else:
            return "Every picture tells a story — make yours worth sharing."

    try:
        final_caption, final_hashtags = generate_instagram_caption(caption)
        final_quote = generate_quote(caption)

        st.subheader("📸 Instagram Caption & Quote")
        st.text_area("📝 Caption", value=final_caption or "No caption generated", height=70)
        st.text_area("🏷️ Hashtags", value=final_hashtags or "#music", height=50)
        st.markdown(f"💬 **Quote:** _{final_quote}_")
    except Exception as e:
        st.error(f"⚠️ Failed to generate social content: {e}")

