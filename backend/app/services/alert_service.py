import pandas as pd
import numpy as np
from datetime import datetime
from backend.app.services.data_service import get_historical_data
from backend.app.services.prediction_service import get_predictions

# 模拟的存储阈值的字典，实际应用中应存储在数据库中
thresholds = {}


def _calculate_severity(value, threshold):
    """计算警报严重程度 (低、中、高)"""
    ratio = value / threshold
    if ratio < 1.2:
        return "低"
    elif ratio < 1.5:
        return "中"
    else:
        return "高"


def _calculate_risk_score(historical_ratio, predicted_ratio, slope, threshold):
    """计算风险评分 (0-100)"""
    # 历史异常比例权重 (30%)
    historical_score = min(historical_ratio * 100 * 2, 30)

    # 预测异常比例权重 (40%)
    predicted_score = min(predicted_ratio * 100 * 2, 40)

    # 趋势斜率权重 (30%)，正斜率表示趋势上升
    trend_factor = 0
    if slope > 0:
        # 斜率归一化，假设最大斜率为threshold的10%
        normalized_slope = min(slope / (threshold * 0.1), 1)
        trend_factor = normalized_slope * 30

    # 总分数
    total_score = historical_score + predicted_score + trend_factor

    return round(total_score, 1)


def _determine_risk_level(risk_score):
    """根据风险评分确定风险等级"""
    if risk_score < 20:
        return "安全"
    elif risk_score < 40:
        return "低风险"
    elif risk_score < 60:
        return "中风险"
    elif risk_score < 80:
        return "高风险"
    else:
        return "严重风险"


def get_alerts(product_id):
    """获取当前预警信息"""
    # 获取预测数据
    predictions = get_predictions(product_id)

    # 获取阈值，如果没有设置则使用默认值
    threshold = thresholds.get(product_id, {}).get('value', 0)

    if threshold == 0:
        # 如果没有设置阈值，使用历史数据平均值的150%作为默认阈值
        historical_data = get_historical_data(product_id)
        values = [point['value'] for point in historical_data['data']]
        threshold = int(np.mean(values) * 1.5)
        thresholds[product_id] = {'value': threshold, 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    # 检查哪些预测点超过阈值
    alerts = []
    for prediction in predictions['predictions']:
        if prediction['value'] > threshold:
            alerts.append({
                'timestamp': prediction['timestamp'],
                'predicted_value': prediction['value'],
                'threshold': threshold,
                'severity': _calculate_severity(prediction['value'], threshold)
            })

    result = {
        'product_id': product_id,
        'threshold': threshold,
        'alert_count': len(alerts),
        'alerts': alerts
    }

    return result


def set_threshold(product_id, threshold_value):
    """设置预警阈值"""
    thresholds[product_id] = {
        'value': threshold_value,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return {
        'product_id': product_id,
        'threshold': threshold_value,
        'status': 'success',
        'message': f'已成功更新商品ID {product_id} 的预警阈值为 {threshold_value}'
    }


def get_risk_assessment(product_id):
    """获取风险评估指标"""
    # 获取历史数据和预测
    historical_data = get_historical_data(product_id)
    predictions = get_predictions(product_id)

    # 获取阈值
    threshold = thresholds.get(product_id, {}).get('value', 0)
    if threshold == 0:
        values = [point['value'] for point in historical_data['data']]
        threshold = int(np.mean(values) * 1.5)

    # 计算历史异常比例
    historical_values = [point['value'] for point in historical_data['data']]
    historical_anomaly_ratio = sum(1 for v in historical_values if v > threshold) / len(historical_values)

    # 计算预测异常比例
    predicted_values = [point['value'] for point in predictions['predictions']]
    predicted_anomaly_ratio = sum(1 for v in predicted_values if v > threshold) / len(predicted_values)

    # 计算预测趋势斜率
    if len(predicted_values) > 1:
        slope = (predicted_values[-1] - predicted_values[0]) / len(predicted_values)
    else:
        slope = 0

    # 计算总体风险分数 (0-100)
    risk_score = _calculate_risk_score(historical_anomaly_ratio, predicted_anomaly_ratio, slope, threshold)

    # 确定风险等级
    risk_level = _determine_risk_level(risk_score)

    result = {
        'product_id': product_id,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'factors': {
            'historical_anomaly_ratio': round(historical_anomaly_ratio * 100, 2),
            'predicted_anomaly_ratio': round(predicted_anomaly_ratio * 100, 2),
            'trend_slope': round(slope, 2)
        },
        'threshold': threshold
    }

    return result