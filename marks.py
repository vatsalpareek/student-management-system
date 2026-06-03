import customtkinter as ctk
from tkinter import messagebox, ttk
import db

class MarksFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT: SELECTION & FORM ---
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="Academic Entry", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        # Student Selection
        self.search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=20)
        
        self.roll_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search by Name, Roll, Email, Dept...")
        self.roll_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.roll_search.bind("<Return>", lambda e: self.find_student())
        self.roll_search.bind("<KeyRelease>", self.show_recommendations)
        
        ctk.CTkButton(self.search_frame, text="Find", width=60, command=self.find_student).pack(side="left")

        # Recommendations Frame (Hidden initially)
        self.rec_frame = ctk.CTkScrollableFrame(self.left_frame, height=120, fg_color="transparent", border_width=1, border_color=("gray70", "gray30"))

        # Info Display
        self.info_label = ctk.CTkLabel(self.left_frame, text="Search a student to begin", text_color="gray")
        self.info_label.pack(pady=10)

        # Marks Form (Hidden until student found)
        self.form_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        
        self.subject_var = ctk.StringVar()
        self.marks_var = ctk.StringVar()

        ctk.CTkLabel(self.form_container, text="Subject Name").pack(anchor="w", padx=20)
        ctk.CTkEntry(self.form_container, textvariable=self.subject_var).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.form_container, text="Marks Obtained").pack(anchor="w", padx=20)
        ctk.CTkEntry(self.form_container, textvariable=self.marks_var).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(self.form_container, text="Save Marks", command=self.save_marks).pack(fill="x", padx=20, pady=20)

        # --- RIGHT: MARKS LIST & CALCULATION ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(self.right_frame, text="Marksheet Preview", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.tree = ttk.Treeview(self.right_frame, columns=("subject", "marks", "max"), show="headings")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("marks", text="Marks")
        self.tree.heading("max", text="Max Marks")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.summary_label = ctk.CTkLabel(self.right_frame, text="Total: -- | Percentage: --%", font=ctk.CTkFont(size=16, weight="bold"))
        self.summary_label.pack(pady=20)

        self.selected_student = None

    def show_recommendations(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            if event.keysym == "Escape":
                self.rec_frame.pack_forget()
            return

        q = self.roll_search.get().strip()
        if not q:
            self.rec_frame.pack_forget()
            return

        results = db.search_students(q)
        if not results:
            self.rec_frame.pack_forget()
            return

        # Clear old recommendations
        for widget in self.rec_frame.winfo_children():
            widget.destroy()

        # Populate new recommendations
        for row in results[:5]:
            btn = ctk.CTkButton(
                self.rec_frame,
                text=f"{row['roll_no']} - {row['name']}",
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                height=30,
                command=lambda r=row: self.select_recommendation(r)
            )
            btn.pack(fill="x", pady=1)

        # Pack recommendation frame right below search input
        self.rec_frame.pack(fill="x", padx=20, pady=(5, 10), after=self.search_frame)

    def select_recommendation(self, row):
        self.roll_search.delete(0, "end")
        self.roll_search.insert(0, row['roll_no'])
        self.rec_frame.pack_forget()
        self.find_student()

    def find_student(self):
        self.rec_frame.pack_forget()  # Hide recommendations
        roll = self.roll_search.get()
        results = db.search_students(roll)
        if results:
            self.selected_student = results[0]
            self.info_label.configure(
                text=f"Student: {self.selected_student['name']}\nDept: {self.selected_student['dept_name']}",
                text_color="white"
            )
            self.form_container.pack(fill="x")
            self.load_marks()
        else:
            messagebox.showerror("Error", "Student not found!")
            self.form_container.pack_forget()

    def save_marks(self):
        if not self.selected_student: return
        
        sub = self.subject_var.get()
        mks = self.marks_var.get()
        
        if not sub or not mks:
            messagebox.showwarning("Warning", "Fill all fields")
            return
            
        try:
            mks_int = int(mks)
            db.add_marks(self.selected_student['roll_no'], sub, mks_int)
            self.load_marks()
            self.subject_var.set("")
            self.marks_var.set("")
        except ValueError:
            messagebox.showerror("Error", "Marks must be a number")

    def load_marks(self):
        if not self.selected_student: return
        
        self.tree.delete(*self.tree.get_children())
        marks_list = db.get_student_marks(self.selected_student['roll_no'])
        
        total = 0
        count = 0
        for row in marks_list:
            self.tree.insert("", "end", values=(row['subject'], row['marks_obtained'], row['max_marks']))
            total += row['marks_obtained']
            count += 1
            
        if count > 0:
            perc = (total / (count * 100)) * 100
            self.summary_label.configure(text=f"Total: {total} | Percentage: {perc:.2f}%")
        else:
            self.summary_label.configure(text="Total: 0 | Percentage: 0%")
