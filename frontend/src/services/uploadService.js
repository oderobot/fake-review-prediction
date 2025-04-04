// src/services/uploadService.js
import { API_BASE_URL } from '../utils/config';

/**
 * 上传文件
 * @param {File} file - 文件对象
 * @returns {Promise<Object>} 上传结果
 */
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload/`, {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || '文件上传失败');
    }

    // 验证文件
    if (result.status === 'success') {
      const validateResponse = await fetch(`${API_BASE_URL}/api/upload/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_path: result.file.path }),
      });

      const validateResult = await validateResponse.json();

      if (!validateResponse.ok || validateResult.status !== 'success') {
        throw new Error(validateResult.message || '文件验证失败');
      }

      // 合并上传和验证结果
      return {
        status: 'success',
        message: '文件上传并验证成功',
        file: {
          ...result.file,
          info: validateResult.file_info
        }
      };
    }

    return result;
  } catch (error) {
    console.error('文件上传错误:', error);
    return {
      status: 'error',
      message: error.message || '文件上传失败'
    };
  }
};

// 在 src/services/uploadService.js 中添加
/**
 * 获取文件的完整数据
 * @param {string} filePath - 文件路径
 * @returns {Promise<Object>} 包含完整数据的响应
 */
export const getFullFileData = async (filePath) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upload/get-full-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_path: filePath }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || '获取文件数据失败');
    }

    return result;
  } catch (error) {
    console.error('获取文件数据错误:', error);
    throw error;
  }
};