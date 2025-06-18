import React from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useProject } from "@/hooks/useProjects";
import AnalysisProgress from "@/components/analysis/AnalysisProgress";

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

export default function AnalysisProgressPage() {
  const { projectId, analysisId } = useParams();
  const navigate = useNavigate();
  const { data: project, isLoading: projectLoading } = useProject(projectId);

  // Handle completion of analysis
  const handleAnalysisComplete = (completedAnalysisId) => {
    navigate(`/projects/${projectId}/analysis/${completedAnalysisId}`);
  };

  if (projectLoading) {
    return (
      <div className="container max-w-6xl py-10">
        <div className="text-center py-20">
          <p className="text-muted-foreground">Loading project data...</p>
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
            <h1 className="text-3xl font-bold mb-2">{project.name}</h1>
            <p className="text-muted-foreground">
              Analysis #{analysisId} • Tracking Progress
            </p>
          </div>
          <Link to={`/projects/${projectId}`}>
            <Button variant="outline">Back to Project</Button>
          </Link>
        </div>
      </motion.div>

      <AnalysisProgress
        projectId={projectId}
        analysisId={analysisId}
        onComplete={handleAnalysisComplete}
      />
    </motion.div>
  );
}
