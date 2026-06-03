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

    def validate_fields(self):
        import re
        roll_no = self.vars["roll_no"].get().strip()
        name = self.vars["name"].get().strip()
        email = self.vars["email"].get().strip()
        phone = self.vars["phone"].get().strip()

        if not roll_no or not name or not email or not phone:
            messagebox.showwarning("Validation Error", "All fields (Roll Number, Full Name, Email, Phone) are mandatory!")
            return False

        if not roll_no.isalnum():
            messagebox.showwarning("Validation Error", "Roll Number must be alphanumeric only (no spaces or special characters)!")
            return False

        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, email):
            messagebox.showwarning("Validation Error", "Please enter a valid email address (e.g., user@domain.com)!")
            return False

        if not phone.isdigit() or len(phone) != 10:
            messagebox.showwarning("Validation Error", "Phone number must be exactly 10 digits containing only numbers!")
            return False

        return True

    def add_student(self):
        if not self.validate_fields():
            return
            
        data = (
            self.vars["roll_no"].get().strip(),
            self.vars["name"].get().strip(),
            self.vars["email"].get().strip(),
            self.vars["phone"].get().strip(),
            "", # dob
            self.vars["gender"].get(),
            "", # address
            self.dept_map.get(self.vars["dept"].get()),
            self.vars["semester"].get()
        )
        
        success, msg = db.add_student(data)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)

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
        if not row: return
        roll_no = row[0]
        
        student = db.get_student(roll_no)
        if student:
            self.vars["roll_no"].set(student['roll_no'])
            self.vars["name"].set(student['name'])
            self.vars["email"].set(student['email'] if student['email'] else "")
            self.vars["phone"].set(student['phone'] if student['phone'] else "")
            self.vars["gender"].set(student['gender'] if student['gender'] else "Male")
            self.vars["semester"].set(student['semester'] if student['semester'] else "Sem 1")
            if student['dept_name'] in self.dept_map:
                self.vars["dept"].set(student['dept_name'])

    def update_student(self):
        roll_no = self.vars["roll_no"].get().strip()
        if not roll_no:
            messagebox.showwarning("Warning", "Please select a student from the list or enter a Roll Number to update.")
            return
            
        student = db.get_student(roll_no)
        if not student:
            messagebox.showerror("Error", f"No student found with Roll Number '{roll_no}'.")
            return
            
        if not self.validate_fields():
            return
            
        data = (
            self.vars["name"].get().strip(),
            self.vars["email"].get().strip(),
            self.vars["phone"].get().strip(),
            "", # dob
            self.vars["gender"].get(),
            "", # address
            self.dept_map.get(self.vars["dept"].get()),
            self.vars["semester"].get()
        )
        
        success, msg = db.update_student(roll_no, data)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)
    def delete_student(self):
        r = self.vars["roll_no"].get()
        if r and messagebox.askyesno("!", f"Delete {r}?"):
            db.delete_student(r); self.load_students(); self.clear_fields()

    def clear_fields(self):
        for v in self.vars.values(): v.set("")
        self.vars["gender"].set("Male")
