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
api_key = os.getenv("GEMINI_API_KEY")

# Flag to track if API key is valid (used to trigger fallback)
api_key_error = False
model = None

# Debug: Check if API key is loaded
if not api_key:
    print("⚠️  ERROR: GEMINI_API_KEY not found in .env file!")
    api_key_error = True
else:
    print(f"✓ API Key loaded (length: {len(api_key)})")
    if api_key.startswith("AQ."):
        print("⚠️  WARNING: API key has 'AQ.' prefix - this is likely INVALID!")
        print("   Get a valid key from: https://aistudio.google.com/apikey")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    print("✓ Gemini model configured successfully")
except Exception as e:
    print(f"⚠️  Warning: Gemini configuration failed: {str(e)}")
    print("Will use fallback data for all requests")
    api_key_error = True


# ============= CORE LLM COMMUNICATION =============

def call_llm(prompt: str) -> str:
    """
    Send a prompt to Google Gemini and get a response.
    
    This is the base function for all LLM interactions.
    Handles API calls and specific error reporting.
    Uses fallback for API key errors specifically.
    
    Args:
        prompt (str): The prompt/instruction to send to Gemini
        
    Returns:
        str: The text response from the model
        
    Raises:
        Exception: If the API call fails, especially for API key errors
    """
    global api_key_error
    
    # If we already detected an API key error, immediately fail to trigger fallback
    if api_key_error or model is None:
        raise Exception("API key not valid. Using fallback data.")
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        print(f"Gemini API Error: {error_str}")
        
        # Check if this is a quota/rate limit error
        if "quota" in error_str.lower() or "rate_limit" in error_str.lower() or "429" in error_str:
            print("⚠️  QUOTA EXCEEDED - Switching to fallback data")
            print("   Free tier limits: 60 requests/minute")
            print("   Solution: Wait a minute or upgrade to paid plan")
            raise Exception(f"API quota exceeded: {error_str}. Using fallback data.")
        
        # Check if this is an API key error
        if "API_KEY_INVALID" in error_str or "API key" in error_str or "not valid" in error_str.lower():
            api_key_error = True
            print("⚠️  API Key Error Detected - Switching to fallback data for all requests")
            raise Exception(f"API key error: {error_str}. Using fallback data.")
        else:
            # For other errors, re-raise them
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


