import React, { useState, useEffect } from "react";
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
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./ui/accordion";
import {
  Heart,
  Brain,
  Users,
  Target,
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  Loader2,
  Download,
  RefreshCw,
  MessageCircle,
  TrendingUp,
  Star,
} from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { cn } from "../lib/utils";

const TherapeuticInterventions = () => {
  const [conversationId, setConversationId] = useState("");
  const [approachPreferences, setApproachPreferences] = useState([]);
  const [interventionTypes, setInterventionTypes] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [interventionPlan, setInterventionPlan] = useState(null);
  const [error, setError] = useState(null);
  const [availableOptions, setAvailableOptions] = useState({
    approaches: [],
    interventionTypes: [],
  });
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  const { toast } = useToast();

  // Load available options on component mount
  useEffect(() => {
    loadAvailableOptions();
  }, []);

  const loadAvailableOptions = async () => {
    try {
      const [approachesResponse, typesResponse] = await Promise.all([
        fetch("/api/v1/advanced/interventions/approaches", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }),
        fetch("/api/v1/advanced/interventions/types", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }),
      ]);

      if (approachesResponse.ok && typesResponse.ok) {
        const approaches = await approachesResponse.json();
        const types = await typesResponse.json();

        setAvailableOptions({
          approaches,
          interventionTypes: types,
        });
      }
    } catch (error) {
      console.error("Error loading options:", error);
    }
  };

  const handleApproachToggle = (approach) => {
    setApproachPreferences((prev) =>
      prev.includes(approach)
        ? prev.filter((a) => a !== approach)
        : [...prev, approach]
    );
  };

  const handleInterventionTypeToggle = (type) => {
    setInterventionTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const generateInterventions = async () => {
    setIsGenerating(true);
    setGenerationProgress(0);
    setError(null);
    setInterventionPlan(null);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress((prev) => Math.min(prev + 12, 90));
      }, 400);

      const requestBody = {
        conversation_id: conversationId || null,
        approach_preferences:
          approachPreferences.length > 0 ? approachPreferences : null,
        intervention_types:
          interventionTypes.length > 0 ? interventionTypes : null,
        custom_config: {},
      };

      const response = await fetch("/api/v1/advanced/interventions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(requestBody),
      });

      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (response.ok) {
        const result = await response.json();
        setInterventionPlan(result);
        toast({
          title: "Interventions Generated",
          description:
            "Therapeutic intervention plan has been created successfully.",
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Intervention generation failed");
      }
    } catch (error) {
      console.error("Intervention generation error:", error);
      setError(error.message);
      toast({
        title: "Generation Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
      setTimeout(() => setGenerationProgress(0), 1000);
    }
  };

  const downloadPlan = () => {
    if (!interventionPlan) return;

    const dataStr = JSON.stringify(interventionPlan, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `therapeutic_intervention_plan_${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low":
        return "text-green-600 bg-green-50 border-green-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getApproachIcon = (approach) => {
    switch (approach?.toLowerCase()) {
      case "cbt":
        return <Brain className="h-4 w-4" />;
      case "gottman":
        return <Heart className="h-4 w-4" />;
      case "eft":
        return <Users className="h-4 w-4" />;
      case "dbt":
        return <Target className="h-4 w-4" />;
      default:
        return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case "communication":
        return <MessageCircle className="h-4 w-4" />;
      case "conflict_resolution":
        return <Users className="h-4 w-4" />;
      case "emotional_regulation":
        return <Heart className="h-4 w-4" />;
      case "behavioral_change":
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Target className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            Therapeutic Intervention Recommendations
          </CardTitle>
          <CardDescription>
            Generate AI-powered therapeutic interventions and personalized
            recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="conversation-id">Conversation ID (Optional)</Label>
            <Input
              id="conversation-id"
              placeholder="Enter conversation ID to analyze specific conversation"
              value={conversationId}
              onChange={(e) => setConversationId(e.target.value)}
            />
            <p className="text-xs text-gray-500">
              Leave empty to use sample conversation data for demonstration
            </p>
          </div>

          <Tabs defaultValue="approaches" className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="approaches">
                Therapeutic Approaches
              </TabsTrigger>
              <TabsTrigger value="types">Intervention Types</TabsTrigger>
            </TabsList>

            <TabsContent value="approaches" className="space-y-4">
              <div className="space-y-2">
                <Label>Preferred Therapeutic Approaches (Optional)</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {availableOptions.approaches.map((approach) => (
                    <div key={approach} className="flex items-center space-x-2">
                      <Checkbox
                        id={`approach-${approach}`}
                        checked={approachPreferences.includes(approach)}
                        onCheckedChange={() => handleApproachToggle(approach)}
                      />
                      <Label
                        htmlFor={`approach-${approach}`}
                        className="text-sm flex items-center gap-2"
                      >
                        {getApproachIcon(approach)}
                        {approach.toUpperCase()}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="types" className="space-y-4">
              <div className="space-y-2">
                <Label>Intervention Types (Optional)</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {availableOptions.interventionTypes.map((type) => (
                    <div key={type} className="flex items-center space-x-2">
                      <Checkbox
                        id={`type-${type}`}
                        checked={interventionTypes.includes(type)}
                        onCheckedChange={() =>
                          handleInterventionTypeToggle(type)
                        }
                      />
                      <Label
                        htmlFor={`type-${type}`}
                        className="text-sm flex items-center gap-2"
                      >
                        {getTypeIcon(type)}
                        {type
                          .replace("_", " ")
                          .replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {isGenerating && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Generating therapeutic interventions...</span>
                <span>{generationProgress}%</span>
              </div>
              <Progress value={generationProgress} className="w-full" />
            </div>
          )}

          <Button
            onClick={generateInterventions}
            disabled={isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Interventions...
              </>
            ) : (
              <>
                <Brain className="h-4 w-4 mr-2" />
                Generate Therapeutic Interventions
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {interventionPlan && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Intervention Plan Overview</span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setInterventionPlan(null)}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Clear
                  </Button>
                  <Button variant="outline" size="sm" onClick={downloadPlan}>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg mb-2">
                    {interventionPlan.title}
                  </h3>
                  <p className="text-gray-600">
                    {interventionPlan.assessment_summary}
                  </p>
                </div>

                {interventionPlan.primary_concerns &&
                  interventionPlan.primary_concerns.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Primary Concerns</h4>
                      <div className="flex flex-wrap gap-2">
                        {interventionPlan.primary_concerns.map(
                          (concern, index) => (
                            <Badge key={index} variant="destructive">
                              {concern}
                            </Badge>
                          )
                        )}
                      </div>
                    </div>
                  )}

                {interventionPlan.identified_patterns &&
                  interventionPlan.identified_patterns.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Identified Patterns</h4>
                      <div className="flex flex-wrap gap-2">
                        {interventionPlan.identified_patterns.map(
                          (pattern, index) => (
                            <Badge key={index} variant="secondary">
                              {pattern
                                .replace("_", " ")
                                .replace(/\b\w/g, (l) => l.toUpperCase())}
                            </Badge>
                          )
                        )}
                      </div>
                    </div>
                  )}

                {interventionPlan.overall_goals &&
                  interventionPlan.overall_goals.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Overall Goals</h4>
                      <ul className="space-y-1">
                        {interventionPlan.overall_goals.map((goal, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <Target className="h-4 w-4 text-blue-600 mt-0.5" />
                            <span className="text-sm">{goal}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
            </CardContent>
          </Card>

          {interventionPlan.interventions &&
            interventionPlan.interventions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Recommended Interventions</CardTitle>
                  <CardDescription>
                    {interventionPlan.interventions.length} personalized
                    therapeutic interventions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="space-y-2">
                    {interventionPlan.interventions.map(
                      (intervention, index) => (
                        <AccordionItem
                          key={index}
                          value={`intervention-${index}`}
                        >
                          <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center justify-between w-full mr-4">
                              <div className="flex items-center gap-3">
                                {getApproachIcon(intervention.approach)}
                                <div className="text-left">
                                  <div className="font-medium">
                                    {intervention.title}
                                  </div>
                                  <div className="text-sm text-gray-500">
                                    {intervention.approach?.toUpperCase()} •{" "}
                                    {intervention.type?.replace("_", " ")}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge
                                  variant="outline"
                                  className={cn(
                                    "text-xs",
                                    getPriorityColor(intervention.priority)
                                  )}
                                >
                                  {intervention.priority} Priority
                                </Badge>
                                {intervention.priority === "high" && (
                                  <Star className="h-4 w-4 text-yellow-500" />
                                )}
                              </div>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent>
                            <div className="space-y-4 pt-2">
                              <div>
                                <h5 className="font-medium mb-2">
                                  Description
                                </h5>
                                <p className="text-sm text-gray-600">
                                  {intervention.description}
                                </p>
                              </div>

                              {intervention.rationale && (
                                <div>
                                  <h5 className="font-medium mb-2">
                                    Rationale
                                  </h5>
                                  <p className="text-sm text-gray-600">
                                    {intervention.rationale}
                                  </p>
                                </div>
                              )}

                              {intervention.techniques &&
                                intervention.techniques.length > 0 && (
                                  <div>
                                    <h5 className="font-medium mb-2">
                                      Techniques
                                    </h5>
                                    <div className="space-y-3">
                                      {intervention.techniques.map(
                                        (technique, techIndex) => (
                                          <div
                                            key={techIndex}
                                            className="border rounded-lg p-3 bg-gray-50"
                                          >
                                            <h6 className="font-medium text-sm mb-1">
                                              {technique.name}
                                            </h6>
                                            <p className="text-xs text-gray-600 mb-2">
                                              {technique.description}
                                            </p>
                                            {technique.instructions && (
                                              <div className="text-xs">
                                                <span className="font-medium">
                                                  Instructions:
                                                </span>
                                                <p className="mt-1 text-gray-600">
                                                  {technique.instructions}
                                                </p>
                                              </div>
                                            )}
                                          </div>
                                        )
                                      )}
                                    </div>
                                  </div>
                                )}

                              <div className="flex gap-2 pt-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() =>
                                    setSelectedIntervention(intervention)
                                  }
                                >
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Mark as Applied
                                </Button>
                                <Button size="sm" variant="ghost">
                                  <MessageCircle className="h-4 w-4 mr-2" />
                                  Add Notes
                                </Button>
                              </div>
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      )
                    )}
                  </Accordion>
                </CardContent>
              </Card>
            )}

          {interventionPlan.generation_time && (
            <div className="text-sm text-gray-600 text-center">
              Intervention plan generated in {interventionPlan.generation_time}
              ms
            </div>
          )}
        </div>
      )}

      {selectedIntervention && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            Intervention "{selectedIntervention.title}" has been marked as
            applied.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default TherapeuticInterventions;
