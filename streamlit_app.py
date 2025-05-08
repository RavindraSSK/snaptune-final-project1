import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib.pyplot as plt
import wordcloud
import os

# Load Spotify credentials from Streamlit Secrets
os.environ["SPOTIPY_CLIENT_ID"] = st.secrets["SPOTIPY_CLIENT_ID"]
os.environ["SPOTIPY_CLIENT_SECRET"] = st.secrets["SPOTIPY_CLIENT_SECRET"]

st.set_page_config(page_title="🎵 SnapTune – AI Photo-to-Music", layout="centered")
st.title("🎵 SnapTune")
st.caption("Upload a photo. Let AI describe it, sense the mood, and play the perfect music.")

uploaded_file = st.file_uploader("📷 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Step 1: Caption Generation
    st.info("Generating image caption using BLIP...")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    st.success(f"🧠 Caption: {caption}")

    # Step 2: Mood Inference (DistilGPT2)
    st.info("Inferring mood from image caption...")
    theme_generator = pipeline("text-generation", model="distilgpt2")
    prompt = f"What kind of music or emotion does this describe: '{caption}'? Reply in 2-3 words."
    theme_output = theme_generator(prompt, max_new_tokens=20, do_sample=True)[0]['generated_text']
    mood_keywords = theme_output.split(":")[-1].strip()
    st.success(f"🎼 Inferred Mood: {mood_keywords}")

    # Mood Bar Chart (mock example)
    st.markdown("### 🎭 Mood Intensity Chart")
    mock_moods = ["Happy", "Sad", "Romantic", "Energetic"]
    import random
    scores = [random.randint(10, 90) for _ in mock_moods]
    fig, ax = plt.subplots()
    ax.bar(mock_moods, scores, color='skyblue')
    ax.set_ylabel("Intensity")
    st.pyplot(fig)

    # Word Cloud
    st.markdown("### ☁️ Word Cloud from Caption")
    wc = wordcloud.WordCloud(width=500, height=300, background_color='white').generate(caption)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis('off')
    st.pyplot(fig_wc)

    # Step 3: Music Recommendations
    st.markdown("### 🎧 Recommended Songs")
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    search_terms = {
        "Telugu": mood_keywords + " telugu",
        "Hindi": mood_keywords + " hindi",
        "English": mood_keywords + " english",
        "Tamil": mood_keywords + " tamil"
    }
    for lang, term in search_terms.items():
        try:
            results = sp.search(q=term + " music", limit=1, type='track')
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                st.markdown(f"**{lang}**: [{track['name']} - {track['artists'][0]['name']}]({track['external_urls']['spotify']})")
            else:
                st.warning(f"No {lang} result found.")
        except Exception as e:
            st.error(f"Spotify error for {lang}: {e}")

    # Step 4: Instagram-Style Caption & Quote
    def generate_caption(caption_text):
        words = [w for w in caption_text.split() if w.isalpha() and len(w) > 3]
        hashtags = "#" + " #".join(words)
        return caption_text.capitalize() + " 🎶📷", hashtags

    def generate_quote(text):
        if "flower" in text.lower():
            return "Let yourself bloom like the flowers."
        elif "sunset" in text.lower():
            return "Every sunset brings the promise of a new dawn."
        else:
            return "Every picture tells a story – make yours worth hearing."

    final_caption, hashtags = generate_caption(caption)
    quote = generate_quote(caption)

    st.markdown("### 📸 Social Share")
    st.text_area("Instagram Caption", value=final_caption, height=50)
    st.text_area("Hashtags", value=hashtags, height=50)
    st.markdown(f"_💬 Quote: {quote}_")
