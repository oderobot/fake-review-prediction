<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, toRefs } from 'vue';
import Chart from 'chart.js/auto';

// 定义props
const props = defineProps({
  chartData: {
    type: Array,
    required: true
  },
  chartLabels: {
    type: Array,
    required: true
  },
  horizontal: {
    type: Boolean,
    default: false
  }
});

// 解构props以便在watch中使用
const { chartData, chartLabels, horizontal } = toRefs(props);

// 引用canvas元素
const chartCanvas = ref(null);
// 存储图表实例
let chartInstance = null;

// 设置图表数据
const setupChart = () => {
  if (!chartCanvas.value) return;

  // 如果已存在图表实例，销毁它
  if (chartInstance) {
    chartInstance.destroy();
  }

  // 生成颜色数组
  const colors = chartLabels.value.map(() =>
    `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.7)`
  );

  // 创建图表
  chartInstance = new Chart(chartCanvas.value, {
    type: horizontal.value ? 'bar' : 'bar', // 水平或垂直条形图
    data: {
      labels: chartLabels.value,
      datasets: [{
        label: '数量',
        data: chartData.value,
        backgroundColor: colors,
        borderColor: colors.map(color => color.replace('0.7', '1')),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal.value ? 'y' : 'x', // 设置为水平或垂直
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: horizontal.value ? '' : '数量'
          }
        },
        x: {
          title: {
            display: true,
            text: horizontal.value ? '数量' : ''
          }
        }
      }
    }
  });
};

// 在组件挂载后初始化图表
onMounted(() => {
  setupChart();
});

// 监听数据变化，更新图表
watch([chartData, chartLabels, horizontal], () => {
  setupChart();
});
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  width: 100%;
}
</style>