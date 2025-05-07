# 🎵 SnapTune – AI-Powered Final Project

SnapTune is an interactive AI-based music and caption recommender. You upload a photo, and it:
- Generates a caption using **BLIP (HuggingFace)**
- Infers mood with **DistilGPT2 (HuggingFace)**
- Recommends songs in 4 languages using **Spotify API**
- Creates an Instagram caption, hashtags, and a quote

## 🤖 AI Tools Used
- BLIP – Image Captioning
- DistilGPT2 – Text Generation for mood
- Spotify API – Music Recommendation

## 🛠️ How to Run
```bash
pip install -r requirements.txt
python streamlit_app.py
