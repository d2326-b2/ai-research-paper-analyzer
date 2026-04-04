"""
HypoGen LLM Service Module
Handles all Google Gemini AI interactions and research paper analysis

This module provides advanced NLP functions using Google's Gemini API:
- Summary generation from research papers
- Key concept extraction and identification
- Relationship mapping between concepts
- Research gap identification
- Hypothesis generation (3 levels: basic, intermediate, advanced)
- Experiment design proposal

Author: Your Name
Date: 2024
"""

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pdf_extractor import smart_chunk

# Load API key from .env file and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


# ============= CORE LLM COMMUNICATION =============

def call_llm(prompt: str) -> str:
    """
    Send a prompt to Google Gemini and get a response.
    
    This is the base function for all LLM interactions.
    Handles API calls and basic error reporting.
    
    Args:
        prompt (str): The prompt/instruction to send to Gemini
        
    Returns:
        str: The text response from the model
        
    Raises:
        Exception: If the API call fails
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise


def safe_parse_json(raw: str) -> dict | list:
    """
    Safely parse and clean JSON responses from Gemini.
    
    Gemini sometimes returns JSON wrapped in markdown code fences
    or with smart quotes. This function handles multiple edge cases:
    - Removes markdown code fences (```)
    - Converts smart/curly quotes to straight quotes
    - Attempts intelligent quote fixing for malformed JSON
    
    Args:
        raw (str): Raw JSON string from Gemini
        
    Returns:
        dict | list: Parsed JSON object or array
        
    Raises:
        ValueError: If JSON cannot be parsed after all fix attempts
    """
    cleaned = raw.strip()

    # Remove markdown fences if present
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

    # Try to fix inner double quotes breaking JSON structure
    try:
        import re
        fixed = re.sub(r'"([^"]*)"([^,\[\]]*)"([^"]*)"', r'"\1\2\3"', cleaned)
        return json.loads(fixed)
    except:
        pass

    raise ValueError("Could not parse JSON from LLM response")


# ============= ANALYSIS FUNCTIONS =============

def generate_summary(text: str) -> str:
    """
    Generate a concise summary of the research paper.
    
    Creates a 150-200 word summary covering:
    - The problem the paper solves
    - Methods or approaches used
    - Key results and findings
    
    Args:
        text (str): Full text of the research paper
        
    Returns:
        str: Research paper summary (single paragraph)
    """
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
    """
    Extract the most important key concepts from the paper.
    
    Identifies 8-10 central concepts that are crucial to understanding
    the paper. These may include:
    - Methods, models, or algorithms
    - Datasets or data sources
    - Key variables or parameters
    - Diseases, chemicals, or biological entities
    - Techniques or methodologies
    
    Limited to 8-10 concepts to avoid knowledge graph overcrowding.
    
    Args:
        text (str): Full text of the research paper
        
    Returns:
        list: Array of concept strings (e.g., ["BERT", "NLP", "Transformer"])
    """
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
    """
    Extract relationships and connections between concepts.
    
    Creates a knowledge graph by identifying how concepts relate to each other.
    Returns relationship triples in: (subject, relation, object) format.
    
    Ensures comprehensive coverage - every concept appears in at least one relation.
    
    Args:
        text (str): Full text of the research paper
        concepts (list): List of key concepts to relate
        
    Returns:
        list: Array of relationship objects:
            [
                {"subject": "BERT", "relation": "improves", "object": "accuracy"},
                {"subject": "dataset", "relation": "trains", "object": "BERT"}
            ]
    """
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
    """
    Identify 4 key research gaps in the paper.
    
    Research gaps are areas where:
    - The paper's methodology could be improved
    - Generalizability is limited
    - Comparisons with other approaches are missing
    - Real-world applications are not addressed
    
    Multiple parsing strategies ensure robustness against API response variations.
    
    Args:
        text (str): Full text of the research paper
        
    Returns:
        list: Array of 4 gap strings describing limitations and future work
    """
    prompt = f"""You are a research reviewer. Read this paper and find 4 research gaps.

IMPORTANT RULES:
- Do NOT use any quotation marks inside the gap text
- Use simple plain sentences only
- No special characters inside the text

Research Paper:
{smart_chunk(text)}

Return ONLY this exact JSON format:
["gap one here", "gap two here", "gap three here", "gap four here"]"""

    # Attempt 1: Direct JSON parsing
    try:
        raw = call_llm(prompt)
        print(f"Raw gaps response: {raw[:200]}")
        result = safe_parse_json(raw)
        if isinstance(result, list) and len(result) > 0:
            print(f"Gaps found: {len(result)}")
            return result
    except Exception as e:
        print(f"Gaps attempt 1 failed: {e}")

    # Attempt 2: Extract via regex patterns
    try:
        import re
        matches = re.findall(r'"([^"]{20,})"', raw)
        if len(matches) >= 2:
            print(f"Gaps extracted via regex: {len(matches)}")
            return matches[:4]
    except Exception as e:
        print(f"Gaps attempt 2 failed: {e}")

    # Attempt 3: Extract via line splitting
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

    # Final fallback: Return sensible defaults
    print("Using default gaps")
    return [
        "The study uses a limited dataset which may affect generalizability",
        "The model was not tested across multiple domains or languages",
        "No comparison was made with recent state-of-the-art methods",
        "Real-world deployment and scalability were not addressed"
    ]


def generate_hypotheses(gaps: list) -> list:
    """
    Generate 3 ranked hypotheses based on identified research gaps.
    
    Creates three hypotheses at different complexity/novelty levels:
    1. BASIC - Small, incremental improvement on existing work
    2. INTERMEDIATE - Moderate novelty combining existing approaches
    3. ADVANCED - High-risk, high-reward innovative idea
    
    Each hypothesis includes rationale explaining how it addresses the gaps.
    
    Args:
        gaps (list): List of research gaps identified in the paper
        
    Returns:
        list: Array of hypothesis objects:
            [
                {
                    "level": "Basic",
                    "hypothesis": "hypothesis statement",
                    "rationale": "why this addresses the gaps"
                },
                ...
            ]
    """
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
    """
    Design structured experiment plans for testing hypotheses.
    
    For each hypothesis, proposes:
    - Clear experimental objective
    - Step-by-step methodology
    - Required data and resources
    - Metrics for evaluation
    - Expected outcomes
    
    Args:
        hypotheses (list): List of hypothesis objects to design experiments for
        
    Returns:
        list: Array of experiment plan objects:
            [
                {
                    "hypothesis": "hypothesis being tested",
                    "objective": "what this experiment aims to prove",
                    "methodology": "1. First step 2. Second step...",
                    "required_data": "Item 1 | Item 2 | Item 3",
                    "evaluation_metrics": "Metric 1 | Metric 2 | Metric 3",
                    "expected_outcome": "expected result validating hypothesis"
                }
            ]
    """
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