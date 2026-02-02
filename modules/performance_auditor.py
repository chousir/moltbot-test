"""
Performance Auditor & Dynamic Weighting Module
自我進化的績效審計系統 - 追蹤預測準確度並自動調整權重

核心功能：
1. 讀取歷史決策日誌，驗證過去預測
2. 當預測到期時（T+1, T+5, T+20），對比真實股價
3. 計算各分析師的績效指標
4. 根據績效自動調整權重（反饋循環）
5. 歸因分析：識別失敗類型，給予差異化懲罰
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yfinance as yf
from collections import defaultdict


class PerformanceAuditor:
    """
    績效審計員 - Alpha 系統的自我進化引擎
    """
    
    def __init__(self, 
                 logs_dir="/workspaces/moltbot-test/logs",
                 audit_dir="/workspaces/moltbot-test/data/audit",
                 performance_history_path="/workspaces/moltbot-test/data/audit/performance_history.json"):
        
        self.logs_dir = logs_dir
        self.audit_dir = audit_dir
        self.performance_history_path = performance_history_path
        
        os.makedirs(self.audit_dir, exist_ok=True)
        
        # 讀取或初始化績效歷史
        self.performance_history = self._load_performance_history()
        
        # 預測到期檢查的時間窗口定義
        self.prediction_windows = {
            "T+1": 1,    # 1 day
            "T+5": 5,    # 5 days
            "T+20": 20   # 20 days
        }
        
        # 權重調整參數
        self.weight_adjustment_params = {
            "excellent": 0.04,      # >80% 準確度：+4%
            "good": 0.02,           # 60-80%：+2%
            "normal": 0.0,          # 40-60%：維持
            "poor": -0.05,          # 20-40%：-5%
            "critical": -0.10,      # <20%：-10%
        }
        
        # 權重邊界（防止單一分析師過度主導或被邊緣化）
        self.weight_limits = {
            "The Valuator (Fundamental)": (0.20, 0.50),
            "The Chip Watcher (Institutional)": (0.10, 0.35),
            "The Whale Hunter (Large Holders)": (0.10, 0.35),
            "The Strategist (Macro)": (0.05, 0.25),
            "The Chartist (Technical)": (0.02, 0.20)
        }
        
        # 最後調整時間（冷卻期：3 天）
        self.last_adjustment_time = self._load_last_adjustment_time()
        self.cooldown_days = 3

    def _load_performance_history(self):
        """載入績效歷史紀錄"""
        if os.path.exists(self.performance_history_path):
            with open(self.performance_history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"predictions": {}, "audits": [], "analyst_stats": {}}

    def _save_performance_history(self):
        """保存績效歷史紀錄"""
        with open(self.performance_history_path, 'w', encoding='utf-8') as f:
            json.dump(self.performance_history, f, ensure_ascii=False, indent=2)

    def _load_last_adjustment_time(self):
        """載入上次權重調整的時間"""
        adjustment_log = os.path.join(self.audit_dir, "adjustment_log.json")
        if os.path.exists(adjustment_log):
            with open(adjustment_log, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get("last_adjustment", datetime.now().isoformat()))
        return datetime.now() - timedelta(days=10)  # 允許立即調整

    def _save_adjustment_time(self):
        """保存權重調整時間戳"""
        adjustment_log = os.path.join(self.audit_dir, "adjustment_log.json")
        with open(adjustment_log, 'w', encoding='utf-8') as f:
            json.dump({"last_adjustment": datetime.now().isoformat()}, f)

    def record_prediction(self, ticker: str, analysts_report: List[Dict], 
                         current_price: float, prediction_date: str = None):
        """
        記錄今天的預測 - 為未來的驗證做準備
        
        Args:
            ticker: 股票代碼
            analysts_report: 分析師報告列表
            current_price: 當前股價
            prediction_date: 預測日期 (ISO format, 預設為今天)
        """
        if prediction_date is None:
            prediction_date = datetime.now().strftime("%Y-%m-%d")
        
        prediction_key = f"{ticker}_{prediction_date}"
        
        self.performance_history["predictions"][prediction_key] = {
            "ticker": ticker,
            "prediction_date": prediction_date,
            "entry_price": current_price,
            "analysts": analysts_report,
            "recorded_at": datetime.now().isoformat(),
            "T+1_verified": False,
            "T+5_verified": False,
            "T+20_verified": False,
            "actual_prices": {}  # 將填入驗證數據
        }
        
        self._save_performance_history()
        return prediction_key

    def verify_predictions(self):
        """
        掃描所有已記錄的預測，檢查是否到期。
        如果到期（T+1, T+5, T+20），從 yfinance 獲取實際股價並計算準確度。
        """
        predictions = self.performance_history["predictions"]
        verified_count = 0
        
        print("\n[PerformanceAuditor] 開始驗證預測...")
        
        for pred_key, pred_data in list(predictions.items()):
            pred_date = datetime.fromisoformat(pred_data["prediction_date"])
            today = datetime.now()
            days_elapsed = (today - pred_date).days
            
            # 檢查各時間窗口
            for window_name, window_days in self.prediction_windows.items():
                verification_key = f"{window_name}_verified"
                
                # 如果還未驗證 且 時間已到
                if (not pred_data.get(verification_key, False) and 
                    days_elapsed >= window_days):
                    
                    ticker = pred_data["ticker"]
                    target_date = (pred_date + timedelta(days=window_days)).strftime("%Y-%m-%d")
                    
                    # 從 yfinance 獲取實際股價
                    actual_price = self._fetch_actual_price(ticker, target_date)
                    
                    if actual_price is not None:
                        # 計算準確度和歸因
                        accuracy = self._calculate_accuracy(
                            pred_data["entry_price"],
                            actual_price,
                            pred_data["analysts"]
                        )
                        
                        # 記錄實際價格和準確度
                        pred_data["actual_prices"][window_name] = actual_price
                        predictions[pred_key][verification_key] = True
                        
                        # 執行歸因分析
                        attribution = self._perform_attribution_analysis(
                            ticker, pred_data["analysts"], accuracy, window_name
                        )
                        
                        # 記錄審計結果
                        audit_record = {
                            "timestamp": datetime.now().isoformat(),
                            "prediction_key": pred_key,
                            "window": window_name,
                            "entry_price": pred_data["entry_price"],
                            "actual_price": actual_price,
                            "accuracy": accuracy,
                            "attribution": attribution
                        }
                        
                        self.performance_history["audits"].append(audit_record)
                        verified_count += 1
                        
                        print(f"   ✓ {ticker} @ {target_date}: 準確度 {accuracy*100:.1f}% | {attribution['failure_type']}")
        
        self._save_performance_history()
        return verified_count

    def _fetch_actual_price(self, ticker: str, target_date: str) -> float:
        """
        從 yfinance 獲取指定日期的收盤價
        
        Args:
            ticker: 股票代碼
            target_date: 目標日期 (YYYY-MM-DD)
        
        Returns:
            實際收盤價，若取不到則返回 None
        """
        try:
            # yfinance 需要台灣股票代碼格式 (e.g., 2330.TW)
            if not ticker.endswith(".TW") and not ticker.endswith(".TA"):
                ticker = f"{ticker}.TW"
            
            data = yf.download(ticker, start=target_date, end=target_date, 
                              progress=False, show_errors=False)
            
            if not data.empty:
                return round(float(data["Close"].iloc[0]), 2)
            return None
        except Exception as e:
            print(f"   ⚠ 無法獲取 {ticker} @ {target_date} 的價格: {e}")
            return None

    def _calculate_accuracy(self, entry_price: float, actual_price: float, 
                           analysts_report: List[Dict]) -> float:
        """
        計算預測準確度
        
        邏輯：
        - 預測方向正確 + 誤差 < 5% = 100% 準確度
        - 預測方向正確 + 誤差 5-15% = 70% 準確度
        - 預測方向正確 + 誤差 > 15% = 40% 準確度
        - 預測方向錯誤 = 0% 準確度
        """
        consensus_signal = self._get_consensus_signal(analysts_report)
        actual_return = (actual_price - entry_price) / entry_price
        
        # 判斷預測方向是否正確
        direction_correct = False
        if consensus_signal == "BUY" and actual_return > 0:
            direction_correct = True
        elif consensus_signal == "SELL" and actual_return < 0:
            direction_correct = True
        elif consensus_signal == "NEUTRAL":
            direction_correct = abs(actual_return) < 0.05  # ±5% 視為中立正確
        
        if not direction_correct:
            return 0.0
        
        # 計算誤差
        error = abs(actual_return)
        
        if error < 0.05:
            return 1.0  # 100%
        elif error < 0.15:
            return 0.7  # 70%
        else:
            return 0.4  # 40%

    def _get_consensus_signal(self, analysts_report: List[Dict]) -> str:
        """根據分析師報告推導共識信號"""
        buy_count = sum(1 for r in analysts_report if r.get("signal") == "BUY")
        sell_count = sum(1 for r in analysts_report if r.get("signal") == "SELL")
        
        if buy_count > sell_count:
            return "BUY"
        elif sell_count > buy_count:
            return "SELL"
        else:
            return "NEUTRAL"

    def _perform_attribution_analysis(self, ticker: str, analysts_report: List[Dict],
                                     accuracy: float, window: str) -> Dict:
        """
        執行歸因分析 - 確定失敗的根源類別
        
        Returns:
            {
                "failure_type": "technical" | "fundamental" | "institutional" | "macro" | "normal",
                "analyst_responsible": str,
                "recommendation": str
            }
        """
        
        if accuracy > 0.7:  # 準確度高，視為正常表現
            return {
                "failure_type": "normal",
                "analyst_responsible": None,
                "recommendation": "所有分析師表現良好"
            }
        
        # 根據分析師類型和市場表現判斷
        failure_analysis = defaultdict(list)
        
        for analyst in analysts_report:
            analyst_name = analyst.get("analyst_name", "Unknown")
            
            if "Chartist" in analyst_name:
                failure_analysis["technical"].append(analyst_name)
            elif "Valuator" in analyst_name:
                failure_analysis["fundamental"].append(analyst_name)
            elif "Chip Watcher" in analyst_name or "Whale Hunter" in analyst_name:
                failure_analysis["institutional"].append(analyst_name)
            elif "Strategist" in analyst_name:
                failure_analysis["macro"].append(analyst_name)
        
        # 判斷最可能的失敗類型（簡化邏輯，可擴展）
        if accuracy == 0.0:  # 方向完全錯誤
            # 傾向於認為技術面分析失敗最常見
            primary_failure = "technical"
        else:
            # 幅度預估錯誤，可能是基本面或籌碼面
            primary_failure = "fundamental"
        
        return {
            "failure_type": primary_failure,
            "analyst_responsible": failure_analysis.get(primary_failure, [None])[0],
            "recommendation": self._generate_penalty_recommendation(primary_failure, accuracy)
        }

    def _generate_penalty_recommendation(self, failure_type: str, accuracy: float) -> str:
        """根據失敗類型生成懲罰建議"""
        recommendations = {
            "technical": "Chartist 需要重新審視技術指標的有效性",
            "fundamental": "Valuator 需要加強盈利預測模型",
            "institutional": "ChipWatcher/WhaleHunter 需要更新籌碼面數據源",
            "macro": "Strategist 需要改進宏觀因素權衡"
        }
        return recommendations.get(failure_type, "通用建議：重新評估分析方法")

    def calculate_analyst_performance(self, lookback_days: int = 7) -> Dict[str, Dict]:
        """
        計算每位分析師最近 N 天的績效指標
        
        Returns:
            {
                "analyst_name": {
                    "accuracy": float (0-1),
                    "prediction_count": int,
                    "stability_score": float,
                    "recommendation": "excellent|good|normal|poor|critical"
                }
            }
        """
        audits = self.performance_history["audits"]
        analyst_stats = defaultdict(lambda: {
            "accuracies": [],
            "confidence_scores": [],
            "predictions": 0
        })
        
        # 篩選 lookback_days 內的審計紀錄
        cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
        
        for audit in audits:
            if audit["timestamp"] >= cutoff_date:
                accuracy = audit["accuracy"]
                pred_key = audit["prediction_key"]
                
                # 從 performance_history 中取得分析師詳情
                if pred_key in self.performance_history["predictions"]:
                    prediction = self.performance_history["predictions"][pred_key]
                    
                    for analyst in prediction["analysts"]:
                        analyst_name = analyst.get("analyst_name", "Unknown")
                        analyst_stats[analyst_name]["accuracies"].append(accuracy)
                        analyst_stats[analyst_name]["confidence_scores"].append(
                            analyst.get("confidence", 0.5)
                        )
                        analyst_stats[analyst_name]["predictions"] += 1
        
        # 計算指標
        performance_summary = {}
        for analyst_name, stats in analyst_stats.items():
            if stats["predictions"] == 0:
                continue
            
            mean_accuracy = np.mean(stats["accuracies"])
            std_accuracy = np.std(stats["accuracies"]) if len(stats["accuracies"]) > 1 else 0
            
            # 穩定性評分：標準差越低越穩定
            stability_score = 1.0 - (std_accuracy / 2.0)  # 標準化到 0-1
            stability_score = max(0.0, min(1.0, stability_score))
            
            # 信心校準（Brier Score）
            # 理想情況：信心 = 準確度
            if stats["confidence_scores"]:
                brier_score = np.mean([(c - a) ** 2 for c, a in 
                                      zip(stats["confidence_scores"], stats["accuracies"])])
                calibration = 1.0 - brier_score  # 越接近 1 越好
            else:
                calibration = 0.5
            
            # 綜合評分
            overall_accuracy = (mean_accuracy * 0.5 + stability_score * 0.3 + 
                               calibration * 0.2)
            
            # 根據準確度判定等級
            if overall_accuracy > 0.80:
                recommendation = "excellent"
            elif overall_accuracy > 0.60:
                recommendation = "good"
            elif overall_accuracy > 0.40:
                recommendation = "normal"
            elif overall_accuracy > 0.20:
                recommendation = "poor"
            else:
                recommendation = "critical"
            
            performance_summary[analyst_name] = {
                "mean_accuracy": round(mean_accuracy, 3),
                "stability": round(stability_score, 3),
                "calibration": round(calibration, 3),
                "overall_score": round(overall_accuracy, 3),
                "prediction_count": stats["predictions"],
                "recommendation": recommendation,
                "std_dev": round(std_accuracy, 3)
            }
        
        return performance_summary

    def adjust_weights(self, current_weights: Dict[str, float]) -> Tuple[Dict[str, float], bool]:
        """
        根據績效計算新的權重
        
        Args:
            current_weights: 當前的權重字典
        
        Returns:
            (adjusted_weights, was_adjusted)
        """
        # 檢查冷卻期
        if (datetime.now() - self.last_adjustment_time).days < self.cooldown_days:
            return current_weights, False
        
        # 計算性能指標
        perf_metrics = self.calculate_analyst_performance(lookback_days=7)
        
        if not perf_metrics:
            print("[PerformanceAuditor] 沒有足夠的績效數據進行調整")
            return current_weights, False
        
        # 根據推薦等級調整權重
        adjustment_multiplier = {}
        for analyst_name, current_weight in current_weights.items():
            if analyst_name not in perf_metrics:
                adjustment_multiplier[analyst_name] = 1.0
                continue
            
            recommendation = perf_metrics[analyst_name]["recommendation"]
            adjustment = self.weight_adjustment_params.get(recommendation, 0.0)
            
            # 計算新權重
            new_weight = current_weight * (1 + adjustment)
            
            # 應用邊界限制
            if analyst_name in self.weight_limits:
                min_w, max_w = self.weight_limits[analyst_name]
                new_weight = max(min_w, min(max_w, new_weight))
            
            adjustment_multiplier[analyst_name] = new_weight / current_weight if current_weight > 0 else 1.0
        
        # 正規化以確保總和 = 1.0
        adjusted_weights = {}
        total = 0
        
        for analyst_name, current_weight in current_weights.items():
            new_weight = current_weight * adjustment_multiplier.get(analyst_name, 1.0)
            adjusted_weights[analyst_name] = new_weight
            total += new_weight
        
        # 正規化
        if total > 0:
            adjusted_weights = {k: v / total for k, v in adjusted_weights.items()}
        
        # 檢查是否有實質改變
        was_adjusted = any(
            abs(adjusted_weights.get(k, 0) - current_weights.get(k, 0)) > 0.01
            for k in current_weights
        )
        
        if was_adjusted:
            self.last_adjustment_time = datetime.now()
            self._save_adjustment_time()
            
            # 記錄調整
            adjustment_record = {
                "timestamp": datetime.now().isoformat(),
                "old_weights": current_weights,
                "new_weights": adjusted_weights,
                "performance_metrics": perf_metrics
            }
            
            adjustment_log_file = os.path.join(self.audit_dir, "weight_adjustments.jsonl")
            with open(adjustment_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(adjustment_record, ensure_ascii=False) + "\n")
        
        return adjusted_weights, was_adjusted

    def generate_audit_report(self) -> str:
        """生成格式化的審計報告"""
        perf_metrics = self.calculate_analyst_performance()
        
        report = "\n" + "="*70 + "\n"
        report += "[PERFORMANCE AUDIT REPORT]\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "="*70 + "\n\n"
        
        report += "Analyst Performance (7-day rolling):\n"
        report += "-" * 70 + "\n"
        
        for analyst_name, metrics in sorted(perf_metrics.items()):
            report += f"\n{analyst_name}\n"
            report += f"  • 平均準確度: {metrics['mean_accuracy']*100:.1f}%\n"
            report += f"  • 穩定性: {metrics['stability']*100:.1f}%\n"
            report += f"  • 信心校準: {metrics['calibration']*100:.1f}%\n"
            report += f"  • 綜合評分: {metrics['overall_score']*100:.1f}%\n"
            report += f"  • 預測數: {metrics['prediction_count']}\n"
            report += f"  • 評級: {metrics['recommendation'].upper()}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report

    def get_star_candidates(self, top_n: int = 2) -> List[Tuple[str, float]]:
        """
        識別「明日之星」- 最有潛力的分析師
        
        篩選標準：
        1. 綜合評分 > 70%
        2. 穩定性 > 60%
        3. 信心校準 > 70%
        4. 預測數 >= 3
        """
        perf_metrics = self.calculate_analyst_performance()
        
        candidates = []
        for analyst_name, metrics in perf_metrics.items():
            if (metrics["overall_score"] > 0.70 and
                metrics["stability"] > 0.60 and
                metrics["calibration"] > 0.70 and
                metrics["prediction_count"] >= 3):
                
                candidates.append((analyst_name, metrics["overall_score"]))
        
        # 排序並返回 top N
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_n]
