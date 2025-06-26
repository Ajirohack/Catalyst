import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import ProviderCard from "../../components/admin/ProviderCard";
import { aiProvidersApi } from "../../lib/services/aiProviders";
import {
  Activity,
  BarChart3,
  DollarSign,
  RefreshCw,
  Settings,
  Zap,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

export default function AIProviders() {
  const [providers, setProviders] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [testing, setTesting] = useState(false);
  const [selectedTimePeriod, setSelectedTimePeriod] = useState("last_24h");

  // Chart colors for provider usage
  const CHART_COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#8dd1e1"];

  useEffect(() => {
    loadData();
  }, [loadData]);

  const loadData = React.useCallback(async () => {
    try {
      setLoading(true);
      const [providersData, statusData] = await Promise.all([
        aiProvidersApi.getProviders(),
        aiProvidersApi.getSystemStatus(),
      ]);

      setProviders(providersData);
      setSystemStatus(statusData);
    } catch (error) {
      console.error("Failed to load AI providers data:", error);
      // Set fallback data for development
      setProviders([
        {
          provider_type: "openai",
          name: "OpenAI",
          enabled: true,
          available: true,
          status: "active",
          priority: 1,
          default_model: "gpt-3.5-turbo",
          api_key_configured: true,
          base_url: "https://api.openai.com/v1",
          models: {
            "gpt-4": {
              type: "chat",
              max_tokens: 8192,
              cost_per_1k_tokens: { input: 0.03, output: 0.06 },
            },
            "gpt-3.5-turbo": {
              type: "chat",
              max_tokens: 16384,
              cost_per_1k_tokens: { input: 0.0015, output: 0.002 },
            },
          },
          rate_limits: { requests_per_minute: 3500, tokens_per_minute: 90000 },
          usage: {
            requests_count: 156,
            total_tokens: 45000,
            total_cost: 2.34,
            average_response_time: 1200,
          },
        },
        {
          provider_type: "anthropic",
          name: "Anthropic Claude",
          enabled: true,
          available: false,
          status: "error",
          priority: 2,
          default_model: "claude-3-sonnet-20240229",
          api_key_configured: false,
          base_url: "https://api.anthropic.com",
          models: {
            "claude-3-opus-20240229": {
              type: "chat",
              max_tokens: 200000,
              cost_per_1k_tokens: { input: 0.015, output: 0.075 },
            },
          },
          rate_limits: { requests_per_minute: 1000 },
          usage: {
            requests_count: 0,
            total_tokens: 0,
            total_cost: 0,
            average_response_time: 0,
          },
        },
        {
          provider_type: "local",
          name: "Local Models",
          enabled: false,
          available: false,
          status: "inactive",
          priority: 3,
          default_model: "llama2",
          api_key_configured: true,
          base_url:
            process.env.REACT_APP_LOCAL_MODEL_URL || "http://localhost:11434",
          models: {
            llama2: {
              type: "chat",
              max_tokens: 4096,
              cost_per_1k_tokens: { input: 0, output: 0 },
            },
          },
          rate_limits: { requests_per_minute: 60 },
          usage: {
            requests_count: 0,
            total_tokens: 0,
            total_cost: 0,
            average_response_time: 0,
          },
        },
      ]);
      setSystemStatus({
        service_healthy: true,
        active_providers: 1,
        total_providers: 3,
        default_provider: "openai",
        fallback_enabled: true,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleTestProvider = async (providerId) => {
    try {
      const result = await aiProvidersApi.testProvider(providerId);
      setTestResults((prev) => ({ ...prev, [providerId]: result }));
    } catch (error) {
      setTestResults((prev) => ({
        ...prev,
        [providerId]: {
          success: false,
          error_message: error.message || "Connection test failed",
        },
      }));
    }
  };

  const handleTestAllProviders = async () => {
    setTesting(true);
    try {
      const results = await aiProvidersApi.testAllProviders();
      const resultsMap = {};
      results.forEach((result) => {
        resultsMap[result.provider_type] = result;
      });
      setTestResults(resultsMap);
    } catch (error) {
      console.error("Failed to test all providers:", error);
    } finally {
      setTesting(false);
    }
  };

  const handleToggleProvider = async (providerId) => {
    try {
      await aiProvidersApi.toggleProvider(providerId);
      await loadData(); // Refresh data
    } catch (error) {
      console.error(`Failed to toggle provider ${providerId}:`, error);
    }
  };

  const handleConfigureProvider = (providerId) => {
    console.log("Configure provider:", providerId);
    // Feature: Provider configuration modal will be implemented in future update
  };

  const handleViewUsage = (providerId) => {
    console.log("View usage for provider:", providerId);
    // Feature: Usage analytics modal will be implemented in future update
  };

  // Prepare chart data
  const usageChartData = providers.map((provider) => ({
    name: provider.name,
    requests: provider.usage?.requests_count || 0,
    cost: provider.usage?.total_cost || 0,
    tokens: provider.usage?.total_tokens || 0,
  }));

  const providerDistributionData = providers
    .map((provider, index) => ({
      name: provider.name,
      value: provider.usage?.requests_count || 0,
      color: CHART_COLORS[index % CHART_COLORS.length],
    }))
    .filter((item) => item.value > 0);

  // System health indicators
  const SystemHealthCard = () => (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Health
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Service Status</span>
            <Badge
              variant={
                systemStatus?.service_healthy ? "default" : "destructive"
              }
            >
              {systemStatus?.service_healthy ? "Healthy" : "Unhealthy"}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Active Providers</span>
            <span className="font-semibold">
              {systemStatus?.active_providers || 0} /{" "}
              {systemStatus?.total_providers || 0}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Default Provider</span>
            <Badge variant="outline">
              {systemStatus?.default_provider || "None"}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Fallback Enabled</span>
            {systemStatus?.fallback_enabled ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <XCircle className="w-4 h-4 text-red-500" />
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Provider Management</h1>
          <p className="text-gray-600 mt-1">
            Configure and monitor AI providers for enhanced analysis
            capabilities
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedTimePeriod}
            onChange={(e) => setSelectedTimePeriod(e.target.value)}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value="last_24h">Last 24 Hours</option>
            <option value="last_week">Last Week</option>
            <option value="last_month">Last Month</option>
          </select>
          <Button
            variant="outline"
            onClick={handleTestAllProviders}
            disabled={testing}
          >
            {testing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            Test All
          </Button>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SystemHealthCard />

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Total Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {providers
                .reduce((sum, p) => sum + (p.usage?.requests_count || 0), 0)
                .toLocaleString()}
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {selectedTimePeriod.replace("_", " ")}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Total Cost
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              $
              {providers
                .reduce((sum, p) => sum + (p.usage?.total_cost || 0), 0)
                .toFixed(4)}
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {selectedTimePeriod.replace("_", " ")}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Avg Response Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {Math.round(
                providers.reduce(
                  (sum, p, _, arr) =>
                    sum + (p.usage?.average_response_time || 0),
                  0
                ) /
                  providers.filter((p) => p.usage?.average_response_time)
                    .length || 1
              )}
              ms
            </div>
            <p className="text-sm text-gray-600 mt-1">Across all providers</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      {usageChartData.some((d) => d.requests > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Usage by Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={usageChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="requests" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {providerDistributionData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Request Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={providerDistributionData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label
                    >
                      {providerDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Provider Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">AI Providers</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {providers.map((provider) => (
            <ProviderCard
              key={provider.provider_type}
              provider={provider}
              onTest={handleTestProvider}
              onToggle={handleToggleProvider}
              onConfigure={handleConfigureProvider}
              onViewUsage={handleViewUsage}
              testResults={testResults[provider.provider_type]}
            />
          ))}
        </div>
      </div>

      {/* Empty State */}
      {providers.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">
              No AI Providers Configured
            </h3>
            <p className="text-gray-500 mb-4">
              Configure AI providers to enable enhanced analysis capabilities
            </p>
            <Button variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Configure Providers
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
