import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useProject } from "@/hooks/useProjects";
import { useSpecificAnalysis } from "@/hooks/useAnalysis";
import AnalysisResults from "@/components/analysis/AnalysisResults";

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

export default function AnalysisPage() {
  const { projectId, analysisId } = useParams();
  const navigate = useNavigate();
  const { data: project, isLoading: projectLoading } = useProject(projectId);
  const { data: analysis, isLoading: analysisLoading } = useSpecificAnalysis(
    projectId,
    analysisId
  );

  if (projectLoading || analysisLoading) {
    return (
      <div className="container max-w-6xl py-10">
        <div className="text-center py-20">
          <p className="text-muted-foreground">Loading analysis data...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container max-w-6xl py-10">
        <div className="text-center py-20 text-red-500">
          <p>Project not found.</p>
          <Link to="/projects">
            <Button variant="outline" className="mt-4">
              Back to Projects
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="container max-w-6xl py-10">
        <div className="text-center py-20 text-red-500">
          <p>Analysis not found or still in progress.</p>
          <Link to={`/projects/${projectId}`}>
            <Button variant="outline" className="mt-4">
              Back to Project
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="container max-w-6xl py-10"
    >
      <motion.div variants={itemVariants} className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {project.name} - Analysis
            </h1>
            <p className="text-muted-foreground">
              Analysis #{analysisId} • Completed on{" "}
              {new Date(analysis.completed_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            <Link to={`/projects/${projectId}`}>
              <Button variant="outline">Back to Project</Button>
            </Link>
            <Button onClick={() => window.print()}>Print Report</Button>
          </div>
        </div>
      </motion.div>

      <AnalysisResults projectId={projectId} analysisId={analysisId} />
    </motion.div>
  );
}
