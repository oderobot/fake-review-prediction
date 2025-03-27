# backend/app/api/__init__.py
from flask import Blueprint

bp = Blueprint('api', __name__)

# 导入子蓝图
from backend.app.api.upload import upload_bp

# 注册子蓝图
bp.register_blueprint(upload_bp, url_prefix='/upload')

# 导入路由
from backend.app.api import routes