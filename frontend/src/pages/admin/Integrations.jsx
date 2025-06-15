import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Plus,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Trash2,
  Key,
  RefreshCw,
  Check,
  X,
  BarChart,
  Webhook,
  Database,
  Globe,
} from "lucide-react";
import { Card, CardContent, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";

export default function Integrations() {
  const [expandedSection, setExpandedSection] = useState("apis");

  // Mock data for integrations
  const apiIntegrations = [
    {
      id: 1,
      name: "OpenAI API",
      description: "Integration for GPT models and embedding services",
      status: true,
      lastUpdated: "2 days ago",
      apiKey: "sk-********************abc",
      endpointUrl: "https://api.openai.com/v1",
      usageLimit: "50,000 tokens/day",
      currentUsage: "23,456 tokens",
    },
    {
      id: 2,
      name: "Anthropic API",
      description: "Integration for Claude models",
      status: true,
      lastUpdated: "1 week ago",
      apiKey: "sk-ant-********************xyz",
      endpointUrl: "https://api.anthropic.com/v1",
      usageLimit: "30,000 tokens/day",
      currentUsage: "12,789 tokens",
    },
    {
      id: 3,
      name: "Google Vertex AI",
      description: "Integration for Gemini models",
      status: false,
      lastUpdated: "2 weeks ago",
      apiKey: "AIza********************def",
      endpointUrl: "https://us-central1-aiplatform.googleapis.com/v1",
      usageLimit: "Not configured",
      currentUsage: "0 tokens",
    },
  ];

  const dataIntegrations = [
    {
      id: 1,
      name: "MongoDB Connection",
      description: "Main database connection for user data",
      status: true,
      lastUpdated: "1 day ago",
      connectionString:
        "mongodb+srv://******:******@cluster0.example.mongodb.net",
      databaseName: "catalyst_production",
    },
    {
      id: 2,
      name: "Redis Cache",
      description: "Caching service for performance optimization",
      status: true,
      lastUpdated: "3 days ago",
      connectionString:
        "redis://********@redis-12345.c1.us-east-1.ec2.cloud.redislabs.com:12345",
    },
  ];

  const webhookIntegrations = [
    {
      id: 1,
      name: "Slack Notifications",
      description: "Sends alerts and notifications to Slack channels",
      status: true,
      lastUpdated: "5 days ago",
      webhookUrl: "https://hooks.slack.com/services/T******/B******/******",
      events: ["system_alert", "user_signup", "model_error"],
    },
    {
      id: 2,
      name: "Discord Updates",
      description: "Sends system updates to Discord server",
      status: false,
      lastUpdated: "2 weeks ago",
      webhookUrl: "https://discord.com/api/webhooks/******/******",
      events: ["system_update", "maintenance_alert"],
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

  const toggleSection = (section) => {
    if (expandedSection === section) {
      setExpandedSection(null);
    } else {
      setExpandedSection(section);
    }
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
          <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
          <p className="text-muted-foreground">
            Manage external API connections and services
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Integration
        </Button>
      </div>

      <motion.div variants={itemVariants} className="space-y-4">
        {/* API Integrations */}
        <Card>
          <div
            className="flex justify-between items-center p-6 cursor-pointer"
            onClick={() => toggleSection("apis")}
          >
            <div className="flex items-center gap-3">
              <Key className="h-5 w-5 text-primary" />
              <CardTitle>API Integrations</CardTitle>
            </div>
            <button className="h-6 w-6 rounded-full flex items-center justify-center">
              {expandedSection === "apis" ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>

          {expandedSection === "apis" && (
            <CardContent className="pt-0">
              <div className="space-y-4">
                {apiIntegrations.map((integration) => (
                  <div
                    key={integration.id}
                    className="border rounded-lg p-4 space-y-3"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{integration.name}</h3>
                          {integration.status ? (
                            <Badge className="bg-green-500/10 text-green-500 text-xs px-2 py-0.5 rounded-full">
                              Active
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-500/10 text-gray-500 text-xs px-2 py-0.5 rounded-full">
                              Inactive
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {integration.description}
                        </p>
                      </div>
                      <div className="flex items-center">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={integration.status}
                            readOnly
                          />
                          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">API Key:</p>
                        <p className="font-mono">{integration.apiKey}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Endpoint:</p>
                        <p className="font-mono truncate">
                          {integration.endpointUrl}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Usage Limit:</p>
                        <p>{integration.usageLimit}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Current Usage:</p>
                        <p>{integration.currentUsage}</p>
                      </div>
                    </div>

                    <div className="flex justify-end gap-2 mt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Test
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        <RefreshCw className="h-3 w-3" />
                        Refresh
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1 text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-3 w-3" />
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>

        {/* Database Integrations */}
        <Card>
          <div
            className="flex justify-between items-center p-6 cursor-pointer"
            onClick={() => toggleSection("databases")}
          >
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5 text-blue-500" />
              <CardTitle>Database Connections</CardTitle>
            </div>
            <button className="h-6 w-6 rounded-full flex items-center justify-center">
              {expandedSection === "databases" ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>

          {expandedSection === "databases" && (
            <CardContent className="pt-0">
              <div className="space-y-4">
                {dataIntegrations.map((integration) => (
                  <div
                    key={integration.id}
                    className="border rounded-lg p-4 space-y-3"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{integration.name}</h3>
                          {integration.status ? (
                            <span className="flex items-center text-xs text-green-500 gap-1">
                              <Check className="h-3 w-3" /> Connected
                            </span>
                          ) : (
                            <span className="flex items-center text-xs text-red-500 gap-1">
                              <X className="h-3 w-3" /> Disconnected
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {integration.description}
                        </p>
                      </div>
                      <div className="flex items-center">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={integration.status}
                            readOnly
                          />
                          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">
                          Connection String:
                        </p>
                        <p className="font-mono text-xs">
                          {integration.connectionString}
                        </p>
                      </div>
                      {integration.databaseName && (
                        <div>
                          <p className="text-muted-foreground">
                            Database Name:
                          </p>
                          <p>{integration.databaseName}</p>
                        </div>
                      )}
                    </div>

                    <div className="flex justify-end gap-2 mt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        <BarChart className="h-3 w-3" />
                        Stats
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        <RefreshCw className="h-3 w-3" />
                        Test Connection
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>

        {/* Webhook Integrations */}
        <Card>
          <div
            className="flex justify-between items-center p-6 cursor-pointer"
            onClick={() => toggleSection("webhooks")}
          >
            <div className="flex items-center gap-3">
              <Globe className="h-5 w-5 text-purple-500" />
              <CardTitle>Webhook Integrations</CardTitle>
            </div>
            <button className="h-6 w-6 rounded-full flex items-center justify-center">
              {expandedSection === "webhooks" ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>

          {expandedSection === "webhooks" && (
            <CardContent className="pt-0">
              <div className="space-y-4">
                {webhookIntegrations.map((integration) => (
                  <div
                    key={integration.id}
                    className="border rounded-lg p-4 space-y-3"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{integration.name}</h3>
                          {integration.status ? (
                            <Badge className="bg-green-500/10 text-green-500 text-xs px-2 py-0.5 rounded-full">
                              Active
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-500/10 text-gray-500 text-xs px-2 py-0.5 rounded-full">
                              Inactive
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {integration.description}
                        </p>
                      </div>
                      <div className="flex items-center">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={integration.status}
                            readOnly
                          />
                          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Webhook URL:</p>
                        <p className="font-mono text-xs">
                          {integration.webhookUrl}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Events:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {integration.events.map((event, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100"
                            >
                              {event}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end gap-2 mt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        <Webhook className="h-3 w-3" />
                        Test Webhook
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center gap-1 text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-3 w-3" />
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      </motion.div>
    </motion.div>
  );
}

// Custom Badge component (since we're not importing the one from ShadCN)
const Badge = ({ children, className, ...props }) => {
  return (
    <span className={`inline-flex items-center ${className}`} {...props}>
      {children}
    </span>
  );
};
