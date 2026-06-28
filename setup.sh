#!/bin/bash
# setup.sh - 一鍵安裝並啟動桌寵
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🐾 Desktop Pet 安裝中..."

# 檢查 Python 版本
python3 -c "import sys; assert sys.version_info >= (3,10), '需要 Python 3.10+'" \
  || { echo "❌ 請安裝 Python 3.10 以上版本"; exit 1; }

# 建立虛擬環境
if [ ! -d ".venv" ]; then
  echo "📦 建立虛擬環境..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 確認 assets 資料夾存在
for dir in idle working pat grabbed poke notify confirm; do
  mkdir -p "assets/$dir"
done

echo ""
echo "✅ 安裝完成！"
echo ""
echo "📌 使用說明："
echo "   把圖片放進 assets/ 對應的資料夾："
echo "   assets/idle/    → 待機動畫幀 (001.png, 002.png, ...)"
echo "   assets/working/ → Copilot 工作中動畫幀"
echo "   assets/pat/     → 摸頭動畫幀"
echo "   assets/grabbed/ → 被抓起動畫幀"
echo "   assets/poke/    → 點一下動畫幀"
echo "   assets/notify/  → 完成通知動畫幀"
echo "   assets/confirm/ → 確認按鈕動畫幀"
echo ""
echo "   沒放圖片也沒關係，會用內建佔位圓圈代替 🟣"
echo ""
echo "🚀 啟動桌寵..."
python3 main.py
