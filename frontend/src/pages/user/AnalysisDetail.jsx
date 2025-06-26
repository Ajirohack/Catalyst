import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  useSpecificAnalysis,
  useAnalysisMetrics,
} from "../../hooks/useAnalysis";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "../../components/ui/tabs";
import {
  LineChart,
  Line,
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
} from "recharts";

/**
 * Component that displays detailed analysis results
 */
const AnalysisDetail = () => {
  const { projectId, analysisId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("summary");

  const {
    data: analysis,
    isLoading: isAnalysisLoading,
    isError: isAnalysisError,
    error: analysisError,
  } = useSpecificAnalysis(projectId, analysisId);

  const {
    data: metrics,
    isLoading: isMetricsLoading,
    isError: isMetricsError,
  } = useAnalysisMetrics(projectId, analysisId);

  // Handle tab change
  const handleTabChange = (value) => {
    setActiveTab(value);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Get status badge
  const getStatusBadge = (status) => {
    let className = "";
    switch (status) {
      case "completed":
        className = "bg-green-100 text-green-800";
        break;
      case "in_progress":
        className = "bg-blue-100 text-blue-800";
        break;
      case "failed":
        className = "bg-red-100 text-red-800";
        break;
      default:
        className = "bg-gray-100 text-gray-800";
    }

    return (
      <Badge className={className}>
        {status === "in_progress"
          ? "In Progress"
          : status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  // Define chart colors
  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

  if (isAnalysisLoading || isMetricsLoading) {
    return (
      <div className="container max-w-6xl py-10">
        <div className="text-center py-12">
          <div className="spinner mb-4"></div>
          <p>Loading analysis data...</p>
        </div>
      </div>
    );
  }

  if (isAnalysisError || isMetricsError) {
    return (
      <div className="container max-w-6xl py-10">
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-red-500 mb-4">
                Failed to load analysis:{" "}
                {analysisError?.message || "Unknown error"}
              </p>
              <Button onClick={() => navigate(`/projects/${projectId}`)}>
                Back to Project
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container max-w-6xl py-10">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Analysis Results</h1>
          <p className="text-gray-500">Project ID: {projectId}</p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate(`/projects/${projectId}`)}
        >
          Back to Project
        </Button>
      </div>

      {/* Analysis Header Card */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Analysis Details</CardTitle>
            {analysis && getStatusBadge(analysis.status)}
          </div>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Analysis ID</dt>
              <dd className="mt-1">{analysisId.substring(0, 8)}...</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Started</dt>
              <dd className="mt-1">{formatDate(analysis?.created_at)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Completed</dt>
              <dd className="mt-1">{formatDate(analysis?.completed_at)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Duration</dt>
              <dd className="mt-1">{analysis?.duration || "N/A"}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      {/* Tabs for different analysis views */}
      <Tabs
        defaultValue="summary"
        onValueChange={handleTabChange}
        className="mb-6"
      >
        <TabsList className="mb-6">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
          <TabsTrigger value="raw">Raw Data</TabsTrigger>
        </TabsList>

        {/* Summary Tab */}
        <TabsContent value="summary">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Findings */}
            <Card>
              <CardHeader>
                <CardTitle>Key Findings</CardTitle>
                <CardDescription>
                  Main insights from the analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {analysis?.summary ? (
                  <div className="space-y-4">
                    <p>{analysis.summary}</p>
                    {analysis.key_findings && (
                      <ul className="list-disc pl-5 space-y-2">
                        {analysis.key_findings.map((finding, index) => (
                          <li key={index}>{finding}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No summary available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Top Metrics Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Top Metrics</CardTitle>
                <CardDescription>Key performance indicators</CardDescription>
              </CardHeader>
              <CardContent>
                {metrics?.key_metrics ? (
                  <div className="space-y-6">
                    {Object.entries(metrics.key_metrics).map(
                      ([key, value], index) => (
                        <div key={key}>
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium capitalize">
                              {key.replace(/_/g, " ")}
                            </span>
                            <span className="text-sm">
                              {typeof value === "number" ? `${value}%` : value}
                            </span>
                          </div>
                          {typeof value === "number" && (
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div
                                className="h-2.5 rounded-full"
                                style={{
                                  width: `${value}%`,
                                  backgroundColor:
                                    COLORS[index % COLORS.length],
                                }}
                              ></div>
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No metrics available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Conversation Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Conversation Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                {metrics?.conversation_stats ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">
                        Total Messages
                      </div>
                      <div className="text-2xl font-bold">
                        {metrics.conversation_stats.total_messages || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Participants</div>
                      <div className="text-2xl font-bold">
                        {metrics.conversation_stats.participant_count || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">
                        Avg. Response Time
                      </div>
                      <div className="text-2xl font-bold">
                        {metrics.conversation_stats.avg_response_time || "N/A"}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">
                        Total Duration
                      </div>
                      <div className="text-2xl font-bold">
                        {metrics.conversation_stats.duration || "N/A"}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No conversation statistics available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Sentiment Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Sentiment Overview</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                {metrics?.sentiment_data ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          {
                            name: "Positive",
                            value: metrics.sentiment_data.positive || 0,
                          },
                          {
                            name: "Neutral",
                            value: metrics.sentiment_data.neutral || 0,
                          },
                          {
                            name: "Negative",
                            value: metrics.sentiment_data.negative || 0,
                          },
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) =>
                          `${name}: ${(percent * 100).toFixed(0)}%`
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {[
                          { name: "Positive", color: "#4caf50" },
                          { name: "Neutral", color: "#2196f3" },
                          { name: "Negative", color: "#f44336" },
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No sentiment data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics">
          <div className="grid grid-cols-1 gap-6">
            {/* Engagement Over Time */}
            <Card>
              <CardHeader>
                <CardTitle>Engagement Over Time</CardTitle>
                <CardDescription>
                  Message frequency and engagement patterns
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                {metrics?.time_series_data ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={metrics.time_series_data.map((d) => ({
                        ...d,
                        date: new Date(d.timestamp).toLocaleDateString(),
                      }))}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="message_count"
                        name="Message Count"
                        stroke="#8884d8"
                        activeDot={{ r: 8 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="engagement_score"
                        name="Engagement"
                        stroke="#82ca9d"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No time series data available
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Communication Patterns */}
            <Card>
              <CardHeader>
                <CardTitle>Communication Patterns</CardTitle>
                <CardDescription>
                  Distribution of communication behaviors
                </CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                {metrics?.communication_patterns ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(metrics.communication_patterns).map(
                        ([key, value]) => ({
                          pattern: key
                            .replace(/_/g, " ")
                            .replace(/\b\w/g, (l) => l.toUpperCase()),
                          value,
                        })
                      )}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="pattern" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" name="Frequency" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    No communication pattern data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Insights</CardTitle>
              <CardDescription>In-depth analysis findings</CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.insights ? (
                <div className="space-y-6">
                  {analysis.insights.map((insight, index) => (
                    <div
                      key={index}
                      className="border-b pb-4 mb-4 last:border-b-0"
                    >
                      <div className="flex items-center mb-2">
                        <Badge
                          className={
                            insight.type === "positive"
                              ? "bg-green-100 text-green-800"
                              : insight.type === "negative"
                                ? "bg-red-100 text-red-800"
                                : insight.type === "opportunity"
                                  ? "bg-blue-100 text-blue-800"
                                  : "bg-gray-100 text-gray-800"
                          }
                        >
                          {insight.type.charAt(0).toUpperCase() +
                            insight.type.slice(1)}
                        </Badge>
                        {insight.importance && (
                          <Badge variant="outline" className="ml-2">
                            Priority: {insight.importance}
                          </Badge>
                        )}
                      </div>
                      <h3 className="text-lg font-medium mb-2">
                        {insight.title}
                      </h3>
                      <p className="text-gray-700 mb-2">
                        {insight.description}
                      </p>
                      {insight.evidence && (
                        <div className="bg-gray-50 p-3 rounded-md mt-2 text-sm">
                          <div className="font-medium mb-1">Evidence:</div>
                          <p className="text-gray-600">{insight.evidence}</p>
                        </div>
                      )}
                      {insight.recommendation && (
                        <div className="mt-3">
                          <div className="font-medium">Recommendation:</div>
                          <p className="text-gray-700">
                            {insight.recommendation}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No detailed insights available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Suggestions Tab */}
        <TabsContent value="suggestions">
          <Card>
            <CardHeader>
              <CardTitle>Improvement Suggestions</CardTitle>
              <CardDescription>
                Actionable recommendations to improve communication
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis?.suggestions && analysis.suggestions.length > 0 ? (
                <div className="space-y-4">
                  {analysis.suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-4 hover:bg-gray-50"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium mb-2">
                            {suggestion.title}
                          </h3>
                          <p className="text-gray-700 mb-3">
                            {suggestion.description}
                          </p>
                          {suggestion.example && (
                            <div className="bg-gray-100 p-3 rounded-md text-sm mb-3">
                              <div className="font-medium mb-1">Example:</div>
                              <div className="flex flex-col space-y-2">
                                {suggestion.example.before && (
                                  <div>
                                    <span className="text-red-500">
                                      ❌ Instead of:
                                    </span>
                                    <p className="ml-5 text-gray-700">
                                      {suggestion.example.before}
                                    </p>
                                  </div>
                                )}
                                {suggestion.example.after && (
                                  <div>
                                    <span className="text-green-500">
                                      ✓ Try:
                                    </span>
                                    <p className="ml-5 text-gray-700">
                                      {suggestion.example.after}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                        <Badge
                          className={
                            suggestion.difficulty === "easy"
                              ? "bg-green-100 text-green-800"
                              : suggestion.difficulty === "medium"
                                ? "bg-yellow-100 text-yellow-800"
                                : suggestion.difficulty === "hard"
                                  ? "bg-red-100 text-red-800"
                                  : "bg-gray-100 text-gray-800"
                          }
                        >
                          {suggestion.difficulty?.charAt(0).toUpperCase() +
                            suggestion.difficulty?.slice(1) || "Normal"}
                        </Badge>
                      </div>
                      {suggestion.benefits && (
                        <div className="mt-3">
                          <div className="font-medium mb-1">Benefits:</div>
                          <ul className="list-disc pl-5 space-y-1">
                            {suggestion.benefits.map((benefit, bidx) => (
                              <li key={bidx} className="text-sm text-gray-700">
                                {benefit}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No suggestions available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Raw Data Tab */}
        <TabsContent value="raw">
          <Card>
            <CardHeader>
              <CardTitle>Raw Analysis Data</CardTitle>
              <CardDescription>
                Complete analysis output for technical review
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-[500px]">
                <pre className="text-xs">
                  {JSON.stringify(analysis, null, 2)}
                </pre>
              </div>
              <div className="mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    const dataStr = JSON.stringify(analysis, null, 2);
                    const blob = new Blob([dataStr], {
                      type: "application/json",
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.download = `analysis-${analysisId}.json`;
                    a.href = url;
                    a.click();
                  }}
                >
                  Download Raw Data
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex space-x-4 mt-8">
        <Button onClick={() => navigate(`/projects/${projectId}`)}>
          Back to Project
        </Button>
        <Button variant="outline" onClick={() => window.print()}>
          Print Report
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            // Handle export functionality
            alert("Export functionality would be implemented here");
          }}
        >
          Export Report
        </Button>
      </div>
    </div>
  );
};

export default AnalysisDetail;
