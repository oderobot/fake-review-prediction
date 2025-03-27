import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# 模拟数据函数，实际项目中应从数据库获取
def _generate_mock_data(product_id, start_date, end_date):
    """生成模拟的历史数据"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    date_range = pd.date_range(start=start, end=end, freq='H')

    # 基于商品ID生成不同的模拟数据
    seed = hash(product_id) % 10000
    np.random.seed(seed)

    # 生成基本趋势
    base = 10 + np.sin(np.arange(len(date_range)) * 0.1) * 5

    # 添加随机波动
    noise = np.random.normal(0, 1, size=len(date_range))

    # 添加周期性模式
    hourly_pattern = np.sin(np.arange(len(date_range)) % 24 * (np.pi / 12)) * 3

    # 添加一些异常点
    anomalies = np.zeros(len(date_range))
    anomaly_indices = np.random.choice(len(date_range), size=int(len(date_range) * 0.05), replace=False)
    anomalies[anomaly_indices] = np.random.uniform(10, 20, size=len(anomaly_indices))

    # 组合所有成分
    values = base + noise + hourly_pattern + anomalies
    values = np.maximum(values, 0)  # 确保数值为非负

    df = pd.DataFrame({
        'timestamp': date_range,
        'fake_reviews': np.round(values).astype(int)
    })

    return df


def get_historical_data(product_id, start_date=None, end_date=None):
    """获取历史虚假评论数据"""
    df = _generate_mock_data(product_id, start_date, end_date)

    result = {
        'product_id': product_id,
        'data': [{
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'value': int(row['fake_reviews'])
        } for _, row in df.iterrows()]
    }

    return result


def get_statistics(product_id, start_date=None, end_date=None):
    """获取统计数据"""
    df = _generate_mock_data(product_id, start_date, end_date)

    stats = {
        'product_id': product_id,
        'mean': float(df['fake_reviews'].mean()),
        'median': float(df['fake_reviews'].median()),
        'max': int(df['fake_reviews'].max()),
        'min': int(df['fake_reviews'].min()),
        'total': int(df['fake_reviews'].sum()),
        'std_dev': float(df['fake_reviews'].std()),
        'count': int(len(df)),
        'start_date': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
        'end_date': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
    }

    return stats


def get_anomalies(product_id, start_date=None, end_date=None):
    """识别并返回异常点"""
    df = _generate_mock_data(product_id, start_date, end_date)

    # 简单的异常检测 - 使用3倍标准差作为阈值
    mean = df['fake_reviews'].mean()
    std = df['fake_reviews'].std()
    threshold = 3 * std

    # 找出异常值
    anomalies = df[abs(df['fake_reviews'] - mean) > threshold]

    result = {
        'product_id': product_id,
        'anomalies': [{
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'value': int(row['fake_reviews']),
            'deviation': float(abs(row['fake_reviews'] - mean) / std)
        } for _, row in anomalies.iterrows()]
    }

    return result