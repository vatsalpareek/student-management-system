import customtkinter as ctk
from tkinter import ttk, messagebox
import db

class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Main Grid
        self.grid_columnconfigure(0, weight=4) # Form (Increased Width)
        self.grid_columnconfigure(1, weight=6) # Table
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT: ENTRY FORM (Vertical Optimization) ---
        self.form_frame = ctk.CTkFrame(self, corner_radius=15)
        self.form_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(self.form_frame, text="Registration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.vars = {
            "roll_no": ctk.StringVar(), "name": ctk.StringVar(),
            "email": ctk.StringVar(), "phone": ctk.StringVar(),
            "dob": ctk.StringVar(), "gender": ctk.StringVar(value="Male"),
            "dept": ctk.StringVar(), "semester": ctk.StringVar(value="Semester 1")
        }

        # Compact Fields
        self.create_compact_field("Roll Number", self.vars["roll_no"])
        self.create_compact_field("Full Name", self.vars["name"])
        self.create_compact_field("Email", self.vars["email"])
        self.create_compact_field("Phone", self.vars["phone"])
        
        # Row for Gender & Dept (Side by side to save height)
        gd_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        gd_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(gd_frame, text="Gender").grid(row=0, column=0, sticky="w")
        ctk.CTkSegmentedButton(gd_frame, values=["Male", "Female"], variable=self.vars["gender"], height=26, width=120).grid(row=1, column=0, padx=(0, 5))
        
        ctk.CTkLabel(gd_frame, text="Dept").grid(row=0, column=1, sticky="w")
        self.dept_dropdown = ctk.CTkOptionMenu(gd_frame, variable=self.vars["dept"], height=26, width=120)
        self.dept_dropdown.grid(row=1, column=1)

        # Semester
        ctk.CTkLabel(self.form_frame, text="Semester").pack(anchor="w", padx=15)
        ctk.CTkOptionMenu(self.form_frame, values=["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"], variable=self.vars["semester"], height=28).pack(fill="x", padx=15, pady=(0, 10))

        self.refresh_departments()

        # Action Buttons (Fixed 2x2 Grid for absolute visibility)
        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkButton(btn_frame, text="Add Student", fg_color="#27AE60", command=self.add_student).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Update", command=self.update_student).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Delete", fg_color="#E74C3C", command=self.delete_student).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Clear", fg_color="gray", command=self.clear_fields).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- RIGHT: TABLE ---
        self.table_frame = ctk.CTkFrame(self, corner_radius=15)
        self.table_frame.grid(row=0, column=1, sticky="nsew")

        # Search
        search_f = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_f.pack(fill="x", padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(search_f, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self.search())
        ctk.CTkButton(search_f, text="Find", width=50, command=self.search).pack(side="left")

        # Treeview
        self.tree = ttk.Treeview(self.table_frame, columns=("r", "n", "d", "s"), show="headings")
        for col, head in zip(("r", "n", "d", "s"), ("Roll", "Name", "Dept", "Sem")):
            self.tree.heading(col, text=head)
        self.tree.column("r", width=50)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self.get_cursor)

        self.load_students()

    def create_compact_field(self, label, var):
        ctk.CTkLabel(self.form_frame, text=label).pack(anchor="w", padx=15)
        ctk.CTkEntry(self.form_frame, textvariable=var, height=28).pack(fill="x", padx=15, pady=(0, 5))

    def refresh_departments(self):
        depts = db.get_departments()
        self.dept_map = {d['name']: d['id'] for d in depts}
        names = list(self.dept_map.keys())
        if names:
            self.dept_dropdown.configure(values=names)
            self.vars["dept"].set(names[0])

    def add_student(self):
        data = (self.vars["roll_no"].get(), self.vars["name"].get(), self.vars["email"].get(),
                self.vars["phone"].get(), "", self.vars["gender"].get(), "",
                self.dept_map.get(self.vars["dept"].get()), self.vars["semester"].get())
        if not data[0]: return
        success, msg = db.add_student(data)
        if success: self.load_students(); self.clear_fields()
        else: messagebox.showerror("Error", msg)

    def load_students(self):
        self.tree.delete(*self.tree.get_children())
        for row in db.get_all_students():
            self.tree.insert("", "end", values=(row['roll_no'], row['name'], row['dept_name'], row['semester']))

    def search(self):
        q = self.search_entry.get()
        self.tree.delete(*self.tree.get_children())
        for row in db.search_students(q):
            self.tree.insert("", "end", values=(row['roll_no'], row['name'], row['dept_name'], row['semester']))

    def get_cursor(self, event):
        sel = self.tree.focus()
        if not sel: return
        row = self.tree.item(sel)['values']
        self.vars["roll_no"].set(row[0]); self.vars["name"].set(row[1])

    def update_student(self): messagebox.showinfo("Info", "Coming in next update!")
    def delete_student(self):
        r = self.vars["roll_no"].get()
        if r and messagebox.askyesno("!", f"Delete {r}?"):
            db.delete_student(r); self.load_students(); self.clear_fields()

    def clear_fields(self):
        for v in self.vars.values(): v.set("")
        self.vars["gender"].set("Male")
