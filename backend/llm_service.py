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
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise

def safe_parse_json(raw: str):
    """Cleans and parses Gemini JSON response with extra fixes."""
    cleaned = raw.strip()

    # Remove markdown fences
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]

    cleaned = cleaned.strip()

    # Fix smart/curly quotes to straight quotes
    cleaned = cleaned.replace('\u201c', '"').replace('\u201d', '"')
    cleaned = cleaned.replace('\u2018', "'").replace('\u2019', "'")

    try:
        return json.loads(cleaned)
    except:
        pass

    # Fix inner double quotes breaking JSON
    # Replace inner quotes with single quotes
    try:
        import re
        # Find content between array brackets
        fixed = re.sub(r'"([^"]*)"([^,\[\]]*)"([^"]*)"', r'"\1\2\3"', cleaned)
        return json.loads(fixed)
    except:
        pass

    raise ValueError("Could not parse JSON")

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
    """Extracts 8-10 most important key concepts from the paper.
    Kept minimal to avoid knowledge graph overcrowding."""
    prompt = f"""You are a research analyst. Read this research paper and extract
ONLY the 8-10 MOST important key concepts.
These can be models, methods, datasets, techniques, variables, diseases, chemicals, or algorithms.
Keep it minimal and focused on the most important ones only.

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
    """Finds relationships between ALL concepts."""
    prompt = f"""You are a research analyst. Given these concepts: {concepts}

    IMPORTANT RULES:
    - Every concept must appear in at least ONE relation
    - No concept should be left unconnected
    - Use short action verbs: improves, uses, trains, evaluates,
      combines, extends, achieves, requires, produces, compares
    - Create exactly {len(concepts)} relationship triples

    Research Paper:
    {smart_chunk(text)}

    Return ONLY a valid JSON array. No explanation. No markdown. Just JSON.
    Example:
    [
    {{"subject": "BERT", "relation": "improves", "object": "accuracy"}},
    {{"subject": "dataset", "relation": "trains", "object": "BERT"}}
    ]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return []


def identify_gaps(text: str) -> list:
    """Identifies research gaps with robust parsing."""

    prompt = f"""You are a research reviewer. Read this paper and find 4 research gaps.

IMPORTANT RULES:
- Do NOT use any quotation marks inside the gap text
- Use simple plain sentences only
- No special characters inside the text

Research Paper:
{smart_chunk(text)}

Return ONLY this exact JSON format:
["gap one here", "gap two here", "gap three here", "gap four here"]"""

    # Attempt 1
    try:
        raw = call_llm(prompt)
        print(f"Raw gaps response: {raw[:200]}")
        result = safe_parse_json(raw)
        if isinstance(result, list) and len(result) > 0:
            print(f"Gaps found: {len(result)}")
            return result
    except Exception as e:
        print(f"Gaps attempt 1 failed: {e}")

    # Attempt 2 — manually extract lines
    try:
        import re
        # Find all text between quotes in the response
        matches = re.findall(r'"([^"]{20,})"', raw)
        if len(matches) >= 2:
            print(f"Gaps extracted via regex: {len(matches)}")
            return matches[:4]
    except Exception as e:
        print(f"Gaps attempt 2 failed: {e}")

    # Attempt 3 — split by newlines
    try:
        lines = raw.replace('[', '').replace(']', '').strip().split('\n')
        gaps = []
        for line in lines:
            clean = line.strip().strip('",').strip()
            clean = re.sub(r'^\d+[\.\)]\s*', '', clean)
            if len(clean) > 20:
                gaps.append(clean)
        if len(gaps) >= 2:
            print(f"Gaps from lines: {gaps}")
            return gaps[:4]
    except Exception as e:
        print(f"Gaps attempt 3 failed: {e}")

    # Final fallback
    print("Using default gaps")
    return [
        "The study uses a limited dataset which may affect generalizability",
        "The model was not tested across multiple domains or languages",
        "No comparison was made with recent state-of-the-art methods",
        "Real-world deployment and scalability were not addressed"
    ]

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

IMPORTANT FORMATTING RULES:
- methodology: Write as numbered steps like "1. Do this 2. Do that 3. Then this"
- required_data: Write as bullet points separated by " | " like "Dataset A | Tool B | Resource C"
- evaluation_metrics: Write as bullet points separated by " | " like "Metric 1 | Metric 2 | Metric 3"
- objective: One clear sentence
- expected_outcome: One clear sentence

Return ONLY a valid JSON array. No explanation. No markdown. Just JSON.
Format:
[
  {{
    "hypothesis": "hypothesis being tested",
    "objective": "what this experiment aims to prove",
    "methodology": "1. First step 2. Second step 3. Third step 4. Fourth step",
    "required_data": "Item 1 | Item 2 | Item 3",
    "evaluation_metrics": "Metric 1 | Metric 2 | Metric 3",
    "expected_outcome": "what result validates the hypothesis"
  }}
]"""
    raw = call_llm(prompt)
    try:
        return safe_parse_json(raw)
    except:
        return []