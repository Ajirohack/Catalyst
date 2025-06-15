import React from "react";
import {
  Box,
  Paper,
  Typography,
  // TextField, // Unused import
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Grid,
} from "@mui/material";
import { motion } from "framer-motion";

export default function Settings() {
  const [settings, setSettings] = React.useState({
    notifications: true,
    darkMode: false,
    language: "en",
    autoSave: true,
  });

  const handleSettingChange = (setting, value) => {
    setSettings((prev) => ({ ...prev, [setting]: value }));
  };

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>

        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            General Settings
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications}
                    onChange={(e) =>
                      handleSettingChange("notifications", e.target.checked)
                    }
                  />
                }
                label="Enable Notifications"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.darkMode}
                    onChange={(e) =>
                      handleSettingChange("darkMode", e.target.checked)
                    }
                  />
                }
                label="Dark Mode"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={settings.language}
                  label="Language"
                  onChange={(e) =>
                    handleSettingChange("language", e.target.value)
                  }
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoSave}
                    onChange={(e) =>
                      handleSettingChange("autoSave", e.target.checked)
                    }
                  />
                }
                label="Auto Save"
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ display: "flex", gap: 2 }}>
            <Button variant="contained" color="primary">
              Save Changes
            </Button>
            <Button variant="outlined">Reset to Defaults</Button>
          </Box>
        </Paper>
      </motion.div>
    </Box>
  );
}
