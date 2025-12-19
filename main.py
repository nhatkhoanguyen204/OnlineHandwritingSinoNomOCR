import tkinter as tk
from app_ui import HandwritingApp

def main():
    root = tk.Tk()
    app = HandwritingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()