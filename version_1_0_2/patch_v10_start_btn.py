import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_btn = """        self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                        fg_color=THEMES[self.current_theme][0], 
                                        command=self.toggle_start_menu)"""

new_btn = """        start_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "start.png")
        if os.path.exists(start_icon_path):
            start_img = ctk.CTkImage(light_image=Image.open(start_icon_path), size=(25, 25))
            self.start_btn = ctk.CTkButton(self.taskbar, text="", image=start_img, width=60, height=45,
                                            fg_color=THEMES[self.current_theme][0], hover_color="#555555",
                                            command=self.toggle_start_menu)
        else:
            self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                            fg_color=THEMES[self.current_theme][0], 
                                            command=self.toggle_start_menu)"""

if old_btn in code:
    code = code.replace(old_btn, new_btn)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patch 10 aplicado correctamente")
else:
    print("No se encontró el bloque del botón de inicio")
