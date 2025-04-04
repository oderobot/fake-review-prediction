# backend/app/services/upload_service.py
import os
import uuid
from datetime import datetime
import pandas as pd
import traceback
from flask import current_app
from werkzeug.utils import secure_filename


class UploadService:
    """文件上传服务类"""

    @staticmethod
    def save_file(file, upload_dir=None):
        """保存上传的文件

        Args:
            file: 上传的文件对象
            upload_dir: 上传目录路径

        Returns:
            dict: 包含文件信息的字典
        """
        if upload_dir is None:
            upload_dir = os.path.join(current_app.root_path, 'tmp', 'uploads')

            # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)  # 自动创建目录

        # 生成唯一文件名（保留原有逻辑）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        file.save(file_path)
        return {
            'original_name': file.filename,
            'saved_name': filename,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'upload_time': timestamp
        }

    @staticmethod
    def validate_file_type(filename):
        """验证文件类型是否允许

        Args:
            filename: 文件名

        Returns:
            bool: 文件类型是否允许
        """
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def validate_file_content(file_path):
        """验证文件内容是否符合格式要求

        Args:
            file_path: 文件路径

        Returns:
            dict: 验证结果和文件信息
        """
        try:
            # 根据文件类型读取数据
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return {'valid': False, 'message': '不支持的文件类型'}

            # 检查必要的列
            required_columns = ['prod_id', 'date', 'tag']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return {
                    'valid': False,
                    'message': f"文件缺少必要的列: {', '.join(missing_columns)}"
                }

            # 基本验证通过，返回文件信息
            return {
                'valid': True,
                'rows': len(df),
                'columns': list(df.columns),
                'products': df['prod_id'].nunique(),
                'date_range': {
                    'min': str(df['date'].min()),
                    'max': str(df['date'].max())
                },
                'fake_count': len(df[df['tag'] == 'fake']),
                'sample_data': df.head(5).to_dict('records')
            }

        except Exception as e:
            return {
                'valid': False,
                'message': f"验证文件时出错: {str(e)}"
            }

    @staticmethod
    def get_full_file_data(file_path):
        """读取文件的完整数据

        Args:
            file_path: 文件路径

        Returns:
            dict: 包含完整数据的字典
        """
        try:
            # 根据文件类型读取数据
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return {'valid': False, 'message': '不支持的文件类型'}

            # 将日期列转换为日期类型
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

            # 返回完整数据
            return {
                'valid': True,
                'rows': len(df),
                'columns': list(df.columns),
                'data': df.to_dict('records')
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f"读取文件时出错: {str(e)}",
                'traceback': traceback.format_exc()
            }