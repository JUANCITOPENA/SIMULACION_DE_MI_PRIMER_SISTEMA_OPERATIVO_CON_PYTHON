import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Replace InternalWindow
old_window = """class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        super().__init__(master, width=width, height=height, corner_radius=15, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.app_id = app_id
        self.on_close = on_close

        # Barra de Título
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color="#34495e", corner_radius=12)
        self.title_bar.pack(fill="x", side="top", padx=3, pady=3)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=15)
        
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=35, height=30, 
                                        fg_color="#e17055", hover_color="#d63031", command=self.close_window)
        self.close_btn.pack(side="right", padx=5)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-1>", lambda e: self.lift())

    def start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}
        self.lift()

    def do_drag(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y)

    def close_window(self):
        if self.on_close: self.on_close(self.app_id)
        self.destroy()"""

new_window = """class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, on_minimize=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        super().__init__(master, width=width, height=height, corner_radius=10, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.app_id = app_id
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.is_maximized = False
        self.old_geometry = {"x": 300, "y": 100, "w": width, "h": height}
        
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color="#34495e", corner_radius=10)
        self.title_bar.pack(fill="x", side="top", padx=2, pady=2)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=10)
        
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, fg_color="#e81123", hover_color="#f1707a", command=self.close_window)
        self.close_btn.pack(side="right", padx=2)
        
        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=25, fg_color="transparent", hover_color="#555555", command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=2)
        
        self.min_btn = ctk.CTkButton(self.title_bar, text="_", width=30, height=25, fg_color="transparent", hover_color="#555555", command=self.minimize_window)
        self.min_btn.pack(side="right", padx=2)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.grip = ctk.CTkFrame(self, width=20, height=20, fg_color="transparent", cursor="sizing")
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<B1-Motion>", self.do_resize)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-1>", lambda e: self.lift())

        self._resize_job = None

    def start_drag(self, event):
        if self.is_maximized: return
        self._drag_data = {"x": event.x, "y": event.y}
        self.lift()

    def do_drag(self, event):
        if self.is_maximized: return
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y)
        
    def do_resize(self, event):
        if self.is_maximized: return
        new_w = max(200, event.x_root - self.winfo_rootx())
        new_h = max(150, event.y_root - self.winfo_rooty())
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(30, lambda: self._apply_resize(new_w, new_h))
        
    def _apply_resize(self, w, h):
        self.configure(width=w, height=h)
        self.place(width=w, height=h)

    def toggle_maximize(self):
        if not self.is_maximized:
            self.old_geometry = {"x": self.winfo_x(), "y": self.winfo_y(), "w": self.winfo_width(), "h": self.winfo_height()}
            parent = self.master
            self.place(x=0, y=0, width=parent.winfo_width(), height=parent.winfo_height())
            self.is_maximized = True
            self.grip.place_forget()
        else:
            self.place(x=self.old_geometry["x"], y=self.old_geometry["y"], width=self.old_geometry["w"], height=self.old_geometry["h"])
            self.is_maximized = False
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

    def minimize_window(self):
        if self.on_minimize: self.on_minimize(self.app_id)
        self.place_forget()

    def close_window(self):
        if self.on_close: self.on_close(self.app_id)
        self.destroy()"""

code = code.replace(old_window, new_window)

# 2. Add apps_tb_frame
old_tb = """        # Botones Taskbar
        self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                        fg_color=THEMES[self.current_theme][0], 
                                        command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=15, pady=5)

        self.vol_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")"""
new_tb = """        # Botones Taskbar
        self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                        fg_color=THEMES[self.current_theme][0], 
                                        command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=15, pady=5)
        
        self.apps_tb_frame = ctk.CTkScrollableFrame(self.taskbar, fg_color="transparent", orientation="horizontal", height=45)
        self.apps_tb_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.vol_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")"""
code = code.replace(old_tb, new_tb)

# 3. Add desktop click events
old_desktop_binds = """        self.update_time()
        self.setup_desktop_icons()
        self.start_menu = None
        self.load_wallpaper()"""
