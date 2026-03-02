from PIL import Image

# Open your high-res transparent PNG
img = Image.open("logo.png")

# Bake it into a true multi-resolution Windows ICO file
img.save("icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("High-res icon created successfully!")
