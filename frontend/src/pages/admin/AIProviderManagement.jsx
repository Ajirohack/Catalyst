import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Switch } from "../../components/ui/switch";
import { Badge } from "../../components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../../components/ui/tabs";
import { Alert, AlertDescription } from "../../components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../components/ui/dialog";
import {
  PlusCircle,
  Settings,
  Activity,
  AlertCircle,
  CheckCircle,
  Zap,
  DollarSign,
  Clock,
  TrendingUp,
  TestTube,
  Trash2,
} from "lucide-react";
import { motion } from "framer-motion";
import { formatNumber, formatCurrency, getStatusColor } from "../../lib/utils";
import { toast } from "../../lib/toast";

const AIProviderManagement = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState({});

  // Load providers on component mount
  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/v1/admin/ai-providers/");
      if (!response.ok) throw new Error("Failed to load providers");
      const data = await response.json();
      setProviders(data);
    } catch (error) {
      toast.error("Failed to load AI providers");
      console.error("Error loading providers:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderToggle = async (providerId, enabled) => {
    try {
      const endpoint = enabled ? "enable" : "disable";
      const response = await fetch(
        `/api/v1/admin/ai-providers/${providerId}/${endpoint}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) throw new Error(`Failed to ${endpoint} provider`);

      // Update local state
      setProviders(
        providers.map((p) => (p.id === providerId ? { ...p, enabled } : p))
      );

      toast.success(
        `Provider ${enabled ? "enabled" : "disabled"} successfully`
      );
    } catch (error) {
      toast.error(`Failed to update provider`);
      console.error("Error updating provider:", error);
    }
  };

  const testProviderConnection = async (providerId) => {
    try {
      setIsTestingConnection((prev) => ({ ...prev, [providerId]: true }));

      const response = await fetch(
        `/api/v1/admin/ai-providers/${providerId}/test`,
        {
          method: "POST",
        }
      );

      if (!response.ok) throw new Error("Test failed");
      const result = await response.json();

      if (result.success) {
        toast.success(
          `Connection successful (${result.response_time_ms.toFixed(0)}ms)`
        );
      } else {
        toast.error(`Connection failed: ${result.message}`);
      }

      // Reload providers to get updated status
      loadProviders();
    } catch (error) {
      toast.error("Connection test failed");
      console.error("Error testing connection:", error);
    } finally {
      setIsTestingConnection((prev) => ({ ...prev, [providerId]: false }));
    }
  };

  const deleteProvider = async (providerId) => {
    // eslint-disable-next-line no-restricted-globals
    if (
      !window.confirm(
        "Are you sure you want to delete this provider? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/admin/ai-providers/${providerId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete provider");

      setProviders(providers.filter((p) => p.id !== providerId));
      toast.success("Provider deleted successfully");
    } catch (error) {
      toast.error("Failed to delete provider");
      console.error("Error deleting provider:", error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "inactive":
        return "bg-gray-500";
      case "error":
        return "bg-red-500";
      case "testing":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4" />;
      case "error":
        return <AlertCircle className="h-4 w-4" />;
      case "testing":
        return <TestTube className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 4,
    }).format(amount);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat("en-US").format(num);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">AI Provider Management</h1>
          <p className="text-gray-600 mt-2">
            Configure and manage AI providers for the Catalyst platform
          </p>
        </div>

        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <PlusCircle className="h-4 w-4" />
              Add Provider
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Add New AI Provider</DialogTitle>
              <DialogDescription>
                Configure a new AI provider for the platform
              </DialogDescription>
            </DialogHeader>
            <ProviderCreateForm
              onSuccess={() => {
                setIsCreateDialogOpen(false);
                loadProviders();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      {providers.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No providers configured
            </h3>
            <p className="text-gray-500 mb-4">
              Get started by adding your first AI provider
            </p>
            <Button
              onClick={() => setIsCreateDialogOpen(true)}
              className="flex items-center gap-2"
            >
              <PlusCircle className="h-4 w-4" />
              Add Provider
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {providers.map((provider) => (
            <motion.div
              key={provider.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-3 h-3 rounded-full ${getStatusColor(provider.status)}`}
                      />
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {provider.name}
                          <Badge
                            variant={provider.enabled ? "default" : "secondary"}
                          >
                            {provider.enabled ? "Enabled" : "Disabled"}
                          </Badge>
                        </CardTitle>
                        <p className="text-sm text-gray-600 mt-1">
                          {provider.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Switch
                        checked={provider.enabled}
                        onCheckedChange={(enabled) =>
                          handleProviderToggle(provider.id, enabled)
                        }
                      />

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => testProviderConnection(provider.id)}
                        disabled={isTestingConnection[provider.id]}
                        className="flex items-center gap-1"
                      >
                        {isTestingConnection[provider.id] ? (
                          <div className="animate-spin h-3 w-3 border border-current border-t-transparent rounded-full" />
                        ) : (
                          <TestTube className="h-3 w-3" />
                        )}
                        Test
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedProvider(provider)}
                      >
                        <Settings className="h-3 w-3" />
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteProvider(provider.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {/* Status */}
                    <div className="flex items-center gap-2">
                      {getStatusIcon(provider.status)}
                      <div>
                        <p className="text-xs text-gray-500">Status</p>
                        <p className="font-medium capitalize">
                          {provider.status}
                        </p>
                      </div>
                    </div>

                    {/* Usage Stats */}
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-blue-500" />
                      <div>
                        <p className="text-xs text-gray-500">Requests</p>
                        <p className="font-medium">
                          {formatNumber(
                            provider.usage_stats?.total_requests || 0
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Cost */}
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="text-xs text-gray-500">Cost (30d)</p>
                        <p className="font-medium">
                          {formatCurrency(
                            provider.usage_stats?.total_cost || 0
                          )}
                        </p>
                      </div>
                    </div>

                    {/* Response Time */}
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-purple-500" />
                      <div>
                        <p className="text-xs text-gray-500">Avg Response</p>
                        <p className="font-medium">
                          {provider.usage_stats?.average_response_time_ms
                            ? `${provider.usage_stats.average_response_time_ms.toFixed(0)}ms`
                            : "N/A"}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Models */}
                  {provider.models && provider.models.length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Available Models
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {provider.models.slice(0, 5).map((model) => (
                          <Badge
                            key={model.id}
                            variant="outline"
                            className="text-xs"
                          >
                            {model.model_name}
                          </Badge>
                        ))}
                        {provider.models.length > 5 && (
                          <Badge variant="outline" className="text-xs">
                            +{provider.models.length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Provider Detail Modal */}
      {selectedProvider && (
        <ProviderDetailModal
          provider={selectedProvider}
          onClose={() => setSelectedProvider(null)}
          onUpdate={loadProviders}
        />
      )}
    </div>
  );
};

// Provider Creation Form Component
const ProviderCreateForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    provider_type: "",
    name: "",
    description: "",
    api_key: "",
    base_url: "",
    default_model: "",
    enabled: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [supportedProviders, setSupportedProviders] = useState({});

  useEffect(() => {
    // Load supported providers
    fetch("/api/v1/admin/ai-providers/supported")
      .then((res) => res.json())
      .then((data) => setSupportedProviders(data))
      .catch((err) =>
        console.error("Failed to load supported providers:", err)
      );
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/v1/admin/ai-providers/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create provider");
      }

      toast.success("Provider created successfully");
      onSuccess();
    } catch (error) {
      toast.error(error.message);
      console.error("Error creating provider:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProviderTypeChange = (providerType) => {
    const providerInfo = supportedProviders[providerType];
    if (providerInfo) {
      setFormData({
        ...formData,
        provider_type: providerType,
        name: providerInfo.name,
        base_url: providerInfo.default_base_url,
        default_model: providerInfo.default_models[0] || "",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="provider_type">Provider Type</Label>
          <select
            id="provider_type"
            value={formData.provider_type}
            onChange={(e) => handleProviderTypeChange(e.target.value)}
            className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Select Provider</option>
            {Object.entries(supportedProviders).map(([key, provider]) => (
              <option key={key} value={key}>
                {provider.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Input
          id="description"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="base_url">Base URL</Label>
          <Input
            id="base_url"
            value={formData.base_url}
            onChange={(e) =>
              setFormData({ ...formData, base_url: e.target.value })
            }
            required
          />
        </div>

        <div>
          <Label htmlFor="default_model">Default Model</Label>
          <Input
            id="default_model"
            value={formData.default_model}
            onChange={(e) =>
              setFormData({ ...formData, default_model: e.target.value })
            }
          />
        </div>
      </div>

      {formData.provider_type !== "ollama" && (
        <div>
          <Label htmlFor="api_key">API Key</Label>
          <Input
            id="api_key"
            type="password"
            value={formData.api_key}
            onChange={(e) =>
              setFormData({ ...formData, api_key: e.target.value })
            }
            placeholder="Enter API key"
          />
        </div>
      )}

      <div className="flex items-center space-x-2">
        <Switch
          id="enabled"
          checked={formData.enabled}
          onCheckedChange={(enabled) => setFormData({ ...formData, enabled })}
        />
        <Label htmlFor="enabled">Enable provider</Label>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={() => onSuccess()}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Provider"}
        </Button>
      </div>
    </form>
  );
};

// Provider Detail Modal Component
const ProviderDetailModal = ({ provider, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <Dialog open={!!provider} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div
              className={`w-3 h-3 rounded-full ${getStatusColor(provider.status)}`}
            />
            {provider.name}
            <Badge variant={provider.enabled ? "default" : "secondary"}>
              {provider.enabled ? "Enabled" : "Disabled"}
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Manage provider configuration and monitor performance
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="models">Models</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">
                        {formatNumber(provider.total_requests)}
                      </p>
                      <p className="text-xs text-gray-500">Total Requests</p>
                    </div>
                    <TrendingUp className="h-4 w-4 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">
                        {formatNumber(provider.total_tokens)}
                      </p>
                      <p className="text-xs text-gray-500">Total Tokens</p>
                    </div>
                    <Zap className="h-4 w-4 text-yellow-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">
                        {formatCurrency(provider.total_cost)}
                      </p>
                      <p className="text-xs text-gray-500">Total Cost</p>
                    </div>
                    <DollarSign className="h-4 w-4 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">
                        {provider.usage_stats?.success_rate
                          ? `${(provider.usage_stats.success_rate * 100).toFixed(1)}%`
                          : "N/A"}
                      </p>
                      <p className="text-xs text-gray-500">Success Rate</p>
                    </div>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Provider Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Provider Type</Label>
                    <p className="font-medium">{provider.provider_type}</p>
                  </div>
                  <div>
                    <Label>Base URL</Label>
                    <p className="font-medium">{provider.base_url}</p>
                  </div>
                  <div>
                    <Label>Default Model</Label>
                    <p className="font-medium">{provider.default_model}</p>
                  </div>
                  <div>
                    <Label>Priority</Label>
                    <p className="font-medium">{provider.priority}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="models" className="space-y-4">
            <div className="grid gap-4">
              {provider.models?.map((model) => (
                <Card key={model.id}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">{model.model_name}</h4>
                        <p className="text-sm text-gray-600 capitalize">
                          {model.model_type}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {formatCurrency(model.cost_input_per_1k)}/1K in
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatCurrency(model.cost_output_per_1k)}/1K out
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 flex gap-2">
                      {model.supports_functions && (
                        <Badge variant="outline">Functions</Badge>
                      )}
                      {model.supports_vision && (
                        <Badge variant="outline">Vision</Badge>
                      )}
                      {model.supports_tools && (
                        <Badge variant="outline">Tools</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Alert>
              <TrendingUp className="h-4 w-4" />
              <AlertDescription>
                Detailed analytics and usage trends will be displayed here. This
                feature is currently in development.
              </AlertDescription>
            </Alert>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Alert>
              <Settings className="h-4 w-4" />
              <AlertDescription>
                Provider settings and configuration options will be available
                here. This feature is currently in development.
              </AlertDescription>
            </Alert>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default AIProviderManagement;