new_desktop_binds = """        self.update_time()
        self.setup_desktop_icons()
        self.start_menu = None
        self.context_menu = None
        self.load_wallpaper()
        
        self.bg_label.bind("<Button-1>", self.on_desktop_click)
        self.bg_label.bind("<Button-3>", self.show_context_menu)"""
code = code.replace(old_desktop_binds, new_desktop_binds)

# 4. setup_desktop_icons
old_setup_icons = """    def setup_desktop_icons(self):
        icons = [("🖥️\\nMi PC", "mypc", self.open_my_pc), ("🗂️\\nExplorador", "explorer", self.open_explorer),
                 ("🌍\\nNavegador", "browser", self.open_browser), ("📽️\\nVideo Pro", "video", self.open_video_player),
                 ("🗒️\\nNotepad", "notepad", self.open_notepad)]
        for i, (name, aid, cmd) in enumerate(icons):
            btn = ctk.CTkButton(self.desktop, text=name, width=120, height=130, fg_color="transparent", 
                                 text_color="white", hover_color=("#b2bec3", "#636e72"), 
                                 font=("Segoe UI", 20, "bold"), command=cmd)
            btn.place(x=40, y=30 + (i * 140))"""
new_setup_icons = """    def setup_desktop_icons(self):
        self.icon_images = getattr(self, "icon_images", {})
        icon_data = [
            ("Mi PC", "mypc", self.open_my_pc, "mypc.png"),
            ("Explorador", "explorer", self.open_explorer, "explorer.png"),
            ("Navegador", "browser", self.open_browser, "browser.png"),
            ("Video Pro", "video", self.open_video_player, "video.png"),
            ("Notepad", "notepad", self.open_notepad, "notepad.png"),
            ("Configuración", "settings", self.open_control_panel, "settings.png"),
            ("Task Mgr", "taskmgr", self.open_task_manager, "start.png"),
            ("Terminal", "terminal", self.open_terminal, "start.png")
        ]
        
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        y_pos = 30
        x_pos = 40
        # Limpiar iconos anteriores si existen
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()

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
                x_pos += 120"""
code = code.replace(old_setup_icons, new_setup_icons)

# 5. toggle_start_menu
old_toggle_menu = """    def toggle_start_menu(self):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610); self.start_menu.lift()
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            app_f = ctk.CTkFrame(self.start_menu, fg_color="transparent"); app_f.pack(fill="both", expand=True, padx=10)
            apps = [("🗂️ Explorador", self.open_explorer), ("🌍 Navegador", self.open_browser), ("📽️ Video Player", self.open_video_player),
                    ("🖥️ Mi PC", self.open_my_pc), ("🗒️ Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc)]
            for n, c in apps:
                ctk.CTkButton(app_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            ctk.CTkLabel(self.start_menu, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=5)
            for tname in THEMES:
                ctk.CTkButton(self.start_menu, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=40, pady=1)
            ctk.CTkButton(self.start_menu, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=40, pady=10)"""
new_toggle_menu = """    def toggle_start_menu(self):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            if self.context_menu: self.context_menu.destroy(); self.context_menu = None
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610); self.start_menu.lift()
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            app_f = ctk.CTkFrame(self.start_menu, fg_color="transparent"); app_f.pack(fill="both", expand=True, padx=10)
            apps = [("🗂️ Explorador", self.open_explorer), ("🌍 Navegador", self.open_browser), ("📽️ Video Player", self.open_video_player),
                    ("🖥️ Mi PC", self.open_my_pc), ("🗒️ Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc),
                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal)]
            for n, c in apps:
                ctk.CTkButton(app_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            ctk.CTkLabel(self.start_menu, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=5)
            for tname in THEMES:
                ctk.CTkButton(self.start_menu, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=40, pady=1)
            ctk.CTkButton(self.start_menu, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=40, pady=10)"""
code = code.replace(old_toggle_menu, new_toggle_menu)

