import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useProject } from "../../hooks/useProjects";
import { useAnalysis, useAnalysisHistory } from "../../hooks/useAnalysis";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import AnalysisSummary from "@/components/analysis/AnalysisSummary";
import api from "../../lib/api";
import { toast } from "react-hot-toast";

export default function ProjectDetail() {
  const { id } = useParams();
  const { data: project, isLoading, isError, error } = useProject(id);
  const { startAnalysis } = useAnalysis();
  const { data: analysisHistory } = useAnalysisHistory(id);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const navigate = useNavigate();

  // Get the latest analysis data if available
  const latestAnalysis =
    analysisHistory?.length > 0
      ? analysisHistory.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        )[0]
      : null;

  // Handle file upload
  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploadingFile(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post(`/projects/${id}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      toast.success("File uploaded successfully");
    } catch (err) {
      console.error("Upload error:", err);
      toast.error(err.response?.data?.message || "Error uploading file");
    } finally {
      setUploadingFile(false);
    }
  };

  // Handle file change for upload
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  // Handle starting analysis
  const handleStartAnalysis = async () => {
    try {
      const result = await startAnalysis.mutateAsync({
        projectId: id,
        options: {
          comprehensive: true,
        },
      });

      toast.success("Analysis started successfully");

      // Navigate to progress tracking page
      navigate(`/projects/${id}/analysis/${result.analysis_id}/progress`);
    } catch (err) {
      console.error("Failed to start analysis:", err);
      toast.error("Failed to start analysis");
    }
  };

  // Handle viewing analysis
  const handleViewAnalysis = () => {
    if (analysisHistory && analysisHistory.length > 0) {
      // Find most recent completed analysis
      const latestAnalysis = analysisHistory.find(
        (a) => a.status === "completed"
      );

      if (latestAnalysis) {
        navigate(`/projects/${id}/analysis/${latestAnalysis.id}`);
      } else {
        toast.error("No completed analysis found");
      }
    } else {
      toast.error("No analysis available");
    }
  };

  // Get role display name
  const getRoleDisplayName = (role) => {
    switch (role) {
      case "coach":
        return "Conversation Coach";
      case "therapist":
        return "Communication Therapist";
      case "strategist":
        return "Dialogue Strategist";
      default:
        return role;
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  if (isLoading) {
    return <div className="container py-10">Loading project...</div>;
  }

  if (isError) {
    return (
      <div className="container py-10">
        <div className="text-red-500">Error: {error.message}</div>
        <Link to="/projects">
          <Button variant="outline" className="mt-4">
            Back to Projects
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <Link to="/projects">
          <Button variant="outline">Back to Projects</Button>
        </Link>
      </div>

      {/* Project Details Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Role</dt>
              <dd className="mt-1">
                <Badge variant="outline">
                  {getRoleDisplayName(project.role)}
                </Badge>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-1">{formatDate(project.created_at)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">
                Last Updated
              </dt>
              <dd className="mt-1">{formatDate(project.last_updated)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1">
                <Badge
                  className={
                    project.status === "active"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }
                >
                  {project.status || "No Status"}
                </Badge>
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      {/* Upload Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Upload Conversation Data</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-gray-600">
            Upload conversation data from external sources or use the Chrome
            extension to capture live conversations.
          </p>

          <div className="flex flex-col space-y-4">
            <label className="w-full">
              <Button
                variant="outline"
                className="w-full h-24 flex flex-col items-center justify-center border-dashed"
                onClick={() => document.getElementById("file-upload").click()}
                disabled={uploadingFile}
              >
                <span className="text-lg mb-1">
                  {uploadingFile
                    ? "Uploading..."
                    : "Drag & drop or click to upload"}
                </span>
                <span className="text-sm text-gray-500">
                  Supports .txt, .csv, .json files
                </span>
              </Button>
              <input
                id="file-upload"
                type="file"
                className="hidden"
                accept=".txt,.csv,.json"
                onChange={handleFileChange}
                disabled={uploadingFile}
              />
            </label>

            {uploadingFile && (
              <div className="w-full">
                <Progress value={uploadProgress} className="h-2" />
                <p className="text-xs text-center mt-1">
                  {uploadProgress}% complete
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results Section */}
      {project.has_analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalysisSummary projectId={id} />

            <Button
              className="mt-4"
              onClick={handleViewAnalysis}
              disabled={!analysisHistory?.length}
            >
              View Full Analysis
            </Button>
          </CardContent>
        </Card>
      )}

      {!project.has_analysis && project.conversation_count > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Start Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              You have {project.conversation_count} conversations ready to
              analyze.
            </p>

            <Button onClick={handleStartAnalysis}>Start Analysis</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
