import streamlit as st
import pdfplumber
import requests
from fpdf import FPDF
import os

# ========== FONCTION: extraire le texte depuis un PDF ==========
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

# ========== FONCTION: envoyer à GPT via OpenRouter ==========
def get_feedback_and_perfect_cv(cv_text, job_desc):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Tu es un expert en recrutement.
    Compare le CV suivant avec la description du poste ci-dessous.
    Donne :
    1. Un feedback structuré (forces, faiblesses, suggestions).
    2. Un CV parfait réécrit selon l'offre.
    3. Un pourcentage d'adéquation entre le CV et le poste.

    CV:
    {cv_text}

    Description du poste:
    {job_desc}
    """

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Tu es un expert en RH et carrière."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    result = response.json()
    return result['choices'][0]['message']['content']

# ========== FONCTION: générer un PDF depuis du texte ==========
def generate_pdf_cv(cv_text, filename="cv_parfait.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in cv_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)

# ========== INTERFACE STREAMLIT ==========
st.set_page_config(page_title="AI CV Reviewer", page_icon="📄")
st.title("🤖 AI CV Reviewer")
st.write("Téléverse ton CV et la description du poste pour un feedback et un CV parfait.")

uploaded_file = st.file_uploader("📄 Téléverse ton CV ici", type=["pdf"])
job_desc = st.text_area("📝 Description du poste", placeholder="Colle ici l'offre d'emploi")

if uploaded_file and job_desc:
    with st.spinner("🔍 Analyse et génération en cours..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        feedback = get_feedback_and_perfect_cv(extracted_text, job_desc)

    st.subheader("💬 Feedback de l'IA:")
    st.write(feedback)

    if "CV parfait:" in feedback:
        cv_parfait = feedback.split("CV parfait:")[-1].strip().split("\n\n")[0].strip()
        generate_pdf_cv(cv_parfait)

        with open("cv_parfait.pdf", "rb") as f:
            st.download_button("⬇️ Télécharger le CV parfait (PDF)", f, file_name="cv_parfait.pdf")
