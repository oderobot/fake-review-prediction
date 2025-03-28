# backend/app/__init__.py

from flask import Flask
import os
import importlib
import pkgutil


def create_app():
    app = Flask(__name__)

    # 添加根路由
    @app.route('/')
    def home():
        return "Welcome to Fake Review Prediction API"

    # 注册其他蓝图
    with app.app_context():
        register_all_blueprints(app)

    return app


def register_all_blueprints(app):
    """自动发现并注册应用程序中的所有蓝图"""
    # 定义蓝图所在的包路径
    blueprint_packages = [
        'app.api',
        'app.api.upload'
        # 根据需要添加其他包路径
    ]

    for package_name in blueprint_packages:
        try:
            # 导入包
            package = importlib.import_module(package_name)

            # 获取包的路径
            package_path = os.path.dirname(package.__file__)

            # 扫描包中的所有模块
            for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
                # 只处理模块文件，跳过子包
                if not is_pkg and module_name != '__init__':  # 忽略 __init__.py
                    try:
                        # 导入模块
                        module = importlib.import_module(f"{package_name}.{module_name}")

                        # 在模块中寻找蓝图对象
                        for item_name in dir(module):
                            item = getattr(module, item_name)

                            # 检查对象是否是Flask蓝图，不使用hasattr检查，而是使用isinstance
                            if hasattr(item, '__class__') and item.__class__.__name__ == 'Blueprint':
                                # 注册找到的蓝图
                                app.register_blueprint(item)
                                print(f"已注册蓝图: {item.name}, 前缀: {item.url_prefix}")
                    except Exception as e:
                        print(f"注册模块 {module_name} 的蓝图时出错: {e}")
        except Exception as e:
            print(f"处理包 {package_name} 时出错: {e}")