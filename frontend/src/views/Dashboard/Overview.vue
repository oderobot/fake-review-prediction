<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>虚假评论预测系统 - 数据大屏</h1>
    </div>

    <!-- 整体统计数据 -->
    <div class="overview-cards">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-title">总评论数</div>
            <div class="stat-value">{{ formatNumber(stats.totalComments) }}</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-title">虚假评论数</div>
            <div class="stat-value">{{ formatNumber(stats.fakeComments) }}</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-title">虚假评论率</div>
            <div class="stat-value">{{ formatPercentage(stats.fakeRate) }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 产品ID选择 -->
    <div class="product-selection">
      <el-select
        v-model="selectedProductId"
        placeholder="选择产品ID"
        @change="updateSelectedProduct"
      >
        <el-option
          v-for="pid in uniqueProductIds"
          :key="pid"
          :label="pid"
          :value="pid"
        />
      </el-select>
    </div>

    <!-- 图表区域 -->
    <div class="chart-container">
      <el-row :gutter="20">
        <!-- 虚假评论趋势 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>产品{{ selectedProductId }} - 评论趋势</span>
              </div>
            </template>
            <div class="chart-content">
              <line-chart
                v-if="chartData.trendData.length > 0"
                :chart-data="chartData.trendData[0].data"
                :chart-labels="chartData.trendLabels"
                :multi-line="true"
                :second-line-data="chartData.trendData.length > 1 ? chartData.trendData[1].data : []"
              />
              <div v-else class="no-data">暂无数据</div>
            </div>
          </el-card>
        </el-col>

        <!-- 评论类型分布 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>产品{{ selectedProductId }} - 评论类型</span>
              </div>
            </template>
            <div class="chart-content">
              <pie-chart
                v-if="chartData.productDistribution.length > 0"
                :chart-data="chartData.productDistribution"
                :chart-labels="chartData.productLabels"
              />
              <div v-else class="no-data">暂无数据</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Top 10虚假评论产品 -->
      <el-row class="chart-row">
        <el-col :span="24">
          <el-card class="chart-card table-card">
            <template #header>
              <div class="chart-header">
                <span>Top 10 虚假评论产品</span>
              </div>
            </template>
            <div class="table-content">
              <el-table
                :data="top10Products"
                border
                style="width: 100%"
              >
                <el-table-column prop="product" label="产品ID" />
                <el-table-column prop="totalComments" label="总评论数" />
                <el-table-column prop="fakeComments" label="虚假评论数" />
                <el-table-column prop="fakeRate" label="虚假评论率">
                  <template #default="scope">
                    {{ formatPercentage(scope.row.fakeRate) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import LineChart from '@/components/Charts/LineChart.vue'
import PieChart from '@/components/Charts/PieChart.vue'
import { UploadService } from '@/services/api'

const store = useStore()
const uploadedFile = computed(() => store.getters.getUploadedFile)

// 本地存储文件数据，而不是依赖Vuex
const fileData = ref([])

// 统计数据
const stats = reactive({
  totalComments: 0,
  fakeComments: 0,
  fakeRate: 0
})

// 唯一产品ID列表
const uniqueProductIds = ref([])
const selectedProductId = ref(null)

// 图表数据
const chartData = reactive({
  trendData: [],
  trendLabels: [],
  productDistribution: [],
  productLabels: []
})

// Top 10虚假评论产品
const top10Products = ref([])

onMounted(async () => {
  if (uploadedFile.value) {
    await loadFileData()
  }
})

// 监听uploadedFile变化，当有新文件上传时重新加载数据
watch(uploadedFile, async (newVal) => {
  if (newVal) {
    await loadFileData()
  }
})

const loadFileData = async () => {
  const file = uploadedFile.value
  if (!file) return

  try {
    ElMessage.info('正在加载数据，请稍候...')

    const response = await UploadService.getFullFileData(file.path)

    // 确保response结构正确
    if (!response.data || !response.data.file_data || !response.data.file_data.data) {
      ElMessage.error('返回的数据格式不正确')
      console.error('API返回的数据格式不正确:', response.data)
      return
    }

    // 保存数据到本地引用
    fileData.value = response.data.file_data.data

    // 获取唯一产品ID
    uniqueProductIds.value = [...new Set(fileData.value.map(item => item.prod_id))]

    // 默认选择第一个产品
    if (uniqueProductIds.value.length > 0) {
      selectedProductId.value = uniqueProductIds.value[0]
    }

    processOverallStats(fileData.value)
    processTop10Products(fileData.value)

    if (selectedProductId.value) {
      updateSelectedProduct(selectedProductId.value)
    }

    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error(`加载数据失败: ${error.message || '未知错误'}`)
  }
}

const processOverallStats = (data) => {
  if (!data || data.length === 0) return

  stats.totalComments = data.length
  stats.fakeComments = data.filter(item => item.tag === 'fake').length
  stats.fakeRate = stats.totalComments > 0 ? stats.fakeComments / stats.totalComments : 0
}

const processTop10Products = (data) => {
  if (!data || data.length === 0) return

  const productStats = {}

  data.forEach(item => {
    if (!productStats[item.prod_id]) {
      productStats[item.prod_id] = { total: 0, fake: 0 }
    }
    productStats[item.prod_id].total++
    if (item.tag === 'fake') {
      productStats[item.prod_id].fake++
    }
  })

  top10Products.value = Object.entries(productStats)
    .map(([product, stats]) => ({
      product,
      totalComments: stats.total,
      fakeComments: stats.fake,
      fakeRate: stats.fake / stats.total
    }))
    .sort((a, b) => b.fakeComments - a.fakeComments)
    .slice(0, 10)
}

const updateSelectedProduct = (productId) => {
  if (!productId || !fileData.value || fileData.value.length === 0) {
    console.warn('无法更新产品数据：产品ID不存在或文件数据为空')
    return
  }

  try {
    const productData = fileData.value.filter(item => item.prod_id === productId)

    if (productData.length === 0) {
      console.warn(`未找到产品ID为 ${productId} 的数据`)
      return
    }

    processTrendData(productData)
    processProductDistribution(productData)
  } catch (error) {
    console.error('更新选定产品时出错:', error)
    ElMessage.error(`处理产品${productId}数据时出错`)
  }
}

const processTrendData = (data) => {
  if (!data || data.length === 0) return

  const groupedByDate = {}

  // 确保日期字段存在且格式正确
  data.forEach(item => {
    if (!item.date) return

    const date = typeof item.date === 'string' ? item.date.substring(0, 10) : ''
    if (!date) return

    if (!groupedByDate[date]) {
      groupedByDate[date] = { total: 0, fake: 0 }
    }
    groupedByDate[date].total++
    if (item.tag === 'fake') {
      groupedByDate[date].fake++
    }
  })

  const sortedDates = Object.keys(groupedByDate).sort()

  chartData.trendLabels = sortedDates
  chartData.trendData = [
    {
      name: '总评论数',
      data: sortedDates.map(date => groupedByDate[date].total)
    },
    {
      name: '虚假评论数',
      data: sortedDates.map(date => groupedByDate[date].fake)
    }
  ]
}

const processProductDistribution = (data) => {
  if (!data || data.length === 0) return

  const fakeComments = data.filter(item => item.tag === 'fake').length
  const realComments = data.filter(item => item.tag !== 'fake').length

  chartData.productLabels = ['虚假评论', '真实评论']
  chartData.productDistribution = [fakeComments, realComments]
}

const formatNumber = (num) => isNaN(num) ? '0' : num.toLocaleString()
const formatPercentage = (num) => isNaN(num) ? '0%' : (num * 100).toFixed(2) + '%'
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.dashboard-header {
  margin-bottom: 20px;
}

.dashboard-header h1 {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  color: white;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-title {
  font-size: 16px;
  opacity: 0.8;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.product-selection {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart-container {
  margin-top: 20px;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  height: 400px;
  margin-bottom: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.table-card {
  height: auto;
  min-height: 300px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.chart-content {
  height: 320px;
  padding: 10px;
}

.table-content {
  padding: 10px;
}

.no-data {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .overview-cards .el-col {
    width: 100%;
    margin-bottom: 15px;
  }

  .chart-container .el-col {
    width: 100%;
  }
}
</style>