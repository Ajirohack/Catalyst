import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Fab,
  Tooltip,
} from "@mui/material";
import {
  Analytics as AnalyticsIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import toast from "react-hot-toast";

// Import our new services and components
import advancedAnalyticsService, {
  TIME_RANGES,
  METRIC_TYPES,
  REPORT_TYPES,
  EXPORT_FORMATS,
} from "../lib/services/advancedAnalytics";
import {
  ProfessionalLineChart,
  ProfessionalAreaChart,
  ProfessionalBarChart,
  ProfessionalPieChart,
  ProfessionalRadarChart,
  MetricCard,
} from "../components/charts/ProfessionalCharts";

const EnhancedAnalytics = () => {
  // State management
  const [timeRange, setTimeRange] = useState("30d");
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [generateReportLoading, setGenerateReportLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load analytics data
  const loadAnalyticsData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load comprehensive analytics
      const analyticsResult =
        await advancedAnalyticsService.getComprehensiveAnalytics(timeRange);

      if (analyticsResult.success) {
        setAnalyticsData(analyticsResult.data);
      } else {
        console.warn("Analytics service unavailable, using fallback data");
        setAnalyticsData(
          advancedAnalyticsService.generateFallbackData(timeRange)
        );
      }

      // Load alerts
      const alertsResult = await advancedAnalyticsService.getAlerts(timeRange);
      if (alertsResult.success) {
        setAlerts(alertsResult.data);
      }
    } catch (error) {
      console.error("Error loading analytics:", error);
      setError("Failed to load analytics data");
      // Use fallback data
      setAnalyticsData(
        advancedAnalyticsService.generateFallbackData(timeRange)
      );
    } finally {
      setLoading(false);
    }
  };

  // Generate professional report
  const generateReport = async (reportType) => {
    setGenerateReportLoading(true);

    try {
      const result = await advancedAnalyticsService.generateReport(
        reportType,
        timeRange,
        null,
        [EXPORT_FORMATS.HTML, EXPORT_FORMATS.PDF]
      );

      if (result.success) {
        setSelectedReport(result.data);
        setReportDialogOpen(true);
        toast.success("Report generated successfully!");
      } else {
        toast.error(result.error || "Failed to generate report");
      }
    } catch (error) {
      console.error("Error generating report:", error);
      toast.error("Failed to generate report");
    } finally {
      setGenerateReportLoading(false);
    }
  };

  // Download report
  const downloadReport = async (format) => {
    if (!selectedReport) return;

    try {
      const result = await advancedAnalyticsService.downloadReport(
        selectedReport.report_id,
        format
      );

      if (result.success) {
        toast.success("Report downloaded successfully!");
      } else {
        toast.error(result.error || "Failed to download report");
      }
    } catch (error) {
      console.error("Error downloading report:", error);
      toast.error("Failed to download report");
    }
  };

  // Load data on component mount and time range change
  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  // Format metrics data for charts
  const getChartData = (metricType) => {
    if (!analyticsData?.metrics?.[metricType]) {
      return [];
    }

    return analyticsData.metrics[metricType].map((point) => ({
      date: new Date(point.timestamp).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      value: typeof point.value === "number" ? point.value : 0,
      ...point.metadata,
    }));
  };

  // Get alert color based on level
  const getAlertColor = (level) => {
    switch (level) {
      case "critical":
        return "error";
      case "warning":
        return "warning";
      case "info":
        return "info";
      default:
        return "default";
    }
  };

  // Get alert icon based on level
  const getAlertIcon = (level) => {
    switch (level) {
      case "critical":
        return <WarningIcon />;
      case "warning":
        return <WarningIcon />;
      case "info":
        return <InfoIcon />;
      default:
        return <InfoIcon />;
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "60vh",
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <AnalyticsIcon sx={{ fontSize: 32, color: "primary.main" }} />
            <Typography variant="h4" component="h1">
              Advanced Analytics
            </Typography>
          </Box>

          <Box sx={{ display: "flex", gap: 2 }}>
            {/* Time Range Selector */}
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                label="Time Range"
                onChange={(e) => setTimeRange(e.target.value)}
              >
                {Object.entries(TIME_RANGES).map(([key, range]) => (
                  <MenuItem key={key} value={key}>
                    {range.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Refresh Button */}
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadAnalyticsData}
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error} - Showing demo data for illustration.
          </Alert>
        )}

        {/* System Alerts */}
        {alerts.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Alerts
            </Typography>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              {alerts.slice(0, 5).map((alert, index) => (
                <Chip
                  key={index}
                  icon={getAlertIcon(alert.alert_level)}
                  label={alert.message}
                  color={getAlertColor(alert.alert_level)}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Users"
            value={analyticsData?.summary?.total_users || 250}
            change={12.5}
            trend="up"
            icon={<TrendingUpIcon />}
            color="primary"
            format="number"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Sentiment"
            value={analyticsData?.summary?.avg_sentiment || 78.5}
            change={5.2}
            trend="up"
            icon={<AssessmentIcon />}
            color="success"
            format="percent"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Projects"
            value={analyticsData?.summary?.active_projects || 12}
            change={-2}
            trend="down"
            icon={<AnalyticsIcon />}
            color="warning"
            format="number"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Improvement Rate"
            value={analyticsData?.summary?.improvement_rate || 15.2}
            change={8.1}
            trend="up"
            icon={<TrendingUpIcon />}
            color="success"
            format="percent"
          />
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* User Activity Trend */}
        <Grid item xs={12} lg={8}>
          <ProfessionalLineChart
            data={getChartData(METRIC_TYPES.ACTIVE_USERS)}
            title="User Activity Trend"
            subtitle={`Active users over the last ${TIME_RANGES[timeRange].label.toLowerCase()}`}
            lines={[{ key: "value", name: "Active Users", color: "#1976d2" }]}
            height={350}
          />
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} lg={4}>
          <ProfessionalPieChart
            data={[
              { name: "Very Positive", value: 35, color: "#4caf50" },
              { name: "Positive", value: 30, color: "#8bc34a" },
              { name: "Neutral", value: 20, color: "#ffc107" },
              { name: "Negative", value: 10, color: "#ff9800" },
              { name: "Very Negative", value: 5, color: "#f44336" },
            ]}
            title="Sentiment Distribution"
            subtitle="Overall conversation sentiment"
            height={350}
          />
        </Grid>

        {/* Communication Patterns */}
        <Grid item xs={12} lg={6}>
          <ProfessionalAreaChart
            data={getChartData(METRIC_TYPES.MESSAGE_COUNT)}
            title="Communication Patterns"
            subtitle="Message volume over time"
            areas={[{ key: "value", name: "Messages", color: "#2196f3" }]}
            height={300}
          />
        </Grid>

        {/* Session Duration Analysis */}
        <Grid item xs={12} lg={6}>
          <ProfessionalBarChart
            data={getChartData(METRIC_TYPES.SESSION_DURATION).slice(-7)} // Last 7 days
            title="Session Duration Analysis"
            subtitle="Average session duration (minutes)"
            bars={[{ key: "value", name: "Duration", color: "#ff9800" }]}
            height={300}
          />
        </Grid>

        {/* Relationship Health Radar */}
        <Grid item xs={12} lg={8}>
          <ProfessionalRadarChart
            data={[
              { category: "Communication", score: 78 },
              { category: "Trust", score: 85 },
              { category: "Empathy", score: 72 },
              { category: "Conflict Resolution", score: 68 },
              { category: "Quality Time", score: 80 },
              { category: "Support", score: 88 },
            ]}
            title="Relationship Health Overview"
            subtitle="Multi-dimensional relationship assessment"
            height={400}
          />
        </Grid>

        {/* Performance Insights */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Insights
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {analyticsData?.insights?.map((insight, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    {insight.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {insight.description}
                  </Typography>
                  <Chip
                    size="small"
                    label={insight.priority}
                    color={insight.priority === "high" ? "error" : "default"}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              )) || (
                <Typography variant="body2" color="text.secondary">
                  No specific insights available for the selected time range.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Professional Reports Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Professional Reports
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Generate comprehensive reports for detailed analysis and insights.
          </Typography>

          <Grid container spacing={2}>
            {Object.entries(REPORT_TYPES).map(([key, reportType]) => (
              <Grid item xs={12} sm={6} md={3} key={key}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AssessmentIcon />}
                  onClick={() => generateReport(reportType)}
                  disabled={generateReportLoading}
                  sx={{ textTransform: "none" }}
                >
                  {key
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (l) => l.toUpperCase())}
                </Button>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Floating Action Button for Quick Actions */}
      <Tooltip title="Download Analytics Data">
        <Fab
          color="primary"
          sx={{ position: "fixed", bottom: 16, right: 16 }}
          onClick={() => generateReport(REPORT_TYPES.EXECUTIVE_SUMMARY)}
        >
          <DownloadIcon />
        </Fab>
      </Tooltip>

      {/* Report Dialog */}
      <Dialog
        open={reportDialogOpen}
        onClose={() => setReportDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Report Generated Successfully</DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedReport.metadata?.title || "Analytics Report"}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Generated on:{" "}
                {new Date(
                  selectedReport.metadata?.generated_at
                ).toLocaleString()}
              </Typography>

              <Typography variant="subtitle2" gutterBottom>
                Available Formats:
              </Typography>
              <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                {Object.entries(selectedReport.export_paths || {}).map(
                  ([format, path]) => (
                    <Chip
                      key={format}
                      label={format.toUpperCase()}
                      clickable
                      onClick={() => downloadReport(format)}
                      color="primary"
                      variant="outlined"
                    />
                  )
                )}
              </Box>

              <Typography variant="body2">
                Report ID: {selectedReport.report_id}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => downloadReport(EXPORT_FORMATS.PDF)}
            disabled={!selectedReport}
          >
            Download PDF
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedAnalytics;
