import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Plus,
  Settings,
  RefreshCw,
  Trash2,
  ExternalLink,
  Chrome,
  Download,
  Info,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Switch } from "../../components/ui/switch";
import { Badge } from "../../components/ui/badge";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../../components/ui/tabs";

export default function Models() {
  const [activeTab, setActiveTab] = useState("llm");
  const [isExtensionInstalled, setIsExtensionInstalled] = useState(false);
  const [extensionUsageStats, setExtensionUsageStats] = useState({
    totalWhispers: 0,
    appliedWhispers: 0,
    activeUsers: 0,
    lastSync: "Never",
  });

  // Check if extension is installed on page load
  useEffect(() => {
    // This will only work if the page is loaded within the extension
    if (window.chrome && window.chrome.runtime) {
      try {
        // Try to communicate with our extension
        window.chrome.runtime.sendMessage(
          { type: "CHECK_INSTALLATION" },
          (response) => {
            if (response && !window.chrome.runtime.lastError) {
              setIsExtensionInstalled(true);
              // Update usage stats if available
              if (response.stats) {
                setExtensionUsageStats(response.stats);
              }
            }
          }
        );
      } catch (error) {
        console.error("Error checking extension:", error);
      }
    }
  }, []);

  // Mock data for AI models
  const llmModels = [
    {
      id: 1,
      name: "GPT-4 Turbo",
      provider: "OpenAI",
      description: "Advanced language model for text generation and reasoning",
      status: "active",
      lastUpdated: "2 days ago",
      apiKey: "sk-********************abc",
      usage: "84%",
    },
    {
      id: 2,
      name: "Claude 3 Opus",
      provider: "Anthropic",
      description: "High-performance text generation and analysis model",
      status: "active",
      lastUpdated: "1 week ago",
      apiKey: "sk-ant-********************xyz",
      usage: "65%",
    },
    {
      id: 3,
      name: "Llama 3 70B",
      provider: "Meta",
      description: "Open source large language model for diverse applications",
      status: "inactive",
      lastUpdated: "3 weeks ago",
      apiKey: "None (Local)",
      usage: "12%",
    },
  ];

  const whisperModels = [
    {
      id: 1,
      name: "Whisper Large v3",
      provider: "OpenAI",
      description:
        "Advanced speech recognition model for accurate transcription",
      status: "active",
      lastUpdated: "5 days ago",
      apiKey: "sk-********************abc",
      usage: "76%",
    },
    {
      id: 2,
      name: "Deepgram Nova-2",
      provider: "Deepgram",
      description:
        "Fast and accurate speech-to-text for real-time applications",
      status: "active",
      lastUpdated: "2 weeks ago",
      apiKey: "dg-********************def",
      usage: "31%",
    },
  ];

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
        duration: 0.3,
      },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Models</h1>
          <p className="text-muted-foreground">
            Manage AI models and configure settings
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Model
        </Button>
      </div>

      <motion.div variants={itemVariants} className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveTab("llm")}
          className={`px-4 py-2 text-sm font-medium transition-colors relative ${
            activeTab === "llm"
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Language Models
          {activeTab === "llm" && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab("whisper")}
          className={`px-4 py-2 text-sm font-medium transition-colors relative ${
            activeTab === "whisper"
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Speech Recognition
          {activeTab === "whisper" && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab("extension")}
          className={`px-4 py-2 text-sm font-medium transition-colors relative ${
            activeTab === "extension"
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Browser Extension
          {activeTab === "extension" && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
          )}
        </button>
      </motion.div>

      <div>
        {activeTab === "llm" && (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
          >
            {llmModels.map((model) => (
              <motion.div key={model.id} variants={itemVariants}>
                <Card
                  className={model.status === "inactive" ? "opacity-70" : ""}
                >
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="flex items-center gap-2">
                          <span>{model.name}</span>
                          {model.status === "active" ? (
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                          ) : (
                            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                          )}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {model.provider}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <button className="p-2 rounded-md hover:bg-muted transition-colors">
                          <Settings className="h-4 w-4" />
                        </button>
                        <button className="p-2 rounded-md hover:bg-muted transition-colors text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm">{model.description}</p>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">API Usage</span>
                        <span className="font-medium">{model.usage}</span>
                      </div>
                      <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: model.usage }}
                        ></div>
                      </div>
                    </div>

                    <div className="pt-2 text-xs text-muted-foreground">
                      <div className="flex justify-between py-1">
                        <span>API Key:</span>
                        <span className="font-mono">{model.apiKey}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Last Updated:</span>
                        <span>{model.lastUpdated}</span>
                      </div>
                    </div>

                    <div className="flex justify-between pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-1"
                      >
                        <RefreshCw className="h-3 w-3" />
                        Refresh
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Test
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {activeTab === "whisper" && (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
          >
            {whisperModels.map((model) => (
              <motion.div key={model.id} variants={itemVariants}>
                <Card
                  className={model.status === "inactive" ? "opacity-70" : ""}
                >
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="flex items-center gap-2">
                          <span>{model.name}</span>
                          {model.status === "active" ? (
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                          ) : (
                            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                          )}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {model.provider}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <button className="p-2 rounded-md hover:bg-muted transition-colors">
                          <Settings className="h-4 w-4" />
                        </button>
                        <button className="p-2 rounded-md hover:bg-muted transition-colors text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm">{model.description}</p>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">API Usage</span>
                        <span className="font-medium">{model.usage}</span>
                      </div>
                      <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: model.usage }}
                        ></div>
                      </div>
                    </div>

                    <div className="pt-2 text-xs text-muted-foreground">
                      <div className="flex justify-between py-1">
                        <span>API Key:</span>
                        <span className="font-mono">{model.apiKey}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Last Updated:</span>
                        <span>{model.lastUpdated}</span>
                      </div>
                    </div>

                    <div className="flex justify-between pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-1"
                      >
                        <RefreshCw className="h-3 w-3" />
                        Refresh
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Test
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {activeTab === "extension" && (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid gap-6 grid-cols-1 md:grid-cols-2"
          >
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Catalyst Whisper Coach
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Browser extension for real-time communication coaching
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-center py-6">
                    <Button className="flex items-center gap-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="lucide lucide-chrome"
                      >
                        <circle cx="12" cy="12" r="10" />
                        <circle cx="12" cy="12" r="4" />
                        <line x1="21.17" y1="8" x2="12" y2="8" />
                        <line x1="3.95" y1="6.06" x2="8.54" y2="14" />
                        <line x1="10.88" y1="21.94" x2="15.46" y2="14" />
                      </svg>
                      Install Chrome Extension
                    </Button>
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">Supported Platforms</h3>
                    <div className="flex flex-wrap gap-2">
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        WhatsApp
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Messenger
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Instagram
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Facebook
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Discord
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Slack
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Teams
                      </div>
                      <div className="px-2 py-1 bg-muted rounded-md text-xs">
                        Telegram
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 text-xs text-muted-foreground">
                    <div className="flex justify-between py-1">
                      <span>Version:</span>
                      <span>1.0.0</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span>Last Updated:</span>
                      <span>Today</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle>Extension Statistics</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Usage metrics and performance data
                  </p>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-muted p-4 rounded-lg">
                      <h3 className="text-xl font-bold">352</h3>
                      <p className="text-xs text-muted-foreground">
                        Total Whispers
                      </p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg">
                      <h3 className="text-xl font-bold">127</h3>
                      <p className="text-xs text-muted-foreground">
                        Applied Suggestions
                      </p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg">
                      <h3 className="text-xl font-bold">25</h3>
                      <p className="text-xs text-muted-foreground">
                        Active Users
                      </p>
                    </div>
                    <div className="bg-muted p-4 rounded-lg">
                      <h3 className="text-xl font-bold">36%</h3>
                      <p className="text-xs text-muted-foreground">
                        Acceptance Rate
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">
                      Platform Distribution
                    </h3>
                    <div className="space-y-1">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>WhatsApp</span>
                          <span>64%</span>
                        </div>
                        <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: "64%" }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Instagram</span>
                          <span>22%</span>
                        </div>
                        <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: "22%" }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Others</span>
                          <span>14%</span>
                        </div>
                        <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: "14%" }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-1"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Refresh Stats
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-1"
                    >
                      <ExternalLink className="h-3 w-3" />
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
