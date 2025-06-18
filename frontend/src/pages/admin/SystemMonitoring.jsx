import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";

/**
 * System Monitoring Component for Admin Dashboard
 * Displays real-time system metrics, health checks, and performance data
 */
const SystemMonitoring = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [lastRefreshed, setLastRefreshed] = useState(new Date());
  const [isLoading, setIsLoading] = useState(false);

  // Mock system status data - would be replaced with real API calls
  const [systemStatus, setSystemStatus] = useState({
    status: "healthy", // healthy, degraded, critical
    uptime: "99.98%",
    activeUsers: 124,
    apiRequests: {
      total: 1245689,
      lastHour: 1865,
      failedLastHour: 8,
      averageResponseTime: 187, // ms
    },
    resources: {
      cpu: 32, // percentage
      memory: 64, // percentage
      disk: 47, // percentage
      network: 26, // percentage
    },
    services: [
      { name: "API Gateway", status: "healthy", latency: 42 },
      { name: "Database", status: "healthy", latency: 89 },
      { name: "Analytics Engine", status: "healthy", latency: 105 },
      { name: "Auth Service", status: "healthy", latency: 58 },
      { name: "Storage Service", status: "degraded", latency: 203 },
      { name: "Whisper Service", status: "healthy", latency: 76 },
    ],
    alerts: [
      {
        id: 1,
        type: "warning",
        message: "Storage service performance degraded",
        timestamp: "2025-06-15T08:45:12Z",
        resolved: false,
      },
      {
        id: 2,
        type: "info",
        message: "Scheduled maintenance in 2 days",
        timestamp: "2025-06-14T14:30:00Z",
        resolved: false,
      },
      {
        id: 3,
        type: "error",
        message: "Database connection timeout",
        timestamp: "2025-06-14T06:12:33Z",
        resolved: true,
      },
    ],
  });

  // Mock time-series data for charts
  const [performanceData, setPerformanceData] = useState({
    cpu: Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      value: 20 + Math.random() * 40,
    })),
    memory: Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      value: 50 + Math.random() * 30,
    })),
    apiRequests: Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      requests: Math.floor(1000 + Math.random() * 1500),
      errors: Math.floor(Math.random() * 20),
    })),
    responseTime: Array.from({ length: 24 }, (_, i) => ({
      time: `${i}:00`,
      value: 150 + Math.random() * 100,
    })),
  });

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

  // Handle tab change
  const handleTabChange = (value) => {
    setActiveTab(value);
  };

  // Simulate data refresh
  const refreshData = () => {
    setIsLoading(true);

    // Simulate API call delay
    setTimeout(() => {
      // Update some random values to simulate live data
      setSystemStatus((prev) => ({
        ...prev,
        activeUsers: Math.floor(100 + Math.random() * 50),
        apiRequests: {
          ...prev.apiRequests,
          lastHour: Math.floor(1500 + Math.random() * 500),
          failedLastHour: Math.floor(Math.random() * 15),
        },
        resources: {
          cpu: Math.floor(20 + Math.random() * 40),
          memory: Math.floor(40 + Math.random() * 40),
          disk: prev.resources.disk,
          network: Math.floor(20 + Math.random() * 30),
        },
        services: prev.services.map((service) => ({
          ...service,
          latency: Math.floor(40 + Math.random() * 200),
          status: Math.random() > 0.9 ? "degraded" : "healthy",
        })),
      }));

      // Update last refreshed time
      setLastRefreshed(new Date());
      setIsLoading(false);
    }, 1000);
  };

  // Auto-refresh on interval
  useEffect(() => {
    const interval = setInterval(() => {
      refreshData();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Format status badge with appropriate color
  const getStatusBadge = (status) => {
    let className = "";
    switch (status) {
      case "healthy":
        className = "bg-green-100 text-green-800";
        break;
      case "degraded":
        className = "bg-yellow-100 text-yellow-800";
        break;
      case "critical":
        className = "bg-red-100 text-red-800";
        break;
      default:
        className = "bg-gray-100 text-gray-800";
    }

    return (
      <Badge className={className}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  // Format alert type badge
  const getAlertBadge = (type) => {
    let className = "";
    switch (type) {
      case "info":
        className = "bg-blue-100 text-blue-800";
        break;
      case "warning":
        className = "bg-yellow-100 text-yellow-800";
        break;
      case "error":
        className = "bg-red-100 text-red-800";
        break;
      default:
        className = "bg-gray-100 text-gray-800";
    }

    return (
      <Badge className={className}>
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    );
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <motion.div
      className="container p-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">System Monitoring</h1>
          <p className="text-gray-500">
            Monitor system health, performance, and resource usage
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span>Last updated: {lastRefreshed.toLocaleTimeString()}</span>
          <Button variant="outline" onClick={refreshData} disabled={isLoading}>
            {isLoading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      {/* System Status Overview */}
      <motion.div variants={itemVariants}>
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>System Status</CardTitle>
              {getStatusBadge(systemStatus.status)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">Uptime</div>
                <div className="text-2xl font-bold">{systemStatus.uptime}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">Active Users</div>
                <div className="text-2xl font-bold">
                  {systemStatus.activeUsers}
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">
                  API Requests (Last Hour)
                </div>
                <div className="text-2xl font-bold">
                  {systemStatus.apiRequests.lastHour}
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-500 mb-1">
                  Avg Response Time
                </div>
                <div className="text-2xl font-bold">
                  {systemStatus.apiRequests.averageResponseTime} ms
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">CPU</span>
                  <span className="text-sm font-medium">
                    {systemStatus.resources.cpu}%
                  </span>
                </div>
                <Progress value={systemStatus.resources.cpu} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">Memory</span>
                  <span className="text-sm font-medium">
                    {systemStatus.resources.memory}%
                  </span>
                </div>
                <Progress
                  value={systemStatus.resources.memory}
                  className="h-2"
                />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">Disk</span>
                  <span className="text-sm font-medium">
                    {systemStatus.resources.disk}%
                  </span>
                </div>
                <Progress value={systemStatus.resources.disk} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">Network</span>
                  <span className="text-sm font-medium">
                    {systemStatus.resources.network}%
                  </span>
                </div>
                <Progress
                  value={systemStatus.resources.network}
                  className="h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tabs for different views */}
      <Tabs
        defaultValue="overview"
        onValueChange={handleTabChange}
        className="mb-6"
      >
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="logs">System Logs</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* API Requests Chart */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>API Requests (24h)</CardTitle>
                  <CardDescription>
                    Request volume and error rates
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={performanceData.apiRequests}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="requests" name="Requests" fill="#8884d8" />
                      <Bar dataKey="errors" name="Errors" fill="#ff8042" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Response Time Chart */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>Response Time (24h)</CardTitle>
                  <CardDescription>
                    Average API response time in milliseconds
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={performanceData.responseTime}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="value"
                        name="Response Time (ms)"
                        stroke="#8884d8"
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* CPU Usage Chart */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>CPU Usage (24h)</CardTitle>
                  <CardDescription>System CPU utilization</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={performanceData.cpu}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="value"
                        name="CPU Usage (%)"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>

            {/* Memory Usage Chart */}
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>Memory Usage (24h)</CardTitle>
                  <CardDescription>System memory utilization</CardDescription>
                </CardHeader>
                <CardContent className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={performanceData.memory}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="value"
                        name="Memory Usage (%)"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="mt-6">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <Card>
              <CardHeader>
                <CardTitle>Service Health</CardTitle>
                <CardDescription>
                  Status and performance of system services
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b text-sm text-gray-500">
                        <th className="text-left py-3 px-4">Service</th>
                        <th className="text-left py-3 px-4">Status</th>
                        <th className="text-left py-3 px-4">Latency</th>
                        <th className="text-left py-3 px-4">Uptime</th>
                        <th className="text-left py-3 px-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {systemStatus.services.map((service, index) => (
                        <motion.tr
                          key={service.name}
                          variants={itemVariants}
                          className="border-b hover:bg-gray-50"
                        >
                          <td className="py-3 px-4 font-medium">
                            {service.name}
                          </td>
                          <td className="py-3 px-4">
                            {getStatusBadge(service.status)}
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center">
                              <span
                                className={
                                  service.latency < 100
                                    ? "text-green-600"
                                    : service.latency < 200
                                      ? "text-yellow-600"
                                      : "text-red-600"
                                }
                              >
                                {service.latency} ms
                              </span>
                            </div>
                          </td>
                          <td className="py-3 px-4">99.9%</td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                Details
                              </Button>
                              <Button variant="ghost" size="sm">
                                Restart
                              </Button>
                            </div>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="mt-6">
          {/* Performance metrics would go here */}
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="mt-6">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <Card>
              <CardHeader>
                <CardTitle>System Alerts</CardTitle>
                <CardDescription>
                  Recent system alerts and notifications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {systemStatus.alerts.map((alert) => (
                    <motion.div
                      key={alert.id}
                      variants={itemVariants}
                      className={`p-4 border rounded-md ${
                        alert.resolved ? "bg-gray-50" : "bg-white"
                      }`}
                    >
                      <div className="flex items-start">
                        <div className="flex-1">
                          <div className="flex items-center mb-1">
                            {getAlertBadge(alert.type)}
                            <span className="ml-2 text-sm text-gray-500">
                              {formatDate(alert.timestamp)}
                            </span>
                            {alert.resolved && (
                              <Badge variant="outline" className="ml-2">
                                Resolved
                              </Badge>
                            )}
                          </div>
                          <p className={alert.resolved ? "text-gray-500" : ""}>
                            {alert.message}
                          </p>
                        </div>
                        <div>
                          <Button variant="ghost" size="sm">
                            {alert.resolved ? "Details" : "Resolve"}
                          </Button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="mt-6">
          {/* System logs would go here */}
        </TabsContent>
      </Tabs>
    </motion.div>
  );
};

export default SystemMonitoring;
