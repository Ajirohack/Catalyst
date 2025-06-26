import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Shield,
  Zap,
  TrendingUp,
  TrendingDown,
  Clock,
  Users,
  MessageCircle,
  Brain,
  Heart,
  Target,
  Activity,
  CheckCircle,
  XCircle,
  Pause,
  Play,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { Alert, AlertDescription } from "../ui/alert";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/tabs";

const ConflictDetectionPanel = ({ projectId, onInterventionTrigger }) => {
  const [conflictLevel, setConflictLevel] = useState("low");
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [recentConflicts, setRecentConflicts] = useState([]);
  const [interventionHistory, setInterventionHistory] = useState([]);
  const [conflictPatterns, setConflictPatterns] = useState([]);
  const [escalationRisk, setEscalationRisk] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Mock data for demonstration
  const mockConflictData = {
    currentLevel: "medium",
    escalationRisk: 35,
    recentConflicts: [
      {
        id: 1,
        timestamp: new Date(Date.now() - 300000), // 5 minutes ago
        level: "high",
        trigger: "Criticism detected",
        participants: ["User A", "User B"],
        resolved: false,
        duration: 120, // seconds
        patterns: ["defensiveness", "criticism"],
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 900000), // 15 minutes ago
        level: "medium",
        trigger: "Emotional escalation",
        participants: ["User A", "User B"],
        resolved: true,
        duration: 45,
        patterns: ["frustration", "interruption"],
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
        level: "low",
        trigger: "Tone shift detected",
        participants: ["User A"],
        resolved: true,
        duration: 30,
        patterns: ["sarcasm"],
      },
    ],
    conflictPatterns: [
      {
        pattern: "Criticism",
        frequency: 8,
        trend: "increasing",
        severity: "high",
        lastOccurrence: "5 minutes ago",
      },
      {
        pattern: "Defensiveness",
        frequency: 12,
        trend: "stable",
        severity: "medium",
        lastOccurrence: "8 minutes ago",
      },
      {
        pattern: "Stonewalling",
        frequency: 3,
        trend: "decreasing",
        severity: "low",
        lastOccurrence: "2 hours ago",
      },
      {
        pattern: "Contempt",
        frequency: 1,
        trend: "stable",
        severity: "critical",
        lastOccurrence: "1 day ago",
      },
    ],
    interventionHistory: [
      {
        id: 1,
        timestamp: new Date(Date.now() - 300000),
        type: "automatic",
        intervention: "Breathing exercise suggestion",
        effectiveness: "high",
        userResponse: "accepted",
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 1200000),
        type: "manual",
        intervention: "Communication timeout",
        effectiveness: "medium",
        userResponse: "partially_followed",
      },
    ],
  };

  useEffect(() => {
    // Initialize with mock data
    setConflictLevel(mockConflictData.currentLevel);
    setEscalationRisk(mockConflictData.escalationRisk);
    setRecentConflicts(mockConflictData.recentConflicts);
    setConflictPatterns(mockConflictData.conflictPatterns);
    setInterventionHistory(mockConflictData.interventionHistory);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setLastUpdate(new Date());
      // Randomly update escalation risk
      setEscalationRisk((prev) =>
        Math.max(0, Math.min(100, prev + (Math.random() - 0.5) * 10))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getConflictLevelInfo = (level) => {
    switch (level) {
      case "critical":
        return {
          color: "bg-red-500",
          textColor: "text-red-700",
          bgColor: "bg-red-50",
          icon: AlertTriangle,
          text: "Critical",
          description: "Immediate intervention required",
        };
      case "high":
        return {
          color: "bg-orange-500",
          textColor: "text-orange-700",
          bgColor: "bg-orange-50",
          icon: AlertTriangle,
          text: "High",
          description: "Active conflict detected",
        };
      case "medium":
        return {
          color: "bg-yellow-500",
          textColor: "text-yellow-700",
          bgColor: "bg-yellow-50",
          icon: Zap,
          text: "Medium",
          description: "Tension building",
        };
      default:
        return {
          color: "bg-green-500",
          textColor: "text-green-700",
          bgColor: "bg-green-50",
          icon: Shield,
          text: "Low",
          description: "Conversation is healthy",
        };
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "increasing":
        return { icon: TrendingUp, color: "text-red-500" };
      case "decreasing":
        return { icon: TrendingDown, color: "text-green-500" };
      default:
        return { icon: Activity, color: "text-blue-500" };
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "critical":
        return "text-red-600 bg-red-100";
      case "high":
        return "text-orange-600 bg-orange-100";
      case "medium":
        return "text-yellow-600 bg-yellow-100";
      default:
        return "text-green-600 bg-green-100";
    }
  };

  const conflictInfo = getConflictLevelInfo(conflictLevel);

  const triggerIntervention = (type) => {
    const intervention = {
      id: Date.now(),
      timestamp: new Date(),
      type: "manual",
      intervention: type,
      effectiveness: "pending",
      userResponse: "pending",
    };

    setInterventionHistory((prev) => [intervention, ...prev]);

    if (onInterventionTrigger) {
      onInterventionTrigger(intervention);
    }
  };

  return (
    <div className="space-y-6">
      {/* Monitoring Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div
              className={`w-3 h-3 rounded-full ${isMonitoring ? "bg-green-500" : "bg-gray-400"} animate-pulse`}
            />
            <span className="text-sm font-medium">
              {isMonitoring ? "Conflict Detection Active" : "Monitoring Paused"}
            </span>
          </div>
          <Badge variant="outline" className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
          </Badge>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsMonitoring(!isMonitoring)}
          className="flex items-center space-x-2"
        >
          {isMonitoring ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{isMonitoring ? "Pause" : "Resume"}</span>
        </Button>
      </div>

      {/* Current Conflict Level */}
      <Card
        className={`border-l-4 border-l-${conflictInfo.color.replace("bg-", "")}`}
      >
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-full ${conflictInfo.color}`}>
                <conflictInfo.icon className="w-5 h-5 text-white" />
              </div>
              <div>
                <CardTitle className={conflictInfo.textColor}>
                  Conflict Level: {conflictInfo.text}
                </CardTitle>
                <CardDescription>{conflictInfo.description}</CardDescription>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{escalationRisk}%</div>
              <div className="text-sm text-gray-500">Escalation Risk</div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Escalation Risk</span>
                <span>{escalationRisk}%</span>
              </div>
              <Progress
                value={escalationRisk}
                className={`h-2 ${escalationRisk > 70 ? "bg-red-100" : escalationRisk > 40 ? "bg-yellow-100" : "bg-green-100"}`}
              />
            </div>

            {escalationRisk > 60 && (
              <Alert className="border-orange-200 bg-orange-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  High escalation risk detected. Consider immediate
                  intervention.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick Intervention Actions */}
      {conflictLevel !== "low" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="w-5 h-5" />
              <span>Quick Interventions</span>
            </CardTitle>
            <CardDescription>
              Immediate actions to help de-escalate the situation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <Button
                variant="outline"
                onClick={() => triggerIntervention("Breathing Exercise")}
                className="flex items-center space-x-2"
              >
                <Heart className="w-4 h-4" />
                <span>Breathing Exercise</span>
              </Button>
              <Button
                variant="outline"
                onClick={() => triggerIntervention("Communication Timeout")}
                className="flex items-center space-x-2"
              >
                <Pause className="w-4 h-4" />
                <span>Take a Break</span>
              </Button>
              <Button
                variant="outline"
                onClick={() => triggerIntervention("Active Listening Prompt")}
                className="flex items-center space-x-2"
              >
                <MessageCircle className="w-4 h-4" />
                <span>Active Listening</span>
              </Button>
              <Button
                variant="outline"
                onClick={() => triggerIntervention("Empathy Building")}
                className="flex items-center space-x-2"
              >
                <Users className="w-4 h-4" />
                <span>Empathy Building</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Analysis Tabs */}
      <Tabs defaultValue="recent" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="recent">Recent Conflicts</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="interventions">Interventions</TabsTrigger>
        </TabsList>

        <TabsContent value="recent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Conflict Events</CardTitle>
              <CardDescription>
                Timeline of detected conflicts and their resolution status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentConflicts.map((conflict) => {
                  const conflictInfo = getConflictLevelInfo(conflict.level);
                  return (
                    <motion.div
                      key={conflict.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`p-4 rounded-lg border ${conflictInfo.bgColor} border-l-4 border-l-${conflictInfo.color.replace("bg-", "")}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <conflictInfo.icon
                              className={`w-4 h-4 ${conflictInfo.textColor}`}
                            />
                            <span className="font-medium">
                              {conflict.trigger}
                            </span>
                            <Badge className={getSeverityColor(conflict.level)}>
                              {conflict.level}
                            </Badge>
                            {conflict.resolved ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <XCircle className="w-4 h-4 text-red-500" />
                            )}
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>
                              Participants: {conflict.participants.join(", ")}
                            </div>
                            <div>Duration: {conflict.duration}s</div>
                            <div>Patterns: {conflict.patterns.join(", ")}</div>
                          </div>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          {conflict.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Conflict Patterns Analysis</CardTitle>
              <CardDescription>
                Recurring patterns and their trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {conflictPatterns.map((pattern, index) => {
                  const trendInfo = getTrendIcon(pattern.trend);
                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{pattern.pattern}</span>
                          <Badge className={getSeverityColor(pattern.severity)}>
                            {pattern.severity}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="text-center">
                          <div className="font-medium">{pattern.frequency}</div>
                          <div className="text-gray-500">occurrences</div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <trendInfo.icon
                            className={`w-4 h-4 ${trendInfo.color}`}
                          />
                          <span className={trendInfo.color}>
                            {pattern.trend}
                          </span>
                        </div>
                        <div className="text-gray-500">
                          {pattern.lastOccurrence}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="interventions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Intervention History</CardTitle>
              <CardDescription>
                Past interventions and their effectiveness
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {interventionHistory.map((intervention) => (
                  <div key={intervention.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Brain className="w-4 h-4 text-blue-500" />
                        <span className="font-medium">
                          {intervention.intervention}
                        </span>
                        <Badge
                          variant={
                            intervention.type === "automatic"
                              ? "default"
                              : "secondary"
                          }
                        >
                          {intervention.type}
                        </Badge>
                      </div>
                      <span className="text-sm text-gray-500">
                        {intervention.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-600">Effectiveness:</span>
                        <Badge
                          className={
                            intervention.effectiveness === "high"
                              ? "bg-green-100 text-green-700"
                              : intervention.effectiveness === "medium"
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-gray-100 text-gray-700"
                          }
                        >
                          {intervention.effectiveness}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-gray-600">Response:</span>
                        <Badge variant="outline">
                          {intervention.userResponse.replace("_", " ")}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ConflictDetectionPanel;
