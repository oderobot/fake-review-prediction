from flask import Blueprint, request, jsonify
from backend.app.services.alert_service import get_alerts, set_threshold, get_risk_assessment

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@alerts_bp.route('/', methods=['GET'])
def alerts():
    """获取当前预警信息"""
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    alert_data = get_alerts(product_id)
    return jsonify(alert_data)


@alerts_bp.route('/threshold', methods=['POST'])
def threshold():
    """设置预警阈值"""
    data = request.get_json()

    if not data or 'product_id' not in data or 'threshold' not in data:
        return jsonify({"error": "必须提供商品ID和阈值"}), 400

    product_id = data['product_id']
    threshold_value = data['threshold']

    result = set_threshold(product_id, threshold_value)
    return jsonify(result)


@alerts_bp.route('/risk', methods=['GET'])
def risk():
    """获取风险评估指标"""
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    risk_data = get_risk_assessment(product_id)
    return jsonify(risk_data)