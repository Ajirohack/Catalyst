import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Favorite as HeartIcon,
  Psychology as AIIcon,
  Timeline as TimelineIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const Dashboard = () => {
  const navigate = useNavigate();

  // Mock data
  const recentProjects = [
    {
      id: 1,
      name: 'Improving Communication',
      participants: ['Alice', 'Bob'],
      status: 'active',
      progress: 75,
      lastActivity: '2 hours ago',
    },
    {
      id: 2,
      name: 'Family Bonding',
      participants: ['Mom', 'Dad', 'Sister'],
      status: 'active',
      progress: 45,
      lastActivity: '1 day ago',
    },
    {
      id: 3,
      name: 'Workplace Relationships',
      participants: ['Team Lead', 'Colleagues'],
      status: 'paused',
      progress: 30,
      lastActivity: '3 days ago',
    },
  ];

  const relationshipHealthData = [
    { name: 'Mon', score: 7.2 },
    { name: 'Tue', score: 7.8 },
    { name: 'Wed', score: 6.9 },
    { name: 'Thu', score: 8.1 },
    { name: 'Fri', score: 8.5 },
    { name: 'Sat', score: 9.0 },
    { name: 'Sun', score: 8.7 },
  ];

  const communicationBreakdown = [
    { name: 'Positive', value: 65, color: '#10b981' },
    { name: 'Neutral', value: 25, color: '#6b7280' },
    { name: 'Needs Work', value: 10, color: '#ef4444' },
  ];

  const recentInsights = [
    {
      id: 1,
      type: 'achievement',
      title: 'Communication Milestone',
      description: 'You\'ve improved active listening by 40% this week!',
      time: '1 hour ago',
    },
    {
      id: 2,
      type: 'suggestion',
      title: 'Quality Time Opportunity',
      description: 'Consider scheduling a device-free dinner tonight',
      time: '3 hours ago',
    },
    {
      id: 3,
      type: 'analysis',
      title: 'Weekly Analysis Ready',
      description: 'Your relationship health report is available',
      time: '1 day ago',
    },
  ];

  const getInsightIcon = (type) => {
    switch (type) {
      case 'achievement': return <CheckIcon color="success" />;
      case 'suggestion': return <AIIcon color="primary" />;
      case 'analysis': return <AnalyticsIcon color="info" />;
      default: return <HeartIcon />;
    }
  };

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
        {/* Welcome Section */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Welcome back, John! 👋
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Here's what's happening with your relationships today.
            </Typography>
          </Box>
        </motion.div>

        {/* Quick Stats */}
        <motion.div variants={itemVariants}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 2 }}>
                  <HeartIcon />
                </Avatar>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  8.5
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Relationship Health
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 2 }}>
                  <TrendingUpIcon />
                </Avatar>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  +12%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Weekly Improvement
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 2 }}>
                  <TimelineIcon />
                </Avatar>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  3
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Projects
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center', p: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 2 }}>
                  <AIIcon />
                </Avatar>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  24
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  AI Suggestions Used
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </motion.div>

        <Grid container spacing={3}>
          {/* Recent Projects */}
          <Grid item xs={12} md={8}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6" fontWeight="bold">
                      Your Projects
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => navigate('/new-project')}
                    >
                      New Project
                    </Button>
                  </Box>
                  
                  {recentProjects.map((project) => (
                    <Box key={project.id} sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {project.name}
                        </Typography>
                        <Chip
                          label={project.status}
                          size="small"
                          color={project.status === 'active' ? 'success' : 'default'}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Participants: {project.participants.join(', ')}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={project.progress}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {project.progress}%
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Last activity: {project.lastActivity}
                      </Typography>
                      {project.id < recentProjects.length && <Divider sx={{ mt: 2 }} />}
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            {/* Relationship Health Chart */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Relationship Health Trend
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={relationshipHealthData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis domain={[0, 10]} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="score"
                          stroke="#6366f1"
                          strokeWidth={3}
                          dot={{ fill: '#6366f1', strokeWidth: 2, r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            {/* Communication Breakdown */}
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Communication Quality
                  </Typography>
                  <Box sx={{ height: 200 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={communicationBreakdown}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {communicationBreakdown.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                  <Box sx={{ mt: 2 }}>
                    {communicationBreakdown.map((item) => (
                      <Box key={item.name} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            bgcolor: item.color,
                            mr: 1,
                          }}
                        />
                        <Typography variant="body2" sx={{ flexGrow: 1 }}>
                          {item.name}
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {item.value}%
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Insights */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Recent Insights
                  </Typography>
                  <List>
                    {recentInsights.map((insight) => (
                      <ListItem key={insight.id} sx={{ px: 0 }}>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: 'transparent' }}>
                            {getInsightIcon(insight.type)}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={insight.title}
                          secondary={
                            <>
                              <Typography variant="body2" color="text.secondary">
                                {insight.description}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {insight.time}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </Box>
    </motion.div>
  );
};

export default Dashboard;