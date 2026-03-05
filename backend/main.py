# main.py
# Flask backend server for AI Hypothesis Generator

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

from pdf_extractor import extract_text, is_valid_pdf
from llm_service import (
    generate_summary,
    extract_concepts,
    extract_relations,
    identify_gaps,
    generate_hypotheses,
    design_experiments
)

# Initialize Flask app
# template_folder = where HTML files are stored
# static_folder   = where CSS and JS files are stored
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

CORS(app)


@app.route("/")
def home():
    """Serves the main frontend HTML page."""
    return render_template('index.html')


@app.route("/analyze", methods=["POST"])
def analyze_paper():
    """Receives a PDF file and runs the full analysis pipeline."""

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted"}), 400

    temp_path = f"temp_{file.filename}"
    file.save(temp_path)

    try:
        print("Step 1: Extracting text...")
        text = extract_text(temp_path)

        if not is_valid_pdf(text):
            return jsonify({
                "error": "This PDF is scanned or image-based."
            }), 400

        print("Step 2: Generating summary...")
        summary = generate_summary(text)

        print("Step 3: Extracting concepts...")
        concepts = extract_concepts(text)

        print("Step 4: Extracting relations...")
        relations = extract_relations(text, concepts)

        print("Step 5: Identifying gaps...")
        gaps = identify_gaps(text)

        print("Step 6: Generating hypotheses...")
        hypotheses = generate_hypotheses(gaps)

        print("Step 7: Designing experiments...")
        experiments = design_experiments(hypotheses)

        print("Done! Sending results to frontend...")

        return jsonify({
            "status": "success",
            "filename": file.filename,
            "summary": summary,
            "concepts": concepts,
            "graph": {
                "nodes": concepts,
                "edges": relations
            },
            "gaps": gaps,
            "hypotheses": hypotheses,
            "experiments": experiments
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(debug=True, port=8000)