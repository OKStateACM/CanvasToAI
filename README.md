# CanvasToAI 🎓🤖

**CanvasToAI** is a synchronization tool that connects your **Canvas LMS** assignments to Generative AI engines (**ChatGPT** and **Google Gemini**). 

The application automates the tedious task of manually copying assignment details and uploading files to your favorite AI assistant by using **Playwright** behind the scenes. 


## ✨ Features

- 🔗 **Canvas API Integration**: Fetches your upcoming, active assignments automatically.
- 📁 **Auto-File Handling**: Downloads all assignment attachments (PDFs, PPTXs, Source files) and prepares them for the AI.
- 🤖 **Multi-AI Support**: Fully automated, browser-based interaction with **ChatGPT** and **Google Gemini**.
- 🔐 **Persistent Sessions**: Log in once, and the bot remembers your session for future runs.
- 🖥️ **Interactive UI**: A simple, user-friendly interface powered by `tkinter`.

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.9+**
- **Google Chrome** installed (used for better bot detection avoidance).

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browser drivers
playwright install chromium
```

### 3. Configuration

Rename `.env.example` to `.env` and fill in your details:

```env
CANVAS_DOMAIN=https://canvas.yourschool.edu
CANVAS_API_TOKEN=your_token_here
```

> [!TIP]
> To get your **Canvas API Token**, go to **Canvas** → **Account** → **Settings** → **New Access Token**.

---

## 🎮 Usage

Run the main application:

```bash
python main.py
```

### Initial Setup
1. Open the app and click the **Setup Login** button for your preferred AI (ChatGPT or Gemini).
2. A browser window will open; log in to your account manually.
3. Close the browser when finished. The app will save your session!

### Interacting with Assignments
1. Refresh the assignment list in the UI.
2. Select an assignment and pick your AI target.
3. Click **Play** ▶️ — Watch the bot fetch context, upload files, and prepare your prompt!

---

## 🎓 Workshop

Interested in learning how this works? Check out the workshop folder for step-by-step exercises to build your own Playwright automation bots from scratch!
---

## ⚖️ License

Made for **OKState ACM**. For educational use only.
