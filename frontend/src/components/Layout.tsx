import React from 'react';
import { Container, AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Portfolio', path: '/portfolio' },
    { label: 'Alerts', path: '/alerts' },
    { label: 'Predictions', path: '/predictions' },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ backgroundColor: '#1a1f35' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, color: '#00bcd4' }}>
            Financial Analytics Dashboard
          </Typography>
          {menuItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              onClick={() => navigate(item.path)}
              sx={{
                color: location.pathname === item.path ? '#00bcd4' : 'white',
                mx: 1,
              }}
            >
              {item.label}
            </Button>
          ))}
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;
