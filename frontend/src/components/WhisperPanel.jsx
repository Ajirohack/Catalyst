import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Fade,
  Collapse,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Close as CloseIcon,
  Minimize as MinimizeIcon,
  Maximize as MaximizeIcon,
  Psychology as PsychologyIcon,
  Send as SendIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  Favorite as FavoriteIcon,
  Warning as WarningIcon,
  Settings as SettingsIcon,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";

const WhisperPanel = ({
  isOpen,
  onClose,
  projectId,
  isMinimized,
  onToggleMinimize,
}) => {
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoSuggest, setAutoSuggest] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    if (isOpen && projectId) {
      connectWebSocket();
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [isOpen, projectId]);

  const connectWebSocket = () => {
    try {
      const wsUrl = `ws://localhost:8000/ws/whisper/${projectId}`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log("Whisper WebSocket connected");
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      websocket.onclose = () => {
        setIsConnected(false);
        console.log("Whisper WebSocket disconnected");
      };

      websocket.onerror = (error) => {
        setError("Connection failed. Please try again.");
        console.error("WebSocket error:", error);
      };

      setWs(websocket);
    } catch (err) {
      setError("Failed to connect to Whisper service.");
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case "suggestion":
        const newSuggestion = {
          id: Date.now(),
          content: data.content,
          confidence: data.confidence,
          category: data.category,
          timestamp: new Date(data.timestamp),
        };
        setSuggestions((prev) => [newSuggestion, ...prev.slice(0, 9)]); // Keep last 10
        break;
      case "pong":
        // Handle ping/pong for connection health
        break;
      case "error":
        setError(data.content);
        break;
      default:
        console.log("Unknown message type:", data.type);
    }
  };

  const sendMessage = () => {
    if (!ws || !currentMessage.trim()) return;

    setIsLoading(true);
    const message = {
      type: "message",
      content: currentMessage,
      project_id: projectId,
      timestamp: new Date().toISOString(),
    };

    ws.send(JSON.stringify(message));
    setCurrentMessage("");
    setIsLoading(false);
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getSuggestionIcon = (category) => {
    switch (category) {
      case "positive_reinforcement":
        return <FavoriteIcon color="success" />;
      case "conflict_resolution":
        return <WarningIcon color="warning" />;
      case "engagement":
        return <TrendingUpIcon color="primary" />;
      default:
        return <LightbulbIcon color="info" />;
    }
  };

  const getSuggestionColor = (category) => {
    switch (category) {
      case "positive_reinforcement":
        return "success";
      case "conflict_resolution":
        return "warning";
      case "engagement":
        return "primary";
      default:
        return "info";
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [suggestions]);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 20 }}
      transition={{ duration: 0.2 }}
      style={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: isMinimized ? 300 : 400,
        height: isMinimized ? 60 : 500,
        zIndex: 1300,
      }}
    >
      <Paper
        elevation={8}
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          borderRadius: 3,
          overflow: "hidden",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(10px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <PsychologyIcon sx={{ color: "white" }} />
            <Typography variant="h6" sx={{ color: "white", fontWeight: 600 }}>
              Catalyst Whisper
            </Typography>
            <Chip
              label={isConnected ? "Connected" : "Disconnected"}
              color={isConnected ? "success" : "error"}
              size="small"
              sx={{ ml: 1 }}
            />
          </Box>

          <Box>
            <IconButton
              size="small"
              onClick={() => setShowSettings(!showSettings)}
              sx={{ color: "white", mr: 0.5 }}
            >
              <SettingsIcon fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              onClick={onToggleMinimize}
              sx={{ color: "white", mr: 0.5 }}
            >
              {isMinimized ? (
                <MaximizeIcon fontSize="small" />
              ) : (
                <MinimizeIcon fontSize="small" />
              )}
            </IconButton>
            <IconButton size="small" onClick={onClose} sx={{ color: "white" }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>

        <Collapse in={!isMinimized}>
          {/* Settings Panel */}
          <Collapse in={showSettings}>
            <Box sx={{ p: 2, bgcolor: "rgba(255, 255, 255, 0.05)" }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoSuggest}
                    onChange={(e) => setAutoSuggest(e.target.checked)}
                    size="small"
                  />
                }
                label="Auto-suggest"
                sx={{ color: "white" }}
              />
            </Box>
            <Divider sx={{ bgcolor: "rgba(255, 255, 255, 0.1)" }} />
          </Collapse>

          {/* Error Display */}
          {error && (
            <Box sx={{ p: 1 }}>
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            </Box>
          )}

          {/* Suggestions List */}
          <Box
            sx={{
              flexGrow: 1,
              overflow: "auto",
              p: 1,
              "&::-webkit-scrollbar": {
                width: "6px",
              },
              "&::-webkit-scrollbar-track": {
                background: "rgba(255, 255, 255, 0.1)",
              },
              "&::-webkit-scrollbar-thumb": {
                background: "rgba(255, 255, 255, 0.3)",
                borderRadius: "3px",
              },
            }}
          >
            {suggestions.length === 0 ? (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  color: "rgba(255, 255, 255, 0.7)",
                  textAlign: "center",
                  p: 2,
                }}
              >
                <PsychologyIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
                <Typography variant="body2">
                  Send a message to get AI-powered relationship coaching
                  suggestions
                </Typography>
              </Box>
            ) : (
              <List sx={{ p: 0 }}>
                <AnimatePresence>
                  {suggestions.map((suggestion) => (
                    <motion.div
                      key={suggestion.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.2 }}
                    >
                      <ListItem
                        sx={{
                          mb: 1,
                          bgcolor: "rgba(255, 255, 255, 0.1)",
                          borderRadius: 2,
                          backdropFilter: "blur(10px)",
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {getSuggestionIcon(suggestion.category)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography
                              variant="body2"
                              sx={{ color: "white", fontWeight: 500 }}
                            >
                              {suggestion.content}
                            </Typography>
                          }
                          secondary={
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                                mt: 0.5,
                              }}
                            >
                              <Chip
                                label={suggestion.category?.replace("_", " ")}
                                color={getSuggestionColor(suggestion.category)}
                                size="small"
                                sx={{ fontSize: "0.7rem", height: 20 }}
                              />
                              {suggestion.confidence && (
                                <Typography
                                  variant="caption"
                                  sx={{ color: "rgba(255, 255, 255, 0.7)" }}
                                >
                                  {Math.round(suggestion.confidence * 100)}%
                                  confidence
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </List>
            )}
          </Box>

          {/* Input Area */}
          <Box
            sx={{
              p: 2,
              background: "rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(10px)",
            }}
          >
            <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                placeholder="Type a message to get coaching suggestions..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={!isConnected || isLoading}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    color: "white",
                    "& fieldset": {
                      borderColor: "rgba(255, 255, 255, 0.3)",
                    },
                    "&:hover fieldset": {
                      borderColor: "rgba(255, 255, 255, 0.5)",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "white",
                    },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "rgba(255, 255, 255, 0.7)",
                    opacity: 1,
                  },
                }}
              />
              <IconButton
                onClick={sendMessage}
                disabled={!isConnected || isLoading || !currentMessage.trim()}
                sx={{
                  color: "white",
                  bgcolor: "rgba(255, 255, 255, 0.2)",
                  "&:hover": {
                    bgcolor: "rgba(255, 255, 255, 0.3)",
                  },
                  "&.Mui-disabled": {
                    color: "rgba(255, 255, 255, 0.3)",
                  },
                }}
              >
                {isLoading ? (
                  <CircularProgress size={20} sx={{ color: "white" }} />
                ) : (
                  <SendIcon />
                )}
              </IconButton>
            </Box>
          </Box>
        </Collapse>
      </Paper>
    </motion.div>
  );
};

export default WhisperPanel;
