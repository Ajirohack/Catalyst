import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  Button,
} from "@mui/material";
import {
  Psychology as WhisperIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const Header = ({ onWhisperToggle, whisperPanelOpen }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [notificationAnchor, setNotificationAnchor] = React.useState(null);
  const [isDarkMode, setIsDarkMode] = React.useState(false);

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const mockNotifications = [
    {
      id: 1,
      title: "New Analysis Complete",
      message: "Your communication analysis is ready",
      time: "2 min ago",
      unread: true,
    },
    {
      id: 2,
      title: "Milestone Achieved",
      message: 'You\'ve completed "Better Listening" goal',
      time: "1 hour ago",
      unread: true,
    },
    {
      id: 3,
      title: "Weekly Report",
      message: "Your relationship insights are available",
      time: "1 day ago",
      unread: false,
    },
  ];

  const unreadCount = mockNotifications.filter((n) => n.unread).length;

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: "background.paper",
        borderBottom: "1px solid #e2e8f0",
        color: "text.primary",
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", px: 3 }}>
        {/* Left side - Page title and breadcrumb */}
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Typography variant="h6" fontWeight={600} color="text.primary">
            Dashboard
          </Typography>
          <Chip
            label="Live"
            size="small"
            color="success"
            sx={{ ml: 2, fontSize: "0.7rem" }}
          />
        </Box>

        {/* Right side - Actions and user menu */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {/* Theme toggle */}
          <IconButton onClick={toggleTheme} color="inherit">
            {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>

          {/* Whisper toggle */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant={whisperPanelOpen ? "contained" : "outlined"}
              startIcon={<WhisperIcon />}
              onClick={onWhisperToggle}
              sx={{
                borderRadius: 2,
                textTransform: "none",
                fontWeight: 500,
              }}
            >
              AI Whisper
            </Button>
          </motion.div>

          {/* Notifications */}
          <IconButton
            color="inherit"
            onClick={handleNotificationMenuOpen}
            sx={{ ml: 1 }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Profile menu */}
          <IconButton onClick={handleProfileMenuOpen} sx={{ ml: 1 }}>
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: "primary.main",
                fontSize: "0.9rem",
              }}
            >
              JD
            </Avatar>
          </IconButton>
        </Box>

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationAnchor}
          open={Boolean(notificationAnchor)}
          onClose={handleNotificationMenuClose}
          PaperProps={{
            sx: {
              width: 320,
              maxHeight: 400,
              mt: 1,
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: "1px solid #e2e8f0" }}>
            <Typography variant="h6" fontWeight={600}>
              Notifications
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {unreadCount} unread notifications
            </Typography>
          </Box>

          {mockNotifications.map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={handleNotificationMenuClose}
              sx={{
                py: 2,
                borderBottom: "1px solid #f1f5f9",
                backgroundColor: notification.unread
                  ? "primary.50"
                  : "transparent",
              }}
            >
              <Box sx={{ width: "100%" }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 0.5,
                  }}
                >
                  <Typography variant="subtitle2" fontWeight={600}>
                    {notification.title}
                  </Typography>
                  {notification.unread && (
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        bgcolor: "primary.main",
                      }}
                    />
                  )}
                </Box>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 0.5 }}
                >
                  {notification.message}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {notification.time}
                </Typography>
              </Box>
            </MenuItem>
          ))}

          <Box sx={{ p: 2, textAlign: "center" }}>
            <Button size="small" color="primary">
              View All Notifications
            </Button>
          </Box>
        </Menu>

        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleProfileMenuClose}
          PaperProps={{
            sx: {
              width: 240,
              mt: 1,
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: "1px solid #e2e8f0" }}>
            <Typography variant="subtitle1" fontWeight={600}>
              John Doe
            </Typography>
            <Typography variant="body2" color="text.secondary">
              john.doe@example.com
            </Typography>
          </Box>

          <MenuItem onClick={handleProfileMenuClose}>
            <AccountIcon sx={{ mr: 2 }} />
            Profile
          </MenuItem>

          <MenuItem onClick={handleProfileMenuClose}>
            <SettingsIcon sx={{ mr: 2 }} />
            Settings
          </MenuItem>

          <Divider />

          <MenuItem onClick={handleProfileMenuClose}>
            <LogoutIcon sx={{ mr: 2 }} />
            Sign Out
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
