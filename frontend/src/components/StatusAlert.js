// src/components/StatusAlert.js
import React from 'react';
import { Alert, Snackbar, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';

const StatusAlert = ({ open, severity, message, onClose, duration = 6000 }) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={duration}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert
        severity={severity}
        variant="filled"
        action={
          <IconButton
            size="small"
            color="inherit"
            onClick={onClose}
          >
            <Close fontSize="small" />
          </IconButton>
        }
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default StatusAlert;