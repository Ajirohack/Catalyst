import React from 'react';
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
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";

const Dashboard = () => {
  const navigate = useNavigate();

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
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Welcome back, John! 👋
            </h1>
            <p className="text-muted-foreground text-lg">
              Here's what's happening with your relationships today.
            </p>
          </div>
        </motion.div>

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
      </div>
    </motion.div>
  );
};

export default Dashboard;
