import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Search,
  Download,
  Trash2,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  User,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";

export default function Logs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedLog, setExpandedLog] = useState(null);
  const [activeFilter, setActiveFilter] = useState("all");

  // Mock log data
  const logs = [
    {
      id: 1,
      type: "system",
      severity: "error",
      message: "Database connection failed",
      timestamp: "2025-06-15T08:12:43",
      source: "database_service",
      details:
        "Connection to MongoDB Atlas timed out after 30s. Check network configuration and MongoDB Atlas status.",
      user: null,
      ipAddress: "10.0.1.23",
    },
    {
      id: 2,
      type: "auth",
      severity: "warning",
      message: "Failed login attempt",
      timestamp: "2025-06-15T10:23:15",
      source: "auth_service",
      details:
        "Multiple failed login attempts for user admin@catalyst.io from unusual IP address.",
      user: "admin@catalyst.io",
      ipAddress: "198.51.100.24",
    },
    {
      id: 3,
      type: "api",
      severity: "info",
      message: "API rate limit approaching",
      timestamp: "2025-06-15T11:05:37",
      source: "api_gateway",
      details:
        "OpenAI API usage at 85% of daily quota. Consider implementing additional rate limiting.",
      user: null,
      ipAddress: null,
    },
    {
      id: 4,
      type: "auth",
      severity: "success",
      message: "New admin user created",
      timestamp: "2025-06-15T13:45:22",
      source: "user_service",
      details:
        "Admin user sarah.johnson@catalyst.io created with full system access by super_admin.",
      user: "super_admin@catalyst.io",
      ipAddress: "10.0.1.5",
    },
    {
      id: 5,
      type: "system",
      severity: "error",
      message: "Model loading failed",
      timestamp: "2025-06-15T14:12:00",
      source: "model_service",
      details:
        "Failed to load Llama 3 70B model. CUDA out of memory error. Recommend increasing GPU resources or reducing batch size.",
      user: null,
      ipAddress: null,
    },
    {
      id: 6,
      type: "api",
      severity: "info",
      message: "API endpoint deprecated",
      timestamp: "2025-06-15T15:30:16",
      source: "api_gateway",
      details:
        "The /v1/legacy endpoint is now deprecated and will be removed in the next release. Please update your integrations.",
      user: null,
      ipAddress: null,
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

  const toggleLogExpansion = (id) => {
    if (expandedLog === id) {
      setExpandedLog(null);
    } else {
      setExpandedLog(id);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-amber-500" />;
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "info":
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.user && log.user.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesFilter = activeFilter === "all" || log.type === activeFilter;

    return matchesSearch && matchesFilter;
  });

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Logs</h1>
          <p className="text-muted-foreground">
            View and analyze system logs and activity
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export Logs
          </Button>
          <Button variant="destructive" className="flex items-center gap-2">
            <Trash2 className="h-4 w-4" />
            Clear Logs
          </Button>
        </div>
      </div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="pb-3">
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              <CardTitle>Activity Logs</CardTitle>
              <div className="flex w-full sm:w-auto gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    className="rounded-md border border-input pl-8 pr-3 py-2 text-sm bg-background w-full"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="flex gap-1">
                  <Button
                    variant={activeFilter === "all" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveFilter("all")}
                  >
                    All
                  </Button>
                  <Button
                    variant={activeFilter === "system" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveFilter("system")}
                  >
                    System
                  </Button>
                  <Button
                    variant={activeFilter === "auth" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveFilter("auth")}
                  >
                    Auth
                  </Button>
                  <Button
                    variant={activeFilter === "api" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveFilter("api")}
                  >
                    API
                  </Button>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredLogs.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-20" />
                  <p>No logs found matching your filters</p>
                </div>
              ) : (
                filteredLogs.map((log) => (
                  <motion.div
                    key={log.id}
                    variants={itemVariants}
                    className="border rounded-lg overflow-hidden"
                  >
                    <div
                      className="flex items-center gap-4 p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => toggleLogExpansion(log.id)}
                    >
                      <div>{getSeverityIcon(log.severity)}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{log.message}</span>
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100">
                            {log.type}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatTimestamp(log.timestamp)}
                          </span>
                          <span>•</span>
                          <span>{log.source}</span>
                          {log.user && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <User className="h-3 w-3" />
                                {log.user}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div>
                        {expandedLog === log.id ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </div>
                    </div>

                    {expandedLog === log.id && (
                      <div className="px-4 pb-4 pt-0 bg-muted/20">
                        <div className="bg-card p-4 rounded-md border text-sm">
                          <h4 className="font-medium mb-2">Details</h4>
                          <p className="text-muted-foreground mb-4">
                            {log.details}
                          </p>

                          <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">
                                Timestamp:{" "}
                              </span>
                              <span>{formatTimestamp(log.timestamp)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Source:{" "}
                              </span>
                              <span>{log.source}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Type:{" "}
                              </span>
                              <span>{log.type}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">
                                Severity:{" "}
                              </span>
                              <span>{log.severity}</span>
                            </div>
                            {log.user && (
                              <div>
                                <span className="text-muted-foreground">
                                  User:{" "}
                                </span>
                                <span>{log.user}</span>
                              </div>
                            )}
                            {log.ipAddress && (
                              <div>
                                <span className="text-muted-foreground">
                                  IP Address:{" "}
                                </span>
                                <span>{log.ipAddress}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        <Card>
          <CardHeader>
            <CardTitle>Log Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-muted/20 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">
                    {logs.filter((log) => log.severity === "error").length}
                  </div>
                  <div className="text-sm text-muted-foreground">Errors</div>
                </div>
                <div className="bg-muted/20 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">
                    {logs.filter((log) => log.severity === "warning").length}
                  </div>
                  <div className="text-sm text-muted-foreground">Warnings</div>
                </div>
                <div className="bg-muted/20 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">
                    {logs.filter((log) => log.type === "auth").length}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Auth Events
                  </div>
                </div>
                <div className="bg-muted/20 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold">
                    {logs.filter((log) => log.type === "api").length}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    API Events
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <h4 className="text-sm font-medium mb-2">
                  Log Volume (Last 24h)
                </h4>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary"
                    style={{ width: "65%" }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>0</span>
                  <span>234 logs</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Critical Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {logs
                .filter((log) => log.severity === "error")
                .slice(0, 3)
                .map((log) => (
                  <div
                    key={log.id}
                    className="flex items-start gap-3 p-3 border rounded-lg"
                  >
                    {getSeverityIcon(log.severity)}
                    <div>
                      <p className="font-medium">{log.message}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatTimestamp(log.timestamp)}
                      </p>
                      <p className="text-sm mt-1">{log.details}</p>
                    </div>
                  </div>
                ))}

              {logs.filter((log) => log.severity === "error").length === 0 && (
                <div className="text-center py-6 text-muted-foreground">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                  <p>No critical events to display</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
