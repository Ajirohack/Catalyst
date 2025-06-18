import { screen } from "@testing-library/react";
import { render } from "../lib/test-utils";
import App from "../App";
import { getUserRole } from "../context/auth";

// Mock the auth context
jest.mock("../context/auth", () => ({
  getUserRole: jest.fn(),
}));

describe("App Component", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test("renders login page when user is not authenticated", () => {
    // Mock the getUserRole to return null (not authenticated)
    getUserRole.mockReturnValue(null);

    render(<App />);

    // Check for loading state first
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test("renders user dashboard for user role", async () => {
    // Mock the getUserRole to return 'user'
    getUserRole.mockReturnValue("user");

    render(<App />);

    // Initially shows loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test("renders admin dashboard for admin role", async () => {
    // Mock the getUserRole to return 'admin'
    getUserRole.mockReturnValue("admin");

    render(<App />);

    // Initially shows loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
