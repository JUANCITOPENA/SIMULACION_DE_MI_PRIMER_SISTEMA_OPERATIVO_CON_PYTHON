import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_btn = """            for n, c in apps:
                ctk.CTkButton(scroll_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")"""

new_btn = """            for n, c in apps:
                ctk.CTkButton(scroll_f, text=n, fg_color="transparent", text_color=("#000000", "#FFFFFF"), anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")"""

if old_btn in code:
    code = code.replace(old_btn, new_btn)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patch 11 aplicado correctamente")
else:
    print("Error: No se encontró la creación de los botones del menú inicio.")
