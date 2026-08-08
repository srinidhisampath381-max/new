import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import matplotlib.pyplot as plt
import numpy as np

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCzFl2mCS74fhpd5nCs9tr7welTPsqHuvs"
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_file):
    """Extracts text from a given PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def analyze_resume(job_desc, resume_text):
    """Uses Gemini AI to score a resume against a job description."""
    prompt = f"""
    You are an AI recruiter. Compare the following resume with the job description and rate the match percentage (0-100%).
    \n\nJob Description:\n{job_desc}\n\nResume:\n{resume_text}
    \n\nProvide only the percentage match as a number.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        score_text = response.text.strip().replace("%", "")
        return float(score_text)
    except ValueError:
        return 0.0

def generate_visualization(scores):
    """Generates a bar chart for resume similarity scores."""
    filenames = [s["filename"] for s in scores]
    values = [s["score"] for s in scores]
    
    plt.figure(figsize=(10, 6))
    plt.barh(filenames, values, color='skyblue')
    plt.xlabel("Match Percentage")
    plt.ylabel("Resume Files")
    plt.title("Resume Similarity Analysis")
    plt.xlim(0, 100)
    plt.gca().invert_yaxis()
    plt.savefig("uploads/similarity_chart.png")

def extract_candidate_details(resume_text):
    """Extracts candidate name, branch, and email from resume."""
    prompt = f"""
    Extract the candidate's name, branch of study, and email from the following resume text. Return JSON format:
    {{"name": "", "branch": "", "email": ""}}
    \n\nResume Text:\n{resume_text}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        return eval(response.text.strip())
    except Exception:
        return {"name": "Unknown", "branch": "Unknown", "email": "Unknown"}

@app.route("/upload", methods=["POST"])
def upload_resumes():
    """Handles resume uploads and returns top matching candidates."""
    try:
        job_description = request.form["job_description"]
        openings = int(request.form["openings"])
        resumes = request.files.getlist("resumes")

        if len(resumes) == 0:
            return jsonify({"error": "No resumes uploaded"}), 400

        scores = []
        candidate_details = []
        for resume in resumes:
            resume_text = extract_text_from_pdf(resume)
            score = analyze_resume(job_description, resume_text)
            details = extract_candidate_details(resume_text)
            
            scores.append({"filename": resume.filename, "score": score})
            candidate_details.append({**details, "filename": resume.filename, "score": score})

        # Sort by highest score and select top 'openings' candidates
        shortlisted = sorted(candidate_details, key=lambda x: x["score"], reverse=True)[:openings]
        generate_visualization(scores)

        return jsonify({"shortlisted_resumes": shortlisted, "chart_url": "/uploads/similarity_chart.png"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
