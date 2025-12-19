import io
import easyocr
import numpy as np
from PIL import Image, ImageOps
from typing import Optional, List, Tuple
import tkinter as tk

class OCREngine:
    """Xử lý toàn bộ logic liên quan đến nhận diện hình ảnh."""
    
    def __init__(self):
        # Khởi tạo Reader một lần duy nhất để tối ưu hiệu năng
        self.reader = easyocr.Reader(['ch_tra'], gpu=False, quantize=True)

    def canvas_to_pil(self, canvas: tk.Canvas) -> Optional[Image.Image]:
        """Chuyển đổi dữ liệu Canvas Tkinter sang PIL Image."""
        try:
            ps_data = canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps_data.encode('utf-8')))
            return img.convert("RGB")
        except Exception as e:
            print(f"Lỗi chuyển đổi ảnh: {e}")
            return None

    def preprocess(self, pil_img: Image.Image) -> Optional[Image.Image]:
        """Tiền xử lý ảnh: Crop sát nội dung và thêm padding."""
        gray = pil_img.convert("L")
        inverted = ImageOps.invert(gray)
        bbox = inverted.getbbox()
        
        if not bbox:
            return None
            
        padding = 20
        w, h = pil_img.size
        safe_bbox = (
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(w, bbox[2] + padding),
            min(h, bbox[3] + padding)
        )
        return pil_img.crop(safe_bbox)

    def recognize(self, pil_img: Image.Image) -> List[Tuple[str, float]]:
        """Thực hiện nhận diện và trả về danh sách (văn bản, độ tin cậy)."""
        # Chuyển PIL sang Numpy array cho EasyOCR
        img_array = np.array(pil_img)
        
        results = self.reader.readtext(
            img_array,
            decoder='greedy',
            mag_ratio=1.0,
            threshold=0.1
        )
        
        # Sắp xếp theo độ tin cậy giảm dần
        sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
        return [(text, prob) for (_, text, prob) in sorted_results]