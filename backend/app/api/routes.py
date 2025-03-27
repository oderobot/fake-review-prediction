# backend/app/api/routes.py 通用路由
from flask import jsonify
from . import bp

@bp.route('/status', methods=['GET'])
def status():
    """API状态检查"""
    return jsonify({
        'status': 'online',
        'message': '虚假评论预测系统API正常运行'
    })