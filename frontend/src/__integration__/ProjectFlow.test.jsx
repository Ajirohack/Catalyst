// src/__integration__/ProjectFlow.test.jsx
// Integration test for the project creation and management flow
import React from "react";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { render } from "../lib/test-utils";
import { BrowserRouter } from "react-router-dom";
import Dashboard from "../pages/user/Dashboard";
import ProjectDetail from "../pages/user/ProjectDetail";
import NewProject from "../pages/user/NewProject";
import { server } from "../mocks/server";
import { rest } from "msw";

// Custom render with router
const renderWithRouter = (ui, { route = "/" } = {}) => {
  window.history.pushState({}, "Test page", route);
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe("Project Flow Integration", () => {
  beforeEach(() => {
    // Mock localStorage for authentication
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn(() =>
          JSON.stringify({
            token: "fake-jwt-token",
            user: {
              id: 1,
              name: "Test User",
              email: "test@example.com",
              role: "user",
            },
          })
        ),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  test("should display user projects on dashboard", async () => {
    renderWithRouter(<Dashboard />, { route: "/dashboard" });

    // Wait for first project to load
    await waitFor(() => {
      expect(screen.getByText("Test Project")).toBeInTheDocument();
    });

    // Then check for second project
    expect(screen.getByText("Another Project")).toBeInTheDocument();
  });

  test("should navigate to project creation form", async () => {
    renderWithRouter(<Dashboard />, { route: "/dashboard" });

    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByText("Test Project")).toBeInTheDocument();
    });

    // Find and click on new project button
    const newProjectButton = screen.getByText(/new project/i);
    fireEvent.click(newProjectButton);

    // Check if navigation worked
    await waitFor(() => {
      expect(window.location.pathname).toBe("/projects/new");
    });
  });

  test("should create a new project", async () => {
    // Setup server mock for project creation
    server.use(
      rest.post("http://localhost:8000/api/projects", (req, res, ctx) => {
        return res(
          ctx.status(201),
          ctx.json({
            id: 3,
            name: req.body.name,
            description: req.body.description,
            status: "active",
            createdAt: new Date().toISOString(),
          })
        );
      })
    );

    renderWithRouter(<NewProject />, { route: "/projects/new" });

    // Fill in project creation form
    const nameInput = screen.getByLabelText(/project name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole("button", {
      name: /create project/i,
    });

    fireEvent.change(nameInput, { target: { value: "New Test Project" } });
    fireEvent.change(descriptionInput, {
      target: {
        value: "This is a new test project created from integration tests",
      },
    });
    fireEvent.click(submitButton);

    // Wait for redirect to project detail
    await waitFor(() => {
      expect(window.location.pathname).toMatch(/^\/projects\/\d+$/);
    });
  });

  test("should view project details", async () => {
    renderWithRouter(<ProjectDetail />, { route: "/projects/1" });

    // Wait for project name to load
    await waitFor(() => {
      expect(screen.getByText("Project 1")).toBeInTheDocument();
    });

    // Then check for description
    expect(screen.getByText("This is project 1")).toBeInTheDocument();

    // Check if analyses are displayed
    expect(screen.getByText("Initial Analysis")).toBeInTheDocument();
  });

  test("should start a new analysis", async () => {
    // Setup server mock for analysis creation
    server.use(
      rest.post(
        "http://localhost:8000/api/projects/1/analyses",
        (req, res, ctx) => {
          return res(
            ctx.status(201),
            ctx.json({
              id: 2,
              name: req.body.name,
              projectId: 1,
              status: "pending",
              createdAt: new Date().toISOString(),
            })
          );
        }
      )
    );

    renderWithRouter(<ProjectDetail />, { route: "/projects/1" });

    // Wait for project details to load
    await waitFor(() => {
      expect(screen.getByText("Project 1")).toBeInTheDocument();
    });

    // Find and click on new analysis button
    const newAnalysisButton = screen.getByText(/new analysis/i);
    fireEvent.click(newAnalysisButton);

    // Fill in analysis name in the modal
    const nameInput = screen.getByLabelText(/analysis name/i);
    fireEvent.change(nameInput, { target: { value: "Follow-up Analysis" } });

    // Submit the form
    const submitButton = screen.getByRole("button", {
      name: /start analysis/i,
    });
    fireEvent.click(submitButton);

    // Wait for the new analysis to appear
    await waitFor(() => {
      expect(screen.getByText("Follow-up Analysis")).toBeInTheDocument();
    });
  });
});
