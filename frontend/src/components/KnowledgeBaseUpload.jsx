import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  Upload,
  File,
  X,
  CheckCircle,
  AlertCircle,
  FileText,
  Image,
  FileSpreadsheet,
  FileCode,
  Archive,
} from "lucide-react";
import { toast } from "react-hot-toast";
import AIModelSelector from "./AIModelSelector";

const KnowledgeBaseUpload = ({
  onUploadComplete,
  projectId,
  className = "",
}) => {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [isUploading, setIsUploading] = useState(false);
  const [metadata, setMetadata] = useState({
    title: "",
    description: "",
    tags: "",
    category: "",
    visibility: "private",
  });
  const [aiProcessing, setAiProcessing] = useState({
    enabled: true,
    selectedProvider: null,
    selectedModel: null,
    extractSummary: true,
    extractKeywords: true,
    generateEmbeddings: true,
    analyzeSentiment: false,
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const acceptedFileTypes = {
    "text/plain": [".txt"],
    "text/markdown": [".md"],
    "application/pdf": [".pdf"],
    "application/msword": [".doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
      ".docx",
    ],
    "text/csv": [".csv"],
    "application/json": [".json"],
    "text/html": [".html"],
    "application/rtf": [".rtf"],
  };

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      toast.error(
        `Some files were rejected. Please check file types and sizes.`
      );
    }

    const newFiles = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: "pending",
      progress: 0,
      error: null,
    }));

    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true,
  });

  const removeFile = (fileId) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
    setUploadProgress((prev) => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
  };

  const getFileIcon = (file) => {
    const type = file.type;
    const name = file.name.toLowerCase();

    if (type.startsWith("image/")) return <Image className="h-4 w-4" />;
    if (type.includes("pdf")) return <FileText className="h-4 w-4" />;
    if (type.includes("spreadsheet") || name.includes(".csv"))
      return <FileSpreadsheet className="h-4 w-4" />;
    if (type.includes("json") || name.includes(".json"))
      return <FileCode className="h-4 w-4" />;
    if (type.includes("zip") || type.includes("rar"))
      return <Archive className="h-4 w-4" />;
    return <File className="h-4 w-4" />;
  };

  const getStatusIcon = (status, error) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const uploadFile = async (fileData) => {
    const formData = new FormData();
    formData.append("file", fileData.file);
    formData.append(
      "metadata",
      JSON.stringify({
        ...metadata,
        tags: metadata.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
        project_id: projectId,
        ai_processing: aiProcessing,
      })
    );

    try {
      const response = await fetch("/api/v1/knowledge-base/upload", {
        method: "POST",
        body: formData,
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress((prev) => ({
            ...prev,
            [fileData.id]: progress,
          }));
        },
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error("Please select files to upload");
      return;
    }

    if (!metadata.title.trim()) {
      toast.error("Please provide a title for this upload");
      return;
    }

    setIsUploading(true);

    // Update all files to uploading status
    setFiles((prev) => prev.map((f) => ({ ...f, status: "uploading" })));

    const results = [];
    for (const fileData of files) {
      try {
        const result = await uploadFile(fileData);

        if (result.success) {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileData.id
                ? { ...f, status: "completed", data: result.data }
                : f
            )
          );
          results.push({
            file: fileData.file.name,
            success: true,
            data: result.data,
          });
        } else {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileData.id
                ? { ...f, status: "error", error: result.error }
                : f
            )
          );
          results.push({
            file: fileData.file.name,
            success: false,
            error: result.error,
          });
        }
      } catch (error) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, status: "error", error: error.message }
              : f
          )
        );
        results.push({
          file: fileData.file.name,
          success: false,
          error: error.message,
        });
      }
    }

    setIsUploading(false);

    const successful = results.filter((r) => r.success).length;
    const failed = results.filter((r) => !r.success).length;

    if (successful > 0) {
      toast.success(`Successfully uploaded ${successful} file(s)`);
    }
    if (failed > 0) {
      toast.error(`Failed to upload ${failed} file(s)`);
    }

    onUploadComplete?.(results);

    // Clear completed files after a delay
    setTimeout(() => {
      setFiles((prev) => prev.filter((f) => f.status !== "completed"));
    }, 3000);
  };

  const resetForm = () => {
    setFiles([]);
    setUploadProgress({});
    setMetadata({
      title: "",
      description: "",
      tags: "",
      category: "",
      visibility: "private",
    });
    setIsDialogOpen(false);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Knowledge Base Upload
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Drop Zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/25 hover:border-primary/50"
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">
              {isDragActive ? "Drop files here" : "Drag & drop files here"}
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              Supports: PDF, Word, Text, Markdown, CSV, JSON, HTML
            </p>
            <Button variant="outline" size="sm">
              Or browse files
            </Button>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium">Selected Files ({files.length})</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {files.map((fileData) => (
                  <div
                    key={fileData.id}
                    className="flex items-center gap-3 p-3 bg-muted rounded-lg"
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      {getFileIcon(fileData.file)}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {fileData.file.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {fileData.status === "uploading" && (
                        <div className="w-20">
                          <Progress
                            value={uploadProgress[fileData.id] || 0}
                            className="h-2"
                          />
                        </div>
                      )}

                      <Badge
                        variant={
                          fileData.status === "completed"
                            ? "success"
                            : fileData.status === "error"
                              ? "destructive"
                              : fileData.status === "uploading"
                                ? "secondary"
                                : "outline"
                        }
                      >
                        {fileData.status}
                      </Badge>

                      {getStatusIcon(fileData.status, fileData.error)}

                      {fileData.status !== "uploading" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(fileData.id)}
                          className="h-8 w-8 p-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {files.some((f) => f.status === "error") && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Some files failed to upload. Check the error messages above.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Upload Configuration */}
          <div className="space-y-4 pt-4 border-t">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={metadata.title}
                  onChange={(e) =>
                    setMetadata((prev) => ({ ...prev, title: e.target.value }))
                  }
                  placeholder="Enter a title for this upload..."
                  disabled={isUploading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={metadata.category}
                  onValueChange={(value) =>
                    setMetadata((prev) => ({ ...prev, category: value }))
                  }
                  disabled={isUploading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="documentation">Documentation</SelectItem>
                    <SelectItem value="research">Research</SelectItem>
                    <SelectItem value="reference">Reference</SelectItem>
                    <SelectItem value="training">Training Material</SelectItem>
                    <SelectItem value="policy">Policy</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={metadata.description}
                onChange={(e) =>
                  setMetadata((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Optional description..."
                disabled={isUploading}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                value={metadata.tags}
                onChange={(e) =>
                  setMetadata((prev) => ({ ...prev, tags: e.target.value }))
                }
                placeholder="Comma-separated tags..."
                disabled={isUploading}
              />
            </div>

            {/* AI Processing Configuration */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="w-full">
                  Configure AI Processing
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>AI Processing Configuration</DialogTitle>
                  <DialogDescription>
                    Configure how AI will process and analyze your uploaded
                    documents
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-6">
                  {/* AI Model Selection */}
                  <AIModelSelector
                    selectedProvider={aiProcessing.selectedProvider}
                    onProviderChange={(provider) =>
                      setAiProcessing((prev) => ({
                        ...prev,
                        selectedProvider: provider,
                      }))
                    }
                    selectedModel={aiProcessing.selectedModel}
                    onModelChange={(model) =>
                      setAiProcessing((prev) => ({
                        ...prev,
                        selectedModel: model,
                      }))
                    }
                    task="text-analysis"
                    showAdvancedSettings={false}
                  />

                  {/* Processing Options */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Processing Options</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={aiProcessing.extractSummary}
                            onChange={(e) =>
                              setAiProcessing((prev) => ({
                                ...prev,
                                extractSummary: e.target.checked,
                              }))
                            }
                          />
                          <span>Extract Summary</span>
                        </label>

                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={aiProcessing.extractKeywords}
                            onChange={(e) =>
                              setAiProcessing((prev) => ({
                                ...prev,
                                extractKeywords: e.target.checked,
                              }))
                            }
                          />
                          <span>Extract Keywords</span>
                        </label>

                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={aiProcessing.generateEmbeddings}
                            onChange={(e) =>
                              setAiProcessing((prev) => ({
                                ...prev,
                                generateEmbeddings: e.target.checked,
                              }))
                            }
                          />
                          <span>Generate Embeddings</span>
                        </label>

                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={aiProcessing.analyzeSentiment}
                            onChange={(e) =>
                              setAiProcessing((prev) => ({
                                ...prev,
                                analyzeSentiment: e.target.checked,
                              }))
                            }
                          />
                          <span>Analyze Sentiment</span>
                        </label>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </DialogContent>
            </Dialog>

            {/* Upload Actions */}
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleUpload}
                disabled={
                  files.length === 0 || isUploading || !metadata.title.trim()
                }
                className="flex-1"
              >
                {isUploading
                  ? "Uploading..."
                  : `Upload ${files.length} file(s)`}
              </Button>

              <Button
                variant="outline"
                onClick={resetForm}
                disabled={isUploading}
              >
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KnowledgeBaseUpload;
