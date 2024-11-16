import React from 'react';
import { AppBar, Toolbar, IconButton, Box, Tooltip, Button, Typography } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { SettingsApplications, Storage, Task, Home, School, DocumentScanner, Forum } from '@mui/icons-material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../../../contexts/AuthContext';
import useStyles from './HeaderStyles';
import Logger from '../../../utils/Logger';

interface NavGroupProps {
  groupIndex: 1 | 2 | 3;
  children: React.ReactNode;
}

const Header: React.FC = () => {
  const classes = useStyles();
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();

  const handleNavigation = (path: string): void => {
    navigate(path);
  };

  const handleLogout = (): void => {
    Logger.info('Logging out');
    logout();
    navigate('/login');
  };

  const isActive = (path: string): boolean => {
    if (path === '/knowledgebase') {
      return location.pathname.startsWith(path);
    }
    return location.pathname === path;
  };

  const NavGroup: React.FC<NavGroupProps> = ({ groupIndex, children }) => (
    <Box className={`${classes.navGroup} ${classes[`group${groupIndex}`]}`}>
      {children}
    </Box>
  );

  return (
    <AppBar position="static" className={classes.header}>
      <Toolbar className={classes.toolbar}>
        <Box className={classes.leftSection}>
          <Tooltip title="Home">
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => handleNavigation('/')}
              className={isActive('/') ? classes.activeButton : ''}
            >
              <Home />
            </IconButton>
          </Tooltip>
        </Box>
        
        {isAuthenticated && (
          <Box className={classes.centerSection}>
            <NavGroup groupIndex={1}>
              <Tooltip title="Chat with Alice">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/chat-alice')}
                  className={isActive('/chat-alice') ? classes.activeButton : ''}
                >
                  <Forum />
                </IconButton>
              </Tooltip>
              <Tooltip title="Execute tasks">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/start-task')}
                  className={isActive('/start-task') ? classes.activeButton : ''}
                >
                  <Task />
                </IconButton>
              </Tooltip>
            </NavGroup>

            <NavGroup groupIndex={2}>
              <Tooltip title="Edit structures">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/structures')}
                  className={isActive('/structures') ? classes.activeButton : ''}
                >
                  <Storage />
                </IconButton>
              </Tooltip>
              <Tooltip title="View references">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/references')}
                  className={isActive('/references') ? classes.activeButton : ''}
                >
                  <DocumentScanner />
                </IconButton>
              </Tooltip>
            </NavGroup>

            <NavGroup groupIndex={3}>
              <Tooltip title="Learn">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/knowledgebase')}
                  className={isActive('/knowledgebase') ? classes.activeButton : ''}
                >
                  <School />
                </IconButton>
              </Tooltip>
            </NavGroup>
          </Box>
        )}

        <Box className={classes.rightSection}>
          {isAuthenticated ? (
            <>
              <Typography variant="body1" className={classes.userEmail}>
                {user?.email}
              </Typography>
              <Tooltip title="User Settings">
                <IconButton
                  color="inherit"
                  onClick={() => handleNavigation('/user-settings')}
                  className={isActive('/user-settings') ? classes.activeButton : ''}
                >
                  <SettingsApplications />
                </IconButton>
              </Tooltip>
              <Tooltip title="Logout">
                <IconButton color="inherit" onClick={handleLogout}>
                  <LogoutIcon />
                </IconButton>
              </Tooltip>
            </>
          ) : (
            <Button color="inherit" onClick={() => handleNavigation('/login')}>
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;