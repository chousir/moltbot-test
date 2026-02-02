# Performance Auditor & Dynamic Weighting 模組使用指南

## 📋 概述

`PerformanceAuditor` 是 Alpha 系統的自我進化引擎，負責：

1. **預測追蹤** - 記錄每日預測（T+1, T+5, T+20 時間窗口）
2. **準確度驗證** - 在預測到期時對比真實股價，計算誤差
3. **績效評估** - 根據多維度指標評估每位分析師的表現
4. **動態權重調整** - 根據績效自動調整分析師在決策中的權重
5. **歸因分析** - 區分失敗類型，給予差異化懲罰

---

## 🚀 快速開始

### 1. 自動運行（集成在 main.py）

```bash
python main.py 2330.TW
```

系統會自動：
- ✅ 驗證過去的預測
- ✅ 生成績效報告
- ✅ 根據績效調整權重
- ✅ 執行當日分析

### 2. 手動審計命令

```bash
# 驗證已到期的預測
python run_audit.py --verify

# 查看績效報告
python run_audit.py --report

# 手動調整權重
python run_audit.py --adjust

# 完整審計周期（推薦）
python run_audit.py --full

# 查看明日之星候選
python run_audit.py --stars

# 顯示績效歷史
python run_audit.py --history
```

---

## 📊 核心概念

### 時間窗口

| 窗口 | 時長 | 用途 |
|------|------|------|
| **T+1** | 1 天 | 短期技術面驗證 |
| **T+5** | 5 天 | 周級別趨勢驗證 |
| **T+20** | 20 天 | 月級別方向驗證 |

每個預測在各時間窗口到期時都會被獨立驗證。

### 準確度評分

```
預測方向 + 誤差幅度 = 準確度評分

✓ 方向正確 + 誤差 < 5%   → 100% 準確度
✓ 方向正確 + 誤差 5-15%  → 70% 準確度
✓ 方向正確 + 誤差 > 15%  → 40% 準確度
✗ 方向錯誤                → 0% 準確度
```

### 績效指標

每位分析師被評估的維度：

| 指標 | 含義 | 計算方式 |
|------|------|--------|
| **Mean Accuracy** | 平均準確度 | 所有預測的平均得分 |
| **Stability** | 穩定性 | 1 - (標準差 / 2.0)，越低越穩定 |
| **Calibration** | 信心校準 | 預期信心度 vs 實際命中率一致性 |
| **Overall Score** | 綜合評分 | 50% 準確度 + 30% 穩定性 + 20% 校準 |

### 綜合評級

| 評級 | Overall Score | 權重調整 |
|------|---------------|--------|
| 🌟 **Excellent** | > 80% | +4% |
| ✅ **Good** | 60-80% | +2% |
| ➡️ **Normal** | 40-60% | 0% |
| ⚠️ **Poor** | 20-40% | -5% |
| 🔴 **Critical** | < 20% | -10% |

---

## 🔄 歸因分析 (Attribution Analysis)

當預測失敗時，系統會自動判斷原因並給予針對性懲罰：

| 失敗類型 | 原因 | 責任分析師 | 懲罰類型 |
|---------|------|-----------|--------|
| **技術面失敗** | 技術指標反向 | Chartist | 重度 (-8%) |
| **基本面失敗** | 盈利不如預期 | Valuator | 重度 (-8%) |
| **籌碼面失敗** | 機構行為異常 | ChipWatcher/WhaleHunter | 重度 (-8%) |
| **宏觀失敗** | 政策/大盤突變 | Strategist | 中度 (-5%) |
| **系統性失敗** | 黑天鵝事件 | 全體 | 輕度 (-3%) |

---

## ⚙️ 配置參數

### 權重邊界 (Weight Limits)

防止單一分析師過度主導或被邊緣化：

```python
{
    "The Valuator (Fundamental)": (0.20, 0.50),        # 最低 20%，最高 50%
    "The Chip Watcher (Institutional)": (0.10, 0.35),  # 最低 10%，最高 35%
    "The Whale Hunter (Large Holders)": (0.10, 0.35),
    "The Strategist (Macro)": (0.05, 0.25),
    "The Chartist (Technical)": (0.02, 0.20)            # 最低 2%（防止出局）
}
```

### 冷卻期 (Cooldown)

權重調整後 **3 天內不再調整**，防止過度震盪。

---

## 📁 數據結構

### 績效歷史 (`data/audit/performance_history.json`)

