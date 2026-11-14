## Windows 版

本專案是以 Linux／X11 為目標開發的（`setup.sh`、`notify-send`、X11 視窗旗標）。
**Windows 移植版**由 [@1NotAmon](https://github.com/1NotAmon ) 維護在
[`mahiro_pet_windows`](https://github.com/1NotAmon/mahiro_pet_windows )，
角色與素材完全沿用，Linux 用法保持不變，同一份程式碼在 Linux 上照樣能跑。

- 倉庫：<https://github.com/1NotAmon/mahiro_pet_windows>
- 下載：<https://github.com/1NotAmon/mahiro_pet_windows/releases/latest>
  （每個 release 都附 Source code zip／tar.gz，解壓即可，不需要裝 Git）
- 授權：沿用本專案的 MIT，角色設計與素材版權仍屬於原始作者

### 安裝

需要 64 位元的 Python 3.10 以上（PyQt6 沒有 32-bit wheel）。於 PowerShell 執行：

```powershell
git clone https://github.com/1NotAmon/mahiro_pet_windows.git
cd mahiro_pet_windows
powershell -ExecutionPolicy Bypass -File setup.ps1
```

`setup.ps1` 會自動建立 `.venv`、安裝依賴，完成後直接啟動。已經裝過再跑一次會跳過
安裝直接啟動，不會重複裝套件。沒有裝 Git 的話，直接下載上面 release 頁的 zip，
解壓後跑同樣那行 `setup.ps1` 就好。

### 日常啟動

| 想做的事 | 怎麼做 |
|---|---|
| 正常啟動（看不到終端機視窗） | 雙擊 `啟動桌寵.bat` |
| 想同時看 log | 雙擊 `啟動桌寵_除錯模式.bat` |
| 檢查環境是否正常 | `python main.py --info` |
| 測試系統通知鏈路 | `python main.py --test-notify` |
| 開機自動啟動 | `python main.py --autostart on`（取消：`off`） |

桌寵本身不需要 Copilot CLI 也能跑（只是不會自動切換工作動畫）。要在 Windows 上搭配
Copilot CLI，先裝它：

```powershell
winget install GitHub.Copilot
```

### 跟 Linux 版的差異

| 項目 | 說明 |
|---|---|
| 系統通知 | 改用 Windows 原生 Toast（走桌寵自己的系統匣，並在啟動 QApplication 前註冊 AppUserModelID）。不需要 `plyer`，`requirements.txt` 用環境標記讓 Windows 不安裝它 |
| 開機自啟 | Windows 寫 `HKCU\...\Run`，Linux 仍是 `.desktop` |
| 氣泡視窗旗標 | `X11BypassWindowManagerHint` 只在 Linux 使用，Windows 改補 `WindowDoesNotAcceptFocus`（氣泡出現時不搶終端機焦點） |
| 定位 | 改用 `availableGeometry()` 並在拖曳結束／DPI 變更後 clamp，不會被工作列擋住或被拖到螢幕外找不回來 |
| 視窗掃描 | 程序偵測在 Windows 改用 Toolhelp32 快照（實測一次掃描 3210ms → 12.6ms），並排除 Win11 內建的 Copilot App 造成的誤判 |
| 啟動速度 | 動畫幀改背景執行緒載入，`PetWindow` 建立 0.38 秒即可見（原本要等 3.5 秒） |
| 單實例 | Windows 用 `CreateMutexW`、Linux/macOS 用 `flock`，雙擊兩次不會跑出兩隻桌寵 |
| 設定 | 新增 `settings.json`（尺寸、FPS、互動門檻、copilot 路徑…），不用改程式碼就能調；附 `settings.json.example` |
| 多出的檔案 | `setup.ps1`、`啟動桌寵.bat`、`啟動桌寵_除錯模式.bat`、`platform_utils.py`、`config.py` |

移植過程中也一併修掉了幾個在 Linux 版同樣存在的問題（例如第一幀沒送出導致
桌寵看不見、確認按鈕不會出現）。完整記錄在移植版 README 的
「移植過程：Linux → Windows」章節，想參考或摘回本專案都可以。
