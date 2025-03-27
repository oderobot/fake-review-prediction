from flask import Blueprint, request, jsonify
from backend.app.services.data_service import get_historical_data, get_statistics, get_anomalies

data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('/historical', methods=['GET'])
def historical_data():
    """获取历史虚假评论数据"""
    product_id = request.args.get('product_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    data = get_historical_data(product_id, start_date, end_date)
    return jsonify(data)


@data_bp.route('/statistics', methods=['GET'])
def statistics():
    """获取统计数据（均值、最大值、总数等）"""
    product_id = request.args.get('product_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    stats = get_statistics(product_id, start_date, end_date)
    return jsonify(stats)


@data_bp.route('/anomalies', methods=['GET'])
def anomalies():
    """获取异常点数据"""
    product_id = request.args.get('product_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    anomaly_data = get_anomalies(product_id, start_date, end_date)
    return jsonify(anomaly_data)


@data_bp.route('/products', methods=['GET'])
def products():
    """获取所有可用的商品列表"""
    # 这里将来需要从数据库中获取商品列表
    # 暂时返回模拟数据
    product_list = [
        {"id": "prod001", "name": "智能手机A"},
        {"id": "prod002", "name": "笔记本电脑B"},
        {"id": "prod003", "name": "耳机C"}
    ]
    return jsonify(product_list)