import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.app.services.data_service import get_historical_data


def _parse_horizon(horizon):
    """解析预测时间范围"""
    if horizon.endswith('h'):
        hours = int(horizon[:-1])
        return hours
    elif horizon.endswith('d'):
        days = int(horizon[:-1])
        return days * 24
    else:
        # 默认24小时
        return 24


def get_predictions(product_id, horizon='24h', confidence_interval=0.95):
    """获取预测结果"""
    # 获取历史数据
    historical_data = get_historical_data(product_id)

    # 解析预测时间长度
    forecast_hours = _parse_horizon(horizon)

    # 获取最后一个时间点
    last_timestamp = datetime.strptime(historical_data['data'][-1]['timestamp'], '%Y-%m-%d %H:%M:%S')

    # 模拟Informer模型的预测结果
    # 在实际应用中，这里应该加载训练好的模型并进行预测

    # 生成预测时间点
    forecast_times = [last_timestamp + timedelta(hours=i + 1) for i in range(forecast_hours)]

    # 获取最近24个点的平均值和标准差，作为预测的基础
    recent_values = [point['value'] for point in historical_data['data'][-24:]]
    base_value = np.mean(recent_values)
    std_value = np.std(recent_values)

    # 模拟预测结果：基于最近的趋势加上一些随机性
    np.random.seed(hash(product_id) % 10000)

    # 基本趋势 - 随时间略微上升
    trend = np.linspace(0, 0.1 * base_value, forecast_hours)

    # 周期性变化
    periodicity = np.sin(np.arange(forecast_hours) % 24 * (np.pi / 12)) * 0.1 * base_value

    # 随机波动
    noise = np.random.normal(0, 0.05 * base_value, forecast_hours)

    # 合并所有成分
    predictions = base_value + trend + periodicity + noise
    predictions = np.maximum(predictions, 0)  # 确保非负

    # 计算置信区间
    z_score = 1.96  # 95%置信区间对应的z值
    confidence_range = z_score * std_value
    upper_bound = predictions + confidence_range
    lower_bound = np.maximum(predictions - confidence_range, 0)  # 确保下界非负

    # 构建结果
    result = {
        'product_id': product_id,
        'forecast_horizon': horizon,
        'confidence_interval': confidence_interval,
        'predictions': [{
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'value': int(round(pred)),
            'lower_bound': int(round(lb)),
            'upper_bound': int(round(ub))
        } for time, pred, lb, ub in zip(forecast_times, predictions, lower_bound, upper_bound)]
    }

    return result


def get_model_performance(product_id):
    """获取模型性能指标"""
    # 在实际应用中，这里应该从数据库或评估文件中读取真实的模型性能数据

    # 模拟的性能指标
    np.random.seed(hash(product_id) % 10000)

    mse = np.random.uniform(10, 50)
    rmse = np.sqrt(mse)
    mae = np.random.uniform(0.7, 0.9) * rmse
    mape = np.random.uniform(5, 15)

    # 模拟历史预测与实际对比数据
    # 实际实现时应该从数据库获取真实记录
    history_comparison = []
    for i in range(7):  # 过去7天的对比
        day = (datetime.now() - timedelta(days=i + 1)).strftime('%Y-%m-%d')
        error_pct = np.random.uniform(-10, 10)
        history_comparison.append({
            'date': day,
            'predicted': int(np.random.uniform(50, 150)),
            'actual': int(np.random.uniform(50, 150)),
            'error_percentage': round(error_pct, 2)
        })

    result = {
        'product_id': product_id,
        'metrics': {
            'mse': round(mse, 2),
            'rmse': round(rmse, 2),
            'mae': round(mae, 2),
            'mape': round(mape, 2)
        },
        'history_comparison': history_comparison
    }

    return result