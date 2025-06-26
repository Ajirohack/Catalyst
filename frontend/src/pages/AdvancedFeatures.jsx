import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import { Badge } from "../components/ui/badge";
import {
  MessageSquare,
  BarChart3,
  Heart,
  Sparkles,
  FileText,
  TrendingUp,
  Brain,
  Users,
  Target,
  CheckCircle,
  Star,
  Zap,
} from "lucide-react";
import MultiFormatProcessor from "../components/MultiFormatProcessor";
import AdvancedReporting from "../components/AdvancedReporting";
import TherapeuticInterventions from "../components/TherapeuticInterventions";

const AdvancedFeatures = () => {
  const [activeTab, setActiveTab] = useState("processor");

  const features = [
    {
      id: "processor",
      title: "Multi-Format Input Processing",
      description:
        "Process conversations from various platforms and formats with advanced AI analysis",
      icon: <MessageSquare className="h-6 w-6" />,
      color: "bg-blue-500",
      capabilities: [
        "WhatsApp, Messenger, Discord, Slack conversations",
        "Audio transcription and analysis",
        "PDF and document processing",
        "Real-time streaming analysis",
        "Batch and incremental processing",
      ],
      component: <MultiFormatProcessor />,
    },
    {
      id: "reporting",
      title: "Advanced Reporting & Visualizations",
      description:
        "Generate comprehensive reports with interactive visualizations and insights",
      icon: <BarChart3 className="h-6 w-6" />,
      color: "bg-green-500",
      capabilities: [
        "Interactive charts and graphs",
        "Sentiment timeline analysis",
        "Communication pattern heatmaps",
        "Relationship health radar charts",
        "Exportable reports (PDF, JSON, HTML)",
      ],
      component: <AdvancedReporting />,
    },
    {
      id: "interventions",
      title: "Therapeutic Intervention Recommendations",
      description:
        "AI-powered therapeutic interventions and personalized recommendations",
      icon: <Heart className="h-6 w-6" />,
      color: "bg-purple-500",
      capabilities: [
        "CBT, Gottman, EFT therapeutic approaches",
        "Personalized intervention strategies",
        "Conflict resolution techniques",
        "Emotional regulation exercises",
        "Progress tracking and outcomes",
      ],
      component: <TherapeuticInterventions />,
    },
  ];

  const stats = [
    {
      label: "Supported Formats",
      value: "15+",
      icon: <FileText className="h-5 w-5" />,
      color: "text-blue-600",
    },
    {
      label: "Analysis Types",
      value: "12+",
      icon: <TrendingUp className="h-5 w-5" />,
      color: "text-green-600",
    },
    {
      label: "Therapeutic Approaches",
      value: "8+",
      icon: <Brain className="h-5 w-5" />,
      color: "text-purple-600",
    },
    {
      label: "Visualization Types",
      value: "10+",
      icon: <BarChart3 className="h-5 w-5" />,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-purple-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Advanced Features
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Unlock the full potential of Catalyst with cutting-edge AI-powered
            conversation analysis, advanced reporting, and therapeutic
            intervention recommendations.
          </p>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mt-8">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-4 shadow-sm border"
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className={stat.color}>{stat.icon}</div>
                  <span className="text-2xl font-bold text-gray-900">
                    {stat.value}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card
              key={feature.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                activeTab === feature.id
                  ? "ring-2 ring-purple-500 shadow-lg"
                  : ""
              }`}
              onClick={() => setActiveTab(feature.id)}
            >
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${feature.color} text-white`}>
                    {feature.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    {activeTab === feature.id && (
                      <Badge variant="secondary" className="mt-1">
                        <Star className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    )}
                  </div>
                </div>
                <CardDescription className="text-sm">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700">
                    Key Capabilities:
                  </h4>
                  <ul className="space-y-1">
                    {feature.capabilities
                      .slice(0, 3)
                      .map((capability, index) => (
                        <li
                          key={index}
                          className="flex items-start gap-2 text-xs text-gray-600"
                        >
                          <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{capability}</span>
                        </li>
                      ))}
                    {feature.capabilities.length > 3 && (
                      <li className="text-xs text-gray-500 italic">
                        +{feature.capabilities.length - 3} more features...
                      </li>
                    )}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content */}
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-3 max-w-2xl mx-auto">
            {features.map((feature) => (
              <TabsTrigger
                key={feature.id}
                value={feature.id}
                className="flex items-center gap-2"
              >
                {feature.icon}
                <span className="hidden sm:inline">
                  {feature.title.split(" ")[0]}
                </span>
              </TabsTrigger>
            ))}
          </TabsList>

          {features.map((feature) => (
            <TabsContent
              key={feature.id}
              value={feature.id}
              className="space-y-6"
            >
              <div className="bg-white rounded-lg p-6 shadow-sm border">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`p-3 rounded-lg ${feature.color} text-white`}>
                    {feature.icon}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {feature.title}
                    </h2>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-semibold text-gray-700 mb-3">
                    Full Capabilities:
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {feature.capabilities.map((capability, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <Zap className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-600">
                          {capability}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {feature.component}
            </TabsContent>
          ))}
        </Tabs>

        {/* Footer */}
        <div className="text-center py-8">
          <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            <p className="text-lg font-semibold">
              Powered by Advanced AI • Built for Relationship Success
            </p>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Experience the future of relationship analysis and therapeutic
            support
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFeatures;
