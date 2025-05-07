# 🎵 SnapTune – AI Final Project

## 🧠 What It Does
SnapTune is an AI-powered web app that transforms an uploaded photo into a rich music and social media experience.

It:
- Generates a descriptive caption using **BLIP** (Hugging Face image captioning model)
- Infers a music mood or theme using **DistilGPT2** (text generation model)
- Recommends one song each in **Telugu, Hindi, English, and Tamil** using the **Spotify API**
- Creates an **Instagram-style caption**, relevant hashtags, and an inspirational quote

---

## 🤖 Tools & Models Used
- **BLIP** (Salesforce/blip-image-captioning-base) – for image captioning
- **DistilGPT2** – to extract mood keywords from the caption
- **Spotify API** – for multi-language music suggestions
- **Streamlit** – for the interactive web interface
- **Python Libraries** – Transformers, Spotipy, Pillow, etc.

---

## 🚀 How to Run the Project

### 🟢  Try the Live App (Streamlit Cloud) ✅  
No setup needed! Just click:

🔗 [Live Demo](https://snaptune-final-project1-7zm2adxdf3mjgvhbhrysv7.streamlit.app/)

---
or
### ⚙ Run Locally

1. Clone this repository:
```bash
git clone https://github.com/RavindraSSK/snaptune-final-project1.git
cd snaptune-final-project
