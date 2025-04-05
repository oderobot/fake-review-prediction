const { defineConfig } = require('@vue/cli-service')
const path = require('path')

module.exports = defineConfig({
  transpileDependencies: true,

  // 配置别名
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
  lintOnSave: false,
  // 开发服务器配置
  devServer: {
    port: 8080,
    open: true,  // 自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 后端Flask服务地址
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    }
  }
})