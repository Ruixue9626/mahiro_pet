"""
dialog_bubble.py - 對話框泡泡
跟著桌寵位置顯示的無邊框狀態泡泡
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen


class DialogBubble(QWidget):
    BUBBLE_W = 200
    BUBBLE_H = 70
    TAIL_H = 14   # 尾巴高度
    CORNER_R = 14
    BG_COLOR = QColor(255, 255, 255, 230)
    BORDER_COLOR = QColor(180, 180, 200, 200)
    TEXT_COLOR = QColor(60, 60, 80)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Tool |
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(self.BUBBLE_W, self.BUBBLE_H + self.TAIL_H)

        self._label = QLabel(self)
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPixelSize(13)
        self._label.setFont(font)
        self._label.setStyleSheet(f"color: rgb({self.TEXT_COLOR.red()},{self.TEXT_COLOR.green()},{self.TEXT_COLOR.blue()}); background: transparent;")
        self._label.setGeometry(12, 8, self.BUBBLE_W - 24, self.BUBBLE_H - 16)

        # 自動隱藏計時器
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

        self._opacity = 1.0
        self.hide()

    def show_message(self, text: str, duration_ms: int = 3000):
        """顯示訊息，duration_ms 後自動消失（0 = 不自動消失）"""
        self._label.setText(text)
        self._hide_timer.stop()
        self.show()
        self.raise_()
        if duration_ms > 0:
            self._hide_timer.start(duration_ms)

    def update_position(self, pet_pos: QPoint, pet_size: tuple):
        """根據桌寵位置更新泡泡位置（顯示在桌寵上方）"""
        pet_x, pet_y = pet_pos.x(), pet_pos.y()
        pet_w, pet_h = pet_size

        x = pet_x + pet_w // 2 - self.BUBBLE_W // 2
        y = pet_y - self.BUBBLE_H - self.TAIL_H - 4

        # 避免超出螢幕左右邊
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = max(0, min(x, screen.width() - self.BUBBLE_W))
        y = max(0, y)

        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.BUBBLE_W, self.BUBBLE_H
        r = self.CORNER_R
        tail_h = self.TAIL_H
        tail_w = 18
        tail_cx = w // 2

        # 氣泡主體路徑
        path = QPainterPath()
        path.moveTo(r, 0)
        path.lineTo(w - r, 0)
        path.quadTo(w, 0, w, r)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        # 尾巴（置中向下）
        path.lineTo(tail_cx + tail_w // 2, h)
        path.lineTo(tail_cx, h + tail_h)
        path.lineTo(tail_cx - tail_w // 2, h)
        path.lineTo(r, h)
        path.quadTo(0, h, 0, h - r)
        path.lineTo(0, r)
        path.quadTo(0, 0, r, 0)
        path.closeSubpath()

        # 陰影
        shadow_path = QPainterPath(path)
        shadow_path.translate(2, 2)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 30))

        # 主體
        painter.fillPath(path, self.BG_COLOR)

        # 邊框
        painter.setPen(QPen(self.BORDER_COLOR, 1.5))
        painter.drawPath(path)
