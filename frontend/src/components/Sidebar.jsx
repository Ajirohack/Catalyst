import React from "react";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
  Avatar,
  Chip,
  IconButton,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Add as AddIcon,
  PlayArrow as ContinueIcon,
  Timeline as TimelineIcon,
  Analytics as AnalyticsIcon,
  Psychology as WhisperIcon,
  Favorite as HeartIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

const DRAWER_WIDTH = 280;

const navigationItems = [
  {
    text: "Dashboard",
    icon: <DashboardIcon />,
    path: "/dashboard",
    color: "#6366f1",
  },
  {
    text: "New Project",
    icon: <AddIcon />,
    path: "/new-project",
    color: "#10b981",
  },
  {
    text: "Continue Project",
    icon: <ContinueIcon />,
    path: "/continue-project",
    color: "#f59e0b",
  },
  {
    text: "Timeline",
    icon: <TimelineIcon />,
    path: "/timeline",
    color: "#8b5cf6",
  },
  {
    text: "Analytics",
    icon: <AnalyticsIcon />,
    path: "/analytics",
    color: "#06b6d4",
  },
];

const Sidebar = ({ onWhisperToggle, selectedProject, onProjectSelect }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          backgroundColor: "#ffffff",
          borderRight: "1px solid #e2e8f0",
          boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
        },
      }}
    >
      {/* Logo and Brand */}
      <Box sx={{ p: 3, textAlign: "center" }}>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: "primary.main",
              margin: "0 auto 16px",
            }}
          >
            <HeartIcon sx={{ fontSize: 28 }} />
          </Avatar>
          <Typography variant="h5" fontWeight="bold" color="primary">
            Catalyst
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Relationship Intelligence
          </Typography>
        </motion.div>
      </Box>

      <Divider />

      {/* Navigation */}
      <List sx={{ px: 2, py: 1 }}>
        {navigationItems.map((item, index) => {
          const isActive = location.pathname === item.path;

          return (
            <motion.div
              key={item.text}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <ListItem disablePadding sx={{ mb: 1 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    py: 1.5,
                    backgroundColor: isActive ? "primary.main" : "transparent",
                    color: isActive ? "white" : "text.primary",
                    "&:hover": {
                      backgroundColor: isActive ? "primary.dark" : "grey.100",
                    },
                    transition: "all 0.2s ease-in-out",
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive ? "white" : item.color,
                      minWidth: 40,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontWeight: isActive ? 600 : 500,
                      fontSize: "0.95rem",
                    }}
                  />
                </ListItemButton>
              </ListItem>
            </motion.div>
          );
        })}
      </List>

      <Divider sx={{ mx: 2 }} />

      {/* Whisper Panel Toggle */}
      <Box sx={{ px: 2, py: 1 }}>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <ListItemButton
            onClick={onWhisperToggle}
            sx={{
              borderRadius: 2,
              py: 1.5,
              backgroundColor: "secondary.light",
              color: "white",
              "&:hover": {
                backgroundColor: "secondary.main",
              },
            }}
          >
            <ListItemIcon sx={{ color: "white", minWidth: 40 }}>
              <WhisperIcon />
            </ListItemIcon>
            <ListItemText
              primary="AI Whisper"
              secondary="Real-time coaching"
              primaryTypographyProps={{
                fontWeight: 600,
                fontSize: "0.95rem",
              }}
              secondaryTypographyProps={{
                color: "rgba(255, 255, 255, 0.8)",
                fontSize: "0.8rem",
              }}
            />
          </ListItemButton>
        </motion.div>
      </Box>

      {/* Current Project */}
      {selectedProject && (
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
            Current Project
          </Typography>
          <Box
            sx={{
              p: 2,
              backgroundColor: "grey.50",
              borderRadius: 2,
              border: "1px solid #e2e8f0",
            }}
          >
            <Typography variant="body2" fontWeight={600} noWrap>
              {selectedProject.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {selectedProject.participants?.join(", ")}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip
                label={selectedProject.status}
                size="small"
                color={
                  selectedProject.status === "active" ? "success" : "default"
                }
                sx={{ fontSize: "0.7rem" }}
              />
            </Box>
          </Box>
        </Box>
      )}

      {/* Bottom Actions */}
      <Box sx={{ mt: "auto", p: 2 }}>
        <List>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 2 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <SettingsIcon color="action" />
              </ListItemIcon>
              <ListItemText
                primary="Settings"
                primaryTypographyProps={{ fontSize: "0.9rem" }}
              />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 2 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <HelpIcon color="action" />
              </ListItemIcon>
              <ListItemText
                primary="Help & Support"
                primaryTypographyProps={{ fontSize: "0.9rem" }}
              />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
