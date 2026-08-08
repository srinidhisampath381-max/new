import google.generativeai as genai
import fitz  # PyMuPDF for extracting text from PDFs
import os

# Set up Gemini API
GENAI_API_KEY = "AIzaSyAfwpxZ8tdru5fl4aam9w6_1-HgHzP4sus"
genai.configure(api_key=GENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def process_resumes(job_description, resume_paths, openings):
    """Analyze resumes using Gemini AI and return the best matches"""
    candidates = []

    for resume_path in resume_paths:
        resume_text = extract_text_from_pdf(resume_path)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an AI recruiter. Compare the following resume with the job description and rate the match percentage (0-100%).
        \n\nJob Description:\n{job_description}\n\nResume:\n{resume_text}
        \n\nProvide the matching score and a brief reason.
        """

        response = model.generate_content(prompt)
        score_text = response.text.lower()
        
        try:
            score = int(next(filter(str.isdigit, score_text.split())))
        except:
            score = 0

        candidates.append({"resume_path": resume_path, "score": score})

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
    return candidates[:openings]
