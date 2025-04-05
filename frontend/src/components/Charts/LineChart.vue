<template>
  <div class="file-upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>文件上传</span>
        </div>
      </template>

      <el-upload
        class="uploader"
        drag
        :http-request="uploadFile"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        accept=".csv,.xlsx,.xls"
        multiple
      >
        <el-icon class="el-icon-upload"><Upload /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持 .csv, .xlsx, .xls 文件，且大小不超过 500MB
          </div>
        </template>
      </el-upload>

      <!-- 文件验证信息 -->
      <div v-if="fileValidationInfo" class="file-validation-info">
        <h3>文件信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总行数">
            {{ fileValidationInfo.rows || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="产品数量">
            {{ fileValidationInfo.products || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="日期范围" v-if="fileValidationInfo.date_range">
            {{ fileValidationInfo.date_range.min || '未知' }} 至 {{ fileValidationInfo.date_range.max || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="日期范围" v-else>
            未知
          </el-descriptions-item>
          <el-descriptions-item label="虚假评论数">
            {{ fileValidationInfo.fake_count || 0 }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 预测设置区域 -->
      <div v-if="uploadedFile && productIds.length > 0" class="prediction-settings">
        <h3>预测设置</h3>
        <el-form :model="predictionForm" label-width="120px">
          <el-form-item label="选择商品ID">
            <el-select
              v-model="predictionForm.productId"
              placeholder="请选择商品ID"
              style="width: 100%"
            >
              <el-option
                v-for="id in productIds"
                :key="id"
                :label="id"
                :value="id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="预测天数">
            <el-input-number
              v-model="predictionForm.forecastDays"
              :min="1"
              :max="30"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 预处理和预测按钮 -->
      <div v-if="uploadedFile" class="action-buttons">
        <el-button
          type="primary"
          @click="preprocessAndPredict"
          :loading="isProcessing"
          :disabled="uploadedFile && productIds.length > 0 && !predictionForm.productId"
        >
          开始预处理和预测
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { UploadService, PredictionService } from '@/services/api'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

// 计算属性获取Vuex状态
const uploadedFile = computed(() => store.getters.getUploadedFile)
const fileValidationInfo = computed(() => store.getters.getFileValidationInfo)
const fileData = computed(() => store.getters.getFileData)

// 响应式状态
const isProcessing = ref(false)
const productIds = ref([])

// 预测表单
const predictionForm = ref({
  productId: '',
  forecastDays: 7
})

// 监听文件数据变化，提取可用的商品ID
watch(fileData, (newData) => {
  if (newData && newData.length > 0) {
    extractProductIds(newData)
  }
})

// 组件挂载时，如果已有文件数据，则提取商品ID
onMounted(() => {
  if (fileData.value && fileData.value.length > 0) {
    extractProductIds(fileData.value)
  }
})

// 从文件数据中提取唯一的商品ID
const extractProductIds = (data) => {
  if (!data || data.length === 0) return

  try {
    // 获取唯一的产品ID
    const uniqueIds = [...new Set(data.map(item => item.prod_id))]
    productIds.value = uniqueIds

    // 如果存在商品ID，默认选择第一个
    if (uniqueIds.length > 0) {
      predictionForm.value.productId = uniqueIds[0]
    }
  } catch (error) {
    console.error('提取商品ID时出错:', error)
  }
}

// 文件上传前校验
const beforeUpload = (file) => {
  const isValidType = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    '' // 允许空MIME类型（有些CSV文件可能没有正确的MIME类型）
  ].includes(file.type) || file.name.endsWith('.csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')

  const isLt500M = file.size / 1024 / 1024 < 500

  if (!isValidType) {
    ElMessage.error('只能上传 CSV, XLSX, XLS 文件')
    return false
  }
  if (!isLt500M) {
    ElMessage.error('文件大小不能超过 500MB')
    return false
  }
  return true
}

// 自定义上传方法
const uploadFile = async (options) => {
  try {
    ElMessage.info('文件上传中，请稍候...')

    const formData = new FormData()
    formData.append('file', options.file)

    const response = await UploadService.uploadFile(options.file)

    if (!response.data || !response.data.file) {
      throw new Error('上传响应格式不正确')
    }

    const uploadedFileData = response.data.file

    // 验证文件
    const validationResponse = await UploadService.validateFile(uploadedFileData.path)

    // 检查返回的数据结构
    let validInfo
    if (validationResponse.data && validationResponse.data.file_info) {
      validInfo = validationResponse.data.file_info
    } else if (validationResponse.data && validationResponse.data.valid) {
      validInfo = validationResponse.data
    } else {
      validInfo = {
        rows: 0,
        products: 0,
        fake_count: 0,
        date_range: { min: '未知', max: '未知' }
      }
    }

    // 使用Vuex存储文件信息
    store.dispatch('saveUploadFile', {
      file: uploadedFileData,
      validationInfo: validInfo
    })

    // 获取完整文件数据并存储到Vuex
    try {
      const fileDataResponse = await UploadService.getFullFileData(uploadedFileData.path)
      if (fileDataResponse.data && fileDataResponse.data.file_data && fileDataResponse.data.file_data.data) {
        store.dispatch('saveFileData', fileDataResponse.data.file_data.data)

        // 提取商品ID
        extractProductIds(fileDataResponse.data.file_data.data)
      }
    } catch (error) {
      console.error('获取文件数据失败:', error)
      // 不阻止用户继续操作，只记录错误
    }

    ElMessage.success('文件上传成功')
    options.onSuccess && options.onSuccess()
  } catch (error) {
    console.error('文件上传失败:', error)
    ElMessage.error(`文件上传失败: ${error.response?.data?.message || error.message || '未知错误'}`)
    options.onError && options.onError(error)
  }
}

// 处理上传成功
const handleUploadSuccess = () => {
  // 可以添加额外的成功处理逻辑
}

// 处理上传错误
const handleUploadError = (error) => {
  console.error('上传错误:', error)
  ElMessage.error(`文件上传失败: ${error.message || '未知错误'}`)
}

// 预处理和预测
const preprocessAndPredict = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先上传文件')
    return
  }

  if (!predictionForm.value.productId) {
    ElMessage.warning('请选择要预测的商品ID')
    return
  }

  try {
    isProcessing.value = true
    ElMessage.info(`开始为商品 ${predictionForm.value.productId} 预测 ${predictionForm.value.forecastDays} 天的数据，请耐心等待...`)

    const response = await PredictionService.processAndPredict({
      file_path: uploadedFile.value.path,
      prod_id: predictionForm.value.productId,
      forecast_days: predictionForm.value.forecastDays
    })

    if (response.data.status === 'success') {
      // 存储预测结果
      store.dispatch('savePredictionResult', response.data)

      ElMessage.success('预处理和预测完成')

      // 导航到数据大屏页面查看结果
      router.push('/dashboard')
    } else {
      ElMessage.error(`预测失败: ${response.data.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error(`预测失败: ${error.response?.data?.message || error.message || '未知错误'}`)
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.file-upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-card {
  margin-bottom: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.uploader {
  margin-bottom: 20px;
}

.el-upload__text {
  font-size: 16px;
  color: #606266;
  margin: 12px 0;
}

.el-upload__text em {
  color: #409EFF;
  font-style: normal;
  font-weight: bold;
}

.el-upload__tip {
  color: #909399;
  margin-top: 10px;
}

.file-validation-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.file-validation-info h3, .prediction-settings h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.prediction-settings {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.action-buttons .el-button {
  padding: 12px 24px;
  font-size: 16px;
}
</style>