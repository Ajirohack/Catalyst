import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { MemoryRouter, Routes, Route, Navigate } from "react-router-dom";

// Create mock components for testing
const MockNewProject = () => (
  <div data-testid="new-project-page">New Project Page</div>
);
const MockDashboard = () => (
  <div data-testid="dashboard-page">Dashboard Page</div>
);
const MockLogin = () => {
  return (
    <div data-testid="login-page">
      <h1>Login</h1>
      <form>
        <input type="email" placeholder="Email" data-testid="email-input" />
        <input
          type="password"
          placeholder="Password"
          data-testid="password-input"
        />
        <button type="submit" data-testid="login-button">
          Login
        </button>
      </form>
    </div>
  );
};

// Mock the auth context
jest.mock("../context/AuthContext", () => {
  const originalModule = jest.requireActual("../context/AuthContext");

  return {
    ...originalModule,
    AuthProvider: ({ children }) => {
      const [isAuthenticated, setIsAuthenticated] = React.useState(false);
      const [user, setUser] = React.useState(null);
      const [loading, setLoading] = React.useState(false);

      const login = async (email, password) => {
        setLoading(true);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 100));
        setUser({ id: "123", email, name: "Test User", role: "user" });
        setIsAuthenticated(true);
        setLoading(false);
        return true;
      };

      const logout = async () => {
        setLoading(true);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 100));
        setUser(null);
        setIsAuthenticated(false);
        setLoading(false);
      };

      return (
        <originalModule.AuthContext.Provider
          value={{
            user,
            isAuthenticated,
            loading,
            login,
            logout,
          }}
        >
          {children}
        </originalModule.AuthContext.Provider>
      );
    },
    useAuth: () => {
      const context = React.useContext(originalModule.AuthContext);
      if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
      }
      return context;
    },
  };
});

// Mocking Routes components
jest.mock("../pages/user/NewProject", () => MockNewProject);
jest.mock("../pages/Dashboard", () => MockDashboard);
jest.mock("../pages/auth/Login", () => MockLogin);

describe("Authentication and Navigation Flow Integration", () => {
  test("unauthenticated user is redirected to login", async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Routes>
            <Route path="/login" element={<MockLogin />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <MockDashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    // Should be redirected to login page
    expect(screen.getByTestId("login-page")).toBeInTheDocument();
    expect(screen.queryByTestId("dashboard-page")).not.toBeInTheDocument();
  });

  test("user can login and access protected routes", async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/login"]}>
          <Routes>
            <Route path="/login" element={<MockLogin />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <MockDashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    // Fill login form
    await userEvent.type(screen.getByTestId("email-input"), "user@example.com");
    await userEvent.type(screen.getByTestId("password-input"), "password123");

    // Submit login form
    await userEvent.click(screen.getByTestId("login-button"));

    // Wait for authentication to complete and redirect to occur
    await waitFor(() => {
      expect(screen.getByTestId("dashboard-page")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("login-page")).not.toBeInTheDocument();
  });
});

// Simple protected route implementation for testing
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Import these after mock implementation
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
