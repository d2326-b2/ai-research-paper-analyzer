# Project Structure & Architecture

## 📁 Directory Organization

```
hypothesis_gen/                    # Root project directory
├── backend/                        # Flask backend (Python)
│   ├── main.py                    # Flask app, routes, entry point
│   ├── database.py                # SQLAlchemy models, DB config
│   ├── pdf_extractor.py           # PDF processing utilities
│   ├── llm_service.py             # Gemini AI integration
│   ├── requirements.txt            # Python dependencies (organized by category)
│   ├── instance/                  # SQLite database (created at runtime)
│   │   └── users.db
│   ├── templates/                 # HTML templates (Jinja2)
│   │   ├── index.html             # Main dashboard
│   │   ├── login.html             # Login form
│   │   └── register.html          # Registration form
│   └── static/                    # Frontend assets
│       ├── style.css              # Main stylesheet
│       └── scripts.js             # Frontend JavaScript
│
├── hypo/                          # Python virtual environment
│   ├── pyvenv.cfg
│   ├── Scripts/                   # Windows executables
│   ├── Lib/                       # Installed packages
│   └── Include/                   # C headers
│
├── .env                           # Environment variables (NOT in git)
├── .env.example                   # Template for .env file
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git line ending configuration
├── README.md                      # Project documentation
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guidelines
├── CHANGELOG.md                   # Version history
├── SECURITY.md                    # Security policy
├── ARCHITECTURE.md                # This file
└── .github/
    └── workflows/
        └── python-app.yml         # CI/CD pipeline


```

## 🏗 Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Client Browser (Frontend)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  index.html (Jinja2 Template)                  │   │
│  │  - Navigation & Layout                          │   │
│  │  - PDF Upload Area                             │   │
│  │  - Results Display (Tabs)                      │   │
│  │  - Cytoscape Knowledge Graph Container         │   │
│  └─────────────────────────────────────────────────┘   │
│                      ↓↑ (Fetch/XHR)                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │  scripts.js (Vanilla JavaScript)                │   │
│  │  - File handling & validation                  │   │
│  │  - API communication                           │   │
│  │  - Dynamic DOM rendering                       │   │
│  │  - UI interactions (tabs, modals)              │   │
│  └─────────────────────────────────────────────────┘   │
│                      ↓↑                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  style.css (CSS3)                              │   │
│  │  - Responsive design (Grid/Flex)               │   │
│  │  - Theme & animations                          │   │
│  │  - Component styling                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                     HTTP/S
                      ↓↑
┌─────────────────────────────────────────────────────────┐
│            Flask Backend (Python)                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  main.py (Flask Application)                    │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  Routes & Middleware                    │   │   │
│  │  │  - / (index)                            │   │   │
│  │  │  - /login (authentication)              │   │   │
│  │  │  - /register                            │   │   │
│  │  │  - /logout                              │   │   │
│  │  │  - /analyze (PDF processing)            │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                      ↓ (coordinates)                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  database.py (SQLAlchemy ORM)                  │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  Models:                                 │   │   │
│  │  │  - User (id, name, email, password)   │   │   │
│  │  │  - Methods: set_password(), check_pw() │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  │                  ↓ (ORM)                       │   │
│  │          SQLite users.db                       │   │
│  └─────────────────────────────────────────────────┘   │
│          ↓ (PDF processing)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  pdf_extractor.py                              │   │
│  │  ├─ extract_text(pdf_path) → str              │   │
│  │  ├─ is_valid_pdf(text) → bool                │   │
│  │  └─ smart_chunk(text, limit) → str           │   │
│  │                  ↓ (temp file)                   │   │
│  │          PyMuPDF (fitz) Driver                 │   │
│  └─────────────────────────────────────────────────┘   │
│          ↓ (AI analysis)                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  llm_service.py (Gemini Integration)            │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  Core Functions:                         │   │   │
│  │  │  - generate_summary(text) → str          │   │   │
│  │  │  - extract_concepts(text) → list         │   │   │
│  │  │  - extract_relations(text, concepts)     │   │   │
│  │  │  - identify_gaps(text) → list            │   │   │
│  │  │  - generate_hypotheses(gaps) → list      │   │   │
│  │  │  - design_experiments(hypotheses)        │   │   │
│  │  ├──────────────────────────────────────────┤   │   │
│  │  │  Helper Functions:                       │   │   │
│  │  │  - call_llm(prompt) → str               │   │   │
│  │  │  - safe_parse_json(raw) → dict/list     │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  │                  ↓                               │   │
│  │      Google Generative AI API                  │   │
│  │      (Gemini 2.5-flash)                        │   │
│  └─────────────────────────────────────────────────┘   │
│          ↓ (returns results)                           │
│                  JSON Response                        │
└─────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

