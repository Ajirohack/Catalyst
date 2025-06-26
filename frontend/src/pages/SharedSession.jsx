import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  Tab,
  Tabs,
} from "@mui/material";
import {
  Send as SendIcon,
  VideoCall as VideoCallIcon,
  ScreenShare as ScreenShareIcon,
  Assignment as AssignmentIcon,
  PictureAsPdf as PdfIcon,
  InsertDriveFile as FileIcon,
  Group as GroupIcon,
  Chat as ChatIcon,
  Description as DocumentIcon,
  Analytics as AnalyticsIcon,
  ExitToApp as ExitIcon,
  ArrowBack as BackIcon,
} from "@mui/icons-material";
import { format } from "date-fns";

// API URL
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const SharedSession = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [currentTab, setCurrentTab] = useState(0);
  const [activeDocument, setActiveDocument] = useState(null);
  const [documentContent, setDocumentContent] = useState("");
  const [isEditingDocument, setIsEditingDocument] = useState(false);
  const [webSocketConnected, setWebSocketConnected] = useState(false);

  const websocketRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messageListRef = useRef(null);

  // Mock user data - in a real app, this would come from auth context
  const currentUser = {
    id: "test-user-123",
    name: "Test User",
    email: "test@example.com",
    role: "therapist",
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  // Fetch session data
  const fetchSessionData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_URL}/api/collaboration/sessions/${sessionId}`
      );
      setSession(response.data);
      setParticipants(response.data.participants);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching session:", err);
      setError("Failed to load session data. Please try again later.");
      setLoading(false);
      toast.error("Failed to load session data");
    }
  }, [sessionId]);

  // Fetch messages
  const fetchMessages = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/collaboration/sessions/${sessionId}/messages`
      );
      setMessages(response.data);
    } catch (err) {
      console.error("Error fetching messages:", err);
      toast.error("Failed to load messages");
    }
  }, [sessionId]);

  // Fetch documents
  const fetchDocuments = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/collaboration/sessions/${sessionId}/documents`
      );
      setDocuments(response.data);
    } catch (err) {
      console.error("Error fetching documents:", err);
      toast.error("Failed to load documents");
    }
  }, [sessionId]);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    // Close existing connection if any
    if (
      websocketRef.current &&
      websocketRef.current.readyState === WebSocket.OPEN
    ) {
      websocketRef.current.close();
    }

    // Create new connection
    const wsUrl = `${API_URL.replace("http", "ws")}/api/collaboration/ws/${sessionId}?client_id=${currentUser.id}`;
    websocketRef.current = new WebSocket(wsUrl);

    websocketRef.current.onopen = () => {
      console.log("WebSocket connected");
      setWebSocketConnected(true);
      toast.success("Connected to session");
    };

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message received:", data);

      // Handle different message types
      if (data.type === "new_message") {
        setMessages((prevMessages) => [...prevMessages, data.data]);
      } else if (
        data.type === "participant_joined" ||
        data.type === "participant_left"
      ) {
        // Refresh participants list
        fetchSessionData();

        // Show notification
        const action = data.type === "participant_joined" ? "joined" : "left";
        toast.info(`${data.data.participant_name} has ${action} the session`);
      } else if (data.type === "document_updated") {
        // Refresh documents if the active document was updated
        if (activeDocument && activeDocument.id === data.data.document_id) {
          fetchDocumentContent(data.data.document_id);
        }
        fetchDocuments();
      } else if (data.type === "status_change") {
        // Refresh session data on status change
        fetchSessionData();
        toast.info(`Session status changed to ${data.data.status}`);
      }
    };

    websocketRef.current.onclose = (event) => {
      console.log("WebSocket disconnected:", event);
      setWebSocketConnected(false);

      // Attempt to reconnect after a delay, if not explicitly closed
      if (!event.wasClean) {
        setTimeout(() => {
          if (document.visibilityState !== "hidden") {
            connectWebSocket();
          }
        }, 5000);
      }
    };

    websocketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      toast.error("Connection error. Trying to reconnect...");
    };

    // Ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (
        websocketRef.current &&
        websocketRef.current.readyState === WebSocket.OPEN
      ) {
        websocketRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [sessionId, currentUser.id, fetchSessionData, fetchDocumentContent]);

  // Start session
  const startSession = async () => {
    try {
      await axios.post(
        `${API_URL}/api/collaboration/sessions/${sessionId}/start`
      );
      toast.success("Session started");
      fetchSessionData();
    } catch (err) {
      console.error("Error starting session:", err);
      toast.error("Failed to start session");
    }
  };

  // End session
  const endSession = async () => {
    if (!window.confirm("Are you sure you want to end this session?")) {
      return;
    }

    try {
      await axios.post(
        `${API_URL}/api/collaboration/sessions/${sessionId}/end`
      );
      toast.success("Session ended");
      fetchSessionData();
    } catch (err) {
      console.error("Error ending session:", err);
      toast.error("Failed to end session");
    }
  };

  // Send message
  const sendMessage = async (e) => {
    e.preventDefault();

    if (!newMessage.trim()) return;

    try {
      await axios.post(
        `${API_URL}/api/collaboration/sessions/${sessionId}/messages`,
        {
          content: newMessage,
          content_type: "text",
        }
      );

      setNewMessage("");
    } catch (err) {
      console.error("Error sending message:", err);
      toast.error("Failed to send message");
    }
  };

  // Create document
  const createDocument = async () => {
    const title = prompt("Enter document title:");
    if (!title) return;

    try {
      const response = await axios.post(
        `${API_URL}/api/collaboration/sessions/${sessionId}/documents`,
        {
          title,
          content: "",
          content_type: "text",
        }
      );

      toast.success("Document created");
      fetchDocuments();
      setActiveDocument(response.data);
      setDocumentContent("");
      setIsEditingDocument(true);
      setCurrentTab(1); // Switch to Documents tab
    } catch (err) {
      console.error("Error creating document:", err);
      toast.error("Failed to create document");
    }
  };

  // Fetch document content
  const fetchDocumentContent = async (documentId) => {
    try {
      const response = await axios.get(
        `${API_URL}/api/collaboration/sessions/${sessionId}/documents/${documentId}`
      );
      setActiveDocument(response.data);
      setDocumentContent(response.data.content);
    } catch (err) {
      console.error("Error fetching document:", err);
      toast.error("Failed to load document");
    }
  };

  // Update document
  const updateDocument = async () => {
    if (!activeDocument) return;

    try {
      await axios.put(
        `${API_URL}/api/collaboration/sessions/${sessionId}/documents/${activeDocument.id}`,
        {
          title: activeDocument.title,
          content: documentContent,
          content_type: activeDocument.content_type,
        }
      );

      setIsEditingDocument(false);
      toast.success("Document updated");
    } catch (err) {
      console.error("Error updating document:", err);
      toast.error("Failed to update document");
    }
  };

  // Leave session
  const leaveSession = () => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }
    navigate("/dashboard");
  };

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Initial data loading
  useEffect(() => {
    fetchSessionData();
    fetchMessages();
    fetchDocuments();
    connectWebSocket();

    // Cleanup function
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [fetchSessionData, fetchMessages, fetchDocuments, connectWebSocket]);

  // Status indicator
  const getStatusChip = (status) => {
    const statusColors = {
      scheduled: "default",
      active: "success",
      paused: "warning",
      ended: "error",
      archived: "default",
    };

    return (
      <Chip
        label={status.toUpperCase()}
        color={statusColors[status] || "default"}
        size="small"
        sx={{ ml: 1 }}
      />
    );
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <Paper elevation={3} sx={{ p: 4, maxWidth: 500 }}>
          <Typography variant="h5" color="error" gutterBottom>
            Error
          </Typography>
          <Typography paragraph>{error}</Typography>
          <Button
            variant="contained"
            startIcon={<BackIcon />}
            onClick={() => navigate("/dashboard")}
          >
            Back to Dashboard
          </Button>
        </Paper>
      </Box>
    );
  }

  if (!session) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <Typography>Session not found</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" component="h1">
              {session.title} {getStatusChip(session.status)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {session.session_type} session •{" "}
              {format(new Date(session.created_at), "PPP")}
            </Typography>
          </Box>
          <Box>
            {session.status === "scheduled" &&
              session.host_id === currentUser.id && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={startSession}
                  sx={{ mr: 1 }}
                >
                  Start Session
                </Button>
              )}

            {session.status === "active" &&
              session.host_id === currentUser.id && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={endSession}
                  sx={{ mr: 1 }}
                >
                  End Session
                </Button>
              )}

            <Button
              variant="outlined"
              startIcon={<ExitIcon />}
              onClick={leaveSession}
            >
              Leave
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Connection Status */}
      <Box sx={{ mb: 2 }}>
        <Chip
          label={webSocketConnected ? "Connected" : "Disconnected"}
          color={webSocketConnected ? "success" : "error"}
          size="small"
        />
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Sidebar - Participants */}
        <Grid item xs={12} md={3}>
          <Paper elevation={1} sx={{ p: 2, height: "70vh", overflow: "auto" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              <GroupIcon
                fontSize="small"
                sx={{ verticalAlign: "middle", mr: 1 }}
              />
              Participants ({participants.length})
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List dense>
              {/* Host */}
              <ListItem>
                <Avatar sx={{ mr: 1, bgcolor: "primary.main" }}>
                  {session.host_id === currentUser.id ? "Me" : "H"}
                </Avatar>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight="bold">
                      {session.host_id === currentUser.id
                        ? "You (Host)"
                        : "Host"}
                    </Typography>
                  }
                />
              </ListItem>

              {/* Other participants */}
              {participants.map((participant) => (
                <ListItem key={participant.id}>
                  <Avatar sx={{ mr: 1, bgcolor: "secondary.light" }}>
                    {participant.id === currentUser.id
                      ? "Me"
                      : participant.name.charAt(0)}
                  </Avatar>
                  <ListItemText
                    primary={
                      <Typography variant="body2">
                        {participant.id === currentUser.id
                          ? "You"
                          : participant.name}
                      </Typography>
                    }
                    secondary={participant.role}
                  />
                  <Chip
                    label={participant.is_active ? "Online" : "Offline"}
                    size="small"
                    color={participant.is_active ? "success" : "default"}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Main Content Area */}
        <Grid item xs={12} md={9}>
          <Paper
            elevation={1}
            sx={{ height: "70vh", display: "flex", flexDirection: "column" }}
          >
            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs value={currentTab} onChange={handleTabChange}>
                <Tab label="Chat" icon={<ChatIcon />} iconPosition="start" />
                <Tab
                  label="Documents"
                  icon={<DocumentIcon />}
                  iconPosition="start"
                />
                <Tab
                  label="Analytics"
                  icon={<AnalyticsIcon />}
                  iconPosition="start"
                />
              </Tabs>
            </Box>

            {/* Chat Tab */}
            <Box
              sx={{
                display: currentTab === 0 ? "flex" : "none",
                flexDirection: "column",
                flexGrow: 1,
                height: "100%",
              }}
            >
              {/* Messages List */}
              <Box
                ref={messageListRef}
                sx={{
                  flexGrow: 1,
                  overflowY: "auto",
                  p: 2,
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {messages.length === 0 ? (
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      height: "100%",
                    }}
                  >
                    <ChatIcon
                      sx={{ fontSize: 60, color: "text.disabled", mb: 2 }}
                    />
                    <Typography variant="body1" color="text.secondary">
                      No messages yet. Start the conversation!
                    </Typography>
                  </Box>
                ) : (
                  messages.map((message, index) => (
                    <Box
                      key={index}
                      sx={{
                        alignSelf:
                          message.sender_id === currentUser.id
                            ? "flex-end"
                            : "flex-start",
                        mb: 2,
                        maxWidth: "70%",
                      }}
                    >
                      <Box sx={{ display: "flex", alignItems: "flex-start" }}>
                        {message.sender_id !== currentUser.id && (
                          <Avatar
                            sx={{
                              width: 32,
                              height: 32,
                              mr: 1,
                              bgcolor: "secondary.light",
                            }}
                          >
                            {message.sender_name.charAt(0)}
                          </Avatar>
                        )}

                        <Box>
                          {message.sender_id !== currentUser.id && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {message.sender_name} ({message.sender_role})
                            </Typography>
                          )}

                          <Paper
                            elevation={0}
                            sx={{
                              p: 1.5,
                              borderRadius: 2,
                              bgcolor:
                                message.sender_id === currentUser.id
                                  ? "primary.light"
                                  : "grey.100",
                              color:
                                message.sender_id === currentUser.id
                                  ? "white"
                                  : "inherit",
                            }}
                          >
                            <Typography variant="body2">
                              {message.content}
                            </Typography>
                          </Paper>

                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ ml: 1 }}
                          >
                            {format(new Date(message.timestamp), "p")}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  ))
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Message Input */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
                <form onSubmit={sendMessage}>
                  <Box sx={{ display: "flex" }}>
                    <TextField
                      fullWidth
                      placeholder="Type a message..."
                      variant="outlined"
                      size="small"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      disabled={session.status !== "active"}
                    />
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      sx={{ ml: 1 }}
                      disabled={
                        !newMessage.trim() || session.status !== "active"
                      }
                      endIcon={<SendIcon />}
                    >
                      Send
                    </Button>
                  </Box>
                </form>
              </Box>
            </Box>

            {/* Documents Tab */}
            <Box
              sx={{
                display: currentTab === 1 ? "flex" : "none",
                flexDirection: "column",
                height: "100%",
                p: 2,
                flexGrow: 1,
              }}
            >
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}
              >
                <Typography variant="h6">Shared Documents</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<FileIcon />}
                  onClick={createDocument}
                  disabled={session.status !== "active"}
                >
                  New Document
                </Button>
              </Box>

              <Box sx={{ display: "flex", height: "100%" }}>
                {/* Document List */}
                <Box
                  sx={{
                    width: 250,
                    borderRight: 1,
                    borderColor: "divider",
                    pr: 2,
                    overflowY: "auto",
                  }}
                >
                  <List dense>
                    {documents.length === 0 ? (
                      <ListItem>
                        <ListItemText primary="No documents yet" />
                      </ListItem>
                    ) : (
                      documents.map((doc) => (
                        <ListItem
                          key={doc.id}
                          button
                          selected={
                            activeDocument && activeDocument.id === doc.id
                          }
                          onClick={() => fetchDocumentContent(doc.id)}
                        >
                          <DocumentIcon
                            sx={{ mr: 1, color: "text.secondary" }}
                            fontSize="small"
                          />
                          <ListItemText
                            primary={doc.title}
                            secondary={`Updated: ${format(new Date(doc.updated_at), "PP")}`}
                          />
                        </ListItem>
                      ))
                    )}
                  </List>
                </Box>

                {/* Document Content */}
                <Box
                  sx={{
                    flexGrow: 1,
                    pl: 2,
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  {activeDocument ? (
                    <>
                      <Box
                        sx={{
                          mb: 2,
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Typography variant="h6">
                          {activeDocument.title}
                        </Typography>
                        <Box>
                          {isEditingDocument ? (
                            <>
                              <Button
                                variant="contained"
                                size="small"
                                onClick={updateDocument}
                                sx={{ mr: 1 }}
                              >
                                Save
                              </Button>
                              <Button
                                variant="outlined"
                                size="small"
                                onClick={() => setIsEditingDocument(false)}
                              >
                                Cancel
                              </Button>
                            </>
                          ) : (
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => setIsEditingDocument(true)}
                              disabled={session.status !== "active"}
                            >
                              Edit
                            </Button>
                          )}
                        </Box>
                      </Box>

                      <Box sx={{ flexGrow: 1 }}>
                        {isEditingDocument ? (
                          <TextField
                            fullWidth
                            multiline
                            rows={20}
                            variant="outlined"
                            value={documentContent}
                            onChange={(e) => setDocumentContent(e.target.value)}
                          />
                        ) : (
                          <Paper
                            variant="outlined"
                            sx={{
                              p: 2,
                              height: "100%",
                              overflowY: "auto",
                              whiteSpace: "pre-wrap",
                            }}
                          >
                            {documentContent || "This document is empty."}
                          </Paper>
                        )}
                      </Box>

                      <Box
                        sx={{
                          mt: 2,
                          fontSize: "0.875rem",
                          color: "text.secondary",
                        }}
                      >
                        Last edited by:{" "}
                        {activeDocument.last_edited_by === currentUser.id
                          ? "You"
                          : activeDocument.last_edited_by}{" "}
                        • Version: {activeDocument.version}
                      </Box>
                    </>
                  ) : (
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "100%",
                      }}
                    >
                      <DocumentIcon
                        sx={{ fontSize: 60, color: "text.disabled", mb: 2 }}
                      />
                      <Typography>
                        Select a document or create a new one
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Box>

            {/* Analytics Tab */}
            <Box
              sx={{
                display: currentTab === 2 ? "flex" : "none",
                flexDirection: "column",
                height: "100%",
                p: 3,
              }}
            >
              <Typography variant="h6" gutterBottom>
                Session Analytics
              </Typography>
              <Typography paragraph color="text.secondary">
                Analytics and insights about this session will be displayed
                here. This feature is under development.
              </Typography>

              {/* Placeholder content for analytics */}
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 2 }}>
                    <Typography variant="subtitle1">Participation</Typography>
                    <Typography variant="h4" color="primary">
                      {participants.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active participants
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 2 }}>
                    <Typography variant="subtitle1">Messages</Typography>
                    <Typography variant="h4" color="primary">
                      {messages.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total messages exchanged
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 2 }}>
                    <Typography variant="subtitle1">Documents</Typography>
                    <Typography variant="h4" color="primary">
                      {documents.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Shared documents created
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SharedSession;
