#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Image to PDF
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🖼️
# @raycast.description Convert images to a PDF

# Documentation:
# @raycast.author YoavTC
# @raycast.authorURL https://raycast.com/YoavTC


import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont
import io
from datetime import datetime

class ImageToPDF:
	def __init__(self, root):
		self.root = root
		self.root.title("Image to PDF")
		self.root.geometry("500x600")

		self.images = []  # list of PIL.Image (RGBA or RGB)
		self.thumb_refs = []  # keep refs so tkinter doesn't GC thumbnails

		top = tk.Frame(root)
		top.pack(fill="x", pady=8)

		tk.Button(top, text="Add Image File(s)", command=self.add_files).pack(side="left", padx=6)
		tk.Button(top, text="Paste Image (Ctrl+V)", command=self.paste_image).pack(side="left", padx=6)
		tk.Button(top, text="Export PDF", command=self.export_pdf).pack(side="right", padx=6)

		self.page_index_var = tk.BooleanVar(value=False)
		tk.Checkbutton(root, text="Overlay page index", variable=self.page_index_var).pack(anchor="w", padx=6)

		self.count_label = tk.Label(root, text="0 images")
		self.count_label.pack()

		container = tk.Frame(root)
		container.pack(fill="both", expand=True)

		self.canvas = tk.Canvas(container)
		scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
		self.list_frame = tk.Frame(self.canvas)

		self.list_frame.bind(
			"<Configure>",
			lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		)

		self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
		self.canvas.configure(yscrollcommand=scrollbar.set)

		self.canvas.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		self.root.bind_all("<Control-v>", lambda e: self.paste_image())

	def add_files(self):
		paths = filedialog.askopenfilenames(
			filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
		)
		for p in paths:
			try:
				img = Image.open(p)
				img.load()
				self.images.append(img)
			except Exception as e:
				messagebox.showerror("Error", f"Could not open {p}: {e}")
		self.refresh_list()

	def paste_image(self):
		try:
			clip = ImageGrab.grabclipboard()
		except Exception as e:
			messagebox.showerror("Error", f"Clipboard read failed: {e}")
			return

		if clip is None:
			messagebox.showinfo("No image", "No image found on clipboard.")
			return

		if isinstance(clip, list):
			for p in clip:
				try:
					img = Image.open(p)
					img.load()
					self.images.append(img)
				except Exception:
					pass
		else:
			self.images.append(clip)

		self.refresh_list()

	def remove_image(self, index):
		del self.images[index]
		self.refresh_list()

	def refresh_list(self):
		for widget in self.list_frame.winfo_children():
			widget.destroy()
		self.thumb_refs.clear()

		for i, img in enumerate(self.images):
			row = tk.Frame(self.list_frame, bd=1, relief="solid")
			row.pack(fill="x", padx=6, pady=4)

			thumb = img.copy()
			thumb.thumbnail((80, 80))
			if thumb.mode == "RGBA":
				bg = Image.new("RGB", thumb.size, "white")
				bg.paste(thumb, mask=thumb.split()[3])
				thumb = bg
			tk_thumb = ImageTk.PhotoImage(thumb)
			self.thumb_refs.append(tk_thumb)

			tk.Label(row, image=tk_thumb).pack(side="left", padx=6, pady=6)
			tk.Label(row, text=f"Image {i+1} ({img.width}x{img.height})").pack(side="left", padx=6)
			tk.Button(row, text="Remove", command=lambda i=i: self.remove_image(i)).pack(side="right", padx=6)

		self.count_label.config(text=f"{len(self.images)} images")

	def add_page_index(self, img, index):
		overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
		draw = ImageDraw.Draw(overlay)
		font_size = max(10, min(img.size) // 30)
		font = None
		for font_name in ("Courier New Bold.ttf", "Courier New.ttf", "cour.ttf", "Courier.ttf", "DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf"):
			try:
				font = ImageFont.truetype(font_name, font_size)
				break
			except Exception:
				continue
		if font is None:
			font = ImageFont.load_default()

		text = f"{index:02d}"
		bbox = draw.textbbox((0, 0), text, font=font)
		text_w = bbox[2] - bbox[0]
		text_h = bbox[3] - bbox[1]
		margin = font_size // 2
		x = img.width - text_w - margin
		y = img.height - text_h - margin

		draw.text((x, y), text, font=font, fill=(0, 0, 0, 80))
		return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

	def export_pdf(self):
		if not self.images:
			messagebox.showinfo("No images", "Add or paste at least one image first.")
			return

		default_name = datetime.now().strftime("%d-%m-%Y_%H-%M")
		path = filedialog.asksaveasfilename(
			defaultextension=".pdf",
			initialfile=default_name,
			filetypes=[("PDF files", "*.pdf")]
		)
		if not path:
			return

		flattened = []
		for img in self.images:
			if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
				img = img.convert("RGBA")
				bg = Image.new("RGB", img.size, "white")
				bg.paste(img, mask=img.split()[3])
				flattened.append(bg)
			else:
				flattened.append(img.convert("RGB"))

		if self.page_index_var.get():
			flattened = [self.add_page_index(img, i) for i, img in enumerate(flattened)]

		try:
			flattened[0].save(path, save_all=True, append_images=flattened[1:])
			messagebox.showinfo("Done", f"Saved to {path}")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save PDF: {e}")


if __name__ == "__main__":
	root = tk.Tk()
	app = ImageToPDF(root)
	root.mainloop()