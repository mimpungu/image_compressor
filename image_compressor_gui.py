
#!/usr/bin/env python3
import os
import shutil
import threading
from tkinter import filedialog, Tk, StringVar, IntVar, messagebox, Button, Label, Entry, Toplevel
from tkinter import ttk
from tkinter import TclError
from PIL import Image
from io import BytesIO

SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico', '.tga'
)

output_folder = None  # Dossier de sortie choisi par l'utilisateur, None = dossier "compressed"
TARGET_FILE_SIZE = 20 * 1024  # 20 KB in bytes

def compress_image_pil(img, img_format, quality=75, target_size=TARGET_FILE_SIZE):
    """Renvoie une image PIL compressée selon le format, visant ~20 KB."""
    quality = max(20, min(int(quality), 95))  # Restrict quality between 20 and 95
    scale = 1.0  # Initial scale
    max_attempts = 5  # Limit iterations to avoid infinite loops

    for attempt in range(max_attempts):
        if img_format in ['JPEG', 'JPG']:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            bio = BytesIO()
            img.save(bio, format='JPEG', optimize=True, quality=quality, progressive=True, subsampling=2)
            bio.seek(0)
            size = bio.getbuffer().nbytes
            if size <= target_size or attempt == max_attempts - 1 or quality <= 20:
                return Image.open(bio)
            quality = max(20, quality - 10)  # Reduce quality by 10
            if size > target_size and attempt >= 2:  # Start scaling after 2 attempts
                scale = max(0.7, scale * 0.9)  # Reduce scale by 10%
                w, h = img.size
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        elif img_format == 'PNG':
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256 if attempt == 0 else max(64, 256 - attempt * 64))
            bio = BytesIO()
            img.save(bio, format='PNG', optimize=True, compress_level=9)
            bio.seek(0)
            size = bio.getbuffer().nbytes
            if size <= target_size or attempt == max_attempts - 1:
                return Image.open(bio)
            if size > target_size and attempt >= 2:
                scale = max(0.7, scale * 0.9)
                w, h = img.size
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        elif img_format == 'WEBP':
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGBA')
            bio = BytesIO()
            img.save(bio, format='WEBP', quality=quality, optimize=True, method=6)
            bio.seek(0)
            size = bio.getbuffer().nbytes
            if size <= target_size or attempt == max_attempts - 1 or quality <= 20:
                return Image.open(bio)
            quality = max(20, quality - 10)
            if size > target_size and attempt >= 2:
                scale = max(0.7, scale * 0.9)
                w, h = img.size
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        else:
            return img.copy()

    return img.copy()  # Fallback if compression fails

def get_output_path(input_path, target_ext):
    global output_folder
    base_name = os.path.splitext(os.path.basename(input_path))[0] + f".{target_ext.lower()}"  # Use target extension
    if output_folder:
        out_dir = output_folder
    else:
        out_dir = os.path.join(os.path.dirname(input_path), "compressed")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, base_name)

def threaded_task(func):
    def wrapper(*args, **kwargs):
        def task():
            try:
                func(*args, **kwargs)
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue :\n{e}")
            finally:
                root.after(0, enable_ui)
        disable_ui()
        threading.Thread(target=task, daemon=True).start()
    return wrapper

def disable_ui():
    for widget in buttons:
        try:
            widget.config(state='disabled')
        except TclError:
            pass
    try:
        quality_slider.config(state='disabled')
    except TclError:
        pass
    try:
        scale_slider.config(state='disabled')
    except TclError:
        pass
    try:
        progress_bar.config(state='disabled')
    except TclError:
        pass

def enable_ui():
    for widget in buttons:
        try:
            widget.config(state='normal')
        except TclError:
            pass
    try:
        quality_slider.config(state='normal')
    except TclError:
        pass
    try:
        scale_slider.config(state='normal')
    except TclError:
        pass
    try:
        progress_bar.config(state='normal')
    except TclError:
        pass

