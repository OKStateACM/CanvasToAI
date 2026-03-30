# Playwright Automation Workshop: Building AI Bots 🛠️

Welcome! In this workshop, you'll learn the fundamentals of web browser automation using **Playwright**. You'll build two automated bots that interact with **ChatGPT** and **Google Gemini**, respectively.

---

## 🎨 Workshop Overview

The goal is to complete two Python scripts by filling in the missing Playwright actions. Each file represents a different level of difficulty and covers unique automation concepts.

| File | Difficulty | What You'll Learn |
|:---|:---:|:---|
| [`chatgpt_automation.py`](file:///c:/Users/ricar/Documents/GitHub/CanvasToAI/workshop/chatgpt_automation.py) | ⭐⭐ | CSS Selectors, `page.fill()`, handling hidden file inputs. |
| [`gemini_automation.py`](file:///c:/Users/ricar/Documents/GitHub/CanvasToAI/workshop/gemini_automation.py) | ⭐⭐⭐ | Multi-selector retry loops, contenteditable divs, file chooser interception. |

---

## 🚀 Getting Started

### 1. Install Dependencies

Ensure you have a virtual environment active, then install the necessary tools:

```bash
pip install -r ../requirements.txt
playwright install chromium
```

### 2. Complete the Exercises

Open the files in your editor and look for the `_______` blanks.
> [!NOTE]
> Each blank has a **HINT** comment directly above it to guide you on which Playwright function or selector to use!

### 3. Test Your Work

Run the scripts directly to see them in action. Make sure you use the `setup_login()` method once to save your session cookies!

```bash
# Test your ChatGPT bot
python chatgpt_automation.py

# Test your Gemini bot
python gemini_automation.py
```

---

## 🧩 Learning Path

### Key Playwright Concepts Covered:

- **`launch_persistent_context()`**: Save your login sessions so you don't have to log in every time.
- **`page.wait_for_selector()`**: Handling dynamic web content that takes time to load.
- **`page.locator()`**: Finding elements using CSS, text, or ARIA roles.
- **`expect_file_chooser()`**: Automating the OS-level file picker dialog.
- **`keyboard.insert_text()`**: Interacting with complex "rich text" editors that standard `fill()` cannot handle.

---

## 💡 Troubleshooting Tips

- **Run in Non-Headless Mode**: Ensure `headless=False` is set (it's the default in these scripts) so you can see what the bot is doing!
- **Check DevTools**: If a selector isn't working, right-click the element in Chrome and select **Inspect**.
- **Retry Logic**: Websites like Gemini change their layout often; learn how to use loops to try multiple selectors!

> [!IMPORTANT]
> **Privacy**: These scripts use a local profile (`playwright_profile`) to store your cookies. **Never share this folder!**

Good luck, and happy automating! 🚀
