import streamlit as st
import requests
import time

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="✨ AI Story Generator",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
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

  [data-testid="stSidebar"] {
    background: rgba(13,13,26,0.95) !important;
  }

  label {
    color: #c0a0e0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
  }

  .debug-box {
    background: rgba(255,80,80,0.08);
    border: 1px solid rgba(255,80,80,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: #ff9090;
    font-family: monospace;
    margin-top: 0.5rem;
  }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">✨ AI Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Type a spark — watch a world appear</div>', unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Hugging Face Token")
    st.markdown("""
    **Free token kaise milega:**
    1. [huggingface.co](https://huggingface.co) pe jao
    2. Sign up karo (free)
    3. Settings → Access Tokens
    4. **New token** banao (READ permission kaafi hai)
    5. Neeche paste karo 👇
    """)
    hf_token = st.text_input(
        "Token paste karo",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxx",
    )

    if hf_token:
        if hf_token.startswith("hf_") and len(hf_token) > 10:
            st.success("✅ Token format sahi lag raha hai!")
        else:
            st.error("❌ Token 'hf_' se shuru hona chahiye")

    st.divider()
    st.markdown("### 🤖 Model Choose Karo")
    st.markdown("_Sabse upar wala sabse reliable hai_")

    model_choice = st.selectbox(
        "Model",
        [
            "google/flan-t5-large",
            "facebook/opt-1.3b",
            "bigscience/bloom-560m",
            "gpt2-medium",
            "distilgpt2",
        ],
        help="Yeh sab 100% free hain aur jaldi load hotay hain!"
    )

    st.divider()
    debug_mode = st.checkbox("🐛 Debug Mode (errors dekho)", value=True)

# ─── Main UI ──────────────────────────────────────────────────────────────────
prompt = st.text_area(
    "📝 Apni Story ka Idea Likho",
    placeholder="e.g. Ek jawan jadoogar ne ek purani library ke neeche chhupi kitaab dhoondh li jo waqt rokne ka raaz rakhti thi...",
    height=100,
    max_chars=400,
)

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "🎭 Genre",
        ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror",
         "Adventure", "Thriller", "Comedy", "Drama"]
    )
with col2:
    tone = st.selectbox(
        "🎨 Tone",
        ["Dramatic", "Mysterious", "Lighthearted", "Dark",
         "Inspiring", "Suspenseful", "Epic", "Romantic"]
    )

col3, col4 = st.columns(2)
with col3:
    length = st.select_slider(
        "📏 Length",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )
with col4:
    pov = st.selectbox(
        "👁️ Point of View",
        ["Third Person", "First Person", "Second Person"]
    )

# ─── Prompt Builder ───────────────────────────────────────────────────────────
def build_prompt(idea, genre, tone, length, pov):
    word_map = {"Short": 80, "Medium": 150, "Long": 250}
    words = word_map.get(length, 150)
    pov_map = {
        "Third Person": "third person",
        "First Person": "first person (I/me)",
        "Second Person": "second person (you)",
    }
    return (
        f"Write a {tone.lower()} {genre.lower()} short story in {pov_map[pov]}. "
        f"Story idea: {idea}. "
        f"Write about {words} words. Start directly with the story, no title needed."
    )

