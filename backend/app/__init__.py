from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


def create_app(test_config=None):
    # 创建并配置应用
    app = Flask(__name__, instance_relative_config=True)

    # 设置CORS
    CORS(app)

    # 加载配置
    if test_config is None:
        # 如果不是测试，则加载实例配置（如果存在）
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 如果传入测试配置，则加载测试配置
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 确保服务目录存在
    try:
        from app.services import data_service, prediction_service, alert_service, model_service
        logger.info("已成功导入服务模块")
    except ImportError as e:
        logger.error(f"导入服务模块时出错: {e}")
        # 创建必要的目录和文件
        os.makedirs('app/services', exist_ok=True)
        # 注意：这里不会实际创建文件，只是记录错误

    # 确保API目录存在
    try:
        os.makedirs('app/api', exist_ok=True)
    except OSError:
        pass

    # 注册蓝图（使用try-except处理可能的导入错误）
    try:
        from app.api.data import data_bp
        from app.api.predictions import predictions_bp
        from app.api.alerts import alerts_bp
        from app.api.model import model_bp

        app.register_blueprint(data_bp)
        app.register_blueprint(predictions_bp)
        app.register_blueprint(alerts_bp)
        app.register_blueprint(model_bp)
        logger.info("已成功注册所有蓝图")
    except ImportError as e:
        logger.error(f"注册蓝图时出错: {e}")

    # 添加简单路由
    @app.route('/')
    def index():
        return {'message': '虚假评论预测系统API服务正在运行'}

    return app