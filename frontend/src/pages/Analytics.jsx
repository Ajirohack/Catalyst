import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  LinearProgress,
  Divider,
} from "@mui/material";
import {
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  Analytics as AnalyticsIcon,
  Insights as InsightIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Favorite as HeartIcon,
  Message as MessageIcon,
  Group as GroupIcon,
  Star as StarIcon,
  Download as DownloadIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import toast from "react-hot-toast";

const Analytics = () => {
  const [selectedProject, setSelectedProject] = useState("all");
  const [selectedTimeRange, setSelectedTimeRange] = useState("30");
  const [selectedMetric, setSelectedMetric] = useState("overall");

  // Mock data
  const projects = [
    {
      id: 1,
      name: "Improving Communication",
      type: "romantic",
      color: "#e91e63",
    },
    { id: 2, name: "Family Bonding", type: "family", color: "#2196f3" },
    {
      id: 3,
      name: "Workplace Relationships",
      type: "professional",
      color: "#ff9800",
    },
    { id: 4, name: "Friendship Circle", type: "friendship", color: "#4caf50" },
  ];

  const overallMetrics = {
    totalProjects: 4,
    activeProjects: 2,
    completedGoals: 12,
    totalAnalyses: 45,
    averageScore: 78,
    improvementRate: 15.2,
  };

  const trendData = [
    {
      date: "Week 1",
      communication: 60,
      sentiment: 65,
      engagement: 70,
      overall: 65,
    },
    {
      date: "Week 2",
      communication: 65,
      sentiment: 70,
      engagement: 75,
      overall: 70,
    },
    {
      date: "Week 3",
      communication: 72,
      sentiment: 75,
      engagement: 78,
      overall: 75,
    },
    {
      date: "Week 4",
      communication: 75,
      sentiment: 80,
      engagement: 82,
      overall: 79,
    },
    {
      date: "Week 5",
      communication: 78,
      sentiment: 82,
      engagement: 85,
      overall: 82,
    },
  ];

  const projectPerformance = [
    {
      name: "Communication",
      score: 78,
      change: 12,
      trend: "up",
      analyses: 15,
      goals: 4,
    },
    {
      name: "Family Bonding",
      score: 65,
      change: 8,
      trend: "up",
      analyses: 12,
      goals: 3,
    },
    {
      name: "Professional",
      score: 45,
      change: -2,
      trend: "down",
      analyses: 8,
      goals: 2,
    },
    {
      name: "Friendship",
      score: 85,
      change: 5,
      trend: "up",
      analyses: 10,
      goals: 3,
    },
  ];

  const communicationPatterns = [
    { time: "6 AM", messages: 5, sentiment: 70 },
    { time: "9 AM", messages: 15, sentiment: 65 },
    { time: "12 PM", messages: 25, sentiment: 75 },
    { time: "3 PM", messages: 20, sentiment: 80 },
    { time: "6 PM", messages: 35, sentiment: 85 },
    { time: "9 PM", messages: 30, sentiment: 90 },
    { time: "12 AM", messages: 10, sentiment: 75 },
  ];

  const sentimentDistribution = [
    { name: "Very Positive", value: 35, color: "#4caf50" },
    { name: "Positive", value: 30, color: "#8bc34a" },
    { name: "Neutral", value: 20, color: "#ffc107" },
    { name: "Negative", value: 10, color: "#ff9800" },
    { name: "Very Negative", value: 5, color: "#f44336" },
  ];

  const relationshipHealth = [
    { category: "Communication", score: 78, fullMark: 100 },
    { category: "Trust", score: 85, fullMark: 100 },
    { category: "Empathy", score: 72, fullMark: 100 },
    { category: "Conflict Resolution", score: 68, fullMark: 100 },
    { category: "Quality Time", score: 80, fullMark: 100 },
    { category: "Support", score: 88, fullMark: 100 },
  ];

  const topInsights = [
    {
      id: 1,
      title: "Peak Communication Hours",
      description: "Most positive conversations happen between 6-9 PM",
      impact: "high",
      category: "timing",
      project: "Communication",
    },
    {
      id: 2,
      title: "Response Time Improvement",
      description: "Average response time decreased by 40% this month",
      impact: "high",
      category: "responsiveness",
      project: "Communication",
    },
    {
      id: 3,
      title: "Emotional Tone Patterns",
      description: "Positive language usage increased by 25%",
      impact: "medium",
      category: "sentiment",
      project: "Family Bonding",
    },
    {
      id: 4,
      title: "Goal Achievement Rate",
      description: "80% of weekly goals are being completed on time",
      impact: "medium",
      category: "goals",
      project: "All Projects",
    },
  ];

  const getImpactColor = (impact) => {
    switch (impact) {
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "info";
      default:
        return "default";
    }
  };

  const getTrendIcon = (trend) => {
    return trend === "up" ? (
      <TrendUpIcon color="success" fontSize="small" />
    ) : (
      <TrendDownIcon color="error" fontSize="small" />
    );
  };

  const handleExportData = () => {
    toast.success("Analytics data exported successfully!");
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
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <Box sx={{ maxWidth: 1400, mx: "auto" }}>
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box
            sx={{
              mb: 4,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Box>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Analytics Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Deep insights into your relationship patterns and progress.
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExportData}
            >
              Export Data
            </Button>
          </Box>
        </motion.div>

        {/* Filters */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={4}>
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
                          {project.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
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
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Metric Focus</InputLabel>
                    <Select
                      value={selectedMetric}
                      label="Metric Focus"
                      onChange={(e) => setSelectedMetric(e.target.value)}
                    >
                      <MenuItem value="overall">Overall Health</MenuItem>
                      <MenuItem value="communication">Communication</MenuItem>
                      <MenuItem value="sentiment">Sentiment</MenuItem>
                      <MenuItem value="engagement">Engagement</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </motion.div>

        {/* Key Metrics */}
        <motion.div variants={itemVariants}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <AssessmentIcon
                    color="primary"
                    sx={{ fontSize: 32, mb: 1 }}
                  />
                  <Typography variant="h5" fontWeight="bold">
                    {overallMetrics.totalProjects}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Projects
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <SpeedIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight="bold">
                    {overallMetrics.averageScore}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Score
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <StarIcon color="warning" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight="bold">
                    {overallMetrics.completedGoals}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Goals Achieved
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <AnalyticsIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight="bold">
                    {overallMetrics.totalAnalyses}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Analyses
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <TrendUpIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight="bold">
                    +{overallMetrics.improvementRate}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Improvement
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Card>
                <CardContent sx={{ textAlign: "center" }}>
                  <HeartIcon color="error" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight="bold">
                    {overallMetrics.activeProjects}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Projects
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>

        <Grid container spacing={4}>
          {/* Progress Trends */}
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Progress Trends
                  </Typography>
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="overall"
                        stackId="1"
                        stroke="#1976d2"
                        fill="#1976d2"
                        fillOpacity={0.6}
                        name="Overall Score"
                      />
                      <Area
                        type="monotone"
                        dataKey="communication"
                        stackId="2"
                        stroke="#e91e63"
                        fill="#e91e63"
                        fillOpacity={0.4}
                        name="Communication"
                      />
                      <Area
                        type="monotone"
                        dataKey="sentiment"
                        stackId="3"
                        stroke="#4caf50"
                        fill="#4caf50"
                        fillOpacity={0.4}
                        name="Sentiment"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Relationship Health Radar */}
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Relationship Health
                  </Typography>
                  <ResponsiveContainer width="100%" height={350}>
                    <RadarChart data={relationshipHealth}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="category" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar
                        name="Score"
                        dataKey="score"
                        stroke="#1976d2"
                        fill="#1976d2"
                        fillOpacity={0.3}
                        strokeWidth={2}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Communication Patterns */}
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Daily Communication Patterns
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={communicationPatterns}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Bar
                        yAxisId="left"
                        dataKey="messages"
                        fill="#2196f3"
                        name="Messages"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="sentiment"
                        stroke="#4caf50"
                        name="Sentiment"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Sentiment Distribution */}
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <Card sx={{ mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Sentiment Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={sentimentDistribution}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, percent }) =>
                          `${name} ${(percent * 100).toFixed(0)}%`
                        }
                      >
                        {sentimentDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Project Performance Table */}
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Project Performance
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Project</TableCell>
                          <TableCell align="center">Score</TableCell>
                          <TableCell align="center">Change</TableCell>
                          <TableCell align="center">Analyses</TableCell>
                          <TableCell align="center">Goals</TableCell>
                          <TableCell align="center">Progress</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {projectPerformance.map((project) => (
                          <TableRow key={project.name}>
                            <TableCell>
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <Avatar
                                  sx={{
                                    width: 32,
                                    height: 32,
                                    bgcolor: "primary.main",
                                  }}
                                >
                                  {project.name[0]}
                                </Avatar>
                                {project.name}
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="h6" fontWeight="bold">
                                {project.score}%
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  gap: 0.5,
                                }}
                              >
                                {getTrendIcon(project.trend)}
                                <Typography
                                  variant="body2"
                                  color={
                                    project.trend === "up"
                                      ? "success.main"
                                      : "error.main"
                                  }
                                >
                                  {project.change > 0 ? "+" : ""}
                                  {project.change}%
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              {project.analyses}
                            </TableCell>
                            <TableCell align="center">
                              {project.goals}
                            </TableCell>
                            <TableCell align="center">
                              <LinearProgress
                                variant="determinate"
                                value={project.score}
                                sx={{ width: 60, height: 6, borderRadius: 3 }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Top Insights */}
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Key Insights
                  </Typography>
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 2 }}
                  >
                    {topInsights.map((insight) => (
                      <Paper key={insight.id} sx={{ p: 2 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                            mb: 1,
                          }}
                        >
                          <Typography variant="subtitle2" fontWeight="bold">
                            {insight.title}
                          </Typography>
                          <Chip
                            label={insight.impact}
                            size="small"
                            color={getImpactColor(insight.impact)}
                            variant="outlined"
                          />
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {insight.description}
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <Chip
                            label={insight.category}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="caption" color="text.secondary">
                            {insight.project}
                          </Typography>
                        </Box>
                      </Paper>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </Box>
    </motion.div>
  );
};

export default Analytics;
