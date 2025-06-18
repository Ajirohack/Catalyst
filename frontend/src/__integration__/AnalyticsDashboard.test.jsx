// src/__integration__/AnalyticsDashboard.test.jsx
// Integration test for the analytics dashboard
import React from "react";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { render } from "../lib/test-utils";
import { BrowserRouter } from "react-router-dom";
import AnalyticsDashboard from "../pages/admin/AnalyticsDashboard";

// Custom render with router
const renderWithRouter = (ui, { route = "/" } = {}) => {
  window.history.pushState({}, "Test page", route);
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe("Analytics Dashboard Integration", () => {
  beforeEach(() => {
    // Mock localStorage for authentication with admin role
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn(() =>
          JSON.stringify({
            token: "fake-jwt-token",
            user: {
              id: 2,
              name: "Admin User",
              email: "admin@example.com",
              role: "admin",
            },
          })
        ),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  test("should load and display analytics dashboard with all sections", async () => {
    renderWithRouter(<AnalyticsDashboard />, { route: "/admin/analytics" });

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText(/user growth/i)).toBeInTheDocument();
    });

    // Check for user metrics section
    await waitFor(() => {
      expect(screen.getByText(/messages sent/i)).toBeInTheDocument();
    });

    // Check for project metrics
    await waitFor(() => {
      expect(screen.getByText(/total projects/i)).toBeInTheDocument();
    });

    // Check for platform usage
    await waitFor(() => {
      expect(screen.getByText(/platform usage/i)).toBeInTheDocument();
    });

    // Check for specific metrics data
    await waitFor(() => {
      expect(screen.getByText(/150/)).toBeInTheDocument(); // Total projects
    });
  });

  test("should display charts and visualizations", async () => {
    renderWithRouter(<AnalyticsDashboard />, { route: "/admin/analytics" });

    // Wait for all charts to load
    await waitFor(() => {
      const charts = screen.getAllByTestId(/chart/i);
      expect(charts.length).toBeGreaterThan(0);
    });

    // Check for platform breakdown in the pie chart
    await waitFor(() => {
      expect(screen.getByText(/WhatsApp/i)).toBeInTheDocument();
    });

    // Check for other platforms after initial waitFor
    expect(screen.getByText(/Messenger/i)).toBeInTheDocument();
    expect(screen.getByText(/Slack/i)).toBeInTheDocument();
  });

  test("should display date filters and apply them", async () => {
    renderWithRouter(<AnalyticsDashboard />, { route: "/admin/analytics" });

    // Wait for date filters to load
    await waitFor(() => {
      expect(screen.getByText(/filter by date/i)).toBeInTheDocument();
    });

    // Find date range selector
    const dateFilter = screen.getByLabelText(/date range/i);
    expect(dateFilter).toBeInTheDocument();

    // Select a different date range
    const dateRangeSelect = screen.getByRole("combobox", {
      name: /date range/i,
    });
    fireEvent.change(dateRangeSelect, { target: { value: "last30Days" } });

    // Check if data was refreshed with new date range
    await waitFor(() => {
      expect(screen.getByText(/last 30 days/i)).toBeInTheDocument();
    });
  });

  test("should export analytics data", async () => {
    // Mock download function
    global.URL.createObjectURL = jest.fn();
    const mockLink = {
      click: jest.fn(),
      href: "",
      download: "",
      style: { display: "none" },
    };
    jest.spyOn(document, "createElement").mockImplementation(() => mockLink);
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();

    renderWithRouter(<AnalyticsDashboard />, { route: "/admin/analytics" });

    // Wait for export button to load
    await waitFor(() => {
      expect(screen.getByText(/export data/i)).toBeInTheDocument();
    });

    // Click export button
    const exportButton = screen.getByText(/export data/i);
    fireEvent.click(exportButton);

    // Check if export function was called
    await waitFor(() => {
      expect(mockLink.click).toHaveBeenCalled();
    });

    // Restore mocks
    jest.restoreAllMocks();
  });
});
