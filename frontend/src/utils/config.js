// src/utils/config.js

// API基础URL
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

// 应用配置
export const APP_CONFIG = {
  // 应用名称
  appName: '虚假评论预测系统',

  // 版本号
  version: '1.0.0',

  // 支持的问题类型
  problemTypes: [
    { value: 'fake_review', label: '虚假评论预测' },
    { value: 'sales_forecast', label: '销售预测' }
  ],

  // 支持的文件类型
  supportedFileTypes: ['.csv', '.xlsx', '.xls'],

  // 预测天数范围
  forecastDaysRange: {
    min: 1,
    max: 30,
    default: 7
  }
};