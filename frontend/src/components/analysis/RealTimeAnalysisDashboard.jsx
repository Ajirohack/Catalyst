import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/tabs";
import { Progress } from "../ui/progress";
import { Alert, AlertDescription } from "../ui/alert";
import {
  Activity,
  AlertTriangle,
  Brain,
  Heart,
  MessageCircle,
  TrendingUp,
  TrendingDown,
  Users,
  Zap,
  Shield,
  Target,
  Clock,
  BarChart3,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  Radar as RadarIcon,
} from "lucide-react";

const RealTimeAnalysisDashboard = ({ projectId, isRealTime = true }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [conflictLevel, setConflictLevel] = useState("low");
  const [emotionalState, setEmotionalState] = useState("neutral");
  const [conversationTrend, setConversationTrend] = useState("stable");
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState("1h");
  const wsRef = useRef(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (isRealTime) {
      const ws = new WebSocket(
        `ws://localhost:8000/api/v1/ai-therapy/real-time-coaching`
      );
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log("Real-time analysis WebSocket connected");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleRealTimeUpdate(data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("Real-time analysis WebSocket disconnected");
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      };

      return () => {
        ws.close();
      };
    }
  }, [isRealTime]);

  // Handle real-time updates
  const handleRealTimeUpdate = (data) => {
    if (data.type === "analysis_update") {
      setAnalysisData((prev) => ({
        ...prev,
        ...data.analysis,
        timestamp: Date.now(),
      }));
    }

    if (data.type === "conflict_detection") {
      setConflictLevel(data.urgency);
      if (data.urgency === "high" || data.urgency === "critical") {
        setActiveAlerts((prev) => [
          ...prev,
          {
            id: Date.now(),
            type: "conflict",
            urgency: data.urgency,
            message: data.message,
            timestamp: Date.now(),
          },
        ]);
      }
    }

    if (data.type === "emotional_state") {
      setEmotionalState(data.state);
    }

    if (data.type === "conversation_trend") {
      setConversationTrend(data.trend);
    }
  };

  // Mock data for demonstration
  const mockAnalysisData = {
    sentimentTrend: [
      { time: "10:00", positive: 0.7, negative: 0.2, neutral: 0.1 },
      { time: "10:15", positive: 0.6, negative: 0.3, neutral: 0.1 },
      { time: "10:30", positive: 0.5, negative: 0.4, neutral: 0.1 },
      { time: "10:45", positive: 0.4, negative: 0.5, neutral: 0.1 },
      { time: "11:00", positive: 0.6, negative: 0.3, neutral: 0.1 },
    ],
    communicationPatterns: [
      { pattern: "Active Listening", score: 85, change: 5 },
      { pattern: "Empathy", score: 72, change: -3 },
      { pattern: "Conflict Resolution", score: 68, change: 8 },
      { pattern: "Emotional Support", score: 91, change: 2 },
      { pattern: "Problem Solving", score: 76, change: -1 },
    ],
    emotionalBreakdown: [
      { emotion: "Joy", value: 35, color: "#10b981" },
      { emotion: "Neutral", value: 30, color: "#6b7280" },
      { emotion: "Concern", value: 20, color: "#f59e0b" },
      { emotion: "Frustration", value: 10, color: "#ef4444" },
      { emotion: "Anger", value: 5, color: "#dc2626" },
    ],
    conflictMetrics: {
      escalationRisk: 25,
      resolutionPotential: 78,
      interventionNeeded: false,
      lastIncident: "2 hours ago",
    },
    therapeuticInsights: [
      {
        type: "strength",
        title: "Strong Emotional Support",
        description: "Both parties show consistent empathy and validation",
        confidence: 0.89,
      },
      {
        type: "opportunity",
        title: "Improve Active Listening",
        description: "Consider pausing before responding to show understanding",
        confidence: 0.76,
      },
      {
        type: "warning",
        title: "Rising Tension Detected",
        description: "Communication pattern suggests increasing frustration",
        confidence: 0.82,
      },
    ],
  };

  const currentData = analysisData || mockAnalysisData;

  // Get conflict level color and icon
  const getConflictLevelInfo = (level) => {
    switch (level) {
      case "critical":
        return { color: "bg-red-500", icon: AlertTriangle, text: "Critical" };
      case "high":
        return { color: "bg-orange-500", icon: AlertTriangle, text: "High" };
      case "medium":
        return { color: "bg-yellow-500", icon: Zap, text: "Medium" };
      default:
        return { color: "bg-green-500", icon: Shield, text: "Low" };
    }
  };

  const conflictInfo = getConflictLevelInfo(conflictLevel);

  // Get trend icon
  const getTrendIcon = (trend) => {
    switch (trend) {
      case "escalating":
        return { icon: TrendingUp, color: "text-red-500" };
      case "de_escalating":
        return { icon: TrendingDown, color: "text-green-500" };
      case "stable":
        return { icon: Activity, color: "text-blue-500" };
      default:
        return { icon: Activity, color: "text-gray-500" };
    }
  };

  const trendInfo = getTrendIcon(conversationTrend);

  return (
    <div className="space-y-6">
      {/* Real-time Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div
              className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"} animate-pulse`}
            />
            <span className="text-sm font-medium">
              {isConnected ? "Live Analysis Active" : "Disconnected"}
            </span>
          </div>
          <Badge variant="outline" className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>Last update: {new Date().toLocaleTimeString()}</span>
          </Badge>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange("1h")}
          >
            1H
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange("6h")}
          >
            6H
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedTimeRange("24h")}
          >
            24H
          </Button>
        </div>
      </div>

      {/* Active Alerts */}
      <AnimatePresence>
        {activeAlerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-2"
          >
            {activeAlerts.map((alert) => (
              <Alert
                key={alert.id}
                className={`border-l-4 ${
                  alert.urgency === "critical"
                    ? "border-red-500 bg-red-50"
                    : alert.urgency === "high"
                      ? "border-orange-500 bg-orange-50"
                      : "border-yellow-500 bg-yellow-50"
                }`}
              >
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>{alert.urgency.toUpperCase()} ALERT:</strong>{" "}
                  {alert.message}
                </AlertDescription>
              </Alert>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Conflict Level
                </p>
                <p className="text-2xl font-bold">{conflictInfo.text}</p>
              </div>
              <div className={`p-3 rounded-full ${conflictInfo.color}`}>
                <conflictInfo.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Emotional State
                </p>
                <p className="text-2xl font-bold capitalize">
                  {emotionalState}
                </p>
              </div>
              <div className="p-3 rounded-full bg-purple-500">
                <Heart className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Conversation Trend
                </p>
                <p className="text-2xl font-bold capitalize">
                  {conversationTrend.replace("_", " ")}
                </p>
              </div>
              <div className={`p-3 rounded-full bg-blue-500`}>
                <trendInfo.icon className={`w-6 h-6 text-white`} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Resolution Potential
                </p>
                <p className="text-2xl font-bold">
                  {currentData.conflictMetrics.resolutionPotential}%
                </p>
              </div>
              <div className="p-3 rounded-full bg-green-500">
                <Target className="w-6 h-6 text-white" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis Tabs */}
      <Tabs defaultValue="sentiment" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger
            value="sentiment"
            className="flex items-center space-x-2"
          >
            <LineChartIcon className="w-4 h-4" />
            <span>Sentiment</span>
          </TabsTrigger>
          <TabsTrigger value="patterns" className="flex items-center space-x-2">
            <RadarIcon className="w-4 h-4" />
            <span>Patterns</span>
          </TabsTrigger>
          <TabsTrigger value="emotions" className="flex items-center space-x-2">
            <PieChartIcon className="w-4 h-4" />
            <span>Emotions</span>
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center space-x-2">
            <Brain className="w-4 h-4" />
            <span>Insights</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sentiment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sentiment Trend Analysis</CardTitle>
              <CardDescription>
                Real-time sentiment tracking over the conversation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={currentData.sentimentTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="positive"
                    stackId="1"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="neutral"
                    stackId="1"
                    stroke="#6b7280"
                    fill="#6b7280"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="negative"
                    stackId="1"
                    stroke="#ef4444"
                    fill="#ef4444"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Communication Patterns</CardTitle>
              <CardDescription>
                Analysis of communication effectiveness and style
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {currentData.communicationPatterns.map((pattern, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">
                          {pattern.pattern}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">
                            {pattern.score}%
                          </span>
                          <Badge
                            variant={
                              pattern.change > 0 ? "default" : "destructive"
                            }
                            className="text-xs"
                          >
                            {pattern.change > 0 ? "+" : ""}
                            {pattern.change}%
                          </Badge>
                        </div>
                      </div>
                      <Progress value={pattern.score} className="h-2" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="emotions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Emotional Breakdown</CardTitle>
              <CardDescription>
                Distribution of emotional states in the conversation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={currentData.emotionalBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ emotion, value }) => `${emotion}: ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {currentData.emotionalBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid gap-4">
            {currentData.therapeuticInsights.map((insight, index) => (
              <Card
                key={index}
                className={`border-l-4 ${
                  insight.type === "strength"
                    ? "border-green-500"
                    : insight.type === "opportunity"
                      ? "border-blue-500"
                      : "border-orange-500"
                }`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                    <Badge
                      variant={
                        insight.type === "warning" ? "destructive" : "default"
                      }
                    >
                      {insight.type}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-2">{insight.description}</p>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Confidence:</span>
                    <Progress
                      value={insight.confidence * 100}
                      className="flex-1 h-2"
                    />
                    <span className="text-sm font-medium">
                      {Math.round(insight.confidence * 100)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RealTimeAnalysisDashboard;
