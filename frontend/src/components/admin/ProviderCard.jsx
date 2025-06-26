import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Eye,
  EyeOff,
  Play,
  Settings,
  Zap,
  TrendingUp,
  Wifi,
  WifiOff,
} from "lucide-react";

export default function ProviderCard({
  provider,
  onTest,
  onToggle,
  onConfigure,
  onViewUsage,
  isLoading = false,
  testResults = null,
}) {
  const [showDetails, setShowDetails] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);

  // Provider type to display name mapping
  const providerDisplayNames = {
    openai: "OpenAI",
    anthropic: "Anthropic Claude",
    local: "Local Models",
    huggingface: "Hugging Face",
  };

  // Provider type to icon mapping
  const ProviderIcon = ({ type, className = "w-6 h-6" }) => {
    const icons = {
      openai: <Zap className={className} />,
      anthropic: <Activity className={className} />,
      local: <Settings className={className} />,
      huggingface: <TrendingUp className={className} />,
    };
    return icons[type] || <Settings className={className} />;
  };

  // Status badge component
  const StatusBadge = ({ status, available }) => {
    if (!available) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1">
          <WifiOff className="w-3 h-3" />
          Unavailable
        </Badge>
      );
    }

    const statusConfig = {
      active: { variant: "default", icon: CheckCircle, text: "Active" },
      inactive: { variant: "secondary", icon: Clock, text: "Inactive" },
      error: { variant: "destructive", icon: AlertCircle, text: "Error" },
      testing: { variant: "outline", icon: Activity, text: "Testing" },
    };

    const config = statusConfig[status] || statusConfig["inactive"];
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.text}
      </Badge>
    );
  };

  // Usage stats component
  const UsageStats = ({ usage }) => {
    if (!usage) return null;

    return (
      <div className="grid grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-500" />
          <div>
            <p className="text-sm text-gray-600">Requests (24h)</p>
            <p className="font-semibold">
              {usage.requests_count?.toLocaleString() || 0}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-green-500" />
          <div>
            <p className="text-sm text-gray-600">Cost (24h)</p>
            <p className="font-semibold">
              ${usage.total_cost?.toFixed(4) || "0.0000"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-500" />
          <div>
            <p className="text-sm text-gray-600">Tokens</p>
            <p className="font-semibold">
              {usage.total_tokens?.toLocaleString() || 0}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-purple-500" />
          <div>
            <p className="text-sm text-gray-600">Avg Response</p>
            <p className="font-semibold">
              {usage.average_response_time?.toFixed(0) || 0}ms
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Test results component
  const TestResults = ({ results }) => {
    if (!results) return null;

    const isSuccess = results.success;
    return (
      <div
        className={`p-3 rounded-lg mt-3 ${isSuccess ? "bg-green-50" : "bg-red-50"}`}
      >
        <div className="flex items-center gap-2 mb-2">
          {isSuccess ? (
            <CheckCircle className="w-4 h-4 text-green-600" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-600" />
          )}
          <span
            className={`text-sm font-medium ${isSuccess ? "text-green-800" : "text-red-800"}`}
          >
            {isSuccess ? "Connection Test Passed" : "Connection Test Failed"}
          </span>
        </div>
        {isSuccess ? (
          <div className="text-sm text-green-700">
            <p>Response time: {results.response_time_ms?.toFixed(1)}ms</p>
            {results.model_used && <p>Model: {results.model_used}</p>}
            {results.response_preview && (
              <p>Preview: {results.response_preview}</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-red-700">{results.error_message}</p>
        )}
      </div>
    );
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    try {
      await onTest(provider.provider_type);
    } finally {
      setIsTestingConnection(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-md transition-shadow duration-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-100">
                <ProviderIcon type={provider.provider_type} />
              </div>
              <div>
                <CardTitle className="text-lg">
                  {providerDisplayNames[provider.provider_type] ||
                    provider.name}
                </CardTitle>
                <p className="text-sm text-gray-500 mt-1">
                  Default Model: {provider.default_model}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge
                status={provider.status}
                available={provider.available}
              />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Basic Info */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Wifi className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  Priority: {provider.priority}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  Models:{" "}
                  {provider.models ? Object.keys(provider.models).length : 0}
                </span>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleTestConnection}
                disabled={isTestingConnection || !provider.available}
              >
                <Play className="w-3 h-3 mr-1" />
                {isTestingConnection ? "Testing..." : "Test"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onToggle(provider.provider_type)}
                disabled={isLoading}
              >
                {provider.enabled ? "Disable" : "Enable"}
              </Button>
            </div>
          </div>

          {/* Test Results */}
          <TestResults results={testResults} />

          {/* Detailed Information */}
          {showDetails && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 space-y-4"
            >
              {/* Configuration Info */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Configuration</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">API Key:</span>
                    <span className="ml-2">
                      {provider.api_key_configured
                        ? "••••••••"
                        : "Not configured"}
                    </span>
                  </div>
                  {provider.base_url && (
                    <div>
                      <span className="text-gray-600">Base URL:</span>
                      <span className="ml-2 font-mono text-xs">
                        {provider.base_url}
                      </span>
                    </div>
                  )}
                  {provider.rate_limits &&
                    Object.keys(provider.rate_limits).length > 0 && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Rate Limits:</span>
                        <div className="mt-1">
                          {Object.entries(provider.rate_limits).map(
                            ([key, value]) => (
                              <span
                                key={key}
                                className="inline-block bg-gray-200 rounded px-2 py-1 text-xs mr-2"
                              >
                                {key}: {value}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}
                </div>
              </div>

              {/* Available Models */}
              {provider.models && Object.keys(provider.models).length > 0 && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium mb-2">Available Models</h4>
                  <div className="space-y-2">
                    {Object.entries(provider.models).map(
                      ([modelName, modelInfo]) => (
                        <div
                          key={modelName}
                          className="flex items-center justify-between p-2 bg-white rounded"
                        >
                          <div>
                            <span className="font-medium text-sm">
                              {modelName}
                            </span>
                            <div className="text-xs text-gray-600">
                              Type: {modelInfo.type} | Max Tokens:{" "}
                              {modelInfo.max_tokens?.toLocaleString()}
                            </div>
                          </div>
                          {modelInfo.cost_per_1k_tokens && (
                            <div className="text-xs text-gray-600">
                              ${modelInfo.cost_per_1k_tokens.input || 0}/1k
                              input | $
                              {modelInfo.cost_per_1k_tokens.output || 0}/1k
                              output
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

              {/* Usage Stats */}
              {provider.usage && <UsageStats usage={provider.usage} />}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onConfigure(provider.provider_type)}
                  className="flex-1"
                >
                  <Settings className="w-3 h-3 mr-1" />
                  Configure
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewUsage(provider.provider_type)}
                  className="flex-1"
                >
                  <TrendingUp className="w-3 h-3 mr-1" />
                  View Usage
                </Button>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
