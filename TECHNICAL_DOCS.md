# ARK Doubao Translator Technical Documentation

## Project Overview
ARK Doubao Translator is a Flask-based web application that provides real-time translation using the ARK Doubao Translation API. Key features include:
- Dark theme UI with responsive design
- Markdown and LaTeX rendering support
- Automatic translation with debounced input
- Translation history (local storage)
- Font size adjustment
- 28 supported languages

## Architecture

### Backend (Flask)
**Main File: `app.py`**
- **Routes**: `/` (index page) and `/translate` (API endpoint)
- **Core Function**: `ark_translate()` (lines 46-125) handles API communication
- **Language Support**: `LANGUAGE_MAP` (lines 15-44) with 28 languages
- **Error Handling**: Comprehensive error handling for API responses (HTTP errors, timeouts, network issues)
- **Character Limit**: 10,000 character input validation

### Frontend
**Key Files**:
1. `templates/index.html`: Main page structure with input/output sections, history, and status bar
2. `static/script.js`: Frontend logic including:
   - `debounce()` (lines 39-48): 500ms delay for input throttling
   - `renderMarkdownAndMath()` (lines 71-108): Extract-Render-Inject pattern for safe content rendering
   - `performTranslation()` (lines 114-175): Main translation function
   - History management (max 5 items)
3. `static/style.css`: Dark theme with CSS variables (lines 1-13)

### Key Integrations
- **MathJax**: Localized library for LaTeX rendering (config in index.html lines 16-33)
- **Marked.js**: Localized library for Markdown processing
- **ARK Doubao API**: Translation service with 30-second timeout

## Development Setup
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure API Key**:
   - `cp .env.example translator.env`
   - Add your `ARK_API_KEY` to `translator.env`
3. **Run the App**: `python app.py` (available at http://127.0.0.1:5000)

## Core Features
1. **Real-time Translation**: Debounced input with automatic translation
2. **Content Rendering**: Combined Markdown and LaTeX processing
3. **Translation History**: Local storage with max 5 items
4. **UI Controls**: Font size adjustment (12-26px), input collapse, language swapping
5. **Error Handling**: User-friendly error messages for API issues

## Code Structure
```
ARK-translator/
├── app.py                # Backend entry point
├── requirements.txt      # Dependencies
├── translator.env        # API key config (gitignored)
├── templates/
│   └── index.html        # Main UI template
├── static/
│   ├── style.css         # Dark theme styling
│   ├── script.js         # Frontend logic
│   └── lib/
│       ├── marked.min.js # Markdown processor
│       └── tex-mml-chtml.js # MathJax library
└── TECHNICAL_DOCS.md     # This document
```

## Security Notes
- API keys stored in `translator.env` (gitignored)
- Input validation for language codes and character limit
- Comprehensive error handling for API responses

## Deployment Considerations
- **Development Server**: Flask dev server not suitable for production
- **Production**: Use WSGI server (e.g., Gunicorn)
- **Static Assets**: All libraries (MathJax, Marked.js) are localized
- **Env Config**: Ensure `translator.env` is properly configured in production

## Troubleshooting
1. **Missing API Key**: Check `translator.env` for `ARK_API_KEY`
2. **MathJax Issues**: Ensure local library paths are correct
3. **Translation Errors**: Check API key validity and network connection
4. **Rendering Problems**: Verify Marked.js and MathJax integration
