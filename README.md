# 🎓 Playwright Automation Workshop

Welcome! In this workshop you'll learn how to automate web browsers using **Playwright** by building bots that interact with **ChatGPT** and **Google Gemini**.

## 📋 Prerequisites

- Python 3.9+
- Google Chrome installed
- A ChatGPT account and/or a Google account

## 🚀 Getting Started

### 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Up Environment Variables


Edit `.env` with your Canvas LMS credentials (needed only if you want to pull assignments automatically).

### 3. Complete the Workshop Files

Open the two automation files and **fill in the blanks** (`_______`):

| File | Difficulty | What You'll Learn |
|------|-----------|-------------------|
| `chatgpt_automation.py` | ⭐⭐ Intermediate | Selectors, `fill()`, hidden file inputs, `data-testid` |
| `gemini_automation.py` | ⭐⭐⭐ Advanced | Multi-selector retry loops, contenteditable divs, file chooser interception |

Each blank has a **HINT** comment right above it to guide you!

### 4. Test Your Work

```python
# Test ChatGPT bot
python chatgpt_automation.py

# Test Gemini bot
python gemini_automation.py
```

## 🧩 Key Playwright Concepts

| Concept | ChatGPT File | Gemini File |
|---------|-------------|-------------|
| Persistent Context | ✅ | ✅ |
| `page.goto()` | ✅ | ✅ |
| `page.wait_for_selector()` | ✅ | ✅ |
| `page.fill()` | ✅ | |
| `page.locator()` | ✅ | ✅ |
| `set_input_files()` | ✅ | |
| `expect_file_chooser()` | ✅ | ✅ |
| `keyboard.insert_text()` | | ✅ |
| `keyboard.press()` | ✅ | ✅ |
| Multi-selector resilience | | ✅ |
| Retry loops | | ✅ |

## 💡 Tips

- **Run `setup_login()` first!** You need to log in once so your session cookies get saved.
- **Use `headless=False`** — you need to see the browser to debug your selectors!
- **Check DevTools** — Right-click → Inspect to find element selectors on the page.
- If a selector doesn't work, try alternatives: `data-testid`, `aria-label`, `:has-text()`.

Good luck! 🚀
