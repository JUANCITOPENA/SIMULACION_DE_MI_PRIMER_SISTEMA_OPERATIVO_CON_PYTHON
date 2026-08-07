import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix literal string issue
code = code.replace(r'btn.grid(row=0, column=i, padx=10, pady=5)\n        self.setup_desktop_icons()', 
                    'btn.grid(row=0, column=i, padx=10, pady=5)\n        self.setup_desktop_icons()')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Syntax fix aplicado correctamente 2")
