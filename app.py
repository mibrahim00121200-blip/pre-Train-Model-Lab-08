import streamlit as st
import requests
import time

st.set_page_config(
    page_title="✨ AI Story Generator",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Inter:wght@400;500;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp {
    background: linear-gradient(135deg, #1a1025 0%, #0d0d1a 50%, #1a0d25 100%);
    min-height: 100vh;
  }
  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 6vw, 3.5rem);
    font-weight: 700;
    color: #f0c060;
    text-align: center;
    line-height: 1.1;
    margin-bottom: 0.2em;
    text-shadow: 0 0 40px rgba(240,192,96,0.3);
  }
  .hero-subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: clamp(0.95rem, 2.5vw, 1.15rem);
    color: #a070d0;
    text-align: center;
    margin-bottom: 2em;
  }
  .story-box {
    background: rgba(240,192,96,0.05);
    border: 1px solid rgba(240,192,96,0.25);
    border-left: 4px solid #f0c060;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    font-family: 'Playfair Display', serif;
    font-size: clamp(1rem, 2.2vw, 1.1rem);
    line-height: 1.85;
    color: #e8dfc8;
    white-space: pre-wrap;
    margin-top: 1rem;
  }
  .stats-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.8rem; }
  .stat-chip {
    background: rgba(160,112,208,0.15);
    border: 1px solid rgba(160,112,208,0.3);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #c0a0e0;
  }
  .stButton > button {
    background: linear-gradient(135deg, #f0c060, #d4a040) !important;
    color: #1a1025 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.65rem 2.5rem !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(240,192,96,0.25) !important;
  }
  hr { border-color: rgba(240,192,96,0.1) !important; }
  [data-testid="stSidebar"] { background: rgba(13,13,26,0.95) !important; }
  label { color: #c0a0e0 !important; font-size: 0.85rem !important; font-weight: 500 !important; }
  .info-box {
    background: rgba(96,160,240,0.08);
    border: 1px solid rgba(96,160,240,0.25);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    font-size: 0.83rem;
    color: #90c0ff;
    margin: 0.5rem 0;
    line-height: 1.6;
  }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">✨ AI Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Type a spark — watch a world appear</div>', unsafe_allow_html=True)

# ── GROQ FREE MODELS ──────────────────────────────────────────────────────────
MODELS = {
    "Llama 3.1 8B (Fast + Smart)":   "llama-3.1-8b-instant",
    "Llama 3 70B (Best Quality)":     "llama3-70b-8192",
    "Mixtral 8x7B (Creative)":        "mixtral-8x7b-32768",
    "Gemma 2 9B (Balanced)":          "gemma2-9b-it",
}

with st.sidebar:
    st.markdown("### 🔑 Groq API Key (FREE)")
    st.markdown("""
<div style="background:rgba(96,240,96,0.08);border:1px solid rgba(96,240,96,0.2);border-radius:8px;padding:0.8rem;font-size:0.82rem;color:#90e090;line-height:1.7;">
<b>Free key kaise milegi:</b><br>
1. <a href="https://console.groq.com" target="_blank" style="color:#f0c060;">console.groq.com</a> pe jao<br>
2. Sign up karo (bilkul FREE)<br>
3. <b>API Keys → Create API Key</b><br>
4. Copy karke neeche paste karo 👇<br><br>
✅ No credit card needed<br>
✅ Very fast (seconds mein story)<br>
✅ Streamlit Cloud pe kaam karta hai
</div>
""", unsafe_allow_html=True)

    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_xxxxxxxxxxxxxxxx",
    )
    if groq_key:
        if groq_key.startswith("gsk_") and len(groq_key) > 10:
            st.success("✅ Key format sahi!")
        else:
            st.warning("⚠️ Key 'gsk_' se shuru honi chahiye")

    st.divider()
    st.markdown("### 🤖 Model")
    model_label = st.selectbox("Model choose karo", list(MODELS.keys()))
    selected_model = MODELS[model_label]

# ── Main inputs ───────────────────────────────────────────────────────────────
prompt = st.text_area(
    "📝 Apni Story ka Idea Likho",
    placeholder="e.g. Ek jawan jadoogar ne ek purani library ke neeche chhupi kitaab dhoondh li jo waqt rokne ka raaz rakhti thi...",
    height=110,
    max_chars=500,
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("🎭 Genre", ["Fantasy","Sci-Fi","Mystery","Romance","Horror","Adventure","Thriller","Comedy","Drama"])
with col2:
    tone  = st.selectbox("🎨 Tone",  ["Dramatic","Mysterious","Lighthearted","Dark","Inspiring","Suspenseful","Epic","Romantic"])

col3, col4 = st.columns(2)
with col3:
    length = st.select_slider("📏 Length", options=["Short (~100 words)","Medium (~200 words)","Long (~350 words)"], value="Medium (~200 words)")
with col4:
    pov = st.selectbox("👁️ Point of View", ["Third Person","First Person","Second Person"])

lang = st.selectbox("🌐 Story Language", ["English", "Urdu (اردو)", "Hindi", "Roman Urdu"])


def build_system_prompt(genre, tone, length, pov, lang):
    word_map = {
        "Short (~100 words)":  100,
        "Medium (~200 words)": 200,
        "Long (~350 words)":   350,
    }
    words = word_map.get(length, 200)
    pov_map = {
        "Third Person": "third person (he/she/they)",
        "First Person": "first person (I/me/my)",
        "Second Person": "second person (you/your)",
    }
    lang_map = {
        "English":      "Write in English.",
        "Urdu (اردو)":  "اردو میں لکھیں۔",
        "Hindi":        "हिंदी में लिखें।",
        "Roman Urdu":   "Write in Roman Urdu (Urdu words written in English letters).",
    }
    return (
        f"You are a master storyteller. Write a compelling {tone.lower()} {genre.lower()} story "
        f"in {pov_map[pov]}. Write approximately {words} words. "
        f"Begin the story immediately — no title, no preamble, no explanation. "
        f"Just the story. {lang_map[lang]}"
    )


def call_groq(user_idea, system_prompt, model, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Write a story based on this idea: {user_idea}"},
        ],
        "temperature": 0.85,
        "max_tokens": 1024,
        "top_p": 0.92,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)

        if resp.status_code == 200:
            data = resp.json()
            story = data["choices"][0]["message"]["content"].strip()
            return story, None

        elif resp.status_code == 401:
            return None, "❌ API Key galat hai! console.groq.com pe check karo."

        elif resp.status_code == 429:
            return None, "⚠️ Rate limit aa gaya. 1 minute wait karo aur dobara try karo."

        elif resp.status_code == 400:
            err = resp.json().get("error", {}).get("message", resp.text)
            return None, f"❌ Bad request: {err}"

        else:
            return None, f"❌ Error {resp.status_code}: {resp.text[:200]}"

    except requests.exceptions.ConnectionError:
        return None, "🔌 Connection error! Internet check karo."
    except requests.exceptions.Timeout:
        return None, "⏰ Timeout! Dobara try karo."
    except Exception as e:
        return None, f"💥 Unexpected error: {str(e)}"


# ── Generate ──────────────────────────────────────────────────────────────────
generate = st.button("🪄 Story Banao!")

if generate:
    if not prompt.strip():
        st.warning("✏️ Pehle story ka idea likho!")
    elif not groq_key:
        st.error("🔑 Sidebar mein Groq API key daalo! (console.groq.com se free milegi)")
    elif not groq_key.startswith("gsk_"):
        st.error("❌ Groq key 'gsk_' se shuru honi chahiye!")
    else:
        with st.spinner(f"🌙 Story ban rahi hai ({model_label})..."):
            sys_prompt = build_system_prompt(genre, tone, length, pov, lang)
            story, error = call_groq(prompt, sys_prompt, selected_model, groq_key)

        if error:
            st.error(error)
        elif story and len(story.strip()) > 20:
            wc = len(story.split())
            st.success("✅ Story tayyar hai!")
            st.markdown(f"""
            <div class="stats-row">
              <span class="stat-chip">📖 {wc} words</span>
              <span class="stat-chip">🎭 {genre}</span>
              <span class="stat-chip">🎨 {tone}</span>
              <span class="stat-chip">👁️ {pov}</span>
              <span class="stat-chip">🌐 {lang}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "⬇️ Download (.txt)",
                    data=story,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_b:
                md = f"# {genre} Story\n\n**Tone:** {tone} | **POV:** {pov} | **Lang:** {lang}\n\n---\n\n{story}"
                st.download_button(
                    "📄 Download (.md)",
                    data=md,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            st.caption("💡 Dobara dabao — bilkul alag story aayegi!")
        else:
            st.error("Story generate nahi hui. Dobara try karo.")

st.divider()
st.markdown(
    '<p style="text-align:center;color:#604080;font-size:0.78rem;">'
    'Free ⚡ Groq API · Llama 3 · Streamlit · No paid model'
    '</p>', unsafe_allow_html=True
)
