import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate
} from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Switch
} from '@mui/material';
import {
  Menu as MenuIcon,
  BarChart as BarChartIcon,
  Dashboard as DashboardIcon,
  DataUsage as DataUsageIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Brightness4 as Brightness4Icon,
  Upload as UploadIcon
} from '@mui/icons-material';

// 导入页面组件
import DataUploadPage from './pages/DataUploadPage';
import DataVisualizationPage from './pages/DataVisualizationPage';
import PredictionPage from './pages/PredictionPage';
import { getInformerStatus } from './services/predictionService';

function App() {
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [serverStatus, setServerStatus] = useState({
    checked: false,
    isOnline: false,
    info: null
  });

  // 创建主题
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#3f51b5',
      },
      secondary: {
        main: '#f50057',
      },
    },
    shape: {
      borderRadius: 8,
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 500,
      },
    },
    components: {
      MuiPaper: {
        defaultProps: {
          elevation: 0,
        },
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  });

  // 切换深色模式
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
  };

  // 切换抽屉
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  // 检查服务器状态
  React.useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const status = await getInformerStatus();
        setServerStatus({
          checked: true,
          isOnline: status.status === 'success',
          info: status
        });
      } catch (error) {
        console.error('检查服务器状态失败:', error);
        setServerStatus({
          checked: true,
          isOnline: false,
          error: error.message
        });
      }
    };

    checkServerStatus();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* 顶部导航栏 */}
          <AppBar
            position="fixed"
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
              boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={toggleDrawer}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                虚假评论预测系统
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{
                  display: 'flex',
                  alignItems: 'center',
                  mr: 2,
                  backgroundColor: serverStatus.isOnline ? 'success.main' : 'error.main',
                  color: 'white',
                  borderRadius: 1,
                  px: 1,
                  py: 0.5,
                  fontSize: '0.75rem',
                  fontWeight: 'medium'
                }}>
                  {serverStatus.isOnline ? '服务在线' : '服务离线'}
                </Box>
                <Brightness4Icon sx={{ mr: 1 }} />
                <Switch
                  checked={darkMode}
                  onChange={toggleDarkMode}
                  color="default"
                />
              </Box>
            </Toolbar>
          </AppBar>

          {/* 侧边导航抽屉 */}
          <Drawer
            variant="temporary"
            open={drawerOpen}
            onClose={toggleDrawer}
            sx={{
              width: 240,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: 240,
                boxSizing: 'border-box',
                pt: (theme) => `${theme.mixins.toolbar.minHeight}px`,
              },
            }}
          >
            <Box sx={{ overflow: 'auto', pt: 2 }}>
              <List>
                <ListItem
                  button
                  component={Link}
                  to="/upload"
                  onClick={toggleDrawer}
                >
                  <ListItemIcon>
                    <UploadIcon />
                  </ListItemIcon>
                  <ListItemText primary="数据上传" />
                </ListItem>
                <ListItem
                  button
                  component={Link}
                  to="/visualization"
                  onClick={toggleDrawer}
                >
                  <ListItemIcon>
                    <BarChartIcon />
                  </ListItemIcon>
                  <ListItemText primary="数据可视化" />
                </ListItem>
                <ListItem
                  button
                  component={Link}
                  to="/prediction"
                  onClick={toggleDrawer}
                >
                  <ListItemIcon>
                    <DashboardIcon />
                  </ListItemIcon>
                  <ListItemText primary="预测分析" />
                </ListItem>
              </List>
              <Divider />
              <List>
                <ListItem button>
                  <ListItemIcon>
                    <HistoryIcon />
                  </ListItemIcon>
                  <ListItemText primary="历史记录" />
                </ListItem>
                <ListItem button>
                  <ListItemIcon>
                    <SettingsIcon />
                  </ListItemIcon>
                  <ListItemText primary="系统设置" />
                </ListItem>
              </List>
            </Box>
          </Drawer>

          {/* 主内容区 */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              bgcolor: 'background.default',
              p: 3,
              pt: (theme) => `calc(${theme.mixins.toolbar.minHeight}px + 24px)`,
              width: '100%'
            }}
          >
            <Routes>
              <Route path="/upload" element={<DataUploadPage />} />
              <Route path="/visualization" element={<DataVisualizationPage />} />
              <Route path="/prediction" element={<PredictionPage />} />
              <Route path="/" element={<Navigate to="/upload" replace />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;