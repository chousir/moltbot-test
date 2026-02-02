# MoltBot AI Investment Advisory System (MoltBot AI 投顧決策系統)

> **"Risk control first, profit follows."**
> — Alpha, Chief FinTech Consultant

## 📖 Project Overview (專案概述)

MoltBot 是一套運行於 GitHub Codespaces 的 **模組化 AI 投資顧問系統**。
它模擬了一間真實投顧公司的運作架構，由多位「虛擬分析師」組成的團隊，針對 **台灣股市 (TWSE)** 進行全天候的監控、分析與決策。

本系統專注於 **長期價值投資 (Long-term Value Investing)**，並輔以籌碼面與技術面尋找最佳買賣點。

---

## 🏗️ Architecture (系統架構)

我們採用 **"Committee-based AI" (委員會式 AI)** 架構。最終決策並非由單一指標決定，而是由不同領域的專家權重投票產生。

### 👥 The Virtual Analyst Team (虛擬分析師團隊)

1.  **The Valuator (基本面獵人)** `Weight: 40%`
    *   **任務**: 評估公司內在價值，尋找安全邊際。
    *   **數據源**: TWSE 本益比、殖利率、股價淨值比 (BWIBBU)。
    *   **邏輯**: 尋找低 PE、低 PB 或高殖利率的優質股。

2.  **The Chip Watcher (籌碼面偵探)** `Weight: 30%`
    *   **任務**: 追蹤聰明錢 (Smart Money) 流向。
    *   **數據源**: TWSE 三大法人買賣超日報 (T86)。
    *   **邏輯**: 識別外資 (Foreign) 與投信 (Trust) 的連續買超行為。

3.  **The Strategist (總經策略師)** `Weight: 20%`
    *   **任務**: 監控宏觀風險。
    *   **數據源**: VIX 恐慌指數 (Yahoo Finance)。
    *   **邏輯**: 在市場極度恐慌時建議減碼，在平穩時建議加碼。

4.  **The Chartist (技術面專家)** `Weight: 10%`
    *   **任務**: 擇時 (Timing)。
    *   **數據源**: K 線圖 (Yahoo Finance)。
    *   **邏輯**: 使用 MACD, RSI, 布林通道判斷進出場點與支撐/壓力位。

---

## 🚀 Features (核心功能)

*   **Industry-First Analysis (產業導向)**: 報告以產業為單位 (如半導體、AI 伺服器)，而非散亂個股。
*   **Dual-Tier Selection (雙層選股)**:
    *   🛡️ **Core Holdings (核心持股)**: 高市值、獲利穩健、籌碼安定的龍頭股。
    *   🌟 **Rising Stars (明日之星)**: 高成長潛力、股本較小、動能強勁的黑馬。
*   **Actionable Pricing (價位預測)**: 自動計算 **Target Price (目標價)** 與 **Stop Loss (停損點)**。
*   **Self-Correction (自我修正)**: 內建決策日誌與回測機制。

---

## 🛠️ Installation & Usage (安裝與使用)

### Prerequisites
*   Python 3.12+
*   Environment: GitHub Codespaces (Recommended)

### Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Daily Advisory Report (每日投顧報告):**
   ```bash
   python3 run_advisory.py
   ```
   *這將掃描 `config/universe.json` 中的所有板塊，並產出投資建議。*

3. **Analyze Single Ticker:**
   ```bash
   python3 main.py 2330.TW
   ```

---

## 📂 Directory Structure

*   `modules/`: 分析師邏輯核心 (Brains)。
*   `data/`: 暫存數據與緩存。
*   `logs/`: 決策日誌 (用於檢討)。
*   `config/`: 股票池與系統設定。

---

## ⚠️ Disclaimer (免責聲明)

本系統僅供學術研究與輔助參考，不構成任何證券買賣之要約或建議。投資人應獨立判斷並自負風險。

**Owner:** Steven Chou (Chairman)
**Built by:** Alpha (Chief AI Consultant)
