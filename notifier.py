"""
notifier.py - 系統通知
Copilot 完成工作後送出桌面通知
"""
import subprocess
import shutil


def notify(title: str, message: str, icon: str = "dialog-information"):
    """
    送出系統通知，優先使用 libnotify (notify-send)，
    fallback 到 plyer
    """
    # 優先用 notify-send（Linux 最通用）
    if shutil.which("notify-send"):
        try:
            subprocess.Popen([
                "notify-send",
                "--app-name", "Desktop Pet",
                "--icon", icon,
                "--urgency", "normal",
                title,
                message,
            ])
            return
        except Exception:
            pass

    # fallback: plyer
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Desktop Pet",
            timeout=5,
        )
    except Exception:
        # 最後 fallback：印到 stderr
        import sys
        print(f"[通知] {title}: {message}", file=sys.stderr)


def notify_copilot_done():
    notify(
        "✅ Copilot 完成了！",
        "GitHub Copilot CLI 已完成工作",
        icon="emblem-ok-symbolic",
    )


def notify_copilot_started():
    notify(
        "🤖 Copilot 開始工作",
        "GitHub Copilot CLI 正在執行中",
        icon="media-playback-start-symbolic",
    )
