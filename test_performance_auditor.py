#!/usr/bin/env python3
"""
測試場景：演示 PerformanceAuditor 的完整工作流程

此腳本模擬：
1. 記錄過去的預測
2. 模擬時間推進（T+1, T+5, T+20）
3. 驗證預測準確度
4. 自動調整權重
"""

import sys
import json
from datetime import datetime, timedelta
from colorama import Fore, Style, init

sys.path.insert(0, '/workspaces/moltbot-test')

from modules.performance_auditor import PerformanceAuditor
from main import AlphaCore

init(autoreset=True)


def demo_scenario():
    """演示場景"""
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== PerformanceAuditor 演示場景 ===\n")
    
    auditor = PerformanceAuditor()
    alpha = AlphaCore()
    
    # ============================================================
    # 第一步：模擬過去的預測
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 1] 記錄模擬預測\n")
    
    # 創建 3 天前的預測（便於立即驗證）
    past_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    # 模擬預測 1：Chartist 和 Valuator 強烈看漲
    mock_analysts_1 = [
        {
            "analyst_name": "The Chartist (Technical)",
            "signal": "BUY",
            "confidence": 0.85,
            "reason": "黃金交叉信號"
        },
        {
            "analyst_name": "The Valuator (Fundamental)",
            "signal": "BUY",
            "confidence": 0.80,
            "reason": "P/E 低於平均"
        },
        {
            "analyst_name": "The Chip Watcher (Institutional)",
            "signal": "NEUTRAL",
            "confidence": 0.60,
            "reason": "籌碼無明顯信號"
        }
    ]
    
    pred_key_1 = auditor.record_prediction(
        ticker="2330.TW",
        analysts_report=mock_analysts_1,
        current_price=450.00,
        prediction_date=past_date
    )
    
    print(f"✓ 已記錄預測 1: {pred_key_1}")
    print(f"  預測日期: {past_date}")
    print(f"  入場價: 450.00 TWD")
    print(f"  共識: 3/3 看漲\n")
    
    # 模擬預測 2：Strategist 看空
    mock_analysts_2 = [
        {
            "analyst_name": "The Strategist (Macro)",
            "signal": "SELL",
            "confidence": 0.75,
            "reason": "升息環境不利"
        },
        {
            "analyst_name": "The Whale Hunter (Large Holders)",
            "signal": "SELL",
            "confidence": 0.70,
            "reason": "大戶減持"
        }
    ]
    
    pred_key_2 = auditor.record_prediction(
        ticker="3008.TW",
        analysts_report=mock_analysts_2,
        current_price=280.00,
        prediction_date=past_date
    )
    
    print(f"✓ 已記錄預測 2: {pred_key_2}")
    print(f"  預測日期: {past_date}")
    print(f"  入場價: 280.00 TWD")
    print(f"  共識: 2/2 看空\n")
    
    # ============================================================
    # 第二步：模擬實際股價 (手動模擬，實際使用 yfinance)
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 2] 注入模擬實際股價\n")
    
    # 編輯 performance_history 以模擬已驗證的結果
    # 情景 1：預測 1 表現良好（準確度高）
    auditor.performance_history["predictions"][pred_key_1]["actual_prices"]["T+1"] = 458.50  # +1.9%
    auditor.performance_history["predictions"][pred_key_1]["T+1_verified"] = True
    
    auditor.performance_history["predictions"][pred_key_1]["actual_prices"]["T+5"] = 465.75  # +3.5%
    auditor.performance_history["predictions"][pred_key_1]["T+5_verified"] = True
    
    # 情景 2：預測 2 完全失敗（方向反向）
    auditor.performance_history["predictions"][pred_key_2]["actual_prices"]["T+1"] = 288.50  # +3%（反向）
    auditor.performance_history["predictions"][pred_key_2]["T+1_verified"] = True
    
    print(f"✓ 預測 1 (2330.TW):")
    print(f"  T+1: 450.00 → 458.50 (+1.9%) ✓ 正確")
    print(f"  T+5: 450.00 → 465.75 (+3.5%) ✓ 正確\n")
    
    print(f"✓ 預測 2 (3008.TW):")
    print(f"  T+1: 280.00 → 288.50 (+3%) ✗ 反向（預期下跌）\n")
    
    # ============================================================
    # 第三步：手動驗證審計
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 3] 執行審計驗證\n")
    
    # 手動觸發審計邏輯（模擬 yfinance 結果）
    for pred_key, pred_data in auditor.performance_history["predictions"].items():
        for window in ["T+1", "T+5"]:
            if window in pred_data["actual_prices"] and pred_data.get(f"{window}_verified"):
                actual_price = pred_data["actual_prices"][window]
                accuracy = auditor._calculate_accuracy(
                    pred_data["entry_price"],
                    actual_price,
                    pred_data["analysts"]
                )
                
                attribution = auditor._perform_attribution_analysis(
                    pred_data["ticker"],
                    pred_data["analysts"],
                    accuracy,
                    window
                )
                
                audit_record = {
                    "timestamp": datetime.now().isoformat(),
                    "prediction_key": pred_key,
                    "window": window,
                    "entry_price": pred_data["entry_price"],
                    "actual_price": actual_price,
                    "accuracy": accuracy,
                    "attribution": attribution
                }
                
                auditor.performance_history["audits"].append(audit_record)
                
                symbol = "✓" if accuracy > 0.6 else "✗"
                print(f"{symbol} {pred_key} @ {window}: {accuracy*100:.1f}% 準確度 ({attribution['failure_type']})")
    
    auditor._save_performance_history()
    print()
    
    # ============================================================
    # 第四步：計算績效指標
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 4] 績效指標計算\n")
    
    perf_metrics = auditor.calculate_analyst_performance(lookback_days=30)
    
    print("分析師績效排行:")
    print("-" * 70)
    
    for analyst_name, metrics in sorted(
        perf_metrics.items(),
        key=lambda x: x[1]["overall_score"],
        reverse=True
    ):
        print(f"\n{analyst_name}")
        print(f"  準確度: {metrics['mean_accuracy']*100:>5.1f}%  " + 
              f"穩定性: {metrics['stability']*100:>5.1f}%  " +
              f"校準: {metrics['calibration']*100:>5.1f}%")
        print(f"  綜合評分: {metrics['overall_score']*100:.1f}% " +
              f"[{metrics['recommendation'].upper()}]  " +
              f"預測數: {metrics['prediction_count']}")
    
    print()
    
    # ============================================================
    # 第五步：動態權重調整
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 5] 動態權重調整\n")
    
    # 清除冷卻期以允許調整
    auditor.last_adjustment_time = datetime.now() - timedelta(days=10)
    
    old_weights = alpha.weights.copy()
    new_weights, was_adjusted = auditor.adjust_weights(old_weights)
    
    if was_adjusted:
        print(f"{Fore.GREEN}✓ 權重已調整！\n")
        
        print("權重對比:")
        print("-" * 70)
        print(f"{'分析師':<45} {'舊權重':>10} {'新權重':>10} {'變化':>10}")
        print("-" * 70)
        
        for name in sorted(old_weights.keys()):
            old_w = old_weights[name]
            new_w = new_weights[name]
            change = new_w - old_w
            change_pct = (change / old_w * 100) if old_w > 0 else 0
            
            print(f"{name:<45} {old_w:>9.1%} {new_w:>9.1%} {change_pct:>+9.2f}%")
        
        # 驗證總和 = 1.0
        total = sum(new_weights.values())
        print(f"\n總和驗證: {total:.4f}")
    else:
        print(f"{Fore.YELLOW}ℹ 權重暫無調整\n")
    
    # ============================================================
    # 第六步：識別明日之星
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 6] 明日之星識別\n")
    
    stars = auditor.get_star_candidates(top_n=3)
    
    if stars:
        print(f"{Fore.GREEN}發現 {len(stars)} 位明日之星：\n")
        for rank, (analyst_name, score) in enumerate(stars, 1):
            print(f"  {rank}. {analyst_name} (評分: {score*100:.1f}%)")
    else:
        print(f"{Fore.YELLOW}暫無符合標準的明日之星\n")
    
    # ============================================================
    # 第七步：完整報告
    # ============================================================
    print(f"{Fore.YELLOW}[步驟 7] 完整審計報告\n")
    print(auditor.generate_audit_report())
    
    print(f"{Fore.GREEN}✓ 演示場景完成！\n")


if __name__ == "__main__":
    demo_scenario()
