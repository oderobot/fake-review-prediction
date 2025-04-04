import React, { useState, useEffect, useMemo } from 'react';
import {
  Container,
  Typography,
  Grid,
  Box,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import ReactECharts from 'echarts-for-react';
import Papa from 'papaparse';
import * as _ from 'lodash';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusAlert from '../components/StatusAlert';
import { API_BASE_URL } from '../utils/config';

const DataVisualizationPage = () => {
  const navigate = useNavigate();
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ show: false, severity: 'info', message: '' });
  const [dataStats, setDataStats] = useState({
    totalComments: 0,
    fakeComments: 0,
    realComments: 0,
    fakeRatio: 0,
    productCount: 0,
    userCount: 0
  });

  // 图表配置使用 useMemo 确保只在数据变化时重新计算
  const chartOptions = useMemo(() => {
    if (rawData.length === 0) return {};

    // 按日期统计真实/虚假评论
    const commentByDate = _.groupBy(rawData, 'date');
    const dates = Object.keys(commentByDate).sort();
    const realComments = dates.map(date =>
      commentByDate[date].filter(item => item.tag === 'real').length
    );
    const fakeComments = dates.map(date =>
      commentByDate[date].filter(item => item.tag === 'fake').length
    );

    // 产品评论分布
    const commentByProduct = _.countBy(rawData, 'prod_id');

    // 产品虚假评论率
    const productStats = _.groupBy(rawData, 'prod_id');
    const productFakeRatio = Object.entries(productStats).map(([prodId, comments]) => {
      const fakeCount = comments.filter(c => c.tag === 'fake').length;
      const totalCount = comments.length;
      return {
        prodId,
        fakeRatio: (fakeCount / totalCount * 100).toFixed(2)
      };
    });

    return {
      // 评论趋势图
      commentTrend: {
        title: { text: '每日评论趋势', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: {
          data: ['真实评论', '虚假评论'],
          top: 'bottom'
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: { rotate: 45 }
        },
        yAxis: { type: 'value', name: '评论数' },
        series: [
          {
            name: '真实评论',
            type: 'line',
            data: realComments,
            itemStyle: { color: 'green' }
          },
          {
            name: '虚假评论',
            type: 'line',
            data: fakeComments,
            itemStyle: { color: 'red' }
          }
        ]
      },
      // 产品评论分布
      productDistribution: {
        title: { text: '产品评论分布', left: 'center' },
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: { show: false },
          data: Object.entries(commentByProduct).map(([name, value]) => ({
            name,
            value,
            itemStyle: { color: `hsl(${Math.random() * 360}, 70%, 50%)` }
          }))
        }]
      },
      // 产品虚假评论率
      fakeRatio: {
        title: { text: '产品虚假评论率', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: productFakeRatio.map(p => p.prodId),
          axisLabel: { rotate: 45 }
        },
        yAxis: { type: 'value', name: '虚假评论率(%)', max: 100 },
        series: [{
          type: 'bar',
          data: productFakeRatio.map(p => p.fakeRatio),
          itemStyle: {
            color: (params) => {
              const ratio = parseFloat(params.data);
              return ratio > 50 ? 'red' :
                     ratio > 20 ? 'orange' : 'green';
            }
          }
        }]
      }
    };
  }, [rawData]);

  useEffect(() => {
    try {
      // 安全地从sessionStorage获取数据
      const storedData = sessionStorage.getItem('uploadedFileData');
      if (!storedData) {
        setAlert({
          show: true,
          severity: 'error',
          message: '未找到上传文件，请重新上传'
        });
        navigate('/upload');
        return;
      }

      let fileData;
      try {
        fileData = JSON.parse(storedData);
      } catch (parseError) {
        console.error('解析存储的文件数据错误:', parseError);
        setAlert({
          show: true,
          severity: 'error',
          message: '存储的文件数据格式错误，请重新上传'
        });
        navigate('/upload');
        return;
      }

      // 使用新API获取完整数据
      const fetchData = async () => {
        try {
          setLoading(true);
          console.log('正在请求文件数据，文件路径:', fileData.path);

          const response = await fetch(`${API_BASE_URL}/api/upload/get-full-data`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ file_path: fileData.path }),
          });

          // 检查响应状态
          if (!response.ok) {
            const errorText = await response.text();
            console.error('API响应错误:', response.status, errorText);
            throw new Error(`服务器返回错误: ${response.status} ${errorText.substr(0, 100)}`);
          }

          // 安全解析JSON
          let result;
          try {
            result = await response.json();
          } catch (jsonError) {
            console.error('解析响应JSON错误:', jsonError);
            throw new Error('无法解析服务器响应');
          }

          if (result.status === 'success') {
            const completeData = result.file_data?.data || [];
            if (completeData.length === 0) {
              console.warn('API返回的数据为空');
            }
            processDataStats(completeData);
            setRawData(completeData);
          } else {
            throw new Error(result.message || '获取数据失败');
          }
        } catch (error) {
          console.error('获取数据错误:', error);
          setAlert({
            show: true,
            severity: 'error',
            message: `数据加载失败: ${error.message}`
          });
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    } catch (error) {
      console.error('整体数据加载流程错误:', error);
      setAlert({
        show: true,
        severity: 'error',
        message: `发生未预期的错误: ${error.message}`
      });
      setLoading(false);
    }
  }, [navigate]);

  const processDataStats = (data) => {
    const realComments = data.filter(c => c.tag === 'real');
    const fakeComments = data.filter(c => c.tag === 'fake');
    const uniqueProducts = new Set(data.map(c => c.prod_id));
    const uniqueUsers = new Set(data.map(c => c.user_id));

    setDataStats({
      totalComments: data.length,
      fakeComments: fakeComments.length,
      realComments: realComments.length,
      fakeRatio: (fakeComments.length / data.length * 100).toFixed(2),
      productCount: uniqueProducts.size,
      userCount: uniqueUsers.size
    });
  };

  if (loading) {
    return <LoadingSpinner message="正在加载数据..." />;
  }

  return (
    <Container maxWidth="xl">
      <StatusAlert
        open={alert.show}
        severity={alert.severity}
        message={alert.message}
        onClose={() => setAlert({ ...alert, show: false })}
      />

      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        数据可视化分析
      </Typography>

      {/* 总体统计 */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Chip
          label={`总评论数: ${dataStats.totalComments}`}
          color="primary"
          variant="outlined"
        />
        <Chip
          label={`真实评论数: ${dataStats.realComments}`}
          color="success"
          variant="outlined"
        />
        <Chip
          label={`虚假评论数: ${dataStats.fakeComments}`}
          color="error"
          variant="outlined"
        />
        <Chip
          label={`虚假评论率: ${dataStats.fakeRatio}%`}
          color="warning"
          variant="outlined"
        />
        <Chip
          label={`产品数量: ${dataStats.productCount}`}
          color="info"
          variant="outlined"
        />
        <Chip
          label={`用户数量: ${dataStats.userCount}`}
          color="secondary"
          variant="outlined"
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                评论趋势
              </Typography>
              {chartOptions.commentTrend ? (
                <ReactECharts
                  option={chartOptions.commentTrend}
                  style={{ height: 400 }}
                />
              ) : (
                <Typography variant="body1" color="text.secondary">
                  暂无评论趋势数据
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                产品评论分布
              </Typography>
              {chartOptions.productDistribution ? (
                <ReactECharts
                  option={chartOptions.productDistribution}
                  style={{ height: 400 }}
                />
              ) : (
                <Typography variant="body1" color="text.secondary">
                  暂无产品评论分布数据
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                产品虚假评论率
              </Typography>
              {chartOptions.fakeRatio ? (
                <ReactECharts
                  option={chartOptions.fakeRatio}
                  style={{ height: 500 }}
                />
              ) : (
                <Typography variant="body1" color="text.secondary">
                  暂无产品虚假评论率数据
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DataVisualizationPage;