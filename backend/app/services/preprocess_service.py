# backend/app/services/preprocess_service.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class PreprocessService:
    """数据预处理服务类，生成适用于Informer模型的数据 保存到新的文件当中"""

    @staticmethod
    def preprocess_for_informer(file_path, output_dir=None, prod_id=None):
        """预处理上传的文件数据并保存为Informer模型可用的格式

        Args:
            file_path: 原始文件路径
            output_dir: 输出目录，如果为None则使用原文件所在目录
            prod_id: 可选，指定要分析的产品ID

        Returns:
            dict: 预处理结果
        """
        try:
            # 根据文件类型读取数据
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return {'status': 'error', 'message': '不支持的文件类型'}

            # 确保必要的列存在
            required_columns = ['prod_id', 'date', 'tag']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    'status': 'error',
                    'message': f"文件缺少必要的列: {', '.join(missing_columns)}"
                }

            # 将产品ID转换为字符串，以确保类型一致性
            df['prod_id'] = df['prod_id'].astype(str)

            # 将日期列转换为日期类型
            df['date'] = pd.to_datetime(df['date'])

            # 设置输出目录
            if output_dir is None:
                output_dir = os.path.dirname(file_path)

            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)

            # 获取原始文件名（不带扩展名）
            original_filename = os.path.splitext(os.path.basename(file_path))[0]

            # 处理的产品和生成的文件信息
            processed_files = []

            # 处理商品ID的逻辑
            if prod_id is not None:
                # 将输入的prod_id转换为字符串
                prod_id = str(prod_id)

                # 检查是否存在指定的产品ID
                if prod_id not in df['prod_id'].unique():
                    return {
                        'status': 'error',
                        'message': f'没有找到产品ID为 {prod_id} 的数据',
                        'available_product_ids': list(df['prod_id'].unique())
                    }

                # 如果存在，只处理该产品
                product_ids = [prod_id]
            else:
                # 否则处理所有产品
                product_ids = df['prod_id'].unique()

            for p_id in product_ids:
                # 筛选当前产品的数据
                product_df = df[df['prod_id'] == p_id]

                # 获取日期范围
                min_date = product_df['date'].min()
                max_date = product_df['date'].max()

                # 创建完整的日期范围
                date_range = pd.date_range(start=min_date, end=max_date)

                # 按日期统计评论数
                daily_stats = product_df.groupby(product_df['date'].dt.date).agg(
                    total_comments=('tag', 'count'),
                    fake_comments=('tag', lambda x: (x == 'fake').sum())
                ).reset_index()

                # 将日期转换为相同格式以便后续合并
                daily_stats['date'] = pd.to_datetime(daily_stats['date'])

                # 创建包含所有日期的DataFrame
                full_date_df = pd.DataFrame({'date': date_range})

                # 合并已有数据和完整日期范围
                merged_df = pd.merge(full_date_df, daily_stats, on='date', how='left')

                # 填充缺失值
                merged_df['total_comments'] = merged_df['total_comments'].fillna(0).astype(int)
                merged_df['fake_comments'] = merged_df['fake_comments'].fillna(0).astype(int)

                # 为Informer模型准备数据格式
                informer_df = pd.DataFrame()
                informer_df['date'] = merged_df['date'].dt.strftime('%Y-%m-%d')  # 日期列
                informer_df['total'] = merged_df['total_comments']  # 总评论数
                informer_df['fake'] = merged_df['fake_comments']  # 虚假评论数

                # 生成输出文件名（与原始文件名和产品ID相关联）
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                output_filename = f"{original_filename}_product_{p_id}_{timestamp}.csv"
                output_path = os.path.join(output_dir, output_filename)

                # 保存为CSV文件（Informer模型通常使用CSV格式）
                informer_df.to_csv(output_path, index=False)

                # 记录处理信息
                processed_files.append({
                    'product_id': p_id,
                    'file_path': output_path,
                    'date_range': {
                        'start': min_date.strftime('%Y-%m-%d'),
                        'end': max_date.strftime('%Y-%m-%d')
                    },
                    'total_days': len(date_range),
                    'total_comments': int(merged_df['total_comments'].sum()),
                    'fake_comments': int(merged_df['fake_comments'].sum())
                })

            return {
                'status': 'success',
                'processed_files': processed_files,
                'summary': {
                    'total_products': len(processed_files),
                    'original_file': file_path,
                    'all_product_ids': list(df['prod_id'].unique())
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f"数据预处理时出错: {str(e)}"
            }