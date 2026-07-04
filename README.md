# 🤖 Gemini QA Automation Agent

An automated QA assistant that leverages **Google Gemini 3.5 Flash**, **LangChain**, and **Pydantic** to instantly convert raw requirements and user stories into highly structured, comprehensive test suites. 

Instead of writing test cases manually, simply drop your acceptance criteria into a file, and this agent will generate positive paths, negative paths, and edge cases, exporting them neatly into both `.csv` and `.md` formats.

## ✨ Features
* **AI-Powered Analysis:** Uses Gemini's strong reasoning capabilities to spot missing edge cases in requirements.
* **Guaranteed Structure:** Uses Pydantic to force the LLM to output strictly formatted data—no messy text walls.
* **File-Based Input:** Reads requirements cleanly from a local `requirements.md` file.
* **Automated Exports:** Instantly saves generated test cases as timestamped `.csv` (for Excel/Jira) and `.md` (for documentation) files.
* **Secure Setup:** Uses environment variables (`.env`) to keep your API keys safe and out of version control.

## 🛠️ Prerequisites
* Python 3.8+
* A valid [Google Gemini API Key](https://aistudio.google.com/app/apikey)

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/gemini-qa-agent.git](https://github.com/yourusername/gemini-qa-agent.git)
   cd gemini-qa-agent
