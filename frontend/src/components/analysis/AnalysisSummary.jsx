import React from "react";
import { motion } from "framer-motion";
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
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAnalysisHistory } from "@/hooks/useAnalysis";
import { Link } from "react-router-dom";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

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

export default function AnalysisSummary({ projectId }) {
  const {
    data: analysisHistory,
    isLoading,
    error,
  } = useAnalysisHistory(projectId);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">Loading analysis summary...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center text-red-500">
            <p>Error loading analysis summary.</p>
            <p className="text-sm mt-2">{error.message}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysisHistory || analysisHistory.length === 0) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">
              No analysis data available for this project.
            </p>
            <Button className="mt-4">Start your first analysis</Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Get the most recent completed analysis
  const latestAnalysis = analysisHistory.find((a) => a.status === "completed");

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

  // Extract sentiment trend data
  const sentimentTrend = latestAnalysis?.summary?.sentiment_trend || [
    { date: "Week 1", score: 65 },
    { date: "Week 2", score: 70 },
    { date: "Week 3", score: 68 },
    { date: "Week 4", score: 75 },
  ];

  // Extract topic distribution
  const topicDistribution = latestAnalysis?.summary?.topic_distribution || [
    { name: "Daily Life", value: 35 },
    { name: "Work", value: 25 },
    { name: "Family", value: 20 },
    { name: "Future Plans", value: 15 },
    { name: "Other", value: 5 },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Recent Analysis Overview */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Recent Analysis</CardTitle>
                <CardDescription>
                  {latestAnalysis
                    ? `Last analyzed on ${formatDate(latestAnalysis.completed_at)}`
                    : "No completed analysis yet"}
                </CardDescription>
              </div>
              {latestAnalysis && (
                <Badge
                  className={
                    latestAnalysis.quality_score > 80
                      ? "bg-green-100 text-green-800"
                      : latestAnalysis.quality_score > 60
                        ? "bg-amber-100 text-amber-800"
                        : "bg-red-100 text-red-800"
                  }
                >
                  Score: {latestAnalysis.quality_score}/100
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {latestAnalysis ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-muted/20 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">
                      Conversations
                    </p>
                    <p className="text-2xl font-bold">
                      {latestAnalysis.conversation_count}
                    </p>
                  </div>
                  <div className="bg-muted/20 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">
                      Messages
                    </p>
                    <p className="text-2xl font-bold">
                      {latestAnalysis.message_count}
                    </p>
                  </div>
                  <div className="bg-muted/20 p-4 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">
                      Insights
                    </p>
                    <p className="text-2xl font-bold">
                      {latestAnalysis.insight_count}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Sentiment Trend */}
                  <div>
                    <h4 className="text-sm font-semibold mb-3">
                      Sentiment Trend
                    </h4>
                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={sentimentTrend}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[0, 100]} />
                          <Tooltip />
                          <Line
                            type="monotone"
                            dataKey="score"
                            stroke="#8884d8"
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Topic Distribution */}
                  <div>
                    <h4 className="text-sm font-semibold mb-3">
                      Topic Distribution
                    </h4>
                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={topicDistribution}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={70}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {topicDistribution.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* Key Insights */}
                <div>
                  <h4 className="text-sm font-semibold mb-3">Key Insights</h4>
                  <div className="space-y-3">
                    {latestAnalysis.key_insights?.map((insight, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-start gap-3">
                          <div
                            className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                              insight.type === "positive"
                                ? "bg-green-100 text-green-600"
                                : insight.type === "negative"
                                  ? "bg-red-100 text-red-600"
                                  : "bg-blue-100 text-blue-600"
                            }`}
                          >
                            {insight.type === "positive"
                              ? "✓"
                              : insight.type === "negative"
                                ? "!"
                                : "i"}
                          </div>
                          <div>
                            <h5 className="font-medium">{insight.title}</h5>
                            <p className="text-sm text-muted-foreground">
                              {insight.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end mt-4">
                  <Link
                    to={`/projects/${projectId}/analysis/${latestAnalysis.id}`}
                  >
                    <Button>View Full Analysis</Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-muted-foreground">
                  No completed analysis available for this project.
                </p>
                <Button className="mt-4">Start your first analysis</Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Analysis History */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Analysis History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysisHistory.length > 0 ? (
                analysisHistory.map((analysis, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">Analysis #{analysis.id}</p>
                      <p className="text-sm text-muted-foreground">
                        {analysis.status === "completed"
                          ? `Completed on ${formatDate(analysis.completed_at)}`
                          : analysis.status === "in_progress"
                            ? "In progress"
                            : analysis.status === "failed"
                              ? "Failed"
                              : "Queued"}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge
                        className={
                          analysis.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : analysis.status === "in_progress"
                              ? "bg-blue-100 text-blue-800"
                              : analysis.status === "failed"
                                ? "bg-red-100 text-red-800"
                                : "bg-amber-100 text-amber-800"
                        }
                      >
                        {analysis.status === "completed"
                          ? "Completed"
                          : analysis.status === "in_progress"
                            ? "In Progress"
                            : analysis.status === "failed"
                              ? "Failed"
                              : "Queued"}
                      </Badge>

                      {analysis.status === "completed" && (
                        <Link
                          to={`/projects/${projectId}/analysis/${analysis.id}`}
                        >
                          <Button variant="outline" size="sm">
                            View
                          </Button>
                        </Link>
                      )}

                      {analysis.status === "in_progress" && (
                        <Link
                          to={`/projects/${projectId}/analysis/${analysis.id}/progress`}
                        >
                          <Button variant="outline" size="sm">
                            Track
                          </Button>
                        </Link>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6">
                  <p className="text-muted-foreground">
                    No analysis history found.
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
