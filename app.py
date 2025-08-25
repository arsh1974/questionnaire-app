import streamlit as st
import PyPDF2
from openai import OpenAI
import os
from io import BytesIO
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to generate questions from text
def generate_questions(text, level):
    prompt = f"""
    You are a teacher creating a questionnaire for students.
    Content:
    {text[:3000]}  # limit text length

    Create 5 {level}-level questions based on this chapter.
    Format output as:
    Q1.
    Q2.
    ...
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful teacher assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Function to create Word file
def create_word(questions, level):
    doc = Document()
    doc.add_heading(f"{level} Level Questionnaire", 0)
    for q in questions.split("\n"):
        doc.add_paragraph(q)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Function to create PDF file
def create_pdf(questions, level):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [Paragraph(f"{level} Level Questionnaire", styles['Title'])]
    for q in questions.split("\n"):
        content.append(Paragraph(q, styles['Normal']))
    doc.build(content)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("📘 Teacher Questionnaire Generator")

uploaded_file = st.file_uploader("Upload Chapter PDF", type="pdf")
level = st.selectbox("Select Difficulty Level", ["Basic", "Advanced", "Expert"])

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.success("PDF uploaded and text extracted successfully!")

    if st.button("Generate Questionnaire"):
        with st.spinner("Generating questions..."):
            questions = generate_questions(text, level)
        st.subheader(f"{level} Level Questionnaire")
        st.text_area("Generated Questions", questions, height=300)

        # Download as Word
        word_file = create_word(questions, level)
        st.download_button(
            label="📥 Download as Word",
            data=word_file,
            file_name="questionnaire.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Download as PDF
        pdf_file = create_pdf(questions, level)
        st.download_button(
            label="📥 Download as PDF",
            data=pdf_file,
            file_name="questionnaire.pdf",
            mime="application/pdf"
        )