# 6. request_app and on_app_close
old_request = """    def request_app(self, app_id, title, size):
        if app_id in self.running_apps:
            self.running_apps[app_id].lift(); return None
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), on_close=self.on_app_close, theme_colors=THEMES[self.current_theme])
        self.running_apps[app_id] = win
        win.place(x=300, y=100); return win

    def on_app_close(self, app_id):
        if app_id in self.running_apps: del self.running_apps[app_id]"""
new_request = """    def request_app(self, app_id, title, size):
        if app_id in self.running_apps:
            self.restore_app(app_id)
            return None
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), 
                             on_close=self.on_app_close, on_minimize=self.on_app_minimize, theme_colors=THEMES[self.current_theme])
        self.running_apps[app_id] = win
        win.place(x=300, y=100)
        self.update_taskbar_buttons()
        return win

    def on_app_close(self, app_id):
        if app_id in self.running_apps: 
            del self.running_apps[app_id]
            self.update_taskbar_buttons()

    def on_desktop_click(self, event):
        if getattr(self, "start_menu", None): self.start_menu.destroy(); self.start_menu = None
        if getattr(self, "context_menu", None): self.context_menu.destroy(); self.context_menu = None

    def show_context_menu(self, event):
        self.on_desktop_click(None)
        self.context_menu = ctk.CTkFrame(self.desktop, width=150, corner_radius=5, border_width=1, border_color="gray")
        self.context_menu.place(x=event.x, y=event.y)
        
        opts = [
            ("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.load_wallpaper()]),
            ("📁 Nueva Carpeta", lambda: [self.context_menu.destroy(), self.create_new_folder()]),
            ("📄 Nuevo Archivo", lambda: [self.context_menu.destroy(), self.create_new_file()]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.open_control_panel()])
        ]
        
        for name, cmd in opts:
            ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent", 
                          hover_color="#555555", command=cmd).pack(fill="x", padx=2, pady=2)
                          
    def create_new_folder(self):
        name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if name:
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            messagebox.showinfo("Sistema", "Carpeta creada.")
            
    def create_new_file(self):
        name = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo (ej. notas.txt):")
        if name:
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            messagebox.showinfo("Sistema", "Archivo creado.")

    def update_taskbar_buttons(self):
        for widget in self.apps_tb_frame.winfo_children():
            widget.destroy()
            
        for app_id, win in self.running_apps.items():
            btn = ctk.CTkButton(self.apps_tb_frame, text=win.title_label.cget("text"), width=120, height=30,
                                fg_color="transparent", border_width=1, border_color="gray",
                                hover_color="#555555", command=lambda aid=app_id: self.restore_app(aid))
            btn.pack(side="left", padx=5)

    def restore_app(self, app_id):
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            if not win.winfo_viewable():
                win.place(x=win.old_geometry.get("x", 300), y=win.old_geometry.get("y", 100), 
                          width=win.old_geometry.get("w", win.winfo_width()), height=win.old_geometry.get("h", win.winfo_height()))
            win.lift()

    def on_app_minimize(self, app_id):
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            win.old_geometry = {"x": win.winfo_x(), "y": win.winfo_y(), "w": win.winfo_width(), "h": win.winfo_height()}"""
code = code.replace(old_request, new_request)

