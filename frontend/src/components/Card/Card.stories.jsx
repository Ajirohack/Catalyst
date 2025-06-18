// src/components/Card/Card.stories.jsx
import React from "react";
import Card from "./Card";

const meta = {
  title: "Components/Card",
  component: Card,
  argTypes: {
    title: { control: "text" },
    subtitle: { control: "text" },
    children: { control: "text" },
    footer: { control: "text" },
    variant: {
      control: { type: "select" },
      options: [
        "default",
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
      ],
    },
    elevated: { control: "boolean" },
    bordered: { control: "boolean" },
    padding: {
      control: { type: "select" },
      options: ["none", "sm", "md", "lg"],
    },
    fullWidth: { control: "boolean" },
    onClick: { action: "clicked" },
  },
  parameters: {
    docs: {
      description: {
        component:
          "A versatile card component that can be used to display content in a contained format.",
      },
    },
  },
};

export default meta;

// Default card
export const Default = {
  args: {
    title: "Card Title",
    children:
      "This is the main content of the card. You can put any content here.",
  },
};

// Card with subtitle
export const WithSubtitle = {
  args: {
    ...Default.args,
    subtitle: "Card Subtitle",
  },
};

// Card with footer
export const WithFooter = {
  args: {
    ...Default.args,
    footer: "Card Footer",
  },
};

// Elevated card
export const Elevated = {
  args: {
    ...Default.args,
    elevated: true,
  },
};

// Bordered card
export const Bordered = {
  args: {
    ...Default.args,
    bordered: true,
  },
};

// Primary variant
export const Primary = {
  args: {
    ...Default.args,
    variant: "primary",
  },
};

// Success variant
export const Success = {
  args: {
    ...Default.args,
    variant: "success",
  },
};

// Danger variant
export const Danger = {
  args: {
    ...Default.args,
    variant: "danger",
  },
};

// Card with complex content
export const ComplexContent = {
  args: {
    title: "Project Summary",
    subtitle: "Key metrics and information",
    children: (
      <div>
        <div className="flex justify-between mb-4">
          <div>
            <h4 className="text-gray-500 text-sm">Total Messages</h4>
            <p className="text-2xl font-bold">1,234</p>
          </div>
          <div>
            <h4 className="text-gray-500 text-sm">Sentiment Score</h4>
            <p className="text-2xl font-bold text-green-500">8.7</p>
          </div>
          <div>
            <h4 className="text-gray-500 text-sm">Completion</h4>
            <p className="text-2xl font-bold">87%</p>
          </div>
        </div>
        <div className="bg-gray-100 h-12 rounded-md mb-4"></div>
        <p className="text-gray-600 mb-2">
          This project is progressing well with positive sentiment across most
          conversations. The majority of users are satisfied with the response
          time.
        </p>
      </div>
    ),
    footer: (
      <div className="flex justify-between">
        <button className="text-blue-500 hover:text-blue-700">
          View Details
        </button>
        <button className="text-gray-500 hover:text-gray-700">
          Export Data
        </button>
      </div>
    ),
    elevated: true,
  },
};

// Interactive card
export const Interactive = {
  args: {
    ...Default.args,
    title: "Click Me",
    children: "This card is clickable. Try clicking on it!",
    onClick: () => alert("Card clicked!"),
    elevated: true,
    className: "hover:bg-gray-50 cursor-pointer transition-colors",
  },
};
