import React, { useState, useCallback, useRef } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Upload,
  FileText,
  MessageSquare,
  Download,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { cn } from "../lib/utils";

const MultiFormatProcessor = () => {
  const [activeTab, setActiveTab] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingMode, setProcessingMode] = useState("batch");
  const [formatHint, setFormatHint] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [supportedFormats, setSupportedFormats] = useState([]);
  const [processingModes, setProcessingModes] = useState([]);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  // Load supported formats and processing modes on component mount
  React.useEffect(() => {
    loadCapabilities();
  }, []);

  const loadCapabilities = async () => {
    try {
      const [formatsResponse, modesResponse] = await Promise.all([
        fetch("/api/v1/advanced/formats", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
        fetch("/api/v1/advanced/processing-modes", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
      ]);

      if (formatsResponse.ok && modesResponse.ok) {
        const formats = await formatsResponse.json();
        const modes = await modesResponse.json();
        setSupportedFormats(formats);
        setProcessingModes(modes);
      }
    } catch (error) {
      console.error("Error loading capabilities:", error);
    }
  };

  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);

      // Auto-detect format hint based on file extension
      const extension = file.name.split(".").pop().toLowerCase();
      const formatMap = {
        txt: "text",
        json: "json",
        csv: "csv",
        pdf: "pdf",
        mp3: "audio",
        wav: "audio",
        mp4: "audio",
        jpg: "image",
        jpeg: "image",
        png: "image",
      };

      if (formatMap[extension]) {
        setFormatHint(formatMap[extension]);
      }
    }
  }, []);

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      const file = event.dataTransfer.files[0];
      if (file) {
        setSelectedFile(file);
        handleFileSelect({ target: { files: [file] } });
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
  }, []);

  const processConversation = async () => {
    if (!textContent && !selectedFile) {
      setError("Please provide text content or select a file to process.");
      return;
    }

    setIsProcessing(true);
    setProcessingProgress(0);
    setError(null);
    setResults(null);

    try {
      let response;

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProcessingProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      if (selectedFile) {
        // Process file upload
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("processing_mode", processingMode);
        if (formatHint) {
          formData.append("format_hint", formatHint);
        }
        formData.append("options", JSON.stringify({}));

        response = await fetch("/api/v1/advanced/process/upload", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: formData,
        });
      } else {
        // Process text content
        response = await fetch("/api/v1/advanced/process", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            text_content: textContent,
            processing_mode: processingMode,
            format_hint: formatHint || null,
            options: {},
          }),
        });
      }

      clearInterval(progressInterval);
      setProcessingProgress(100);

      if (response.ok) {
        const result = await response.json();
        setResults(result);
        toast({
          title: "Processing Complete",
          description: `Successfully processed ${result.message_count || 0} messages.`,
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Processing failed");
      }
    } catch (error) {
      console.error("Processing error:", error);
      setError(error.message);
      toast({
        title: "Processing Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      setTimeout(() => setProcessingProgress(0), 1000);
    }
  };

  const downloadResults = () => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `conversation_analysis_${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const clearAll = () => {
    setTextContent("");
    setSelectedFile(null);
    setResults(null);
    setError(null);
    setProcessingProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Multi-Format Conversation Processor
          </CardTitle>
          <CardDescription>
            Process conversations from various platforms and formats with
            advanced AI analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="space-y-4"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="text">Text Input</TabsTrigger>
              <TabsTrigger value="file">File Upload</TabsTrigger>
            </TabsList>

            <TabsContent value="text" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="text-content">Conversation Text</Label>
                <Textarea
                  id="text-content"
                  placeholder="Paste your conversation here...\n\nExample formats:\n- WhatsApp: [12/25/23, 10:30:15 AM] John: Hello there\n- Messenger: John (10:30 AM): Hello there\n- Plain text: John: Hello there"
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  className="min-h-[200px] font-mono text-sm"
                />
              </div>
            </TabsContent>

            <TabsContent value="file" className="space-y-4">
              <div className="space-y-2">
                <Label>File Upload</Label>
                <div
                  className={cn(
                    "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                    selectedFile
                      ? "border-green-300 bg-green-50"
                      : "border-gray-300 hover:border-gray-400"
                  )}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                >
                  {selectedFile ? (
                    <div className="space-y-2">
                      <CheckCircle className="h-8 w-8 text-green-500 mx-auto" />
                      <p className="text-sm font-medium">{selectedFile.name}</p>
                      <p className="text-xs text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedFile(null);
                          if (fileInputRef.current)
                            fileInputRef.current.value = "";
                        }}
                      >
                        Remove File
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="h-8 w-8 text-gray-400 mx-auto" />
                      <p className="text-sm text-gray-600">
                        Drag and drop a file here, or click to select
                      </p>
                      <p className="text-xs text-gray-500">
                        Supports: TXT, JSON, CSV, PDF, Audio (MP3, WAV), Images
                        (JPG, PNG)
                      </p>
                      <Input
                        ref={fileInputRef}
                        type="file"
                        onChange={handleFileSelect}
                        accept=".txt,.json,.csv,.pdf,.mp3,.wav,.mp4,.jpg,.jpeg,.png"
                        className="hidden"
                      />
                      <Button
                        variant="outline"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        Select File
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="processing-mode">Processing Mode</Label>
              <Select value={processingMode} onValueChange={setProcessingMode}>
                <SelectTrigger>
                  <SelectValue placeholder="Select processing mode" />
                </SelectTrigger>
                <SelectContent>
                  {processingModes.map((mode) => (
                    <SelectItem key={mode} value={mode}>
                      {mode.charAt(0).toUpperCase() + mode.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="format-hint">Format Hint (Optional)</Label>
              <Select value={formatHint} onValueChange={setFormatHint}>
                <SelectTrigger>
                  <SelectValue placeholder="Auto-detect format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Auto-detect</SelectItem>
                  {supportedFormats.map((format) => (
                    <SelectItem key={format} value={format}>
                      {format.charAt(0).toUpperCase() + format.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isProcessing && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Processing conversation...</span>
                <span>{processingProgress}%</span>
              </div>
              <Progress value={processingProgress} className="w-full" />
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={processConversation}
              disabled={isProcessing || (!textContent && !selectedFile)}
              className="flex-1"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  Process Conversation
                </>
              )}
            </Button>

            <Button variant="outline" onClick={clearAll}>
              Clear All
            </Button>
          </div>
        </CardContent>
      </Card>

      {results && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Processing Results</span>
              <Button variant="outline" size="sm" onClick={downloadResults}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {results.message_count || 0}
                </div>
                <div className="text-sm text-gray-600">Messages Processed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {results.participants?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Participants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {results.detected_format || "Unknown"}
                </div>
                <div className="text-sm text-gray-600">Detected Format</div>
              </div>
            </div>

            {results.participants && results.participants.length > 0 && (
              <div className="space-y-2">
                <Label>Participants</Label>
                <div className="flex flex-wrap gap-2">
                  {results.participants.map((participant, index) => (
                    <Badge key={index} variant="secondary">
                      {participant}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {results.metadata && (
              <div className="mt-4 space-y-2">
                <Label>Metadata</Label>
                <div className="bg-gray-50 p-3 rounded-md">
                  <pre className="text-xs overflow-x-auto">
                    {JSON.stringify(results.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {results.processing_time && (
              <div className="mt-4 text-sm text-gray-600">
                Processing completed in {results.processing_time}ms
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MultiFormatProcessor;
