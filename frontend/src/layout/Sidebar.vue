<template>
  <div class="sidebar-container">
    <el-menu
      default-active="dashboard"
      class="el-menu-vertical"
      :collapse="isCollapse"
      background-color="#001529"
      text-color="#fff"
      active-text-color="#ffd04b"
      router
    >
      <div class="logo-container">
        <img src="../assets/logo.png" alt="Logo" class="logo">
        <h1 v-if="!isCollapse" class="title">虚假评论预测系统</h1>
      </div>

      <el-menu-item index="/dashboard">
        <el-icon><DataBoard /></el-icon>
        <template #title>数据大屏</template>
      </el-menu-item>

      <el-sub-menu index="file-management">
        <template #title>
          <el-icon><DocumentAdd /></el-icon>
          <span>文件管理</span>
        </template>
        <el-menu-item index="/file-list">文件列表</el-menu-item>
        <el-menu-item index="/file-upload">文件上传</el-menu-item>
      </el-sub-menu>

      <el-sub-menu index="prediction">
        <template #title>
          <el-icon><Histogram /></el-icon>
          <span>预测管理</span>
        </template>
        <el-menu-item index="/prediction-list">预测列表</el-menu-item>
        <el-menu-item index="/prediction-analysis">预测分析</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/system-config">
        <el-icon><Setting /></el-icon>
        <template #title>系统配置</template>
      </el-menu-item>
    </el-menu>

    <div class="collapse-btn" @click="toggleSidebar">
      <el-icon>
        <Expand v-if="isCollapse" />
        <Fold v-else />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  DataBoard,
  DocumentAdd,
  Histogram,
  Setting,
  Expand,
  Fold
} from '@element-plus/icons-vue'

const isCollapse = ref(false)

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  background-color: #001529;
  position: relative;
}

.logo-container {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #002140;
}

.logo {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.title {
  color: white;
  font-size: 16px;
  margin: 0;
  white-space: nowrap;
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
}

.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  cursor: pointer;
  font-size: 20px;
}
</style>