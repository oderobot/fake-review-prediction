from flask import Blueprint, request, jsonify
from backend.app.services.model_service import retrain_model, update_parameters, upload_data

model_bp = Blueprint('model', __name__, url_prefix='/api/model')


@model_bp.route('/retrain', methods=['POST'])
def retrain():
    """重新训练模型"""
    data = request.get_json()

    if not data or 'product_id' not in data:
        return jsonify({"error": "必须提供商品ID"}), 400

    product_id = data['product_id']
    parameters = data.get('parameters', {})

    result = retrain_model(product_id, parameters)
    return jsonify(result)


@model_bp.route('/parameters', methods=['POST'])
def parameters():
    """更新模型参数"""
    data = request.get_json()

    if not data or 'product_id' not in data or 'parameters' not in data:
        return jsonify({"error": "必须提供商品ID和参数"}), 400

    product_id = data['product_id']
    parameters = data['parameters']

    result = update_parameters(product_id, parameters)
    return jsonify(result)


@model_bp.route('/data', methods=['POST'])
def data():
    """上传新数据"""
    if 'file' not in request.files:
        return jsonify({"error": "没有上传文件"}), 400

    file = request.files['file']
    product_id = request.form.get('product_id')

    if not product_id:
        return jsonify({"error": "必须提供商品ID"}), 400

    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400

    result = upload_data(product_id, file)
    return jsonify(result)