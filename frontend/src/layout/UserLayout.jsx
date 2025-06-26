import React from "react";
import { Outlet, Link } from "react-router-dom";
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Button,
  Typography,
  Divider,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Add as AddIcon,
  PlayArrow as ContinueIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  LibraryBooks as KnowledgeIcon,
} from "@mui/icons-material";

const drawerWidth = 240;

const menuItems = [
  { text: "Dashboard", path: "/dashboard", icon: <DashboardIcon /> },
  { text: "New Project", path: "/new-project", icon: <AddIcon /> },
  { text: "Continue", path: "/continue", icon: <ContinueIcon /> },
  { text: "Knowledge Base", path: "/knowledge-base", icon: <KnowledgeIcon /> },
  { text: "Settings", path: "/settings", icon: <SettingsIcon /> },
];

export default function UserLayout() {
  // Removed unused navigate variable

  const handleLogout = () => {
    // TODO: Implement actual logout logic
    console.log("Logout clicked");
  };

  return (
    <Box sx={{ display: "flex", height: "100vh" }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            bgcolor: "grey.900",
            color: "white",
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" component="div">
            Catalyst
          </Typography>
        </Box>
        <Divider sx={{ borderColor: "grey.700" }} />
        <List sx={{ flexGrow: 1 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                component={Link}
                to={item.path}
                sx={{
                  color: "white",
                  "&:hover": {
                    bgcolor: "grey.800",
                  },
                }}
              >
                <ListItemIcon sx={{ color: "white" }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Box sx={{ p: 2 }}>
          <Button
            fullWidth
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
            sx={{
              color: "white",
              justifyContent: "flex-start",
              "&:hover": {
                bgcolor: "grey.800",
              },
            }}
          >
            Logout
          </Button>
        </Box>
      </Drawer>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          overflow: "auto",
          bgcolor: "grey.50",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
