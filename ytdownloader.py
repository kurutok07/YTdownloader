import yt_dlp
import urllib.request
from PIL import Image, ImageTk
from io import BytesIO
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import urllib.request
from io import BytesIO

# === GUI Setup ===
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("500x600")

def set_app_icon_from_url(url):
    try:
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        icon_image = Image.open(BytesIO(raw_data))
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(False, icon_photo)
    except Exception as e:
        print(f"Gagal load icon: {e}")

root.iconbitmap("app_icon.ico")  

# Entry URL
tk.Label(root, text="Enter YouTube video URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

# Folder selection
folder_path = tk.StringVar()

def select_folder():
    path = filedialog.askdirectory()
    folder_path.set(path)
    folder_label.config(text=f"Folder: {path}")

tk.Button(root, text="Pilih Folder Simpan", command=select_folder).pack(pady=5)
folder_label = tk.Label(root, text="Folder: Belum dipilih")
folder_label.pack()

# Thumbnail preview
thumbnail_label = tk.Label(root)
thumbnail_label.pack(pady=10)

# Progress label
progress_label = tk.Label(root, text="", fg="green")
progress_label.pack(pady=10)

# === Logic ===
def show_thumbnail(url):
    try:
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        img = Image.open(BytesIO(raw_data)).resize((320, 180))
        tk_img = ImageTk.PhotoImage(img)
        thumbnail_label.config(image=tk_img)
        thumbnail_label.image = tk_img
    except Exception as e:
        print("Gagal load thumbnail:", e)

def run_download():
    video_url = url_entry.get()
    save_path = folder_path.get()

    if not video_url or not save_path:
        messagebox.showwarning("Input Error", "Mohon isi URL dan pilih folder penyimpanan.")
        return

    def progress_hook(d):
        if d['status'] == 'downloading':
            progress_label.config(text=f"Downloading: {d['_percent_str']} - ETA: {d['_eta_str']}")
        elif d['status'] == 'finished':
            progress_label.config(text="Merging audio + video...")

    try:
        # Ambil info & thumbnail
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            thumbnail = info.get("thumbnail")
            if thumbnail:
                show_thumbnail(thumbnail)
    except Exception as e:
        messagebox.showerror("Gagal", f"Gagal ambil info video:\n{e}")
        return

    # Konfigurasi download
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        progress_label.config(text="Download completed!")
        messagebox.showinfo("Selesai", "Video berhasil diunduh.")
    except Exception as e:
        progress_label.config(text="")
        messagebox.showerror("Gagal", str(e))

# Button download
tk.Button(root, text="Download Video", command=lambda: threading.Thread(target=run_download).start()).pack(pady=10)

root.mainloop()
