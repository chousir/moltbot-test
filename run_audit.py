#!/usr/bin/env python3
"""
獨立審計工具 - 手動驗證預測、查看績效報告、調整權重

使用方式：
    python run_audit.py --verify        # 驗證已到期的預測
    python run_audit.py --report        # 顯示績效報告
    python run_audit.py --adjust        # 手動調整權重
    python run_audit.py --full          # 完整審計周期
    python run_audit.py --stars         # 顯示明日之星候選
"""

import sys
import argparse
import json
from colorama import Fore, Style, init
from datetime import datetime

# Add project to path
sys.path.insert(0, '/workspaces/moltbot-test')

from modules.performance_auditor import PerformanceAuditor
from main import AlphaCore

init(autoreset=True)


def format_weights_table(weights: dict) -> str:
    """格式化權重表格"""
    table = "\n{:<45} {:>12}\n".format("Analyst", "Weight")
    table += "-" * 60 + "\n"
    for name, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        weight_pct = f"{weight*100:.2f}%"
        table += "{:<45} {:>12}\n".format(name, weight_pct)
    return table


def main():
    parser = argparse.ArgumentParser(
        description="獨立審計工具 - PerformanceAuditor 命令行界面"
    )
    
    parser.add_argument("--verify", action="store_true", 
                       help="驗證已到期的預測")
    parser.add_argument("--report", action="store_true",
                       help="顯示績效報告")
    parser.add_argument("--adjust", action="store_true",
                       help="手動調整權重")
    parser.add_argument("--full", action="store_true",
                       help="完整審計周期（驗證+報告+調整）")
    parser.add_argument("--stars", action="store_true",
                       help="顯示明日之星候選")
    parser.add_argument("--history", action="store_true",
                       help="顯示績效歷史摘要")
    
    args = parser.parse_args()
    
    # 初始化審計員
    auditor = PerformanceAuditor()
    alpha = AlphaCore()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Performance Audit Console ===")
    print(f"{Fore.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 如果沒指定選項，默認顯示完整周期
    if not any([args.verify, args.report, args.adjust, args.full, args.stars, args.history]):
        args.full = True
    
    # 驗證預測
    if args.verify or args.full:
        print(f"{Fore.YELLOW}[Step 1] 驗證已到期的預測...\n")
        verified = auditor.verify_predictions()
        print(f"✓ 已驗證 {verified} 個預測\n")
    
    # 績效報告
    if args.report or args.full:
        print(f"{Fore.YELLOW}[Step 2] 績效報告\n")
        print(auditor.generate_audit_report())
    
    # 調整權重
    if args.adjust or args.full:
        print(f"{Fore.YELLOW}[Step 3] 權重調整\n")
        old_weights = alpha.weights.copy()
        new_weights, was_adjusted = auditor.adjust_weights(alpha.weights)
        
        if was_adjusted:
            print(f"{Fore.GREEN}✓ 權重已調整！\n")
            print("舊權重:")
            print(format_weights_table(old_weights))
            print("\n新權重:")
            print(format_weights_table(new_weights))
            
            # 計算變化百分比
            print("\n變化詳情:")
            print("-" * 60)
            for name in old_weights:
                old_w = old_weights[name]
                new_w = new_weights[name]
                change_pct = ((new_w - old_w) / old_w * 100) if old_w > 0 else 0
                direction = "↑" if change_pct > 0 else ("↓" if change_pct < 0 else "→")
                print(f"{direction} {name:<40} {change_pct:+.2f}%")
        else:
            print(f"{Fore.YELLOW}ℹ 權重暫無調整（冷卻期或數據不足）\n")
            print("當前權重:")
            print(format_weights_table(old_weights))
    
    # 明日之星
    if args.stars:
        print(f"{Fore.YELLOW}[Stars] 明日之星候選\n")
        candidates = auditor.get_star_candidates(top_n=3)
        
        if candidates:
            print(f"{Fore.GREEN}發現 {len(candidates)} 位明日之星：\n")
            for rank, (analyst_name, score) in enumerate(candidates, 1):
                print(f"{rank}. {analyst_name}")
                print(f"   綜合評分: {score*100:.1f}%\n")
        else:
            print(f"{Fore.YELLOW}尚無符合標準的明日之星候選\n")
    
    # 歷史摘要
    if args.history:
        print(f"{Fore.YELLOW}[History] 績效歷史摘要\n")
        history = auditor.performance_history
        
        print(f"總預測數: {len(history['predictions'])}")
        print(f"已審計數: {len(history['audits'])}")
        
        if history['audits']:
            # 計算平均準確度
            accuracies = [audit['accuracy'] for audit in history['audits']]
            avg_accuracy = sum(accuracies) / len(accuracies)
            print(f"平均準確度: {avg_accuracy*100:.1f}%")
            
            # 顯示最近 5 個審計結果
            print(f"\n最近 5 個審計結果:")
            print("-" * 70)
            for audit in history['audits'][-5:]:
                print(f"[{audit['timestamp'][:10]}] {audit['prediction_key']}")
                print(f"  Entry: {audit['entry_price']} → Actual: {audit['actual_price']}")
                print(f"  準確度: {audit['accuracy']*100:.1f}% | {audit['attribution']['failure_type']}")
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== 審計完成 ===\n")


if __name__ == "__main__":
    main()
