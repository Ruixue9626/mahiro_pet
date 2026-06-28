# Mahiro Desktop Pet

<p align="center">
  <img src="assets/idle/001.png" width="120" alt="Mahiro Desktop Pet" />
</p>

<p align="center">
  一個在你桌面上陪你寫 code 的 PyQt6 桌寵，會監聽 GitHub Copilot CLI 的執行狀態，自動切換動畫與送出系統通知。
</p>

---

## Features

- 監聽 `copilot` 指令執行狀態，自動切換動畫
- 支援多種互動：點一下、摸頭、抓起來拖著走
- Copilot 完成時顯示通知 + 確認按鈕動畫
- 系統托盤圖示，可快速顯示 / 隱藏桌寵
- 支援自訂動畫幀圖片（PNG / JPG / WebP）

---

## Requirements

- Linux（需要支援 `xcb` 的桌面環境）
- Python 3.10 以上
- GitHub Copilot CLI（`copilot` 指令需在 PATH 中）

---

## Environment Setup

確認系統有安裝 Python 3.10+：

```bash
python3 --version
```

如果版本不足，請先安裝：

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

確認已安裝 GitHub CLI 並設定 Copilot extension：

```bash
sudo apt install gh
gh auth login
```

將 `copilot` binary 放到 PATH 可存取的位置：

```bash
mv copilot ~/.local/bin/copilot
chmod +x ~/.local/bin/copilot
```

---

## Installation

### Method 1 — setup.sh（推薦）

一鍵建立虛擬環境、安裝依賴並直接啟動：

```bash
git clone https://github.com/your-username/mahiro-pet.git
cd mahiro-pet
bash setup.sh
```

第一次執行會自動建立 `.venv` 虛擬環境並安裝所有套件。  
之後再次啟動只需要：

```bash
bash setup.sh
```

---

### Method 2 — 手動安裝

1. Clone 專案：

```bash
git clone https://github.com/your-username/mahiro-pet.git
cd mahiro-pet
```

2. （建議）建立虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. 安裝依賴：

```bash
pip install -r requirements.txt
```

4. 啟動：

```bash
python3 main.py
```

---

## Adding Your Sprites

將動畫幀圖片放進 `assets/` 對應的資料夾，命名用數字排序（`001.png`, `002.png`, ...）：

```
assets/
├── idle/        # 待機（循環播放）
├── working/     # Copilot 工作中（循環播放）
├── pat/         # 摸頭（播完回 idle）
├── grabbed/     # 被抓起來（循環，直到放下）
├── poke/        # 點一下（播完回 idle）
├── notify/      # 完成通知（播完顯示確認按鈕）
└── confirm/     # 點確認按鈕（播完回 idle）
```

支援格式：`.png` `.jpg` `.webp`

> 沒有放圖片也沒關係！會自動用內建彩色圓圈代替。

---

## Interactions

| 互動 | 觸發方式 |
|------|---------|
| 點一下 | 快速點擊（< 250ms） |
| 摸頭 | 按住 250 ~ 800ms 後放開 |
| 抓起來 | 按住 > 800ms，可以拖著走 |
| 確認按鈕 | Copilot 完成後出現，點一下確認 |
| 拖曳移動 | 按住後移動滑鼠超過 5px |

---

## Configuration

在 `pet_window.py` 最上方可以調整桌寵大小與互動時間閾值：

```python
PET_SIZE    = (240, 240)  # 桌寵大小（像素）
POKE_MAX_MS = 250         # 點一下最長按住時間（ms）
PAT_MAX_MS  = 800         # 摸頭最長時間，超過視為抓起
```

在 `animation.py` 可以調整各動畫的 FPS：

```python
ANIM_CONFIG = {
    "idle":    {"fps": 8,  "loop": True},
    "working": {"fps": 10, "loop": True},
    "pat":     {"fps": 10, "loop": False},
    # ...
}
```

---

## Dependencies

| 套件 | 用途 |
|------|------|
| `PyQt6` | UI 框架與視窗管理 |
| `psutil` | 監聽 process 執行狀態 |
| `plyer` | 系統通知 fallback |
| `Pillow` | 圖片處理（備用） |

系統通知優先使用 `notify-send`，沒有的話自動 fallback 到 `plyer`。

---

## License

MIT
