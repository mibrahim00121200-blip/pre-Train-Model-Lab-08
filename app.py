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
  .debug-box {
    background: rgba(255,80,80,0.08);
    border: 1px solid rgba(255,80,80,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: #ff9090;
    font-family: monospace;
    margin-top: 0.5rem;
    white-space: pre-wrap;
    word-break: break-all;
  }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">✨ AI Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Type a spark — watch a world appear</div>', unsafe_allow_html=True)

# ── MODELS: using router URL which works on Streamlit Cloud ──────────────────
MODELS = {
    "Mistral 7B (Best Quality)":    "mistralai/Mistral-7B-Instruct-v0.3",
    "Zephyr 7B (Fast)":             "HuggingFaceH4/zephyr-7b-beta",
    "Flan-T5 Large (Lightweight)":  "google/flan-t5-large",
    "OPT 1.3B (Backup)":            "facebook/opt-1.3b",
    "DistilGPT2 (Always Works)":    "distilgpt2",
}

with st.sidebar:
    st.markdown("### 🔑 Hugging Face Token")
    st.markdown("""
**Free token kaise milega:**
1. [huggingface.co](https://huggingface.co) pe jao
2. Sign up (free)
3. Settings → Access Tokens
4. **New token** → READ permission → Copy
""")
    hf_token = st.text_input("Token paste karo", type="password", placeholder="hf_xxxxxxxxxxxxxxxx")
    if hf_token:
        if hf_token.startswith("hf_") and len(hf_token) > 10:
            st.success("✅ Token format sahi!")
        else:
            st.error("❌ 'hf_' se shuru hona chahiye")

    st.divider()
    st.markdown("### 🤖 Model")
    model_label = st.selectbox("Model choose karo", list(MODELS.keys()))
    selected_model = MODELS[model_label]

    st.divider()
    debug_mode = st.checkbox("🐛 Debug Mode", value=True)

# ── Main inputs ───────────────────────────────────────────────────────────────
prompt = st.text_area(
    "📝 Apni Story ka Idea Likho",
    placeholder="e.g. Ek jawan jadoogar ne ek purani library ke neeche chhupi kitaab dhoondh li...",
    height=100,
    max_chars=400,
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("🎭 Genre", ["Fantasy","Sci-Fi","Mystery","Romance","Horror","Adventure","Thriller","Comedy","Drama"])
with col2:
    tone  = st.selectbox("🎨 Tone",  ["Dramatic","Mysterious","Lighthearted","Dark","Inspiring","Suspenseful","Epic","Romantic"])

col3, col4 = st.columns(2)
with col3:
    length = st.select_slider("📏 Length", options=["Short","Medium","Long"], value="Medium")
with col4:
    pov = st.selectbox("👁️ Point of View", ["Third Person","First Person","Second Person"])


def build_prompt(idea, genre, tone, length, pov):
    word_map = {"Short": 80, "Medium": 150, "Long": 250}
    words = word_map.get(length, 150)
    pov_map = {"Third Person": "third person", "First Person": "first person (I/me)", "Second Person": "second person (you)"}
    return (
        f"Write a {tone.lower()} {genre.lower()} short story in {pov_map[pov]}. "
        f"Story idea: {idea}. "
        f"Write about {words} words. Start the story directly."
    )


def call_hf_api(prompt_text, model_id, token):
    """
    Try 3 different URL patterns that work on Streamlit Cloud.
    """
    debug = []

    # ── URL pattern 1: new router endpoint ───────────────────────────────────
    urls_to_try = [
        f"https://router.huggingface.co/hf-inference/models/{model_id}",
        f"https://api-inference.huggingface.co/models/{model_id}",
        f"https://huggingface.co/api/models/{model_id}",
    ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-use-cache": "0",
    }

    is_t5 = "t5" in model_id.lower() or "flan" in model_id.lower()

    payload = {
        "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 300 if is_t5 else 400,
            "temperature": 0.9,
            "do_sample": True,
            "top_p": 0.92,
            "repetition_penalty": 1.2,
            "return_full_text": False,
        },
        "options": {
            "wait_for_model": True,
            "use_cache": False,
        }
    }
    if is_t5:
        payload["parameters"].pop("return_full_text", None)

    for url in urls_to_try:
        debug.append(f"\n── Trying: {url}")
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                debug.append(f"   Attempt {attempt+1} → Status: {resp.status_code}")

                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        text = data[0].get("generated_text", "")
                    elif isinstance(data, dict):
                        text = data.get("generated_text", "")
                        if "error" in data:
                            debug.append(f"   API error: {data['error']}")
                            break
                    else:
                        text = str(data)

                    # Clean echoed prompt
                    for tag in ["[/INST]", "</s>", "<s>", "[INST]"]:
                        if tag in text:
                            text = text.split(tag)[-1]
                    if len(prompt_text) > 30 and prompt_text[:40] in text:
                        text = text[text.find(prompt_text[:40]) + len(prompt_text):]

                    text = text.strip()
                    if len(text) > 30:
                        debug.append(f"   ✅ SUCCESS! Got {len(text.split())} words")
                        return text, "\n".join(debug)

                elif resp.status_code == 503:
                    try:
                        wait = resp.json().get("estimated_time", 20)
                    except:
                        wait = 20
                    debug.append(f"   503 - Model loading, waiting {int(wait)}s...")
                    st.toast(f"⏳ Model load ho raha hai... {int(wait)}s (attempt {attempt+1}/3)")
                    time.sleep(min(float(wait), 35))
                    continue

                elif resp.status_code == 401:
                    debug.append("   ❌ 401 - Token invalid!")
                    return None, "\n".join(debug)

                elif resp.status_code == 403:
                    debug.append("   ❌ 403 - Token ka access nahi. Naya token banao.")
                    return None, "\n".join(debug)

                elif resp.status_code == 429:
                    debug.append("   ⚠️ 429 - Rate limit. 30s wait...")
                    time.sleep(30)
                    continue

                else:
                    debug.append(f"   ❌ {resp.status_code}: {resp.text[:150]}")
                    break

            except requests.exceptions.ConnectionError as e:
                err = str(e)
                debug.append(f"   🔌 Connection Error: {err[:200]}")
                break  # try next URL

            except requests.exceptions.Timeout:
                debug.append(f"   ⏰ Timeout on attempt {attempt+1}")
                time.sleep(5)
                continue

            except Exception as e:
                debug.append(f"   💥 Unexpected: {type(e).__name__}: {str(e)[:150]}")
                break

    debug.append("\n❌ Sab URLs fail ho gaye.")
    return None, "\n".join(debug)


# ── Generate ──────────────────────────────────────────────────────────────────
generate = st.button("🪄 Story Banao!")

if generate:
    if not prompt.strip():
        st.warning("✏️ Pehle story ka idea likho!")
    elif not hf_token:
        st.error("🔑 Sidebar mein HF token daalo!")
    elif not hf_token.startswith("hf_"):
        st.error("❌ Token 'hf_' se shuru hona chahiye!")
    else:
        with st.spinner("🌙 Story ban rahi hai... (30-90 sec lag sakte hain)"):
            full_prompt = build_prompt(prompt, genre, tone, length, pov)
            story, debug_log = call_hf_api(full_prompt, selected_model, hf_token)

        if debug_mode:
            with st.expander("🐛 Debug Info"):
                st.markdown(f'<div class="debug-box">{debug_log}</div>', unsafe_allow_html=True)

        if story and len(story.strip()) > 20:
            wc = len(story.split())
            st.success("✅ Story tayyar hai!")
            st.markdown(f"""
            <div class="stats-row">
              <span class="stat-chip">📖 {wc} words</span>
              <span class="stat-chip">🎭 {genre}</span>
              <span class="stat-chip">🎨 {tone}</span>
              <span class="stat-chip">👁️ {pov}</span>
            </div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button("⬇️ Download (.txt)", data=story,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.txt",
                    mime="text/plain", use_container_width=True)
            with col_b:
                md = f"# {genre} Story\n\n**Tone:** {tone} | **POV:** {pov}\n\n---\n\n{story}"
                st.download_button("📄 Download (.md)", data=md,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.md",
                    mime="text/markdown", use_container_width=True)
            st.caption("💡 Dobara dabao — bilkul alag story aayegi!")

        else:
            st.error("❌ Story nahi aayi. Neeche debug info dekho aur **doosra model** try karo.")
            st.info("""
**Yeh try karo:**
- 🔄 **DistilGPT2** model choose karo sidebar se (sabse reliable)
- ✅ Token [huggingface.co](https://huggingface.co/settings/tokens) pe valid hai?
- 🌐 Kya tumhara internet chal raha hai?
- ⏳ 1 minute wait karo aur dobara try karo
""")

st.divider()
st.markdown(
    '<p style="text-align:center;color:#604080;font-size:0.78rem;">'
    'Free 🤗 HF API · Streamlit · No paid model · Python 3.11'
    '</p>', unsafe_allow_html=True
)
