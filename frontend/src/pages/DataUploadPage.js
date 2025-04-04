import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import FileUploadForm from '../components/FileUploadForm';
import StatusAlert from '../components/StatusAlert';

const DataUploadPage = () => {
  const navigate = useNavigate();
  const [fileData, setFileData] = useState(() => {
    // 尝试从sessionStorage读取之前上传的文件信息
    const savedFileData = sessionStorage.getItem('uploadedFileData');
    return savedFileData ? JSON.parse(savedFileData) : null;
  });
  const [alert, setAlert] = useState({ show: false, severity: 'info', message: '' });

  const handleFileUpload = (data) => {
    if (data === null) {
      // 清除sessionStorage和状态
      sessionStorage.removeItem('uploadedFileData');
      setFileData(null);
      return;
    }

    // 保存到sessionStorage
    sessionStorage.setItem('uploadedFileData', JSON.stringify(data));
    setFileData(data);
    setAlert({
      show: true,
      severity: 'success',
      message: '文件上传成功，可以进行数据可视化'
    });
  };

  const handleNavigateToVisualization = () => {
    // 携带文件数据跳转到可视化页面
    navigate('/visualization');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" color="primary">
        数据上传
      </Typography>
      <Divider sx={{ mb: 4 }} />

      <StatusAlert
        open={alert.show}
        severity={alert.severity}
        message={alert.message}
        onClose={() => setAlert({ ...alert, show: false })}
      />

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              上传数据文件
            </Typography>
            <FileUploadForm
              onFileUpload={handleFileUpload}
              loading={false}
              fileData={fileData}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              文件信息
            </Typography>
            {fileData ? (
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="文件名"
                        secondary={fileData.original_name}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="文件大小"
                        secondary={`${Math.round(fileData.size/1024)} KB`}
                      />
                    </ListItem>
                    {fileData.info && (
                      <>
                        <ListItem>
                          <ListItemText
                            primary="包含产品数"
                            secondary={fileData.info.products || '未知'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="数据范围"
                            secondary={fileData.info.date_range
                              ? `${fileData.info.date_range.min} 至 ${fileData.info.date_range.max}`
                              : '未知'}
                          />
                        </ListItem>
                      </>
                    )}
                  </List>
                </CardContent>
              </Card>
            ) : (
              <Box sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                flexGrow: 1
              }}>
                <Typography variant="body2" color="text.secondary">
                  请先上传数据文件
                </Typography>
              </Box>
            )}

            {fileData && (
              <Box sx={{ mt: 'auto' }}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  onClick={handleNavigateToVisualization}
                >
                  查看数据可视化
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DataUploadPage;