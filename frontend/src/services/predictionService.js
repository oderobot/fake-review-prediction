// src/services/predictionService.js
import { API_BASE_URL } from '../utils/config';

/**
 * 处理预测请求
 * @param {Object} data - 预测请求数据
 * @param {string} data.file_path - 文件路径
 * @param {number} data.forecast_days - 预测天数
 * @param {string} data.problem_type - 问题类型
 * @returns {Promise<Object>} 预测结果
 */
export const processPrediction = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/informer/process-and-predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      // 如果返回了可用的产品ID列表
      if (result.available_product_ids) {
        throw new Error(`没有找到指定的产品ID。可用的产品ID包括: ${result.available_product_ids.join(', ')}`);
      }
      throw new Error(result.message || '预测请求失败');
    }

    return result;
  } catch (error) {
    console.error('预测请求错误:', error);
    throw error;
  }
};

/**
 * 直接进行预测（不包括预处理）
 * @param {Object} data - 预测请求数据
 * @returns {Promise<Object>} 预测结果
 */
export const predict = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/informer/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || '预测请求失败');
    }

    return result;
  } catch (error) {
    console.error('预测请求错误:', error);
    throw error;
  }
};

/**
 * 获取Informer服务状态
 * @returns {Promise<Object>} 服务状态
 */
export const getInformerStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/informer/status`);

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || '获取服务状态失败');
    }

    return result;
  } catch (error) {
    console.error('获取服务状态错误:', error);
    throw error;
  }
};