def update_progress(percent):
    progress_var.set(percent)
    progress_label_var.set(f"Progression : {percent}%")
    root.update_idletasks()

@threaded_task
def process_file(file_path, quality, scale):
    update_progress(0)
    try:
        img = Image.open(file_path)
        img_format = img.format.upper() if img.format else 'JPEG'  # Fallback to JPEG

        if scale < 1.0:
            w, h = img.size
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        compressed_img = compress_image_pil(img, img_format, quality)
        output_path = get_output_path(file_path, img_format.lower())
        compressed_img.save(output_path)
        messagebox.showinfo("Succès", "Image compressée avec succès")
        update_progress(100)
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur compression : {e}")

@threaded_task
def process_folder(folder_path, quality, scale):
    image_files = []
    for root_dir, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(os.path.join(root_dir, f))

    total = len(image_files)
    if total == 0:
        messagebox.showinfo("Info", "Aucune image trouvée.")
        update_progress(0)
        enable_ui()
        return

    output_dir = output_folder if output_folder else os.path.join(folder_path, "compressed")
    os.makedirs(output_dir, exist_ok=True)

    for i, input_path in enumerate(image_files, start=1):
        try:
            img = Image.open(input_path)
            img_format = img.format.upper() if img.format else 'JPEG'
            if scale < 1.0:
                w, h = img.size
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            compressed_img = compress_image_pil(img, img_format, quality)

            rel_path = os.path.relpath(input_path, folder_path)
            output_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            compressed_img.save(output_path)
        except Exception as e:
            print(f"Erreur compression {input_path} : {e}")
        update_progress(int((i / total) * 100))
    messagebox.showinfo("Succès", "Compression du dossier terminée avec succès")

@threaded_task
def convert_to_format(folder_path, target_format, quality=75, scale_factor=1.0):
    image_files = []
    for root_dir, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(os.path.join(root_dir, f))

    total = len(image_files)
    if total == 0:
        messagebox.showinfo("Info", "Aucune image trouvée.")
        update_progress(0)
        enable_ui()
        return

    output_dir = output_folder if output_folder else os.path.join(folder_path, "compressed")
    os.makedirs(output_dir, exist_ok=True)

    for i, input_path in enumerate(image_files, start=1):
        try:
            img = Image.open(input_path)
            if scale_factor < 1.0:
                w, h = img.size
                img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.LANCZOS)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_name = f"{base_name}.{target_format.lower()}"
            rel_path = os.path.relpath(input_path, folder_path)
            output_path = os.path.join(output_dir, os.path.dirname(rel_path), output_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if target_format.upper() == "PNG":
                processed_img = compress_image_pil(img, 'PNG', quality)
                processed_img.save(output_path, format='PNG', optimize=True, compress_level=9)
            elif target_format.upper() in ['JPEG', 'JPG']:
                processed_img = compress_image_pil(img, 'JPEG', quality)
                processed_img.save(output_path, format='JPEG', quality=min(int(quality), 95), optimize=True, progressive=True, subsampling=2)
            elif target_format.upper() == "WEBP":
                processed_img = compress_image_pil(img, 'WEBP', quality)
                processed_img.save(output_path, format='WEBP', quality=min(int(quality), 95), optimize=True, method=6)
            else:
                shutil.copy(input_path, output_path)
        except Exception as e:
            print(f"Erreur conversion {input_path} : {e}")
        update_progress(int((i / total) * 100))

    messagebox.showinfo("Succès", f"Conversion vers {target_format.upper()} terminée avec succès")

@threaded_task
def convert_single_image(input_path, target_format, quality=75, scale_factor=1.0):
    try:
        img = Image.open(input_path)
        if scale_factor < 1.0:
            w, h = img.size
            img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.LANCZOS)
        output_path = get_output_path(input_path, target_format.lower())

        if target_format.upper() == "PNG":
            processed_img = compress_image_pil(img, 'PNG', quality)
            processed_img.save(output_path, format='PNG', optimize=True, compress_level=9)
        elif target_format.upper() in ['JPEG', 'JPG']:
            processed_img = compress_image_pil(img, 'JPEG', quality)
            processed_img.save(output_path, format='JPEG', quality=min(int(quality), 95), optimize=True, progressive=True, subsampling=2)
        elif target_format.upper() == "WEBP":
            processed_img = compress_image_pil(img, 'WEBP', quality)
            processed_img.save(output_path, format='WEBP', quality=min(int(quality), 95), optimize=True, method=6)
        else:
            processed_img = img.copy()
            shutil.copy(input_path, output_path)

        messagebox.showinfo("Succès", f"Image convertie en {target_format.upper()} avec succès")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur conversion : {e}")

