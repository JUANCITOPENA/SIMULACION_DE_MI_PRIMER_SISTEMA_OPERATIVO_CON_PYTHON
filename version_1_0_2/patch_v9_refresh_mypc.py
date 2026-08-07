import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix Context Menu Refresh
old_refresh = '("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.load_wallpaper()])'
new_refresh = '("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.refresh_desktop()])'
code = code.replace(old_refresh, new_refresh)

# Add refresh_desktop method
refresh_method = """    def refresh_desktop(self):
        # Oculta temporalmente los iconos para simular el parpadeo del refresco de Windows real
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget != self.bg_label:
                widget.place_forget()
        self.update()
        self.after(250, lambda: [self.load_wallpaper(), self.setup_desktop_icons()])

    def create_new_folder(self):"""
code = code.replace("    def create_new_folder(self):", refresh_method)

# Fix open_my_pc
old_mypc = """    def open_my_pc(self):
        win = self.request_app("mypc", "Mi PC - Estado", "600x450")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True)
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10); f.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(f, text=f"Unidad {p.device}\\n{u.free//2**30}GB Libres", justify="left").pack(side="left", padx=15, pady=10)
                pg = ctk.CTkProgressBar(f, width=180); pg.pack(side="right", padx=15); pg.set(u.percent/100)
            except: continue"""

new_mypc = """    def open_my_pc(self):
        win = self.request_app("mypc", "Mi PC", "650x550")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Seccion 1: Carpetas Frecuentes
        ctk.CTkLabel(scroll, text="Carpetas Principales", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(0, 10))
        folders_f = ctk.CTkFrame(scroll, fg_color="transparent")
        folders_f.pack(fill="x")
        
        folders = [("Desktop", "Escritorio"), ("Downloads", "Descargas"), ("Documents", "Documentos"), ("Pictures", "Imágenes")]
        for i, (f_icon, f_name) in enumerate(folders):
            btn = ctk.CTkButton(folders_f, text=f"📁 {f_name}", width=120, height=40, fg_color=("#dfe6e9", "#2d3436"), hover_color="#555555",
                                command=lambda n=f_name: messagebox.showinfo("Mi PC", f"Abriendo {n}..."))
            btn.grid(row=0, column=i, padx=10, pady=5)
            
        # Seccion 2: Discos Duros
        ctk.CTkLabel(scroll, text="Dispositivos y unidades", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(20, 10))
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
                f.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(f, text="💾", font=("Segoe UI", 28)).pack(side="left", padx=20, pady=10)
                
                info = ctk.CTkFrame(f, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, pady=10)
                
                ctk.CTkLabel(info, text=f"Disco Local ({p.device[:2]})", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
                pg = ctk.CTkProgressBar(info, height=12, progress_color="#0984e3")
                pg.pack(fill="x", pady=5, padx=5)
                pg.set(u.percent/100)
                ctk.CTkLabel(info, text=f"{u.free//2**30} GB disponibles de {u.total//2**30} GB", font=("Segoe UI", 11), text_color="gray", anchor="w").pack(fill="x")
            except: continue"""
code = code.replace(old_mypc, new_mypc)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 9 aplicado correctamente")
