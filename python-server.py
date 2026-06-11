#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Python Server
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🐍
# @raycast.description Start a local python server

# Documentation:
# @raycast.author YoavTC
# @raycast.authorURL https://raycast.com/YoavTC

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import socket

# ── Palette ────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"   # window background
SURFACE   = "#2a2a3d"   # card / frame background
BORDER    = "#3a3a54"   # subtle border
ACCENT    = "#7c6af7"   # purple accent (buttons)
ACCENT_HO = "#9b8dff"   # hover
ACCENT_DI = "#4a4465"   # disabled
TEXT      = "#cdd6f4"   # primary text
SUBTEXT   = "#7f849c"   # muted text
GREEN     = "#a6e3a1"
RED       = "#f38ba8"
ENTRY_BG  = "#313244"
FONT_BODY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 9)


class FlatButton(tk.Button):
    """A flat, rounded-looking button with hover feedback."""

    def __init__(self, master, accent=True, **kw):
        bg = ACCENT if accent else SURFACE
        fg = "#ffffff" if accent else TEXT
        ab = ACCENT_HO if accent else BORDER
        db = ACCENT_DI if accent else SURFACE
        kw.setdefault("padx", 16)
        kw.setdefault("pady", 7)
        super().__init__(
            master,
            bg=bg, fg=fg,
            activebackground=ab, activeforeground="#ffffff",
            disabledforeground=SUBTEXT,
            relief="flat", bd=0,
            font=FONT_BOLD,
            cursor="hand2",
            **kw,
        )
        self._bg_normal = bg
        self._bg_hover  = ab
        self._bg_disabled = db
        self._accent = accent
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self._bg_hover)

    def _on_leave(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self._bg_normal)

    def config(self, **kw):
        super().config(**kw)
        if "state" in kw and kw["state"] == "disabled":
            super().config(bg=self._bg_disabled)
        elif "state" in kw and kw["state"] == "normal":
            super().config(bg=self._bg_normal)


class ServerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python HTTP Server")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.server_process = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(padx=24, pady=20, fill="both")

        # Header
        tk.Label(
            outer, text="HTTP Server", font=FONT_HEAD, bg=BG, fg=TEXT
        ).pack(anchor="w")
        tk.Label(
            outer, text="python -m http.server", font=FONT_MONO, bg=BG, fg=SUBTEXT
        ).pack(anchor="w", pady=(0, 14))

        # Card
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14)
        card.pack(fill="x")
        card.configure(highlightbackground=BORDER, highlightthickness=1)

        # Port
        self._row(card, 0, "Port")
        self.port_var = tk.StringVar(value="8000")
        port_entry = tk.Entry(
            card, textvariable=self.port_var, width=10,
            bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=FONT_BODY, bd=4,
        )
        port_entry.grid(row=0, column=1, sticky="w", pady=5)

        # Directory
        self._row(card, 1, "Directory")
        self.dir_var = tk.StringVar(value=os.getcwd())
        dir_entry = tk.Entry(
            card, textvariable=self.dir_var, width=38,
            bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=FONT_BODY, bd=4,
        )
        dir_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(0, 6))
        FlatButton(card, text="Browse…", accent=False, command=self._browse, padx=10).grid(
            row=1, column=2, sticky="w", pady=5
        )

        # Separator
        sep = tk.Frame(outer, height=1, bg=BORDER)
        sep.pack(fill="x", pady=10)

        # Status pill
        self.status_var = tk.StringVar(value="Stopped")
        status_frame = tk.Frame(outer, bg=BG)
        status_frame.pack(fill="x", pady=(0, 4))

        tk.Label(status_frame, text="Status:", font=FONT_BOLD, bg=BG, fg=SUBTEXT).pack(
            side="left"
        )
        self.status_badge = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=FONT_BODY,
            bg=BG,
            fg=SUBTEXT,
            wraplength=380,
            justify="left",
        )
        self.status_badge.pack(side="left", padx=8)

        # Dot indicator
        self.dot = tk.Label(status_frame, text="●", font=("Segoe UI", 10), bg=BG, fg=SUBTEXT)
        self.dot.pack(side="left")

        # Buttons
        btn_frame = tk.Frame(outer, bg=BG)
        btn_frame.pack(fill="x", pady=(12, 0))
        self.start_btn = FlatButton(btn_frame, text="Start Server", command=self._start)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.stop_btn = FlatButton(
            btn_frame, text="Stop Server", accent=False, command=self._stop, state="disabled"
        )
        self.stop_btn.pack(side="left")

    def _row(self, parent, row, label):
        tk.Label(
            parent, text=label, font=FONT_BOLD, bg=SURFACE, fg=SUBTEXT, width=10, anchor="w"
        ).grid(row=row, column=0, sticky="w")

    # ── Logic ──────────────────────────────────────────────────────────────

    def _browse(self):
        chosen = filedialog.askdirectory(initialdir=self.dir_var.get())
        if chosen:
            self.dir_var.set(chosen)

    def _validate(self):
        try:
            port = int(self.port_var.get())
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number (1–65535).")
            return False
        directory = self.dir_var.get().strip()
        if not os.path.isdir(directory):
            messagebox.showerror(
                "Invalid Directory", f"The directory does not exist:\n{directory}"
            )
            return False
        return True

    def _get_local_ipv4(self):
        """Return the best local IPv4 address for LAN access, if available."""
        sock = None
        try:
            # This does not send traffic; it asks the OS which interface would route out.
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            pass
        finally:
            if sock is not None:
                sock.close()

        try:
            for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
                ip = info[4][0]
                if ip and not ip.startswith("127."):
                    return ip
        except Exception:
            pass

        return None

    def _start(self):
        if not self._validate():
            return
        port = self.port_var.get().strip()
        directory = self.dir_var.get().strip()
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", port],
                cwd=directory,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to start server:\n{exc}")
            return

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        ipv4 = self._get_local_ipv4()
        if ipv4:
            self.status_var.set(f"http://localhost:{port}/  |  http://{ipv4}:{port}/  ·  {directory}")
        else:
            self.status_var.set(f"http://localhost:{port}/  ·  {directory}")
        self.status_badge.config(fg=GREEN)
        self.dot.config(fg=GREEN)

    def _stop(self):
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Stopped")
        self.status_badge.config(fg=SUBTEXT)
        self.dot.config(fg=SUBTEXT)

    def _on_close(self):
        self._stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app._on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
