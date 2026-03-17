# ✍️ AI Book Writer - Z-BOT Suite v2.0

> A full-featured desktop application powered by Google Gemini AI that allows you to generate entire books page-by-page with plot direction, editing, and PDF export

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?style=flat" alt="Tkinter" />
  <img src="https://img.shields.io/badge/AI-Gemini-orange?style=flat&logo=google" alt="Gemini" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat" alt="License" />
</p>

---

## ✨ Features

| Feature | Description |
|:--------|:------------|
| 🧠 **Gemini AI** | Powered by Google Gemini 1.5 Flash |
| 🖼️ **Tkinter GUI** | Beautiful Python GUI |
| ✍️ **Book Generation** | Define title, genre, tone, plot points |
| 📄 **Auto Headings** | Optional chapter/section headings |
| 🔁 **Regeneration** | Regenerate individual pages |
| 📝 **Edit Content** | Edit before finalizing |
| 📤 **PDF Export** | Export as styled PDF |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/AliZafar780/ai-book-writer.git
cd ai-book-writer

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 🛠️ Tech Stack

| Tool | Purpose |
|:-----|:--------|
| Python | Programming language |
| Tkinter | GUI framework |
| google-generativeai | Gemini 1.5 Flash API |
| ReportLab | PDF generation |
| Threading | Async content generation |

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- Internet connection

## ⚙️ Configuration

Set your API key in the app or as environment variable:
```bash
export GEMINI_API_KEY=your_api_key
```

## 📁 Project Structure

```
ai-book-writer/
├── main.py            # Main application
├── book_generator.py  # AI generation logic
├── gui.py            # Tkinter interface
├── pdf_exporter.py   # PDF generation
└── requirements.txt  # Dependencies
```

## 📜 License

MIT License

---

*Write your story with AI 📖*
