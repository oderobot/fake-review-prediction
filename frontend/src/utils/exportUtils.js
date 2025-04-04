// src/utils/exportUtils.js

/**
 * 将数据导出为CSV文件
 * @param {Array} data - 要导出的数据数组
 * @param {string} filename - 文件名
 */
export const exportToCsv = (data, filename) => {
  if (!data || !data.length) {
    console.warn('没有数据可导出');
    return;
  }

  // 获取所有列名
  const headers = Object.keys(data[0]);

  // 创建CSV内容
  const csvContent = [
    // 添加标题行
    headers.join(','),
    // 添加数据行
    ...data.map(row =>
      headers.map(header => {
        // 处理包含逗号、引号或换行符的数据
        const cell = row[header] != null ? String(row[header]) : '';
        if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
          return `"${cell.replace(/"/g, '""')}"`;
        }
        return cell;
      }).join(',')
    )
  ].join('\n');

  // 创建Blob对象
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

  // 创建下载链接
  const link = document.createElement('a');

  // 支持文件下载的浏览器
  if (navigator.msSaveBlob) { // IE 10+
    navigator.msSaveBlob(blob, filename);
  } else {
    // 其他现代浏览器
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};

/**
 * 将数据导出为JSON文件
 * @param {Object|Array} data - 要导出的数据
 * @param {string} filename - 文件名
 */
export const exportToJson = (data, filename) => {
  if (!data) {
    console.warn('没有数据可导出');
    return;
  }

  // 将数据转换为JSON字符串
  const jsonString = JSON.stringify(data, null, 2);

  // 创建Blob对象
  const blob = new Blob([jsonString], { type: 'application/json' });

  // 创建下载链接
  const link = document.createElement('a');

  // 支持文件下载的浏览器
  if (navigator.msSaveBlob) { // IE 10+
    navigator.msSaveBlob(blob, filename);
  } else {
    // 其他现代浏览器
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};