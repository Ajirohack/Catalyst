// src/components/WhisperPanel/WhisperPanel.stories.jsx
import React from "react";
import WhisperPanel from "./WhisperPanel";

const meta = {
  title: "Components/WhisperPanel",
  component: WhisperPanel,
  argTypes: {
    suggestions: { control: "array" },
    context: { control: "text" },
    isLoading: { control: "boolean" },
    error: { control: "text" },
    onClose: { action: "closed" },
    onSelectSuggestion: { action: "suggestion selected" },
    onRefresh: { action: "refresh requested" },
    position: {
      control: { type: "select" },
      options: ["top-right", "top-left", "bottom-right", "bottom-left"],
    },
  },
  parameters: {
    docs: {
      description: {
        component:
          "The WhisperPanel component displays AI-generated suggestions based on conversation context.",
      },
    },
    layout: "centered",
  },
};

export default meta;

// Default panel
export const Default = {
  args: {
    suggestions: [
      "I understand your concern about the delayed delivery. Let me check the status for you.",
      "I apologize for the inconvenience caused by the delay. I will look into this right away.",
      "Thank you for bringing this to my attention. Let me find out what happened with your delivery.",
    ],
    context: "The user is upset about a delayed delivery.",
    isLoading: false,
    position: "bottom-right",
  },
};

// Loading state
export const Loading = {
  args: {
    suggestions: [],
    context: "The user is upset about a delayed delivery.",
    isLoading: true,
    position: "bottom-right",
  },
};

// Error state
export const Error = {
  args: {
    suggestions: [],
    context: "The user is upset about a delayed delivery.",
    isLoading: false,
    error: "Failed to generate suggestions. Please try again.",
    position: "bottom-right",
  },
};

// No suggestions
export const NoSuggestions = {
  args: {
    suggestions: [],
    context: "The user is upset about a delayed delivery.",
    isLoading: false,
    position: "bottom-right",
  },
};

// Top left position
export const TopLeftPosition = {
  args: {
    ...Default.args,
    position: "top-left",
  },
};

// Top right position
export const TopRightPosition = {
  args: {
    ...Default.args,
    position: "top-right",
  },
};

// Bottom left position
export const BottomLeftPosition = {
  args: {
    ...Default.args,
    position: "bottom-left",
  },
};

// With many suggestions
export const ManySuggestions = {
  args: {
    suggestions: [
      "I understand your concern about the delayed delivery. Let me check the status for you.",
      "I apologize for the inconvenience caused by the delay. I will look into this right away.",
      "Thank you for bringing this to my attention. Let me find out what happened with your delivery.",
      "I am sorry to hear about the delay with your order. Let me help you track it down.",
      "I appreciate your patience regarding the delayed delivery. Let me see what I can do to resolve this.",
      "I understand this delay is frustrating. Let me check what is happening with your order right now.",
      "Thank you for letting me know about this issue. I will work to get your delivery back on track.",
    ],
    context: "The user is upset about a delayed delivery.",
    isLoading: false,
    position: "bottom-right",
  },
};

// With complex context
export const ComplexContext = {
  args: {
    suggestions: [
      "I understand you are considering our premium plan. It offers significant advantages for team collaboration.",
      "The premium plan includes unlimited storage and priority support, which seem to align with your needs.",
      "Based on your team size, the premium plan would be $10 per user, offering great value for the features you need.",
    ],
    context:
      "The user is inquiring about upgrading to a premium plan for their 15-person team. They currently use the basic plan and need more storage and better support options. Price sensitivity is moderate. They have mentioned comparing with competitor products.",
    isLoading: false,
    position: "bottom-right",
  },
};
