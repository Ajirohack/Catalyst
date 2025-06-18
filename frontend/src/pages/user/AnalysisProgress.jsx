import React, { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAnalysisProgress } from "@/hooks/useAnalysis";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "react-hot-toast";

/**
 * Component that displays real-time progress of an ongoing analysis
 */
const AnalysisProgress = () => {
  const { projectId, analysisId } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useAnalysisProgress(
    projectId,
    analysisId
  );

  // Redirect to results page when analysis completes
  useEffect(() => {
    if (data?.status === "completed") {
      toast.success("Analysis completed successfully!");
      navigate(`/projects/${projectId}/analysis/${analysisId}`);
    } else if (data?.status === "failed") {
      toast.error("Analysis failed. Please try again.");
    }
  }, [data?.status, projectId, analysisId, navigate]);

  // Calculate progress percentage
  const getProgressPercentage = () => {
    if (!data) return 0;
    if (data.status === "completed") return 100;
    if (data.status === "failed") return 0;
    return data.progress_percentage || 0;
  };

  // Format estimated time remaining
  const formatTimeRemaining = () => {
    if (!data || !data.estimated_time_remaining) return "Calculating...";

    const minutes = Math.floor(data.estimated_time_remaining / 60);
    const seconds = data.estimated_time_remaining % 60;

    if (minutes === 0) {
      return `${seconds} seconds remaining`;
    } else if (minutes === 1) {
      return `1 minute ${seconds} seconds remaining`;
    } else {
      return `${minutes} minutes ${seconds} seconds remaining`;
    }
  };

  // Handle cancel button
  const handleCancel = () => {
    if (window.confirm("Are you sure you want to cancel this analysis?")) {
      // Implement cancel functionality
      toast.success("Analysis cancelled");
      navigate(`/projects/${projectId}`);
    }
  };

  if (isLoading) {
    return (
      <div className="container max-w-4xl py-10">
        <Card>
          <CardHeader>
            <CardTitle>Loading Analysis Progress...</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <div className="spinner mb-4"></div>
              <p>Retrieving analysis information...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container max-w-4xl py-10">
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-red-500 mb-4">
                Failed to load analysis progress: {error.message}
              </p>
              <Button onClick={() => navigate(`/projects/${projectId}`)}>
                Back to Project
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Analysis Progress</h1>
        <Button
          variant="outline"
          onClick={() => navigate(`/projects/${projectId}`)}
        >
          Back to Project
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>
              {data?.status === "in_progress"
                ? "Processing Analysis"
                : "Analysis Status"}
            </CardTitle>
            <Badge
              className={
                data?.status === "in_progress"
                  ? "bg-blue-100 text-blue-800"
                  : data?.status === "completed"
                    ? "bg-green-100 text-green-800"
                    : data?.status === "failed"
                      ? "bg-red-100 text-red-800"
                      : "bg-gray-100 text-gray-800"
              }
            >
              {data?.status === "in_progress"
                ? "In Progress"
                : data?.status === "completed"
                  ? "Completed"
                  : data?.status === "failed"
                    ? "Failed"
                    : "Unknown"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-500">Progress</span>
              <span className="text-sm font-medium">
                {getProgressPercentage()}%
              </span>
            </div>
            <Progress value={getProgressPercentage()} className="h-2" />
          </div>

          {data?.status === "in_progress" && (
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-500 mb-1">
                  Estimated Time Remaining
                </div>
                <div>{formatTimeRemaining()}</div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">
                  Current Operation
                </div>
                <div>{data?.current_operation || "Initializing..."}</div>
              </div>

              {data?.progress_details && (
                <div>
                  <div className="text-sm text-gray-500 mb-1">Details</div>
                  <div className="text-sm">
                    {data.progress_details.messages_processed
                      ? `${data.progress_details.messages_processed} messages processed`
                      : ""}
                    {data.progress_details.files_processed
                      ? `${data.progress_details.files_processed} files processed`
                      : ""}
                  </div>
                </div>
              )}

              <div className="pt-4">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleCancel}
                >
                  Cancel Analysis
                </Button>
              </div>
            </div>
          )}

          {data?.status === "failed" && (
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-500 mb-1">
                  Error Information
                </div>
                <div className="text-red-500">
                  {data?.error_message || "Unknown error occurred"}
                </div>
              </div>

              <div className="pt-4 flex space-x-4">
                <Button
                  className="flex-1"
                  onClick={() => navigate(`/projects/${projectId}`)}
                >
                  Back to Project
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {data?.stats && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500">Messages Processed</div>
                <div className="font-medium">
                  {data.stats.messages_processed || 0}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Files Processed</div>
                <div className="font-medium">
                  {data.stats.files_processed || 0}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Start Time</div>
                <div className="font-medium">
                  {data.stats.start_time
                    ? new Date(data.stats.start_time).toLocaleString()
                    : "N/A"}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Processing Time</div>
                <div className="font-medium">
                  {data.stats.elapsed_time
                    ? `${Math.round(data.stats.elapsed_time / 60)} minutes`
                    : "N/A"}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AnalysisProgress;
