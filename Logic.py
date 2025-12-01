import xml.etree.ElementTree as ET
import os
import shutil
import subprocess  # Needed to start external programs
from pathlib import Path

class ModManagerLogic:
    def __init__(self):
        # Define paths
        self.xml_file = os.path.join("data", "modlist.xml")
        self.ensure_file_exists()
        self.game_path = self.load_game_path()
        self.mods_folder = None
        
        if self.game_path:
            self.set_mods_folder_from_game_path(self.game_path)
            
        # Initialize sort settings state (will be loaded/saved in XML)
        self.sort_column = "name"
        self.sort_direction = "asc"
        self.load_sort_settings() # Load saved settings on init

    def ensure_file_exists(self):
        # Create base XML if it doesn't exist
        if not os.path.exists(self.xml_file):
            root = ET.Element("manager")
            settings = ET.SubElement(root, "settings")
            # Default sort settings
            ET.SubElement(settings, "sort_column").text = "name"
            ET.SubElement(settings, "sort_direction").text = "asc"
            mods = ET.SubElement(root, "mods")
            tree = ET.ElementTree(root)
            os.makedirs("data", exist_ok=True)
            tree.write(self.xml_file)

    def load_game_path(self):
        # Read the path to SlimeRancher.exe from the XML
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        settings = root.find("settings")
        path_elem = settings.find("game_path")
        if path_elem is not None:
            return path_elem.text
        return None

    def save_game_path(self, path):
        # Save the path to the XML
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        settings = root.find("settings")
        if settings is None:
            settings = ET.SubElement(root, "settings")
        
        path_elem = settings.find("game_path")
        if path_elem is None:
            path_elem = ET.SubElement(settings, "game_path")
        
        path_elem.text = path
        tree.write(self.xml_file)
        
        self.game_path = path
        self.set_mods_folder_from_game_path(path)

    def set_mods_folder_from_game_path(self, game_exe_path):
        """
        Determine the SRML mods folder relative to the selected SlimeRancher.exe.
        
        Expected structure:
            <GameFolder>/
                SlimeRancher.exe
                SRML/
                    mods/
                        *.dll / *.disabled
        """
        game_dir = os.path.dirname(game_exe_path)

        # SRML base folder lives next to the game executable
        srml_folder = os.path.join(game_dir, "SRML")
        mods_folder = os.path.join(srml_folder, "mods")

        # Ensure the directory exists (create if needed)
        try:
            os.makedirs(mods_folder, exist_ok=True)
        except OSError:
            # Can happen if permissions are missing; fall back to None
            mods_folder = None

        self.mods_folder = mods_folder

    def load_sort_settings(self):
        # Load saved sorting column and direction from XML
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            settings = root.find("settings")
            
            col_elem = settings.find("sort_column")
            dir_elem = settings.find("sort_direction")
            
            if col_elem is not None:
                self.sort_column = col_elem.text
            if dir_elem is not None:
                self.sort_direction = dir_elem.text
        except ET.ParseError:
            print("Error parsing modlist.xml for sort settings. Using defaults.")
        except Exception as e:
            print(f"An unexpected error occurred loading sort settings: {e}. Using defaults.")

    def save_sort_settings(self, column, direction):
        # Save current sorting column and direction to XML
        self.sort_column = column
        self.sort_direction = direction
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            settings = root.find("settings")
            
            col_elem = settings.find("sort_column")
            if col_elem is None:
                col_elem = ET.SubElement(settings, "sort_column")
            col_elem.text = column

            dir_elem = settings.find("sort_direction")
            if dir_elem is None:
                dir_elem = ET.SubElement(settings, "sort_direction")
            dir_elem.text = direction
            
            tree.write(self.xml_file)
        except Exception as e:
            print(f"Error saving sort settings: {e}")

    def start_game(self):
        # Start SlimeRancher.exe
        if self.game_path and os.path.exists(self.game_path):
            try:
                # Popen starts the process independently of this tool
                # cwd ensures the working directory is correct (important for mods)
                subprocess.Popen(self.game_path, cwd=os.path.dirname(self.game_path))
                return True, "Game started successfully!"
            except Exception as e:
                return False, f"Error starting game: {e}"
        else:
            return False, "Slime Rancher 2 path not found."

    def sync_mods(self):
        # Synchronize physical files with the XML list
        if not self.mods_folder or not os.path.exists(self.mods_folder):
            return []

        # 1. Read physical files
        found_files = []
        for f in os.listdir(self.mods_folder):
            full_path = os.path.join(self.mods_folder, f)
            if os.path.isfile(full_path):
                if f.endswith(".dll"):
                    found_files.append({"name": f, "enabled": "True"})
                elif f.endswith(".disabled"):
                    found_files.append({"name": f, "enabled": "False"})

        # 2. Update XML
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        mods_elem = root.find("mods")
        if mods_elem is None:
            mods_elem = ET.SubElement(root, "mods")
        
        # Clear old list
        for child in list(mods_elem):
            mods_elem.remove(child)

        # Fill with new scan
        output_list = []
        for mod_data in found_files:
            new_mod = ET.SubElement(mods_elem, "mod")
            new_mod.set("filename", mod_data["name"])
            display_name = mod_data["name"].replace(".dll", "").replace(".disabled", "")
            new_mod.set("name", display_name)
            new_mod.set("enabled", mod_data["enabled"])
            output_list.append(mod_data)

        tree.write(self.xml_file)
        return output_list

    def toggle_mod(self, filename, current_enabled):
        # Rename file from .dll to .disabled or vice versa
        if not self.mods_folder:
            return

        old_path = os.path.join(self.mods_folder, filename)
        
        if current_enabled == "True":
            new_name = filename.replace(".dll", ".disabled")
        else:
            new_name = filename.replace(".disabled", ".dll")
            
        new_path = os.path.join(self.mods_folder, new_name)
        
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            print(f"Error renaming file '{filename}': {e}")


    def add_mod_file(self, source_path):
        if not self.mods_folder or not source_path:
            return
            
        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.mods_folder, filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            self.sync_mods()
        except Exception as e:
            print(f"Could not copy mod: {e}")

    def remove_mod_file(self, filenames):
        if not self.mods_folder:
            return

        # Ensure we are iterating over a list, even if only one file is passed
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            full_path = os.path.join(self.mods_folder, filename)
            try:
                if os.path.exists(full_path):
                    # NOTE: Using os.remove for permanent deletion.
                    os.remove(full_path) 
                    print(f"File deleted: {filename}")
            except OSError as e:
                print(f"Could not delete file '{filename}': {e}")
                
        # Only sync once after all files have been processed
        self.sync_mods()

    def get_mods(self):
        mods_data = self.sync_mods()
        return mods_data