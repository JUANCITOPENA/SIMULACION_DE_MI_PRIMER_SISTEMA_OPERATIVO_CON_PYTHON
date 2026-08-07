import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_create = """    def create_new_folder(self):
        name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if name:
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            messagebox.showinfo("Sistema", "Carpeta creada.")
            
    def create_new_file(self):
        name = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo (ej. notas.txt):")
        if name:
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            messagebox.showinfo("Sistema", "Archivo creado.")"""

new_create = """    def create_new_folder(self):
        dialog = ctk.CTkInputDialog(text="Nombre de la carpeta:", title="Nueva Carpeta")
        name = dialog.get_input()
        if name:
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            self.setup_desktop_icons()
            
    def create_new_file(self):
        dialog = ctk.CTkInputDialog(text="Nombre del archivo (ej. notas.txt):", title="Nuevo Archivo")
        name = dialog.get_input()
        if name:
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            self.setup_desktop_icons()"""

code = code.replace(old_create, new_create)

old_setup = """        for i, (name, aid, cmd, icon_file) in enumerate(icon_data):
            img_path = os.path.join(assets_dir, icon_file)
            img = None
            if os.path.exists(img_path):
                img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                self.icon_images[aid] = img
            
            btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90, 
                                 fg_color="transparent", text_color="white", 
                                 hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 13, "bold"), command=cmd)
            btn.place(x=x_pos, y=y_pos)
            y_pos += 110
            if y_pos > 600:
                y_pos = 30
                x_pos += 120"""

new_setup = """        # Renderizar iconos fijos
        for i, (name, aid, cmd, icon_file) in enumerate(icon_data):
            img_path = os.path.join(assets_dir, icon_file)
            img = None
            if os.path.exists(img_path):
                img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                self.icon_images[aid] = img
            
            btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90, 
                                 fg_color="transparent", text_color="white", 
                                 hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 13, "bold"), command=cmd)
            btn.place(x=x_pos, y=y_pos)
            y_pos += 110
            if y_pos > 600:
                y_pos = 30
                x_pos += 120

        # Renderizar carpetas y archivos creados por el usuario en el escritorio
        if os.path.exists(ROOT_DIR):
            for item in os.listdir(ROOT_DIR):
                if item == "settings.json": continue
                item_path = os.path.join(ROOT_DIR, item)
                is_dir = os.path.isdir(item_path)
                
                # Reutilizamos los iconos existentes si podemos
                fallback_icon = "explorer.png" if is_dir else "notepad.png"
                img_path = os.path.join(assets_dir, fallback_icon)
                img = None
                if os.path.exists(img_path):
                    img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                    self.icon_images[item] = img
                    
                # Definimos una acción al hacer clic: Abrir el explorador o el bloc de notas
                if is_dir:
                    action = self.open_explorer
                else:
                    action = self.open_notepad
                    
                btn = ctk.CTkButton(self.desktop, text=item[:10], image=img, compound="top", width=100, height=90, 
                                     fg_color="transparent", text_color="white", 
                                     hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 12), command=action)
                btn.place(x=x_pos, y=y_pos)
                y_pos += 110
                if y_pos > 600:
                    y_pos = 30
                    x_pos += 120
"""

code = code.replace(old_setup, new_setup)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 6 aplicado correctamente")
