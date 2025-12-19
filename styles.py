import settings
from tkinter import ttk

def setup_styles(root):
    style = ttk.Style()
    style.configure("TButton", font=settings.FONT_REGULAR)
    style.configure("Accent.TButton", font=settings.FONT_BOLD, foreground="white")
    style.configure("Header.TLabel", font=settings.FONT_LARGE)