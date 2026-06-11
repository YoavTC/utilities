#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Hash File
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🔒
# @raycast.description Generate a SHA-256 hash from a file

# Documentation:
# @raycast.author YoavTC
# @raycast.authorURL https://raycast.com/YoavTC

import hashlib
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 120


def file_hash(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def process_file(path):
    path = path.strip("{}")

    try:
        result_var.set(file_hash(path))
    except Exception as e:
        result_var.set(f"Error: {e}")


def on_drop(event):
    process_file(event.data)


def browse():
    path = filedialog.askopenfilename()
    if path:
        process_file(path)


def copy_hash():
    value = result_var.get()

    if value and not value.startswith("Error:"):
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()


root = TkinterDnD.Tk()
root.title("File Hash")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

drop_area = tk.Label(
    frame,
    text="Drag & drop a file here or click Browse",
    relief="groove",
    height=2,
)
drop_area.pack(fill="x")

drop_area.drop_target_register(DND_FILES)
drop_area.dnd_bind("<<Drop>>", on_drop)

top_row = tk.Frame(frame)
top_row.pack(fill="x", pady=5)

tk.Button(top_row, text="Browse", command=browse).pack(side="left")

hash_row = tk.Frame(frame)
hash_row.pack(fill="x")

result_var = tk.StringVar(value="SHA-256 hash will appear here")

result = tk.Entry(
    hash_row,
    textvariable=result_var,
)
result.pack(side="left", fill="x", expand=True)

tk.Button(
    hash_row,
    text="📋",
    width=3,
    command=copy_hash,
).pack(side="left", padx=(5, 0))

root.mainloop()