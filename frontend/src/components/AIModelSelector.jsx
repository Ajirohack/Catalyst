import React, { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Alert, AlertDescription } from "./ui/alert";
import {
  Settings,
  Zap,
  DollarSign,
  Clock,
  Info,
  RefreshCw,
} from "lucide-react";
import { toast } from "react-hot-toast";

const AIModelSelector = ({
  selectedModel,
  onModelChange,
  selectedProvider,
  onProviderChange,
  task = "chat",
  showAdvancedSettings = false,
  onParametersChange,
  disabled = false,
}) => {
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);
  const [modelParameters, setModelParameters] = useState({
    temperature: 0.7,
    max_tokens: 2048,
    top_p: 1.0,
    frequency_penalty: 0.0,
    presence_penalty: 0.0,
    stream: false,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isParametersDialogOpen, setIsParametersDialogOpen] = useState(false);

  // Fetch available providers
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setIsLoading(true);
        const response = await fetch("/api/v1/admin/ai-providers/");
        if (response.ok) {
          const data = await response.json();
          setProviders(data.filter((p) => p.enabled));
        } else {
          throw new Error("Failed to fetch providers");
        }
      } catch (error) {
        console.error("Error fetching providers:", error);
        toast.error("Failed to load AI providers");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProviders();
  }, []);

  // Fetch models when provider changes
  useEffect(() => {
    const fetchModels = async () => {
      if (!selectedProvider) {
        setModels([]);
        return;
      }

      try {
        setIsLoadingModels(true);
        const response = await fetch(
          `/api/v1/admin/ai-providers/${selectedProvider}/models`
        );
        if (response.ok) {
          const data = await response.json();
          setModels(data);

          // Auto-select first model if none selected
          if (!selectedModel && data.length > 0) {
            onModelChange?.(data[0].name);
          }
        } else {
          throw new Error("Failed to fetch models");
        }
      } catch (error) {
        console.error("Error fetching models:", error);
        toast.error("Failed to load models for this provider");
        setModels([]);
      } finally {
        setIsLoadingModels(false);
      }
    };

    fetchModels();
  }, [selectedProvider, onModelChange, selectedModel]);

  // Sync models when provider changes
  const handleSyncModels = async () => {
    if (!selectedProvider) return;

    try {
      setIsLoadingModels(true);
      const response = await fetch(
        `/api/v1/admin/ai-providers/${selectedProvider}/sync-models`,
        { method: "POST" }
      );

      if (response.ok) {
        const data = await response.json();
        setModels(data.models);
        toast.success(`Synced ${data.models.length} models from provider`);
      } else {
        throw new Error("Failed to sync models");
      }
    } catch (error) {
      console.error("Error syncing models:", error);
      toast.error("Failed to sync models from provider");
    } finally {
      setIsLoadingModels(false);
    }
  };

  const handleParameterChange = (key, value) => {
    const newParams = { ...modelParameters, [key]: value };
    setModelParameters(newParams);
    onParametersChange?.(newParams);
  };

  const getModelInfo = () => {
    const model = models.find((m) => m.name === selectedModel);
    return model || null;
  };

  const getProviderBadgeColor = (providerType) => {
    const colors = {
      openai: "bg-green-500/10 text-green-500",
      anthropic: "bg-blue-500/10 text-blue-500",
      mistral: "bg-orange-500/10 text-orange-500",
      openrouter: "bg-purple-500/10 text-purple-500",
      ollama: "bg-gray-500/10 text-gray-500",
      groq: "bg-yellow-500/10 text-yellow-500",
      huggingface: "bg-pink-500/10 text-pink-500",
    };
    return colors[providerType] || "bg-gray-500/10 text-gray-500";
  };

  const modelInfo = getModelInfo();

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            AI Model Selection
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Provider Selection */}
          <div className="space-y-2">
            <Label htmlFor="provider-select">AI Provider</Label>
            <Select
              value={selectedProvider || ""}
              onValueChange={onProviderChange}
              disabled={disabled || isLoading}
            >
              <SelectTrigger id="provider-select">
                <SelectValue placeholder="Select AI provider..." />
              </SelectTrigger>
              <SelectContent>
                {providers.map((provider) => (
                  <SelectItem key={provider.id} value={provider.id.toString()}>
                    <div className="flex items-center gap-2">
                      <span>{provider.name}</span>
                      <Badge
                        className={getProviderBadgeColor(
                          provider.provider_type
                        )}
                      >
                        {provider.provider_type}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Model Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="model-select">Model</Label>
              {selectedProvider && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSyncModels}
                  disabled={isLoadingModels}
                  className="h-8"
                >
                  <RefreshCw
                    className={`h-3 w-3 mr-1 ${isLoadingModels ? "animate-spin" : ""}`}
                  />
                  Sync
                </Button>
              )}
            </div>
            <Select
              value={selectedModel || ""}
              onValueChange={onModelChange}
              disabled={disabled || !selectedProvider || isLoadingModels}
            >
              <SelectTrigger id="model-select">
                <SelectValue placeholder="Select model..." />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem key={model.name} value={model.name}>
                    <div className="flex flex-col">
                      <span>{model.name}</span>
                      {model.description && (
                        <span className="text-xs text-muted-foreground">
                          {model.description}
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Model Information */}
          {modelInfo && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <div className="flex items-center gap-4 text-sm">
                    {modelInfo.max_tokens && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {modelInfo.max_tokens.toLocaleString()} tokens
                      </span>
                    )}
                    {modelInfo.cost_input_per_1k && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />$
                        {modelInfo.cost_input_per_1k}/1K input
                      </span>
                    )}
                  </div>
                  {modelInfo.description && (
                    <p className="text-xs text-muted-foreground">
                      {modelInfo.description}
                    </p>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Advanced Settings */}
          {showAdvancedSettings && selectedModel && (
            <div className="pt-2">
              <Dialog
                open={isParametersDialogOpen}
                onOpenChange={setIsParametersDialogOpen}
              >
                <DialogTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <Settings className="h-4 w-4 mr-2" />
                    Advanced Parameters
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Model Parameters</DialogTitle>
                    <DialogDescription>
                      Customize the behavior of the selected model
                    </DialogDescription>
                  </DialogHeader>

                  <div className="space-y-6">
                    {/* Temperature */}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label>Temperature</Label>
                        <span className="text-sm text-muted-foreground">
                          {modelParameters.temperature}
                        </span>
                      </div>
                      <Slider
                        value={[modelParameters.temperature]}
                        onValueChange={([value]) =>
                          handleParameterChange("temperature", value)
                        }
                        max={2}
                        min={0}
                        step={0.1}
                        className="w-full"
                      />
                      <p className="text-xs text-muted-foreground">
                        Higher values make output more random
                      </p>
                    </div>

                    {/* Max Tokens */}
                    <div className="space-y-2">
                      <Label>Max Tokens</Label>
                      <Input
                        type="number"
                        value={modelParameters.max_tokens}
                        onChange={(e) =>
                          handleParameterChange(
                            "max_tokens",
                            parseInt(e.target.value)
                          )
                        }
                        min={1}
                        max={modelInfo?.max_tokens || 4096}
                      />
                      <p className="text-xs text-muted-foreground">
                        Maximum number of tokens to generate
                      </p>
                    </div>

                    {/* Top P */}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label>Top P</Label>
                        <span className="text-sm text-muted-foreground">
                          {modelParameters.top_p}
                        </span>
                      </div>
                      <Slider
                        value={[modelParameters.top_p]}
                        onValueChange={([value]) =>
                          handleParameterChange("top_p", value)
                        }
                        max={1}
                        min={0}
                        step={0.1}
                        className="w-full"
                      />
                      <p className="text-xs text-muted-foreground">
                        Nucleus sampling parameter
                      </p>
                    </div>

                    {/* Frequency Penalty */}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label>Frequency Penalty</Label>
                        <span className="text-sm text-muted-foreground">
                          {modelParameters.frequency_penalty}
                        </span>
                      </div>
                      <Slider
                        value={[modelParameters.frequency_penalty]}
                        onValueChange={([value]) =>
                          handleParameterChange("frequency_penalty", value)
                        }
                        max={2}
                        min={-2}
                        step={0.1}
                        className="w-full"
                      />
                      <p className="text-xs text-muted-foreground">
                        Penalty for token frequency
                      </p>
                    </div>

                    {/* Presence Penalty */}
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label>Presence Penalty</Label>
                        <span className="text-sm text-muted-foreground">
                          {modelParameters.presence_penalty}
                        </span>
                      </div>
                      <Slider
                        value={[modelParameters.presence_penalty]}
                        onValueChange={([value]) =>
                          handleParameterChange("presence_penalty", value)
                        }
                        max={2}
                        min={-2}
                        step={0.1}
                        className="w-full"
                      />
                      <p className="text-xs text-muted-foreground">
                        Penalty for token presence
                      </p>
                    </div>

                    {/* Stream */}
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Streaming</Label>
                        <p className="text-xs text-muted-foreground">
                          Stream responses in real-time
                        </p>
                      </div>
                      <Switch
                        checked={modelParameters.stream}
                        onCheckedChange={(checked) =>
                          handleParameterChange("stream", checked)
                        }
                      />
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AIModelSelector;
