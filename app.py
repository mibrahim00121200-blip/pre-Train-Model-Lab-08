
import streamlit as st
import requests

# Replace with your Hugging Face Token
HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN"

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

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

    payload = {
        "inputs": prompt
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]

    return str(result)

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
            "",
            value=story,
            height=450
        )

    else:
        st.warning("Please enter a topic.")
