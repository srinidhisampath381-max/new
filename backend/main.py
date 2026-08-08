from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from resume_processor import process_resumes

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_resumes():
    """Handle resume uploads"""
    job_description = request.form.get("job_description")
    openings = int(request.form.get("openings", 1))
    
    files = request.files.getlist("resumes")
    resume_paths = []
    
    for file in files:
        if file.filename.endswith(".pdf"):
            filename = f"{uuid.uuid4()}.pdf"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            resume_paths.append(filepath)
    
    shortlisted_resumes = process_resumes(job_description, resume_paths, openings)

    return jsonify({"shortlisted_resumes": shortlisted_resumes})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
