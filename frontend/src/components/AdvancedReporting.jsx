import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { DatePickerWithRange } from "./ui/date-range-picker";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
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
  ScatterChart,
  Scatter,
  AreaChart,
  Area,
} from "recharts";
import {
  FileText,
  Download,
  Loader2,
  BarChart3,
  PieChart as PieChartIcon,
  TrendingUp,
  Users,
  MessageCircle,
  Heart,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { format } from "date-fns";

const AdvancedReporting = () => {
  const [reportType, setReportType] = useState("");
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [selectedParticipants, setSelectedParticipants] = useState([]);
  const [selectedMetrics, setSelectedMetrics] = useState([]);
  const [selectedVisualizations, setSelectedVisualizations] = useState([]);
  const [exportFormat, setExportFormat] = useState("json");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [reportData, setReportData] = useState(null);
  const [error, setError] = useState(null);
  const [availableOptions, setAvailableOptions] = useState({
    reportTypes: [],
    exportFormats: [],
    participants: [],
    metrics: [],
    visualizations: [],
  });
  const { toast } = useToast();

  // Load available options on component mount
  useEffect(() => {
    loadAvailableOptions();
  }, []);

  const loadAvailableOptions = async () => {
    try {
      const [typesResponse, formatsResponse] = await Promise.all([
        fetch("/api/v1/advanced/report/types", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }),
        fetch("/api/v1/advanced/report/formats", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }),
      ]);

      if (typesResponse.ok && formatsResponse.ok) {
        const types = await typesResponse.json();
        const formats = await formatsResponse.json();

        setAvailableOptions((prev) => ({
          ...prev,
          reportTypes: types,
          exportFormats: formats,
          participants: ["Alice", "Bob", "Charlie", "Diana"], // Mock data
          metrics: [
            "sentiment_analysis",
            "communication_patterns",
            "relationship_health",
            "conflict_detection",
            "emotional_indicators",
            "conversation_flow",
            "response_times",
            "message_frequency",
            "topic_analysis",
            "engagement_levels",
          ],
          visualizations: [
            "sentiment_timeline",
            "communication_heatmap",
            "relationship_radar",
            "conflict_indicators",
            "emotional_flow",
            "participant_activity",
            "topic_distribution",
            "response_patterns",
            "engagement_trends",
          ],
        }));
      }
    } catch (error) {
      console.error("Error loading options:", error);
    }
  };

  const handleParticipantToggle = (participant) => {
    setSelectedParticipants((prev) =>
      prev.includes(participant)
        ? prev.filter((p) => p !== participant)
        : [...prev, participant]
    );
  };

  const handleMetricToggle = (metric) => {
    setSelectedMetrics((prev) =>
      prev.includes(metric)
        ? prev.filter((m) => m !== metric)
        : [...prev, metric]
    );
  };

  const handleVisualizationToggle = (visualization) => {
    setSelectedVisualizations((prev) =>
      prev.includes(visualization)
        ? prev.filter((v) => v !== visualization)
        : [...prev, visualization]
    );
  };

  const generateReport = async () => {
    if (!reportType) {
      setError("Please select a report type.");
      return;
    }

    setIsGenerating(true);
    setGenerationProgress(0);
    setError(null);
    setReportData(null);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress((prev) => Math.min(prev + 15, 90));
      }, 300);

      const requestBody = {
        report_type: reportType,
        time_range:
          dateRange.from && dateRange.to
            ? [
                format(dateRange.from, "yyyy-MM-dd"),
                format(dateRange.to, "yyyy-MM-dd"),
              ]
            : null,
        participants:
          selectedParticipants.length > 0 ? selectedParticipants : null,
        metrics: selectedMetrics.length > 0 ? selectedMetrics : null,
        visualizations:
          selectedVisualizations.length > 0 ? selectedVisualizations : null,
        export_format: exportFormat,
        custom_config: {},
      };

      const response = await fetch("/api/v1/advanced/report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(requestBody),
      });

      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (response.ok) {
        const result = await response.json();
        setReportData(result);
        toast({
          title: "Report Generated",
          description: "Your advanced report has been generated successfully.",
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Report generation failed");
      }
    } catch (error) {
      console.error("Report generation error:", error);
      setError(error.message);
      toast({
        title: "Report Generation Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
      setTimeout(() => setGenerationProgress(0), 1000);
    }
  };

  const downloadReport = () => {
    if (!reportData) return;

    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `advanced_report_${reportType}_${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderVisualization = (vizData, type) => {
    const colors = [
      "#8884d8",
      "#82ca9d",
      "#ffc658",
      "#ff7300",
      "#00ff00",
      "#ff00ff",
    ];

    switch (type) {
      case "sentiment_timeline":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={vizData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="sentiment"
                stroke="#8884d8"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "communication_heatmap":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vizData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="participant" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="messages" fill="#8884d8" />
              <Bar dataKey="responses" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        );

      case "relationship_radar":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={vizData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 1]} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
              />
            </RadarChart>
          </ResponsiveContainer>
        );

      case "emotional_flow":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={vizData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="positive"
                stackId="1"
                stroke="#82ca9d"
                fill="#82ca9d"
              />
              <Area
                type="monotone"
                dataKey="neutral"
                stackId="1"
                stroke="#ffc658"
                fill="#ffc658"
              />
              <Area
                type="monotone"
                dataKey="negative"
                stackId="1"
                stroke="#ff7300"
                fill="#ff7300"
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case "topic_distribution":
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={vizData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {vizData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return (
          <div className="flex items-center justify-center h-64 text-gray-500">
            Visualization not implemented: {type}
          </div>
        );
    }
  };

  const getSampleVisualizationData = (type) => {
    switch (type) {
      case "sentiment_timeline":
        return [
          { time: "10:00", sentiment: 0.2 },
          { time: "10:30", sentiment: -0.1 },
          { time: "11:00", sentiment: 0.5 },
          { time: "11:30", sentiment: 0.3 },
          { time: "12:00", sentiment: 0.7 },
        ];

      case "communication_heatmap":
        return [
          { participant: "Alice", messages: 45, responses: 38 },
          { participant: "Bob", messages: 52, responses: 41 },
          { participant: "Charlie", messages: 23, responses: 19 },
        ];

      case "relationship_radar":
        return [
          { metric: "Trust", value: 0.8 },
          { metric: "Communication", value: 0.6 },
          { metric: "Empathy", value: 0.7 },
          { metric: "Conflict Resolution", value: 0.5 },
          { metric: "Emotional Support", value: 0.9 },
        ];

      case "emotional_flow":
        return [
          { time: "10:00", positive: 0.3, neutral: 0.5, negative: 0.2 },
          { time: "10:30", positive: 0.2, neutral: 0.4, negative: 0.4 },
          { time: "11:00", positive: 0.6, neutral: 0.3, negative: 0.1 },
          { time: "11:30", positive: 0.4, neutral: 0.4, negative: 0.2 },
          { time: "12:00", positive: 0.7, neutral: 0.2, negative: 0.1 },
        ];

      case "topic_distribution":
        return [
          { name: "Work", value: 35 },
          { name: "Family", value: 25 },
          { name: "Hobbies", value: 20 },
          { name: "Plans", value: 15 },
          { name: "Other", value: 5 },
        ];

      default:
        return [];
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Advanced Reporting & Visualizations
          </CardTitle>
          <CardDescription>
            Generate comprehensive reports with advanced analytics and
            interactive visualizations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="report-type">Report Type</Label>
              <Select value={reportType} onValueChange={setReportType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  {availableOptions.reportTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type
                        .replace("_", " ")
                        .replace(/\b\w/g, (l) => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="export-format">Export Format</Label>
              <Select value={exportFormat} onValueChange={setExportFormat}>
                <SelectTrigger>
                  <SelectValue placeholder="Select export format" />
                </SelectTrigger>
                <SelectContent>
                  {availableOptions.exportFormats.map((format) => (
                    <SelectItem key={format} value={format}>
                      {format.toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Date Range (Optional)</Label>
            <DatePickerWithRange
              date={dateRange}
              onDateChange={setDateRange}
              className="w-full"
            />
          </div>

          <Tabs defaultValue="participants" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="participants">Participants</TabsTrigger>
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
              <TabsTrigger value="visualizations">Visualizations</TabsTrigger>
            </TabsList>

            <TabsContent value="participants" className="space-y-4">
              <div className="space-y-2">
                <Label>Filter by Participants (Optional)</Label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {availableOptions.participants.map((participant) => (
                    <div
                      key={participant}
                      className="flex items-center space-x-2"
                    >
                      <Checkbox
                        id={`participant-${participant}`}
                        checked={selectedParticipants.includes(participant)}
                        onCheckedChange={() =>
                          handleParticipantToggle(participant)
                        }
                      />
                      <Label
                        htmlFor={`participant-${participant}`}
                        className="text-sm"
                      >
                        {participant}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="metrics" className="space-y-4">
              <div className="space-y-2">
                <Label>Select Metrics (Optional)</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {availableOptions.metrics.map((metric) => (
                    <div key={metric} className="flex items-center space-x-2">
                      <Checkbox
                        id={`metric-${metric}`}
                        checked={selectedMetrics.includes(metric)}
                        onCheckedChange={() => handleMetricToggle(metric)}
                      />
                      <Label htmlFor={`metric-${metric}`} className="text-sm">
                        {metric
                          .replace("_", " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="visualizations" className="space-y-4">
              <div className="space-y-2">
                <Label>Select Visualizations (Optional)</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {availableOptions.visualizations.map((visualization) => (
                    <div
                      key={visualization}
                      className="flex items-center space-x-2"
                    >
                      <Checkbox
                        id={`viz-${visualization}`}
                        checked={selectedVisualizations.includes(visualization)}
                        onCheckedChange={() =>
                          handleVisualizationToggle(visualization)
                        }
                      />
                      <Label
                        htmlFor={`viz-${visualization}`}
                        className="text-sm"
                      >
                        {visualization
                          .replace("_", " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isGenerating && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Generating report...</span>
                <span>{generationProgress}%</span>
              </div>
              <Progress value={generationProgress} className="w-full" />
            </div>
          )}

          <Button
            onClick={generateReport}
            disabled={isGenerating || !reportType}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Report...
              </>
            ) : (
              <>
                <FileText className="h-4 w-4 mr-2" />
                Generate Report
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {reportData && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Report Summary</span>
                <Button variant="outline" size="sm" onClick={downloadReport}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {reportData.summary?.total_messages || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total Messages</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {reportData.summary?.participants || 0}
                  </div>
                  <div className="text-sm text-gray-600">Participants</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {reportData.summary?.avg_sentiment?.toFixed(2) || "0.00"}
                  </div>
                  <div className="text-sm text-gray-600">Avg Sentiment</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {reportData.summary?.relationship_health?.toFixed(1) ||
                      "0.0"}
                  </div>
                  <div className="text-sm text-gray-600">Health Score</div>
                </div>
              </div>

              {reportData.insights && (
                <div className="space-y-2">
                  <Label>Key Insights</Label>
                  <div className="space-y-2">
                    {reportData.insights.map((insight, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-2 p-3 bg-blue-50 rounded-md"
                      >
                        <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                        <span className="text-sm">{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {reportData.visualizations && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(reportData.visualizations).map(
                ([vizType, vizData]) => (
                  <Card key={vizType}>
                    <CardHeader>
                      <CardTitle className="text-lg">
                        {vizType
                          .replace("_", " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {renderVisualization(
                        getSampleVisualizationData(vizType),
                        vizType
                      )}
                    </CardContent>
                  </Card>
                )
              )}
            </div>
          )}

          {reportData.generation_time && (
            <div className="text-sm text-gray-600 text-center">
              Report generated in {reportData.generation_time}ms
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedReporting;
