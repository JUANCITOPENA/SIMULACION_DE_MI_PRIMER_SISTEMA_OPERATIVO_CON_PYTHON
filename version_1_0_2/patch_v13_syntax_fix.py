import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix syntax errors in main.py
code = code.replace(
    'fg_color="transparent", text_color="white",',
    'fg_color="transparent",'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Syntax fix aplicado correctamente")
