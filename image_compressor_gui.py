#!/usr/bin/env python3
import os
import shutil
from tkinter import filedialog, Tk, StringVar, IntVar, messagebox, Button, Label
from tkinter import ttk
from PIL import Image

# Extensions prises en charge
SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico', '.tga'
)

def compress_image(input_path, output_path, quality=80, scale_factor=1.0):
    try:
        img = Image.open(input_path)
        img_format = img.format.upper()

        if scale_factor < 1.0:
            width, height = img.size
            img = img.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)

        if img_format in ['JPEG', 'JPG']:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, format='JPEG', optimize=True, quality=quality, progressive=True, subsampling=2)

        elif img_format == 'PNG':
            img = img.convert('P', palette=Image.ADAPTIVE)
            img.save(output_path, format='PNG', optimize=True, compress_level=9)

        elif img_format == 'WEBP':
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGBA')
            img.save(output_path, format='WEBP', quality=quality, optimize=True, method=6)

        else:
            shutil.copy(input_path, output_path)

    except Exception as e:
        print(f"Erreur compression {input_path} : {e}")

def process_file(file_path, quality, scale):
    output_dir = os.path.join(os.path.dirname(file_path), "compressed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    compress_image(file_path, output_path, quality, scale)
    update_progress(100)

def process_folder(folder_path, quality, scale):
    image_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(os.path.join(root, file))

    total = len(image_files)
    if total == 0:
        messagebox.showinfo("Info", "Aucune image trouvée.")
        update_progress(0)
        return

    output_dir = os.path.join(folder_path, "compressed")
    os.makedirs(output_dir, exist_ok=True)

    for i, input_path in enumerate(image_files, start=1):
        rel_path = os.path.relpath(input_path, folder_path)
        output_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        compress_image(input_path, output_path, quality, scale)
        update_progress(int((i / total) * 100))

def update_progress(percent):
    progress_var.set(percent)
    progress_label_var.set(f"Progression : {percent}%")
    root.update_idletasks()

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp *.ico *.tga")])
    if file_path:
        progress_bar['value'] = 0
        progress_label_var.set("Compression en cours...")
        process_file(file_path, quality_slider.get(), scale_slider.get() / 100.0)
        messagebox.showinfo("Succès", "Image compressée avec succès.")
        progress_label_var.set("")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        progress_bar['value'] = 0
        progress_label_var.set("Compression en cours...")
        process_folder(folder_path, quality_slider.get(), scale_slider.get() / 100.0)
        messagebox.showinfo("Succès", "Images compressées avec succès.")
        progress_label_var.set("")

# Interface graphique
root = Tk()
root.title("🗜️ Compresseur d'images")
root.geometry("460x500")
root.resizable(False, False)

# Icône (optionnel)
try:
    from tkinter import PhotoImage
    icon = PhotoImage(file="icon.png")
    root.iconphoto(True, icon)
except Exception:
    pass

# TITRE PRINCIPAL
Label(root, text="🗜️ Compresseur d'images", font=("Arial", 18, "bold")).pack(pady=(15, 10))

# PARAMÈTRES
Label(root, text="🔧 Paramètres de compression", font=("Arial", 12, "bold")).pack(pady=(5, 5))

Label(root, text="Qualité JPEG/WEBP (%)", font=("Arial", 10)).pack(anchor="w", padx=20)
quality_slider = ttk.Scale(root, from_=20, to=95, orient="horizontal", length=300)
quality_slider.set(75)
quality_slider.pack(padx=20, pady=5)

Label(root, text="Taille de l’image (%)", font=("Arial", 10)).pack(anchor="w", padx=20)
scale_slider = ttk.Scale(root, from_=30, to=100, orient="horizontal", length=300)
scale_slider.set(100)
scale_slider.pack(padx=20, pady=5)

# TITRE SECONDAIRE
Label(root, text="🎯 Choisissez votre option de compression", font=("Arial", 13, "bold")).pack(pady=(25, 8))

# BOUTONS
Button(root, text="📁 Compresser une image", command=select_file, width=30).pack(pady=6)
Button(root, text="📂 Compresser un dossier", command=select_folder, width=30).pack(pady=6)

# BARRE DE PROGRESSION
Label(root, text="🔄 Progression", font=("Arial", 12, "bold")).pack(pady=(25, 5))

progress_var = IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)

progress_label_var = StringVar()
progress_label = Label(root, textvariable=progress_label_var, font=("Arial", 10))
progress_label.pack()

# LANCEMENT
root.mainloop()