def extract_title(text: str) -> str:
    """
    Extract or generate a meaningful title for the research paper.
    
    Tries to find the paper's actual title in the first few lines,
    or generates one based on the paper's main topic and contribution.
    
    Args:
        text (str): Full text of the research paper
        
    Returns:
        str: Paper title (actual or generated)
    """
    # Try to extract actual title from first few lines
    lines = text.split('\n')[:20]
    first_section = '\n'.join(lines)
    
    # Look for title-like patterns (capitalized, short lines)
    for line in lines:
        line_clean = line.strip()
        if (2 < len(line_clean) < 200 and 
            line_clean.isupper() and 
            len(line_clean.split()) >= 3):
            return line_clean
    
    # If no title found, generate one from content
    prompt = f"""You are a research analyst. Read this research paper excerpt and generate a concise, descriptive title.

The title should:
- Be 5-12 words long
- Be specific to the paper's main contribution
- Be professional and academic in tone
- Avoid generic words like "Analysis" or "Study"

Research Paper Excerpt:
{smart_chunk(text)}

Return ONLY the title text, nothing else. No quotes, no explanation."""
    
    try:
        title = call_llm(prompt).strip().strip('"\'')
        # Clean up the title
        title = title.replace('\n', ' ').strip()
        # If title is too long or too short, use a default
        if len(title) < 5 or len(title) > 200:
            return "Research Paper Analysis"
        return title
    except:
        return "Research Paper Analysis"


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
    def clean_text(text):
        """Remove smart quotes and special characters from text"""
        if not text:
            return ""
        text = str(text)
        # Replace ALL types of smart quotes and special Unicode characters
        text = text.replace('"', '"').replace('"', '"')  # Unicode smart double quotes
        text = text.replace(''', "'").replace(''', "'")  # Unicode smart single quotes
        text = text.replace('–', '-').replace('—', '-')  # en-dash and em-dash
        text = text.replace('…', '...')  # ellipsis
        # Remove any remaining non-ASCII characters
        text = ''.join(c if ord(c) < 128 or c.isspace() else '' for c in text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text.strip()
    
    prompt = f"""You are a research analyst building a knowledge graph for a research paper.

Given these key concepts: {concepts}

Create exactly {len(concepts)} relationship triples forming a well-connected knowledge graph.

STRICT RULES:
1. Every concept MUST appear in at least one relation (as subject or object)
2. Use ONLY these short verb phrases: improves, uses, trains, evaluates, combines, extends, achieves, requires, produces, compares, applies, enables, validates, measures, generates
3. Relations must reflect actual relationships described in the research paper
4. No self-loops (subject must differ from object)
5. Build a connected graph — concepts should chain together, not be isolated pairs

Research Paper:
{smart_chunk(text)}

Return ONLY a valid JSON array. No explanation. No markdown. Example:
[
  {{"subject": "BERT", "relation": "improves", "object": "accuracy"}},
  {{"subject": "dataset", "relation": "trains", "object": "BERT"}}
]"""
    raw = call_llm(prompt)
    try:
        relations = safe_parse_json(raw)
        # Clean the text in each relation to remove smart quotes
        cleaned_relations = []
        for rel in relations:
            if isinstance(rel, dict):
                cleaned_relations.append({
                    'subject': clean_text(rel.get('subject', 'Unknown')),
                    'relation': clean_text(rel.get('relation', 'relates to')),
                    'object': clean_text(rel.get('object', 'Unknown'))
                })
        return cleaned_relations if cleaned_relations else []
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
    prompt = f"""You are a senior research reviewer analyzing a paper to identify critical research gaps and limitations.

Read the paper below and identify exactly 4 SPECIFIC research gaps. Each gap should:
1. Be specific to THIS paper's topic and approach
2. Be realistic and meaningful (not generic)
3. Describe a real limitation or unexplored area in the work
4. Be 1-2 sentences explaining the limitation clearly

Examples of specific gaps:
- "The paper evaluates the model only on datasets from a single domain, limiting validation of cross-domain generalization"
- "The study does not compare results with the latest transformer-based baselines published in 2023-2024"
- "Real-world deployment at scale was not tested, with experiments limited to controlled lab environments"
- "The proposed method lacks analysis of computational complexity and memory requirements for resource-constrained devices"

Research Paper:
{smart_chunk(text)}

Return ONLY this exact JSON format with exactly 4 gaps:
["specific gap 1 from this paper", "specific gap 2 from this paper", "specific gap 3 from this paper", "specific gap 4 from this paper"]"""

    # Attempt 1: Direct JSON parsing
    try:
        raw = call_llm(prompt)
        print(f"Raw gaps response: {raw[:200]}")
        result = safe_parse_json(raw)
        if isinstance(result, list) and len(result) >= 4:
            print(f"Gaps found: {len(result)}")
            return result[:4]
    except Exception as e:
        print(f"Gaps attempt 1 failed: {e}")

    # Attempt 2: Extract via regex patterns
    try:
        import re
        matches = re.findall(r'"([^"]{30,})"', raw)
        if len(matches) >= 4:
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
            if len(clean) > 30:
                gaps.append(clean)
        if len(gaps) >= 4:
            print(f"Gaps from lines: {gaps}")
            return gaps[:4]
    except Exception as e:
        print(f"Gaps attempt 3 failed: {e}")

    # Final fallback: Return sensible defaults
    print("Using default gaps")
    return [
        "The paper does not provide detailed information about the system architecture and its technical implementation.",
        "There is no comprehensive evaluation of the system's effectiveness or its actual impact on the target user population.",
        "The proposed approach has limited applicability, being tested only in controlled settings without consideration of diverse deployment scenarios.",
        "The research does not address critical practical challenges such as scalability constraints, resource limitations, or integration with existing systems."
    ]


def generate_hypotheses(gaps: list) -> list:
    """
    Generate 3 ranked hypotheses based on identified research gaps.
    
    Creates three hypotheses at different complexity/novelty levels:
    1. BASIC - Small, incremental improvement on existing work
    2. INTERMEDIATE - Moderate novelty combining existing approaches
    3. ADVANCED - High-risk, high-reward innovative idea
    
    Each hypothesis is concise with title and rationale.
    Detailed experiment designs are provided separately by design_experiments().
    
    Args:
        gaps (list): List of research gaps identified in the paper
        
    Returns:
        list: Array of hypothesis objects:
            [
                {
                    "level": "BASIC",
                    "title": "hypothesis statement",
                    "rationale": "why this addresses the gaps"
                },
                ...
            ]
    """
    gaps_str = " ".join(gaps) if gaps else "General research limitations"
    
    prompt = f"""You are a senior research scientist proposing innovative extensions to a paper.

Based on these research gaps:
{gaps_str}

Generate exactly 3 REALISTIC and SPECIFIC hypotheses, one at each complexity level.

IMPORTANT INSTRUCTIONS:
1. Each hypothesis should be SPECIFIC to the paper's topic and gaps identified
2. Hypotheses should directly address the identified gaps
3. Keep hypothesis titles concise but specific (1-2 sentences)
4. Provide clear rationale explaining how each hypothesis addresses the gaps

Return ONLY a valid JSON array with exactly 3 hypotheses:
[
  {{
    "level": "BASIC",
    "title": "Specific hypothesis statement addressing one or more gaps",
    "rationale": "How this directly addresses the identified gaps from the paper"
  }},
  {{
    "level": "INTERMEDIATE",
    "title": "Hypothesis combining multiple approaches or moderate technical enhancement",
    "rationale": "How this hypothesis addresses gaps through moderate innovation"
  }},
  {{
    "level": "ADVANCED",
    "title": "Novel hypothesis introducing new techniques or approaches",
    "rationale": "How this high-risk approach could revolutionize addressing the gaps"
  }}
]"""
    
    raw = call_llm(prompt)
    try:
        result = safe_parse_json(raw)
        if isinstance(result, list) and len(result) == 3:
            # Validate that all required fields are present
            for hyp in result:
                if all(k in hyp for k in ["level", "title", "rationale"]):
                    continue
                else:
                    raise ValueError("Missing required fields in hypothesis")
            print(f"Valid hypotheses generated: {len(result)}")
            return result
    except Exception as e:
        print(f"Hypothesis parsing failed: {e}")
    
    # Fallback with realistic hypotheses
    print("Using fallback realistic hypotheses")
    return [
        {
            "level": "BASIC",
            "title": "Documenting the system architecture in detail and conducting a small-scale pilot study with user satisfaction surveys will validate technical soundness and initial user acceptance.",
            "rationale": "This directly addresses gaps related to lack of technical documentation and absence of user evaluation, providing a low-risk initial assessment."
        },
        {
            "level": "INTERMEDIATE",
            "title": "Extending the system with multi-language support for 10+ languages, integrating real-time data feeds, and implementing offline functionality to improve usability in diverse, connectivity-limited environments.",
            "rationale": "Combines multiple moderate enhancements to address gaps regarding limited features, language support, and connectivity challenges."
        },
        {
            "level": "ADVANCED",
            "title": "Implementing federated machine learning with personalized recommendation models trained locally on each user's device, enabling privacy-preserving AI while creating a peer-to-peer knowledge network.",
            "rationale": "Introduces cutting-edge AI techniques to address scalability, privacy, and community-driven insights gaps identified in the original work."
        }
    ]


def design_experiments(hypotheses: list) -> list:
    """
    Design structured experiment plans for testing hypotheses.
    
    For each hypothesis, proposes:
    - Clear experimental objective
    - Step-by-step methodology (numbered steps)
    - Required data and resources (specific, concrete items)
    - Metrics for evaluation (specific measurement approaches)
    - Expected outcomes (quantifiable results)
    
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
    hyp_strs = []
    for h in hypotheses:
        title = h.get('title', h.get('hypothesis', ''))
        hyp_strs.append(f"- Level {h.get('level', 'Unknown')}: {title}")
    hypotheses_str = "\n".join(hyp_strs)
    
    prompt = f"""You are an expert research methodologist designing rigorous experiments.

For these hypotheses, design REALISTIC and DETAILED experiment plans:
{hypotheses_str}

CRITICAL INSTRUCTIONS:
1. Each experiment must be SPECIFIC and TESTABLE with ALL FIVE required fields
2. Include 4-6 numbered methodology steps - write each step as "1. Step text\\n2. Step text\\n3. Step text" (use actual \\n between steps)
3. List SPECIFIC required data/resources separated by " | "
4. Include SPECIFIC metrics with measurement details separated by " | "
5. Provide QUANTIFIABLE expected outcomes (e.g., ">=80% accuracy" or "15-20% improvement over baseline")

FORMATTING RULES:
- hypothesis: The exact hypothesis statement
- objective: One focused, clear sentence
- methodology: Steps separated by \\n like "1. First step\\n2. Second step\\n3. Third step\\n4. Fourth step"
- required_data: Items separated by " | " like "Dataset A | Tool B | 100 participants"
- evaluation_metrics: Metrics separated by " | " like "Accuracy (%) | F1 Score | Likert 1-5"
- expected_outcome: Specific quantified result

Return ONLY a valid JSON array with ONE experiment per hypothesis:
[
  {{
    "hypothesis": "The exact hypothesis from above",
    "objective": "Clear one-sentence objective",
    "methodology": "1. Design and prepare experimental setup\\n2. Recruit participants and collect baseline data\\n3. Implement proposed method\\n4. Run evaluation and collect results\\n5. Analyze and compare against baseline",
    "required_data": "Specific dataset | Specific tool | Hardware | Sample size: 100+ participants",
    "evaluation_metrics": "Precision and Recall | F1 Score | User satisfaction (1-5 Likert)",
    "expected_outcome": "Achieves >=85% accuracy with >=20% baseline improvement"
  }}
]"""
    
    raw = call_llm(prompt)
    try:
        result = safe_parse_json(raw)
        if isinstance(result, list) and len(result) > 0:
            # Validate all required fields are present in each experiment
            valid_results = []
            for exp in result:
                required_fields = ["hypothesis", "objective", "methodology", "required_data", "evaluation_metrics", "expected_outcome"]
                # Check if all fields exist and are not empty/N/A
                has_all_fields = all(k in exp and exp[k] and str(exp[k]).strip() not in ['', 'N/A', 'null'] for k in required_fields)
                
                if has_all_fields:
                    valid_results.append(exp)
                else:
                    print(f"Experiment has missing fields, will use fallback")
            
            if valid_results and len(valid_results) > 0:
                print(f"Valid experiments from API: {len(valid_results)}")
                return valid_results
            else:
                print("API returned experiments but they're missing required fields, using fallback")
    except Exception as e:
        print(f"Experiment design parsing failed: {e}")
    
    # Fallback with comprehensive realistic experiments
    print("Using fallback realistic experiments with full data")
    
    # Build fallback from hypothesis titles
    fallback = []
    if hypotheses and len(hypotheses) > 0:
        for i, hyp in enumerate(hypotheses):
            title = hyp.get('title', hyp.get('hypothesis', f'Hypothesis {i+1}'))
            exp_obj = {
                "hypothesis": title,
                "objective": f"To validate the effectiveness and feasibility of: {title[:80]}...",
                "methodology": "1. Design experimental protocol with clear procedures and success criteria 2. Prepare and validate all required datasets and tools 3. Conduct pilot testing to identify and resolve issues 4. Execute main experiment with full participant group 5. Collect comprehensive data and conduct statistical analysis 6. Document results and validate against hypothesis",
                "required_data": "Relevant domain dataset (500+ samples) | Analysis tools and software (R/Python/SPSS) | Computing resources (GPU/multi-core processor) | 50-100 human participants or expert reviewers | Standardized evaluation protocols and rubrics",
                "evaluation_metrics": "Primary metric: Accuracy/Success rate (≥80% target) | Secondary metrics: Precision and Recall (F1 score ≥0.75) | User/Expert satisfaction (Likert 1-5 scale, target ≥3.5) | Task completion time and efficiency | Statistical significance (p <0.05)",
                "expected_outcome": "Hypothesis validation with ≥80% success rate | Measurable improvement of 15-25% over baseline | Statistically significant results (p <0.05) | At least 3 actionable insights for future work | Reproducible findings across ≥2 validation runs"
            }
            fallback.append(exp_obj)
            print(f"Fallback experiment {i+1} created with complete fields")
    
    if not fallback:
        # Ultimate fallback if no hypotheses provided
        print("No hypotheses provided, returning empty experiments list (this should not happen in normal usage)")
    
    print(f"Returning {len(fallback)} experiments")
    return fallback