// src/components/Modal/Modal.stories.jsx
import React from "react";
import Modal from "./Modal";
import Button from "../Button/Button";

const meta = {
  title: "Components/Modal",
  component: Modal,
  argTypes: {
    isOpen: { control: "boolean" },
    onClose: { action: "closed" },
    title: { control: "text" },
    size: {
      control: { type: "select" },
      options: ["sm", "md", "lg", "xl", "full"],
    },
    children: { control: "text" },
    footer: { control: "text" },
    closeOnOverlayClick: { control: "boolean" },
    closeOnEsc: { control: "boolean" },
    showCloseButton: { control: "boolean" },
  },
  parameters: {
    docs: {
      description: {
        component:
          "A modal dialog component for displaying content in a layer above the app.",
      },
    },
    layout: "centered",
  },
};

export default meta;

// Default modal
export const Default = {
  args: {
    isOpen: true,
    title: "Modal Title",
    children: "This is the content of the modal dialog.",
    size: "md",
    closeOnOverlayClick: true,
    closeOnEsc: true,
    showCloseButton: true,
  },
};

// Small modal
export const Small = {
  args: {
    ...Default.args,
    title: "Small Modal",
    size: "sm",
  },
};

// Large modal
export const Large = {
  args: {
    ...Default.args,
    title: "Large Modal",
    size: "lg",
  },
};

// Full screen modal
export const FullScreen = {
  args: {
    ...Default.args,
    title: "Full Screen Modal",
    size: "full",
  },
};

// Modal with footer
export const WithFooter = {
  args: {
    ...Default.args,
    title: "Confirmation",
    children:
      "Are you sure you want to delete this item? This action cannot be undone.",
    footer: (
      <div className="flex justify-end space-x-2">
        <Button variant="secondary">Cancel</Button>
        <Button variant="danger">Delete</Button>
      </div>
    ),
  },
};

// Modal with form
export const WithForm = {
  args: {
    ...Default.args,
    title: "Create New Project",
    children: (
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Project Name
          </label>
          <input
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter project name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            rows={3}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter project description"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Platform
          </label>
          <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
            <option>WhatsApp</option>
            <option>Messenger</option>
            <option>Slack</option>
            <option>Teams</option>
          </select>
        </div>
      </form>
    ),
    footer: (
      <div className="flex justify-end space-x-2">
        <Button variant="secondary">Cancel</Button>
        <Button variant="primary">Create Project</Button>
      </div>
    ),
  },
};

// Modal without close button
export const WithoutCloseButton = {
  args: {
    ...Default.args,
    title: "No Close Button",
    showCloseButton: false,
  },
};

// Modal without overlay close
export const WithoutOverlayClose = {
  args: {
    ...Default.args,
    title: "No Overlay Close",
    closeOnOverlayClick: false,
  },
};

// Modal with long content
export const WithLongContent = {
  args: {
    ...Default.args,
    title: "Long Content",
    children: (
      <div className="space-y-4">
        {Array(10)
          .fill(0)
          .map((_, i) => (
            <p key={i}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
              euismod, nisl eget aliquam ultricies, nunc nisl aliquet nunc, quis
              aliquam nisl nunc quis nisl. Nullam euismod, nisl eget aliquam
              ultricies, nunc nisl aliquet nunc, quis aliquam nisl nunc quis
              nisl.
            </p>
          ))}
      </div>
    ),
  },
};
