from flask import Blueprint, request, jsonify
from backend.app.services.prediction_service import get_predictions, get_model_performance

predictions_bp = Blueprint('predictions', __name__, url_prefix='/api/predictions')


@predictions_bp.route('/', methods=['GET'])
def get_prediction():
    """获取虚假评论预测数据"""
    product_id = request.args.get('product_id')
    horizon = request.args.get('horizon', default='24h')  # 默认预测24小时
    confidence_interval = request.args.get('confidence_interval', default='0.95')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    prediction_data = get_predictions(product_id, horizon, float(confidence_interval))
    return jsonify(prediction_data)


@predictions_bp.route('/performance', methods=['GET'])
def performance():
    """获取模型性能评估数据"""
    product_id = request.args.get('product_id')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    performance_data = get_model_performance(product_id)
    return jsonify(performance_data)


@predictions_bp.route('/compare', methods=['GET'])
def compare_predictions():
    """比较多个商品的预测结果"""
    product_ids = request.args.getlist('product_ids')
    horizon = request.args.get('horizon', default='24h')

    if not product_ids:
        return jsonify({"error": "必须提供至少一个商品ID"}), 400

    result = {}
    for product_id in product_ids:
        result[product_id] = get_predictions(product_id, horizon)

    return jsonify(result)