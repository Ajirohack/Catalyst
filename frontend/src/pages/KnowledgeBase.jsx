import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Search,
  FileText,
  Image,
  Download,
  Trash2,
  Filter,
  Eye,
  BarChart3,
  Brain,
  Database,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  X,
  Grid,
  List,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const KnowledgeBase = () => {
  // State management
  const [documents, setDocuments] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [categories, setCategories] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);

  // UI state
  const [activeTab, setActiveTab] = useState("documents");
  const [viewMode, setViewMode] = useState("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [documentPreview, setDocumentPreview] = useState(null);

  // Upload form state
  const [uploadFiles, setUploadFiles] = useState([]);
  const [uploadCategory, setUploadCategory] = useState("");
  const [uploadTags, setUploadTags] = useState("");
  const [autoTag, setAutoTag] = useState(true);
  const [autoCategorize, setAutoCategorize] = useState(true);

  // API functions
  const apiCall = useCallback(async (endpoint, options = {}) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/knowledge-base${endpoint}`,
        {
          headers: {
            "Content-Type": "application/json",
            ...options.headers,
          },
          ...options,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      toast.error(error.message || "API call failed");
      throw error;
    }
  }, []);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory && selectedCategory !== "all") params.append("category", selectedCategory);
      if (selectedTags.length > 0)
        params.append("tags", selectedTags.join(","));
      if (searchQuery) params.append("search_query", searchQuery);

      const data = await apiCall(`/documents?${params.toString()}`);
      setDocuments(data);
    } catch (error) {
      console.error("Failed to load documents:", error);
    } finally {
      setLoading(false);
    }
  }, [apiCall, selectedCategory, selectedTags, searchQuery]);

  const loadCategories = useCallback(async () => {
    try {
      const data = await apiCall("/categories");
      setCategories(data.categories || []);
    } catch (error) {
      console.error("Failed to load categories:", error);
    }
  }, [apiCall]);

  const loadTags = useCallback(async () => {
    try {
      const data = await apiCall("/tags");
      setAllTags(data.tags || []);
    } catch (error) {
      console.error("Failed to load tags:", error);
    }
  }, [apiCall]);

  const loadAnalytics = useCallback(async () => {
    try {
      const data = await apiCall("/analytics");
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    }
  }, [apiCall]);

  // Load initial data
  useEffect(() => {
    loadDocuments();
    loadCategories();
    loadTags();
    loadAnalytics();
  }, [loadDocuments, loadCategories, loadTags, loadAnalytics]);

  // Reload documents when filters change
  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileUpload = async (files) => {
    setUploading(true);
    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append("file", file);
      if (uploadCategory) formData.append("category", uploadCategory);
      if (uploadTags) formData.append("tags", uploadTags);
      formData.append("auto_tag", autoTag.toString());
      formData.append("auto_categorize", autoCategorize.toString());

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/knowledge-base/documents/upload`,
          {
            method: "POST",
            body: formData,
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Upload failed for ${file.name}`);
        }

        const result = await response.json();
        toast.success(`${file.name} uploaded successfully`);
        return result;
      } catch (error) {
        toast.error(`Failed to upload ${file.name}: ${error.message}`);
        throw error;
      }
    });

    try {
      await Promise.all(uploadPromises);
      loadDocuments();
      loadAnalytics();
      setUploadModalOpen(false);
      setUploadFiles([]);
      setUploadTags("");
      setUploadCategory("");
    } catch (error) {
      console.error("Some uploads failed:", error);
    } finally {
      setUploading(false);
    }
  };

  // Handle document search
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      return;
    }

    setSearchLoading(true);
    try {
      const response = await apiCall("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          limit: 10,
          threshold: 0.7,
          filters: {
            category: selectedCategory && selectedCategory !== "all" ? selectedCategory : undefined,
            tags: selectedTags.length > 0 ? selectedTags : undefined,
          },
          include_content: true,
        }),
      });

      setSearchResults(response.results);
      setActiveTab("search");
    } catch (error) {
      toast.error("Search failed: " + error.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle document preview
  const handlePreview = async (documentId) => {
    try {
      const document = await apiCall(`/documents/${documentId}`);
      setDocumentPreview(document);
    } catch (error) {
      toast.error("Failed to load document preview: " + error.message);
    }
  };

  // Handle document deletion
  const handleDelete = async (documentId) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await apiCall(`/documents/${documentId}`, {
        method: "DELETE",
      });

      toast.success("Document deleted successfully");
      loadDocuments();
      loadAnalytics();

      // Close preview if open for this document
      if (documentPreview && documentPreview.document_id === documentId) {
        setDocumentPreview(null);
      }
    } catch (error) {
      toast.error("Failed to delete document: " + error.message);
    }
  };

  // Handle tag management
  const handleUpdateTags = async (documentId, tags, replace = false) => {
    try {
      await apiCall(`/documents/${documentId}/tags`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tags,
          replace,
        }),
      });

      toast.success("Tags updated successfully");
      loadDocuments();

      // Update preview if open
      if (documentPreview && documentPreview.document_id === documentId) {
        handlePreview(documentId);
      }
    } catch (error) {
      toast.error("Failed to update tags: " + error.message);
    }
  };

  const handleDownloadDocument = async (documentId, filename) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/knowledge-base/documents/${documentId}/download`
      );
      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success("Download started");
    } catch (error) {
      toast.error("Download failed");
      console.error("Download failed:", error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "processing":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getFileIcon = (documentType) => {
    switch (documentType) {
      case "pdf":
        return <FileText className="w-8 h-8 text-red-500" />;
      case "image":
        return <Image className="w-8 h-8 text-blue-500" />;
      case "docx":
        return <FileText className="w-8 h-8 text-blue-600" />;
      default:
        return <FileText className="w-8 h-8 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Brain className="w-8 h-8 text-indigo-600" />
              Knowledge Base
            </h1>
            <p className="text-gray-600 mt-1">
              Manage, search, and organize your documents with AI-powered
              insights
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={() => setUploadModalOpen(true)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload Documents
            </Button>
            <Button
              variant="outline"
              onClick={loadAnalytics}
              className="border-indigo-200 hover:bg-indigo-50"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </motion.div>

        {/* Analytics Cards */}
        {analytics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <Card className="border-indigo-200 bg-white/80 backdrop-blur">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Total Documents
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics.total_documents}
                    </p>
                  </div>
                  <Database className="w-8 h-8 text-indigo-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-indigo-200 bg-white/80 backdrop-blur">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Text Chunks
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics.total_chunks}
                    </p>
                  </div>
                  <Grid className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-indigo-200 bg-white/80 backdrop-blur">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Storage Used
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {(analytics.total_size / (1024 * 1024)).toFixed(1)} MB
                    </p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-indigo-200 bg-white/80 backdrop-blur">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Recent Uploads
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics.recent_uploads}
                    </p>
                  </div>
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Search and Filters */}
        <Card className="border-indigo-200 bg-white/80 backdrop-blur">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="Search documents with AI-powered semantic search..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleSearch(e)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || searchLoading}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  {searchLoading ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4 mr-2" />
                  )}
                  Search
                </Button>
              </div>

              <div className="flex flex-wrap gap-4">
                <Select
                  value={selectedCategory}
                  onValueChange={setSelectedCategory}
                >
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Tags:</span>
                  {selectedTags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() =>
                        setSelectedTags(selectedTags.filter((t) => t !== tag))
                      }
                    >
                      {tag}
                      <X className="w-3 h-3 ml-1" />
                    </Badge>
                  ))}
                </div>

                <div className="flex items-center gap-2 ml-auto">
                  <Button
                    variant={viewMode === "grid" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("grid")}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === "list" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("list")}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="search">Search Results</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="space-y-6">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
              </div>
            ) : (
              <motion.div
                layout
                className={`grid gap-6 ${
                  viewMode === "grid"
                    ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
                    : "grid-cols-1"
                }`}
              >
                <AnimatePresence>
                  {documents.map((doc) => (
                    <motion.div
                      key={doc.document_id}
                      layout
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      whileHover={{ scale: 1.02 }}
                      className="group"
                    >
                      <Card className="border-indigo-200 bg-white/80 backdrop-blur hover:shadow-lg transition-all duration-200">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                              {getFileIcon(doc.document_type)}
                              <div className="flex-1 min-w-0">
                                <CardTitle className="text-sm font-semibold truncate">
                                  {doc.filename}
                                </CardTitle>
                                <CardDescription className="text-xs">
                                  {new Date(
                                    doc.created_at
                                  ).toLocaleDateString()}
                                </CardDescription>
                              </div>
                            </div>
                            {getStatusIcon(doc.status)}
                          </div>
                        </CardHeader>

                        <CardContent className="space-y-3">
                          {doc.category && (
                            <Badge variant="outline" className="text-xs">
                              {doc.category}
                            </Badge>
                          )}

                          <div className="flex flex-wrap gap-1">
                            {doc.tags.slice(0, 3).map((tag) => (
                              <Badge
                                key={tag}
                                variant="secondary"
                                className="text-xs"
                              >
                                {tag}
                              </Badge>
                            ))}
                            {doc.tags.length > 3 && (
                              <Badge variant="secondary" className="text-xs">
                                +{doc.tags.length - 3}
                              </Badge>
                            )}
                          </div>

                          <div className="text-xs text-gray-500">
                            {doc.chunk_count} chunks •{" "}
                            {(doc.file_size / 1024).toFixed(1)} KB
                          </div>

                          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handlePreview(doc.document_id)}
                            >
                              <Eye className="w-3 h-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                handleDownloadDocument(
                                  doc.document_id,
                                  doc.filename
                                )
                              }
                            >
                              <Download className="w-3 h-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(doc.document_id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </motion.div>
            )}
          </TabsContent>

          <TabsContent value="search" className="space-y-6">
            {searchResults.length > 0 ? (
              <div className="space-y-4">
                {searchResults.map((result, index) => (
                  <Card
                    key={`${result.document_id}-${result.chunk_id}`}
                    className="border-indigo-200 bg-white/80 backdrop-blur"
                  >
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          {result.document_metadata &&
                            getFileIcon(result.document_metadata.document_type)}
                          <div>
                            <h3 className="font-semibold">
                              {result.document_metadata?.filename ||
                                "Unknown Document"}
                            </h3>
                            <p className="text-sm text-gray-600">
                              Similarity: {(result.score * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        <Badge variant="outline">
                          {result.document_metadata?.category ||
                            "Uncategorized"}
                        </Badge>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-4 mb-3">
                        <p className="text-sm text-gray-700">
                          {result.content}
                        </p>
                      </div>

                      {result.document_metadata?.tags && (
                        <div className="flex flex-wrap gap-1">
                          {result.document_metadata.tags.map((tag) => (
                            <Badge
                              key={tag}
                              variant="secondary"
                              className="text-xs"
                            >
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="border-indigo-200 bg-white/80 backdrop-blur">
                <CardContent className="p-12 text-center">
                  <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No search results
                  </h3>
                  <p className="text-gray-600">
                    {searchQuery
                      ? "Try adjusting your search query or filters"
                      : "Enter a search query to find relevant documents"}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            {analytics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-indigo-200 bg-white/80 backdrop-blur">
                  <CardHeader>
                    <CardTitle>Categories</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.categories.map((cat) => (
                        <div
                          key={cat.category}
                          className="flex justify-between items-center"
                        >
                          <span className="text-sm font-medium">
                            {cat.category}
                          </span>
                          <Badge variant="outline">{cat.document_count}</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-indigo-200 bg-white/80 backdrop-blur">
                  <CardHeader>
                    <CardTitle>Top Tags</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.top_tags.map((tag) => (
                        <div key={tag.tag} className="space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">
                              {tag.tag}
                            </span>
                            <span className="text-xs text-gray-600">
                              {tag.usage_percentage.toFixed(1)}%
                            </span>
                          </div>
                          <Progress
                            value={tag.usage_percentage}
                            className="h-2"
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Upload Modal */}
        <AnimatePresence>
          {uploadModalOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={(e) =>
                e.target === e.currentTarget && setUploadModalOpen(false)
              }
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold">Upload Documents</h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setUploadModalOpen(false)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Files
                    </label>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.gif"
                      onChange={(e) =>
                        setUploadFiles(Array.from(e.target.files || []))
                      }
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Supported formats: PDF, DOCX, TXT, Images (PNG, JPG, GIF)
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category (optional)
                      </label>
                      <Select
                        value={uploadCategory}
                        onValueChange={setUploadCategory}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map((category) => (
                            <SelectItem key={category} value={category}>
                              {category}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tags (optional)
                      </label>
                      <Input
                        placeholder="Enter tags separated by commas"
                        value={uploadTags}
                        onChange={(e) => setUploadTags(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id="auto-tag"
                        checked={autoTag}
                        onChange={(e) => setAutoTag(e.target.checked)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <label
                        htmlFor="auto-tag"
                        className="text-sm text-gray-700"
                      >
                        Enable automatic tagging
                      </label>
                    </div>

                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id="auto-categorize"
                        checked={autoCategorize}
                        onChange={(e) => setAutoCategorize(e.target.checked)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <label
                        htmlFor="auto-categorize"
                        className="text-sm text-gray-700"
                      >
                        Enable automatic categorization
                      </label>
                    </div>
                  </div>

                  {uploadFiles.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">
                        Selected Files ({uploadFiles.length})
                      </h3>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {uploadFiles.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-gray-50 rounded"
                          >
                            <span className="text-sm truncate">
                              {file.name}
                            </span>
                            <span className="text-xs text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setUploadModalOpen(false)}
                    disabled={uploading}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleFileUpload(uploadFiles)}
                    disabled={uploadFiles.length === 0 || uploading}
                    className="bg-indigo-600 hover:bg-indigo-700"
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Upload {uploadFiles.length} Files
                      </>
                    )}
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Document Preview Modal */}
        <AnimatePresence>
          {documentPreview && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={(e) =>
                e.target === e.currentTarget && setDocumentPreview(null)
              }
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold">
                      {documentPreview.filename}
                    </h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDocumentPreview(null)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Type:</span>{" "}
                      {documentPreview.document_type}
                    </div>
                    <div>
                      <span className="font-medium">Size:</span>{" "}
                      {(documentPreview.file_size / 1024).toFixed(1)} KB
                    </div>
                    <div>
                      <span className="font-medium">Category:</span>{" "}
                      {documentPreview.category || "None"}
                    </div>
                    <div>
                      <span className="font-medium">Chunks:</span>{" "}
                      {documentPreview.chunk_count}
                    </div>
                    <div>
                      <span className="font-medium">Created:</span>{" "}
                      {new Date(documentPreview.created_at).toLocaleString()}
                    </div>
                    <div>
                      <span className="font-medium">Status:</span>{" "}
                      {documentPreview.status}
                    </div>
                  </div>

                  {documentPreview.tags.length > 0 && (
                    <div>
                      <span className="font-medium text-sm mb-2 block">
                        Tags:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {documentPreview.tags.map((tag) => (
                          <Badge
                            key={tag}
                            variant="secondary"
                            className="text-xs"
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default KnowledgeBase;
