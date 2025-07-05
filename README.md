# ✍️ AI Book Writer – Z-BOT Suite v2.0

A full-featured desktop application powered by Google Gemini AI that allows you to generate entire books page-by-page with plot direction, editing, and PDF export — all inside a beautiful Python GUI built with Tkinter.

---

## 🚀 Features

- 🧠 Gemini 1.5 Flash-powered text generation
- 🖼️ Tkinter-based GUI — no terminal mess
- ✍️ Define book title, genre, tone, and key plot points
- 📄 Auto-generates optional chapter and section headings
- 🔁 Regenerate individual pages if needed
- 📝 Edit content before finalizing
- 📤 Export book as a styled, clean PDF using ReportLab

---

## 🧰 Tech Stack

| Tool                  | Purpose                        |
|-----------------------|--------------------------------|
| Python                | Programming language           |
| Tkinter               | GUI framework                  |
| google-generativeai   | Access to Gemini 1.5 Flash API |
| ReportLab             | PDF generation                 |
| Threading             | Async content generation       |

---

## ⚙️ Setup & Usage (Everything You Need)

To get started, clone the repository, set up a virtual environment, install dependencies, and run the app. Everything you need is listed below.

```bash
# Clone the repository
git clone https://github.com/AliZafar780/ai-book-writer
cd ai-book-writer

# Create and activate a virtual environment (Recommended)
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# OR install them manually
pip install google-generativeai reportlab

# Launch the app
python ai_writer.py
Once the app launches:

Paste your Gemini API Key

Fill in the Book Title, Author Name, Genre, Writing Tone, and Key Plot Points

Set the number of pages

Enable or disable auto-generated chapter/section headings

Click "Generate New Book"

Edit the content directly in the built-in editor

When satisfied, click "Save as PDF" to export

🧪 requirements.txt
Your requirements.txt file should include the following:

Copy
Edit
google-generativeai
reportlab
📁 Folder Structure
bash
Copy
Edit
ai-book-writer/
├── ai_writer.py           # Main GUI Application
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── output/                # (Optional) Folder for exported PDFs