# ─── API Call with full debug ─────────────────────────────────────────────────
def call_hf_api(prompt_text, model, token, debug=False):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Different payload for different model types
    if "flan-t5" in model:
        payload = {
            "inputs": prompt_text,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.9,
                "do_sample": True,
            },
            "options": {"wait_for_model": True, "use_cache": False}
        }
    else:
        payload = {
            "inputs": prompt_text,
            "parameters": {
                "max_new_tokens": 350,
                "temperature": 0.85,
                "top_p": 0.92,
                "repetition_penalty": 1.2,
                "do_sample": True,
                "return_full_text": False,
            },
            "options": {"wait_for_model": True, "use_cache": False}
        }

    debug_info = []
    debug_info.append(f"URL: {url}")
    debug_info.append(f"Token starts with: {token[:8]}...")

    for attempt in range(4):
        try:
            debug_info.append(f"Attempt {attempt+1}: Sending request...")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            debug_info.append(f"Status Code: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                debug_info.append(f"Response type: {type(data)}")

                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "")
                    # Clean up the text
                    for tag in ["[/INST]", "</s>", "<s>", "[INST]"]:
                        if tag in text:
                            text = text.split(tag)[-1]
                    # Remove the original prompt if echoed
                    if prompt_text[:30] in text:
                        text = text.replace(prompt_text, "").strip()
                    return text.strip(), "\n".join(debug_info)

                elif isinstance(data, dict):
                    if "error" in data:
                        debug_info.append(f"API Error in response: {data['error']}")
                        return None, "\n".join(debug_info)
                    text = data.get("generated_text", str(data))
                    return text.strip(), "\n".join(debug_info)

            elif resp.status_code == 503:
                try:
                    wait_data = resp.json()
                    wait_time = wait_data.get("estimated_time", 20)
                except:
                    wait_time = 20
                debug_info.append(f"503 - Model loading, waiting {int(wait_time)}s...")
                st.toast(f"⏳ Model load ho raha hai... {int(wait_time)}s wait karo (attempt {attempt+1}/4)")
                time.sleep(min(float(wait_time), 35))
                continue

            elif resp.status_code == 401:
                debug_info.append("401 - Token invalid ya expired!")
                return None, "\n".join(debug_info)

            elif resp.status_code == 403:
                debug_info.append("403 - Token ko is model ka access nahi. Token regenerate karo.")
                return None, "\n".join(debug_info)

            elif resp.status_code == 429:
                debug_info.append("429 - Rate limit! Thoda wait karo.")
                time.sleep(30)
                continue

            else:
                debug_info.append(f"Unknown error: {resp.status_code} - {resp.text[:200]}")
                return None, "\n".join(debug_info)

        except requests.exceptions.ConnectionError as e:
            debug_info.append(f"CONNECTION ERROR: {str(e)}")
            debug_info.append("Internet check karo ya firewall/VPN try karo")
            return None, "\n".join(debug_info)

        except requests.exceptions.Timeout:
            debug_info.append(f"TIMEOUT on attempt {attempt+1}")
            if attempt < 3:
                time.sleep(10)
                continue
            return None, "\n".join(debug_info)

        except Exception as e:
            debug_info.append(f"UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
            return None, "\n".join(debug_info)

    debug_info.append("Sab attempts fail ho gaye!")
    return None, "\n".join(debug_info)


# ─── Generate Button ──────────────────────────────────────────────────────────
generate = st.button("🪄 Story Banao!")

if generate:
    if not prompt.strip():
        st.warning("✏️ Pehle story ka idea likho!")
    elif not hf_token:
        st.error("🔑 Sidebar mein Hugging Face token daalo pehle!")
    elif not hf_token.startswith("hf_"):
        st.error("❌ Token galat lag raha hai — 'hf_' se shuru hona chahiye!")
    else:
        with st.spinner("🌙 Story ban rahi hai... (30-60 seconds lag sakte hain)"):
            full_prompt = build_prompt(prompt, genre, tone, length, pov)
            story, debug_log = call_hf_api(full_prompt, model_choice, hf_token, debug_mode)

        if debug_mode:
            with st.expander("🐛 Debug Info (kya hua dekho)"):
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
            </div>
            """, unsafe_allow_html=True)

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
                md_content = f"# {genre} Story\n\n**Tone:** {tone} | **POV:** {pov}\n\n---\n\n{story}"
                st.download_button(
                    "📄 Download (.md)",
                    data=md_content,
                    file_name=f"story_{genre.lower()}_{int(time.time())}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            st.caption("💡 Dobara Generate dabao — bilkul alag story aayegi!")
        else:
            st.error("""
            ❌ Story generate nahi hui. Yeh try karo:
            
            1. **Doosra model** choose karo sidebar se (distilgpt2 sabse reliable hai)
            2. **Token check karo** — huggingface.co pe valid hai?
            3. **Thoda wait karo** aur dobara try karo (model cold start hota hai)
            4. **Debug info dekho** upar click karke
            """)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center;color:#604080;font-size:0.78rem;">'
    'Free 🤗 Hugging Face API · Streamlit · No paid model · Python 3.11'
    '</p>',
    unsafe_allow_html=True
)
