import React from "react";
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
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useAnalysisDetails, useAnalysisMetrics } from "@/hooks/useAnalysis";

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884D8",
  "#FF6B6B",
];

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

export default function AnalysisResults({ projectId, analysisId }) {
  const {
    data: analysis,
    isLoading: analysisLoading,
    error: analysisError,
  } = useAnalysisDetails(analysisId);
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useAnalysisMetrics(projectId, analysisId);

  if (analysisLoading || metricsLoading) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">Loading analysis results...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (analysisError || metricsError) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center text-red-500">
            <p>Error loading analysis results.</p>
            <p className="text-sm mt-2">
              {analysisError?.message || metricsError?.message}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">No analysis data available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Analysis Overview */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Analysis Overview</CardTitle>
                <CardDescription>
                  Analysis completed on {formatDate(analysis.completed_at)}
                </CardDescription>
              </div>
              <Badge
                className={
                  analysis.quality_score > 80
                    ? "bg-green-100 text-green-800"
                    : analysis.quality_score > 60
                      ? "bg-amber-100 text-amber-800"
                      : "bg-red-100 text-red-800"
                }
              >
                Score: {analysis.quality_score}/100
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-muted/20 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">
                  Conversations
                </p>
                <p className="text-2xl font-bold">
                  {analysis.conversation_count}
                </p>
              </div>
              <div className="bg-muted/20 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Messages</p>
                <p className="text-2xl font-bold">{analysis.message_count}</p>
              </div>
              <div className="bg-muted/20 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">
                  Time Period
                </p>
                <p className="text-2xl font-bold">
                  {analysis.time_period} days
                </p>
              </div>
              <div className="bg-muted/20 p-4 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Insights</p>
                <p className="text-2xl font-bold">{analysis.insight_count}</p>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Summary</h3>
              <p>{analysis.summary}</p>

              <div className="mt-4 space-y-1">
                {analysis.key_findings.map((finding, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <div className="h-5 w-5 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 mt-0.5">
                      {index + 1}
                    </div>
                    <p>{finding}</p>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Detailed Analysis Tabs */}
      <motion.div variants={itemVariants}>
        <Tabs defaultValue="sentiment">
          <TabsList className="w-full">
            <TabsTrigger value="sentiment" className="flex-1">
              Sentiment Analysis
            </TabsTrigger>
            <TabsTrigger value="topics" className="flex-1">
              Topic Breakdown
            </TabsTrigger>
            <TabsTrigger value="patterns" className="flex-1">
              Communication Patterns
            </TabsTrigger>
            <TabsTrigger value="suggestions" className="flex-1">
              Suggestions
            </TabsTrigger>
          </TabsList>

          {/* Sentiment Analysis Tab */}
          <TabsContent value="sentiment">
            <Card>
              <CardHeader>
                <CardTitle>Sentiment Over Time</CardTitle>
                <CardDescription>
                  How emotional tone has changed over the analyzed period
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metrics?.sentiment_over_time || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="positive"
                        stroke="#00C49F"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="neutral"
                        stroke="#8884D8"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="negative"
                        stroke="#FF8042"
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <h4 className="text-sm font-semibold mb-4">
                      Sentiment Distribution
                    </h4>
                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={metrics?.sentiment_distribution || []}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {metrics?.sentiment_distribution?.map(
                              (entry, index) => (
                                <Cell
                                  key={`cell-${index}`}
                                  fill={COLORS[index % COLORS.length]}
                                />
                              )
                            )}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-4">
                      Key Sentiment Metrics
                    </h4>
                    <div className="space-y-4">
                      {metrics?.sentiment_metrics?.map((metric, index) => (
                        <div key={index}>
                          <div className="flex justify-between mb-1">
                            <p className="text-sm">{metric.name}</p>
                            <p className="text-sm font-medium">
                              {metric.value}/10
                            </p>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary"
                              style={{ width: `${metric.value * 10}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Topic Breakdown Tab */}
          <TabsContent value="topics">
            <Card>
              <CardHeader>
                <CardTitle>Conversation Topics</CardTitle>
                <CardDescription>
                  Main themes and topics discussed during conversations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={metrics?.topic_distribution || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="topic" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="frequency" fill="#8884D8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="mt-8">
                  <h4 className="text-sm font-semibold mb-4">Topic Details</h4>
                  <div className="space-y-4">
                    {metrics?.topic_details?.map((topic, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex justify-between">
                          <h5 className="font-medium">{topic.name}</h5>
                          <Badge>{topic.frequency}%</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-2">
                          {topic.description}
                        </p>

                        <div className="mt-3">
                          <h6 className="text-xs font-medium mb-2">
                            Common phrases:
                          </h6>
                          <div className="flex flex-wrap gap-2">
                            {topic.key_phrases.map((phrase, idx) => (
                              <Badge key={idx} variant="outline">
                                {phrase}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Communication Patterns Tab */}
          <TabsContent value="patterns">
            <Card>
              <CardHeader>
                <CardTitle>Communication Patterns</CardTitle>
                <CardDescription>
                  Analysis of how you communicate with each other
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  <div>
                    <h4 className="text-sm font-semibold mb-4">
                      Message Frequency by Time
                    </h4>
                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={metrics?.message_frequency_by_time || []}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="hour" />
                          <YAxis />
                          <Tooltip />
                          <Area
                            type="monotone"
                            dataKey="count"
                            fill="#8884D8"
                            stroke="#8884D8"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-4">
                      Response Time Distribution
                    </h4>
                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={metrics?.response_time_distribution || []}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="range" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="percentage" fill="#00C49F" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold mb-4">
                    Communication Style Analysis
                  </h4>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart
                        outerRadius={90}
                        data={metrics?.communication_style || []}
                      >
                        <PolarGrid />
                        <PolarAngleAxis dataKey="trait" />
                        <PolarRadiusAxis domain={[0, 10]} />
                        <Radar
                          name="Person 1"
                          dataKey="person1"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.6}
                        />
                        <Radar
                          name="Person 2"
                          dataKey="person2"
                          stroke="#82ca9d"
                          fill="#82ca9d"
                          fillOpacity={0.6}
                        />
                        <Legend />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Suggestions Tab */}
          <TabsContent value="suggestions">
            <Card>
              <CardHeader>
                <CardTitle>Improvement Suggestions</CardTitle>
                <CardDescription>
                  Personalized recommendations based on your communication
                  patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {metrics?.suggestions?.map((suggestion, index) => (
                    <div key={index} className="border rounded-lg p-5">
                      <div className="flex gap-4 items-start">
                        <div
                          className={`h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                            suggestion.priority === "high"
                              ? "bg-red-100 text-red-600"
                              : suggestion.priority === "medium"
                                ? "bg-amber-100 text-amber-600"
                                : "bg-blue-100 text-blue-600"
                          }`}
                        >
                          {suggestion.priority === "high"
                            ? "!"
                            : suggestion.priority === "medium"
                              ? "+"
                              : "i"}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between">
                            <h4 className="font-semibold">
                              {suggestion.title}
                            </h4>
                            <Badge variant="outline" className="capitalize">
                              {suggestion.priority} priority
                            </Badge>
                          </div>
                          <p className="mt-2">{suggestion.description}</p>

                          <div className="mt-4 space-y-2">
                            <h5 className="text-sm font-medium">
                              Actions to take:
                            </h5>
                            <ul className="list-disc list-inside space-y-1 text-sm">
                              {suggestion.actions.map((action, idx) => (
                                <li key={idx}>{action}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}

                  {(!metrics?.suggestions ||
                    metrics.suggestions.length === 0) && (
                    <div className="text-center py-10">
                      <p className="text-muted-foreground">
                        No suggestions available for this analysis.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Export Actions */}
      <motion.div variants={itemVariants} className="flex justify-end">
        <Button className="mr-2" variant="outline">
          Export as PDF
        </Button>
        <Button>Share Results</Button>
      </motion.div>
    </motion.div>
  );
}
