# Contributing to HypoGen

First off, thank you for considering contributing to HypoGen! It's people like you that make HypoGen such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**
* **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Setup

### Prerequisites
- Python 3.12+
- Git
- Virtual environment tool (venv)

### Local Development

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/hypogen.git
cd hypogen
```

2. **Create Virtual Environment**
```bash
python -m venv hypo
source hypo/bin/activate  # On Windows: hypo\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your Gemini API key
```

5. **Run Tests**
```bash
python -m pytest tests/
```

6. **Start Development Server**
```bash
cd backend
python main.py
```

## Style Guide

### Python
- Follow [PEP 8](https://pep8.org/)
- Use type hints for function parameters and returns
- Write docstrings for all functions and classes
- Use 4 spaces for indentation

### Example:
```python
def analyze_paper(pdf_text: str) -> dict:
    """
    Analyze a research paper.
    
    Args:
        pdf_text (str): Full text of the research paper
        
    Returns:
        dict: Analysis results containing summary, concepts, etc.
    """
    # Implementation here
    pass
```

### Git Commits
- Use clear, descriptive commit messages
- Start with a capital letter
- Use imperative mood ("add feature" not "added feature")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally

### Example Commit Messages:
```
Fix bug in PDF extraction for multi-page documents

- Handle edge case where content spans pages
- Add test case for large PDFs
- Fixes #123
```

## Testing

Before submitting a pull request:

1. **Write tests** for any new functionality
2. **Ensure all tests pass**
```bash
python -m pytest tests/ -v
```

3. **Check code coverage**
```bash
python -m pytest --cov=backend tests/
```

## Documentation

- Update README.md if you're adding features
- Add docstrings to all new functions
- Update API documentation if endpoints change
- Include examples for new features

## File Structure

When adding new files:
```
backend/
├── main.py              # Never modify in breaking ways
├── features/            # Create new modules here
│   └── new_feature.py
├── tests/               # Add corresponding tests
│   └── test_new_feature.py
└── requirements.txt     # Update if adding dependencies
```

## Commit Process

1. Create a new branch for your feature
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Commit frequently with clear messages
4. Push to your fork
```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request with:
   - Clear title
   - Description of changes
   - Reference to related issues
   - Screenshots if UI changes

## Pull Request Process

1. Update documentation and README as needed
2. Ensure all tests pass
3. Add tests for new functionality
4. Increase version numbers following [Semantic Versioning](https://semver.org/)
5. Get approval from maintainers
6. Squash commits if requested
7. Merge when ready

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested
* `wontfix` - This will not be worked on

### Project Priorities

1. **Bug Fixes** - Critical issues are prioritized
2. **Performance** - Optimizations for better speed
3. **Features** - New capabilities and enhancements
4. **Documentation** - Keeping docs up to date

## Questions?

Feel free to ask questions in:
- GitHub Issues
- GitHub Discussions
- Email: contact@hypogen.ai

## Recognition

Contributors will be listed in:
- README.md
- GitHub contributors page
- Release notes (for significant contributions)

Thank you for contributing to HypoGen! 🎉
