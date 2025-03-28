# backend/app/api/preprocess/routes.py
from flask import Blueprint, request, jsonify
import os
from backend.app.services.preprocess_service import PreprocessService

# 创建蓝图
preprocess_bp = Blueprint('preprocess', __name__, url_prefix='/api/preprocess')


@preprocess_bp.route('/informer', methods=['POST'])
def preprocess_for_informer():
    """处理数据并转换为Informer模型可用的格式"""
    # 获取请求数据
    data = request.json

    # 验证必要参数
    if not data or 'file_path' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少文件路径参数'
        }), 400

    file_path = data['file_path']

    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': '文件不存在'
        }), 400

    # 获取可选参数
    output_dir = data.get('output_dir')
    prod_id = data.get('prod_id')

    # 调用预处理服务
    result = PreprocessService.preprocess_for_informer(file_path, output_dir, prod_id)

    if result.get('status') == 'error':
        return jsonify(result), 400

    return jsonify(result)