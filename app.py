import streamlit as st
from groq import Groq

# 🔑 Free API key (create free at console.groq.com)
client = Groq(api_key="YOUR_GROQ_API_KEY")

st.set_page_config(
    page_title="AI Story Generator",
    page_icon="📖",
    layout="centered"
)

st.title("📖 AI Story Generator (FREE & FAST)")

story_topic = st.text_input("Enter Story Topic")

genre = st.selectbox(
    "Genre",
    ["Adventure", "Fantasy", "Science Fiction", "Horror", "Mystery", "Comedy"]
)

story_length = st.selectbox(
    "Story Length",
    ["Short", "Medium", "Long"]
)

def generate_story(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


if st.button("Generate Story"):

    if not story_topic:
        st.warning("Enter a topic first")
    else:

        prompt = f"""
Write a {story_length} {genre} story.

Topic: {story_topic}

Include:
- Title
- Characters
- Plot
- Ending

Make it engaging and creative.
"""

        with st.spinner("Generating..."):
            story = generate_story(prompt)

        st.text_area("Story", story, height=450)