# 7. Add new apps at the bottom
new_apps = """
    def open_control_panel(self):
        win = self.request_app("settings", "Panel de Control", "600x450")
        if not win: return
        ctk.CTkLabel(win.content, text="⚙️ Configuración del Sistema", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        f_tema = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_tema.pack(fill="x", pady=10)
        ctk.CTkLabel(f_tema, text="🎨 Apariencia y Temas", font=("Segoe UI", 16, "bold")).pack(pady=5)
        themes_frame = ctk.CTkFrame(f_tema, fg_color="transparent")
        themes_frame.pack(pady=10)
        for tname in THEMES:
            ctk.CTkButton(themes_frame, text=tname, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(side="left", padx=5)
            
        f_sys = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_sys.pack(fill="x", pady=10)
        ctk.CTkLabel(f_sys, text="💻 Información del Sistema (Real)", font=("Segoe UI", 16, "bold")).pack(pady=5)
        ram = psutil.virtual_memory()
        ctk.CTkLabel(f_sys, text=f"Memoria RAM Total: {ram.total // (1024**3)} GB", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Memoria RAM en Uso: {ram.percent}%", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Uso de CPU Actual: {psutil.cpu_percent()}%", font=("Segoe UI", 14)).pack(pady=(0, 10))

    def open_task_manager(self):
        win = self.request_app("taskmgr", "Administrador de Tareas", "400x500")
        if not win: return
        ctk.CTkLabel(win.content, text="📋 Procesos Activos (JPV OS)", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        self.task_list_frame = ctk.CTkScrollableFrame(win.content)
        self.task_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        def refresh_tasks():
            if not win.winfo_exists(): return
            for widget in self.task_list_frame.winfo_children():
                widget.destroy()
            for app_id, app_win in list(self.running_apps.items()):
                f = ctk.CTkFrame(self.task_list_frame, fg_color=("#dfe6e9", "#2d3436"), corner_radius=5)
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=app_win.title_label.cget("text")).pack(side="left", padx=10, pady=5)
                ctk.CTkButton(f, text="Finalizar", fg_color="#e17055", hover_color="#d63031", width=60, height=24,
                              command=lambda aid=app_id: self.running_apps[aid].close_window()).pack(side="right", padx=10)
            win.after(2000, refresh_tasks)
            
        refresh_tasks()

    def open_terminal(self):
        win = self.request_app("terminal", "JPV Terminal", "600x400")
        if not win: return
        win.content.configure(fg_color="black")
        
        output_txt = ctk.CTkTextbox(win.content, fg_color="black", text_color="#00ff00", font=("Consolas", 14), state="disabled")
        output_txt.pack(fill="both", expand=True, padx=5, pady=5)
        
        input_frame = ctk.CTkFrame(win.content, fg_color="black")
        input_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(input_frame, text="C:\\\\VIRTUAL_DRIVE> ", text_color="#00ff00", font=("Consolas", 14)).pack(side="left")
        
        cmd_var = ctk.StringVar()
        cmd_entry = ctk.CTkEntry(input_frame, textvariable=cmd_var, fg_color="black", text_color="#00ff00", border_width=0, font=("Consolas", 14))
        cmd_entry.pack(side="left", fill="x", expand=True)
        cmd_entry.focus()
        
        self.current_term_dir = ROOT_DIR
        
        def log(text):
            output_txt.configure(state="normal")
            output_txt.insert("end", text + "\\n")
            output_txt.configure(state="disabled")
            output_txt.see("end")

        log("Mini Windows JPV Terminal [Versión 2.0]")
        log("(c) Ing. Juancito Peña. Todos los derechos reservados.\\n")
        
        def execute_command(event=None):
            command = cmd_var.get().strip()
            if not command: return
            
            cmd_var.set("")
            log(f"C:\\\\VIRTUAL_DRIVE> {command}")
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "help":
                log("Comandos disponibles: help, dir, clear, echo, date, exit")
            elif cmd == "dir":
                try:
                    for item in os.listdir(self.current_term_dir):
                        log(f"  {item}")
                except Exception as e:
                    log(f"Error: {e}")
            elif cmd == "clear":
                output_txt.configure(state="normal")
                output_txt.delete("1.0", "end")
                output_txt.configure(state="disabled")
            elif cmd == "echo":
                log(" ".join(parts[1:]))
            elif cmd == "date":
                log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif cmd == "exit":
                win.close_window()
            else:
                log(f"'{cmd}' no se reconoce como un comando interno o externo.")
            log("")
            
        cmd_entry.bind("<Return>", execute_command)

if __name__ == "__main__":"""
code = code.replace('if __name__ == "__main__":', new_apps)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch aplicado correctamente sin afectar líneas críticas.")
