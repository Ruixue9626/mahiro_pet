"""
animation.py - 動畫控制器
管理所有動作的幀動畫切換
"""
import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, QObject, pyqtSignal


# 動畫狀態定義
class AnimState:
    IDLE = "idle"
    WORKING = "working"
    PAT = "pat"
    GRABBED = "grabbed"
    POKE = "poke"
    NOTIFY = "notify"
    CONFIRM = "confirm"


# 各動畫播放設定
ANIM_CONFIG = {
    AnimState.IDLE:    {"fps": 8,  "loop": True,  "next": None},
    AnimState.WORKING: {"fps": 10, "loop": True,  "next": None},
    AnimState.PAT:     {"fps": 10, "loop": False, "next": AnimState.IDLE},
    AnimState.GRABBED: {"fps": 8,  "loop": True,  "next": None},
    AnimState.POKE:    {"fps": 12, "loop": False, "next": AnimState.IDLE},
    AnimState.NOTIFY:  {"fps": 10, "loop": False, "next": AnimState.IDLE},
    AnimState.CONFIRM: {"fps": 10, "loop": False, "next": AnimState.IDLE},
}

# 預設佔位圖顏色（當圖片不存在時使用）
PLACEHOLDER_COLORS = {
    AnimState.IDLE:    "#A8D8EA",
    AnimState.WORKING: "#FFD3B6",
    AnimState.PAT:     "#FFAAA5",
    AnimState.GRABBED: "#D4A5A5",
    AnimState.POKE:    "#B5EAD7",
    AnimState.NOTIFY:  "#FFDAC1",
    AnimState.CONFIRM: "#C7CEEA",
}


class AnimationController(QObject):
    frame_changed = pyqtSignal(QPixmap)
    anim_finished = pyqtSignal(str)  # 動畫播放完畢時發出，帶狀態名

    def __init__(self, assets_dir: str, pet_size: tuple = (120, 120)):
        super().__init__()
        self.assets_dir = assets_dir
        self.pet_size = pet_size
        self.current_state = AnimState.IDLE
        self.frames: dict[str, list[QPixmap]] = {}
        self.current_frame_idx = 0
        self.placeholder_pixmaps: dict[str, QPixmap] = {}

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)

        self._load_all_frames()
        self._make_placeholders()

    # ── 載入圖片 ──────────────────────────────────────────────
    def _load_all_frames(self):
        """掃描 assets/ 下各子資料夾，載入幀圖"""
        all_states = [
            AnimState.IDLE, AnimState.WORKING, AnimState.PAT,
            AnimState.GRABBED, AnimState.POKE, AnimState.NOTIFY, AnimState.CONFIRM
        ]
        for state in all_states:
            folder = os.path.join(self.assets_dir, state)
            frames = []
            if os.path.isdir(folder):
                files = sorted(
                    f for f in os.listdir(folder)
                    if f.lower().endswith((".png", ".jpg", ".webp"))
                )
                for f in files:
                    path = os.path.join(folder, f)
                    px = QPixmap(path)
                    if not px.isNull():
                        px = px.scaled(
                            *self.pet_size,
                            aspectRatioMode=__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AspectRatioMode.KeepAspectRatio,
                            transformMode=__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.TransformationMode.SmoothTransformation,
                        )
                        frames.append(px)
            self.frames[state] = frames

    def _make_placeholders(self):
        """沒有圖片時，生成純色佔位 pixmap"""
        from PyQt6.QtGui import QColor, QPainter
        from PyQt6.QtCore import Qt as _Qt
        w, h = self.pet_size
        for state, color in PLACEHOLDER_COLORS.items():
            px = QPixmap(w, h)
            px.fill(QColor(0, 0, 0, 0))
            painter = QPainter(px)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(color))
            painter.setPen(_Qt.PenStyle.NoPen)
            painter.drawEllipse(10, 10, w - 20, h - 20)
            # 畫眼睛
            painter.setBrush(QColor("#333333"))
            painter.drawEllipse(w // 2 - 18, h // 2 - 10, 10, 10)
            painter.drawEllipse(w // 2 + 8, h // 2 - 10, 10, 10)
            # 嘴巴
            from PyQt6.QtGui import QPen
            painter.setPen(QPen(QColor("#333333"), 2))
            painter.setBrush(_Qt.BrushStyle.NoBrush)
            from PyQt6.QtCore import QRect
            painter.drawArc(QRect(w // 2 - 12, h // 2, 24, 14), 0, -180 * 16)
            # 狀態標籤
            painter.setPen(QColor("#555555"))
            from PyQt6.QtGui import QFont
            font = QFont()
            font.setPixelSize(9)
            painter.setFont(font)
            painter.drawText(0, h - 4, w, 12,
                             __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignHCenter,
                             state)
            painter.end()
            self.placeholder_pixmaps[state] = px

    # ── 狀態切換 ──────────────────────────────────────────────
    def set_state(self, state: str, force: bool = False):
        """切換到指定動畫狀態"""
        if state == self.current_state and not force:
            return
        self.current_state = state
        self.current_frame_idx = 0
        self._timer.stop()

        cfg = ANIM_CONFIG.get(state, {"fps": 8})
        interval = max(1, int(1000 / cfg["fps"]))
        self._timer.start(interval)
        self._emit_current_frame()

    def _next_frame(self):
        frames = self.frames.get(self.current_state, [])
        cfg = ANIM_CONFIG.get(self.current_state, {"loop": True, "next": None})
        total = len(frames) if frames else 1

        self.current_frame_idx += 1
        if self.current_frame_idx >= total:
            if cfg["loop"]:
                self.current_frame_idx = 0
            else:
                self.current_frame_idx = total - 1
                self._timer.stop()
                next_state = cfg.get("next")
                self.anim_finished.emit(self.current_state)
                if next_state:
                    self.set_state(next_state)
                return
        self._emit_current_frame()

    def _emit_current_frame(self):
        frames = self.frames.get(self.current_state, [])
        if frames:
            px = frames[self.current_frame_idx]
        else:
            px = self.placeholder_pixmaps.get(self.current_state,
                                               self.placeholder_pixmaps[AnimState.IDLE])
        self.frame_changed.emit(px)

    @property
    def state(self):
        return self.current_state
