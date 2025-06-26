import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  CircularProgress,
  Divider,
} from "@mui/material";
import {
  Add as AddIcon,
  VideoCall as VideoCallIcon,
  GroupAdd as GroupAddIcon,
  Schedule as ScheduleIcon,
  AccessTime as TimeIcon,
  CheckCircle as ActiveIcon,
  Cancel as EndedIcon,
  MoreHoriz as ScheduledIcon,
} from "@mui/icons-material";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { format } from "date-fns";

// API URL
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const CollaborativeSessions = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newSession, setNewSession] = useState({
    title: "",
    description: "",
    session_type: "coaching",
    scheduled_start: new Date(Date.now() + 3600000), // 1 hour from now
    scheduled_end: new Date(Date.now() + 7200000), // 2 hours from now
    max_participants: 5,
    features_enabled: {
      chat: true,
      video: true,
      screen_sharing: true,
      document_collaboration: true,
      intervention_sharing: true,
      exercises: true,
      breakout_rooms: false,
      recording: false,
    },
  });

  // Fetch sessions from API
  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/collaboration/sessions`);
      setSessions(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      toast.error("Failed to load sessions");
      setLoading(false);
    }
  };

  // Create new session
  const createSession = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/api/collaboration/sessions`,
        newSession
      );
      toast.success("Session created successfully");
      setOpenDialog(false);
      fetchSessions();

      // Optionally, navigate to the new session
      navigate(`/session/${response.data.id}`);
    } catch (error) {
      console.error("Error creating session:", error);
      toast.error("Failed to create session");
    }
  };

  // Open create session dialog
  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  // Close create session dialog
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewSession({ ...newSession, [name]: value });
  };

  // Handle date changes
  const handleDateChange = (name, value) => {
    setNewSession({ ...newSession, [name]: value });
  };

  // Initialize component
  useEffect(() => {
    fetchSessions();
  }, []);

  // Get status chip for session
  const getStatusChip = (status) => {
    switch (status) {
      case "active":
        return (
          <Chip
            icon={<ActiveIcon />}
            label="Active"
            color="success"
            size="small"
          />
        );
      case "ended":
        return (
          <Chip icon={<EndedIcon />} label="Ended" color="error" size="small" />
        );
      case "scheduled":
        return (
          <Chip
            icon={<ScheduledIcon />}
            label="Scheduled"
            color="primary"
            size="small"
          />
        );
      default:
        return <Chip label={status} color="default" size="small" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={4}
      >
        <Typography variant="h4" component="h1">
          Collaborative Sessions
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenDialog}
        >
          New Session
        </Button>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : sessions.length === 0 ? (
        <Paper elevation={1} sx={{ p: 4, textAlign: "center" }}>
          <GroupAddIcon sx={{ fontSize: 60, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Collaborative Sessions Yet
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Create your first collaborative session to start working with
            clients or colleagues.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Create First Session
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {/* Active Sessions */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Active & Upcoming Sessions
            </Typography>
            <Grid container spacing={2}>
              {sessions
                .filter((session) =>
                  ["active", "scheduled"].includes(session.status)
                )
                .map((session) => (
                  <Grid item xs={12} md={6} lg={4} key={session.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box
                          display="flex"
                          justifyContent="space-between"
                          alignItems="center"
                          mb={1}
                        >
                          <Typography variant="h6" component="div">
                            {session.title}
                          </Typography>
                          {getStatusChip(session.status)}
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          gutterBottom
                        >
                          {session.description || "No description provided"}
                        </Typography>
                        <Divider sx={{ my: 1 }} />
                        <Box display="flex" alignItems="center" mb={1}>
                          <ScheduleIcon
                            fontSize="small"
                            sx={{ mr: 1, color: "text.secondary" }}
                          />
                          <Typography variant="body2">
                            {session.scheduled_start
                              ? format(new Date(session.scheduled_start), "PPp")
                              : "Not scheduled"}
                          </Typography>
                        </Box>
                        <Box display="flex" alignItems="center">
                          <TimeIcon
                            fontSize="small"
                            sx={{ mr: 1, color: "text.secondary" }}
                          />
                          <Typography variant="body2">
                            Duration:{" "}
                            {session.scheduled_end && session.scheduled_start
                              ? `${Math.round((new Date(session.scheduled_end) - new Date(session.scheduled_start)) / 60000)} minutes`
                              : "Not specified"}
                          </Typography>
                        </Box>
                        <Box display="flex" alignItems="center" mt={1}>
                          <GroupAddIcon
                            fontSize="small"
                            sx={{ mr: 1, color: "text.secondary" }}
                          />
                          <Typography variant="body2">
                            Participants: {session.participants?.length || 0} /{" "}
                            {session.max_participants}
                          </Typography>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          variant="contained"
                          fullWidth
                          component={Link}
                          to={`/session/${session.id}`}
                        >
                          {session.status === "active"
                            ? "Join Session"
                            : "View Details"}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          </Grid>

          {/* Past Sessions */}
          {sessions.some((session) =>
            ["ended", "archived"].includes(session.status)
          ) && (
            <Grid item xs={12} sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Past Sessions
              </Typography>
              <Grid container spacing={2}>
                {sessions
                  .filter((session) =>
                    ["ended", "archived"].includes(session.status)
                  )
                  .map((session) => (
                    <Grid item xs={12} md={6} lg={4} key={session.id}>
                      <Card variant="outlined" sx={{ opacity: 0.8 }}>
                        <CardContent>
                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            mb={1}
                          >
                            <Typography variant="h6" component="div">
                              {session.title}
                            </Typography>
                            {getStatusChip(session.status)}
                          </Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            {session.description || "No description provided"}
                          </Typography>
                          <Divider sx={{ my: 1 }} />
                          <Box display="flex" alignItems="center" mb={1}>
                            <ScheduleIcon
                              fontSize="small"
                              sx={{ mr: 1, color: "text.secondary" }}
                            />
                            <Typography variant="body2">
                              {session.actual_start
                                ? `Started: ${format(new Date(session.actual_start), "PPp")}`
                                : "Start time not recorded"}
                            </Typography>
                          </Box>
                          <Box display="flex" alignItems="center">
                            <TimeIcon
                              fontSize="small"
                              sx={{ mr: 1, color: "text.secondary" }}
                            />
                            <Typography variant="body2">
                              {session.actual_end
                                ? `Ended: ${format(new Date(session.actual_end), "PPp")}`
                                : "End time not recorded"}
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button
                            size="small"
                            variant="outlined"
                            fullWidth
                            component={Link}
                            to={`/session/${session.id}`}
                          >
                            View Session
                          </Button>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
              </Grid>
            </Grid>
          )}
        </Grid>
      )}

      {/* Create Session Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Collaborative Session</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Session Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newSession.title}
            onChange={handleInputChange}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            variant="outlined"
            value={newSession.description}
            onChange={handleInputChange}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
            <InputLabel id="session-type-label">Session Type</InputLabel>
            <Select
              labelId="session-type-label"
              id="session-type"
              name="session_type"
              value={newSession.session_type}
              label="Session Type"
              onChange={handleInputChange}
            >
              <MenuItem value="coaching">Coaching</MenuItem>
              <MenuItem value="therapy">Therapy</MenuItem>
              <MenuItem value="consultation">Consultation</MenuItem>
              <MenuItem value="peer_support">Peer Support</MenuItem>
              <MenuItem value="mediation">Mediation</MenuItem>
              <MenuItem value="group_therapy">Group Therapy</MenuItem>
            </Select>
          </FormControl>

          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                gap: 2,
                mb: 2,
              }}
            >
              <DateTimePicker
                label="Start Time"
                value={newSession.scheduled_start}
                onChange={(newValue) =>
                  handleDateChange("scheduled_start", newValue)
                }
                sx={{ flex: 1 }}
              />
              <DateTimePicker
                label="End Time"
                value={newSession.scheduled_end}
                onChange={(newValue) =>
                  handleDateChange("scheduled_end", newValue)
                }
                sx={{ flex: 1 }}
              />
            </Box>
          </LocalizationProvider>

          <TextField
            margin="dense"
            name="max_participants"
            label="Max Participants"
            type="number"
            fullWidth
            variant="outlined"
            value={newSession.max_participants}
            onChange={handleInputChange}
            InputProps={{ inputProps: { min: 2, max: 20 } }}
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="inherit">
            Cancel
          </Button>
          <Button
            onClick={createSession}
            color="primary"
            variant="contained"
            disabled={!newSession.title}
          >
            Create Session
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CollaborativeSessions;