@threaded_task
def rename_folder_images(folder_path, base_name):
    if not base_name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom de base pour les fichiers.")
        return

    image_files = []
    for root_dir, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(os.path.join(root_dir, f))

    total = len(image_files)
    if total == 0:
        messagebox.showinfo("Info", "Aucune image trouvée.")
        update_progress(0)
        enable_ui()
        return

    output_dir = output_folder if output_folder else os.path.join(folder_path, "compressed")
    os.makedirs(output_dir, exist_ok=True)

    for i, input_path in enumerate(image_files, start=1):
        try:
            img = Image.open(input_path)
            img_format = img.format.upper() if img.format else 'JPEG'
            compressed_img = compress_image_pil(img, img_format, quality_slider.get())

            rel_path = os.path.relpath(input_path, folder_path)
            output_name = f"{base_name}-{i}.{img_format.lower()}"
            output_path = os.path.join(output_dir, os.path.dirname(rel_path), output_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            compressed_img.save(output_path)
        except Exception as e:
            print(f"Erreur renommage/compression {input_path} : {e}")
        update_progress(int((i / total) * 100))
    messagebox.showinfo("Succès", f"Renommage et compression terminés avec succès")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp *.ico *.tga")])
    if file_path:
        process_file(file_path, quality_slider.get(), scale_slider.get() / 100.0)

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_folder(folder_path, quality_slider.get(), scale_slider.get() / 100.0)

def convert_folder_to_png():
    folder_path = filedialog.askdirectory()
    if folder_path:
        convert_to_format(folder_path, "PNG", scale_factor=scale_slider.get() / 100.0)

def convert_folder_to_webp():
    folder_path = filedialog.askdirectory()
    if folder_path:
        convert_to_format(folder_path, "WEBP", quality=quality_slider.get(), scale_factor=scale_slider.get() / 100.0)

def convert_jpg_to_png():
    file_path = filedialog.askopenfilename(filetypes=[("JPEG images", "*.jpg *.jpeg")])
    if file_path:
        convert_single_image(file_path, "PNG", quality=quality_slider.get(), scale_factor=scale_slider.get() / 100.0)

def convert_png_to_jpg():
    file_path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
    if file_path:
        convert_single_image(file_path, "JPEG", quality=quality_slider.get(), scale_factor=scale_slider.get() / 100.0)

def choose_output_folder():
    global output_folder
    folder = filedialog.askdirectory()
    if folder:
        output_folder = folder
        output_folder_var.set(output_folder)
    else:
        output_folder = None
        output_folder_var.set("Utiliser le dossier 'compressed'")

def rename_images_dialog():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    dialog = Toplevel(root)
    dialog.title("Renommer les images")
    dialog.geometry("300x150")
    dialog.resizable(False, False)

    Label(dialog, text="Entrez le nom de base pour les fichiers :", font=("Arial", 10)).pack(pady=10)
    base_name_entry = Entry(dialog, width=30)
    base_name_entry.pack(pady=5)

    def on_submit():
        base_name = base_name_entry.get().strip()
        dialog.destroy()
        rename_folder_images(folder_path, base_name)

    def on_cancel():
        dialog.destroy()

    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=10)
    Button(btn_frame, text="Valider", command=on_submit, width=10).pack(side="left", padx=10)
    Button(btn_frame, text="Annuler", command=on_cancel, width=10).pack(side="right", padx=10)

