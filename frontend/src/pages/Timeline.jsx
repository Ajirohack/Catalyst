import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Avatar,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  TrendingUp as TrendIcon,
  Message as MessageIcon,
  CheckCircle as CheckIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Insights as InsightIcon,
  Analytics as AnalyticsIcon,
  Group as GroupIcon,
  Flag as GoalIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TimelinePage = () => {
  const navigate = useNavigate();
  const [selectedProject, setSelectedProject] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('30');
  const [selectedEventType, setSelectedEventType] = useState('all');

  // Mock data
  const projects = [
    { id: 1, name: 'Improving Communication', type: 'romantic' },
    { id: 2, name: 'Family Bonding', type: 'family' },
    { id: 3, name: 'Workplace Relationships', type: 'professional' },
    { id: 4, name: 'Friendship Circle', type: 'friendship' },
  ];

  const timelineEvents = [
    {
      id: 1,
      type: 'milestone',
      title: 'Project Created',
      description: 'Started "Improving Communication" project with Alice and Bob',
      date: '2024-01-10T10:00:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <PlayIcon />,
      color: 'primary',
    },
    {
      id: 2,
      type: 'analysis',
      title: 'First Analysis Completed',
      description: 'Analyzed 15 messages with 78% positive sentiment',
      date: '2024-01-11T14:30:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <AnalyticsIcon />,
      color: 'info',
      metrics: { sentiment: 78, messages: 15 },
    },
    {
      id: 3,
      type: 'goal',
      title: 'Goal Achieved',
      description: 'Completed goal: "Reduce misunderstandings"',
      date: '2024-01-12T16:45:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <CheckIcon />,
      color: 'success',
    },
    {
      id: 4,
      type: 'insight',
      title: 'AI Insight Generated',
      description: 'Response time improved by 40% - great progress on active listening',
      date: '2024-01-13T09:15:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <InsightIcon />,
      color: 'warning',
    },
    {
      id: 5,
      type: 'milestone',
      title: 'Weekly Milestone',
      description: 'Completed first week with 5 meaningful conversations',
      date: '2024-01-14T18:00:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <StarIcon />,
      color: 'secondary',
    },
    {
      id: 6,
      type: 'analysis',
      title: 'Communication Pattern Analysis',
      description: 'Identified peak conversation times and emotional patterns',
      date: '2024-01-15T11:20:00Z',
      projectId: 1,
      projectName: 'Improving Communication',
      icon: <TrendIcon />,
      color: 'info',
      metrics: { patterns: 3, insights: 7 },
    },
    {
      id: 7,
      type: 'milestone',
      title: 'Family Project Started',
      description: 'Created "Family Bonding" project with family members',
      date: '2024-01-05T12:00:00Z',
      projectId: 2,
      projectName: 'Family Bonding',
      icon: <GroupIcon />,
      color: 'primary',
    },
    {
      id: 8,
      type: 'goal',
      title: 'Family Goal Set',
      description: 'Added goal: "Weekly family dinners"',
      date: '2024-01-06T19:30:00Z',
      projectId: 2,
      projectName: 'Family Bonding',
      icon: <GoalIcon />,
      color: 'info',
    },
  ];

  const progressData = [
    { date: 'Jan 1', communication: 60, family: 45, professional: 30, friendship: 70 },
    { date: 'Jan 8', communication: 65, family: 50, professional: 35, friendship: 75 },
    { date: 'Jan 15', communication: 72, family: 55, professional: 40, friendship: 80 },
    { date: 'Jan 22', communication: 75, family: 60, professional: 45, friendship: 85 },
  ];

  const getEventTypeColor = (type) => {
    switch (type) {
      case 'milestone': return 'primary';
      case 'analysis': return 'info';
      case 'goal': return 'success';
      case 'insight': return 'warning';
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return {
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    };
  };

  const filteredEvents = timelineEvents
    .filter(event => {
      if (selectedProject !== 'all' && event.projectId !== parseInt(selectedProject)) return false;
      if (selectedEventType !== 'all' && event.type !== selectedEventType) return false;
      
      const eventDate = new Date(event.date);
      const now = new Date();
      const daysAgo = parseInt(selectedTimeRange);
      const cutoffDate = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000));
      
      return eventDate >= cutoffDate;
    })
    .sort((a, b) => new Date(b.date) - new Date(a.date));

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

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Project Timeline
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your relationship journey and see how your projects evolve over time.
            </Typography>
          </Box>
        </motion.div>

        {/* Filters */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Project</InputLabel>
                    <Select
                      value={selectedProject}
                      label="Project"
                      onChange={(e) => setSelectedProject(e.target.value)}
                    >
                      <MenuItem value="all">All Projects</MenuItem>
                      {projects.map((project) => (
                        <MenuItem key={project.id} value={project.id}>
                          {getProjectTypeIcon(project.type)} {project.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Time Range</InputLabel>
                    <Select
                      value={selectedTimeRange}
                      label="Time Range"
                      onChange={(e) => setSelectedTimeRange(e.target.value)}
                    >
                      <MenuItem value="7">Last 7 days</MenuItem>
                      <MenuItem value="30">Last 30 days</MenuItem>
                      <MenuItem value="90">Last 3 months</MenuItem>
                      <MenuItem value="365">Last year</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Event Type</InputLabel>
                    <Select
                      value={selectedEventType}
                      label="Event Type"
                      onChange={(e) => setSelectedEventType(e.target.value)}
                    >
                      <MenuItem value="all">All Events</MenuItem>
                      <MenuItem value="milestone">Milestones</MenuItem>
                      <MenuItem value="analysis">Analyses</MenuItem>
                      <MenuItem value="goal">Goals</MenuItem>
                      <MenuItem value="insight">Insights</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" fontWeight="bold" color="primary">
                      {filteredEvents.length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Events Found
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </motion.div>

        <Grid container spacing={4}>
          {/* Progress Chart */}
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Progress Overview
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={progressData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="communication"
                        stroke="#e91e63"
                        strokeWidth={2}
                        name="Communication"
                      />
                      <Line
                        type="monotone"
                        dataKey="family"
                        stroke="#2196f3"
                        strokeWidth={2}
                        name="Family"
                      />
                      <Line
                        type="monotone"
                        dataKey="professional"
                        stroke="#ff9800"
                        strokeWidth={2}
                        name="Professional"
                      />
                      <Line
                        type="monotone"
                        dataKey="friendship"
                        stroke="#4caf50"
                        strokeWidth={2}
                        name="Friendship"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Quick Stats */}
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Stats
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <StarIcon color="warning" fontSize="small" />
                        <Typography variant="body2">Milestones</Typography>
                      </Box>
                      <Typography variant="h6" fontWeight="bold">
                        {timelineEvents.filter(e => e.type === 'milestone').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AnalyticsIcon color="info" fontSize="small" />
                        <Typography variant="body2">Analyses</Typography>
                      </Box>
                      <Typography variant="h6" fontWeight="bold">
                        {timelineEvents.filter(e => e.type === 'analysis').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckIcon color="success" fontSize="small" />
                        <Typography variant="body2">Goals Achieved</Typography>
                      </Box>
                      <Typography variant="h6" fontWeight="bold">
                        {timelineEvents.filter(e => e.type === 'goal').length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <InsightIcon color="warning" fontSize="small" />
                        <Typography variant="body2">AI Insights</Typography>
                      </Box>
                      <Typography variant="h6" fontWeight="bold">
                        {timelineEvents.filter(e => e.type === 'insight').length}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Timeline */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Event Timeline
              </Typography>
              {filteredEvents.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <Typography variant="body1" color="text.secondary">
                    No events found for the selected filters.
                  </Typography>
                </Box>
              ) : (
                <Timeline>
                  {filteredEvents.map((event, index) => {
                    const { time, date } = formatDate(event.date);
                    return (
                      <TimelineItem key={event.id}>
                        <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                          <Typography variant="caption" display="block">
                            {date}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {time}
                          </Typography>
                        </TimelineOppositeContent>
                        <TimelineSeparator>
                          <TimelineDot color={event.color}>
                            {event.icon}
                          </TimelineDot>
                          {index < filteredEvents.length - 1 && <TimelineConnector />}
                        </TimelineSeparator>
                        <TimelineContent sx={{ py: '12px', px: 2 }}>
                          <Paper sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                              <Typography variant="h6" component="span">
                                {event.title}
                              </Typography>
                              <Chip
                                label={event.type}
                                size="small"
                                color={getEventTypeColor(event.type)}
                                variant="outlined"
                              />
                            </Box>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              {event.description}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Chip
                                label={event.projectName}
                                size="small"
                                variant="outlined"
                                onClick={() => navigate(`/project/${event.projectId}`)}
                              />
                              {event.metrics && (
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  {Object.entries(event.metrics).map(([key, value]) => (
                                    <Typography key={key} variant="caption" color="text.secondary">
                                      {key}: {value}
                                    </Typography>
                                  ))}
                                </Box>
                              )}
                            </Box>
                          </Paper>
                        </TimelineContent>
                      </TimelineItem>
                    );
                  })}
                </Timeline>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </motion.div>
  );
};

export default TimelinePage;