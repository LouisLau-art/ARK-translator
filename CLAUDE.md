# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ARK Doubao Translator is a Flask-based web application that provides real-time translation using the ARK Doubao Translation API. The application features a dark theme UI with support for Markdown/LaTeX rendering, automatic translation, translation history, and font size adjustment.

## Architecture

### Backend (Flask)
- **app.py**: Main Flask application entry point
  - Contains the `ark_translate()` function that interfaces with the ARK API
  - Implements two routes: `/` (index page) and `/translate` (API endpoint)
  - Handles language mapping for 28 supported languages
  - Includes comprehensive error handling for API responses

### Frontend (HTML/CSS/JavaScript)
- **templates/index.html**: Main page template with responsive layout
- **static/style.css**: Complete dark theme styling with CSS custom properties
- **static/script.js**: Frontend JavaScript with features including:
  - Real-time translation with debounced input
  - Markdown and LaTeX rendering pipeline
  - Local storage for translation history
  - Collapsible UI sections and font size controls

### Key Integration Points
- **MathJax**: Localized library for LaTeX formula rendering
- **Marked.js**: Localized library for Markdown processing
- **ARK API**: Translation service integration with 30-second timeout

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example translator.env
# Edit translator.env and add your ARK_API_KEY
```

### Running the Application
```bash
# Start development server
python app.py

# Application will be available at http://127.0.0.1:5000
```

### Security Notes
- API keys are stored in `translator.env` (gitignored)
- Never commit API keys or sensitive configuration
- Application validates API key presence on startup

## Code Structure Insights

### Translation Pipeline
1. **Input Processing**: Text is sanitized and validated (10,000 character limit)
2. **API Integration**: Uses ARK Doubao Translation API with proper error handling
3. **Content Rendering**: Combined Markdown and LaTeX processing with placeholder-based approach
4. **MathJax Integration**: Formula rendering with cache clearing and re-rendering

### Key Functions
- `ark_translate()` (app.py:46): Core translation function with comprehensive error handling
- `renderMarkdownAndMath()` (script.js:71): Three-step process (Extract-Render-Inject) for safe content rendering
- `debounce()` (script.js:39): Input throttling for performance optimization

### Configuration Management
- Environment variables loaded via `python-dotenv`
- Language mapping centralized in `LANGUAGE_MAP` constant
- All configuration files are gitignored for security

## Testing and Validation

- No formal test suite exists currently
- Manual testing should verify:
  - Translation functionality with various text inputs
  - Markdown and LaTeX rendering pipeline
  - Error handling for API failures
  - UI responsiveness and accessibility features

## Deployment Considerations

- Application runs on Flask development server (not suitable for production)
- For production deployment, consider using a proper WSGI server
- Ensure `translator.env` is properly configured on deployment server
- Static assets are served locally (MathJax and Marked.js libraries are localized)