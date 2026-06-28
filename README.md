# 🐾 Desktop Pet — GitHub Copilot CLI 桌寵

PyQt6 桌寵，監聽 `copilot` 指令執行狀態，自動切換動畫並顯示通知。

---

## 快速開始

```bash
# 1. 進入專案資料夾
cd desktop_pet

# 2. 一鍵安裝 + 啟動
bash setup.sh
```

第一次執行會自動建立虛擬環境並安裝依賴。之後每次啟動只要：

```bash
source .venv/bin/activate
python3 main.py
```

---

## 放入你的圖片

把動畫幀圖片放進 `assets/` 對應的資料夾，
圖片格式支援 `.png`、`.jpg`、`.webp`，命名用數字排序：

```
assets/
├── idle/        # 待機（循環）
│   ├── 001.png
│   ├── 002.png
│   └── ...
├── working/     # Copilot 工作中（循環）
├── pat/         # 摸頭（播完回 idle）
├── grabbed/     # 被抓起（循環，直到放下）
├── poke/        # 點一下（播完回 idle）
├── notify/      # 完成通知（播完顯示確認按鈕）
└── confirm/     # 按確認按鈕（播完回 idle）
```

> 沒放圖片也沒關係！會用內建彩色圓圈代替。

---

## 功能說明

| 互動 | 觸發方式 |
|---|---|
| **點一下** | 快速點擊（< 250ms） |
| **摸頭** | 按住 250~800ms 後放開 |
| **抓起來** | 按住 > 800ms，可以拖著走 |
| **確認按鈕** | Copilot 完成後出現，點擊確認 |
| **拖曳移動** | 按住後移動滑鼠超過 5px |

### 自動監聽 Copilot
- 桌寵每秒掃描一次 process，偵測到 `copilot` 在跑 → 切換工作動畫
- Copilot 結束 → 播放通知動畫 + 送出系統通知 + 顯示確認按鈕

### 系統托盤
- 左鍵點托盤圖示 → 顯示/隱藏桌寵
- 右鍵 → 選單（顯示 / 關閉）

---

## 依賴套件

```
PyQt6       # UI 框架
psutil      # process 監聽
plyer       # 系統通知 fallback
Pillow      # 圖片處理（備用）
```

系統通知優先使用 `notify-send`（大部分 Linux 桌面環境都有），
沒有的話自動 fallback 到 `plyer`。

---

## 調整設定

打開 `pet_window.py` 最上方可以修改：

```python
PET_SIZE = (120, 120)   # 桌寵大小（像素）

POKE_MAX_MS = 250       # 點一下最長按住時間
PAT_MAX_MS = 800        # 摸頭最長按住時間，超過就是抓起
```

打開 `animation.py` 可以調整各動畫 FPS：

```python
ANIM_CONFIG = {
    "idle":    {"fps": 8,  "loop": True},
    "working": {"fps": 10, "loop": True},
    "pat":     {"fps": 10, "loop": False},
    ...
}
```
