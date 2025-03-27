# backend/app/__init__.py
import os
from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # 确保临时文件夹存在
    tmp_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'tmp')
    uploads_folder = os.path.join(tmp_folder, 'uploads')
    processed_folder = os.path.join(tmp_folder, 'processed')

    os.makedirs(uploads_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)

    # 注册API蓝图
    from backend.app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app