```json
{
  "predictions": {
    "2330.TW_2026-02-02": {
      "ticker": "2330.TW",
      "prediction_date": "2026-02-02",
      "entry_price": 450.50,
      "analysts": [
        {
          "analyst_name": "The Chartist (Technical)",
          "signal": "BUY",
          "confidence": 0.75,
          ...
        }
      ],
      "actual_prices": {
        "T+1": 453.20,
        "T+5": 458.75,
        "T+20": 465.30
      },
      "T+1_verified": true,
      "T+5_verified": true,
      "T+20_verified": true
    }
  },
  "audits": [
    {
      "timestamp": "2026-02-03T10:30:00",
      "prediction_key": "2330.TW_2026-02-02",
      "window": "T+1",
      "entry_price": 450.50,
      "actual_price": 453.20,
      "accuracy": 0.95,
      "attribution": {
        "failure_type": "normal",
        "analyst_responsible": null,
        "recommendation": "..."
      }
    }
  ],
  "analyst_stats": {}
}
```

### 權重調整日誌 (`data/audit/weight_adjustments.jsonl`)

每行一條調整記錄：

```json
{
  "timestamp": "2026-02-05T14:00:00",
  "old_weights": {
    "The Valuator (Fundamental)": 0.35,
    ...
  },
  "new_weights": {
    "The Valuator (Fundamental)": 0.38,
    ...
  },
  "performance_metrics": {
    "The Valuator (Fundamental)": {
      "mean_accuracy": 0.82,
      "stability": 0.85,
      "calibration": 0.78,
      "overall_score": 0.817,
      "recommendation": "excellent"
    }
  }
}
```

---

## 🌟 「明日之星」識別標準

系統會自動識別最有潛力的分析師，篩選標準：

```
1. Overall Score > 70%
2. Stability > 60%
3. Calibration > 70%
4. Prediction Count >= 3
```

查看候選：
```bash
python run_audit.py --stars
```

---

## 📈 監控指標

### 關鍵 KPI

```
1. 系統平均準確度 - 所有預測的平均得分
2. 預測命中率 - 方向正確的預測占比
3. 誤差均值 - 平均幅度偏離
4. 分析師一致性 - 5 位分析師的信號一致度
5. 權重穩定性 - 月度權重變化幅度
```

### 監控腳本

```bash
# 顯示歷史摘要
python run_audit.py --history

# 顯示最新績效報告
python run_audit.py --report
```

---

## 🔧 高級用法

### 手動記錄預測

如果需要手動測試，可直接調用：

```python
from modules.performance_auditor import PerformanceAuditor

auditor = PerformanceAuditor()

# 記錄預測
analysts_report = [
    {"analyst_name": "The Chartist", "signal": "BUY", "confidence": 0.75, ...},
    ...
]

pred_key = auditor.record_prediction("2330.TW", analysts_report, 450.50)

# 手動驗證
auditor.verify_predictions()

# 查看報告
print(auditor.generate_audit_report())
```

### 修改權重調整參數

編輯 `modules/performance_auditor.py`：

```python
self.weight_adjustment_params = {
    "excellent": 0.05,      # 改為 +5%
    "good": 0.03,           # 改為 +3%
    "normal": 0.0,
    "poor": -0.06,          # 改為 -6%
    "critical": -0.12,      # 改為 -12%
}
```

---

## 🐛 常見問題

### Q: 為什麼預測沒有被驗證？

A: 檢查幾點：
1. 預測日期是否正確？
2. 是否距今已過 T+1/T+5/T+20 天？
3. yfinance 是否能取得該股票的數據？

```bash
# 調試：檢查績效歷史
python -c "
from modules.performance_auditor import PerformanceAuditor
auditor = PerformanceAuditor()
import json
print(json.dumps(auditor.performance_history, indent=2, ensure_ascii=False))
"
```

### Q: 權重為什麼沒有調整？

A: 可能原因：
1. 冷卻期未到達（3 天）
2. 績效數據不足（< 3 個預測）
3. 沒有已驗證的預測

查看最後調整時間：
```bash
cat /workspaces/moltbot-test/data/audit/adjustment_log.json
```

### Q: 如何重置所有審計數據？

A: 
```bash
rm -rf /workspaces/moltbot-test/data/audit/*
```

**警告：此操作會清除所有績效歷史！**

---

## 📚 相關文件

- **核心模組**: [modules/performance_auditor.py](../modules/performance_auditor.py)
- **集成代碼**: [main.py](../main.py)
- **命令行工具**: [run_audit.py](../run_audit.py)
- **績效數據**: `data/audit/performance_history.json`
- **調整日誌**: `data/audit/weight_adjustments.jsonl`

---

## 🎯 下一步優化方向

1. **機器學習集成** - 用 ML 模型預測最佳權重
2. **特殊市場狀態適配** - 牛市/熊市各自的權重配置
3. **實時信心更新** - 根據市場流動性動態調整信心度
4. **跨時間窗口相關性** - 分析 T+1/T+5/T+20 的一致性
5. **異常檢測** - 使用 Isolation Forest 識別黑天鵝事件

---

**最後更新**: 2026-02-02  
**作者**: Alpha Performance Auditor Team
