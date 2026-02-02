# 🚀 PerformanceAuditor 快速參考卡片

## 命令速查表

```bash
# 完整審計（推薦日常使用）
python run_audit.py --full

# 分步操作
python run_audit.py --verify          # 驗證已到期預測
python run_audit.py --report          # 顯示績效報告
python run_audit.py --adjust          # 調整權重
python run_audit.py --stars           # 查看明日之星
python run_audit.py --history         # 歷史摘要

# 運行分析（自動觸發審計）
python main.py 2330.TW                # 自動執行完整流程

# 演示場景
python test_performance_auditor.py    # 查看系統實際運作
```

---

## 權重調整算法

```
輸入：過去 7 天的預測績效

計算步驟：
1. 計算每位分析師的綜合評分
   综合評分 = 50% × 準確度 
            + 30% × 穩定性 
            + 20% × 信心校準

2. 根據評分確定等級 → 調整係數
   Excellent (>80%)  → ×1.04
   Good (60-80%)     → ×1.02
   Normal (40-60%)   → ×1.00
   Poor (20-40%)     → ×0.95
   Critical (<20%)   → ×0.90

3. 應用邊界限制（防止極端配置）
   Valuator:        20% ≤ w ≤ 50%
   Others:          5-25% ≤ w ≤ 35%

4. 正規化（確保 Σweights = 100%）
   新權重 = (原權重 × 係數) / 總和

輸出：調整後的權重配置
```

---

## 準確度評分機制

```
真實價格 vs 預測價格的比較方式：

預測信號 + 實際漲跌 = 準確度
┌─────────────────────────────────────┐
│ ✓ BUY  + 股價上漲 + 誤差 < 5%  = 100%│
│ ✓ BUY  + 股價上漲 + 誤差 5-15% = 70% │
│ ✓ BUY  + 股價上漲 + 誤差 > 15% = 40% │
│ ✗ BUY  + 股價下跌              = 0%  │
│                                     │
│ 同理適用於 SELL 和 NEUTRAL 信號      │
└─────────────────────────────────────┘

時間窗口：T+1（1 天）、T+5（5 天）、T+20（20 天）
```

---

## 數據流向圖

```
Alpha 每日分析
    ↓
記錄預測 (entry_price, analysts, signal, confidence)
    ↓
T+1 天時
    ├─ 從 yfinance 獲取實際價格
    ├─ 計算準確度 (accuracy score)
    ├─ 執行歸因分析 (failure type)
    └─ 記錄審計結果
    ↓
每 3 天一次
    ├─ 計算分析師綜合評分
    ├─ 判定等級 (excellent/good/normal/poor/critical)
    ├─ 計算新權重係數
    ├─ 應用邊界限制
    └─ 正規化 → 寫入日誌
    ↓
下一輪分析時
    ├─ 使用新權重重新計算 final_score
    └─ Alpha 做出更精準的決策
```

---

## 文件清單

| 文件 | 大小 | 用途 |
|------|------|------|
| `modules/performance_auditor.py` | 550 行 | 核心模組 |
| `main.py` | 修改 | 集成審計 |
| `run_audit.py` | 250 行 | 命令行工具 |
| `test_performance_auditor.py` | 280 行 | 演示場景 |
| `PERFORMANCE_AUDITOR_GUIDE.md` | 長文檔 | 詳細使用說明 |
| `STRATEGY_DECISION_DOCUMENT.md` | 長文檔 | 戰略決策指南 |
| `data/audit/performance_history.json` | 動態 | 預測記錄 |
| `data/audit/weight_adjustments.jsonl` | 動態 | 調整日誌 |

---

## 常見操作

### 查看最新績效報告
```bash
python run_audit.py --report
```

### 手動驗證預測（用於測試）
```bash
python run_audit.py --verify
```

### 看預測歷史
```bash
python -c "
import json
from modules.performance_auditor import PerformanceAuditor
auditor = PerformanceAuditor()
print(f'總預測數: {len(auditor.performance_history[\"predictions\"])}')
print(f'已審計: {len(auditor.performance_history[\"audits\"])}')
"
```

### 強制重置審計數據
```bash
rm -rf /workspaces/moltbot-test/data/audit/*
```

---

## 效能指標監控

監控這 5 個數字，掌握系統狀況：

```
1. 系統平均準確度    = 所有審計的 accuracy 平均值
   目標: > 70%

2. 預測命中率        = 方向正確的預測占比
   目標: > 65%

3. 分析師一致性      = 5 位分析師信號相同的比例
   目標: > 50%

4. 權重月度變化      = max(新權重) - max(舊權重)
   目標: < 10%（防止過度波動）

5. 明日之星數量      = 符合標準的分析師
   目標: 最少 1 位，最多 3 位
```

查看實時監控：
```bash
python run_audit.py --history
```

---

## 故障排除

### ❌ 問題：預測沒被驗證
```
可能原因：
1. 距今時間不足（需滿足 T+1/T+5/T+20）
2. yfinance 無該股票數據
3. 預測記錄不完整

解決方案：
python -c "
from datetime import datetime, timedelta
from modules.performance_auditor import PerformanceAuditor
auditor = PerformanceAuditor()
for key in auditor.performance_history['predictions']:
    print(key)
"
```

### ❌ 問題：權重沒有調整
```
可能原因：
1. 冷卻期未過（需 3 天）
2. 預測數不足（需 ≥ 3 個）
3. 沒有已驗證的預測

檢查冷卻期：
cat /workspaces/moltbot-test/data/audit/adjustment_log.json
```

### ❌ 問題：Import 錯誤
```bash
# 確保依賴安裝
pip install -r requirements.txt

# 檢查路徑
python -c "import sys; print(sys.path)"
```

---

## 權重調整範例

```
舊配置 (default):
  The Valuator:           35%
  The Chip Watcher:       25%
  The Whale Hunter:       20%
  The Strategist:         15%
  The Chartist:           5%

若 7 天績效：
  The Valuator:    EXCELLENT (99%) → +4%
  The Chartist:    EXCELLENT (95%) → +4%
  The Strategist:  POOR (35%)      → -5%
  The Chip Watcher: GOOD (72%)     → +2%
  The Whale Hunter: NORMAL (50%)   → 0%

計算新權重：
  Valuator:    35% × 1.04 = 36.4%
  Chartist:     5% × 1.04 =  5.2%
  Strategist:  15% × 0.95 = 14.25%
  Chip Watcher: 25% × 1.02 = 25.5%
  Whale Hunter: 20% × 1.00 = 20.0%
  ────────────────────────────
  小計：                   101.35%

正規化（除以總和 1.0135）：
  Valuator:     35.9%
  Chartist:      5.1%
  Strategist:   14.0%
  Chip Watcher: 25.2%
  Whale Hunter: 19.8%
  ────────────────────
  總計：      100.0% ✓
```

---

## 一行命令速查

```bash
# 查看所有可用命令
python run_audit.py --help

# 完整流程
python run_audit.py --full

# 僅審計並查看明日之星
python run_audit.py --verify --stars

# 生成性能歷史記錄
python run_audit.py --history > audit_report_$(date +%Y%m%d).txt

# 自動每日運行（加入 crontab）
0 9 * * * cd /workspaces/moltbot-test && python main.py 2330.TW >> logs/daily.log 2>&1
0 18 * * * cd /workspaces/moltbot-test && python run_audit.py --full >> logs/audit.log 2>&1
```

---

**最後更新**: 2026-02-02  
**系統狀態**: Production Ready ✅
