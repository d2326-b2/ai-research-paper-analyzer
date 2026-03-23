from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

from database import db, User
from pdf_extractor import extract_text, is_valid_pdf
from llm_service import (
    extract_title, generate_summary, extract_concepts,
    extract_relations, identify_gaps, generate_hypotheses,
    design_experiments
)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'hypogen-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm', '')

        if not name or not email or not password:
            return render_template('register.html', error='All fields are required')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')

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
    logout_user()
    return redirect(url_for('login'))


@app.route('/analyze', methods=['POST'])
@login_required
def analyze_paper():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files accepted'}), 400

    temp_path = f'temp_{file.filename}'
    file.save(temp_path)

    try:
        print('Step 1: Extracting text...')
        text = extract_text(temp_path)

        if not is_valid_pdf(text):
            return jsonify({'error': 'Scanned PDF detected.'}), 400

        print('Step 2: Extracting title...')
        title = extract_title(text)

        print('Step 3: Generating summary...')
        summary = generate_summary(text)

        print('Step 4: Extracting concepts...')
        concepts = extract_concepts(text)

        print('Step 5: Extracting relations...')
        relations = extract_relations(text, concepts)

        print('Step 6: Identifying gaps...')
        gaps = identify_gaps(text)

        print('Step 7: Generating hypotheses...')
        hypotheses = generate_hypotheses(gaps)

        print('Step 8: Designing experiments...')
        experiments = design_experiments(hypotheses)

        print('Done!')

        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'title': title,
            'summary': summary,
            'concepts': concepts,
            'graph': {'nodes': concepts, 'edges': relations},
            'gaps': gaps,
            'hypotheses': hypotheses,
            'experiments': experiments
        })

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == '__main__':
    app.run(debug=True, port=8000)