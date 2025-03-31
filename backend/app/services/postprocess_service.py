# backend/app/services/postprocess_service.py
import numpy as np
import pandas as pd
import json
import os
import logging
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostprocessService:
    """预测结果后处理服务类，将Informer预测结果转换回原始尺度"""

    @staticmethod
    def postprocess_predictions(predictions, data_path, target_name="fake", problem_type="fake_review",
                                product_id="unknown"):
        """对Informer预测结果进行后处理，将值转换回原始尺度

        Args:
            predictions: 模型预测结果的numpy数组
            data_path: 预处理后的数据文件路径
            target_name: 目标特征名称
            problem_type: 问题类型
            product_id: 产品ID

        Returns:
            dict: 后处理后的预测结果
        """
        try:
            logger.info(f"开始对预测结果进行后处理，目标特征: {target_name}")

            # 读取原始数据
            df_raw = pd.read_csv(data_path)
            if 'date' not in df_raw.columns:
                logger.error("数据文件缺少date列")
                return {
                    'status': 'error',
                    'message': '数据文件格式不正确，缺少date列'
                }

            # 确保日期列是日期类型
            df_raw['date'] = pd.to_datetime(df_raw['date'])

            # 获取预测形状
            pred_shape = predictions.shape
            logger.info(f"预测结果形状: {pred_shape}")

            # 将预测值重塑为2D，便于处理
            pred_2d = predictions.reshape(-1, predictions.shape[-1])

            # 分割训练集用于拟合scaler
            num_train = int(len(df_raw) * 0.7)

            # 确保目标列存在
            if target_name not in df_raw.columns:
                logger.warning(f"目标列 {target_name} 不在数据中，将使用未转换的预测值")
                pred_orig = predictions
            else:
                try:
                    logger.info(f"应用数据转换恢复原始尺度")
                    train_data = df_raw[target_name][:num_train]

                    # 应用对数转换
                    has_zeros = (train_data == 0).any()
                    if has_zeros:
                        logger.info("检测到零值，使用log1p转换")
                        train_data_log = np.log1p(train_data)
                    else:
                        logger.info("使用log转换")
                        train_data_log = np.log(train_data)

                    # 创建和拟合MinMaxScaler
                    scaler = MinMaxScaler(feature_range=(0, 1))
                    scaler.fit(train_data_log.values.reshape(-1, 1))

                    # 应用MinMaxScaler逆变换
                    pred_log = scaler.inverse_transform(pred_2d)

                    # 应用指数变换（对数的逆变换）
                    if has_zeros:
                        pred_orig = np.expm1(pred_log)
                    else:
                        pred_orig = np.exp(pred_log)

                    # 重新调整形状
                    pred_orig = pred_orig.reshape(pred_shape)

                except Exception as e:
                    logger.error(f"数据转换过程出错: {str(e)}")
                    # 如果转换失败，使用原始预测值
                    pred_orig = predictions

            # 确保数值为非负
            pred_orig = np.maximum(pred_orig, 0)

            # 根据问题类型进行特定处理
            if problem_type == "fake_review":
                # 虚假评论数量应为整数
                pred_orig = np.round(pred_orig)

            # 生成预测日期
            last_date = df_raw['date'].iloc[-1]
            forecast_days = pred_orig.shape[1] if len(pred_orig.shape) > 1 else len(pred_orig)
            pred_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
            pred_dates_str = [date.strftime('%Y-%m-%d') for date in pred_dates]

            # 创建结果数据
            result_data = []

            # 处理不同形状的预测结果
            if len(pred_orig.shape) == 3:  # [batch, time, feature]
                pred_values = pred_orig[0, :, 0]  # 第一个批次，所有时间点，第一个特征
            elif len(pred_orig.shape) == 2:  # [time, feature]
                pred_values = pred_orig[:, 0]  # 所有时间点，第一个特征
            else:
                pred_values = pred_orig  # 假设是一维数组

            # 构建结果数据
            for i in range(min(len(pred_dates_str), len(pred_values))):
                result_data.append({
                    'date': pred_dates_str[i],
                    f'predicted_{target_name}': float(pred_values[i]),
                })

            # 计算基本统计量
            if target_name in df_raw.columns:
                stats = {
                    'min': float(df_raw[target_name].min()),
                    'max': float(df_raw[target_name].max()),
                    'mean': float(df_raw[target_name].mean()),
                    'std': float(df_raw[target_name].std())
                }
            else:
                stats = None

            # 生成文件名和路径
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            result_filename = f"prediction_{problem_type}_product_{product_id}_{timestamp}.json"
            result_path = os.path.join(os.path.dirname(data_path), result_filename)

            # 构建完整结果
            detailed_result = {
                'metadata': {
                    'model': 'informer',
                    'prediction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'target_feature': target_name,
                    'forecast_days': forecast_days,
                    'original_scale': True,
                    'product_statistics': stats,
                    'data_range': {
                        'start': df_raw['date'].min().strftime('%Y-%m-%d'),
                        'end': df_raw['date'].max().strftime('%Y-%m-%d')
                    }
                },
                'predictions': result_data
            }

            # 保存结果
            with open(result_path, 'w') as f:
                json.dump(detailed_result, f, indent=4)

            logger.info(f"后处理完成，结果保存至: {result_path}")

            return {
                'status': 'success',
                'product_id': product_id,
                'problem_type': problem_type,
                'data_path': data_path,
                'prediction_path': result_path,
                'forecast_days': forecast_days,
                'predictions': result_data,
                'metadata': detailed_result['metadata']
            }

        except Exception as e:
            logger.error(f"后处理预测结果时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'message': f"后处理预测结果时出错: {str(e)}"
            }