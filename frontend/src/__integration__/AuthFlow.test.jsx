// src/__integration__/AuthFlow.test.jsx
// Integration test for the authentication flow
import React from "react";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { render } from "../lib/test-utils";
import { BrowserRouter } from "react-router-dom";
import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import ForgotPassword from "../pages/auth/ForgotPassword";
import { server } from "../mocks/server";
import { rest } from "msw";

// Custom render with router
const renderWithRouter = (ui, { route = "/" } = {}) => {
  window.history.pushState({}, "Test page", route);
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe("Authentication Flow Integration", () => {
  test("should allow a user to login successfully", async () => {
    renderWithRouter(<Login />);

    // Fill in login form
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password" } });
    fireEvent.click(submitButton);

    // Wait for successful login
    await waitFor(() => {
      expect(window.location.pathname).toBe("/dashboard");
    });
  });

  test("should show error on invalid credentials", async () => {
    // Override the default handler for this specific test
    server.use(
      rest.post("http://localhost:8000/api/auth/login", (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json({
            message: "Invalid credentials",
          })
        );
      })
    );

    renderWithRouter(<Login />);

    // Fill in login form with invalid credentials
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: "wrong@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrongpassword" } });
    fireEvent.click(submitButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  test("should navigate from login to registration", async () => {
    renderWithRouter(<Login />);

    // Find and click on the registration link
    const registerLink = screen.getByText(/sign up/i);
    fireEvent.click(registerLink);

    // Check if navigation worked
    await waitFor(() => {
      expect(window.location.pathname).toBe("/register");
    });
  });

  test("should navigate from login to forgot password", async () => {
    renderWithRouter(<Login />);

    // Find and click on the forgot password link
    const forgotPasswordLink = screen.getByText(/forgot password/i);
    fireEvent.click(forgotPasswordLink);

    // Check if navigation worked
    await waitFor(() => {
      expect(window.location.pathname).toBe("/forgot-password");
    });
  });

  test("should allow registration of a new user", async () => {
    renderWithRouter(<Register />, { route: "/register" });

    // Fill in registration form
    const nameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole("button", { name: /sign up/i });

    fireEvent.change(nameInput, { target: { value: "New User" } });
    fireEvent.change(emailInput, { target: { value: "newuser@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "newpassword" } });
    fireEvent.change(confirmPasswordInput, {
      target: { value: "newpassword" },
    });
    fireEvent.click(submitButton);

    // Wait for successful registration and redirect to onboarding
    await waitFor(() => {
      expect(window.location.pathname).toBe("/onboarding");
    });
  });

  test("should allow password reset request", async () => {
    renderWithRouter(<ForgotPassword />, { route: "/forgot-password" });

    // Fill in forgot password form
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole("button", {
      name: /reset password/i,
    });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);

    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText(/check your email/i)).toBeInTheDocument();
    });
  });
});
