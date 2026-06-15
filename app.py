import streamlit as st
import requests
import json
import time

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="✨ AI Story Generator",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Inter:wght@400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Dark parchment background */
  .stApp {
    background: linear-gradient(135deg, #1a1025 0%, #0d0d1a 50%, #1a0d25 100%);
    min-height: 100vh;
  }

  /* Hero title */
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
    letter-spacing: 0.02em;
  }

  /* Cards */
  .card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(240,192,96,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
  }

  /* Genre pills */
  .genre-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #a070d0;
    margin-bottom: 0.5rem;
  }

  /* Story output box */
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

  /* Stats bar */
  .stats-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
  }
  .stat-chip {
    background: rgba(160,112,208,0.15);
    border: 1px solid rgba(160,112,208,0.3);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #c0a0e0;
  }

  /* Streamlit widget overrides */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea,
  .stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(240,192,96,0.2) !important;
    border-radius: 10px !important;
    color: #e8dfc8 !important;
    font-family: 'Inter', sans-serif !important;
  }

  .stSlider > div > div > div > div {
    background: #f0c060 !important;
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
    transition: transform 0.15s, box-shadow 0.15s !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 20px rgba(240,192,96,0.25) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(240,192,96,0.4) !important;
  }

  label, .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label {
    color: #c0a0e0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
  }

  /* Divider */
  hr { border-color: rgba(240,192,96,0.1) !important; }

  /* Sidebar */
  .css-1d391kg, [data-testid="stSidebar"] {
    background: rgba(13,13,26,0.95) !important;
  }

  /* Mobile spacing */
  @media (max-width: 640px) {
    .card { padding: 1rem; }
    .story-box { padding: 1rem 1.2rem; }
  }
</style>
""", unsafe_allow_html=True)


# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">✨ AI Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Type a spark — watch a world appear</div>', unsafe_allow_html=True)

# ─── Sidebar: API Key ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Setup")
    hf_token = st.text_input(
        "Hugging Face Token (Free)",
        type="password",
        placeholder="hf_xxxxxxxxxxxx",
        help="Get yours FREE at huggingface.co/settings/tokens"
    )
    st.markdown("""
    **How to get free token:**
    1. Go to [huggingface.co](https://huggingface.co)
    2. Sign up (free)
    3. Settings → Access Tokens
    4. Create token → paste here
    """)
    st.divider()
    st.markdown("### 🤖 Model")
    model_choice = st.selectbox(
        "Story Model",
        [
            "mistralai/Mistral-7B-Instruct-v0.3",
            "HuggingFaceH4/zephyr-7b-beta",
            "tiiuae/falcon-7b-instruct",
        ],
        help="All free on Hugging Face!"
    )


# ─── Main Input Card ───────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)

prompt = st.text_area(
    "📝 Your Story Idea",
    placeholder="e.g. A young wizard discovers a hidden library beneath Hogwarts that contains spells forbidden by time itself...",
    height=100,
    max_chars=500,
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "🎭 Genre",
        ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Adventure",
         "Thriller", "Historical Fiction", "Comedy", "Drama"]
    )
with col2:
    tone = st.selectbox(
        "🎨 Tone",
        ["Dramatic", "Mysterious", "Lighthearted", "Dark", "Inspiring",
         "Suspenseful", "Whimsical", "Epic", "Romantic", "Melancholic"]
    )

col3, col4 = st.columns(2)
with col3:
    length = st.select_slider(
        "📏 Story Length",
        options=["Short (100 words)", "Medium (200 words)", "Long (350 words)"],
        value="Medium (200 words)"
    )
with col4:
    pov = st.selectbox(
        "👁️ Point of View",
        ["Third Person", "First Person", "Second Person"]
    )

st.markdown('</div>', unsafe_allow_html=True)


# ─── Generate Button ───────────────────────────────────────────────────────────
generate = st.button("🪄 Generate My Story")


# ─── Story Generation ──────────────────────────────────────────────────────────
def build_prompt(user_idea, genre, tone, length, pov):
    word_map = {
        "Short (100 words)": 100,
        "Medium (200 words)": 200,
        "Long (350 words)": 350,
    }
    words = word_map.get(length, 200)
    pov_guide = {
        "Third Person": "Write in third person (he/she/they).",
        "First Person": "Write in first person (I/me/my).",
        "Second Person": "Write in second person (you/your).",
    }

    system = (
        f"You are a master storyteller. Write compelling, vivid {genre} stories. "
        f"Keep the tone {tone.lower()}. {pov_guide[pov]} "
        f"Write approximately {words} words. Begin the story immediately — no titles, no preamble."
    )
    user = f"Write a {genre.lower()} story based on this idea:\n\n{user_idea}"

    # Mistral / Zephyr instruct format
    return f"<s>[INST] {system}\n\n{user} [/INST]"


def call_hf_api(prompt_text, model, token):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.85,
            "top_p": 0.92,
            "repetition_penalty": 1.15,
            "do_sample": True,
            "return_full_text": False,
        },
        "options": {"wait_for_model": True},
    }

    for attempt in range(3):
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code == 503:
            wait = resp.json().get("estimated_time", 20)
            st.toast(f"Model loading… waiting {int(wait)}s (attempt {attempt+1}/3)")
            time.sleep(min(wait, 30))
            continue
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
                # Strip prompt echo if present
                for tag in ["[/INST]", "</s>"]:
                    if tag in text:
                        text = text.split(tag)[-1]
                return text.strip()
        else:
            return f"❌ API Error {resp.status_code}: {resp.text}"

    return "⚠️ Model took too long to load. Please try again in a moment."


if generate:
    if not prompt.strip():
        st.warning("✏️ Please enter a story idea first!")
    elif not hf_token:
        st.warning("🔑 Add your free Hugging Face token in the sidebar!")
    else:
        with st.spinner("🌙 Weaving your story…"):
            full_prompt = build_prompt(prompt, genre, tone, length, pov)
            story = call_hf_api(full_prompt, model_choice, hf_token)

        if story.startswith("❌") or story.startswith("⚠️"):
            st.error(story)
        else:
            # Word count
            wc = len(story.split())
            char_count = len(story)

            st.success("✅ Your story is ready!")

            # Stats
            st.markdown(f"""
            <div class="stats-row">
              <span class="stat-chip">📖 {wc} words</span>
              <span class="stat-chip">🎭 {genre}</span>
              <span class="stat-chip">🎨 {tone}</span>
              <span class="stat-chip">👁️ {pov}</span>
            </div>
            """, unsafe_allow_html=True)

            # Story display
            st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)

            # Download
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "⬇️ Download Story (.txt)",
                    data=story,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_b:
                md_content = f"# {genre} Story\n\n**Tone:** {tone} | **POV:** {pov}\n\n---\n\n{story}"
                st.download_button(
                    "📄 Download as Markdown",
                    data=md_content,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            # Regenerate tip
            st.caption("💡 Tip: Click generate again for a completely different story!")


# ─── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center;color:#604080;font-size:0.78rem;">'
    'Powered by 🤗 Hugging Face Free API · Built with Streamlit · No paid model used'
    '</p>',
    unsafe_allow_html=True
)
