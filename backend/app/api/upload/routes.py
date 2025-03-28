# backend/app/api/upload/routes.py
import os
from flask import current_app, request, jsonify, Blueprint
from backend.app.services.upload_service import UploadService

# 创建蓝图
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')
@upload_bp.route('/', methods=['POST'])
def upload_file():
    """处理文件上传请求"""
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有上传文件'}), 400

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '未选择文件'}), 400

    # 检查文件类型是否允许
    if not UploadService.validate_file_type(file.filename):
        return jsonify({
            'status': 'error',
            'message': '不支持的文件类型，允许的类型：csv, xlsx, xls'
        }), 400

    try:
        # 保存文件
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'tmp', 'uploads')
        # 在 routes.py 中调用时
        file_info = UploadService.save_file(file)  # 不传 upload_dir，自动使用配置的路径
        # 返回上传成功的响应
        return jsonify({
            'status': 'success',
            'message': '文件上传成功',
            'file': file_info
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'文件上传失败: {str(e)}'
        }), 500


@upload_bp.route('/validate', methods=['POST'])
def validate_file():
    """验证上传的文件格式"""
    data = request.json
    file_path = data.get('file_path') or data.get('filepath')  # 兼容两种字段名

    if not file_path or not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': '文件不存在'
        }), 400

    # 验证文件内容
    validation_result = UploadService.validate_file_content(file_path)

    if not validation_result.get('valid', False):
        return jsonify({
            'status': 'error',
            'message': validation_result.get('message', '文件验证失败')
        }), 400

    return jsonify({
        'status': 'success',
        'message': '文件格式验证通过',
        'file_info': validation_result
    })