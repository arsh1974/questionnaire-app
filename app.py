import os
import time
import random
import streamlit as st
from openai import OpenAI, error as openai_error

# Load API key from Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No OpenAI API key found. Please set it in Streamlit Cloud Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

def generate_questions(text, level):
    prompt = f"""
    You are a teacher creating a questionnaire for students.

    Content:
    {text[:3000]}

    Create 5 {level}-level questions based on this chapter.
    Format:
    Q1.
    Q2.
    Q3.
    Q4.
    Q5.
    """

    # Retry with exponential backoff
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",   # ⚡️ smaller, cheaper, higher rate limit
                messages=[
                    {"role": "system", "content": "You are a helpful teacher."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()

        except openai_error.RateLimitError:
            wait_time = (2 ** attempt) + random.random()
            st.warning(f"⏳ OpenAI rate limit hit. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

        except openai_error.OpenAIError as e:
            st.error(f"❌ OpenAI error: {str(e)}")
            return None

    return "❌ Failed after multiple retries. Please try again later."
