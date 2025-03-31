# backend/app/api/informer/routes.py
import sys

import torch
from flask import Blueprint, request, jsonify, current_app
import os
import json
import logging
from backend.app.services.informer_adapter import InformerAdapter
from backend.app.services.preprocess_service import PreprocessService

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
informer_bp = Blueprint('informer', __name__, url_prefix='/api/informer')


@informer_bp.route('/predict', methods=['POST'])
def predict():
    """使用Informer模型进行预测

    请求数据格式:
    {
        "data_path": "/path/to/preprocessed/data.csv",
        "forecast_days": 7,
        "problem_type": "fake_review"
    }
    """
    try:
        logger.info("接收到预测请求")
        data = request.json

        # 验证请求数据
        if not data:
            logger.error("请求数据为空")
            return jsonify({
                'status': 'error',
                'message': '请求数据为空'
            }), 400

        if 'data_path' not in data:
            logger.error("缺少数据文件路径参数")
            return jsonify({
                'status': 'error',
                'message': '缺少数据文件路径参数'
            }), 400

        data_path = data['data_path']

        # 检查文件是否存在
        if not os.path.exists(data_path):
            logger.error(f"数据文件不存在: {data_path}")
            return jsonify({
                'status': 'error',
                'message': '数据文件不存在'
            }), 400

        # 获取可选参数
        forecast_days = int(data.get('forecast_days', 7))
        problem_type = data.get('problem_type', 'fake_review')

        logger.info(f"调用Informer适配器，数据路径: {data_path}，预测天数: {forecast_days}，问题类型: {problem_type}")

        # 调用Informer适配器
        result = InformerAdapter.predict(data_path, forecast_days, problem_type)

        if result.get('status') == 'error':
            logger.error(f"预测失败: {result.get('message')}")
            return jsonify(result), 400

        logger.info("预测成功")
        return jsonify(result)

    except Exception as e:
        logger.exception("预测接口异常")
        return jsonify({
            'status': 'error',
            'message': f'预测接口异常: {str(e)}'
        }), 500


@informer_bp.route('/process-and-predict', methods=['POST'])
def process_and_predict():
    """一步完成数据预处理和预测

    请求数据格式:
    {
        "file_path": "/path/to/original/file.csv",
        "output_dir": "/optional/output/directory",
        "prod_id": "可选的产品ID",
        "forecast_days": 7,
        "problem_type": "fake_review"
    }
    """
    try:
        logger.info("接收到预处理和预测请求")
        data = request.json

        # 验证请求数据
        if not data:
            logger.error("请求数据为空")
            return jsonify({
                'status': 'error',
                'message': '请求数据为空'
            }), 400

        if 'file_path' not in data:
            logger.error("缺少文件路径参数")
            return jsonify({
                'status': 'error',
                'message': '缺少文件路径参数'
            }), 400

        file_path = data['file_path']

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return jsonify({
                'status': 'error',
                'message': '文件不存在'
            }), 400

        # 获取可选参数
        output_dir = data.get('output_dir')
        prod_id = data.get('prod_id')
        forecast_days = int(data.get('forecast_days', 7))
        problem_type = data.get('problem_type', 'fake_review')

        logger.info(f"开始数据预处理，文件路径: {file_path}")

        # 第一步：预处理数据
        preprocess_result = PreprocessService.preprocess_for_informer(file_path, output_dir, prod_id)

        if preprocess_result.get('status') == 'error':
            logger.error(f"预处理失败: {preprocess_result.get('message')}")
            return jsonify(preprocess_result), 400

        logger.info("预处理成功，开始执行预测")

        # 收集所有产品的预测结果
        predictions = []

        # 第二步：对每个预处理后的文件进行预测
        for processed_file in preprocess_result['processed_files']:
            logger.info(f"预测产品: {processed_file['product_id']}")

            # 调用Informer适配器
            prediction_result = InformerAdapter.predict(
                processed_file['file_path'],
                forecast_days,
                problem_type
            )

            if prediction_result.get('status') == 'error':
                logger.warning(f"产品 {processed_file['product_id']} 预测失败: {prediction_result.get('message')}")
                prediction_result['product_id'] = processed_file['product_id']
                predictions.append(prediction_result)
            else:
                logger.info(f"产品 {processed_file['product_id']} 预测成功")
                predictions.append(prediction_result)

        # 计算成功和失败的预测数量
        successful_predictions = sum(1 for p in predictions if p.get('status') == 'success')
        failed_predictions = sum(1 for p in predictions if p.get('status') == 'error')

        logger.info(f"完成所有预测，成功: {successful_predictions}，失败: {failed_predictions}")

        # 返回所有预测结果
        return jsonify({
            'status': 'success',
            'problem_type': problem_type,
            'predictions': predictions,
            'summary': {
                'total_products': len(preprocess_result['processed_files']),
                'successful_predictions': successful_predictions,
                'failed_predictions': failed_predictions,
                'original_file': file_path
            }
        })

    except Exception as e:
        logger.exception("预处理和预测接口异常")
        return jsonify({
            'status': 'error',
            'message': f'预处理和预测接口异常: {str(e)}'
        }), 500


@informer_bp.route('/status', methods=['GET'])
def status():
    """检查Informer服务状态"""
    try:
        informer_path = InformerAdapter.INFORMER_PATH

        # 检查Informer项目路径是否存在
        path_exists = os.path.exists(informer_path)

        # 检查main_informer.py是否存在
        main_script = os.path.join(informer_path, 'main_informer.py')
        script_exists = os.path.exists(main_script)

        return jsonify({
            'status': 'success',
            'informer_path': informer_path,
            'path_exists': path_exists,
            'script_exists': script_exists,
            'environment': {
                'python_version': sys.version,
                'torch_available': 'Yes' if torch.__version__ else 'No',
                'cuda_available': 'Yes' if torch.cuda.is_available() else 'No'
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务状态检查失败: {str(e)}'
        }), 500