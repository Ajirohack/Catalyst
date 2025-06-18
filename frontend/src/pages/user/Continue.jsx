import { useState } from "react";
import { Link } from "react-router-dom";
import { useProjects } from "../../hooks/useProjects";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function Continue() {
  const { listProjects } = useProjects();
  const [isLoading, setIsLoading] = useState(false);

  // Format date to a readable format
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // Function to get badge color based on role
  const getRoleBadgeColor = (role) => {
    switch (role) {
      case "coach":
        return "bg-blue-100 text-blue-800";
      case "therapist":
        return "bg-green-100 text-green-800";
      case "strategist":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
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

  if (listProjects.isLoading) {
    return (
      <div className="container max-w-4xl py-10">
        <div className="text-center">Loading projects...</div>
      </div>
    );
  }

  if (listProjects.isError) {
    return (
      <div className="container max-w-4xl py-10">
        <div className="text-center text-red-500">
          Error loading projects: {listProjects.error.message}
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Projects</h1>
        <Link to="/projects/new">
          <Button>Create New Project</Button>
        </Link>
      </div>

      {listProjects.data?.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="mb-4 text-lg text-gray-600">
              You don't have any projects yet.
            </p>
            <Link to="/projects/new">
              <Button>Create Your First Project</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {listProjects.data?.map((project) => (
            <Link to={`/projects/${project.id}`} key={project.id}>
              <Card className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="text-xl font-semibold mb-2">
                        {project.name}
                      </h2>
                      <Badge className={getRoleBadgeColor(project.role)}>
                        {getRoleDisplayName(project.role)}
                      </Badge>
                      <p className="mt-3 text-sm text-gray-500">
                        Created: {formatDate(project.created_at)}
                      </p>
                      {project.last_updated && (
                        <p className="text-sm text-gray-500">
                          Last activity: {formatDate(project.last_updated)}
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">
                        {project.conversation_count || 0} conversations
                      </div>
                      {project.analysis_status === "completed" && (
                        <Badge className="bg-green-100 text-green-800 mt-2">
                          Analysis Complete
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
