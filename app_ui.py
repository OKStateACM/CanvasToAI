import customtkinter as ctk
import threading

class AppUI(ctk.CTk):
    def __init__(self, canvas_bot, play_callback, setup_callback=None):
        super().__init__()
        self.canvas_bot = canvas_bot
        self.play_callback = play_callback
        self.setup_callback = setup_callback
        
        # Set a modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Canvas to ChatGPT Auto-Helper")
        self.geometry("650x550")
        
        self.title_label = ctk.CTkLabel(self, text="Upcoming Assignments", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=15)
        
        self.refresh_btn = ctk.CTkButton(self, text="Refresh Assignments", command=self.load_assignments_async, width=200)
        self.refresh_btn.pack(pady=5)
        
        if self.setup_callback:
            # Container for setup buttons
            setup_frame = ctk.CTkFrame(self, fg_color="transparent")
            setup_frame.pack(pady=5)
            
            self.setup_gpt_btn = ctk.CTkButton(setup_frame, text="⚙️ Setup ChatGPT", command=lambda: self._on_setup_click("chatgpt"), width=140, fg_color="#d48a00", hover_color="#b07300")
            self.setup_gpt_btn.pack(side="left", padx=10)
            
            self.setup_gemini_btn = ctk.CTkButton(setup_frame, text="⚙️ Setup Gemini", command=lambda: self._on_setup_click("gemini"), width=140, fg_color="#006eb8", hover_color="#004c80")
            self.setup_gemini_btn.pack(side="left", padx=10)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=600, height=350)
        self.scrollable_frame.pack(pady=15, padx=20, fill="both", expand=True)

    def load_assignments_async(self):
        self.refresh_btn.configure(text="Loading...", state="disabled")
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Run in thread so UI doesn't freeze
        threading.Thread(target=self._fetch_and_display, daemon=True).start()

    def _fetch_and_display(self):
        assignments = self.canvas_bot.get_upcoming_assignments()
        self.after(0, self._render_assignments, assignments)

    def _render_assignments(self, assignments):
        self.refresh_btn.configure(text="Refresh Assignments", state="normal")
        if not assignments:
            lbl = ctk.CTkLabel(self.scrollable_frame, text="No upcoming assignments found or Canvas API not configured.")
            lbl.pack(pady=40)
            return
            
        for assign in assignments:
            frame = ctk.CTkFrame(self.scrollable_frame)
            frame.pack(pady=10, padx=10, fill="x")
            
            title = assign.get('name', 'Unknown')
            due = assign.get('due_at')
            if due:
                due = due.split('T')[0]
            else:
                due = 'No due date'
                
            course_id = assign.get('course_id')
            assign_id = assign.get('id')
            
            # Left side texts
            text_frame = ctk.CTkFrame(frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            title_lbl = ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w", justify="left")
            title_lbl.pack(fill="x")
            
            due_lbl = ctk.CTkLabel(text_frame, text=f"Due: {due}", anchor="w", text_color="gray")
            due_lbl.pack(fill="x")
            
            # Buttons container
            btns_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btns_frame.pack(side="right", padx=15, pady=15)
            
            btn_gemini = ctk.CTkButton(
                btns_frame, 
                text="▶ Ask Gemini", 
                fg_color="#006eb8",  # Google blue-ish
                hover_color="#004c80",
                width=120,
                command=lambda c=course_id, a=assign_id, n=title: self._on_play_click(c, a, n, "gemini")
            )
            btn_gemini.pack(side="top", pady=(0, 5))

            btn_gpt = ctk.CTkButton(
                btns_frame, 
                text="▶ Ask ChatGPT", 
                fg_color="#10a37f", # ChatGPT green
                hover_color="#0b7a5e",
                width=120,
                command=lambda c=course_id, a=assign_id, n=title: self._on_play_click(c, a, n, "chatgpt")
            )
            btn_gpt.pack(side="top")

    def _on_play_click(self, course_id, assign_id, title, ai_target):
        btn_states = []
        for widget in self.winfo_children():
            # Basic disable to prevent double clicking anything
            if isinstance(widget, ctk.CTkButton):
                widget.configure(state="disabled")
                
        def run():
            self.play_callback(course_id, assign_id, title, ai_target)
            # Re-enable all buttons safely via after mainloop
            self.after(0, self._enable_all_buttons)
                
        threading.Thread(target=run, daemon=True).start()
        
    def _enable_all_buttons(self):
        for frame in [self, self.scrollable_frame]:
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state="normal")
                # recursively enable within nested frames
                if isinstance(child, ctk.CTkFrame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ctk.CTkButton):
                            subchild.configure(state="normal")

    def _on_setup_click(self, target):
        self.setup_gpt_btn.configure(state="disabled")
        self.setup_gemini_btn.configure(state="disabled")
        
        def run():
            self.setup_callback(target)
            self.after(0, lambda: self.setup_gpt_btn.configure(state="normal"))
            self.after(0, lambda: self.setup_gemini_btn.configure(state="normal"))
            
        threading.Thread(target=run, daemon=True).start()
