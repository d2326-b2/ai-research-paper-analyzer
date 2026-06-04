# How Dummy Data is Converted to PDF

## Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: User clicks "Download PDF Report"                     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ downloadPDF() function in scripts.js                            │
│ - Gets reportData from global variable (real or dummy)          │
│ - Initializes jsPDF document                                    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ PDF GENERATION STEPS:                                           │
│                                                                 │
│ 1. Cover Page                                                   │
│    - Title from reportData.title                               │
│    - Generated date & filename                                  │
│                                                                 │
│ 2. Table of Contents                                            │
│                                                                 │
│ 3. Paper Summary                                                │
│    - reportData.summary (formatted text)                        │
│                                                                 │
│ 4. Key Concepts                                                 │
│    - reportData.concepts (array → formatted tags)               │
│                                                                 │
│ 5. Knowledge Graph                                              │
│    - reportData.graph (Cytoscape canvas → PNG image)            │
│                                                                 │
│ 6. Research Gaps                                                │
│    - reportData.gaps (array → formatted bullet list)            │
│                                                                 │
│ 7. Generated Hypotheses                                         │
│    - reportData.hypotheses (3 levels: Basic/Inter/Advanced)     │
│    - Each hypothesis gets colored header                        │
│                                                                 │
│ 8. Experiment Designs                                           │
│    - reportData.experiments (array of objects)                  │
│                                                                 │
│    For each experiment:                                         │
│    ├─ Hypothesis (formatted text with background)              │
│    ├─ Objective (single paragraph)                             │
│    ├─ Methodology (formatted as numbered steps)                │
│    ├─ Required Data (formatted as bullet list)                 │
│    ├─ Evaluation Metrics (formatBulletPoints())               │
│    └─ Expected Outcome (formatBulletPoints())                  │
│                                                                 │
│ 9. Page Numbers & Headers                                       │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ doc.save('Hypothesis_Report_[title].pdf')                      │
│                                                                 │
│ PDF file downloaded to user's Downloads folder                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow for Dummy Dashboard

### 1. Backend (/analyze endpoint in app.py)
```python
# When API call fails, returns dummy data:
from dummy_data import get_dummy_data_with_filename

dummy_data = get_dummy_data_with_filename(file.filename)
dummy_data['fallback'] = True
return jsonify(dummy_data)  # Returns JSON
```

### 2. Frontend Receives JSON
```javascript
// analyzePaper() function
const response = await fetch('/analyze', { method: 'POST', body: formData });
const data = await response.json();
reportData = data;  // Store globally
```

### 3. Display Data in Dashboard
```javascript
if (data.experiments) displayExperiments(data.experiments);
// Renders HTML with formatBullets() and formatBulletPoints()
```

### 4. Convert to PDF (downloadPDF function)

#### For "Evaluation Metrics" & "Expected Outcome":
```javascript
// Raw dummy data format:
"evaluation_metrics": "• System architecture documentation completeness score\n• Prototype stability (uptime percentage)\n• User satisfaction score (1-5 Likert scale, target ≥3.5/5)\n..."

// Processing:
const metr = exp.evaluation_metrics || 'N/A';
const out  = exp.expected_outcome || 'N/A';

// In PDF generation:
{ label: 'EVALUATION METRICS', text: formatBulletPoints(metr), ... }
{ label: 'EXPECTED OUTCOME',   text: formatBulletPoints(out),  ... }

// formatBulletPoints() function:
function formatBulletPoints(text) {
  // 1. Split by newline OR pipe
  // 2. Remove leading bullets (•), dashes, asterisks
  // 3. Return newline-separated items
  // 4. multiLineText() renders each line separately
}
```

#### For "Objective":
```javascript
// Single paragraph, no special formatting
{ label: 'OBJECTIVE', text: cleanText(obj), ... }
// cleanText() just removes smart quotes and extra spaces
```

#### For "Methodology":
```javascript
// Formatted as numbered steps
{ label: 'METHODOLOGY', text: formatSteps(meth), isSteps: true }

// formatSteps() function:
function formatSteps(text) {
  // Converts "1. Step 2. Step 3. Step" → newline-separated
  text = text.replace(/\s+(\d+)\.\s+/g, '\n$1. ');
  return text;
}

// multiLineText() renders each numbered step on separate line
```

---

## Key Functions in scripts.js

### `downloadPDF()`
- Main PDF generation function (line ~451)
- Creates jsPDF document
- Renders all sections
- Handles page breaks
- Saves file

### `formatBulletPoints(text)` (PDF only)
- Located inside downloadPDF() function
- Handles pipe-separated OR newline-separated values
- Removes bullet points
- Returns newline-separated string for PDF rendering
- Used for: Evaluation Metrics, Expected Outcome, Required Data

### `formatSteps(text)` (PDF only)
- Located inside downloadPDF() function
- Formats numbered methodology steps
- Converts inline format → newline-separated

### `multiLineText(text, x, startY, maxW, lineH, color, size, bold)`
- Located inside downloadPDF() function
- Renders multi-line text with proper line breaks
- Handles `\n` characters in text
- Each line respects line height & max width

### `formatBullets(text)` (HTML Dashboard)
- Located in main scope (line ~440)
- Used to display data in HTML dashboard
- Creates `<ul><li>` HTML list
- Used for: displayExperiments() function

---

## Dummy Data Structure (dummy_data.py)

```python
DUMMY_ANALYSIS = {
    "status": "success",
    "filename": "farmers-smart-assistant-system.pdf",
    "title": "...",
    "summary": "...",
    "concepts": [...],
    "graph": {"nodes": [...], "edges": [...]},
    "gaps": [...],
    "hypotheses": [
        {
            "level": "BASIC|INTERMEDIATE|ADVANCED",
            "title": "...",
            "rationale": "..."
        },
        ...
    ],
    "experiments": [
        {
            "hypothesis": "...",
            "objective": "...",
            "methodology": "1. Step 2. Step 3. Step",
            "required_data": "Data1 | Data2 | Data3",
            "evaluation_metrics": "• Metric1\n• Metric2\n• Metric3",
            "expected_outcome": "• Outcome1\n• Outcome2\n• Outcome3"
        },
        ...
    ]
}
```

---

## Summary

1. **Backend** → Returns dummy data as JSON (either real analysis or dummy fallback)
2. **Frontend receives** → Stores in `reportData` global variable
3. **Display** → `displayExperiments()` renders HTML using `formatBullets()`
4. **PDF Export** → `downloadPDF()` processes data using:
   - `formatBulletPoints()` for lists (metrics, outcomes, required data)
   - `formatSteps()` for numbered steps (methodology)
   - `multiLineText()` to render with line breaks
5. **Output** → Professional PDF with properly formatted sections

The key is that **same data flows through two formatting pipelines**:
- **HTML pipeline**: `formatBullets()` → creates `<ul><li>` lists
- **PDF pipeline**: `formatBulletPoints()` → creates newline-separated text for `multiLineText()`
