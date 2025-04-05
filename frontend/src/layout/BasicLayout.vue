<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="240px">
        <Sidebar />
      </el-aside>

      <el-container>
        <el-header height="60px">
          <Header />
        </el-header>

        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>

        <el-footer height="50px">
          <div class="footer-content">
            © 2024 虚假评论预测系统 | 技术支持：AI智能团队
          </div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
</script>

<style>
.layout-container {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #001529;
  transition: width 0.3s;
}

.el-header {
  padding: 0;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.el-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f2f5;
  color: #999;
  font-size: 12px;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from,
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>