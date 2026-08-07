import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90,',
    'btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'btn = ctk.CTkButton(self.desktop, text=item[:10], image=img, compound="top", width=100, height=90,',
    'btn = ctk.CTkButton(self.desktop, text=item[:10], image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent",',
    'ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'ctk.CTkButton(scroll, text=f"{\'📁\' if is_d else \'📄\'} {item}", anchor="w", fg_color="transparent", command=',
    'ctk.CTkButton(scroll, text=f"{\'📁\' if is_d else \'📄\'} {item}", anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"), command='
)
code = code.replace(
    'btn = ctk.CTkButton(folders_f, text=f"📁 {f_name}", width=120, height=40, fg_color=("#dfe6e9", "#2d3436"), hover_color="#555555",',
    'btn = ctk.CTkButton(folders_f, text=f"📁 {f_name}", width=120, height=40, fg_color=("#dfe6e9", "#2d3436"), hover_color="#555555", text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'ctk.CTkButton(scroll, text=f"🖼️ {w}", anchor="w", fg_color="transparent",',
    'ctk.CTkButton(scroll, text=f"🖼️ {w}", anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'btn = ctk.CTkButton(f, text="Instalado" if appid in getattr(self, \'installed_apps\', []) else "Descargar",',
    'btn = ctk.CTkButton(f, text="Instalado" if appid in getattr(self, \'installed_apps\', []) else "Descargar", text_color=("#000000", "#FFFFFF"),'
)
code = code.replace(
    'ctk.CTkButton(grid, text=b, width=65, height=65, command=',
    'ctk.CTkButton(grid, text=b, width=65, height=65, text_color=("#000000", "#FFFFFF"), command='
)
code = code.replace(
    'ctk.CTkLabel(info, text=f"{u.free//2**30} GB disponibles de {u.total//2**30} GB", font=("Segoe UI", 11), text_color="gray", anchor="w")',
    'ctk.CTkLabel(info, text=f"{u.free//2**30} GB disponibles de {u.total//2**30} GB", font=("Segoe UI", 11), text_color=("#444444", "#AAAAAA"), anchor="w")'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 12 aplicado correctamente")
