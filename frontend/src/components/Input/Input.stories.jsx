// src/components/Input/Input.stories.jsx
import React from "react";
import Input from "./Input";

const meta = {
  title: "Components/Input",
  component: Input,
  argTypes: {
    type: {
      control: { type: "select" },
      options: [
        "text",
        "password",
        "email",
        "number",
        "tel",
        "url",
        "search",
        "date",
      ],
    },
    label: { control: "text" },
    placeholder: { control: "text" },
    helperText: { control: "text" },
    error: { control: "text" },
    disabled: { control: "boolean" },
    required: { control: "boolean" },
    fullWidth: { control: "boolean" },
    value: { control: "text" },
    onChange: { action: "changed" },
    onFocus: { action: "focused" },
    onBlur: { action: "blurred" },
  },
  parameters: {
    docs: {
      description: {
        component:
          "A versatile input component with various states and styles.",
      },
    },
  },
};

export default meta;

// Default input
export const Default = {
  args: {
    type: "text",
    label: "Username",
    placeholder: "Enter your username",
  },
};

// Input with helper text
export const WithHelperText = {
  args: {
    ...Default.args,
    helperText: "Your username must be 5-20 characters long",
  },
};

// Input with error
export const WithError = {
  args: {
    ...Default.args,
    error: "Username is already taken",
  },
};

// Disabled input
export const Disabled = {
  args: {
    ...Default.args,
    disabled: true,
    value: "DisabledUser",
  },
};

// Required input
export const Required = {
  args: {
    ...Default.args,
    required: true,
  },
};

// Password input
export const Password = {
  args: {
    type: "password",
    label: "Password",
    placeholder: "Enter your password",
    helperText: "Password must be at least 8 characters",
  },
};

// Email input
export const Email = {
  args: {
    type: "email",
    label: "Email Address",
    placeholder: "name@example.com",
  },
};

// Number input
export const Number = {
  args: {
    type: "number",
    label: "Age",
    placeholder: "Enter your age",
    min: 0,
    max: 120,
  },
};

// Date input
export const Date = {
  args: {
    type: "date",
    label: "Birth Date",
  },
};

// Search input
export const Search = {
  args: {
    type: "search",
    label: "Search",
    placeholder: "Search projects...",
    fullWidth: true,
  },
};

// Full width input
export const FullWidth = {
  args: {
    ...Default.args,
    fullWidth: true,
  },
};

// Input with predefined value
export const WithValue = {
  args: {
    ...Default.args,
    value: "JohnDoe",
  },
};

// Input with icon
export const WithIcon = {
  args: {
    ...Default.args,
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5 text-gray-400"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
};
