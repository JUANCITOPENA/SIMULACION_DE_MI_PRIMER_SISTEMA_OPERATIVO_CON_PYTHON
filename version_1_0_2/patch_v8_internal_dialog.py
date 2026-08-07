import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_create = """    def create_new_folder(self):
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

new_create = """    def show_internal_input_dialog(self, title, prompt, on_submit):
        # Cuadro de dialogo totalmente interno al sistema simulado
        dialog = ctk.CTkFrame(self.desktop, width=320, height=160, corner_radius=15, border_width=2, border_color="gray", fg_color=("#ecf0f1", "#2c3e50"))
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)
        dialog.lift()

        ctk.CTkLabel(dialog, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(dialog, text=prompt, font=("Segoe UI", 12)).pack()
        
        entry = ctk.CTkEntry(dialog, width=260)
        entry.pack(pady=10)
        entry.focus_set()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        def submit(event=None):
            val = entry.get()
            dialog.destroy()
            if val: on_submit(val)
                
        def cancel():
            dialog.destroy()
            
        ctk.CTkButton(btn_frame, text="Aceptar", width=100, command=submit).pack(side="left", padx=25)
        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="#e81123", hover_color="#f1707a", command=cancel).pack(side="right", padx=25)
        
        entry.bind("<Return>", submit)

    def create_new_folder(self):
        def on_submit(name):
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Nueva Carpeta", "Nombre de la carpeta:", on_submit)
            
    def create_new_file(self):
        def on_submit(name):
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Nuevo Archivo", "Nombre del archivo (ej. notas.txt):", on_submit)"""

if old_create in code:
    code = code.replace(old_create, new_create)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patch 8 aplicado correctamente")
else:
    print("Error: No se encontró el bloque a reemplazar")
