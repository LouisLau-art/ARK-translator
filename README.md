https://img.shields.io/badge/python-v3.7+-blue.svg

https://img.shields.io/badge/flask-v2.3.2-green.svg

https://img.shields.io/badge/license-MIT-blue.svg

https://img.shields.io/badge/PRs-welcome-brightgreen.svg



\# ARK Doubao Translator 🔤



A lightweight, dark-themed web translator powered by ARK Doubao Translation API with Markdown rendering support.



!\[Demo Screenshot](screenshots/demo.png)



\## Features ✨



\- 🌙 \*\*Dark Mode\*\*: Eye-friendly dark theme

\- 🔄 \*\*Auto-Translation\*\*: Translates as you type with smart debouncing

\- 📝 \*\*Markdown Support\*\*: Renders formatted text with proper styling

\- 🌍 \*\*Multi-Language\*\*: Supports Chinese-English bidirectional translation

\- 📋 \*\*One-Click Copy\*\*: Easy copying of translation results

\- ⚡ \*\*Lightweight\*\*: Minimal dependencies, fast startup

\- 🎯 \*\*Full-Screen Layout\*\*: Maximizes screen utilization



\## Tech Stack 🛠



\- \*\*Backend\*\*: Flask (Python)

\- \*\*Frontend\*\*: Vanilla HTML/CSS/JavaScript

\- \*\*API\*\*: ARK Doubao Translation Model

\- \*\*Markdown\*\*: Python-Markdown



\## Quick Start 🚀



\### Prerequisites



\- Python 3.7+

\- ARK API Key (\[Get it here](https://www.volcengine.com/))



\### Installation



1\. \*\*Clone the repository\*\*

   ```bash

   git clone https://github.com/yourusername/ark-translator.git

   cd ark-translator



2.Install dependencies



 	pip install -r requirements.txt



3.Configure API Key



cp .env.example translator.env

\# Edit translator.env and add your ARK API key



4.Run the application



python app.py



5.Open in browser



http://localhost:5000



Configuration ⚙️



The application uses environment variables for configuration. Create a translator.env file:



ARK\_API\_KEY=your\_actual\_api\_key\_here



Usage 📖

Enter or paste text in the left panel

Translation appears automatically in the right panel

Use the swap button (⇄) to exchange source and target languages

Click the copy button (📋) to copy the translation

Toggle auto-translation with the switch at the bottom

API Documentation 📚

The ARK Doubao Translation API supports 28 languages. This implementation focuses on Chinese-English translation but can be extended.



Supported Languages (Current Implementation)

🇨🇳 Chinese (Simplified)

🇺🇸 English

🔍 Auto-detect

Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.



Fork the project

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

Security 🔒

Never commit your API keys

Use environment variables for sensitive data

The .gitignore file is configured to exclude environment files

License 📄

This project is licensed under the MIT License - see the LICENSE file for details.



Acknowledgments 🙏

Volcano Engine for the ARK API

Flask for the web framework

Python-Markdown for Markdown rendering



Author 👤





GitHub: @LouisLau-art

Email: louis.shawn@qq.com



Support ⭐

If you find this project helpful, please give it a star!



Made with ❤️ and ☕


