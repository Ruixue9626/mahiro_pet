#!/usr/bin/env python3
"""
Desktop Pet - GitHub Copilot CLI 桌寵
主程式入口，自動檢查環境並啟動
"""
import sys
import os
import shutil
import subprocess

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from pet_window import PetWindow


def check_copilot():
    """找 copilot binary，找不到回傳 None"""
    path = shutil.which("copilot")
    if path:
        return path
    for candidate in [
        os.path.expanduser("~/.local/bin/copilot"),
        "/usr/local/bin/copilot",
        "/usr/bin/copilot",
    ]:
        if os.path.exists(candidate):
            return candidate
    return None


def show_install_guide(app):
    """找不到 copilot 時顯示安裝提示"""
    msg = QMessageBox()
    msg.setWindowTitle("找不到 GitHub Copilot CLI")
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText("找不到 copilot 指令！")
    msg.setInformativeText(
        "請先安裝 GitHub Copilot CLI：\n\n"
        "1. 確認已安裝 GitHub CLI：\n"
        "     sudo apt install gh\n\n"
        "2. 取得 copilot binary 並放到 PATH：\n"
        "     mv copilot ~/.local/bin/copilot\n"
        "     chmod +x ~/.local/bin/copilot\n\n"
        "安裝完後重新啟動桌寵。"
    )
    btn_ignore = msg.addButton("先跳過，繼續啟動", QMessageBox.ButtonRole.AcceptRole)
    msg.addButton("關閉", QMessageBox.ButtonRole.RejectRole)
    msg.exec()
    return msg.clickedButton() == btn_ignore


def check_dependencies():
    """檢查 Python 套件，回傳缺少的清單"""
    missing = []
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
    try:
        import plyer
    except ImportError:
        missing.append("plyer")
    return missing


def show_missing_deps(app, missing):
    """缺少套件時顯示安裝提示，可自動安裝"""
    pkgs = " ".join(missing)
    msg = QMessageBox()
    msg.setWindowTitle("缺少套件")
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText(f"缺少必要的 Python 套件：{pkgs}")
    msg.setInformativeText(
        f"請執行以下指令安裝：\n\n"
        f"  pip install {pkgs}\n\n"
        f"或點「自動安裝」讓我幫你裝。"
    )
    install_btn = msg.addButton("自動安裝", QMessageBox.ButtonRole.AcceptRole)
    msg.addButton("關閉", QMessageBox.ButtonRole.RejectRole)
    msg.exec()

    if msg.clickedButton() == install_btn:
        try:
            ret = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing,
                capture_output=True, text=True
            )
            if ret.returncode == 0:
                QMessageBox.information(
                    None, "安裝完成",
                    "套件安裝成功！\n請重新啟動桌寵。"
                )
            else:
                QMessageBox.critical(
                    None, "安裝失敗",
                    f"請手動執行：\npip install {pkgs}\n\n{ret.stderr}"
                )
        except Exception as e:
            QMessageBox.critical(None, "安裝失敗", str(e))
    sys.exit(1)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Pet")
    app.setQuitOnLastWindowClosed(False)

    # 1. 檢查 Python 依賴
    missing = check_dependencies()
    if missing:
        show_missing_deps(app, missing)
        return

    # 2. 檢查 copilot
    copilot_path = check_copilot()
    if not copilot_path:
        should_continue = show_install_guide(app)
        if not should_continue:
            sys.exit(0)

    # 3. 啟動桌寵
    window = PetWindow()
    window._show_pet()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
