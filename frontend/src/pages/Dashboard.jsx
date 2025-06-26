import React, { useState } from 'react';
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
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
} from "recharts";
import {
  Plus,
  TrendingUp,
  Heart,
  Brain,
  FolderOpen,
  BarChart3,
  CheckCircle,
  Activity,
  AlertTriangle,
  Shield,
  Zap,
  Eye,
  Settings,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import RealTimeAnalysisDashboard from "../components/analysis/RealTimeAnalysisDashboard";
import ConflictDetectionPanel from "../components/analysis/ConflictDetectionPanel";

const Dashboard = () => {
  const navigate = useNavigate();
  const [activeView, setActiveView] = useState('overview');
  const [realTimeEnabled, setRealTimeEnabled] = useState(true);
  const [conflictDetectionEnabled, setConflictDetectionEnabled] = useState(true);

  // Mock data
  const recentProjects = [
    {
      id: 1,
      name: "Improving Communication",
      participants: ["Alice", "Bob"],
      status: "active",
      progress: 75,
      lastActivity: "2 hours ago",
    },
    {
      id: 2,
      name: "Family Bonding",
      participants: ["Mom", "Dad", "Sister"],
      status: "active",
      progress: 45,
      lastActivity: "1 day ago",
    },
    {
      id: 3,
      name: "Workplace Relationships",
      participants: ["Team Lead", "Colleagues"],
      status: "paused",
      progress: 30,
      lastActivity: "3 days ago",
    },
  ];

  const relationshipHealthData = [
    { name: "Mon", score: 7.2 },
    { name: "Tue", score: 7.8 },
    { name: "Wed", score: 6.9 },
    { name: "Thu", score: 8.1 },
    { name: "Fri", score: 8.5 },
    { name: "Sat", score: 9.0 },
    { name: "Sun", score: 8.7 },
  ];

  const communicationBreakdown = [
    { name: "Positive", value: 65, color: "#10b981" },
    { name: "Neutral", value: 25, color: "#6b7280" },
    { name: "Needs Work", value: 10, color: "#ef4444" },
  ];

  const recentInsights = [
    {
      id: 1,
      type: "achievement",
      title: "Communication Milestone",
      description: "You've improved active listening by 40% this week!",
      time: "1 hour ago",
    },
    {
      id: 2,
      type: "suggestion",
      title: "Quality Time Opportunity",
      description: "Consider scheduling a device-free dinner tonight",
      time: "3 hours ago",
    },
    {
      id: 3,
      type: "analysis",
      title: "Weekly Analysis Ready",
      description: "Your relationship health report is available",
      time: "1 day ago",
    },
  ];

  // Real-time status data
  const realTimeStatus = {
    conflictLevel: 'medium',
    emotionalState: 'concerned',
    activeConversations: 2,
    interventionsToday: 3,
    lastUpdate: new Date()
  };

  const handleInterventionTrigger = (intervention) => {
    console.log('Intervention triggered:', intervention);
    // Handle intervention logic here
  };

  const getConflictLevelInfo = (level) => {
    switch (level) {
      case 'critical':
        return { color: 'text-red-600', bg: 'bg-red-100', icon: AlertTriangle };
      case 'high':
        return { color: 'text-orange-600', bg: 'bg-orange-100', icon: AlertTriangle };
      case 'medium':
        return { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: Zap };
      default:
        return { color: 'text-green-600', bg: 'bg-green-100', icon: Shield };
    }
  };

  const conflictInfo = getConflictLevelInfo(realTimeStatus.conflictLevel);

  const getInsightIcon = (type) => {
    switch (type) {
      case "achievement":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "suggestion":
        return <Brain className="h-5 w-5 text-blue-600" />;
      case "analysis":
        return <BarChart3 className="h-5 w-5 text-purple-600" />;
      default:
        return <Heart className="h-5 w-5 text-red-600" />;
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
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <div className="max-w-7xl mx-auto p-6">
        {/* Welcome Section */}
        <motion.div variants={itemVariants}>
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">
                  Welcome back, John! 👋
                </h1>
                <p className="text-muted-foreground text-lg">
                  AI-powered relationship insights and real-time conflict detection
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${realTimeEnabled ? 'bg-green-500' : 'bg-gray-400'} animate-pulse`} />
                  <span className="text-sm font-medium">
                    {realTimeEnabled ? 'Live Analysis' : 'Offline'}
                  </span>
                </div>
                <Button
                  onClick={() => navigate("/new-project")}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Project</span>
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Real-time Status Bar */}
        {realTimeEnabled && (
          <motion.div variants={itemVariants}>
            <Card className="border-l-4 border-l-blue-500 mb-8">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-2">
                      <conflictInfo.icon className={`w-5 h-5 ${conflictInfo.color}`} />
                      <div>
                        <div className="font-medium">Conflict Level: {realTimeStatus.conflictLevel}</div>
                        <div className="text-sm text-gray-500">Emotional State: {realTimeStatus.emotionalState}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <Activity className="w-4 h-4 text-blue-500" />
                        <span>{realTimeStatus.activeConversations} active</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Brain className="w-4 h-4 text-purple-500" />
                        <span>{realTimeStatus.interventionsToday} interventions today</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    Last update: {realTimeStatus.lastUpdate.toLocaleTimeString()}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Navigation Tabs */}
        <Tabs value={activeView} onValueChange={setActiveView} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="realtime" className="flex items-center space-x-2">
              <Activity className="w-4 h-4" />
              <span>Real-time Analysis</span>
            </TabsTrigger>
            <TabsTrigger value="conflicts" className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4" />
              <span>Conflict Detection</span>
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center space-x-2">
              <Eye className="w-4 h-4" />
              <span>Insights</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">

        {/* Quick Stats */}
        <motion.div variants={itemVariants}>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="h-6 w-6 text-primary-foreground" />
                </div>
                <h3 className="text-3xl font-bold text-primary mb-2">8.5</h3>
                <p className="text-sm text-muted-foreground">Relationship Health</p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-green-600 mb-2">+12%</h3>
                <p className="text-sm text-muted-foreground">Weekly Improvement</p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FolderOpen className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-blue-600 mb-2">3</h3>
                <p className="text-sm text-muted-foreground">Active Projects</p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-3xl font-bold text-orange-600 mb-2">24</h3>
                <p className="text-sm text-muted-foreground">AI Suggestions Used</p>
              </CardContent>
            </Card>
          </div>
        </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Projects */}
              <div className="lg:col-span-2">
                <motion.div variants={itemVariants}>
                  <Card className="mb-6">
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>Your Projects</CardTitle>
                        <Button onClick={() => navigate("/new-project")} className="flex items-center gap-2">
                          <Plus className="h-4 w-4" />
                          New Project
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>

                      {recentProjects.map((project, index) => (
                        <div key={project.id} className={`${index < recentProjects.length - 1 ? 'mb-6 pb-6 border-b' : 'mb-0'}`}>
                          <div className="flex justify-between items-center mb-2">
                            <h4 className="text-lg font-semibold">{project.name}</h4>
                            <Badge variant={project.status === "active" ? "default" : "secondary"}>
                              {project.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            Participants: {project.participants.join(", ")}
                          </p>
                          <div className="flex items-center gap-3 mb-2">
                            <div className="flex-1">
                              <Progress value={project.progress} className="h-2" />
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {project.progress}%
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Last activity: {project.lastActivity}
                          </p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Relationship Health Chart */}
                <motion.div variants={itemVariants}>
                  <Card>
                    <CardHeader>
                      <CardTitle>Relationship Health Trend</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={relationshipHealthData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis domain={[0, 10]} />
                            <Tooltip />
                            <Line
                              type="monotone"
                              dataKey="score"
                              stroke="hsl(var(--primary))"
                              strokeWidth={3}
                              dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>

              {/* Sidebar */}
              <div className="lg:col-span-1">
                {/* Communication Breakdown */}
                <motion.div variants={itemVariants}>
                  <Card className="mb-6">
                    <CardHeader>
                      <CardTitle>Communication Quality</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-52">
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
                      </div>
                      <div className="mt-4 space-y-2">
                        {communicationBreakdown.map((item) => (
                          <div key={item.name} className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: item.color }}
                              />
                              <span className="text-sm">{item.name}</span>
                            </div>
                            <span className="text-sm font-semibold">{item.value}%</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Recent Insights */}
                <motion.div variants={itemVariants}>
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Insights</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {recentInsights.map((insight) => (
                          <div key={insight.id} className="flex items-start gap-3">
                            <div className="flex-shrink-0 mt-1">
                              {getInsightIcon(insight.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="text-sm font-semibold mb-1">{insight.title}</h4>
                              <p className="text-sm text-muted-foreground mb-1">
                                {insight.description}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {insight.time}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="realtime">
            <RealTimeAnalysisDashboard projectId="current" isRealTime={realTimeEnabled} />
          </TabsContent>

          <TabsContent value="conflicts">
            <ConflictDetectionPanel 
              projectId="current" 
              onInterventionTrigger={handleInterventionTrigger}
            />
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Therapeutic Insights & Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>Advanced insights panel coming soon...</p>
                  <p className="text-sm mt-2">This will include detailed therapeutic recommendations, progress tracking, and personalized coaching suggestions.</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </motion.div>
  );
};

export default Dashboard;
