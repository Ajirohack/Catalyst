import React, { useEffect } from "react";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAnalysisProgress, useAnalysis } from "@/hooks/useAnalysis";

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
      duration: 0.5,
    },
  },
};

export default function AnalysisProgress({
  projectId,
  analysisId,
  onComplete,
}) {
  const {
    data: progress,
    isLoading,
    error,
    refetch,
  } = useAnalysisProgress(projectId, analysisId);
  const { cancelAnalysis } = useAnalysis();

  // Automatically call onComplete when analysis is complete
  useEffect(() => {
    if (progress?.status === "completed" && onComplete) {
      onComplete(analysisId);
    }
  }, [progress?.status, analysisId, onComplete]);

  const handleCancel = async () => {
    if (
      confirm(
        "Are you sure you want to cancel this analysis? This action cannot be undone."
      )
    ) {
      try {
        await cancelAnalysis.mutateAsync({ projectId, analysisId });
      } catch (err) {
        console.error("Failed to cancel analysis:", err);
      }
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">
              Loading analysis progress...
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center text-red-500">
            <p>Error loading analysis progress.</p>
            <p className="text-sm mt-2">{error.message}</p>
            <Button onClick={refetch} className="mt-4" variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!progress) {
    return (
      <Card>
        <CardContent className="py-10">
          <div className="text-center">
            <p className="text-muted-foreground">No progress data available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case "failed":
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case "cancelled":
        return <Badge className="bg-gray-100 text-gray-800">Cancelled</Badge>;
      case "queued":
        return <Badge className="bg-amber-100 text-amber-800">Queued</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  // Format time
  const formatTime = (seconds) => {
    if (!seconds && seconds !== 0) return "Unknown";

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);

    if (minutes < 1) {
      return `${remainingSeconds} seconds`;
    }

    return `${minutes} min ${remainingSeconds} sec`;
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Analysis Progress</CardTitle>
                <CardDescription>
                  {progress.status === "in_progress"
                    ? "Your conversation data is being processed"
                    : progress.status === "completed"
                      ? "Analysis has been completed successfully"
                      : progress.status === "failed"
                        ? "Analysis encountered an error"
                        : progress.status === "cancelled"
                          ? "Analysis was cancelled"
                          : "Analysis is queued and will start soon"}
                </CardDescription>
              </div>
              {getStatusBadge(progress.status)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {progress.status === "in_progress" && (
                <>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{progress.progress_percentage}% Complete</span>
                      <span>
                        {formatTime(progress.estimated_time_remaining)}{" "}
                        remaining
                      </span>
                    </div>
                    <Progress
                      value={progress.progress_percentage}
                      className="h-2"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Current Stage
                      </p>
                      <p className="font-medium">{progress.current_stage}</p>
                    </div>
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Processing Time
                      </p>
                      <p className="font-medium">
                        {formatTime(progress.elapsed_time)}
                      </p>
                    </div>
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Items Processed
                      </p>
                      <p className="font-medium">
                        {progress.items_processed} / {progress.total_items}
                      </p>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4 bg-blue-50 text-blue-800 mt-4">
                    <h4 className="font-semibold mb-2">Currently Processing</h4>
                    <p className="text-sm">{progress.current_activity}</p>
                  </div>

                  <div className="flex justify-end mt-4">
                    <Button
                      variant="outline"
                      onClick={handleCancel}
                      disabled={cancelAnalysis.isLoading}
                    >
                      {cancelAnalysis.isLoading
                        ? "Cancelling..."
                        : "Cancel Analysis"}
                    </Button>
                  </div>
                </>
              )}

              {progress.status === "completed" && (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800">
                    <h4 className="font-semibold mb-2">Analysis Complete</h4>
                    <p>
                      Your conversation analysis has been successfully
                      processed.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Conversations
                      </p>
                      <p className="font-medium">
                        {progress.total_conversations}
                      </p>
                    </div>
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Processing Time
                      </p>
                      <p className="font-medium">
                        {formatTime(progress.elapsed_time)}
                      </p>
                    </div>
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Completion Time
                      </p>
                      <p className="font-medium">
                        {new Date(progress.completed_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-end mt-4">
                    <Button onClick={() => onComplete(analysisId)}>
                      View Results
                    </Button>
                  </div>
                </div>
              )}

              {progress.status === "failed" && (
                <div className="space-y-4">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                    <h4 className="font-semibold mb-2">Analysis Failed</h4>
                    <p>
                      {progress.error_message ||
                        "There was an error processing your analysis."}
                    </p>
                  </div>

                  <div className="bg-muted/20 p-4 rounded-lg mt-4">
                    <p className="text-sm text-muted-foreground mb-1">
                      Error Details
                    </p>
                    <p className="font-medium">
                      {progress.error_details ||
                        "No additional details available."}
                    </p>
                  </div>

                  <div className="flex justify-end mt-4 space-x-2">
                    <Button variant="outline" onClick={refetch}>
                      Retry Check
                    </Button>
                    <Button onClick={() => window.location.reload()}>
                      Start New Analysis
                    </Button>
                  </div>
                </div>
              )}

              {progress.status === "queued" && (
                <div className="space-y-4">
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-800">
                    <h4 className="font-semibold mb-2">Analysis Queued</h4>
                    <p>Your analysis is in the queue and will start soon.</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Queue Position
                      </p>
                      <p className="font-medium">{progress.queue_position}</p>
                    </div>
                    <div className="bg-muted/20 p-4 rounded-lg">
                      <p className="text-sm text-muted-foreground mb-1">
                        Estimated Start
                      </p>
                      <p className="font-medium">
                        {formatTime(progress.estimated_start_time)}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-end mt-4">
                    <Button
                      variant="outline"
                      onClick={handleCancel}
                      disabled={cancelAnalysis.isLoading}
                    >
                      {cancelAnalysis.isLoading
                        ? "Cancelling..."
                        : "Cancel Analysis"}
                    </Button>
                  </div>
                </div>
              )}

              {progress.status === "cancelled" && (
                <div className="space-y-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-gray-800">
                    <h4 className="font-semibold mb-2">Analysis Cancelled</h4>
                    <p>This analysis was cancelled and did not complete.</p>
                  </div>

                  <div className="flex justify-end mt-4">
                    <Button onClick={() => window.location.reload()}>
                      Start New Analysis
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