### 1. User Registration/Login Flow
```
User Input → Flask Route → Database Query → Password Hashing
         ↓
    Session Created → Redirect to Dashboard
```

### 2. PDF Analysis Flow
```
PDF Upload → File Validation → PDF Text Extraction
         ↓
    Valid PDF? → [No] Return Error
         ↓ [Yes]
    Generate Summary → Extract Concepts → Extract Relations
         ↓
    Identify Gaps → Generate Hypotheses → Design Experiments
         ↓
    JSON Response → Frontend Rendering → Display Results
```

## 🔄 Component Interaction

### Backend Components

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| `main.py` | Request routing, session management | Flask, Flask-Login |
| `database.py` | User model, password management | SQLAlchemy, bcrypt |
| `pdf_extractor.py` | PDF text extraction | PyMuPDF (fitz) |
| `llm_service.py` | AI analysis orchestration | Google GenAI |

### Frontend Components

| Component | Purpose | Technologies |
|-----------|---------|--------------|
| `index.html` | Page structure, templates | Jinja2, HTML5 |
| `scripts.js` | Interactivity, API calls | ES6 JavaScript |
| `style.css` | Visual styling, animations | CSS3, Grid, Flexbox |

## 🔐 Security Architecture

```
┌─ User Input Validation
│  ├─ File type validation (.pdf only)
│  ├─ File size limits (optional)
│  └─ Text sanitization
├─ Authentication
│  ├─ Password hashing (bcrypt)
│  ├─ Session management (Flask-Login)
│  └─ CSRF protection (implicit with Flask)
├─ Data Protection
│  ├─ Environment variables (.env)
│  ├─ Database isolation per user
│  └─ Temporary file cleanup
└─ API Security
   ├─ CORS configuration
   ├─ Rate limiting (implementable)
   └─ Input validation on all endpoints
```

## 📦 Dependency Categories

### Core Framework
- Flask, Flask-Login, Flask-SQLAlchemy, Flask-CORS
- Werkzeug (WSGI utilities)

### AI/LLM
- google-generativeai
- Supporting APIs: google-auth, google-api-python-client

### Database
- SQLAlchemy, greenlet

### PDF Processing
- PyMuPDF (fitz)

### Security
- bcrypt, cryptography

### Utilities
- python-dotenv, requests

## 🚀 Deployment Architecture

For production deployment, the architecture would typically be:

```
Internet
    ↓
Reverse Proxy (nginx/Apache)
    ↓
WSGI Server (Gunicorn/uWSGI)
    ↓
Flask Application Instances (load balanced)
    ↓
SQLite Database (or PostgreSQL for production)
```

## 📈 Scalability Considerations

### Current Limitations
- SQLite is suitable for development only
- Single instance deployment
- No caching layer
- Synchronous API calls

### Future Improvements
- Migrate to PostgreSQL
- Implement caching (Redis)
- Async processing with Celery
- Load balancing with multiple instances
- API rate limiting
- Monitoring & logging infrastructure

---

**Last Updated:** April 4, 2024
