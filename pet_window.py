"""
pet_window.py - 桌寵主視窗
"""
import os
import time
import random
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QIcon, QColor, QCursor, QAction

from animation import AnimationController, AnimState
from copilot_watcher import CopilotWatcher
from dialog_bubble import DialogBubble
from notifier import notify_copilot_done

PET_SIZE   = (240,240)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

POKE_MAX_MS = 250
PAT_MAX_MS  = 800
GRAB_MS     = 800


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._first_show  = True
        self._press_start = 0.0
        self._press_pos   = QPoint()
        self._drag_offset = QPoint()
        self._is_grabbed  = False

        self._init_window()
        self._init_widgets()
        self._init_animation()
        self._init_watcher()
        self._init_tray()
        self._init_timers()

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(PET_SIZE[0], PET_SIZE[1] + 36)

    def _init_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._pet_label = QLabel(self)
        self._pet_label.setFixedSize(*PET_SIZE)
        self._pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pet_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self._pet_label)

        self._confirm_btn = QPushButton("✓ 確認", self)
        self._confirm_btn.setFixedHeight(30)
        self._confirm_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 180, 130, 210);
                color: white; border: none; border-radius: 10px;
                font-size: 12px; font-weight: bold;
                padding: 0 8px; margin: 3px 8px;
            }
            QPushButton:hover   { background: rgba(80, 160, 110, 230); }
            QPushButton:pressed { background: rgba(60, 140, 90, 255); }
        """)
        self._confirm_btn.clicked.connect(self._on_confirm)
        self._confirm_btn.hide()
        layout.addWidget(self._confirm_btn)

        self._bubble = DialogBubble()

    def _init_animation(self):
        self._anim = AnimationController(ASSETS_DIR, PET_SIZE)
        self._anim.frame_changed.connect(self._pet_label.setPixmap)
        self._anim.anim_finished.connect(self._on_anim_finished)
        self._anim.set_state(AnimState.IDLE)

    def _init_watcher(self):
        self._watcher = CopilotWatcher(self)
        self._watcher.copilot_started.connect(self._on_copilot_started)
        self._watcher.copilot_stopped.connect(self._on_copilot_stopped)
        self._watcher.status_changed.connect(self._on_status_changed)
        self._watcher.start()

    def _init_tray(self):
        self._tray = QSystemTrayIcon(self)
        icon_px = QPixmap(32, 32)
        icon_px.fill(QColor("#A8D8EA"))
        icon_path = os.path.join(ASSETS_DIR, "idle", "001.png")
        if os.path.exists(icon_path):
            icon_px = QPixmap(icon_path).scaled(
                32, 32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self._tray.setIcon(QIcon(icon_px))
        self._tray.setToolTip("Desktop Pet 🐾")
        menu = QMenu()
        show_act = QAction("顯示桌寵", self)
        show_act.triggered.connect(self._show_pet)
        quit_act = QAction("關閉", self)
        quit_act.triggered.connect(QApplication.quit)
        menu.addAction(show_act)
        menu.addSeparator()
        menu.addAction(quit_act)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _init_timers(self):
        self._grab_timer = QTimer(self)
        self._grab_timer.setSingleShot(True)
        self._grab_timer.timeout.connect(self._trigger_grab)

        self._confirm_hide_timer = QTimer(self)
        self._confirm_hide_timer.setSingleShot(True)
        self._confirm_hide_timer.timeout.connect(self._confirm_btn.hide)

    # ══════════════════════════════════════════════
    # 顯示
    # ══════════════════════════════════════════════

    def _show_pet(self):
        if self._first_show:
            self._first_show = False
            screen = QApplication.primaryScreen().geometry()
            self.move(
                screen.width()  - self.width()  - 40,
                screen.height() - self.height() - 60
            )
        self.show()
        self.raise_()

    # ══════════════════════════════════════════════
    # 滑鼠互動
    # ══════════════════════════════════════════════

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._press_start = time.time() * 1000
        self._press_pos   = event.globalPosition().toPoint()
        self._drag_offset = event.globalPosition().toPoint() - self.pos()
        self._grab_timer.start(GRAB_MS)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        new_pos = event.globalPosition().toPoint() - self._drag_offset
        self.move(new_pos)
        self._update_bubble_pos()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._grab_timer.stop()
        held_ms = time.time() * 1000 - self._press_start

        if self._is_grabbed:
            self._is_grabbed = False
            self._anim.set_state(AnimState.IDLE)
            self._bubble.show_message("放我下來了～", 1500)
            self._update_bubble_pos()
            return

        if held_ms < POKE_MAX_MS:
            self._do_poke()
        elif held_ms < PAT_MAX_MS:
            self._do_pat()

    def _trigger_grab(self):
        self._is_grabbed = True
        self._anim.set_state(AnimState.GRABBED)
        self._bubble.show_message("哇！被抓住了！", 0)
        self._update_bubble_pos()

    def _do_poke(self):
        self._anim.set_state(AnimState.POKE, force=True)
        self._bubble.show_message(
            random.choice(["欸！？", "戳我幹嘛！", "嗚…", "///(〃＞＿＜；〃)"]), 2000)
        self._update_bubble_pos()

    def _do_pat(self):
        self._anim.set_state(AnimState.PAT, force=True)
        self._bubble.show_message(
            random.choice([">///<", "好舒服…", "摸頭摸頭～", "(∪｡∪)｡｡｡zzz"]), 2000)
        self._update_bubble_pos()

    def _on_anim_finished(self, state: str):
        if state == AnimState.CONFIRM:
            self._confirm_btn.hide()

    # ══════════════════════════════════════════════
    # Copilot 狀態
    # ══════════════════════════════════════════════

    def _on_copilot_started(self):
        if self._is_grabbed:
            return
        self._anim.set_state(AnimState.WORKING)
        self._bubble.show_message("Copilot 開始工作了！", 2500)
        self._update_bubble_pos()

    def _on_copilot_stopped(self):
        self._anim.set_state(AnimState.NOTIFY)
        self._bubble.show_message("✅ 完成啦！", 4000)
        self._update_bubble_pos()
        notify_copilot_done()

    def _on_status_changed(self, msg: str):
        self._tray.setToolTip(f"Desktop Pet 🐾 | {msg}")

    # ══════════════════════════════════════════════
    # 確認按鈕
    # ══════════════════════════════════════════════

    def _show_confirm_btn(self):
        self._confirm_btn.show()
        self._confirm_hide_timer.start(10000)

    def _on_confirm(self):
        self._anim.set_state(AnimState.CONFIRM, force=True)
        self._bubble.show_message("確認！(ﾉ>ω<)ﾉ", 2000)
        self._update_bubble_pos()
        self._confirm_btn.hide()
        self._confirm_hide_timer.stop()

    # ══════════════════════════════════════════════
    # 工具
    # ══════════════════════════════════════════════

    def _update_bubble_pos(self):
        self._bubble.update_position(self.pos(), (self.width(), PET_SIZE[1]))

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
                self._bubble.hide()
            else:
                self._show_pet()

    def paintEvent(self, event):
        pass

    def closeEvent(self, event):
        self._bubble.close()
        self._watcher.stop()
        QApplication.quit()
