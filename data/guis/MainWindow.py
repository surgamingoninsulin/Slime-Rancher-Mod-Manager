import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ModListFrame(ttk.Frame):
    # Accept initial sort state
    def __init__(self, parent, controller, initial_sort_col="name", initial_sort_dir="asc"):
        super().__init__(parent)
        self.controller = controller
        
        # Sorting state
        self._sort_column = initial_sort_col
        self._sort_direction = initial_sort_dir # "asc" or "desc"
        
        # Header (gebruik een "card" frame voor moderne look)
        header_frame = ttk.Frame(self, style="Card.TFrame")
        header_frame.pack(fill="x", pady=10, padx=10)
        
        lbl = ttk.Label(header_frame, text="Mod Manager Dashboard", style="Header.TLabel")
        lbl.pack(side="left")

        # Play button in the header (top right)
        ttk.Button(header_frame, text="▶ PLAY", style="Play.TButton", 
                   command=self.controller.start_game_logic).pack(side="right", padx=(5, 10))

        # Mod List (Treeview) - Changed selectmode to 'extended' for multiple selections
        columns = ("name", "status")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', selectmode="extended")
        
        # Bind headings for sorting
        self.tree.heading("name", text="Mod Name", command=lambda: self.sort_column("name"))
        self.tree.heading("status", text="Status", command=lambda: self.sort_column("status"))
        
        self.tree.column("name", width=350)
        self.tree.column("status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="top", fill="both", expand=True, padx=10)
        scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

        # Buttons frame (bottom)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=15, padx=10)

        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))
        
        # Scrollbar in Slime Rancher stijl
        style.configure(
            "Vertical.TScrollbar",
            background="#ff7ec6",
            troughcolor="#ffe4f2",
            bordercolor="#ff7ec6",
            arrowcolor="#ffffff"
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", "#7fe0ff")]
        )
        
        # Ensure the scrollbar is on top
        scrollbar.lift()

        ttk.Button(btn_frame, text="Install New Mod (.dll)", style="Action.TButton", 
                   command=self.controller.open_add_mod_window).pack(side="left", padx=5)
        
        # Changed button text and logic to reflect mass action
        ttk.Button(btn_frame, text="Toggle Selected Status", 
                   command=self.on_toggle).pack(side="left", padx=5)
        
        # Added padx to give space from the right border
        ttk.Button(btn_frame, text="Delete Selected", 
                   command=self.on_delete).pack(side="right", padx=(5, 10))


    def sort_column(self, col_id):
        # Determine new direction
        if self._sort_column == col_id:
            # Toggle direction if the same column is clicked
            new_direction = "desc" if self._sort_direction == "asc" else "asc"
        else:
            # New column clicked, reset to default direction ("asc")
            new_direction = "asc"
            
        self._sort_column = col_id
        self._sort_direction = new_direction
        
        # Save state and refresh list
        self.controller.save_sort_settings(self._sort_column, self._sort_direction)
        self.controller.refresh_mod_list()


    def update_list(self, mods):
        
        # 1. Apply sorting to the mod data list
        reverse_sort = self._sort_direction == "desc"
        
        if self._sort_column == "name":
            # Sort by clean name (case-insensitive alphabetical)
            # Default 'asc' means A-Z. Reverse=False for 'asc'
            mods.sort(key=lambda m: m["name"].lower().replace(".dll", "").replace(".disabled", ""), 
                      reverse=reverse_sort)
            
        elif self._sort_column == "status":
            # Sort by status. True ('ACTIVE') is 1, False ('DISABLED') is 0.
            # Default 'asc' requested is ACTIVE (1) on top. Reverse=True makes 1 go top.
            # We use m["enabled"] == "True" as the key (1 for ACTIVE, 0 for DISABLED).
            # If direction is 'asc', we want reverse=True (1 on top).
            # If direction is 'desc', we want reverse=False (0 on top).
            
            # The Treeview's display is always in the order the items are inserted.
            # We want:
            # - 'asc' direction: ACTIVE (1) top, DISABLED (0) bottom. Set reverse=True on the key.
            # - 'desc' direction: DISABLED (0) top, ACTIVE (1) bottom. Set reverse=False on the key.
            
            # The expression `self._sort_direction == "asc"` correctly evaluates to True/False for the 'reverse' parameter.
            mods.sort(key=lambda m: m["enabled"] == "True", 
                      reverse=self._sort_direction == "asc") 
        
        # 2. Clear treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # 3. Refill treeview
        for mod in mods:
            display_status = "ACTIVE" if mod["enabled"] == "True" else "DISABLED"
            
            # Add to treeview (index 2 is the hidden filename)
            self.tree.insert("", "end", values=(
                mod["name"].replace(".dll", "").replace(".disabled", ""), # Clean name (Index 0)
                display_status, # (Index 1)
                mod["name"] # Actual filename (Index 2 - used for logic)
            ))

    def on_toggle(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Required", "Please select one or more mods to toggle.")
            return

        for item in selected_items:
            # Note: values[2] still holds the actual filename even though it's not displayed
            values = self.tree.item(item)['values']
            filename = values[2]
            status_text = values[1]
            
            # Determine the current status
            current_bool_status = "True" if status_text == "ACTIVE" else "False"
            
            # Toggle the status for each selected file
            self.controller.toggle_mod_status(filename, current_bool_status)
        
        # Refresh the entire list after all toggles are done
        self.controller.refresh_mod_list()

    def on_delete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Selection Required", "Please select one or more mods to delete.")
            return

        filenames_to_delete = []
        for item in selected_items:
            values = self.tree.item(item)['values']
            filenames_to_delete.append(values[2]) # Get the actual filename

        # Pass the list of filenames to the controller for confirmation
        self.controller.confirm_delete(filenames_to_delete)