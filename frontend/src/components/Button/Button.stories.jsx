// src/components/Button/Button.stories.jsx
import React from "react";
import Button from "./Button";

export default {
  title: "Components/Button",
  component: Button,
  argTypes: {
    variant: {
      control: { type: "select" },
      options: [
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
      ],
    },
    size: {
      control: { type: "select" },
      options: ["sm", "md", "lg"],
    },
    isLoading: {
      control: { type: "boolean" },
    },
    isDisabled: {
      control: { type: "boolean" },
    },
    fullWidth: {
      control: { type: "boolean" },
    },
    onClick: { action: "clicked" },
  },
  parameters: {
    docs: {
      description: {
        component:
          "A reusable button component with various styles and states.",
      },
    },
  },
};

// Default button
export const Default = {
  args: {
    children: "Button",
    variant: "primary",
    size: "md",
    isLoading: false,
    isDisabled: false,
    fullWidth: false,
  },
};

// Primary button
export const Primary = {
  args: {
    ...Default.args,
    children: "Primary Button",
    variant: "primary",
  },
};

// Secondary button
export const Secondary = {
  args: {
    ...Default.args,
    children: "Secondary Button",
    variant: "secondary",
  },
};

// Success button
export const Success = {
  args: {
    ...Default.args,
    children: "Success Button",
    variant: "success",
  },
};

// Danger button
export const Danger = {
  args: {
    ...Default.args,
    children: "Danger Button",
    variant: "danger",
  },
};

// Warning button
export const Warning = {
  args: {
    ...Default.args,
    children: "Warning Button",
    variant: "warning",
  },
};

// Loading state
export const Loading = {
  args: {
    ...Default.args,
    children: "Loading Button",
    isLoading: true,
  },
};

// Disabled state
export const Disabled = {
  args: {
    ...Default.args,
    children: "Disabled Button",
    isDisabled: true,
  },
};

// Small size
export const Small = {
  args: {
    ...Default.args,
    children: "Small Button",
    size: "sm",
  },
};

// Large size
export const Large = {
  args: {
    ...Default.args,
    children: "Large Button",
    size: "lg",
  },
};

// Full width
export const FullWidth = {
  args: {
    ...Default.args,
    children: "Full Width Button",
    fullWidth: true,
  },
};

// With icon
export const WithIcon = {
  args: {
    ...Default.args,
    children: (
      <>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 mr-2"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
            clipRule="evenodd"
          />
        </svg>
        Add Item
      </>
    ),
  },
};