# --- Interface graphique ---
root = Tk()
root.title("🗜️ Compresseur d'images")
root.geometry("480x720")
root.resizable(False, False)

try:
    from tkinter import PhotoImage
    icon = PhotoImage(file="icon.png")
    root.iconphoto(True, icon)
except Exception:
    pass

Label(root, text="🗜️ Compresseur d'images", font=("Arial", 18, "bold")).pack(pady=(15, 0))

Label(root, text="Sous-titre : Outil simple pour compresser et convertir vos images", font=("Arial", 11, "bold"), fg="red").pack(pady=(0, 10))

Label(root, text="🔧 Paramètres de compression", font=("Arial", 12, "bold")).pack(pady=(5, 5))

Label(root, text="Qualité JPEG/WEBP (%)", font=("Arial", 10)).pack(anchor="w", padx=20)
quality_slider = ttk.Scale(root, from_=20, to=95, orient="horizontal", length=320)
quality_slider.set(75)
quality_slider.pack(padx=20, pady=5)

Label(root, text="Taille de l’image (%)", font=("Arial", 10)).pack(anchor="w", padx=20)
scale_slider = ttk.Scale(root, from_=30, to=100, orient="horizontal", length=320)
scale_slider.set(100)
scale_slider.pack(padx=20, pady=5)

Label(root, text="📂 Choix dossier de sortie", font=("Arial", 12, "bold")).pack(pady=(15, 3))

output_folder_var = StringVar(value="Utiliser le dossier 'compressed'")
output_folder_label = Label(root, textvariable=output_folder_var, fg="blue")
output_folder_label.pack()

Button(root, text="🗂️ Choisir dossier de sortie", command=choose_output_folder, width=35).pack(pady=(5, 15))

Label(root, text="🎯 Choisissez votre option de compression / conversion", font=("Arial", 13, "bold")).pack(pady=(5, 8))

buttons = []
btn1 = Button(root, text="📁 Compresser une image", command=select_file, width=35)
btn1.pack(pady=6)
buttons.append(btn1)

btn2 = Button(root, text="📂 Compresser un dossier", command=select_folder, width=35)
btn2.pack(pady=6)
buttons.append(btn2)

btn3 = Button(root, text="🖼️ Convertir un dossier vers PNG", command=convert_folder_to_png, width=35)
btn3.pack(pady=6)
buttons.append(btn3)

btn4 = Button(root, text="🌐 Convertir un dossier vers WEBP", command=convert_folder_to_webp, width=35)
btn4.pack(pady=6)
buttons.append(btn4)

btn5 = Button(root, text="🖼️ Convertir une image JPG/JPEG vers PNG", command=convert_jpg_to_png, width=35)
btn5.pack(pady=6)
buttons.append(btn5)

btn6 = Button(root, text="🖼️ Convertir une image PNG vers JPG/JPEG", command=convert_png_to_jpg, width=35)
btn6.pack(pady=6)
buttons.append(btn6)

btn7 = Button(root, text="🔄 Renommer et compresser un dossier", command=rename_images_dialog, width=35)
btn7.pack(pady=6)
buttons.append(btn7)

Label(root, text="🔄 Progression", font=("Arial", 12, "bold")).pack(pady=(25, 5))

progress_var = IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=320, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)

progress_label_var = StringVar()
progress_label = Label(root, textvariable=progress_label_var, font=("Arial", 10))
progress_label.pack()

Label(root, text="© 2025 Deo Mimpungu - Tous droits réservés", font=("Arial", 9, "italic")).pack(side="bottom", pady=10)

root.mainloop()
