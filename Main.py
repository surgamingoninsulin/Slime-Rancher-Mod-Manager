'''
Author: SuGOI
Description: A Mod Manager for the first game "Slime Rancher" not mistaken for "Slime Rancher 2"!
Version: 1.0.0 
Lisence: GNU GENERAL PUBLIC LICENSE
'''
import Logic
import Gui
import ctypes
import platform

# Main entry point of the application
if __name__ == "__main__":
    # Ensure High DPI support on Windows for sharp, modern look
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    # Initialize the logic (Model)
    logic_instance = Logic.ModManagerLogic()
    
    # Initialize the GUI (View/Controller) and pass logic
    app = Gui.ModManagerGui(logic_instance)
    
    # Start the application
    app.start()