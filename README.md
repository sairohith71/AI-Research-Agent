# AI-Powered Research Agent (Local Ollama version)

## Login and accounts
- The app opens with a professional **Sign in / Create account** page.
- First-time users select **Create account**, choose a username and a password (minimum 8 characters), then sign in.
- User accounts are stored in `users.db` (SQLite). Passwords are stored as salted PBKDF2-SHA256 hashes, not plain text.
- Use **Log out** in the sidebar to end the current session.
- This is suitable for a local academic/demo application. For public deployment, add HTTPS, rate limiting, password reset, and a production-grade identity provider.

# AI-Powered Research Agent (Local Ollama version)

Planning, analysis, and report generation use a local Ollama model. OpenAI API credits are not required. Tavily is still used for web search and requires a Tavily API key.

## 1. Install Ollama

Install Ollama for Windows from https://ollama.com/download. Open PowerShell and run:

```powershell
ollama pull llama3.2:3b
ollama list
```

Keep Ollama running while using the app. If the Ollama service is not running, open another PowerShell window and run `ollama serve`.

## 2. Set up this Python project

Open this project folder in VS Code (the folder containing `app.py` and `requirements.txt`). Then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.

## 3. Configure Tavily

Copy `.env.example` to a new file named `.env` in the same folder as `app.py`. Add your Tavily key:

```env
TAVILY_API_KEY=your_actual_tavily_key
OLLAMA_MODEL=llama3.2:3b
```

No `OPENAI_API_KEY` is needed. Do not share your API key or commit `.env` to GitHub.

## 4. Run

```powershell
python -m streamlit run app.py
```

Open the local Streamlit address shown in the terminal (normally http://localhost:8501).

## Deploy on Streamlit Community Cloud

Connect the GitHub repository to Streamlit Community Cloud and set the app's main file to `app.py`. Add the Tavily API key in the app's **Settings > Secrets**:

```toml
TAVILY_API_KEY = "your_actual_tavily_key"
```

Do not commit API keys, passwords, `.env`, or `users.db`. The local database contains account usernames and password hashes and is intentionally ignored by Git. Streamlit Cloud does not share your computer's local Ollama service; cloud deployment requires an Ollama server reachable from the app.

## Change the local model

Pull another Ollama model, then update `OLLAMA_MODEL` in `.env` to its exact local name. For example, `ollama pull qwen2.5:3b`, then set `OLLAMA_MODEL=qwen2.5:3b`. The model must be downloaded before use.
