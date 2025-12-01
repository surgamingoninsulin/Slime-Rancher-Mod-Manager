import tkinter as tk
from tkinter import ttk

class DeleteConfirmDialog(tk.Toplevel):
    def __init__(self, parent, controller, filenames):
        super().__init__(parent)
        self.controller = controller
        self.filenames = filenames # This is now a list
        
        self.title("Confirm Deletion")
        self.geometry("420x190") # Slightly larger for long messages
        # Slime Rancher geïnspireerde achtergrond
        self.configure(bg="#fdf6ff")

        # Make modal
        self.transient(parent)
        self.grab_set()

        if len(filenames) == 1:
            # Clean name for display if only one item
            display_name = filenames[0].replace(".dll", "").replace(".disabled", "")
            msg = f"Are you sure you want to permanently delete '{display_name}' from disk?"
        else:
            msg = f"Are you sure you want to permanently delete {len(filenames)} selected mods from disk?"

        ttk.Label(self, text=msg, wraplength=360, justify="center").pack(pady=20, padx=10)

        btn_frame = ttk.Frame(self, style="Card.TFrame")
        btn_frame.pack(pady=10, padx=10)

        ttk.Button(btn_frame, text="Yes, Delete", command=self.confirm).pack(side="left", padx=10, pady=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=10, pady=5)

    def confirm(self):
        # Pass the list of filenames to the controller
        self.controller.delete_mod_logic(self.filenames)
        self.destroy()