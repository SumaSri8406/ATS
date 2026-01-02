from flask import Flask, jsonify, request, render_template
import PyPDF2
import google.generativeai as genai
import os

app = Flask(__name__)

# -------------------- Gemini API Config --------------------
genai.configure(api_key=os.getenv("AIzaSyB8SG9KxLUxCNva7vAdOf2NW0u1DbLPdkc"))
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- PDF Text Extraction --------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

# -------------------- Routes --------------------

# Frontend Page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Backend Health Check (optional but useful)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Backend is running ✅",
        "message": "Use POST /analyze to analyze resume vs job description"
    })

# Resume Analysis API
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        data = request.get_json()
        job_description = data.get("job_description", "")

        pdf_path = "Resume (3).pdf"  # ensure file exists
        resume_text = extract_text_from_pdf(pdf_path)

        prompt = f"""
        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Candidate is a 3rd year B.Tech CSE student.

        Provide:
        1. ATS score out of 100
        2. Strengths
        3. Weaknesses
        4. Improvement suggestions
        """

        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "analysis": response.text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# -------------------- Run Server --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
