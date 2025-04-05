import axios from 'axios'

const BASE_URL = 'http://localhost:5000/api'  // 直接访问后端，不使用代理

export const UploadService = {
  // 文件上传
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`${BASE_URL}/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 验证文件
  validateFile(filePath) {
    return axios.post(`${BASE_URL}/upload/validate`, { file_path: filePath })
  },

  // 获取完整文件数据
  getFullFileData(filePath) {
    console.log('API Call - File Path:', filePath)
    return axios.post(`${BASE_URL}/upload/get-full-data`, {
      file_path: filePath
    })
  },
}

export const PreprocessService = {
  // 数据预处理
  preprocessForInformer(fileInfo, prodId = null) {
    return axios.post(`${BASE_URL}/preprocess/informer`, {
      file_path: fileInfo.path,
      output_dir: null,
      prod_id: prodId
    })
  }
}

export const PredictionService = {
  // 执行预测
  predict(preprocessedFile, forecastDays = 7) {
    return axios.post(`${BASE_URL}/informer/predict`, {
      data_path: preprocessedFile.file_path,
      forecast_days: forecastDays,
      problem_type: 'fake_review'
    })
  },

  // 一步完成预处理和预测
  processAndPredict(options) {
    const { file_path, prod_id, forecast_days = 7, problem_type = 'fake_review' } = options;

    return axios.post(`${BASE_URL}/informer/process-and-predict`, {
      file_path: file_path,
      prod_id: prod_id,              // 指定要预测的商品ID
      output_dir: null,              // 使用默认输出目录
      forecast_days: forecast_days,  // 预测天数
      problem_type: problem_type     // 问题类型，默认假评论预测
    })
  }
}

// 新增：仪表盘服务
export const DashboardService = {
  // 获取已上传的文件列表
  getUploadedFiles() {
    return axios.get(`${BASE_URL}/upload/list-files`)
  },

  // 获取文件统计数据
  getFileStats(filePath) {
    return axios.post(`${BASE_URL}/upload/get-stats`, { file_path: filePath })
  },

  // 获取趋势数据
  getTrendData(filePath, period = 'daily') {
    return axios.post(`${BASE_URL}/upload/get-trend`, {
      file_path: filePath,
      period: period  // daily, weekly, monthly
    })
  },

  // 获取产品分布数据
  getProductDistribution(filePath) {
    return axios.post(`${BASE_URL}/upload/get-product-distribution`, { file_path: filePath })
  }
}