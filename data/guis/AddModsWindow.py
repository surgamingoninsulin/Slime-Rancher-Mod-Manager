import tkinter as tk
from tkinter import ttk, filedialog

class AddModDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Install Mod")
        self.geometry("420x160")
        # Slime Rancher geïnspireerde achtergrond
        self.configure(bg="#fdf6ff")

        # Make modal (block main window)
        self.transient(parent)
        self.grab_set()

        lbl = ttk.Label(self, text="Select a .dll file to install:")
        lbl.pack(pady=15, padx=10)

        btn_frame = ttk.Frame(self, style="Card.TFrame")
        btn_frame.pack(pady=10, padx=10, fill="x")

        ttk.Button(btn_frame, text="Browse...", command=self.browse_file).pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Mod DLL",
            filetypes=[("DLL Files", "*.dll")]
        )
        
        if file_path:
            # Call the controller
            self.controller.add_mod_logic(file_path)
            self.destroy()