import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Timeline as TimelineIcon,
  Analytics as AnalyticsIcon,
  Group as GroupIcon,
  Flag as GoalIcon,
  TrendingUp as TrendIcon,
  Message as MessageIcon,
  Insights as InsightIcon,
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as UncheckIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import toast from 'react-hot-toast';

const ProjectDetails = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [activeTab, setActiveTab] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [addGoalDialogOpen, setAddGoalDialogOpen] = useState(false);
  const [newGoal, setNewGoal] = useState('');

  // Mock project data - in real app, this would come from API
  const [project, setProject] = useState({
    id: parseInt(projectId),
    name: 'Improving Communication',
    description: 'Working on better daily communication patterns with my partner',
    participants: [
      { name: 'Alice', role: 'Partner', avatar: 'A' },
      { name: 'Bob', role: 'Partner', avatar: 'B' }
    ],
    status: 'active',
    progress: 75,
    projectType: 'romantic',
    createdAt: '2024-01-10',
    lastActivity: '2 hours ago',
    analysisCount: 12,
    goals: [
      { id: 1, text: 'Reduce misunderstandings', completed: true },
      { id: 2, text: 'Increase quality time', completed: false },
      { id: 3, text: 'Better conflict resolution', completed: false },
      { id: 4, text: 'Practice active listening', completed: true },
    ],
    insights: [
      {
        id: 1,
        type: 'positive',
        title: 'Communication Improvement',
        description: 'Your response time has improved by 40% this week',
        date: '2024-01-15',
        category: 'responsiveness'
      },
      {
        id: 2,
        type: 'suggestion',
        title: 'Emotional Tone',
        description: 'Consider using more positive language in evening conversations',
        date: '2024-01-14',
        category: 'tone'
      },
      {
        id: 3,
        type: 'milestone',
        title: 'Weekly Goal Achieved',
        description: 'Successfully completed 5 meaningful conversations this week',
        date: '2024-01-13',
        category: 'goals'
      }
    ],
    progressData: [
      { date: 'Jan 1', score: 60, messages: 45 },
      { date: 'Jan 8', score: 65, messages: 52 },
      { date: 'Jan 15', score: 72, messages: 48 },
      { date: 'Jan 22', score: 75, messages: 55 },
    ],
    communicationMetrics: [
      { category: 'Positive Tone', value: 78 },
      { category: 'Response Time', value: 85 },
      { category: 'Active Listening', value: 72 },
      { category: 'Conflict Resolution', value: 68 },
    ]
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'info';
      default: return 'default';
    }
  };

  const getProjectTypeIcon = (type) => {
    switch (type) {
      case 'romantic': return '💕';
      case 'family': return '👨‍👩‍👧‍👦';
      case 'friendship': return '👫';
      case 'professional': return '🤝';
      default: return '🌟';
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'positive': return <TrendIcon color="success" />;
      case 'suggestion': return <InsightIcon color="warning" />;
      case 'milestone': return <CheckIcon color="info" />;
      default: return <MessageIcon />;
    }
  };

  const handleStatusToggle = () => {
    const newStatus = project.status === 'active' ? 'paused' : 'active';
    setProject({ ...project, status: newStatus });
    toast.success(`Project ${newStatus}`);
  };

  const handleGoalToggle = (goalId) => {
    setProject({
      ...project,
      goals: project.goals.map(goal =>
        goal.id === goalId ? { ...goal, completed: !goal.completed } : goal
      )
    });
  };

  const handleAddGoal = () => {
    if (newGoal.trim()) {
      const newGoalObj = {
        id: Date.now(),
        text: newGoal.trim(),
        completed: false
      };
      setProject({
        ...project,
        goals: [...project.goals, newGoalObj]
      });
      setNewGoal('');
      setAddGoalDialogOpen(false);
      toast.success('Goal added successfully');
    }
  };

  const completedGoals = project.goals.filter(goal => goal.completed).length;
  const goalProgress = (completedGoals / project.goals.length) * 100;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
      },
    },
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => navigate('/continue-project')}>
              <BackIcon />
            </IconButton>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h4" fontWeight="bold">
                {getProjectTypeIcon(project.projectType)} {project.name}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {project.description}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditDialogOpen(true)}
              >
                Edit
              </Button>
              <Button
                variant="contained"
                startIcon={project.status === 'active' ? <PauseIcon /> : <PlayIcon />}
                onClick={handleStatusToggle}
                color={project.status === 'active' ? 'warning' : 'success'}
              >
                {project.status === 'active' ? 'Pause' : 'Resume'}
              </Button>
            </Box>
          </Box>
        </motion.div>

        {/* Project Overview Cards */}
        <motion.div variants={itemVariants}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Chip
                    label={project.status}
                    color={getStatusColor(project.status)}
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="h6" fontWeight="bold">
                    {project.progress}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overall Progress
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={project.progress}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AnalyticsIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {project.analysisCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Analyses Completed
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <GoalIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {completedGoals}/{project.goals.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Goals Achieved
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={goalProgress}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    color="success"
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <GroupIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {project.participants.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Participants
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>

        {/* Tabs */}
        <motion.div variants={itemVariants}>
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                <Tab label="Overview" />
                <Tab label="Goals" />
                <Tab label="Analytics" />
                <Tab label="Insights" />
                <Tab label="Participants" />
              </Tabs>
            </Box>

            {/* Overview Tab */}
            <TabPanel value={activeTab} index={0}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" gutterBottom>
                    Progress Trend
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={project.progressData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#1976d2"
                        strokeWidth={3}
                        dot={{ fill: '#1976d2', strokeWidth: 2, r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>
                    Recent Activity
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <MessageIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="New analysis completed"
                        secondary="2 hours ago"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <CheckIcon color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Goal marked as complete"
                        secondary="1 day ago"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <InsightIcon color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary="New insight generated"
                        secondary="2 days ago"
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </TabPanel>

            {/* Goals Tab */}
            <TabPanel value={activeTab} index={1}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Project Goals ({completedGoals}/{project.goals.length} completed)
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setAddGoalDialogOpen(true)}
                >
                  Add Goal
                </Button>
              </Box>
              <List>
                {project.goals.map((goal) => (
                  <React.Fragment key={goal.id}>
                    <ListItem
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' },
                        textDecoration: goal.completed ? 'line-through' : 'none',
                        opacity: goal.completed ? 0.7 : 1,
                      }}
                      onClick={() => handleGoalToggle(goal.id)}
                    >
                      <ListItemIcon>
                        {goal.completed ? (
                          <CheckIcon color="success" />
                        ) : (
                          <UncheckIcon color="action" />
                        )}
                      </ListItemIcon>
                      <ListItemText primary={goal.text} />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </TabPanel>

            {/* Analytics Tab */}
            <TabPanel value={activeTab} index={2}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Communication Metrics
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={project.communicationMetrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Message Volume
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={project.progressData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="messages"
                        stroke="#2e7d32"
                        strokeWidth={3}
                        dot={{ fill: '#2e7d32', strokeWidth: 2, r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Grid>
              </Grid>
            </TabPanel>

            {/* Insights Tab */}
            <TabPanel value={activeTab} index={3}>
              <Typography variant="h6" gutterBottom>
                AI-Generated Insights
              </Typography>
              <Grid container spacing={2}>
                {project.insights.map((insight) => (
                  <Grid item xs={12} key={insight.id}>
                    <Paper sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                        {getInsightIcon(insight.type)}
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {insight.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {insight.description}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Chip label={insight.category} size="small" variant="outlined" />
                            <Typography variant="caption" color="text.secondary">
                              {insight.date}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>

            {/* Participants Tab */}
            <TabPanel value={activeTab} index={4}>
              <Typography variant="h6" gutterBottom>
                Project Participants
              </Typography>
              <Grid container spacing={2}>
                {project.participants.map((participant, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Avatar sx={{ width: 64, height: 64, mx: 'auto', mb: 2, bgcolor: 'primary.main' }}>
                          {participant.avatar}
                        </Avatar>
                        <Typography variant="h6" fontWeight="bold">
                          {participant.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {participant.role}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>
          </Card>
        </motion.div>

        {/* Add Goal Dialog */}
        <Dialog open={addGoalDialogOpen} onClose={() => setAddGoalDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Goal</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Goal Description"
              fullWidth
              variant="outlined"
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              placeholder="Enter a specific, measurable goal..."
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddGoalDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleAddGoal} variant="contained" disabled={!newGoal.trim()}>
              Add Goal
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </motion.div>
  );
};

export default ProjectDetails;