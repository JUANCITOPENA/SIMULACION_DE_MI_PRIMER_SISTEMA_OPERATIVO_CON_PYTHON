import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

def create_icon(filename, color, text, shape="rect"):
    size = (128, 128)
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    if shape == "rect":
        draw.rounded_rectangle([10, 10, 118, 118], radius=25, fill=color)
    else:
        draw.ellipse([10, 10, 118, 118], fill=color)
        
    try:
        font = ImageFont.truetype("arialbd.ttf", 60)
    except:
        font = ImageFont.load_default()
        
    # Centering text manually
    draw.text((35, 30), text, fill="white", font=font)
    img.save(os.path.join(ASSETS_DIR, filename))

# Generando Iconos
create_icon("mypc.png", "#3498db", "PC", "rect")
create_icon("explorer.png", "#f1c40f", "EX", "rect")
create_icon("browser.png", "#e74c3c", "WEB", "circle")
create_icon("video.png", "#9b59b6", "VID", "rect")
create_icon("notepad.png", "#2ecc71", "TXT", "rect")
create_icon("settings.png", "#7f8c8d", "SET", "circle")
create_icon("start.png", "#0078D4", "WIN", "circle")

print("Iconos generados con éxito.")
