import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox, filedialog
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import threading
import re

# Z-BOT: Hard limits to prevent runaway costs and API abuse.
MAX_PAGES = 50
COST_PER_PAGE_ESTIMATE = 0.001  # Rough USD estimate per page (Gemini API)

# Z-BOT: Main application class. This holds all the goddamn windows and logic.
class BookWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Z-BOT Advanced Book Generation Suite v2.0")
        self.root.geometry("1200x800")

        # This will hold the generated text for each page
        self.pages_content = []

        # --- Main Layout ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Left Panel: Controls ---
        control_frame = ttk.LabelFrame(main_frame, text="Generation Controls", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # API Key
        ttk.Label(control_frame, text="Gemini API Key:").pack(fill=tk.X, pady=2)
        self.api_key_entry = ttk.Entry(control_frame, width=40, show="*")
        self.api_key_entry.pack(fill=tk.X, pady=2)

        # Book Details
        ttk.Label(control_frame, text="Book Title:").pack(fill=tk.X, pady=5)
        self.title_entry = ttk.Entry(control_frame, width=40)
        self.title_entry.pack(fill=tk.X, pady=2)

        ttk.Label(control_frame, text="Author Name:").pack(fill=tk.X, pady=5)
        self.author_entry = ttk.Entry(control_frame, width=40)
        self.author_entry.pack(fill=tk.X, pady=2)

        ttk.Label(control_frame, text="Category/Genre:").pack(fill=tk.X, pady=5)
        self.category_entry = ttk.Entry(control_frame, width=40)
        self.category_entry.pack(fill=tk.X, pady=2)

        ttk.Label(control_frame, text="Number of Pages:").pack(fill=tk.X, pady=5)
        self.page_count_spinbox = ttk.Spinbox(control_frame, from_=1, to=MAX_PAGES, width=5)
        self.page_count_spinbox.pack(fill=tk.X, pady=2)
        self.page_count_spinbox.set(10)

        # Advanced Settings
        adv_frame = ttk.LabelFrame(control_frame, text="Writing Instructions", padding="10")
        adv_frame.pack(fill=tk.X, pady=15)
        
        self.add_headings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(adv_frame, text="Auto-generate Chapter Titles/Headings", variable=self.add_headings_var).pack(anchor='w')

        ttk.Label(adv_frame, text="Writing Style/Tone:").pack(fill=tk.X, pady=2)
        self.style_entry = ttk.Entry(adv_frame, width=40)
        self.style_entry.insert(0, "Engaging and descriptive")
        self.style_entry.pack(fill=tk.X, pady=2)

        ttk.Label(adv_frame, text="Key Plot Points (one per line):").pack(fill=tk.X, pady=2)
        self.plot_points_text = tk.Text(adv_frame, height=5, width=38)
        self.plot_points_text.pack(fill=tk.X, pady=2)
        
        # Generation Button
        self.generate_button = ttk.Button(control_frame, text="GENERATE NEW BOOK", command=self.start_generation_thread)
        self.generate_button.pack(fill=tk.X, pady=10)

        # --- Page Regeneration Section ---
        regen_frame = ttk.LabelFrame(control_frame, text="Page Regeneration", padding="10")
        regen_frame.pack(fill=tk.X, pady=15)

        ttk.Label(regen_frame, text="Page to Regenerate:").pack(side=tk.LEFT, padx=5)
        self.regen_page_spinbox = ttk.Spinbox(regen_frame, from_=1, to=MAX_PAGES, width=5)
        self.regen_page_spinbox.pack(side=tk.LEFT)
        
        self.regen_button = ttk.Button(regen_frame, text="Regen", command=self.start_regen_thread, state='disabled')
        self.regen_button.pack(side=tk.RIGHT, padx=5)

        # --- Right Panel: Editor ---
        editor_frame = ttk.LabelFrame(main_frame, text="Book Content Editor", padding="10")
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.editor_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, font=("Arial", 12))
        self.editor_text.pack(fill=tk.BOTH, expand=True)
        self.editor_text.configure(state='disabled')

        # --- Bottom Panel: Actions & Status ---
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(bottom_frame, text="Status: Idle. Provide API Key and details.")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.progress_bar = ttk.Progressbar(bottom_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.save_pdf_button = ttk.Button(bottom_frame, text="Save as PDF", command=self.save_as_pdf, state='disabled')
        self.save_pdf_button.pack(side=tk.RIGHT, padx=5)

    def _ui(self, callback):
        """Schedule a UI update on the main thread (thread-safe wrapper for Tkinter)."""
        self.root.after(0, callback)

    def _validate_generation_inputs(self):
        """Validate all inputs before starting generation. Returns (is_valid, num_pages)."""
        try:
            num_pages = int(self.page_count_spinbox.get())
        except ValueError:
            messagebox.showerror("Input Error", "Number of pages must be a valid integer.")
            return False, 0

        if num_pages < 1:
            messagebox.showerror("Input Error", "Number of pages must be at least 1.")
            return False, 0

        if num_pages > MAX_PAGES:
            messagebox.showerror(
                "Input Error",
                f"Maximum allowed pages is {MAX_PAGES}. You requested {num_pages}.\n"
                f"Please reduce the page count."
            )
            return False, 0

        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Input Error", "API Key is required.")
            return False, 0

        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Input Error", "Book title is required.")
            return False, 0

        # Cost confirmation dialog before making API calls
        estimated_cost = num_pages * COST_PER_PAGE_ESTIMATE
        if not messagebox.askyesno(
            "Confirm Generation",
            f"Please confirm the following:\n\n"
            f"  Title: {title}\n"
            f"  Pages: {num_pages}\n"
            f"  Estimated Cost: ${estimated_cost:.4f}\n\n"
            f"Proceed with generation?"
        ):
            return False, 0

        return True, num_pages

    def _get_model(self):
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Error", "API Key is fucking mandatory.")
            return None
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e:
            messagebox.showerror("API Error", f"Couldn't configure the Gemini API. Check your key. Error: {e}")
            return None

    def _lock_controls(self):
        self._ui(lambda: self.generate_button.config(state='disabled'))
        self._ui(lambda: self.save_pdf_button.config(state='disabled'))
        self._ui(lambda: self.regen_button.config(state='disabled'))

    def _unlock_controls(self):
        self._ui(lambda: self.generate_button.config(state='normal'))
        if self.pages_content:
            self._ui(lambda: self.save_pdf_button.config(state='normal'))
            self._ui(lambda: self.regen_button.config(state='normal'))

    def _update_editor_view(self):
        """Thread-safe editor view update."""
        self._ui(self._do_update_editor_view)

    def _do_update_editor_view(self):
        """Actual editor update — runs on main thread via _ui()."""
        self.editor_text.configure(state='normal')
        self.editor_text.delete('1.0', tk.END)
        for i, page_text in enumerate(self.pages_content):
            self.editor_text.insert(tk.END, f"--- PAGE {i+1} ---\n\n")
            self.editor_text.insert(tk.END, page_text)
            self.editor_text.insert(tk.END, "\n\n")
        self.editor_text.configure(state='normal') # Keep editable

    def start_generation_thread(self):
        self._lock_controls()
        threading.Thread(target=self.generate_book, daemon=True).start()

    def start_regen_thread(self):
        self._lock_controls()
        threading.Thread(target=self.regenerate_specific_page, daemon=True).start()

    # Z-BOT: Main book generation logic.
    def generate_book(self):
        # Validate inputs before making any API calls
        is_valid, num_pages = self._validate_generation_inputs()
        if not is_valid:
            self._unlock_controls()
            return

        model = self._get_model()
        if not model:
            self._unlock_controls()
            return

        self.pages_content = []
        self._ui(lambda: self.editor_text.configure(state='normal'))
        self._ui(lambda: self.editor_text.delete('1.0', tk.END))
        
        title = self.title_entry.get()
        category = self.category_entry.get()
        style = self.style_entry.get()
        plot_points = self.plot_points_text.get("1.0", tk.END).strip()
        add_headings = self.add_headings_var.get()

        self._ui(lambda: self.progress_bar.configure(maximum=num_pages, value=0))

        for i in range(num_pages):
            current_page = i + 1
            self._ui(lambda p=current_page, n=num_pages: self.status_label.config(
                text=f"Status: Generating Page {p} of {n}..."))

            previous_text = self.pages_content[-1][-200:] if self.pages_content else "This is the beginning of the book."
            
            heading_instruction = ""
            if add_headings:
                # Tell it to add a chapter title every 5-7 pages, or a heading sometimes
                if i == 0 or i % 6 == 0:
                    heading_instruction = 'Start this page with a new chapter title, formatted as "[CHAPTER]: Your Title Here".'
                else:
                    heading_instruction = 'You may optionally include a minor heading, formatted as "[HEADING]: Your Heading Here".'

            prompt = f"""
            You are a creative author writing a book titled '{title}' in the {category} genre.
            Writing Style: {style}. Key Plot Points: {plot_points}.
            Total desired pages: {num_pages}. You are currently writing page {current_page}.
            The last few sentences from the previous page were: "{previous_text}"
            {heading_instruction}
            Continue the story from there. Write a full page (300-400 words) for page {current_page}.
            Do not write headers like "Page X". Only use the specified [CHAPTER] or [HEADING] formats if you add one. Just write the content.
            """

            try:
                response = model.generate_content(prompt)
                self.pages_content.append(response.text)
                self._ui(lambda v=current_page: self.progress_bar.configure(value=v))
            except Exception as e:
                error_msg = str(e)
                self._ui(lambda msg=error_msg, p=current_page: messagebox.showerror(
                    "Generation Error", f"AI failed on page {p}. Error: {msg}"))
                self._ui(lambda: self.status_label.config(text="Status: AI Generation Failed."))
                self._unlock_controls()
                return

        self._update_editor_view()
        self._ui(lambda: self.status_label.config(text="Status: Generation Complete. Edit or save."))
        self._unlock_controls()

    # Z-BOT: For when you inevitably fuck up a page.
    def regenerate_specific_page(self):
        model = self._get_model()
        if not model:
            self._unlock_controls()
            return

        try:
            page_num = int(self.regen_page_spinbox.get())
            page_index = page_num - 1
            if not (0 <= page_index < len(self.pages_content)):
                self._ui(lambda: messagebox.showerror("Error", "Invalid page number."))
                self._unlock_controls()
                return
        except ValueError:
            self._ui(lambda: messagebox.showerror("Error", "Page number must be a valid integer."))
            self._unlock_controls()
            return
            
        self._ui(lambda p=page_num: self.status_label.config(text=f"Status: Regenerating page {p}..."))

        # Get context from surrounding pages for better coherence.
        prev_page_context = self.pages_content[page_index - 1][-200:] if page_index > 0 else "This is the beginning of the book."
        next_page_context = self.pages_content[page_index + 1][:200] if page_index < len(self.pages_content) - 1 else "This is the end of the book."
        
        title = self.title_entry.get()
        category = self.category_entry.get()
        style = self.style_entry.get()
        plot_points = self.plot_points_text.get("1.0", tk.END).strip()

        prompt = f"""
        You are a creative author revising a book titled '{title}' in the {category} genre.
        Your task is to REWRITE page {page_num}.
        The end of the PREVIOUS page is: "{prev_page_context}"
        The start of the NEXT page is: "{next_page_context}"
        Rewrite page {page_num} to flow smoothly between these two points. Maintain the style: '{style}'.
        Adhere to the key plot points: {plot_points}.
        Do not write headers like "Page X". Just provide the new text for this single page.
        """

        try:
            response = model.generate_content(prompt)
            self.pages_content[page_index] = response.text
            self._ui(lambda p=page_num: self.status_label.config(text=f"Status: Page {p} regenerated."))
            self._update_editor_view()
        except Exception as e:
            error_msg = str(e)
            self._ui(lambda msg=error_msg, p=page_num: messagebox.showerror(
                "Generation Error", f"AI failed to regenerate page {p}. Error: {msg}"))
            self._ui(lambda: self.status_label.config(text="Status: AI Regeneration Failed."))
        
        self._unlock_controls()


    # Z-BOT: Now dump the edited text into a PDF that doesn't look like total shit.
    def save_as_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")])
        if not file_path:
            return

        self.status_label.config(text="Status: Saving to PDF...")
        try:
            full_text = self.editor_text.get('1.0', tk.END)
            edited_pages = [p.split("---\n\n")[1].strip() for p in full_text.split("--- PAGE ")[1:]]

            doc = SimpleDocTemplate(file_path, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
            
            # Z-BOT: Styles. Because your last PDF looked like it was made in notepad.
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='TitlePage', fontSize=24, leading=28, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='Author', fontSize=16, leading=20, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='ChapterTitle', fontSize=18, leading=22, spaceBefore=24, spaceAfter=12, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='Heading', fontSize=14, leading=18, spaceBefore=12, spaceAfter=6))
            styles.add(ParagraphStyle(name='Body', fontSize=11, leading=14, alignment=TA_JUSTIFY, firstLineIndent=20))

            story = []
            
            # Title Page
            story.append(Spacer(1, 2 * 72)) # 2 inches of space
            story.append(Paragraph(self.title_entry.get(), styles['TitlePage']))
            story.append(Spacer(1, 0.25 * 72))
            story.append(Paragraph(f"By {self.author_entry.get()}", styles['Author']))
            story.append(PageBreak())

            # Z-BOT: Now we parse the AI's output for the markers it was told to add.
            for page_content in edited_pages:
                lines = page_content.split('\n')
                for line in lines:
                    if line.strip().startswith("[CHAPTER]:"):
                        title_text = line.replace("[CHAPTER]:", "").strip()
                        story.append(Paragraph(title_text, styles['ChapterTitle']))
                    elif line.strip().startswith("[HEADING]:"):
                        heading_text = line.replace("[HEADING]:", "").strip()
                        story.append(Paragraph(heading_text, styles['Heading']))
                    elif line.strip():
                        p = Paragraph(line, styles['Body'])
                        story.append(p)
                story.append(Spacer(1, 12)) # Space between paragraphs from different pages

            doc.build(story)
            self.status_label.config(text="Status: PDF Saved Successfully.")
            messagebox.showinfo("Success", f"Book saved successfully to {file_path}")
        except Exception as e:
            self.status_label.config(text="Status: PDF Save Failed.")
            messagebox.showerror("PDF Error", f"An error occurred while saving the PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookWriterApp(root)
    root.mainloop()