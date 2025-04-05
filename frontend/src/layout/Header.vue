<template>
  <div class="header-container">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <el-input
        v-model="searchContent"
        placeholder="搜索..."
        class="search-input"
        prefix-icon="Search"
      />

      <el-dropdown>
        <div class="user-info">
          <el-avatar
            :src="userAvatar"
            size="default"
            class="user-avatar"
          />
          <span class="username">{{ username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
            <el-dropdown-item @click="handleSettings">系统设置</el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-tooltip content="系统通知" placement="bottom">
        <el-badge :value="12" class="notice-badge">
          <el-icon :size="20"><Bell /></el-icon>
        </el-badge>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'

const route = useRoute()

// 模拟用户信息
const username = ref('管理员')
const userAvatar = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e6565png.png')

// 当前页面标题
const currentPageTitle = computed(() => {
  // 根据路由映射页面标题
  const titleMap = {
    '/dashboard': '数据大屏',
    '/file-list': '文件列表',
    '/file-upload': '文件上传',
    '/prediction-list': '预测列表',
    '/prediction-analysis': '预测分析',
    '/system-config': '系统配置'
  }
  return titleMap[route.path] || '未知页面'
})

const searchContent = ref('')

const handleProfile = () => {
  // 处理个人中心逻辑
}

const handleSettings = () => {
  // 处理系统设置逻辑
}

const handleLogout = () => {
  // 处理退出登录逻辑
}
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-input {
  width: 200px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  margin-right: 10px;
}

.username {
  font-size: 14px;
}

.notice-badge {
  cursor: pointer;
  margin-left: 15px;
}
</style>