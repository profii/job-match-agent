import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

st.set_page_config(page_title="Job Match Assistent", layout="centered")
st.title("Job Match Assistent")

if "step" not in st.session_state:
    st.session_state.step = 0
if "vacancy_data" not in st.session_state:
    st.session_state.vacancy_data = ""
if "suitability" not in st.session_state:
    st.session_state.suitability = ""
if "improvements" not in st.session_state:
    st.session_state.improvements = ""

YOUR_GEMINI_API_KEY = 'GeminiAPIKey' # Replace with your Gemini API key

genai.configure(api_key=YOUR_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')


def parse_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def get_vacancy_data(vacancy_description):
    prompt = f"""Given the following vacancy description, extract and format the following:
1. Speciality and its required level (Junior/Mid/Senior/etc).
2. Short summary (3-5 sentences).
3. Key requirements with skills and tech stack.

Vacancy description:
{vacancy_description}
"""
    response = model.generate_content(prompt)
    return response.text

def evaluate_candidate_suitability(vacancy_data, resume_text):
    prompt = f"""Given the following vacancy data and resume, assess the candidate's suitability:
Suitability level: No matches / Require great development / Some matches / A good match / A complete match.
And explain Strengths and Weaknesses.

Vacancy data:
{vacancy_data}

Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    return response.text

def suggest_improvements(vacancy_data, resume_text):
    prompt = f"""Based on the vacancy data and the candidate's resume, suggest what they need to develop to be a better fit.
List the key skills to improve and provide 2 links to relevant courses. Make your response relevant but as brief as possible.

Vacancy data:
{vacancy_data}

Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    return response.text


with st.form("input_form"):
    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    vacancy_text = st.text_area("Paste the job description")
    submitted = st.form_submit_button("Analyze")


if submitted:
    if resume_file and vacancy_text.strip():
        with st.spinner("Reading your resume..."):
            resume_text = parse_pdf(resume_file)

    with st.chat_message("user"):
        st.markdown("I have uploaded my resume and pasted a job description.")

    with st.chat_message("assistant"):
        st.markdown("Analyzing the job description...")
        st.session_state.vacancy_data = get_vacancy_data(vacancy_text)
        st.success("✅ Job Summary")
        st.markdown(st.session_state.vacancy_data)

    with st.chat_message("assistant"):
        st.markdown("Evaluating your suitability for the role...")
        st.session_state.suitability = evaluate_candidate_suitability(st.session_state.vacancy_data, resume_text)
        st.success("✅ Suitability Analysis")
        st.markdown(st.session_state.suitability)

    with st.chat_message("assistant"):
        st.markdown("Identifying what you can improve...")
        st.session_state.improvements = suggest_improvements(st.session_state.vacancy_data, resume_text)
        st.success("✅ Development Plan")
        st.markdown(st.session_state.improvements)

else:
    st.warning("Please upload a resume and paste a job description.")


