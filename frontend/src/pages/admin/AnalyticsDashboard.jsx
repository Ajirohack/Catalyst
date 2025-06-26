import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { toast } from "../../lib/toast";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../../components/ui/tabs";
import { Button } from "../../components/ui/button";
import {
  Download,
  Calendar,
  TrendingUp,
  Users,
  MessageSquare,
  RefreshCw,
  Filter,
  ArrowRight,
  ArrowUpRight,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
  LineChart as LineChartIcon,
} from "lucide-react";

const AnalyticsDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    userMetrics: {
      totalUsers: 1243,
      activeUsers: 892,
      newUsersThisMonth: 78,
      userGrowthRate: 12.4,
    },
    projectMetrics: {
      totalProjects: 3578,
      activeProjects: 2453,
      averageProjectsPerUser: 2.8,
      projectCompletionRate: 73.2,
    },
    conversationMetrics: {
      totalConversations: 15489,
      averageMessagesPerConversation: 42,
      averageConversationLength: "18 minutes",
      platformDistribution: [
        { platform: "WhatsApp", percentage: 42 },
        { platform: "Messenger", percentage: 23 },
        { platform: "Slack", percentage: 15 },
        { platform: "Discord", percentage: 10 },
        { platform: "Other", percentage: 10 },
      ],
    },
    analysisMetrics: {
      totalAnalyses: 8752,
      averageAnalysisTime: "3.2 minutes",
      insightsGenerated: 52512,
      averageInsightsPerAnalysis: 6,
    },
    systemMetrics: {
      cpuUtilization: 42,
      memoryUtilization: 58,
      storageUtilization: 37,
      apiResponseTime: 210, // ms
    },
    revenueMetrics: {
      totalRevenue: 125400,
      revenueGrowthRate: 8.7,
      activeSubscriptions: 734,
      averageRevenuePerUser: 102,
    },
  });

  const [timeRange, setTimeRange] = useState("30d");
  const [filterOptions, setFilterOptions] = useState({
    platforms: ["all"],
    userTypes: ["all"],
    subscriptionTypes: ["all"],
  });
  const [selectedMetric, setSelectedMetric] = useState("users");
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dashboardError, setDashboardError] = useState(null);

  // Simulated time series data for charts
  const [timeSeriesData, setTimeSeriesData] = useState({
    userGrowth: generateTimeSeriesData(30, 800, 900, 5),
    activeUsers: generateTimeSeriesData(30, 600, 700, 10),
    newProjects: generateTimeSeriesData(30, 50, 100, 2),
    analysisVolume: generateTimeSeriesData(30, 200, 300, 8),
    revenue: generateTimeSeriesData(30, 4000, 5000, 100),
    conversationVolume: generateTimeSeriesData(30, 400, 500, 15),
  });

  // Main analytics data state
  const [analyticsData, setAnalyticsData] = useState({
    userData: [],
    platformUsage: [],
    featureUsage: [],
    retentionCohorts: [],
    hourlyActivity: [],
    messagePlatforms: [],
  });

  // Generate mock time series data
  function generateTimeSeriesData(days, min, max, volatility) {
    const data = [];
    let value = min + Math.random() * (max - min);

    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);

      // Add some randomness to the value
      value = Math.max(
        min,
        Math.min(max, value + (Math.random() - 0.5) * 2 * volatility)
      );

      data.push({
        date: date.toISOString().split("T")[0],
        value: Math.round(value),
      });
    }

    return data;
  }

  // Refresh data based on selected time range
  const refreshData = (range) => {
    setTimeRange(range);

    // In a real app, this would fetch data from an API with the selected range
    toast.success(`Data refreshed for ${range} time range`);

    // Simulate data refresh by slightly modifying the existing data
    setDashboardData((prevData) => ({
      ...prevData,
      userMetrics: {
        ...prevData.userMetrics,
        activeUsers:
          prevData.userMetrics.activeUsers +
          Math.floor(Math.random() * 20 - 10),
      },
      projectMetrics: {
        ...prevData.projectMetrics,
        activeProjects:
          prevData.projectMetrics.activeProjects +
          Math.floor(Math.random() * 50 - 25),
      },
    }));

    // Adjust time series data based on selected range
    const days =
      range === "7d" ? 7 : range === "30d" ? 30 : range === "90d" ? 90 : 365;

    setTimeSeriesData({
      userGrowth: generateTimeSeriesData(days, 800, 900, 5),
      activeUsers: generateTimeSeriesData(days, 600, 700, 10),
      newProjects: generateTimeSeriesData(days, 50, 100, 2),
      analysisVolume: generateTimeSeriesData(days, 200, 300, 8),
      revenue: generateTimeSeriesData(days, 4000, 5000, 100),
      conversationVolume: generateTimeSeriesData(days, 400, 500, 15),
    });
  };

  // Handle dashboard data refresh
  const handleRefreshData = async () => {
    setIsRefreshing(true);
    setDashboardError(null);

    try {
      // In a real app, this would fetch data from an API
      await new Promise((resolve) => setTimeout(resolve, 1500)); // Simulate API call

      refreshData(timeRange);
      setIsRefreshing(false);
    } catch (error) {
      console.error("Error refreshing dashboard data:", error);
      setDashboardError("Failed to refresh dashboard data. Please try again.");
      setIsRefreshing(false);
    }
  };

  // Initialize dashboard
  useEffect(() => {
    // Fetch initial data when component mounts
    handleRefreshData();

    // Set up periodic refresh (every 5 minutes)
    const refreshInterval = setInterval(
      () => {
        handleRefreshData();
      },
      5 * 60 * 1000
    );

    return () => clearInterval(refreshInterval);
  }, []);

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  // Format large numbers for display
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num;
  };

  // Prepare chart colors
  const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#8884d8",
    "#82ca9d",
  ];

  // Animation variants
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

  // Calculate percentage change indicator
  const renderChangeIndicator = (value) => {
    if (value === 0) return null;

    const isPositive = value > 0;
    return (
      <span
        className={`ml-2 text-xs font-medium flex items-center ${
          isPositive ? "text-green-500" : "text-red-500"
        }`}
      >
        {isPositive ? (
          <ArrowUpRight className="h-3 w-3 mr-1" />
        ) : (
          <ArrowUpRight className="h-3 w-3 mr-1 transform rotate-90" />
        )}
        {Math.abs(value)}%
      </span>
    );
  };

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border p-3 rounded-md shadow-md">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground">
            Gain insights into user behavior and platform usage
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={timeRange === "7d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("7d")}
          >
            7 days
          </Button>
          <Button
            variant={timeRange === "30d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("30d")}
          >
            30 days
          </Button>
          <Button
            variant={timeRange === "90d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("90d")}
          >
            90 days
          </Button>
          <Button variant="outline" size="icon">
            <Calendar className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Key Metrics Section */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4"
      >
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline">
              <div className="text-2xl font-bold">
                {dashboardData.userMetrics.totalUsers.toLocaleString()}
              </div>
              {renderChangeIndicator(dashboardData.userMetrics.userGrowthRate)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline">
              <div className="text-2xl font-bold">
                {dashboardData.userMetrics.activeUsers.toLocaleString()}
              </div>
              {renderChangeIndicator(dashboardData.userMetrics.userGrowthRate)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Retention Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline">
              <div className="text-2xl font-bold">
                {dashboardData.userMetrics.retention}%
              </div>
              {renderChangeIndicator(dashboardData.userMetrics.retentionGrowth)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Avg. Session Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline">
              <div className="text-2xl font-bold">
                {dashboardData.userMetrics.averageSessionTime}
              </div>
              {renderChangeIndicator(
                dashboardData.userMetrics.sessionTimeGrowth
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Messages Analyzed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline">
              <div className="text-2xl font-bold">
                {dashboardData.userMetrics.messagesSent.toLocaleString()}
              </div>
              {renderChangeIndicator(
                dashboardData.userMetrics.messagesSentGrowth
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Charts Section */}
      <motion.div variants={itemVariants}>
        <Card className="overflow-hidden">
          <CardHeader>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div>
                <CardTitle>User Activity</CardTitle>
                <CardDescription>
                  Track user growth and engagement over time
                </CardDescription>
              </div>
              <div className="mt-2 sm:mt-0">
                <Tabs defaultValue="bar" className="w-full">
                  <TabsList className="grid grid-cols-3">
                    <TabsTrigger value="bar" className="flex items-center">
                      <BarChartIcon className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Bar</span>
                    </TabsTrigger>
                    <TabsTrigger value="line" className="flex items-center">
                      <LineChartIcon className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Line</span>
                    </TabsTrigger>
                    <TabsTrigger value="area" className="flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Area</span>
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="users">
              <div className="flex justify-between items-center mb-4">
                <TabsList>
                  <TabsTrigger
                    value="users"
                    onClick={() => setSelectedMetric("users")}
                  >
                    <Users className="h-4 w-4 mr-2" />
                    Users
                  </TabsTrigger>
                  <TabsTrigger
                    value="messages"
                    onClick={() => setSelectedMetric("messages")}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Messages
                  </TabsTrigger>
                </TabsList>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                >
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </div>

              {showAdvancedOptions && (
                <div className="flex flex-wrap gap-2 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
                  <Button variant="outline" size="sm">
                    By Platform
                  </Button>
                  <Button variant="outline" size="sm">
                    By Region
                  </Button>
                  <Button variant="outline" size="sm">
                    By Device
                  </Button>
                  <Button variant="outline" size="sm">
                    Compare to Previous
                  </Button>
                </div>
              )}

              <TabsContent value="users" className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={analyticsData.userData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatDate}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => [value, ""]}
                      labelFormatter={formatDate}
                    />
                    <Legend />
                    <Bar
                      dataKey="newUsers"
                      name="New Users"
                      fill="#0088FE"
                      barSize={20}
                    />
                    <Bar
                      dataKey="activeUsers"
                      name="Active Users"
                      fill="#00C49F"
                      barSize={20}
                    />
                    <Bar
                      dataKey="returningUsers"
                      name="Returning Users"
                      fill="#FFBB28"
                      barSize={20}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>

              <TabsContent value="messages" className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      { date: "2025-06-09", count: 2340 },
                      { date: "2025-06-10", count: 2614 },
                      { date: "2025-06-11", count: 3125 },
                      { date: "2025-06-12", count: 2983 },
                      { date: "2025-06-13", count: 3812 },
                      { date: "2025-06-14", count: 4218 },
                      { date: "2025-06-15", count: 4325 },
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatDate}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => [
                        value.toLocaleString(),
                        "Messages",
                      ]}
                      labelFormatter={formatDate}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="count"
                      name="Messages Sent"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </motion.div>

      {/* Platform and Feature Usage Section */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <Card>
          <CardHeader>
            <CardTitle>Platform Usage</CardTitle>
            <CardDescription>
              Distribution of usage across platforms
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.platformUsage}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    fill="#8884d8"
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {analyticsData.platformUsage.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, "Usage"]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Feature Usage</CardTitle>
            <CardDescription>
              Most popular features by usage percentage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={analyticsData.featureUsage}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                    opacity={0.2}
                  />
                  <XAxis type="number" tick={{ fontSize: 12 }} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    tick={{ fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip formatter={(value) => [`${value}%`, "Usage"]} />
                  <Bar dataKey="value" fill="#8884d8">
                    {analyticsData.featureUsage.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Retention Cohort Analysis */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>User Retention by Cohort</CardTitle>
            <CardDescription>
              Weekly cohort analysis showing user retention over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Cohort
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Day 0
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Day 7
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Day 14
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Day 30
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Day 60
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {analyticsData.retentionCohorts.map((cohort, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {cohort.cohort}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center">
                          <div
                            className="h-2.5 w-full bg-green-500 rounded-full"
                            style={{ width: "100%" }}
                          ></div>
                          <span className="ml-2">{cohort.day0}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {cohort.day7 !== null ? (
                          <div className="flex items-center">
                            <div
                              className="h-2.5 bg-green-400 rounded-full"
                              style={{ width: `${cohort.day7}%` }}
                            ></div>
                            <span className="ml-2">{cohort.day7}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {cohort.day14 !== null ? (
                          <div className="flex items-center">
                            <div
                              className="h-2.5 bg-green-300 rounded-full"
                              style={{ width: `${cohort.day14}%` }}
                            ></div>
                            <span className="ml-2">{cohort.day14}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {cohort.day30 !== null ? (
                          <div className="flex items-center">
                            <div
                              className="h-2.5 bg-green-200 rounded-full"
                              style={{ width: `${cohort.day30}%` }}
                            ></div>
                            <span className="ml-2">{cohort.day30}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {cohort.day60 !== null ? (
                          <div className="flex items-center">
                            <div
                              className="h-2.5 bg-green-100 rounded-full"
                              style={{ width: `${cohort.day60}%` }}
                            ></div>
                            <span className="ml-2">{cohort.day60}%</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Secondary Charts Section */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <Card>
          <CardHeader>
            <CardTitle>Hourly User Activity</CardTitle>
            <CardDescription>
              User activity distribution by hour of day
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={analyticsData.hourlyActivity}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis
                    dataKey="hour"
                    tickFormatter={(hour) => `${hour}:00`}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value) => [value, "Users"]}
                    labelFormatter={(hour) => `${hour}:00 - ${hour + 1}:00`}
                  />
                  <Area
                    type="monotone"
                    dataKey="users"
                    name="Active Users"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Message Platform Distribution</CardTitle>
            <CardDescription>Messages analyzed by platform</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.messagePlatforms}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {analyticsData.messagePlatforms.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, "Usage"]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Additional Insights Section */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Key Insights</CardTitle>
            <CardDescription>
              Automatically generated insights from your analytics data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
                  <h3 className="font-medium">User Growth</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  User growth is up 12.4% compared to the previous period, with
                  the highest growth coming from North America and Europe.
                </p>
                <Button variant="link" size="sm" className="mt-2 px-0">
                  View Detailed Report <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <PieChartIcon className="h-5 w-5 text-blue-500 mr-2" />
                  <h3 className="font-medium">Platform Usage</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  The Chrome Extension has seen a 15% increase in usage, making
                  it the fastest-growing platform this month.
                </p>
                <Button variant="link" size="sm" className="mt-2 px-0">
                  View Platform Details <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Users className="h-5 w-5 text-amber-500 mr-2" />
                  <h3 className="font-medium">Retention</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Week 5 cohort is showing a 73% 7-day retention rate, which is
                  8% higher than the average from previous cohorts.
                </p>
                <Button variant="link" size="sm" className="mt-2 px-0">
                  Explore Retention Data <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <MessageSquare className="h-5 w-5 text-purple-500 mr-2" />
                  <h3 className="font-medium">Messaging Trends</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  WhatsApp remains the most analyzed platform with 32% of all
                  messages, but Discord has shown the largest growth at +23%.
                </p>
                <Button variant="link" size="sm" className="mt-2 px-0">
                  View Message Analytics <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default AnalyticsDashboard;
