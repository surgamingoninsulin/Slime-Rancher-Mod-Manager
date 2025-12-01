import os
from urllib.request import urlretrieve
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from data.guis import MainWindow, AddModsWindow, ConfirmWindow

class ModManagerGui:
    def __init__(self, logic):
        self.logic = logic
        self.root = tk.Tk()
        self.root.title("Slime Rancher Mod Manager")
        self.root.geometry("700x500")
        # Pas het venstericoon aan als het beschikbaar is
        icon_path = os.path.join("data", "pink.ico")
        icon_url = "https://raw.githubusercontent.com/surgamingoninsulin/GlobalImages/refs/heads/main/images/pink.ico"
        if not os.path.exists(icon_path):
            try:
                os.makedirs(os.path.dirname(icon_path), exist_ok=True)
                urlretrieve(icon_url, icon_path)
            except Exception:
                pass
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
        
        # Laad initiële sorteerinstellingen vanuit logic
        self.sort_column = self.logic.sort_column
        self.sort_direction = self.logic.sort_direction
        
        # Maak venster niet-herschaalbaar
        self.root.resizable(False, False)
        
        # Stel Modern Thema in (Slime Rancher geïnspireerd)
        style = ttk.Style()
        style.theme_use('clam')
        
        # Slime Rancher kleurenschema (zacht, kleurrijk)
        card_color = "#ffcce6"        # Consistente roze toon voor dashboard/panels
        bg_color = card_color         # Maak het venster dezelfde kleur als de header achtergrond
        accent_color = "#ff7ec6"      # Slime roze
        accent_alt = "#7fe0ff"        # Slime blauw
        text_color = "#2c3e50"        # Donkere tekst voor leesbaarheid
        play_color = "#7fe37f"        # Groen voor Play-knop
        
        self.root.configure(bg=bg_color)
        
        # Basis widgets
        style.configure("TFrame", background=bg_color)
        style.configure("Card.TFrame", background=card_color, relief="flat")
        style.configure(
            "TLabel",
            background=bg_color,
            foreground=text_color,
            font=("Segoe UI", 10)
        )
        # Specifieke stijl voor de grote dashboard titel
        style.configure(
            "Header.TLabel",
            background=card_color,
            foreground="#000000",
            font=("Segoe UI", 18, "bold")
        )
        
        # Algemene knoppen
        style.configure(
            "TButton",
            background=accent_color,
            foreground="#000000",
            borderwidth=0,
            padding=6,
            focusthickness=3,
            focuscolor=accent_alt
        )
        style.map(
            "TButton",
            background=[("active", accent_alt)],
            relief=[("pressed", "sunken"), ("!pressed", "flat")]
        )
        
        # Play-knop
        style.configure(
            "Play.TButton",
            background=play_color,
            foreground="#000000",
            font=("Segoe UI", 11, "bold"),
            padding=(10, 6),
            borderwidth=0
        )
        style.map(
            "Play.TButton",
            background=[("active", "#5ecc68")]
        )

        # Treeview (mod lijst)
        dark_pink_text = "#c03969"
        style.configure(
            "Treeview",
            background=card_color,
            foreground=dark_pink_text,
            fieldbackground=card_color,
            rowheight=26,
            bordercolor=accent_color,
            relief="flat"
        )
        # Maak selectie/hover blauw i.p.v. grijs
        style.map(
            "Treeview",
            background=[("active", accent_alt), ("selected", accent_alt), ("focus", accent_alt)]
        )
        # Kopteksten: roze achtergrond met goed leesbare tekst
        style.configure(
            "Treeview.Heading",
            background=accent_color,   # roze i.p.v. blauw
            foreground="#000000",
            font=("Segoe UI", 10, "bold")
        )
        
        # Initialiseer hoofdvenster
        # Geef de initiële sorteerinstellingen door aan het hoofdvenster
        self.main_window = MainWindow.ModListFrame(self.root, self, self.sort_column, self.sort_direction)
        self.main_window.pack(fill="both", expand=True)

    def start(self):
        # Controleer of het spelpad bekend is bij het opstarten
        if not self.logic.game_path:
            self.ask_game_path()
        else:
            self.refresh_mod_list()
            
        self.root.mainloop()

    def ask_game_path(self):
        messagebox.showinfo("Setup", "Selecteer 'SlimeRancher.exe' om te beginnen.")
        file_path = filedialog.askopenfilename(
            title="Selecteer Slime Rancher Executable",
            filetypes=[("Executable", "*.exe")]
        )
        
        if file_path and file_path.endswith("SlimeRancher.exe"):
            self.logic.save_game_path(file_path)
            self.refresh_mod_list()
        else:
            messagebox.showerror("Fout", "Ongeldig bestand geselecteerd. De applicatie wordt nu gesloten.")
            self.root.destroy()

    def open_add_mod_window(self):
        AddModsWindow.AddModDialog(self.root, self)

    def confirm_delete(self, mod_filenames):
        # mod_filenames is nu een lijst
        ConfirmWindow.DeleteConfirmDialog(self.root, self, mod_filenames)

    # Deze methode wordt herhaaldelijk aangeroepen binnen een lus in MainWindow.on_toggle
    def toggle_mod_status(self, filename, current_status):
        self.logic.toggle_mod(filename, current_status)

    def add_mod_logic(self, file_path):
        self.logic.add_mod_file(file_path)
        self.refresh_mod_list()

    def delete_mod_logic(self, filenames):
        # filenames is nu een lijst
        self.logic.remove_mod_file(filenames)
        self.refresh_mod_list()
        
    def start_game_logic(self):
        # Roept de logica aan om het spel te starten
        success, msg = self.logic.start_game()
        if not success:
            messagebox.showerror("Fout", msg)

    # *** FIX: Deze methode was waarschijnlijk afwezig in uw lokale bestand. ***
    def save_sort_settings(self, column, direction):
        # Werk interne status bij en sla op in XML via logica
        self.sort_column = column
        self.sort_direction = direction
        self.logic.save_sort_settings(column, direction)
        
    def refresh_mod_list(self):
        mods = self.logic.get_mods()
        self.main_window.update_list(mods)