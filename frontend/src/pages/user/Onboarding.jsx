import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "../../components/ui/button";
import { Card, CardContent } from "../../components/ui/card";
import { useNavigate } from "react-router-dom";

/**
 * Onboarding component for new users
 * Guides users through the platform features with interactive tutorials
 */
const Onboarding = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [skipped, setSkipped] = useState(false);

  // Total number of steps in the onboarding process
  const totalSteps = 5;

  // Animation variants
  const variants = {
    enter: (direction) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction) => ({
      x: direction < 0 ? 1000 : -1000,
      opacity: 0,
    }),
  };

  // Handle next step
  const handleNext = () => {
    if (step < totalSteps - 1) {
      setStep(step + 1);
    } else {
      completeOnboarding();
    }
  };

  // Handle previous step
  const handlePrevious = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  // Skip onboarding
  const handleSkip = () => {
    setSkipped(true);
    completeOnboarding();
  };

  // Complete the onboarding process
  const completeOnboarding = () => {
    // Mark onboarding as completed in user settings
    localStorage.setItem("onboardingCompleted", "true");

    // Redirect to dashboard
    navigate("/dashboard");
  };

  // Onboarding steps content
  const steps = [
    {
      title: "Welcome to Catalyst",
      description:
        "Your AI-powered relationship coach. Let's get you started with a quick tour.",
      image: "/images/onboarding/welcome.svg",
      content: (
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Welcome to Catalyst</h1>
          <p className="text-lg mb-6">
            Your AI-powered relationship coach that helps you analyze
            conversations and improve your communication skills in real-time.
          </p>
          <div className="mb-8">
            <img
              src="/images/onboarding/welcome.svg"
              alt="Welcome to Catalyst"
              className="max-w-sm mx-auto"
            />
          </div>
        </div>
      ),
    },
    {
      title: "Create Your First Project",
      description:
        "Projects help you organize your conversation analyses by relationship type.",
      image: "/images/onboarding/projects.svg",
      content: (
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Create Your First Project</h1>
          <p className="text-lg mb-6">
            Projects help you organize conversations by relationship type. Start
            by creating a project for a specific relationship you want to
            improve.
          </p>
          <div className="mb-8">
            <img
              src="/images/onboarding/projects.svg"
              alt="Create Projects"
              className="max-w-sm mx-auto"
            />
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-left mb-6">
            <h3 className="font-medium text-blue-800 mb-2">
              Project Examples:
            </h3>
            <ul className="list-disc pl-5 space-y-1 text-blue-700">
              <li>Work Communication</li>
              <li>Partner Conversations</li>
              <li>Family Discussions</li>
              <li>Client Interactions</li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      title: "Install the Chrome Extension",
      description:
        "Capture conversations from popular messaging platforms with our extension.",
      image: "/images/onboarding/extension.svg",
      content: (
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">
            Install the Chrome Extension
          </h1>
          <p className="text-lg mb-6">
            Our Chrome extension allows you to capture conversations from
            popular messaging platforms and get real-time coaching.
          </p>
          <div className="mb-8">
            <img
              src="/images/onboarding/extension.svg"
              alt="Chrome Extension"
              className="max-w-sm mx-auto"
            />
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-left mb-6">
            <h3 className="font-medium text-green-800 mb-2">
              Supported Platforms:
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center space-x-2">
                <span className="text-green-700">WhatsApp</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-700">Messenger</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-700">Slack</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-700">Discord</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-700">Teams</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-green-700">And many more...</span>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Analyze Your Conversations",
      description: "Get detailed insights into your communication patterns.",
      image: "/images/onboarding/analysis.svg",
      content: (
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">
            Analyze Your Conversations
          </h1>
          <p className="text-lg mb-6">
            Start an analysis to get detailed insights into your communication
            patterns, strengths, and areas for improvement.
          </p>
          <div className="mb-8">
            <img
              src="/images/onboarding/analysis.svg"
              alt="Analyze Conversations"
              className="max-w-sm mx-auto"
            />
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-left mb-6">
            <h3 className="font-medium text-purple-800 mb-2">
              Analysis Includes:
            </h3>
            <ul className="list-disc pl-5 space-y-1 text-purple-700">
              <li>Communication patterns</li>
              <li>Sentiment analysis</li>
              <li>Response time metrics</li>
              <li>Engagement indicators</li>
              <li>Improvement opportunities</li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      title: "Get Real-Time Coaching",
      description: "Receive suggestions and tips while you chat.",
      image: "/images/onboarding/coaching.svg",
      content: (
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Get Real-Time Coaching</h1>
          <p className="text-lg mb-6">
            The Whisper Coach provides real-time suggestions as you chat,
            helping you improve your communication on the fly.
          </p>
          <div className="mb-8">
            <img
              src="/images/onboarding/coaching.svg"
              alt="Real-Time Coaching"
              className="max-w-sm mx-auto"
            />
          </div>
          <div className="bg-amber-50 p-4 rounded-lg text-left mb-6">
            <h3 className="font-medium text-amber-800 mb-2">
              Coaching Features:
            </h3>
            <ul className="list-disc pl-5 space-y-1 text-amber-700">
              <li>In-the-moment suggestions</li>
              <li>Alternative phrasing options</li>
              <li>Tone and sentiment guidance</li>
              <li>Active listening reminders</li>
              <li>Contextual relationship tips</li>
            </ul>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* Header */}
      <header className="py-4 px-6 flex justify-between items-center border-b bg-white">
        <div className="flex items-center space-x-2">
          <img src="/logo.svg" alt="Catalyst Logo" className="h-8" />
          <span className="font-bold text-xl">Catalyst</span>
        </div>
        <Button variant="ghost" onClick={handleSkip}>
          Skip Tour
        </Button>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-3xl">
          <AnimatePresence mode="wait" custom={step}>
            <motion.div
              key={step}
              custom={step}
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{
                x: { type: "spring", stiffness: 300, damping: 30 },
                opacity: { duration: 0.2 },
              }}
              className="bg-white rounded-xl shadow-lg p-8"
            >
              {steps[step].content}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="mt-8 w-full max-w-3xl flex justify-between items-center">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={step === 0}
          >
            Previous
          </Button>

          <div className="flex space-x-2">
            {Array.from({ length: totalSteps }).map((_, index) => (
              <div
                key={index}
                className={`h-2 w-2 rounded-full ${
                  index === step ? "bg-blue-600" : "bg-gray-300"
                }`}
              />
            ))}
          </div>

          <Button onClick={handleNext}>
            {step === totalSteps - 1 ? "Get Started" : "Next"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
