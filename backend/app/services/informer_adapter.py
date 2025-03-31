# backend/app/services/informer_adapter.py
import os
import sys
import json
import subprocess
import torch
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InformerAdapter:
    """Informer模型适配器，用于连接Flask应用和Informer项目"""

    # 从环境变量获取Informer项目路径，如果没有设置，则使用默认路径
    INFORMER_PATH = os.environ.get('INFORMER_PROJECT_PATH', '/path/to/your/informer/project')

    @staticmethod
    def predict(data_path, forecast_days=7, problem_type="fake_review"):
        """调用Informer模型进行预测

        Args:
            data_path: 预处理数据文件路径
            forecast_days: 预测天数
            problem_type: 预测问题类型，默认fake_review

        Returns:
            dict: 预测结果
        """
        try:
            logger.info(f"开始执行Informer预测，数据路径：{data_path}，预测天数：{forecast_days}，问题类型：{problem_type}")

            # 检查文件是否存在
            if not os.path.exists(data_path):
                logger.error(f"数据文件不存在：{data_path}")
                return {'status': 'error', 'message': '数据文件不存在'}

            # 检查Informer项目路径是否存在
            if not os.path.exists(InformerAdapter.INFORMER_PATH):
                logger.error(f"Informer项目路径不存在：{InformerAdapter.INFORMER_PATH}")
                return {'status': 'error', 'message': f'Informer项目路径不存在：{InformerAdapter.INFORMER_PATH}'}

            # 构建问题类型特定的参数配置
            problem_configs = {
                "fake_review": {
                    "features": "MS",
                    "target": "fake",
                    "enc_in": 2,
                    "dec_in": 2,
                    "c_out": 1
                },
                "sales_forecast": {
                    "features": "MS",
                    "target": "sales",
                    "enc_in": 3,
                    "dec_in": 3,
                    "c_out": 1
                }
                # 可以添加更多预测问题类型
            }

            # 获取问题特定的配置
            if problem_type not in problem_configs:
                logger.warning(f"未知的问题类型：{problem_type}，使用默认fake_review配置")
                problem_type = "fake_review"

            config = problem_configs[problem_type]

            # 准备命令行参数
            main_script = os.path.join(InformerAdapter.INFORMER_PATH, 'main_informer.py')
            if not os.path.exists(main_script):
                logger.error(f"Informer主脚本不存在：{main_script}")
                return {'status': 'error', 'message': f'Informer主脚本不存在：{main_script}'}

            data_dir = os.path.dirname(data_path)
            data_filename = os.path.basename(data_path)

            cmd = [
                'python', main_script,
                '--model', 'informer',
                '--data', 'custom',
                '--root_path', data_dir,
                '--data_path', data_filename,
                '--features', config["features"],
                '--target', config["target"],
                '--enc_in', str(config["enc_in"]),
                '--dec_in', str(config["dec_in"]),
                '--c_out', str(config["c_out"]),
                '--pred_len', str(forecast_days),
                '--do_predict'
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")

            # 执行Informer命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=InformerAdapter.INFORMER_PATH
            )
            stdout, stderr = process.communicate()

            # 检查命令执行结果
            if process.returncode != 0:
                error_msg = stderr.decode("utf-8")
                logger.error(f"Informer预测失败: {error_msg}")
                return {
                    'status': 'error',
                    'message': f'Informer预测失败',
                    'details': error_msg
                }

            # 获取命令输出
            try:
                # 首先尝试UTF-8编码
                output = stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 如果UTF-8失败，尝试系统默认编码(中文Windows通常是GBK或GB2312)
                    output = stdout.decode('gbk')
                except UnicodeDecodeError:
                    # 如果还是失败，使用错误处理选项
                    output = stdout.decode('utf-8', errors='replace')
                    logger.warning("命令输出解码时出现非UTF-8字符，已替换为占位符")

            logger.info(f"Informer执行成功，开始查找预测结果")

            # 查找预测结果文件
            result_dir = os.path.join(InformerAdapter.INFORMER_PATH, 'results')
            latest_result = None
            latest_time = 0

            for root, dirs, files in os.walk(result_dir):
                for file in files:
                    if file == 'real_prediction.npy':
                        file_path = os.path.join(root, file)
                        file_time = os.path.getmtime(file_path)
                        if file_time > latest_time:
                            latest_result = file_path
                            latest_time = file_time

            if not latest_result:
                logger.error("未找到预测结果文件")
                return {
                    'status': 'error',
                    'message': '未找到预测结果文件'
                }

            logger.info(f"找到预测结果文件: {latest_result}")

            # 读取预测结果
            predictions = np.load(latest_result)
            logger.info(f"预测结果形状: {predictions.shape}")

            # 确保预测值非负
            predictions = np.maximum(predictions, 0)

            # 读取原始数据以获取日期
            df = pd.read_csv(data_path)
            df['date'] = pd.to_datetime(df['date'])

            # 生成预测日期
            last_date = df['date'].iloc[-1]
            pred_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
            pred_dates_str = [date.strftime('%Y-%m-%d') for date in pred_dates]

            # 创建预测结果
            target_name = config["target"]
            result_data = []

            # 处理预测结果形状可能不同的情况
            if predictions.ndim == 3:  # [batch, time, feature]
                pred_values = predictions[0, :, 0]  # 第一个批次，所有时间点，第一个特征
            elif predictions.ndim == 2:  # [time, feature]
                pred_values = predictions[:, 0]  # 所有时间点，第一个特征
            else:
                pred_values = predictions  # 假设是一维数组

            # 确保我们只使用预测天数的结果
            pred_values = pred_values[:forecast_days]

            for i in range(len(pred_dates_str)):
                if i < len(pred_values):
                    result_data.append({
                        'date': pred_dates_str[i],
                        f'predicted_{target_name}': float(pred_values[i])
                    })

            # 生成产品ID和时间戳
            file_name = os.path.basename(data_path)
            product_id = file_name.split('_product_')[1].split('_')[0] if '_product_' in file_name else 'unknown'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

            # 保存预测结果
            result_filename = f"prediction_{problem_type}_product_{product_id}_{timestamp}.json"
            result_path = os.path.join(os.path.dirname(data_path), result_filename)

            with open(result_path, 'w') as f:
                json.dump(result_data, f, indent=4)

            logger.info(f"预测完成，结果保存至: {result_path}")
            # 调用后处理服务
            from backend.app.services.postprocess_service import PostprocessService
            postprocess_result = PostprocessService.postprocess_predictions(
                predictions=predictions,
                data_path=data_path,
                target_name=target_name,
                problem_type=problem_type,
                product_id=product_id
            )

            if postprocess_result.get('status') == 'error':
                logger.error(f"后处理失败: {postprocess_result.get('message')}")
                # 如果后处理失败，返回原始预测结果
                return {
                    'status': 'success',
                    'product_id': product_id,
                    'problem_type': problem_type,
                    'data_path': data_path,
                    'prediction_path': result_path,
                    'forecast_days': forecast_days,
                    'predictions': result_data
                }
            else:
                # 后处理成功，返回后处理结果
                return postprocess_result
            # return {
            #     'status': 'success',
            #     'product_id': product_id,
            #     'problem_type': problem_type,
            #     'data_path': data_path,
            #     'prediction_path': result_path,
            #     'forecast_days': forecast_days,
            #     'predictions': result_data
            # }

        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Informer预测时出错: {str(e)}\n{error_traceback}")
            return {
                'status': 'error',
                'message': f"Informer预测时出错: {str(e)}",
                'traceback': error_traceback
            }