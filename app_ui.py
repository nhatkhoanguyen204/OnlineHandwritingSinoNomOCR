import tkinter as tk
from tkinter import ttk, messagebox
import settings
from styles import setup_styles
from ocr_engine import OCREngine
from typing import List, Tuple, Optional

class HandwritingApp:
    """
    Giao diện người dùng cho ứng dụng nhận diện chữ viết tay.
    Quản lý Canvas, các nút điều khiển và hiển thị kết quả.
    """
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = OCREngine()  # Khởi tạo OCR Engine (Singleton-like)
        
        self._initialize_state()
        setup_styles(self.root)
        self._setup_window()
        self._create_widgets()
        
        # Vẽ guidelines ban đầu
        self._draw_canvas_guidelines()

    def _initialize_state(self) -> None:
        """Khởi tạo các biến quản lý trạng thái vẽ."""
        self.stroke_count: int = 0
        self.strokes_history: List[str] = []
        self.guideline_ids: List[int] = []
        self.last_x: float = 0.0
        self.last_y: float = 0.0
        
        # UI Elements
        self.canvas: Optional[tk.Canvas] = None
        self.result_var: tk.StringVar = tk.StringVar(value="Ready to draw...")

    def _setup_window(self) -> None:
        """Cấu hình cửa sổ chính."""
        self.root.title(settings.TITLE)
        self.root.geometry(settings.WINDOW_SIZE)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

    def _create_widgets(self) -> None:
        """Tạo các khu vực giao diện."""
        self._create_top_section()
        self._create_middle_section()
        self._create_bottom_section()

    def _create_top_section(self) -> None:
        """Khu vực Canvas và các nút chức năng."""
        top_frame = ttk.Frame(self.root, padding=(20, 20, 20, 10))
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.columnconfigure(0, weight=1)

        # Container cho Canvas
        canvas_container = ttk.Frame(top_frame)
        canvas_container.pack(expand=True)

        ttk.Label(canvas_container, text="Draw below:", font=settings.FONT_BOLD).pack(anchor="w")

        self.canvas = tk.Canvas(
            canvas_container,
            width=settings.CANVAS_WIDTH,
            height=settings.CANVAS_HEIGHT,
            bg=settings.CANVAS_BG,
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(pady=10)

        # Bind sự kiện chuột
        self.canvas.bind("<Button-1>", self._handle_start_draw)
        self.canvas.bind("<B1-Motion>", self._handle_draw)
        self.canvas.bind("<ButtonRelease-1>", self._handle_stop_draw)

        # Buttons
        btn_frame = ttk.Frame(canvas_container)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="↶ Undo", command=self._handle_undo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Clear", style="Danger.TButton", command=self._handle_clear_canvas).pack(side="left", padx=5)

    def _create_middle_section(self) -> None:
        """Hiển thị kết quả nhận diện tức thời."""
        mid_frame = ttk.LabelFrame(self.root, text="Recognition Results", padding=(20, 10))
        mid_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        mid_frame.columnconfigure(0, weight=1)

        self.result_entry = ttk.Entry(
            mid_frame, textvariable=self.result_var, state="readonly", font=settings.FONT_LARGE
        )
        self.result_entry.grid(row=0, column=0, sticky="ew", ipady=8)

    def _create_bottom_section(self) -> None:
        """Khu vực thu thập văn bản cuối cùng."""
        bot_frame = ttk.LabelFrame(self.root, text="Final Text", padding=(20, 10))
        bot_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(5, 20))
        bot_frame.columnconfigure(0, weight=1)
        bot_frame.rowconfigure(0, weight=1)

        self.collection_text = tk.Text(bot_frame, wrap="word", font=settings.FONT_REGULAR)
        self.collection_text.grid(row=0, column=0, sticky="nsew")

        ctrl_frame = ttk.Frame(bot_frame)
        ctrl_frame.grid(row=1, column=0, sticky="e", pady=5)
        ttk.Button(ctrl_frame, text="Copy All", command=self._handle_copy_all).pack(side="right")

    # --- Handlers cho sự kiện vẽ ---

    def _handle_start_draw(self, event: tk.Event) -> None:
        self.stroke_count += 1
        self.last_x, self.last_y = float(event.x), float(event.y)
        self._remove_guidelines()

    def _handle_draw(self, event: tk.Event) -> None:
        tag = f"stroke_{self.stroke_count}"
        cur_x, cur_y = float(event.x), float(event.y)
        
        self.canvas.create_line(
            self.last_x, self.last_y, cur_x, cur_y,
            width=20, capstyle=tk.ROUND, smooth=True,
            fill="#282828", tags=tag
        )
        self.last_x, self.last_y = cur_x, cur_y

    def _handle_stop_draw(self, event: tk.Event) -> None:
        """Xử lý sau khi kết thúc 1 nét vẽ: Gọi Engine OCR."""
        if self.stroke_count == 0: return
        
        self.strokes_history.append(f"stroke_{self.stroke_count}")
        self.result_var.set("Processing...")
        
        # Gọi Logic OCR từ engine.py
        raw_img = self.engine.canvas_to_pil(self.canvas)
        processed_img = self.engine.preprocess(raw_img) if raw_img else None
        
        if processed_img:
            results = self.engine.recognize(processed_img)
            if results:
                best_text, prob = results[0]
                self.result_var.set(f"{best_text} ({prob:.2%})")
                self.collection_text.insert(tk.END, best_text)
            else:
                self.result_var.set("No character detected.")
        
        self._draw_canvas_guidelines()

    # --- Canvas Utilities ---

    def _draw_canvas_guidelines(self) -> None:
        w, h = settings.CANVAS_WIDTH, settings.CANVAS_HEIGHT
        opts = {'fill': '#f3f4f6', 'width': 2, 'tags': 'guideline'}
        self.guideline_ids.append(self.canvas.create_line(w/2, 0, w/2, h, **opts))
        self.guideline_ids.append(self.canvas.create_line(0, h/2, w, h/2, **opts))
        self.canvas.tag_lower("guideline")

    def _remove_guidelines(self) -> None:
        self.canvas.delete("guideline")
        self.guideline_ids.clear()

    def _handle_undo(self) -> None:
        if self.strokes_history:
            last_tag = self.strokes_history.pop()
            self.canvas.delete(last_tag)

    def _handle_clear_canvas(self) -> None:
        self.canvas.delete("all")
        self.strokes_history.clear()
        self.stroke_count = 0
        self._draw_canvas_guidelines()
        self.result_var.set("Canvas cleared.")

    def _handle_copy_all(self) -> None:
        text = self.collection_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Copied to clipboard!")