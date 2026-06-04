"""
HypoGen - AI-Powered Research Paper Analysis
Main Flask Application Module

This module contains the core Flask application and all API endpoints for:
- User authentication (registration, login, logout)
- PDF upload and analysis
- Research paper processing with Gemini AI

Author: Your Name
Date: 2024
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

from database import db, User
from pdf_extractor import extract_text, is_valid_pdf
from llm_service import (
    generate_summary, extract_title, extract_concepts,
    extract_relations, identify_gaps, generate_hypotheses,
    design_experiments
)
from dummy_data import get_dummy_data_with_filename

# ============= APP INITIALIZATION =============
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure Flask app settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hypogen-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for cross-origin requests
CORS(app)

# Initialize database
db.init_app(app)

# Setup Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for session management."""
    return User.query.get(int(user_id))

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


# ============= AUTHENTICATION ROUTES =============

@app.route('/')
def index():
    """
    Home route - redirects to login if not authenticated, otherwise shows dashboard.
    
    Returns:
        - Dashboard if user is logged in
        - Login page redirect if user is not authenticated
    """
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint.
    
    GET: Displays login form
    POST: Authenticates user credentials
        - Validates email and password
        - Creates persistent session if credentials are correct
        - Shows error message if authentication fails
    
    Returns:
        - Login form (GET) or on failed POST
        - Redirect to dashboard on successful login
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Query user by email
        user = User.query.filter_by(email=email).first()
        
        # Verify password and create session
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration endpoint.
    
    GET: Displays registration form
    POST: Creates new user account
        - Validates all required fields are provided
        - Checks password confirmation matches
        - Enforces minimum password length (6 characters)
        - Prevents duplicate email registrations
        - Hashes password before storing in database
    
    Returns:
        - Registration form (GET) or on validation failure
        - Redirect to dashboard on successful registration
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        # Validate all fields are provided
        if not name or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        # Verify password confirmation
        if password != confirm:
            return render_template('register.html', error='Passwords do not match')
        
        # Check password length
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        # Check for duplicate email
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')

        # Create new user with hashed password
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """
    User logout endpoint.
    
    Clears user session and redirects to login page.
    Requires user to be logged in.
    
    Returns:
        Redirect to login page
    """
    logout_user()
    return redirect(url_for('login'))


# ============= ANALYSIS ROUTES =============

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_paper():
    """
    Main PDF analysis endpoint with graceful fallback to dummy data.
    
    Accepts a PDF file, extracts text, and performs comprehensive analysis:
    1. Text extraction from PDF
    2. PDF validity check (detects scanned PDFs)
    3. Summary generation
    4. Key concept extraction
    5. Relationship mapping between concepts
    6. Research gaps identification
    7. Hypothesis generation (3 levels: basic, intermediate, advanced)
    8. Experiment design proposal
    
    If API calls fail (e.g., API key invalid, quota exceeded), returns
    realistic dummy data demonstrating what results would look like.
    
    Returns:
        JSON with complete analysis results or dummy data (fallback) or error message
    """
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files accepted'}), 400

    temp_path = f'temp_{file.filename}'
    file.save(temp_path)

    try:
        # Step 1: Extract text from PDF
        print('Step 1: Extracting text...')
        print(f'  ├─ Reading PDF file: {file.filename}')
        print(f'  ├─ Scanning for text content...')
        text = extract_text(temp_path)
        print(f'  └─ ✓ Extracted {len(text)} characters from PDF')

        # Step 2: Validate PDF (reject scanned/image PDFs)
        print('Step 2: Validating PDF format...')
        print(f'  ├─ Checking for text-based content...')
        if not is_valid_pdf(text):
            print(f'  └─ ✗ Scanned PDF detected - contains images only')
            return jsonify({'error': 'Scanned PDF detected. Please use text-based PDFs.'}), 400
        print(f'  └─ ✓ Valid text-based PDF confirmed')

        try:
            # Step 3: Extract paper title
            print('Step 3: Extracting paper title...')
            print(f'  ├─ Analyzing paper content...')
            print(f'  ├─ Extracting or generating title...')
            paper_title = extract_title(text)
            print(f'  └─ ✓ Title extracted: {paper_title}')
        except Exception as e:
            print(f'Title extraction failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 4: Generate summary
            print('Step 4: Generating summary...')
            print(f'  ├─ Analyzing paper content...')
            print(f'  ├─ Sending to AI model for processing...')
            summary = generate_summary(text)
            print(f'  └─ ✓ Summary generated successfully')
        except Exception as e:
            print(f'Summary generation failed, using dummy data: {str(e)}')
            # If any step fails, use dummy data
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 5: Extract key concepts
            print('Step 5: Extracting concepts...')
            print(f'  ├─ Identifying key terms and topics...')
            print(f'  ├─ Building concept library...')
            concepts = extract_concepts(text)
            print(f'  └─ ✓ Found {len(concepts)} key concepts')
        except Exception as e:
            print(f'Concept extraction failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 6: Extract relationships between concepts
            print('Step 6: Extracting relationships...')
            print(f'  ├─ Mapping connections between concepts...')
            print(f'  ├─ Building knowledge graph...')
            relations = extract_relations(text, concepts)
            print(f'  └─ ✓ Found {len(relations)} concept relationships')
        except Exception as e:
            print(f'Relation extraction failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 7: Identify research gaps
            print('Step 7: Identifying research gaps...')
            print(f'  ├─ Analyzing paper contributions...')
            print(f'  ├─ Finding unexplored areas...')
            gaps = identify_gaps(text)
            print(f'  └─ ✓ Identified {len(gaps)} research gaps')
        except Exception as e:
            print(f'Gap identification failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 8: Generate ranked hypotheses
            print('Step 8: Generating hypotheses...')
            print(f'  ├─ Creating research hypotheses...')
            print(f'  ├─ Ranking by relevance and feasibility...')
            hypotheses = generate_hypotheses(gaps)
            print(f'  └─ ✓ Generated {len(hypotheses)} hypotheses')
        except Exception as e:
            print(f'Hypothesis generation failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        try:
            # Step 9: Design experiments
            print('Step 9: Designing experiments...')
            print(f'  ├─ Creating experimental methodologies...')
            print(f'  ├─ Defining success metrics...')
            experiments = design_experiments(hypotheses)
            print(f'  └─ ✓ Designed {len(experiments)} experiments')
        except Exception as e:
            print(f'Experiment design failed, using dummy data: {str(e)}')
            dummy_data = get_dummy_data_with_filename(file.filename)
            dummy_data['fallback'] = True
            dummy_data['fallback_reason'] = f'API unavailable: {str(e)[:100]}'
            return jsonify(dummy_data)

        print('\n✓ Analysis complete!')
        print('═' * 50)

        # Return comprehensive analysis results
        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'title': paper_title,
            'summary': summary,
            'concepts': concepts,
            'graph': {'nodes': concepts, 'edges': relations},
            'gaps': gaps,
            'hypotheses': hypotheses,
            'experiments': experiments,
            'fallback': False
        })

    except Exception as e:
        print(f'Critical PDF extraction error: {str(e)}')
        # Last resort: return dummy data for any extraction error
        dummy_data = get_dummy_data_with_filename(file.filename if 'file' in locals() else 'unknown.pdf')
        dummy_data['fallback'] = True
        dummy_data['fallback_reason'] = f'Processing error: {str(e)[:100]}'
        return jsonify(dummy_data)

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============= APP ENTRY POINT =============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)