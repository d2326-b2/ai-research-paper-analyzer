# llm_service.py
# Handles all Gemini AI calls for paper analysis

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pdf_extractor import smart_chunk

# Load API key from .env file and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def call_llm(prompt: str) -> str:
    """Sends a prompt to Gemini and returns the response text."""
    response = model.generate_content(prompt)
    return response.text


def safe_parse_json(raw: str):
    """Cleans and parses Gemini's JSON response."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


def generate_summary(text: str) -> str:
    """Generates a 150-200 word summary of the research paper."""
    prompt = f"""You are a research analyst. Read this research paper carefully.
Write a clear concise summary in 150-200 words covering:
- What problem it solves
- What method or approach it uses
- What results or findings it presents

Research Paper:
{smart_chunk(text)}

Write as a single paragraph. No bullet points."""
    return call_llm(prompt)


def extract_concepts(text: str) -> list:
    """Extracts 10-15 key concepts from the paper.
    These become the nodes in the knowledge graph."""
    prompt = f"""You are a research analyst. Read this research paper and extract
10-15 key concepts such as models, methods, datasets, techniques,
variables, diseases, chemicals, or algorithms.

Research Paper:
{smart_chunk(text)}

Return ONLY a valid JSON array of strings. No explanation. No markdown. Just JSON.
Example: ["concept1", "concept2", "concept3"]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return ["Could not extract concepts"]


def extract_relations(text: str, concepts: list) -> list:
    """Finds relationships between concepts as subject-relation-object triples.
    These become the edges in the knowledge graph."""
    prompt = f"""You are a research analyst. Given these concepts: {concepts}

Find how these concepts relate to each other in the paper.
Create 10-15 relationship triples.

Research Paper:
{smart_chunk(text)}

Return ONLY a valid JSON array. No explanation. No markdown. Just JSON.
Example:
[
  {{"subject": "BERT", "relation": "improves", "object": "accuracy"}},
  {{"subject": "dataset", "relation": "used for", "object": "training"}}
]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return []


def identify_gaps(text: str) -> list:
    """Identifies 3-4 research gaps or limitations in the paper."""
    prompt = f"""You are a critical research reviewer. Read this paper carefully.
Identify 3-4 research gaps, limitations, or unexplored areas.
Look everywhere in the paper, not just the limitations section.

Research Paper:
{smart_chunk(text)}

Return ONLY a valid JSON array of strings. No explanation. No markdown. Just JSON.
Example: ["Gap 1 description", "Gap 2 description", "Gap 3 description"]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return ["Could not identify gaps"]


def generate_hypotheses(gaps: list) -> list:
    """Generates 3 ranked hypotheses based on identified research gaps."""
    prompt = f"""You are a research scientist. Based on these research gaps: {gaps}

Generate exactly 3 ranked hypotheses:
1. Basic        - small extension of existing work
2. Intermediate - moderate improvement or combination of methods
3. Advanced     - innovative high-risk novel idea

Return ONLY a valid JSON array. No explanation. No markdown. Just JSON.
Format:
[
  {{
    "level": "Basic",
    "hypothesis": "hypothesis statement",
    "rationale": "why this gap leads to this hypothesis"
  }},
  {{
    "level": "Intermediate",
    "hypothesis": "hypothesis statement",
    "rationale": "why this gap leads to this hypothesis"
  }},
  {{
    "level": "Advanced",
    "hypothesis": "hypothesis statement",
    "rationale": "why this gap leads to this hypothesis"
  }}
]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return []


def design_experiments(hypotheses: list) -> list:
    """Designs a structured experiment plan for each hypothesis."""
    prompt = f"""You are an expert research methodologist.
Design a structured experiment plan for each hypothesis.

Hypotheses: {hypotheses}

Return ONLY a valid JSON array. No explanation. No markdown. Just JSON.
Format:
[
  {{
    "hypothesis": "hypothesis being tested",
    "objective": "what this experiment aims to prove",
    "methodology": "step by step method",
    "required_data": "what data or resources are needed",
    "evaluation_metrics": "how success will be measured",
    "expected_outcome": "what result validates the hypothesis"
  }}
]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return []

def call_llm(prompt: str) -> str:
    """Sends a prompt to Gemini and returns the response text."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Print exact error so we can see what is wrong
        print(f"Gemini API Error: {str(e)}")
        raise