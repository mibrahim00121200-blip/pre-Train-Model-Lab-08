import streamlit as st
import requests

# Put your actual Hugging Face token here
HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxx"

# Lightweight free model
API_URL = "https://api-inference.huggingface.co/models/gpt2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

st.set_page_config(
    page_title="AI Story Generator",
    page_icon="📖",
    layout="centered"
)

st.title("📖 AI Story Generator")
st.write("Generate creative stories using AI.")

story_topic = st.text_input("Story Topic")

genre = st.selectbox(
    "Genre",
    [
        "Adventure",
        "Fantasy",
        "Science Fiction",
        "Horror",
        "Mystery",
        "Comedy"
    ]
)

story_length = st.selectbox(
    "Story Length",
    [
        "Short",
        "Medium",
        "Long"
    ]
)

def generate_story(prompt):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.9,
                "do_sample": True
            }
        }

        response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=120
)
        )

        if response.status_code != 200:
            return f"API Error ({response.status_code}): {response.text}"

        result = response.json()

        if isinstance(result, list):
            return result[0].get("generated_text", "No story generated.")

        return str(result)

    except requests.exceptions.ConnectionError:
        return "Connection Error: Unable to connect to Hugging Face API."

    except requests.exceptions.Timeout:
        return "Timeout Error: API took too long to respond."

    except Exception as e:
        return f"Unexpected Error: {str(e)}"

if st.button("Generate Story"):

    if story_topic:

        prompt = f"""
Write a {story_length} {genre} story.

Topic: {story_topic}

Include:
- Interesting title
- Characters
- Plot
- Ending

Make it engaging and creative.
"""

        with st.spinner("Generating Story..."):
            story = generate_story(prompt)

        st.subheader("Generated Story")
        st.text_area(
            "Story",
            value=story,
            height=450
        )

    else:
        st.warning("Please enter a topic.")
